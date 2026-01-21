# Skill 01: Competitive Intelligence War Room

## Description
Real-time tracking of competitor activities, pricing changes, product launches, and market positioning to maintain strategic advantage for MAB AI Strategies.

## Capabilities
- Monitor competitor websites for changes (pricing, product launches, messaging)
- Track LinkedIn activity (job postings, company updates)
- Generate competitive battlecards automatically
- Alert on significant competitor moves
- Maintain competitive intelligence repository

## Triggers
- "Monitor [Company Name]'s AI consulting pricing"
- "Alert me when [Competitor] launches new products"
- "Generate battlecard: MAB vs [Competitor]"
- "What did [Competitor] announce this week?"
- "Track [Competitor] hiring activity"

## Integration Requirements
- Web scraping (Playwright/Beautiful Soup)
- LinkedIn Sales Navigator API
- Google Alerts
- Notion (intelligence repository)
- Slack (alerts)
- HubSpot (opportunity linking)

## Workflow

### 1. Competitor Registration
**Input:**
- Competitor name
- Website URL
- LinkedIn page URL
- Key pages to monitor (pricing, products, about)
- Alert thresholds

**Process:**
1. Validate URLs
2. Create competitor profile in Firestore
3. Take initial snapshots
4. Schedule monitoring jobs

**Output:**
- Competitor profile ID
- Monitoring schedule confirmation

### 2. Website Monitoring
**Automated (Daily):**
1. Crawl registered pages
2. Calculate diff from last snapshot
3. If change > threshold:
   - Extract changed sections
   - LLM analysis for strategic implications
   - Generate alert
   - Update Notion database
   - Post to Slack

### 3. Battlecard Generation
**Input:**
- Our company: MAB AI Strategies
- Competitor company
- Focus areas (optional)

**Process:**
1. Retrieve latest intelligence on competitor
2. Analyze our strengths vs their offerings
3. Generate battlecard with:
   - Feature comparison matrix
   - Pricing analysis
   - Win themes
   - Objection handling
   - Recent news/updates

**Output:**
- Formatted battlecard document
- PDF export
- Notion page link

## Data Model

### Competitor Profile
```python
{
    "id": "competitor_id",
    "name": "Company Name",
    "website": "https://example.com",
    "linkedin_url": "https://linkedin.com/company/...",
    "monitored_pages": {
        "pricing": "https://example.com/pricing",
        "products": "https://example.com/products",
        "about": "https://example.com/about"
    },
    "alert_thresholds": {
        "pricing_change_percent": 5,
        "content_change_percent": 10
    },
    "last_crawled": "2026-01-20T10:00:00Z",
    "created_at": "2026-01-01T00:00:00Z",
    "active": true
}
```

### Intelligence Entry
```python
{
    "id": "intel_id",
    "competitor_id": "competitor_id",
    "type": "pricing_change | product_launch | content_update | hiring",
    "detected_at": "2026-01-20T10:00:00Z",
    "severity": "high | medium | low",
    "summary": "Brief description",
    "details": {
        "old_value": "...",
        "new_value": "...",
        "diff_percent": 15.5,
        "affected_pages": ["url1", "url2"]
    },
    "strategic_implications": "LLM-generated analysis",
    "alerted": true,
    "notion_url": "https://notion.so/...",
    "related_opportunities": ["opp_id_1"]
}
```

## Security & Privacy
- Respect robots.txt
- Rate limiting on crawls
- No unauthorized access
- Public information only (OSINT)
- Encrypt stored intelligence
- Access restricted to sales/strategy roles

## Success Metrics
- Competitive moves detected 72+ hours before public announcement
- Battlecard factual accuracy: >95%
- Sales wins attributed to insights: track conversion lift
- False positive rate: <5%
- Average time from detection to alert: <30 minutes

## Cost Estimates
- Web scraping: ~$20/month (Playwright hosting)
- LLM analysis: ~$50/month (5 competitors, daily monitoring)
- Storage: ~$5/month
- **Total: ~$75/month**

## Rules
1. NEVER invent competitor data - only report what's verifiably observed
2. ALWAYS cite sources with URLs and timestamps
3. Flag low-confidence insights clearly
4. Respect rate limits and crawl budgets
5. Prioritize accuracy over speed
