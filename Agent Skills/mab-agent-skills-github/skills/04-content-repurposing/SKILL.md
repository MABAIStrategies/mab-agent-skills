# Skill 04: Omnichannel Content Repurposing Engine

## Description
Transforms a single source asset into 20+ platform-optimized variants to maximize reach, engagement, and ROI for MAB AI Strategies.

## Capabilities
- Convert long-form content into multi-channel assets
- Generate platform-specific hooks, CTAs, and hashtags
- Produce email sequences, blog drafts, and social snippets
- A/B test headlines and hooks
- Schedule publishing workflows
- Track engagement performance by variant

## Triggers
- "Repurpose this webinar into LinkedIn posts"
- "Create a 5-email sequence from this case study"
- "Generate a Twitter thread from this blog"
- "Create TikTok scripts from this video transcript"
- "Summarize content into sales enablement notes"

## Integration Requirements
- YouTube API (video ingestion)
- Whisper API (transcription)
- Adobe/Canva (visual creation)
- LinkedIn API (publishing)
- Mailchimp/HubSpot (email)
- Medium/Substack (blog distribution)

## Workflow

### 1. Content Intake
**Input:**
- Source type (webinar, blog, case study)
- Raw transcript or text
- Target platforms

**Process:**
1. Normalize and clean content
2. Extract key themes and quotes
3. Identify CTA and audience

**Output:**
- Structured content source

### 2. Variant Generation
**Process:**
1. Generate platform-specific assets
2. Optimize tone and length
3. Attach hashtags and CTAs

**Output:**
- Repurposed asset batch

### 3. Distribution & Tracking
**Process:**
1. Route to publishing tools
2. Capture engagement metrics
3. Update performance dashboard

**Output:**
- Engagement report and recommendations

## Data Model

### Repurpose Batch
```python
{
    "batch_id": "batch_123",
    "source_id": "webinar_456",
    "assets": [
        {
            "platform": "LinkedIn",
            "format": "post",
            "headline": "AI Automation Trends",
            "body": "...",
            "hashtags": ["#AI", "#Automation"],
            "call_to_action": "Book a strategy call"
        }
    ]
}
```

## Security & Privacy
- Respect platform policies and rate limits
- Remove client-sensitive data before publishing
- Audit trail for content approvals

## Success Metrics
- Content output multiplier (target 20x)
- Engagement lift vs baseline
- Cost per asset reduction
- CTA conversion rate

## Cost Estimates
- LLM generation: ~$40/month
- Storage: ~$5/month
- Total: ~$45/month

## Rules
1. NEVER publish without approval
2. ALWAYS align messaging to MAB AI Strategies brand voice
3. Use compliant hashtags and disclosures
4. Maintain CTA alignment with funnel stage
