# Skill 05: Sales Conversation Intelligence Miner

## Description
Extracts insights, objection patterns, and coaching opportunities from sales calls to continuously improve team performance for MAB AI Strategies.

## Capabilities
- Talk ratio analysis (rep vs prospect)
- Objection detection and categorization
- Value proposition delivery tracking
- Next-step clarity checks
- Sentiment scoring for engagement
- Coaching recommendations
- Best-practice library updates

## Triggers
- "Analyze this sales call transcript"
- "Score call quality for [Rep Name]"
- "Generate coaching tips for Call ID 123"
- "Show top objections this month"
- "Highlight calls with low talk ratio"

## Integration Requirements
- Gong/Chorus/Fireflies (recordings)
- Whisper API (transcription)
- HubSpot (deal association)
- Slack (coach alerts)
- Google Sheets (scorecards)

## Workflow

### 1. Transcript Intake
**Input:**
- Call transcript
- Speaker labels
- Deal context

**Process:**
1. Normalize transcript
2. Identify speakers and metadata
3. Store transcript for analysis

### 2. Call Quality Analysis
**Process:**
1. Calculate talk ratio
2. Detect objections and sentiment
3. Score value prop delivery
4. Compute overall call score

**Output:**
- Call quality scorecard
- Objection summary
- Engagement signals

### 3. Coaching Recommendations
**Process:**
1. Compare to top-performing calls
2. Generate coaching tips
3. Publish to manager dashboard

**Output:**
- Coaching playbook
- Improvement checklist

## Data Model

### Conversation Analysis
```python
{
    "call_id": "call_789",
    "talk_ratio_rep": 0.42,
    "sentiment_score": 0.68,
    "objection_findings": [
        {"category": "pricing", "excerpt": "budget", "confidence": 0.7}
    ],
    "value_prop_mentions": 3,
    "next_steps_defined": true,
    "score": 82.5
}
```

## Security & Privacy
- PII redaction in logs
- Permissioned access for coaching data
- Retain transcripts per compliance policy

## Success Metrics
- Call score improvement: +10 points in 60 days
- Reduced objection escalation rate
- Faster onboarding time for new reps
- Increased win rate for coached reps

## Cost Estimates
- Transcription: ~$30/month
- LLM coaching: ~$35/month
- Total: ~$65/month

## Rules
1. NEVER store sensitive client data without consent
2. ALWAYS provide human review for Red-score calls
3. Flag low-confidence objections
4. Keep coaching feedback constructive and specific
