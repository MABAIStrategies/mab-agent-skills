# Skill 03: Proposal Win-Loss Intelligence Analyzer

## Description
Systematic analysis of won/lost deals to surface patterns, refine messaging, optimize pricing, and improve close rates through data-driven insights for MAB AI Strategies.

## Capabilities
- Analyze deal progression through sales stages
- Identify win/loss patterns by vertical, segment, and competitor
- Correlate objections with lost deals
- Track demo and proposal effectiveness
- Generate quarterly sales playbooks
- Highlight top-performing rep behaviors

## Triggers
- "Analyze win/loss performance for last quarter"
- "Generate a win-loss playbook for healthcare deals"
- "Show objections that most often lead to losses"
- "Compare win rates against [Competitor]"
- "Summarize stage bottlenecks for enterprise deals"

## Integration Requirements
- HubSpot/Salesforce (deal data)
- Gong/Chorus (call transcripts)
- DocuSign (contract timing)
- Google Drive (proposal docs)
- Notion (sales intelligence repository)

## Workflow

### 1. Deal Intake
**Input:**
- Deal records (won/lost/open)
- Stage history
- Objections
- Competitor

**Process:**
1. Normalize deal fields
2. Store in win-loss dataset
3. Validate data completeness

**Output:**
- Structured deal records ready for analysis

### 2. Win-Loss Analysis
**Process:**
1. Aggregate deal outcomes
2. Group by competitor, industry, stage
3. Extract top objections
4. Compute win rate and average deal size

**Output:**
- Win-loss analysis summary
- Pattern breakdowns
- Objection heat map

### 3. Sales Playbook Generation
**Input:** Win-loss analysis

**Process:**
1. Summarize patterns with LLM
2. Generate recommendations
3. Publish playbook

**Output:**
- Executive summary
- Actionable recommendations
- Implementation checklist

## Data Model

### Deal Record
```python
{
    "id": "deal_123",
    "account_name": "Acme Corp",
    "stage": "proposal",
    "outcome": "lost",
    "amount": 250000,
    "industry": "Healthcare",
    "competitor": "Competitor X",
    "objections": ["Pricing", "Implementation time"],
    "demo_score": 0.7,
    "proposal_version": "v3",
    "closed_at": "2026-01-20T00:00:00Z"
}
```

### Analysis Output
```python
{
    "analysis_id": "analysis_abc123",
    "timeframe_days": 90,
    "total_deals": 48,
    "wins": 18,
    "losses": 30,
    "win_rate": 37.5,
    "avg_deal_size": 142000,
    "by_competitor": {"Competitor X": 12, "Competitor Y": 7},
    "by_industry": {"Healthcare": 14, "Telecom": 10},
    "top_objections": ["Pricing", "Security"]
}
```

## Security & Privacy
- Restrict access to sales leadership and RevOps
- Encrypt deal data and playbooks
- Mask sensitive pricing in dashboards
- Maintain audit logs for playbook access

## Success Metrics
- Win rate improvement Q/Q: >5% lift
- Competitive win rate gains
- Average deal size increase
- Sales cycle reduction
- Proposal iteration time reduction

## Cost Estimates
- LLM summarization: ~$25/month
- Storage: ~$5/month
- Total: ~$30/month

## Rules
1. NEVER fabricate deal data
2. ALWAYS cite sources for competitive loss claims
3. Flag low-confidence insights
4. Prioritize accuracy over speed
5. Review insights with sales leadership quarterly
