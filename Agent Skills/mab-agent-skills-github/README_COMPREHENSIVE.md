# MAB AI Strategies - Agent Skills Platform

**Production-Ready AI Agent Skills for Enterprise Consulting**

This repository contains 10 advanced business productivity agent skills built for MAB AI Strategies LLC. Each skill is a fully-functional microservice with webhooks, integrations, and security controls.

## 🚀 Quick Start

```bash
# Clone the repository
git clone <your-repo-url>
cd mab-agent-skills

# Copy environment template
cp .env.example .env
# Edit .env with your credentials

# Install dependencies
pip install -r requirements.txt
npm install

# Start all services locally
docker-compose up -d

# Run tests
pytest tests/

# Deploy to Google Cloud
gcloud builds submit --config cloudbuild.yaml
```

## 📋 Skills Overview

| # | Skill | Purpose | Status |
|---|-------|---------|--------|
| 1 | **Competitive Intelligence War Room** | Track competitor activities, pricing, launches | ✅ Ready |
| 2 | **Client Health Monitor** | Predict churn, trigger retention campaigns | ✅ Ready |
| 3 | **Win-Loss Analyzer** | Analyze deal patterns, improve close rates | ✅ Ready |
| 4 | **Content Repurposing Engine** | 1 asset → 20+ platform variants | ✅ Ready |
| 5 | **Conversation Intelligence** | Extract insights from sales calls | ✅ Ready |
| 6 | **Contract Risk Detector** | Auto-review contracts for unfavorable terms | ✅ Ready |
| 7 | **Upsell Identifier** | Find expansion revenue opportunities | ✅ Ready |
| 8 | **Network Mapper** | Leverage 5K+ connections for warm intros | ✅ Ready |
| 9 | **Demo Generator** | Instant custom demo environments | ✅ Ready |
| 10 | **Revenue Forecasting** | AI-powered sales forecasting | ✅ Ready |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│          Google Antigravity Agent Platform          │
│              (Agent Manager + Planner)              │
└────────────────────┬────────────────────────────────┘
                     │
                     │ Webhook Calls (JWT Auth)
                     │
┌────────────────────▼────────────────────────────────┐
│              Cloud Load Balancer                     │
│           (SSL Termination, DDoS Protection)        │
└────────────────────┬────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
┌────────▼────────┐    ┌────────▼────────┐
│  Cloud Run      │    │  Cloud Run      │
│  Skill 1-5      │    │  Skill 6-10     │
│  (Containers)   │    │  (Containers)   │
└────────┬────────┘    └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
┌────────▼────────┐    ┌────────▼────────┐
│   Firestore     │    │  Cloud Storage  │
│   (State/Data)  │    │  (Artifacts)    │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────┬───────────┘
                     │
         ┌───────────▼───────────┐
         │   External APIs       │
         │ Gmail, HubSpot, etc.  │
         └───────────────────────┘
```

## 🔧 Technology Stack

- **Runtime:** Python 3.11+ with FastAPI
- **Database:** Firestore (NoSQL), Cloud SQL (PostgreSQL for analytics)
- **Storage:** Cloud Storage for artifacts
- **Auth:** OAuth2 with KMS-encrypted tokens
- **Messaging:** Pub/Sub for async tasks
- **Monitoring:** Cloud Logging + Cloud Monitoring
- **Deployment:** Docker + Cloud Run (auto-scaling)
- **IaC:** Terraform for infrastructure

## 📦 Skill Structure

Each skill follows this pattern:

```
skills/XX-skill-name/
├── SKILL.md              # Agent prompt & documentation
├── manifest.json         # Skill registration config
├── handler.py            # Main webhook handler
├── service.py            # Business logic
├── models.py             # Data models
├── integrations.py       # External API calls
├── schemas/
│   ├── input.json        # Request schema
│   └── output.json       # Response schema
├── templates/            # Document templates
├── Dockerfile
├── requirements.txt
└── tests/
    ├── test_handler.py
    └── test_service.py
```

## 🔐 Security

- **OAuth2 Scopes:** Least-privilege per skill
- **Encryption:** KMS for secrets, TLS 1.3 for transit
- **Authentication:** JWT signature validation on all webhooks
- **Authorization:** RBAC with user/role-based access
- **Audit:** All actions logged with user context
- **PII Protection:** Redaction in logs, encryption at rest
- **Rate Limiting:** Per-user and per-skill limits
- **Compliance:** GDPR, HIPAA, SOC 2 ready

## 🧪 Testing

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests (requires credentials)
pytest tests/integration/ -v

# Load testing
locust -f tests/load/locustfile.py

# Security scanning
bandit -r skills/ shared/
safety check
```

## 🚢 Deployment

### Local Development
```bash
docker-compose up -d
# Services available at:
# - Skill 1: http://localhost:8001
# - Skill 2: http://localhost:8002
# - etc.
```

### Production (Google Cloud)
```bash
# One-time setup
cd terraform/
terraform init
terraform plan
terraform apply

# Deploy updates
gcloud builds submit --config cloudbuild.yaml

# Monitor
gcloud logging read "resource.type=cloud_run_revision"
```

## 🔧 Configuration

Edit `.env` file:

```bash
# Google Cloud
GCP_PROJECT_ID=mab-ai-strategies
GCP_REGION=us-central1

# Authentication
OAUTH_CLIENT_ID=your-client-id
OAUTH_CLIENT_SECRET=your-secret
JWT_SECRET=your-jwt-secret

# Integrations
HUBSPOT_API_KEY=your-key
NOTION_API_KEY=your-key
LINKEDIN_CLIENT_ID=your-id
SLACK_WEBHOOK_URL=your-webhook

# LLM
ANTHROPIC_API_KEY=your-key
OPENAI_API_KEY=your-key

# Database
FIRESTORE_DATABASE=mab-production
POSTGRES_CONNECTION_STRING=postgresql://user:pass@host:5432/db

# Feature Flags
ENABLE_SKILL_01=true
ENABLE_SKILL_02=true
# ... etc
```

## 📊 Monitoring & Observability

Each skill exposes:
- `/health` - Health check endpoint
- `/metrics` - Prometheus metrics
- `/ready` - Readiness probe

Key metrics tracked:
- Request latency (p50, p95, p99)
- Error rate by type
- Success rate
- API call success/failure
- LLM token usage
- Cost per request

Dashboards available in Cloud Monitoring for:
- System health overview
- Per-skill performance
- Cost tracking
- User activity
- Error analysis

## 🆘 Support & Maintenance

- **Logs:** `gcloud logging read "resource.type=cloud_run_revision"`
- **Alerts:** Configured for error spikes, latency issues
- **Incident Response:** See `docs/runbooks/`
- **Backups:** Daily Firestore exports to Cloud Storage
- **Updates:** Rolling updates with zero downtime

## 📚 Documentation

- [Architecture Decision Records](docs/adr/)
- [API Documentation](docs/api/)
- [Integration Guides](docs/integrations/)
- [Runbooks](docs/runbooks/)
- [Security Policies](docs/security/)

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/skill-name`
2. Make changes and test: `pytest tests/`
3. Submit PR with description
4. Automated tests run via Cloud Build
5. Code review required before merge

## 📄 License

Proprietary - MAB AI Strategies LLC - All Rights Reserved

---

**Built with 🏀 by Mark Bockrath**  
*Former D1 Athlete | $12M+ Revenue Generator | AI Automation Architect*
