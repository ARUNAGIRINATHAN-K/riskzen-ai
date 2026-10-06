import re
from datetime import datetime, timezone
from typing import Any, Optional
import httpx

from app.config import settings
from app.connectors.base import BaseConnector, SyncResult
from app.utils.logging import get_logger

logger = get_logger("riskzen.connectors.github")


class GitHubConnector(BaseConnector):
    """Connector for syncing GitHub issues, milestones, pull requests, and dependencies."""

    BASE_URL = "https://api.github.com"

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.repo = self._parse_repo_name(config.get("repo", ""))
        self.token = config.get("token") or settings.GITHUB_TOKEN
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "RiskZen-AI-Project-Risk-Monitor",
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    def _parse_repo_name(self, repo_input: str) -> str:
        """Extract 'owner/repo' format from full URL or shorthand string."""
        cleaned = repo_input.strip().rstrip("/")
        if "github.com/" in cleaned:
            parts = cleaned.split("github.com/")[-1].split("/")
            if len(parts) >= 2:
                return f"{parts[0]}/{parts[1]}"
        return cleaned

    async def connect(self) -> bool:
        """Verify repository access and token permissions."""
        if not self.repo:
            raise ValueError("GitHub repository name is missing from connector config (e.g. 'owner/repo').")

        url = f"{self.BASE_URL}/repos/{self.repo}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, headers=self.headers)
            if response.status_code == 200:
                return True
            elif response.status_code == 404:
                raise ValueError(f"GitHub repository '{self.repo}' not found or token lacks read access.")
            elif response.status_code == 401:
                raise ValueError("GitHub API authentication failed: invalid or expired token.")
            elif response.status_code == 403:
                raise ValueError("GitHub API rate limit exceeded or forbidden access.")
            else:
                raise ValueError(f"GitHub API returned unexpected status {response.status_code}: {response.text}")

    async def status(self) -> dict[str, Any]:
        """Check API connectivity and current rate limit quota."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(f"{self.BASE_URL}/rate_limit", headers=self.headers)
                rate_data = res.json().get("resources", {}).get("core", {}) if res.status_code == 200 else {}
                return {
                    "connected": res.status_code == 200,
                    "repo": self.repo,
                    "rate_limit_limit": rate_data.get("limit"),
                    "rate_limit_remaining": rate_data.get("remaining"),
                    "rate_limit_reset": rate_data.get("reset"),
                }
        except Exception as exc:
            return {"connected": False, "repo": self.repo, "error": str(exc)}

    async def fetch_milestones(self) -> list[dict[str, Any]]:
        """Fetch all milestones (open and closed) from GitHub repository."""
        url = f"{self.BASE_URL}/repos/{self.repo}/milestones"
        params = {"state": "all", "per_page": 100}
        milestones = []

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                for m in data:
                    target_date = None
                    if m.get("due_on"):
                        try:
                            target_date = datetime.fromisoformat(m["due_on"].replace("Z", "+00:00")).date()
                        except Exception:
                            target_date = None

                    open_issues = m.get("open_issues", 0)
                    closed_issues = m.get("closed_issues", 0)
                    total = open_issues + closed_issues
                    comp_pct = round((closed_issues / total) * 100.0, 1) if total > 0 else 0.0

                    milestones.append({
                        "external_id": str(m["id"]),
                        "github_number": m["number"],
                        "title": m["title"],
                        "description": m.get("description"),
                        "target_date": target_date,
                        "status": "closed" if m["state"] == "closed" else "open",
                        "completion_percent": comp_pct,
                        "open_issues": open_issues,
                        "closed_issues": closed_issues,
                    })
        return milestones

    async def fetch_issues_and_prs(self, since: Optional[datetime] = None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Fetch all issues and pull requests, paginating through full list."""
        url = f"{self.BASE_URL}/repos/{self.repo}/issues"
        params: dict[str, Any] = {"state": "all", "per_page": 100}
        if since:
            params["since"] = since.isoformat()

        all_items: list[dict[str, Any]] = []
        page = 1

        async with httpx.AsyncClient(timeout=30.0) as client:
            while True:
                params["page"] = page
                response = await client.get(url, headers=self.headers, params=params)
                if response.status_code != 200:
                    logger.error("Failed to fetch GitHub issues page", page=page, status=response.status_code)
                    break

                page_items = response.json()
                if not page_items or not isinstance(page_items, list):
                    break

                all_items.extend(page_items)
                if len(page_items) < 100:
                    break
                page += 1

        raw_issues = []
        raw_prs = []

        for item in all_items:
            if "pull_request" in item:
                raw_prs.append(item)
            else:
                raw_issues.append(item)

        return raw_issues, raw_prs

    def normalize_issue(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Normalize raw GitHub issue payload into WorkItem format."""
        labels = [l["name"] for l in raw.get("labels", []) if isinstance(l, dict)]
        body = raw.get("body") or ""

        # Determine item type
        item_type = "task"
        if any("bug" in l.lower() for l in labels):
            item_type = "bug"
        elif any("feature" in l.lower() or "enhancement" in l.lower() for l in labels):
            item_type = "feature"
        elif any("decision" in l.lower() or "rfc" in l.lower() for l in labels):
            item_type = "decision"

        # Determine priority
        priority = "medium"
        if any("critical" in l.lower() or "urgent" in l.lower() for l in labels):
            priority = "critical"
        elif any("high" in l.lower() or "p1" in l.lower() for l in labels):
            priority = "high"
        elif any("low" in l.lower() or "p3" in l.lower() for l in labels):
            priority = "low"

        # Determine due date (if present in labels or milestone)
        due_date = None
        milestone_data = raw.get("milestone")
        milestone_ext_id = str(milestone_data["id"]) if milestone_data else None
        if milestone_data and milestone_data.get("due_on"):
            try:
                due_date = datetime.fromisoformat(milestone_data["due_on"].replace("Z", "+00:00")).date()
            except Exception:
                pass

        created_at = datetime.fromisoformat(raw["created_at"].replace("Z", "+00:00"))
        updated_at = datetime.fromisoformat(raw["updated_at"].replace("Z", "+00:00"))
        completed_at = None
        cycle_time_hours = None

        if raw.get("closed_at"):
            completed_at = datetime.fromisoformat(raw["closed_at"].replace("Z", "+00:00"))
            cycle_time_hours = round((completed_at - created_at).total_seconds() / 3600.0, 2)

        assignee = None
        if raw.get("assignees"):
            assignee = ", ".join([a["login"] for a in raw["assignees"]])
        elif raw.get("assignee"):
            assignee = raw["assignee"]["login"]

        status = "closed" if raw.get("state") == "closed" else ("in_progress" if assignee else "open")
        if any("in progress" in l.lower() or "wip" in l.lower() for l in labels):
            status = "in_progress"

        return {
            "external_id": str(raw["id"]),
            "github_number": raw["number"],
            "source_type": "github",
            "title": raw.get("title", "Untitled Issue"),
            "description": body,
            "status": status,
            "priority": priority,
            "item_type": item_type,
            "assignee": assignee,
            "labels": labels,
            "due_date": due_date,
            "milestone_external_id": milestone_ext_id,
            "created_at": created_at,
            "updated_at": updated_at,
            "completed_at": completed_at,
            "cycle_time_hours": cycle_time_hours,
            "metadata_json": {
                "html_url": raw.get("html_url"),
                "comments_count": raw.get("comments", 0),
                "author": raw.get("user", {}).get("login"),
            },
        }

    def normalize_pr(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Normalize raw GitHub pull request payload into WorkItem format."""
        issue_form = self.normalize_issue(raw)
        issue_form["item_type"] = "pull_request"
        issue_form["metadata_json"]["is_pr"] = True
        return issue_form

    def extract_dependencies(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Extract issue dependency relationships by parsing body text patterns.

        Matches patterns such as:
        - "blocked by #123"
        - "depends on #123"
        - "prerequisite: #123"
        """
        patterns = [
            r"(?:blocked\s+by|depends\s+on|requires|prerequisite(?:\s+is)?)\s*:?\s*#(\d+)",
            r"(?:blocks|is\s+prerequisite\s+for)\s*:?\s*#(\d+)",
        ]

        # Map number -> item external_id
        number_to_ext_id: dict[int, str] = {}
        for it in items:
            if "github_number" in it and "external_id" in it:
                number_to_ext_id[it["github_number"]] = it["external_id"]

        dependencies = []

        for item in items:
            body = item.get("description") or ""
            source_ext_id = item["external_id"]

            # Pattern 1: this item is BLOCKED BY #num
            for match in re.finditer(patterns[0], body, re.IGNORECASE):
                target_num = int(match.group(1))
                if target_num in number_to_ext_id:
                    dependencies.append({
                        "source_external_id": source_ext_id,
                        "target_external_id": number_to_ext_id[target_num],
                        "dependency_type": "blocks",
                    })

            # Pattern 2: this item BLOCKS #num
            for match in re.finditer(patterns[1], body, re.IGNORECASE):
                target_num = int(match.group(1))
                if target_num in number_to_ext_id:
                    dependencies.append({
                        "source_external_id": number_to_ext_id[target_num],
                        "target_external_id": source_ext_id,
                        "dependency_type": "blocks",
                    })

        return dependencies

    async def sync(self, since: Optional[datetime] = None) -> SyncResult:
        """Execute full fetch and normalization of GitHub project artifacts."""
        result = SyncResult(synced_at=datetime.now(timezone.utc))

        try:
            milestones = await self.fetch_milestones()
            raw_issues, raw_prs = await self.fetch_issues_and_prs(since=since)

            normalized_items = [self.normalize_issue(i) for i in raw_issues]
            normalized_prs = [self.normalize_pr(p) for p in raw_prs]
            all_work_items = normalized_items + normalized_prs

            dependencies = self.extract_dependencies(all_work_items)

            result.items_created = len(all_work_items)
            result.milestones_synced = len(milestones)
            result.dependencies_detected = len(dependencies)
            result.details = {
                "milestones": milestones,
                "work_items": all_work_items,
                "dependencies": dependencies,
            }
            result.success = True
        except Exception as exc:
            logger.error("GitHub connector sync failed", error=str(exc))
            result.success = False
            result.errors.append(str(exc))

        return result
