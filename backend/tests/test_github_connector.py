import pytest
from app.connectors.github import GitHubConnector


def test_repo_name_parsing():
    """Test parsing shorthand and full URL GitHub repo references."""
    c1 = GitHubConnector({"repo": "owner/sample-repo"})
    assert c1.repo == "owner/sample-repo"

    c2 = GitHubConnector({"repo": "https://github.com/facebook/react/"})
    assert c2.repo == "facebook/react"

    c3 = GitHubConnector({"repo": "https://github.com/fastapi/fastapi/issues"})
    assert c3.repo == "fastapi/fastapi"


def test_normalize_issue():
    """Test normalizing raw GitHub issue data into WorkItem structure."""
    connector = GitHubConnector({"repo": "test/repo"})
    raw_issue = {
        "id": 998877,
        "number": 42,
        "title": "Critical Authentication Security Bug",
        "body": "Fix authentication token replay vulnerability. Depends on #10",
        "state": "open",
        "labels": [{"name": "bug"}, {"name": "critical"}, {"name": "backend"}],
        "assignees": [{"login": "alexchen"}],
        "created_at": "2026-10-01T10:00:00Z",
        "updated_at": "2026-10-02T12:00:00Z",
        "closed_at": None,
        "milestone": {
            "id": 12345,
            "number": 1,
            "title": "Payment Tokenization",
            "due_on": "2026-10-15T00:00:00Z",
        },
        "html_url": "https://github.com/test/repo/issues/42",
        "comments": 4,
        "user": {"login": "reporter1"},
    }

    normalized = connector.normalize_issue(raw_issue)

    assert normalized["external_id"] == "998877"
    assert normalized["github_number"] == 42
    assert normalized["item_type"] == "bug"
    assert normalized["priority"] == "critical"
    assert normalized["status"] == "in_progress"
    assert normalized["assignee"] == "alexchen"
    assert "backend" in normalized["labels"]
    assert str(normalized["due_date"]) == "2026-10-15"
    assert normalized["milestone_external_id"] == "12345"


def test_dependency_extraction_from_issue_bodies():
    """Test parsing dependency phrases from issue descriptions."""
    connector = GitHubConnector({"repo": "test/repo"})

    items = [
        {
            "external_id": "ext-10",
            "github_number": 10,
            "title": "Database Schema Setup",
            "description": "Initial Postgres migration.",
        },
        {
            "external_id": "ext-42",
            "github_number": 42,
            "title": "Payment API Endpoint",
            "description": "Create Stripe webhook. Blocked by #10.",
        },
        {
            "external_id": "ext-99",
            "github_number": 99,
            "title": "Prerequisite Auth Service",
            "description": "Core auth. Blocks #100.",
        },
        {
            "external_id": "ext-100",
            "github_number": 100,
            "title": "User Profile Page",
            "description": "Display user details.",
        },
    ]

    deps = connector.extract_dependencies(items)

    assert len(deps) == 2
    # Verify ext-42 is blocked by ext-10
    d1 = next(d for d in deps if d["source_external_id"] == "ext-42")
    assert d1["target_external_id"] == "ext-10"
    assert d1["dependency_type"] == "blocks"

    # Verify ext-100 is blocked by ext-99
    d2 = next(d for d in deps if d["source_external_id"] == "ext-100")
    assert d2["target_external_id"] == "ext-99"
