"""Mock LLM Provider for unit testing and deterministic offline fallback."""
import json
import re
from typing import List, Optional

from app.agent.llm.base import BaseLLMService


class MockLLMProvider(BaseLLMService):
    """Deterministic LLM Provider generating structured outputs for tests and fallbacks."""

    def __init__(self, model: str = "mock-model"):
        self.model = model

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        response_format: Optional[str] = None,
    ) -> str:
        prompt_lower = prompt.lower()

        # 1. Investigate Node Response
        if "investigate" in prompt_lower or "preliminary reasoning" in prompt_lower:
            data = {
                "initial_hypothesis": "The project is experiencing delivery compression due to cascading overdue tasks and key-person dependency.",
                "scope_of_investigation": "Evaluate milestone target dates, open dependencies, and workload distribution.",
                "key_questions": [
                    "Which upstream work item is causing the primary bottleneck?",
                    "Are secondary assignees available to offload critical path items?"
                ],
                "recommended_evidence_queries": [
                    "overdue critical tasks",
                    "blocking dependencies",
                    "milestone slippage historical patterns"
                ]
            }
            return json.dumps(data)

        # 2. Root Cause Analysis Node Response
        if "root-cause" in prompt_lower or "contributing factors" in prompt_lower or "analyze" in prompt_lower:
            data = {
                "explanation": "Critical milestone delivery is compromised due to an unaddressed upstream bottleneck combined with 80% work item concentration on a single senior engineer.",
                "contributing_factors": [
                    {
                        "factor": "Upstream Dependency Blocker",
                        "severity": "high",
                        "evidence_citation": "Task #102 is blocked by Task #101 which is 6 days overdue.",
                        "impact": "Blocks 3 downstream deliverables on the critical path."
                    },
                    {
                        "factor": "Workload Concentration on Key Engineer",
                        "severity": "medium",
                        "evidence_citation": "Senior Developer has 8 active in-progress items.",
                        "impact": "Cycle time increased by 45% over the past 2 weeks."
                    }
                ],
                "confidence_score": 0.88
            }
            return json.dumps(data)

        # 3. Recommendation Node Response
        if "recommend" in prompt_lower or "mitigation actions" in prompt_lower:
            data = {
                "recommendations": [
                    {
                        "action_description": "Reassign non-critical tasks from the bottleneck engineer to available team members to unblock the critical path.",
                        "rationale": "Reduces WIP concentration on the single owner from 8 items to 3 items, restoring cycle velocity.",
                        "suggested_owner": "Project Lead",
                        "urgency": "immediate"
                    },
                    {
                        "action_description": "Schedule a focused technical sync to unblock Task #101 or descope secondary requirements.",
                        "rationale": "Resolving or splitting Task #101 unblocks 3 downstream tasks waiting on this dependency.",
                        "suggested_owner": "Tech Lead",
                        "urgency": "today"
                    },
                    {
                        "action_description": "Update milestone buffer by 4 business days and notify stakeholders.",
                        "rationale": "Aligns delivery expectations with realistic remaining capacity and historical burn rate.",
                        "suggested_owner": "Project Manager",
                        "urgency": "this_week"
                    }
                ]
            }
            return json.dumps(data)

        # 4. Review / Quality Guard Node Response
        if "review" in prompt_lower or "quality check" in prompt_lower:
            data = {
                "quality_check_passed": True,
                "feedback": "All claims are grounded in evidence citations and recommendations are actionable and assigned to realistic owners.",
                "hallucination_detected": False
            }
            return json.dumps(data)

        # Default fallback json response
        return json.dumps({"status": "success", "message": "Mock completion generated."})

    async def embed(self, text: str) -> List[float]:
        # Generate simple deterministic pseudo-embedding based on hash
        val = (hash(text) % 1000) / 1000.0
        return [val] * 1536

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [await self.embed(t) for t in texts]
