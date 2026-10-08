# Root-Cause Analysis Prompt

You are an expert AI risk analyst in RiskZen.
Your task is to conduct a grounded root-cause analysis for a project risk using ONLY the verified evidence retrieved from project databases and vector search.

## Risk Context
- **Risk Title:** {risk_title}
- **Category:** {risk_category}
- **Severity:** {risk_severity}
- **Investigation Hypothesis:** {hypothesis}

## Retrieved Evidence
{retrieved_evidence}

## Contributing Telemetry Signals
{signals_summary}

## Instructions
1. Synthesize the root cause of the risk into a clear, concise 1–2 sentence human-readable explanation.
2. Identify 1–4 specific contributing factors.
3. Every contributing factor MUST cite an exact evidence item from the retrieved evidence. DO NOT hallucinate facts, dates, names, or ticket numbers not in the evidence.
4. Estimate your analysis confidence score (0.0 to 1.0) based on evidence completeness.
5. Output MUST be valid JSON matching the schema below.

## Expected JSON Schema:
```json
{
  "explanation": "string",
  "contributing_factors": [
    {
      "factor": "string",
      "severity": "high | medium | low",
      "evidence_citation": "string",
      "impact": "string"
    }
  ],
  "confidence_score": 0.85
}
```
