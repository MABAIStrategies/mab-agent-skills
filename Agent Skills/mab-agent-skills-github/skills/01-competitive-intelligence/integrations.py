"""
Skill 01: Competitive Intelligence - External Integrations
Notion, Slack, and LinkedIn API clients
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

# Notion
from notion_client import Client as NotionClient

# Slack
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# LinkedIn (custom implementation)
import requests

# Shared
import sys
sys.path.append('/app')
from shared.logging import get_logger

logger = get_logger(__name__, skill_name="competitive-intelligence")


class NotionIntegration:
    """Notion API integration for intelligence repository"""
    
    def __init__(self):
        self.client = NotionClient(auth=os.getenv("NOTION_API_KEY"))
        self.database_id = os.getenv("NOTION_DATABASE_ID")
    
    async def create_intelligence_entry(
        self,
        intel_entry: Dict[str, Any]
    ) -> str:
        """
        Create a new intelligence entry in Notion
        
        Args:
            intel_entry: Intelligence data
            
        Returns:
            Notion page URL
        """
        try:
            # Build properties
            properties = {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": f"{intel_entry['competitor_name']} - {intel_entry['summary']}"
                            }
                        }
                    ]
                },
                "Competitor": {
                    "select": {
                        "name": intel_entry['competitor_name']
                    }
                },
                "Type": {
                    "select": {
                        "name": intel_entry['type']
                    }
                },
                "Severity": {
                    "select": {
                        "name": intel_entry['severity'].title()
                    }
                },
                "Detected": {
                    "date": {
                        "start": intel_entry['detected_at']
                    }
                }
            }
            
            # Build content blocks
            children = [
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": "Summary"}}]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": intel_entry['summary']}}]
                    }
                },
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": "Strategic Implications"}}]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": intel_entry['strategic_implications']}}]
                    }
                },
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": "Recommended Actions"}}]
                    }
                }
            ]
            
            # Add action items as bullet list
            for action in intel_entry['recommended_actions']:
                children.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": action}}]
                    }
                })
            
            # Create page
            page = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties,
                children=children
            )
            
            logger.info(f"Created Notion page: {page['url']}")
            return page['url']
            
        except Exception as e:
            logger.error("Failed to create Notion page", error=e)
            raise


class SlackIntegration:
    """Slack API integration for alerts"""
    
    def __init__(self):
        self.client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    
    async def send_message(
        self,
        channel: str,
        text: str,
        blocks: Optional[List[Dict]] = None
    ) -> bool:
        """
        Send message to Slack channel
        
        Args:
            channel: Channel name (e.g., #competitive-alerts)
            text: Message text
            blocks: Optional rich message blocks
            
        Returns:
            Success status
        """
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=text,
                blocks=blocks if blocks else None,
                unfurl_links=False,
                unfurl_media=False
            )
            
            logger.info(f"Sent Slack message to {channel}")
            return response['ok']
            
        except SlackApiError as e:
            logger.error(f"Slack API error: {e.response['error']}", error=e)
            return False
    
    async def send_webhook(self, message: str) -> bool:
        """
        Send message via Slack webhook (simpler, no auth needed)
        
        Args:
            message: Message text
            
        Returns:
            Success status
        """
        try:
            response = requests.post(
                self.webhook_url,
                json={"text": message},
                headers={"Content-Type": "application/json"}
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error("Failed to send Slack webhook", error=e)
            return False


class LinkedInIntegration:
    """LinkedIn API integration for company monitoring"""
    
    def __init__(self):
        self.access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        self.client_id = os.getenv("LINKEDIN_CLIENT_ID")
        self.client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
        self.base_url = "https://api.linkedin.com/v2"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with auth"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
    
    async def get_company_updates(
        self,
        company_id: str,
        count: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent updates from a LinkedIn company page
        
        Args:
            company_id: LinkedIn company ID
            count: Number of updates to retrieve
            
        Returns:
            List of company updates
        """
        try:
            url = f"{self.base_url}/organizations/{company_id}/updates"
            params = {"count": count}
            
            response = requests.get(
                url,
                headers=self._get_headers(),
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get('elements', [])
            
        except Exception as e:
            logger.error(f"LinkedIn API error for company {company_id}", error=e)
            return []
    
    async def get_company_jobs(
        self,
        company_id: str,
        count: int = 25
    ) -> List[Dict[str, Any]]:
        """
        Get recent job postings from a company
        
        Args:
            company_id: LinkedIn company ID
            count: Number of jobs to retrieve
            
        Returns:
            List of job postings
        """
        try:
            url = f"{self.base_url}/jobPostings"
            params = {
                "q": "company",
                "companyId": company_id,
                "count": count
            }
            
            response = requests.get(
                url,
                headers=self._get_headers(),
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get('elements', [])
            
        except Exception as e:
            logger.error(f"Failed to get jobs for company {company_id}", error=e)
            return []
    
    async def search_companies(
        self,
        query: str,
        count: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for companies by name
        
        Args:
            query: Company name search query
            count: Number of results
            
        Returns:
            List of matching companies
        """
        try:
            url = f"{self.base_url}/organizationSearchResults"
            params = {
                "q": "keywords",
                "keywords": query,
                "count": count
            }
            
            response = requests.get(
                url,
                headers=self._get_headers(),
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get('elements', [])
            
        except Exception as e:
            logger.error(f"LinkedIn search error for '{query}'", error=e)
            return []
