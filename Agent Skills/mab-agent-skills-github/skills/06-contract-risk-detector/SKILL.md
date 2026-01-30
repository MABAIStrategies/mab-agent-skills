# Skill 06: Contract Red Flag Detector & Risk Mitigator

## Description
Automated legal review of contracts, MSAs, and SOWs to identify unfavorable terms before signing, protecting MAB AI Strategies from liability exposure.

## Capabilities
- Detect high-risk clauses (liability, IP ownership, auto-renew)
- Score contract risk (Red/Yellow/Green)
- Generate redline recommendations
- Track negotiation outcomes
- Produce legal review summaries for leadership

## Triggers
- "Review this contract for red flags"
- "Generate redlines for agreement 123"
- "Show me contracts with high risk score"
- "Summarize liability clauses"
- "Compare contract to MAB standard terms"

## Integration Requirements
- DocuSign API (contract ingestion)
- Google Drive (storage)
- Legal clause library (Firestore)
- Slack (attorney escalation)

## Workflow

### 1. Contract Intake
**Input:**
- Contract text or PDF OCR output
- Counterparty info

**Process:**
1. Parse sections (payment, liability, IP)
2. Detect clause patterns
3. Normalize language

**Output:**
- Structured contract record

### 2. Risk Analysis
**Process:**
1. Match clause patterns
2. Score risk and severity
3. Generate recommendations

**Output:**
- Risk scorecard
- Clause findings

### 3. Redline Generation
**Process:**
1. Generate redline suggestions
2. Attach fallback language
3. Route for legal review

**Output:**
- Redline recommendations

## Data Model

### Contract Review
```python
{
    "contract_id": "msa_2026_01",
    "risk_score": 72.5,
    "risk_level": "high",
    "findings": [
        {
            "clause_type": "Unlimited Liability",
            "risk_level": "high",
            "excerpt": "unlimited liability",
            "recommendation": "Cap liability to 12-24 months of fees paid."
        }
    ]
}
```

## Security & Privacy
- Access restricted to legal and executive team
- Encrypt contracts at rest
- Maintain audit trail for redline access

## Success Metrics
- Unfavorable terms caught per quarter
- Negotiation win rate (% redlines accepted)
- Legal review time reduction (3 days → 3 hours)
- Deal value protected

## Cost Estimates
- OCR + storage: ~$20/month
- LLM redlines: ~$30/month
- Total: ~$50/month

## Rules
1. ALWAYS require attorney review before sending redlines
2. NEVER approve contracts automatically
3. Flag high-risk clauses immediately
4. Maintain version history for all edits
