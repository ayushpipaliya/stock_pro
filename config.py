# config.py
import os
from dataclasses import dataclass
from typing import List, Optional
from dotenv import load_dotenv
load_dotenv()

@dataclass
class AgentConfig:
    """Base configuration for all agents"""
    model_name: str
    temperature: float = 0.4
    max_tokens: int = 2048
    show_tool_calls: bool = True
    markdown: bool = True

@dataclass
class APIConfig:
    """API configurations"""
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")  # Changed to GOOGLE_API_KEY
    ALPHA_VANTAGE_API_KEY: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")
    
    @classmethod
    def validate_keys(cls):
        """Validate required API keys"""
        if not cls.GOOGLE_API_KEY:
            raise ValueError(
                "Missing GOOGLE_API_KEY. Please set the GOOGLE_API_KEY environment variable. "
                "You can get an API key from https://makersuite.google.com/app/apikey"
            )

# Agent-specific configurations
WEB_RESEARCH_CONFIG = AgentConfig(
    model_name="gemini-1.5-flash",
)

FINANCIAL_DATA_CONFIG = AgentConfig(
    model_name="gemini-1.5-flash",
)

TECHNICAL_ANALYSIS_CONFIG = AgentConfig(
    model_name="gemini-1.5-flash",
)

STOCK_ADVISOR_CONFIG = AgentConfig(
    model_name="gemini-2.0-flash-exp",
)

# Tool configurations
YFINANCE_TOOLS_CONFIG = {
    "stock_price": True,
    "analyst_recommendations": True,
    "company_info": True,
    "income_statements": True,
    "key_financial_ratios": True,
    "stock_fundamentals": True,
    "technical_indicators": True,
    "historical_prices": True
}