# Skill 10: Revenue Forecasting & Pipeline Health Engine

## Description
AI-powered sales forecasting with anomaly detection and prescriptive recommendations to hit revenue targets with high accuracy.

## Capabilities
- Forecast revenue by quarter and stage
- Predict close probability per deal
- Detect slipping or stalled deals
- Highlight pipeline coverage gaps
- Recommend priority actions

## Triggers
- "Forecast Q2 pipeline"
- "Score all open deals"
- "Show deals at risk of slipping"
- "Identify pipeline shortfall"

## Integration Requirements
- HubSpot/Salesforce (deal data)
- Gong/Chorus (activity data)
- Product analytics (engagement signals)
- Slack (alerts)

## Workflow

### 1. Deal Scoring
**Input:**
- Deal size
- Stage and days in stage
- Activity and engagement
- Competitive presence

**Process:**
1. Compute probability
2. Identify risk factors
3. Estimate close date

**Output:**
- Deal-level forecast scores

### 2. Pipeline Forecast
**Process:**
1. Aggregate best/likely/worst cases
2. Calculate confidence interval
3. Detect shortfalls

**Output:**
- Revenue forecast summary

### 3. Recommendations
**Process:**
1. Prioritize high-probability deals
2. Flag deals needing intervention

**Output:**
- Prescriptive action list

## Data Model

### Deal Forecast Result
```python
{
    "deal_id": "deal_123",
    "probability": 0.78,
    "expected_close_date": "2026-03-20",
    "risk_factors": ["Low activity level"]
}
```

## Security & Privacy
- Restrict access to RevOps and leadership
- Log forecast changes
- Encrypt deal data in transit

## Success Metrics
- Forecast accuracy within ±10%
- Slippage prevention rate (>70%)
- Pipeline coverage ratio improvement

## Cost Estimates
- Forecast compute: ~$20/month
- LLM insights: ~$25/month
- Total: ~$45/month

## Rules
1. NEVER override human commitments automatically
2. ALWAYS flag low-confidence forecasts
3. Refresh forecasts weekly
