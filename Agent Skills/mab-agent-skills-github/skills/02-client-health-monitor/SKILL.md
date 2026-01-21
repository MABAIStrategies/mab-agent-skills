# Skill 02: Client Success Health Monitor & Churn Predictor

## Description
Proactive identification of at-risk clients through engagement scoring, usage analytics, and sentiment analysis to prevent churn before it happens.

## Capabilities
- Calculate real-time health scores for all accounts
- Predict churn risk with ML model (30, 60, 90-day windows)
- Generate automated retention campaigns
- Alert on red/yellow accounts
- Track intervention outcomes
- Monitor product usage velocity
- Analyze communication sentiment
- Detect engagement drop-offs

## Triggers
- "Show me all Red health score accounts"
- "Calculate health score for [Account Name]"
- "Generate retention campaign for at-risk healthcare clients"
- "Which accounts haven't logged in for 14+ days?"
- "Predict churn risk for [Account ID]"
- "Alert me when any account drops to Yellow status"

## Integration Requirements
- HubSpot/Salesforce (account data)
- Google Analytics/Mixpanel (product usage)
- Gmail API (email sentiment)
- Calendar API (meeting frequency)
- Zendesk/Intercom (support tickets)
- Billing system (payment patterns)
- Slack (CSM alerts)

## Workflow

### 1. Health Score Calculation (Automated Daily)
**Algorithm:**
```python
health_score = (
    usage_velocity * 0.30 +        # Product engagement
    engagement_cadence * 0.25 +    # Communication frequency
    sentiment_score * 0.20 +       # Email/call tone
    financial_health * 0.15 +      # Payment/contract status
    support_patterns * 0.10        # Ticket volume/escalations
)
```

**Thresholds:**
- **Green (70-100):** Healthy, identify upsell opportunities
- **Yellow (40-69):** At-risk, trigger proactive outreach
- **Red (0-39):** Churn imminent, immediate intervention required

### 2. Churn Prediction Model
**Features:**
- Days since last login
- Feature adoption rate (% of features used)
- Response time to CSM emails
- NPS score trend
- Support ticket escalation rate
- Payment delay patterns
- Executive engagement level

**Output:**
- Churn probability (0-100%)
- Predicted churn date
- Primary risk factors
- Confidence level

### 3. Retention Campaign Generation
**Input:** At-risk account profile + risk factors
**Process:**
1. Analyze account history
2. Identify success patterns from saved accounts
3. LLM generates personalized campaign:
   - Email sequence (3-5 emails)
   - Talking points for CSM call
   - Value demonstration offer (demo, training, consultation)
   - Executive engagement recommendation

**Output:** Complete campaign playbook

## Data Model

### Account Health Record
```python
{
    "account_id": "acc_123",
    "account_name": "Acme Corp",
    "health_score": 45.3,
    "status": "yellow",  # red | yellow | green
    "last_calculated": "2026-01-20T10:00:00Z",
    "component_scores": {
        "usage_velocity": 30.0,
        "engagement_cadence": 55.0,
        "sentiment_score": 40.0,
        "financial_health": 80.0,
        "support_patterns": 60.0
    },
    "risk_factors": [
        "No login in 21 days",
        "Negative sentiment in last 3 emails",
        "Support ticket escalated"
    ],
    "churn_prediction": {
        "probability": 68.5,
        "predicted_date": "2026-03-15",
        "confidence": "high"
    },
    "csm_assigned": "user_456",
    "next_review": "2026-01-27",
    "intervention_history": [
        {
            "date": "2026-01-10",
            "action": "Outreach email sent",
            "outcome": "No response"
        }
    ]
}
```

## Security & Privacy
- HIPAA compliance for healthcare clients
- PII pseudonymization in logs
- Access restricted to CSM team + executives
- Encrypted health score data
- Audit trail for all actions

## Success Metrics
- **Churn prediction accuracy:** >80% true positive at 30-day window
- **Save rate for Red accounts:** >60%
- **Time to intervention:** <24 hours from Red classification
- **Revenue protected:** Track $ value of prevented churn per quarter
- **False positive rate:** <15%

## Cost Estimates
- **LLM (campaign generation):** ~$40/month (20 campaigns)
- **Storage:** ~$10/month
- **Analytics API calls:** ~$15/month
- **Total:** ~$65/month

## Rules
1. NEVER contact client directly without CSM approval
2. ALWAYS provide data-backed risk factors
3. Flag low-confidence predictions clearly
4. Track all intervention outcomes for model improvement
5. Escalate Red accounts within 24 hours
