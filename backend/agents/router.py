"""
Groq-Only LLM Router — all LLM work flows through Groq.
3 model tiers with smart cascading fallback and rate-limit handling.

Tiers:
  fast     → llama-3.1-8b-instant          (scoring, quick summaries)
  balanced → llama-4-scout-17b-16e-instruct (debate, strategy)
  power    → llama-3.3-70b-versatile        (synthesis, creative, finals)
"""

import os
import time
import asyncio
from datetime import date
from typing import Optional
from loguru import logger
from dotenv import load_dotenv

load_dotenv()


class LLMRouter:
    """Routes LLM requests across 3 Groq model tiers with cascading fallback."""

    def __init__(self, custom_task_routes: dict = None):
        self._client = None
        self._daily_usage = 0
        self._usage_date = str(date.today())
        self._consecutive_rate_limits = 0

        # 3 Groq model tiers — ordered from fastest/cheapest to most powerful
        self.models = {
            "fast": os.getenv("GROQ_MODEL_FAST", "llama-3.1-8b-instant"),
            "balanced": os.getenv("GROQ_MODEL_BALANCED", "meta-llama/llama-4-scout-17b-16e-instruct"),
            "power": os.getenv("GROQ_MODEL_POWER", "llama-3.3-70b-versatile"),
        }

        self.daily_limit = int(os.getenv("GROQ_DAILY_LIMIT", "14000"))
        self.base_cooldown = int(os.getenv("GROQ_RATE_LIMIT_COOLDOWN", "5"))

        # Cascade order: if the preferred model is rate-limited, try these
        self.cascade_order = [
            self.models["power"],
            self.models["balanced"],
            self.models["fast"],
        ]

        # Task → model tier mapping
        default_routes = {
            # Fast tier — lightweight tasks
            "scoring": "fast",
            "quick_summary": "fast",

            # Balanced tier — debate & analysis
            "trend_analysis": "balanced",
            "strategy_planning": "balanced",
            "market_research": "balanced",
            "seo_analysis": "balanced",
            "media_buying": "balanced",
            "debate_opinion": "balanced",

            # Power tier — synthesis & creative
            "copy_generation": "power",
            "creative_direction": "power",
            "video_direction": "power",
            "debate_synthesis": "power",
            "critic_review": "balanced",
            "presentation": "balanced",
        }

        self.task_routes = {**default_routes, **(custom_task_routes or {})}

        # Fallback order for provider-level references (backward compat)
        # Everything maps to groq internally
        self.fallback_order = ["groq"]

    def _reset_daily_if_needed(self):
        """Reset daily counters if date has changed."""
        today = str(date.today())
        if today != self._usage_date:
            self._daily_usage = 0
            self._usage_date = today
            self._consecutive_rate_limits = 0

    def _get_client(self):
        """Lazy init Groq client."""
        if self._client is None:
            try:
                from groq import AsyncGroq
                api_key = os.getenv("GROQ_API_KEY")
                if not api_key:
                    logger.error("GROQ_API_KEY not found in environment!")
                else:
                    self._client = AsyncGroq(api_key=api_key)
                    logger.info("Groq client initialized successfully")
            except ImportError:
                logger.error("groq package not installed — run: pip install groq")
        return self._client

    def _is_within_budget(self) -> bool:
        """Check if we're within daily budget."""
        self._reset_daily_if_needed()
        warning_pct = float(os.getenv("BUDGET_WARNING_PCT", "0.85"))

        if self._daily_usage >= self.daily_limit:
            logger.warning(f"[Groq] Daily limit REACHED: {self._daily_usage}/{self.daily_limit}")
            return False
        if self._daily_usage >= self.daily_limit * warning_pct:
            logger.warning(
                f"[Groq] Approaching limit: {self._daily_usage}/{self.daily_limit} "
                f"({self._daily_usage / self.daily_limit * 100:.0f}%)"
            )
        return True

    def _select_model(self, task_type: str) -> str:
        """Select the best model for a given task type."""
        tier = self.task_routes.get(task_type, "balanced")

        # Handle legacy string-based provider routes (backward compat)
        if tier in ("groq", "groq-llama-8b", "groq-llama-70b"):
            if "70b" in tier:
                tier = "power"
            elif "8b" in tier:
                tier = "fast"
            else:
                tier = "balanced"

        # Handle any non-tier values (e.g., old "mistral", "gemini" references)
        if tier not in self.models:
            tier = "balanced"

        return self.models[tier]

    def _get_backoff_seconds(self) -> float:
        """Progressive backoff based on consecutive rate limits."""
        backoffs = [2, 5, 15, 30, 60]
        idx = min(self._consecutive_rate_limits, len(backoffs) - 1)
        return backoffs[idx]

    async def generate(
        self,
        prompt: str,
        task_type: str = "quick_summary",
        system_prompt: str = "You are an expert marketing strategist.",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        force_provider: Optional[str] = None,  # kept for backward compat, ignored
        force_model: Optional[str] = None,
        retries: int = 2,
    ) -> dict:
        """
        Generate a response using Groq.
        Includes automatic retry with model cascade for rate limits.
        """
        # Determine which model to try first
        if force_model:
            primary_model = force_model
        else:
            primary_model = self._select_model(task_type)

        # Build cascade: primary first, then others
        models_to_try = [primary_model] + [
            m for m in self.cascade_order if m != primary_model
        ]

        last_error = ""

        for model in models_to_try:
            for attempt in range(retries + 1):
                if attempt > 0:
                    wait_time = self._get_backoff_seconds()
                    logger.info(f"[Groq] Retry {attempt}/{retries} for {model}, waiting {wait_time}s...")
                    await asyncio.sleep(wait_time)

                try:
                    start_time = time.time()
                    result = await self._call_groq(prompt, system_prompt, temperature, max_tokens, model)
                    duration = time.time() - start_time

                    self._daily_usage += 1
                    self._consecutive_rate_limits = 0  # Reset on success

                    return {
                        "text": result["text"],
                        "provider": "groq",
                        "model": model,
                        "tokens_used": result.get("tokens", 0),
                        "duration": round(duration, 2),
                        "task_type": task_type,
                    }

                except Exception as e:
                    last_error = str(e).lower()
                    logger.warning(f"[Groq:{model}] Attempt {attempt + 1} failed: {e}")

                    is_rate_limit = "rate limit" in last_error or "429" in last_error
                    if is_rate_limit:
                        self._consecutive_rate_limits += 1

                    # If NOT a rate limit error, don't retry — cascade to next model
                    if not is_rate_limit:
                        break

            # After exhausting retries for this model, try next in cascade
            logger.info(f"[Groq] Model {model} exhausted, cascading to next...")

        # All models exhausted
        logger.error(f"[Groq] All models failed for task: {task_type}. Last error: {last_error}")
        return {
            "text": f"[ERROR] All Groq models failed for task: {task_type}. Last error: {last_error}",
            "provider": "groq",
            "model": "none",
            "tokens_used": 0,
            "duration": 0,
            "task_type": task_type,
        }

    async def _call_groq(
        self, prompt: str, system_prompt: str, temperature: float, max_tokens: int, model: str
    ) -> dict:
        """Call Groq API with the specified model."""
        client = self._get_client()
        if not client:
            raise RuntimeError("Groq client not initialized (missing API key?)")

        # Add 60-second timeout to prevent infinite hangs
        try:
            response = await asyncio.wait_for(
                client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                ),
                timeout=60.0  # 60 second timeout per LLM call
            )
        except asyncio.TimeoutError:
            raise TimeoutError(f"Groq API call to {model} timed out after 60 seconds")

        return {
            "text": response.choices[0].message.content,
            "tokens": response.usage.total_tokens if response.usage else 0,
            "model": model,
        }

    def get_usage_stats(self) -> dict:
        """Get current daily usage statistics."""
        self._reset_daily_if_needed()
        return {
            "groq": {
                "used": self._daily_usage,
                "limit": self.daily_limit,
                "remaining": self.daily_limit - self._daily_usage,
                "usage_pct": round(self._daily_usage / self.daily_limit * 100, 1) if self.daily_limit > 0 else 0,
                "models": self.models,
                "consecutive_rate_limits": self._consecutive_rate_limits,
            }
        }
