# agents.py
from typing import List, Dict, Any
import google.generativeai as genai
from config import AgentConfig, APIConfig
from tools import WebResearchTool, EnhancedYFinanceTools
import json

class BaseAgent:
    """Base agent class with common functionality"""
    
    def __init__(self, config: AgentConfig, instructions: List[str]):
        self.config = config
        self.instructions = instructions
        self._setup_model()
        
    def _setup_model(self):
        """Initialize the Gemini model"""
        # Validate API keys before setup
        APIConfig.validate_keys()
        
        # Configure Gemini with the API key
        genai.configure(api_key=APIConfig.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(
            model_name=self.config.model_name,
            generation_config={
                "temperature": self.config.temperature,
                "max_output_tokens": self.config.max_tokens
            }
        )
        
    async def generate_response(self, prompt: str) -> str:
        """Generate response using the model"""
        try:
            formatted_prompt = self._format_prompt(prompt)
            response = await self.model.generate_content_async(formatted_prompt)
            return response.text
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return ""
            
    def _format_prompt(self, prompt: str) -> str:
        """Format prompt with instructions"""
        return f"""Instructions: {' '.join(self.instructions)}

Query: {prompt}

Please provide a detailed analysis based on the above instructions."""

class WebResearchAgent(BaseAgent):
    """Agent for web research and news analysis"""
    
    def __init__(self, config: AgentConfig, instructions: List[str]):
        super().__init__(config, instructions)
        self.web_tool = WebResearchTool()
        
    async def research_company(self, company: str) -> Dict[str, Any]:
        """Perform comprehensive web research"""
        
        news_data = self.web_tool.search_news(company)
        
        analysis_prompt = f"""
        Analyze the following news articles about {company}:
        
        {news_data}
        
        Provide insights on:
        1. Recent developments
        2. Market sentiment
        3. Key challenges and opportunities
        4. Competitive position
        """
        
        analysis = await self.generate_response(analysis_prompt)
        return {
            "news_data": news_data,
            "analysis": analysis
        }

class FinancialDataAgent(BaseAgent):
    """Agent for financial data analysis"""
    
    def __init__(self, config: AgentConfig, instructions: List[str]):
        super().__init__(config, instructions)
        self.finance_tool = EnhancedYFinanceTools(config={
            "stock_price": True,
            "analyst_recommendations": True,
            "company_info": True,
            "income_statements": True,
            "key_financial_ratios": True,
            "stock_fundamentals": True
        })
        
    async def analyze_financials(self, symbol: str) -> Dict[str, Any]:
        """Analyze company financials"""
        financial_data = self.finance_tool.get_stock_data(symbol)
        
        # Parse JSON strings into dictionaries
        try:
            fundamentals = json.loads(self.finance_tool.get_stock_fundamentals(symbol))
        except:
            fundamentals = {}
            
        try:
            ratios = json.loads(self.finance_tool.get_key_financial_ratios(symbol))
        except:
            ratios = {}
        
        # Combine all financial information
        combined_data = {
            **financial_data,
            "fundamentals": fundamentals,
            "key_ratios": ratios
        }
        
        analysis_prompt = f"""
        Analyze the following financial data for {symbol}:
        
        Financial Overview:
        {combined_data}
        
        Stock Fundamentals:
        {fundamentals}
        
        Key Financial Ratios:
        {ratios}
        
        Provide detailed insights on:
        1. Financial health and stability
        2. Growth trends and projections
        3. Valuation metrics and fair value assessment
        4. Key risk factors and considerations
        5. Comparative industry analysis
        6. Capital structure and efficiency
        7. Profitability metrics and trends
        8. Dividend sustainability (if applicable)
        """
        
        analysis = await self.generate_response(analysis_prompt)
        return {
            "financial_data": combined_data,
            "fundamentals": fundamentals,
            "key_ratios": ratios,
            "analysis": analysis
        }
class TechnicalAnalysisAgent(BaseAgent):
    """Agent for technical analysis"""
    
    def __init__(self, config: AgentConfig, instructions: List[str]):
        super().__init__(config, instructions)
        self.finance_tool = EnhancedYFinanceTools(config={
            "technical_indicators": True,
            "historical_prices": True
        })
        
    async def analyze_technicals(self, symbol: str) -> Dict[str, Any]:
        """Perform technical analysis"""
        technical_data = self.finance_tool.get_stock_data(symbol)
        
        analysis_prompt = f"""
        Analyze the following technical indicators for {symbol}:
        
        {technical_data}
        
        Provide insights on:
        1. Trend analysis
        2. Support and resistance levels
        3. Technical signals
        4. Trading recommendations
        """
        
        analysis = await self.generate_response(analysis_prompt)
        return {
            "technical_data": technical_data,
            "analysis": analysis
        }

class StockAdvisorAgent(BaseAgent):
    """Main agent that coordinates other agents"""
    
    def __init__(self, config: AgentConfig, instructions: List[str]):
        super().__init__(config, instructions)
        self.web_research = WebResearchAgent(config, instructions)
        self.financial = FinancialDataAgent(config, instructions)
        self.technical = TechnicalAnalysisAgent(config, instructions)
        
    async def generate_recommendation(self, symbol: str) -> Dict[str, Any]:
        """Generate comprehensive stock recommendation"""
        # Gather data from all agents
        web_research = await self.web_research.research_company(symbol)
        financials = await self.financial.analyze_financials(symbol)
        technicals = await self.technical.analyze_technicals(symbol)
        
        recommendation_prompt = f"""
        Synthesize the following analyses for {symbol}:
        
        Web Research: {web_research}
        Financial Analysis: {financials}
        Technical Analysis: {technicals}
        
        Provide:
        1. Overall recommendation (Buy/Hold/Sell)
        2. Key reasons for recommendation
        3. Risk factors
        4. Price targets
        5. Investment timeline
        """
        
        final_recommendation = await self.generate_response(recommendation_prompt)
        
        return {
            "web_research": web_research,
            "financials": financials,
            "technicals": technicals,
            "recommendation": final_recommendation
        }