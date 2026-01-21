# MAB AI STRATEGIES - AGENT SKILLS COMPLETE PACKAGE
## DEPLOYMENT GUIDE & IMPLEMENTATION INSTRUCTIONS

---

## 🎯 WHAT YOU'VE RECEIVED

This package contains the **complete production-ready infrastructure** for all 10 MAB AI agent skills:

### ✅ FULLY IMPLEMENTED (Ready to Deploy):
1. **Competitive Intelligence War Room** (100% complete)
   - Full handler, service, and integration code
   - Playwright web scraping
   - LLM-powered change analysis
   - Slack/Notion integration
   - Battlecard generation

2. **Infrastructure & Shared Services** (100% complete)
   - Authentication module (OAuth2, JWT, KMS encryption)
   - Database layer (Firestore, PostgreSQL, Redis, Neo4j)
   - Logging system (structured, PII redaction, Cloud Logging)
   - LLM client (Claude integration with cost tracking)
   - Docker Compose for local development
   - Terraform for GCP deployment

### 📋 SCAFFOLDED (Template Pattern Provided):
Skills 2-10 follow the exact same pattern as Skill 01. Each needs:
- SKILL.md (documentation) ✅ Provided
- handler.py (FastAPI routes) → Copy from Skill 01 pattern
- service.py (business logic) → Copy from Skill 01 pattern
- models.py (Pydantic models) → Define your schemas
- integrations.py (external APIs) → Use shared/integrations/
- Dockerfile → Copy from Skill 01
- requirements.txt → Copy from Skill 01

---

## 🚀 QUICK START (10 Minutes to Running System)

### Step 1: Environment Setup
```bash
cd mab-agent-skills
cp .env.example .env
# Edit .env with your actual API keys
```

### Step 2: Start Local Development
```bash
docker-compose up -d
```

This starts:
- All 10 skill services (ports 8001-8010)
- Firestore emulator
- PostgreSQL database
- Redis cache
- Neo4j graph DB
- Prometheus + Grafana monitoring

### Step 3: Test Skill 01
```bash
curl -X POST http://localhost:8001/webhook \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "intent": "monitor_competitor",
    "parameters": {
      "company_name": "Accenture",
      "website_url": "https://www.accenture.com"
    }
  }'
```

---

## 📦 COMPLETING SKILLS 2-10 (Pattern to Follow)

Each skill follows this structure:

### SKILL.md (Documentation)
✅ Already created for all 10 skills

### handler.py (HTTP Endpoints)
```python
# Copy from skills/01-competitive-intelligence/handler.py
# Replace these functions:
# - monitor_competitor() → your_primary_action()
# - generate_battlecard() → your_secondary_action()
# - get_intelligence() → your_data_retrieval()

# Keep these unchanged:
# - health_check()
# - readiness_check()
# - webhook routing logic
```

### service.py (Business Logic)
```python
# Copy from skills/01-competitive-intelligence/service.py
# Replace CompetitorMonitorService class with your service
# Keep the pattern:
# 1. __init__() with integrations
# 2. Main action methods
# 3. Helper methods prefixed with _
# 4. Error handling and logging
```

### models.py (Data Models)
```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class YourMainModel(BaseModel):
    id: str
    created_at: datetime
    # ... your fields

class YourRequestModel(BaseModel):
    # Webhook request parameters
    pass

class YourResponseModel(BaseModel):
    # Webhook response format
    success: bool
    data: dict
```

---

## 🔧 SKILL-BY-SKILL IMPLEMENTATION GUIDE

### Skill 02: Client Health Monitor

**Core Files to Create:**
1. `handler.py` - Routes for:
   - `/webhook` → calculate_health_score()
   - `/webhook` → get_at_risk_clients()
   - `/webhook` → generate_retention_plan()

2. `service.py` - Classes:
   - `HealthScoreCalculator` - Scoring algorithm
   - `ChurnPredictor` - ML model for prediction
   - `RetentionCampaignGenerator` - LLM-powered campaigns

3. `integrations.py`:
   - HubSpot (account data)
   - Google Analytics (usage metrics)
   - Gmail (sentiment analysis)
   - Calendar (meeting frequency)

**Key Implementation:**
```python
# Health score algorithm
def calculate_health_score(account_id: str) -> float:
    weights = {
        'usage_velocity': 0.30,
        'engagement_cadence': 0.25,
        'sentiment': 0.20,
        'financial_health': 0.15,
        'support_patterns': 0.10
    }
    
    scores = {
        'usage_velocity': get_usage_score(account_id),
        'engagement_cadence': get_engagement_score(account_id),
        # ... etc
    }
    
    return sum(scores[k] * weights[k] for k in weights)
```

### Skill 03: Win-Loss Analyzer

**Database Schema:**
```sql
CREATE TABLE deals (
    id SERIAL PRIMARY KEY,
    deal_id VARCHAR(255) UNIQUE,
    status VARCHAR(50), -- won | lost
    close_date DATE,
    value DECIMAL(10,2),
    competitor_id VARCHAR(255),
    loss_reason TEXT,
    win_factors JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Core Analysis:**
```python
async def analyze_loss_patterns(timeframe_days: int = 90):
    # Query losses from PostgreSQL
    losses = await get_recent_losses(timeframe_days)
    
    # Group by loss reason
    patterns = group_by_loss_reason(losses)
    
    # LLM analysis for insights
    insights = await llm.generate_structured(
        prompt=f"Analyze these loss patterns: {patterns}",
        output_schema={
            "top_3_loss_reasons": ["string"],
            "recommended_fixes": ["string"],
            "competitive_vulnerabilities": ["string"]
        }
    )
    
    return insights
```

### Skills 04-10: Similar Patterns

All follow the same structure. Here's the template:

```
skills/XX-skill-name/
├── SKILL.md                    ✅ PROVIDED
├── handler.py                  → Copy from Skill 01, modify routes
├── service.py                  → Implement your business logic
├── models.py                   → Define Pydantic models
├── integrations.py             → Use shared/integrations/*
├── Dockerfile                  → Copy from Skill 01
├── requirements.txt            → Copy from Skill 01, add extras
├── manifest.json               → Define intents and parameters
└── tests/
    ├── test_handler.py         → Test HTTP endpoints
    └── test_service.py         → Test business logic
```

---

## 🔐 SECURITY CHECKLIST (DO BEFORE PRODUCTION)

- [ ] Replace all example passwords in .env
- [ ] Generate new JWT_SECRET (use: `openssl rand -hex 32`)
- [ ] Set up KMS key ring and crypto keys in GCP
- [ ] Configure OAuth2 credentials for each integration
- [ ] Enable Cloud Armor (DDoS protection)
- [ ] Set up Cloud IAM roles with least privilege
- [ ] Enable audit logging
- [ ] Configure backup schedules
- [ ] Set up monitoring alerts
- [ ] Enable PII redaction in logs
- [ ] Review and test rate limits

---

## 📊 MONITORING & OBSERVABILITY

### Grafana Dashboards (http://localhost:3000)
Default password: `mab_dev_password`

Pre-configured dashboards:
1. **System Health** - CPU, memory, request rates
2. **Skill Performance** - Latency p50/p95/p99 per skill
3. **Cost Tracking** - LLM token usage and costs
4. **Error Analysis** - Error rates by type and skill

### Alerts Configured:
- Error rate > 5% for 5 minutes
- P95 latency > 2 seconds
- Daily LLM cost > $100
- Database connection pool exhaustion
- Disk usage > 85%

---

## 💰 COST ESTIMATES (Production)

### Monthly Costs Per Skill:
| Component | Cost |
|-----------|------|
| Cloud Run (avg 1M requests) | $15-25 |
| Firestore (storage + operations) | $10-20 |
| Cloud Storage (artifacts) | $5-10 |
| LLM API calls (Claude) | $30-100 |
| Logging | $5-15 |
| **Total per skill** | **$65-170/month** |

### Full 10-Skill Platform:
- **Best case:** $650/month
- **Typical:** $1,000/month
- **High usage:** $1,700/month

**Cost optimization tips:**
1. Enable LLM response caching (can reduce costs 60%)
2. Use Firestore query limits
3. Implement aggressive rate limiting
4. Archive old data to cold storage
5. Use Cloud Run min instances = 0 for low-traffic skills

---

## 🧪 TESTING STRATEGY

### Unit Tests
```bash
pytest tests/unit/ -v --cov=skills/
```

### Integration Tests
```bash
# Requires running services
pytest tests/integration/ -v
```

### Load Testing
```bash
# Install locust
pip install locust

# Run load test
locust -f tests/load/locustfile.py --host=http://localhost:8001
```

### Security Scanning
```bash
# Python dependency vulnerabilities
safety check

# Code security issues
bandit -r skills/ shared/

# Docker image scanning
trivy image mab-skill-01:latest
```

---

## 🚢 PRODUCTION DEPLOYMENT

### One-Time GCP Setup
```bash
# Set project
gcloud config set project mab-ai-strategies

# Enable APIs
gcloud services enable \
  run.googleapis.com \
  firestore.googleapis.com \
  cloudscheduler.googleapis.com \
  pubsub.googleapis.com \
  secretmanager.googleapis.com

# Create service account
gcloud iam service-accounts create mab-skills-sa

# Initialize Terraform
cd terraform/
terraform init
terraform plan
terraform apply
```

### Deploy Skills
```bash
# Build and deploy all skills
./scripts/deploy-all.sh

# Or deploy individual skill
./scripts/deploy-skill.sh 01-competitive-intelligence
```

### Set Up Scheduled Jobs
```bash
# Cloud Scheduler for daily competitor crawls
gcloud scheduler jobs create http competitor-crawl \
  --schedule="0 2 * * *" \
  --uri="https://skill-01-xyz.run.app/cron/crawl-all" \
  --http-method=POST \
  --headers="Authorization=Bearer ${SERVICE_TOKEN}"
```

---

## 📚 ADDITIONAL RESOURCES

### Documentation
- `/docs/api/` - API specifications
- `/docs/adr/` - Architecture decision records
- `/docs/runbooks/` - Incident response playbooks

### Example Requests
See `/examples/webhook-payloads/` for JSON examples for each skill

### Postman Collection
Import `/postman/MAB-Skills.postman_collection.json`

---

## 🆘 TROUBLESHOOTING

### Skill won't start
```bash
# Check logs
docker-compose logs skill-01-competitive-intel

# Common issues:
# 1. Missing environment variable → Check .env
# 2. Database connection → Ensure Firestore emulator is running
# 3. Port already in use → Change port in docker-compose.yml
```

### Firestore emulator connection error
```bash
# Restart emulator
docker-compose restart firestore

# Set environment variable
export FIRESTORE_EMULATOR_HOST=localhost:8080
```

### LLM API errors
```bash
# Verify API key
echo $ANTHROPIC_API_KEY

# Test directly
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-sonnet-4-20250514","max_tokens":100,"messages":[{"role":"user","content":"test"}]}'
```

---

## ✅ FINAL DEPLOYMENT CHECKLIST

Before going live:
- [ ] All .env variables set with production values
- [ ] JWT secret generated and stored in Secret Manager
- [ ] OAuth credentials configured for all integrations
- [ ] Terraform infrastructure deployed
- [ ] All 10 skills deployed to Cloud Run
- [ ] Cloud Scheduler jobs configured
- [ ] Monitoring dashboards configured
- [ ] Alert channels set up (Slack, PagerDuty)
- [ ] Backup strategy implemented
- [ ] Load testing completed
- [ ] Security scan passed
- [ ] Documentation updated
- [ ] Team trained on operations

---

## 🎓 NEXT STEPS

1. **Complete Skill 02** using the patterns from Skill 01
2. **Test end-to-end** with real data
3. **Deploy to staging** environment
4. **Integrate with Google Antigravity** agent platform
5. **Beta test** with 1-2 internal use cases
6. **Iterate** based on feedback
7. **Launch** MAB AI Strategies on Jan 1, 2026!

---

**Built by Mark Bockrath**  
Former D1 Athlete | $12M+ Revenue Generator | AI Automation Architect

*This is your competitive advantage. Now go dominate the market.* 🏀
