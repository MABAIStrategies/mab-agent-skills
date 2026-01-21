"""
Skill 02: Client Health Monitor - Service Layer
Core business logic for health scoring and churn prediction
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import numpy as np

# Shared modules
import sys
sys.path.append('/app')
from shared.logging import get_logger
from shared.database import FirestoreRepository, CacheManager, PostgresRepository
from shared.utils.llm import LLMClient

# Integrations
from integrations import (
    HubSpotClient,
    GoogleAnalyticsClient,
    GmailClient,
    CalendarClient
)

logger = get_logger(__name__, skill_name="client-health-monitor")
llm = LLMClient("client-health-monitor")
cache = CacheManager(prefix="health")

# Repositories
health_repo = FirestoreRepository("account_health")
account_repo = FirestoreRepository("accounts")
usage_repo = PostgresRepository("usage_metrics")


class ClientHealthService:
    """Service for calculating health scores and predicting churn"""
    
    def __init__(self):
        self.hubspot = HubSpotClient()
        self.analytics = GoogleAnalyticsClient()
        self.gmail = GmailClient()
        self.calendar = CalendarClient()
    
    async def calculate_health_score(
        self,
        account_id: str,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive health score for an account
        
        Args:
            account_id: Account ID
            force_refresh: Force recalculation
            
        Returns:
            Health score record
        """
        logger.info(f"Calculating health score for account: {account_id}")
        
        # Check cache unless force refresh
        cache_key = f"health_score_{account_id}"
        if not force_refresh and cache.exists(cache_key):
            return cache.get(cache_key)
        
        # Get account data
        account = account_repo.get(account_id)
        if not account:
            raise ValueError(f"Account not found: {account_id}")
        
        # Calculate component scores
        usage_velocity = await self._calculate_usage_velocity(account_id)
        engagement_cadence = await self._calculate_engagement_cadence(account_id)
        sentiment_score = await self._calculate_sentiment_score(account_id)
        financial_health = await self._calculate_financial_health(account_id)
        support_patterns = await self._calculate_support_patterns(account_id)
        
        # Weighted health score
        weights = {
            'usage_velocity': 0.30,
            'engagement_cadence': 0.25,
            'sentiment_score': 0.20,
            'financial_health': 0.15,
            'support_patterns': 0.10
        }
        
        component_scores = {
            'usage_velocity': usage_velocity,
            'engagement_cadence': engagement_cadence,
            'sentiment_score': sentiment_score,
            'financial_health': financial_health,
            'support_patterns': support_patterns
        }
        
        health_score = sum(
            component_scores[k] * weights[k]
            for k in weights
        )
        
        # Classify status
        if health_score >= 70:
            status = "green"
        elif health_score >= 40:
            status = "yellow"
        else:
            status = "red"
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(component_scores, account_id)
        
        # Build health record
        health_record = {
            "account_id": account_id,
            "account_name": account.get("name"),
            "health_score": round(health_score, 2),
            "status": status,
            "component_scores": {k: round(v, 2) for k, v in component_scores.items()},
            "risk_factors": risk_factors,
            "last_calculated": datetime.utcnow().isoformat(),
            "csm_assigned": account.get("csm_assigned")
        }
        
        # Save to Firestore
        health_repo.create(f"health_{account_id}", health_record)
        
        # Cache for 12 hours
        cache.set(cache_key, health_record, expire_seconds=43200)
        
        # Alert if status changed to red
        if status == "red":
            await self._send_red_alert(account_id, health_record)
        
        return health_record
    
    async def _calculate_usage_velocity(self, account_id: str) -> float:
        """Calculate usage engagement score (0-100)"""
        
        # Get last 30 days of usage
        usage_data = usage_repo.execute_query(
            """
            SELECT 
                DATE(timestamp) as date,
                COUNT(DISTINCT user_id) as active_users,
                COUNT(*) as total_events
            FROM usage_events
            WHERE account_id = %s
              AND timestamp >= NOW() - INTERVAL '30 days'
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
            """,
            (account_id,)
        )
        
        if not usage_data:
            return 0.0
        
        # Calculate metrics
        avg_daily_users = np.mean([row['active_users'] for row in usage_data])
        avg_daily_events = np.mean([row['total_events'] for row in usage_data])
        days_active = len(usage_data)
        
        # Get baseline for this account (first 30 days)
        baseline = cache.get(f"baseline_usage_{account_id}")
        if not baseline:
            baseline = {
                'avg_users': avg_daily_users,
                'avg_events': avg_daily_events
            }
        
        # Score based on current vs baseline
        user_score = min((avg_daily_users / baseline['avg_users']) * 50, 50) if baseline['avg_users'] > 0 else 25
        event_score = min((avg_daily_events / baseline['avg_events']) * 30, 30) if baseline['avg_events'] > 0 else 15
        activity_score = (days_active / 30) * 20  # Max 20 points for daily usage
        
        return user_score + event_score + activity_score
    
    async def _calculate_engagement_cadence(self, account_id: str) -> float:
        """Calculate communication engagement score (0-100)"""
        
        # Get account contacts
        account = account_repo.get(account_id)
        csm_email = account.get("csm_email")
        contact_emails = account.get("contact_emails", [])
        
        if not csm_email or not contact_emails:
            return 50.0  # Neutral score if no data
        
        # Check email threads from last 30 days
        recent_emails = await self.gmail.search_threads(
            query=f"from:({' OR '.join(contact_emails)}) after:{(datetime.utcnow() - timedelta(days=30)).strftime('%Y/%m/%d')}",
            max_results=100
        )
        
        # Check meetings from last 30 days
        recent_meetings = await self.calendar.get_events(
            attendees=contact_emails,
            time_min=(datetime.utcnow() - timedelta(days=30)).isoformat(),
            time_max=datetime.utcnow().isoformat()
        )
        
        # Score email engagement
        email_count = len(recent_emails)
        email_score = min(email_count * 3, 50)  # Up to 50 points
        
        # Score meeting engagement
        meeting_count = len(recent_meetings)
        meeting_score = min(meeting_count * 10, 40)  # Up to 40 points
        
        # Response time bonus
        avg_response_time = await self._calculate_avg_response_time(recent_emails)
        if avg_response_time < 24:  # Hours
            response_bonus = 10
        elif avg_response_time < 48:
            response_bonus = 5
        else:
            response_bonus = 0
        
        return min(email_score + meeting_score + response_bonus, 100)
    
    async def _calculate_sentiment_score(self, account_id: str) -> float:
        """Analyze sentiment from communications (0-100)"""
        
        account = account_repo.get(account_id)
        contact_emails = account.get("contact_emails", [])
        
        if not contact_emails:
            return 50.0  # Neutral
        
        # Get recent emails
        recent_emails = await self.gmail.search_threads(
            query=f"from:({' OR '.join(contact_emails)}) after:{(datetime.utcnow() - timedelta(days=14)).strftime('%Y/%m/%d')}",
            max_results=20
        )
        
        # Analyze sentiment with LLM
        if not recent_emails:
            return 50.0
        
        # Extract email text
        email_texts = []
        for email in recent_emails:
            email_texts.append(email.get('snippet', ''))
        
        combined_text = '\n---\n'.join(email_texts[:10])  # Limit for token budget
        
        # LLM sentiment analysis
        sentiment_analysis = llm.generate_structured(
            prompt=f"""Analyze the overall sentiment in these recent client emails:

{combined_text}

Rate the sentiment on a scale of 0-100 where:
- 0-30: Very negative (frustrated, angry, dissatisfied)
- 31-50: Somewhat negative (concerned, disappointed)
- 51-70: Neutral to slightly positive
- 71-90: Positive (satisfied, happy)
- 91-100: Very positive (enthusiastic, delighted)

Return JSON with:
- score: 0-100
- reasoning: Brief explanation
- red_flags: List of concerning phrases""",
            output_schema={
                "score": "number",
                "reasoning": "string",
                "red_flags": ["string"]
            }
        )
        
        return sentiment_analysis.get('score', 50.0)
    
    async def _calculate_financial_health(self, account_id: str) -> float:
        """Calculate financial health score (0-100)"""
        
        account = account_repo.get(account_id)
        
        # Payment status
        payment_status = account.get("payment_status", "current")
        if payment_status == "current":
            payment_score = 40
        elif payment_status == "overdue_15":
            payment_score = 20
        elif payment_status == "overdue_30":
            payment_score = 10
        else:
            payment_score = 0
        
        # Contract proximity to renewal
        contract_end = account.get("contract_end_date")
        if contract_end:
            days_to_renewal = (datetime.fromisoformat(contract_end) - datetime.utcnow()).days
            if days_to_renewal > 180:
                renewal_score = 30
            elif days_to_renewal > 90:
                renewal_score = 20
            elif days_to_renewal > 30:
                renewal_score = 10
            else:
                renewal_score = 0
        else:
            renewal_score = 20
        
        # MRR trend
        current_mrr = account.get("mrr", 0)
        initial_mrr = account.get("initial_mrr", current_mrr)
        
        if current_mrr >= initial_mrr * 1.2:
            mrr_score = 30  # Expanded
        elif current_mrr >= initial_mrr:
            mrr_score = 20  # Stable
        elif current_mrr >= initial_mrr * 0.8:
            mrr_score = 10  # Slight decline
        else:
            mrr_score = 0  # Significant decline
        
        return payment_score + renewal_score + mrr_score
    
    async def _calculate_support_patterns(self, account_id: str) -> float:
        """Calculate support health score (0-100)"""
        
        # Get support tickets from last 30 days
        tickets = await self.hubspot.get_tickets(
            account_id=account_id,
            created_after=(datetime.utcnow() - timedelta(days=30)).isoformat()
        )
        
        if not tickets:
            return 100.0  # No tickets = healthy
        
        # Count escalated tickets
        escalated = sum(1 for t in tickets if t.get('priority') in ['high', 'critical'])
        
        # Calculate ticket velocity
        ticket_count = len(tickets)
        
        # Score
        if ticket_count == 0:
            base_score = 100
        elif ticket_count <= 2:
            base_score = 80
        elif ticket_count <= 5:
            base_score = 60
        elif ticket_count <= 10:
            base_score = 40
        else:
            base_score = 20
        
        # Penalty for escalations
        escalation_penalty = escalated * 10
        
        return max(base_score - escalation_penalty, 0)
    
    def _identify_risk_factors(
        self,
        component_scores: Dict[str, float],
        account_id: str
    ) -> List[str]:
        """Identify specific risk factors"""
        
        risk_factors = []
        
        if component_scores['usage_velocity'] < 40:
            risk_factors.append("Low product usage velocity")
        
        if component_scores['engagement_cadence'] < 40:
            risk_factors.append("Declining communication engagement")
        
        if component_scores['sentiment_score'] < 50:
            risk_factors.append("Negative sentiment in communications")
        
        if component_scores['financial_health'] < 40:
            risk_factors.append("Financial health concerns")
        
        if component_scores['support_patterns'] < 60:
            risk_factors.append("High support ticket volume")
        
        return risk_factors
    
    async def predict_churn(
        self,
        account_id: str,
        window_days: int = 30
    ) -> Dict[str, Any]:
        """
        Predict churn probability using ML model
        
        Args:
            account_id: Account ID
            window_days: Prediction window (30, 60, or 90)
            
        Returns:
            Churn prediction
        """
        # Get health record
        health_record = health_repo.get(f"health_{account_id}")
        if not health_record:
            health_record = await self.calculate_health_score(account_id)
        
        # Simple probability model (replace with ML model in production)
        health_score = health_record['health_score']
        
        # Base probability from health score
        if health_score >= 70:
            base_probability = 5  # 5% churn risk
        elif health_score >= 50:
            base_probability = 20
        elif health_score >= 30:
            base_probability = 50
        else:
            base_probability = 80
        
        # Adjust for window
        window_multiplier = {30: 1.0, 60: 1.3, 90: 1.5}
        adjusted_probability = min(base_probability * window_multiplier.get(window_days, 1.0), 95)
        
        # Predicted date
        if adjusted_probability > 50:
            predicted_date = (datetime.utcnow() + timedelta(days=window_days // 2)).isoformat()
        else:
            predicted_date = None
        
        # Confidence
        confidence = "high" if health_score < 30 or health_score > 80 else "medium"
        
        return {
            "account_id": account_id,
            "churn_probability": round(adjusted_probability, 1),
            "prediction_window_days": window_days,
            "predicted_churn_date": predicted_date,
            "confidence": confidence,
            "primary_risk_factors": health_record.get('risk_factors', [])
        }
    
    async def generate_retention_campaign(
        self,
        account: Dict[str, Any],
        health_record: Dict[str, Any],
        campaign_type: str = "email"
    ) -> Dict[str, Any]:
        """
        Generate personalized retention campaign using LLM
        
        Args:
            account: Account data
            health_record: Health score data
            campaign_type: email | call | executive_engagement
            
        Returns:
            Campaign content
        """
        # Build context
        context = {
            "account_name": account.get("name"),
            "health_score": health_record.get("health_score"),
            "status": health_record.get("status"),
            "risk_factors": health_record.get("risk_factors"),
            "industry": account.get("industry"),
            "product_usage": health_record.get("component_scores", {}).get("usage_velocity"),
            "csm_name": account.get("csm_name", "Account Manager")
        }
        
        # Generate campaign with LLM
        if campaign_type == "email":
            campaign = llm.generate_structured(
                prompt=f"""Generate a personalized retention email campaign for this at-risk account:

Account: {context['account_name']}
Industry: {context['industry']}
Health Status: {context['status'].upper()} ({context['health_score']}/100)
Risk Factors: {', '.join(context['risk_factors'])}

Create a 3-email sequence:
Email 1: Check-in and value reminder (send immediately)
Email 2: Success story + offer (send +3 days)
Email 3: Executive outreach offer (send +7 days)

Return JSON with email objects containing subject and body.""",
                output_schema={
                    "emails": [
                        {
                            "sequence": "number",
                            "subject": "string",
                            "body": "string",
                            "send_delay_days": "number"
                        }
                    ]
                }
            )
        else:
            campaign = llm.generate_structured(
                prompt=f"""Generate a retention campaign plan for {campaign_type}:

Account: {context['account_name']}
Status: {context['status']}
Risk Factors: {', '.join(context['risk_factors'])}

Provide:
- Talking points
- Value propositions to emphasize
- Offers to make
- Success metrics to reference""",
                output_schema={
                    "talking_points": ["string"],
                    "value_props": ["string"],
                    "offers": ["string"],
                    "success_metrics": ["string"]
                }
            )
        
        return campaign
    
    async def get_top_risk_factors(self, timeframe_days: int = 30) -> List[Dict[str, Any]]:
        """Get most common risk factors across at-risk accounts"""
        
        # Get all red/yellow accounts
        at_risk = health_repo.list(
            filters=[("status", "in", ["red", "yellow"])],
            limit=1000
        )
        
        # Count risk factors
        risk_factor_counts = {}
        for account_health in at_risk:
            for factor in account_health.get("risk_factors", []):
                risk_factor_counts[factor] = risk_factor_counts.get(factor, 0) + 1
        
        # Sort by frequency
        sorted_factors = sorted(
            risk_factor_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [
            {"factor": factor, "count": count}
            for factor, count in sorted_factors[:10]
        ]
    
    async def _send_red_alert(self, account_id: str, health_record: Dict[str, Any]):
        """Send alert when account goes red"""
        
        from integrations import SlackIntegration
        slack = SlackIntegration()
        
        message = f"""🚨 **CHURN ALERT: Account Red Status**

**Account:** {health_record['account_name']}
**Health Score:** {health_record['health_score']}/100
**CSM:** {health_record.get('csm_assigned', 'Unassigned')}

**Risk Factors:**
{chr(10).join(['• ' + factor for factor in health_record.get('risk_factors', [])])}

**Action Required:** Immediate intervention needed within 24 hours.
"""
        
        await slack.send_message(
            channel="#churn-alerts",
            text=message
        )
    
    async def _calculate_avg_response_time(self, emails: List[Dict]) -> float:
        """Calculate average response time in hours"""
        # Implementation placeholder
        return 24.0  # Default 24 hours
