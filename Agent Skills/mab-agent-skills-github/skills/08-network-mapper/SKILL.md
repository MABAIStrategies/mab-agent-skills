# Skill 08: Strategic Network Relationship Mapper

## Description
Visualize and leverage Mark's professional network for warm introductions, referrals, and partnership opportunities using graph analytics.

## Capabilities
- Map relationships across people, companies, and industries
- Score relationship strength by frequency and recency
- Identify warm intro paths to target decision-makers
- Detect dormant relationships
- Generate intro request templates

## Triggers
- "Find the shortest intro path to [Target]"
- "Score relationship strength for [Contact]"
- "Show dormant relationships older than 90 days"
- "Map network cluster for healthcare"

## Integration Requirements
- LinkedIn API (connection data)
- Gmail (interaction history)
- Calendar (meeting data)
- HubSpot (deal associations)
- Neo4j (graph database)

## Workflow

### 1. Network Intake
**Input:**
- Connections list
- Interaction history
- Role/industry metadata

**Process:**
1. Normalize nodes and edges
2. Store in graph database
3. Calculate relationship strength

**Output:**
- Relationship graph

### 2. Intro Pathfinding
**Process:**
1. Identify shortest path
2. Score path strength
3. Draft intro request

**Output:**
- Intro path + confidence

### 3. Engagement Alerts
**Process:**
1. Detect dormant ties
2. Trigger re-engagement prompts

**Output:**
- Outreach suggestions

## Data Model

### Relationship Score
```python
{
    "interaction_frequency": 0.8,
    "recency": 0.7,
    "influence_level": 0.9,
    "accessibility": 0.6,
    "score": 0.77
}
```

## Security & Privacy
- Limit access to trusted leadership
- Respect LinkedIn and email privacy policies
- Encrypt relationship metadata

## Success Metrics
- Warm intro conversion rate
- Referral pipeline generated per quarter
- Dormant relationship reactivation rate

## Cost Estimates
- Graph storage: ~$20/month
- Data enrichment: ~$25/month
- Total: ~$45/month

## Rules
1. NEVER send outreach without human approval
2. Respect privacy and opt-out requests
3. Maintain transparency on data sources
