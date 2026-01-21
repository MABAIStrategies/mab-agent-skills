"""
MAB AI Strategies - Shared LLM Module
Claude API integration with safety controls and cost tracking
"""

import os
import json
from typing import List, Dict, Any, Optional
from anthropic import Anthropic
from shared.logging import get_logger
from shared.database import CacheManager

# Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
MAX_TOKENS_PER_REQUEST = int(os.getenv("MAX_LLM_TOKENS_PER_REQUEST", "8000"))

logger = get_logger(__name__)
cache = CacheManager(prefix="llm")


class LLMClient:
    """Claude API client with safety controls"""
    
    def __init__(self, skill_name: str):
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.skill_name = skill_name
        self.model = ANTHROPIC_MODEL
    
    def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        max_tokens: int = None,
        temperature: float = 1.0,
        cache_key: str = None,
        cache_ttl: int = 3600
    ) -> str:
        """
        Generate text using Claude
        
        Args:
            prompt: User prompt
            system_prompt: System instructions
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            cache_key: Optional cache key
            cache_ttl: Cache TTL in seconds
            
        Returns:
            Generated text
        """
        # Check cache
        if cache_key and cache.exists(cache_key):
            logger.debug(f"Cache hit for {cache_key}")
            return cache.get(cache_key)
        
        # Token limit
        if not max_tokens:
            max_tokens = MAX_TOKENS_PER_REQUEST
        else:
            max_tokens = min(max_tokens, MAX_TOKENS_PER_REQUEST)
        
        try:
            # Build message
            messages = [{"role": "user", "content": prompt}]
            
            # Make API call
            logger.info(
                "Claude API call",
                extra={
                    "skill": self.skill_name,
                    "model": self.model,
                    "max_tokens": max_tokens
                }
            )
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt if system_prompt else "",
                messages=messages
            )
            
            # Extract text
            generated_text = response.content[0].text
            
            # Track usage
            self._track_usage(
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens
            )
            
            # Cache result
            if cache_key:
                cache.set(cache_key, generated_text, expire_seconds=cache_ttl)
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Claude API error", error=e)
            raise
    
    def generate_structured(
        self,
        prompt: str,
        output_schema: Dict[str, Any],
        system_prompt: str = None
    ) -> Dict[str, Any]:
        """
        Generate structured JSON output
        
        Args:
            prompt: User prompt
            output_schema: Expected output schema
            system_prompt: System instructions
            
        Returns:
            Parsed JSON output
        """
        # Add schema instruction to prompt
        full_prompt = f"""{prompt}

IMPORTANT: Respond with ONLY valid JSON matching this schema:
{json.dumps(output_schema, indent=2)}

Do not include any explanation or markdown formatting."""
        
        response_text = self.generate(full_prompt, system_prompt)
        
        # Extract JSON from response
        try:
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            return json.loads(response_text.strip())
        except json.JSONDecodeError as e:
            logger.error("Failed to parse JSON from Claude", error=e)
            raise ValueError(f"Invalid JSON response: {response_text[:200]}")
    
    def _track_usage(self, prompt_tokens: int, completion_tokens: int):
        """Track token usage and costs"""
        from shared.database import get_firestore_client
        
        # Calculate costs (example pricing)
        PROMPT_COST_PER_1K = 0.003  # $3/million input tokens
        COMPLETION_COST_PER_1K = 0.015  # $15/million output tokens
        
        prompt_cost = (prompt_tokens / 1000) * PROMPT_COST_PER_1K
        completion_cost = (completion_tokens / 1000) * COMPLETION_COST_PER_1K
        total_cost = prompt_cost + completion_cost
        
        # Log usage
        logger.info(
            "LLM usage",
            extra={
                "skill": self.skill_name,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
                "cost_usd": round(total_cost, 4)
            }
        )
        
        # Store in Firestore
        db = get_firestore_client()
        db.collection("llm_usage").add({
            "skill": self.skill_name,
            "model": self.model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "cost_usd": total_cost,
            "timestamp": firestore.SERVER_TIMESTAMP
        })
        
        # Check cost alerts
        self._check_cost_alerts(total_cost)
    
    def _check_cost_alerts(self, cost: float):
        """Check if daily cost threshold is exceeded"""
        from datetime import datetime, timedelta
        
        # Get today's total
        today = datetime.utcnow().date()
        daily_key = f"llm_cost:{today}"
        
        daily_total = cache.get(daily_key) or 0.0
        daily_total += cost
        cache.set(daily_key, daily_total, expire_seconds=86400)
        
        # Alert threshold
        threshold = float(os.getenv("LLM_COST_ALERT_THRESHOLD_DAILY", "100.0"))
        
        if daily_total > threshold:
            logger.warning(
                f"Daily LLM cost threshold exceeded",
                extra={
                    "daily_total": daily_total,
                    "threshold": threshold
                }
            )
            
            # Send Slack alert
            if os.getenv("ENABLE_COST_ALERTS") == "true":
                from shared.integrations.slack_client import send_slack_message
                send_slack_message(
                    f"⚠️ LLM Cost Alert: ${daily_total:.2f} spent today (threshold: ${threshold})"
                )


class PromptTemplate:
    """Reusable prompt templates"""
    
    @staticmethod
    def summarize(content: str, max_words: int = 200) -> str:
        """Summarization prompt"""
        return f"""Summarize the following content in {max_words} words or less:

{content}

Focus on the key points and main takeaways."""
    
    @staticmethod
    def extract_entities(
        text: str,
        entity_types: List[str]
    ) -> str:
        """Entity extraction prompt"""
        return f"""Extract the following entities from this text:
{', '.join(entity_types)}

Text:
{text}

Return as JSON with entity types as keys and lists of found entities as values."""
    
    @staticmethod
    def classify(
        text: str,
        categories: List[str]
    ) -> str:
        """Classification prompt"""
        return f"""Classify the following text into one of these categories:
{', '.join(categories)}

Text:
{text}

Return ONLY the category name, nothing else."""
    
    @staticmethod
    def sentiment_analysis(text: str) -> str:
        """Sentiment analysis prompt"""
        return f"""Analyze the sentiment of this text.

Text:
{text}

Return a JSON object with:
- sentiment: "positive", "negative", or "neutral"
- confidence: 0-100
- reasoning: brief explanation"""
    
    @staticmethod
    def generate_with_examples(
        task: str,
        examples: List[Dict[str, str]],
        input_text: str
    ) -> str:
        """Few-shot learning prompt"""
        examples_str = "\n\n".join([
            f"Input: {ex['input']}\nOutput: {ex['output']}"
            for ex in examples
        ])
        
        return f"""Task: {task}

Examples:
{examples_str}

Now perform the task for this input:
Input: {input_text}
Output:"""


# Safety checks
class ContentSafetyChecker:
    """Check content for safety violations"""
    
    @staticmethod
    def check(text: str) -> Dict[str, Any]:
        """
        Check text for safety issues
        
        Returns:
            Dict with is_safe, violations, and confidence
        """
        # Implement safety checks
        # This is a placeholder - integrate actual safety API
        
        return {
            "is_safe": True,
            "violations": [],
            "confidence": 1.0
        }
