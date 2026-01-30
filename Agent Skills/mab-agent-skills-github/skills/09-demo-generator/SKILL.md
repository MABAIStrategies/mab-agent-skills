# Skill 09: Portfolio Showcase & Demo Environment Generator

## Description
Instantly spin up customized demo environments showcasing MAB AI Strategies' agents and web apps, tailored to prospect industry and use case.

## Capabilities
- Curate demo stacks by industry or pain point
- Generate demo walkthrough scripts
- Provision isolated demo links with expiration
- Load realistic sample data
- Track engagement analytics

## Triggers
- "Generate a demo for healthcare prospect"
- "Create a fintech demo environment"
- "List available demos by industry"
- "Spin up a demo for sales ops automation"

## Integration Requirements
- GitHub (source repos)
- Docker/Vercel/Netlify (deployment)
- Analytics tracking
- Cloud Storage (demo assets)

## Workflow

### 1. Demo Request Intake
**Input:**
- Prospect industry
- Pain points
- Company size

**Process:**
1. Match demos to industry
2. Select 3-5 relevant agents
3. Generate demo script

**Output:**
- Demo configuration

### 2. Environment Provisioning
**Process:**
1. Build containers
2. Deploy to isolated environment
3. Load sample data

**Output:**
- Demo environment URL

### 3. Analytics Tracking
**Process:**
1. Track usage events
2. Score engagement depth

**Output:**
- Demo engagement report

## Data Model

### Demo Environment
```python
{
    "environment_id": "demo_123",
    "industry": "Healthcare",
    "selected_demos": ["Patient Intake Automation"],
    "demo_url": "https://demo.mabstrategies.com/demo_123",
    "expires_at": "2026-02-01T00:00:00Z"
}
```

## Security & Privacy
- Isolated demo environments
- Expiring links (7 days)
- Read-only demo data

## Success Metrics
- Demo-to-trial conversion (>40%)
- Setup time reduction (2 hours → 5 minutes)
- Engagement depth (% features explored)

## Cost Estimates
- Compute for demos: ~$50/month
- Storage & analytics: ~$15/month
- Total: ~$65/month

## Rules
1. NEVER expose real client data
2. ALWAYS expire demo links
3. Provide walk-through script for sales team
