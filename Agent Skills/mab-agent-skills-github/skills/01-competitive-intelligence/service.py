"""
Skill 01: Competitive Intelligence - Service Layer
Core business logic for monitoring and analysis
"""

import os
import hashlib
import difflib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

# Web scraping
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

# Shared modules
import sys
sys.path.append('/app')
from shared.logging import get_logger
from shared.database import FirestoreRepository, CacheManager
from shared.utils.llm import LLMClient, PromptTemplate

# Integrations
from integrations import (
    NotionClient,
    SlackClient,
    LinkedInClient
)

logger = get_logger(__name__, skill_name="competitive-intelligence")
llm = LLMClient("competitive-intelligence")
cache = CacheManager(prefix="competitor")

# Repositories
competitor_repo = FirestoreRepository("competitors")
intel_repo = FirestoreRepository("intelligence")
snapshot_repo = FirestoreRepository("competitor_snapshots")


class CompetitorMonitorService:
    """Service for monitoring competitors"""
    
    def __init__(self):
        self.notion = NotionClient()
        self.slack = SlackClient()
        self.linkedin = LinkedInClient()
    
    async def crawl_competitor(
        self,
        competitor_id: str,
        is_initial: bool = False
    ) -> Dict[str, Any]:
        """
        Crawl competitor websites and detect changes
        
        Args:
            competitor_id: Competitor ID
            is_initial: Whether this is first crawl
            
        Returns:
            Crawl results with detected changes
        """
        logger.info(f"Crawling competitor: {competitor_id}")
        
        # Get competitor profile
        competitor = competitor_repo.get(competitor_id)
        if not competitor:
            raise ValueError(f"Competitor not found: {competitor_id}")
        
        results = {
            "competitor_id": competitor_id,
            "crawled_at": datetime.utcnow().isoformat(),
            "pages_crawled": [],
            "changes_detected": [],
            "errors": []
        }
        
        # Crawl each monitored page
        for page_type, url in competitor['monitored_pages'].items():
            try:
                page_data = await self._crawl_page(url)
                
                # Store snapshot
                snapshot_id = f"{competitor_id}_{page_type}_{int(datetime.utcnow().timestamp())}"
                snapshot_repo.create(snapshot_id, {
                    "competitor_id": competitor_id,
                    "page_type": page_type,
                    "url": url,
                    "content_hash": page_data['content_hash'],
                    "text_content": page_data['text'],
                    "screenshot_url": page_data.get('screenshot_url'),
                    "crawled_at": datetime.utcnow()
                })
                
                results['pages_crawled'].append(page_type)
                
                # Compare with previous snapshot (if not initial)
                if not is_initial:
                    changes = await self._detect_changes(
                        competitor_id,
                        page_type,
                        page_data
                    )
                    
                    if changes:
                        results['changes_detected'].extend(changes)
                
            except Exception as e:
                logger.error(f"Error crawling {page_type}", error=e)
                results['errors'].append({
                    "page_type": page_type,
                    "error": str(e)
                })
        
        # Process detected changes
        if results['changes_detected']:
            await self._process_changes(competitor, results['changes_detected'])
        
        # Update competitor last_crawled
        competitor_repo.update(competitor_id, {
            "last_crawled": datetime.utcnow()
        })
        
        return results
    
    async def _crawl_page(self, url: str) -> Dict[str, Any]:
        """
        Crawl a single page using Playwright
        
        Args:
            url: Page URL to crawl
            
        Returns:
            Page data including content hash and text
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Navigate to page
            await page.goto(url, wait_until="networkidle")
            
            # Get page content
            html = await page.content()
            
            # Take screenshot (optional)
            screenshot_path = f"/tmp/screenshot_{hashlib.md5(url.encode()).hexdigest()}.png"
            await page.screenshot(path=screenshot_path)
            
            # Upload screenshot to Cloud Storage
            screenshot_url = await self._upload_screenshot(screenshot_path)
            
            await browser.close()
        
        # Parse HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        text = '\n'.join([line.strip() for line in text.splitlines() if line.strip()])
        
        # Calculate content hash
        content_hash = hashlib.sha256(text.encode()).hexdigest()
        
        return {
            "url": url,
            "html": html,
            "text": text,
            "content_hash": content_hash,
            "screenshot_url": screenshot_url,
            "crawled_at": datetime.utcnow().isoformat()
        }
    
    async def _detect_changes(
        self,
        competitor_id: str,
        page_type: str,
        current_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Detect changes from previous snapshot
        
        Returns:
            List of detected changes
        """
        # Get last snapshot
        snapshots = snapshot_repo.list(
            filters=[
                ("competitor_id", "==", competitor_id),
                ("page_type", "==", page_type)
            ],
            order_by="-crawled_at",
            limit=1
        )
        
        if not snapshots:
            return []
        
        previous = snapshots[0]
        
        # Quick check - same hash means no changes
        if previous['content_hash'] == current_data['content_hash']:
            return []
        
        changes = []
        
        # Calculate text diff
        diff = difflib.unified_diff(
            previous['text_content'].splitlines(),
            current_data['text'].splitlines(),
            lineterm=''
        )
        diff_text = '\n'.join(diff)
        
        # Calculate change percentage
        old_lines = len(previous['text_content'].splitlines())
        diff_lines = len([l for l in diff_text.splitlines() if l.startswith('+') or l.startswith('-')])
        change_percent = (diff_lines / old_lines * 100) if old_lines > 0 else 0
        
        # Get competitor for thresholds
        competitor = competitor_repo.get(competitor_id)
        threshold = competitor['alert_thresholds'].get('content_change_percent', 10)
        
        if change_percent >= threshold:
            # Use LLM to analyze changes
            analysis = await self._analyze_change(
                page_type=page_type,
                old_content=previous['text_content'][:3000],  # Limit for token budget
                new_content=current_data['text'][:3000],
                diff=diff_text[:2000]
            )
            
            changes.append({
                "page_type": page_type,
                "change_percent": round(change_percent, 2),
                "diff": diff_text,
                "analysis": analysis,
                "severity": self._classify_severity(change_percent, analysis),
                "detected_at": datetime.utcnow().isoformat()
            })
        
        return changes
    
    async def _analyze_change(
        self,
        page_type: str,
        old_content: str,
        new_content: str,
        diff: str
    ) -> Dict[str, Any]:
        """
        Use LLM to analyze detected changes
        
        Returns:
            Analysis with summary and implications
        """
        prompt = f"""Analyze this change detected on a competitor's {page_type} page.

OLD CONTENT (excerpt):
{old_content}

NEW CONTENT (excerpt):
{new_content}

DIFF:
{diff}

Provide analysis in JSON format:
{{
    "summary": "Brief description of what changed",
    "key_changes": ["list", "of", "key", "changes"],
    "strategic_implications": "What this means for our competitive position",
    "recommended_actions": ["specific", "actions", "to", "take"],
    "confidence": "high|medium|low"
}}"""
        
        analysis = llm.generate_structured(
            prompt=prompt,
            output_schema={
                "summary": "string",
                "key_changes": ["string"],
                "strategic_implications": "string",
                "recommended_actions": ["string"],
                "confidence": "string"
            }
        )
        
        return analysis
    
    def _classify_severity(
        self,
        change_percent: float,
        analysis: Dict[str, Any]
    ) -> str:
        """Classify change severity"""
        
        # High severity if significant change or high confidence
        if change_percent > 30 or analysis.get('confidence') == 'high':
            return "high"
        elif change_percent > 15:
            return "medium"
        else:
            return "low"
    
    async def _process_changes(
        self,
        competitor: Dict[str, Any],
        changes: List[Dict[str, Any]]
    ):
        """
        Process detected changes - create intelligence entries and alerts
        """
        for change in changes:
            # Create intelligence entry
            intel_entry = {
                "competitor_id": competitor['id'],
                "competitor_name": competitor['name'],
                "type": "content_update",
                "page_type": change['page_type'],
                "severity": change['severity'],
                "summary": change['analysis']['summary'],
                "details": {
                    "change_percent": change['change_percent'],
                    "key_changes": change['analysis']['key_changes']
                },
                "strategic_implications": change['analysis']['strategic_implications'],
                "recommended_actions": change['analysis']['recommended_actions'],
                "detected_at": change['detected_at'],
                "alerted": False
            }
            
            intel_id = intel_repo.create(
                f"intel_{competitor['id']}_{int(datetime.utcnow().timestamp())}",
                intel_entry
            )['id']
            
            # Create Notion page
            notion_url = await self.notion.create_intelligence_entry(intel_entry)
            intel_repo.update(intel_id, {"notion_url": notion_url})
            
            # Send alert for high/medium severity
            if change['severity'] in ['high', 'medium']:
                await self._send_alert(competitor, intel_entry, notion_url)
                intel_repo.update(intel_id, {"alerted": True})
    
    async def _send_alert(
        self,
        competitor: Dict[str, Any],
        intel_entry: Dict[str, Any],
        notion_url: str
    ):
        """Send Slack alert for significant changes"""
        
        severity_emoji = {
            "high": "🚨",
            "medium": "⚠️",
            "low": "ℹ️"
        }
        
        message = f"""
{severity_emoji.get(intel_entry['severity'], 'ℹ️')} **Competitor Alert: {competitor['name']}**

**Change Detected:** {intel_entry['summary']}

**Page:** {intel_entry['page_type'].replace('_', ' ').title()}
**Severity:** {intel_entry['severity'].upper()}
**Change Size:** {intel_entry['details']['change_percent']:.1f}%

**Strategic Implications:**
{intel_entry['strategic_implications']}

**Recommended Actions:**
{chr(10).join(['• ' + action for action in intel_entry['recommended_actions']])}

📊 [View Full Intelligence Entry]({notion_url})
"""
        
        await self.slack.send_message(
            channel="#competitive-alerts",
            text=message
        )
    
    async def generate_battlecard(
        self,
        competitor_id: str,
        focus_areas: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate competitive battlecard
        
        Args:
            competitor_id: Competitor ID
            focus_areas: Optional specific areas to focus on
            
        Returns:
            Battlecard content
        """
        # Get competitor
        competitor = competitor_repo.get(competitor_id)
        
        # Get recent intelligence
        recent_intel = intel_repo.list(
            filters=[("competitor_id", "==", competitor_id)],
            order_by="-detected_at",
            limit=20
        )
        
        # Get latest snapshots
        snapshots = snapshot_repo.list(
            filters=[("competitor_id", "==", competitor_id)],
            order_by="-crawled_at",
            limit=10
        )
        
        # Build context for LLM
        context = {
            "competitor_name": competitor['name'],
            "recent_updates": [
                {
                    "summary": intel['summary'],
                    "implications": intel.get('strategic_implications', '')
                }
                for intel in recent_intel[:5]
            ],
            "latest_content": {
                page_type: snapshot['text_content'][:1000]
                for snapshot in snapshots
                for page_type in [snapshot['page_type']]
            }
        }
        
        # Generate battlecard with LLM
        prompt = f"""Generate a competitive battlecard for MAB AI Strategies vs {competitor['name']}.

CONTEXT:
{json.dumps(context, indent=2)}

MAB AI STRATEGIES POSITIONING:
- Enterprise AI automation consulting
- 40+ custom agents, 10+ web apps built
- Proven track record: $12M+ revenue, 100% coaching success rate
- Focus areas: Process automation, Sales enablement, Data intelligence
- Differentiators: Hands-on implementation, not just strategy

Create a comprehensive battlecard in JSON format:
{{
    "executive_summary": "2-3 sentence positioning",
    "feature_comparison": {{
        "feature_name": {{"mab": "our_position", "competitor": "their_position"}}
    }},
    "pricing_analysis": {{
        "mab": "our_pricing_model",
        "competitor": "their_pricing_model",
        "advantage": "why_we_win"
    }},
    "win_themes": ["theme1", "theme2", "theme3"],
    "objection_handling": {{
        "objection": "response"
    }},
    "recent_news": ["update1", "update2"],
    "recommended_approach": "How to position MAB in competitive deals"
}}"""
        
        battlecard = llm.generate_structured(
            prompt=prompt,
            output_schema={
                "executive_summary": "string",
                "feature_comparison": "object",
                "pricing_analysis": "object",
                "win_themes": ["string"],
                "objection_handling": "object",
                "recent_news": ["string"],
                "recommended_approach": "string"
            }
        )
        
        return battlecard
    
    async def _upload_screenshot(self, filepath: str) -> str:
        """Upload screenshot to Cloud Storage"""
        # Implementation placeholder
        # In production, upload to GCS and return public URL
        return f"gs://mab-skill-artifacts/screenshots/{os.path.basename(filepath)}"
