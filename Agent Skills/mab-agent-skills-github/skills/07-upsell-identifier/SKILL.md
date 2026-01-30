# Skill 07: Upsell & Cross-Sell Opportunity Identifier

## Description
Data-driven identification of expansion revenue opportunities within existing accounts through usage patterns and behavior signals for MAB AI Strategies.

## Capabilities
- Score expansion readiness by account
- Surface feature adoption gaps
- Identify executive engagement trends
- Generate upsell proposals with ROI projections
- Track expansion pipeline performance

## Triggers
- "Score upsell opportunities for Q2"
- "Generate expansion proposal for Acme Corp"
- "List accounts with high utilization"
- "Identify accounts with new department growth"

## Integration Requirements
- HubSpot/Salesforce (account data)
- Product usage analytics
- LinkedIn (org changes)
- Support tickets (feature requests)

## Workflow

### 1. Signal Intake
**Input:**
- Usage data
- Feature requests
- Org growth metrics
- Executive engagement

**Process:**
1. Normalize signals
2. Apply scoring weights
3. Identify key drivers

**Output:**
- Expansion score and signal summary

### 2. Opportunity Scoring
**Process:**
1. Calculate weighted score
2. Recommend expansion tier
3. Tag with opportunity label

**Output:**
- Upsell opportunity record

### 3. Proposal Generation
**Process:**
1. Draft ROI projection
2. Outline implementation timeline
3. Add pricing guidance

**Output:**
- Proposal summary and next steps

## Data Model

### Upsell Opportunity
```python
{
    "account_id": "acc_456",
    "account_name": "Acme Corp",
    "expansion_score": 82.5,
    "recommended_tier": "Enterprise+",
    "key_signals": ["High utilization", "Executive engagement"]
}
```

## Security & Privacy
- Restrict visibility to account owners
- Encrypt usage data summaries
- Log proposal access events

## Success Metrics
- Expansion pipeline generated per quarter
- Upsell conversion rate (>30%)
- Average expansion deal size
- Time to opportunity identification (<7 days)

## Cost Estimates
- Data aggregation: ~$15/month
- LLM proposal drafts: ~$20/month
- Total: ~$35/month

## Rules
1. NEVER contact clients directly without CSM approval
2. ALWAYS validate data before scoring
3. Track outcomes to improve scoring model
