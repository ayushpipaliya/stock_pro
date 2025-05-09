# app.py
import streamlit as st
import asyncio
from config import (
    STOCK_ADVISOR_CONFIG,
    APIConfig
)
from agents import StockAdvisorAgent
import json

# Page configuration
st.set_page_config(
    page_title="AI Stock Advisor",
    page_icon="📈",
    layout="wide"
)

def initialize_session_state():
    """Initialize session state variables"""
    if 'advisor_agent' not in st.session_state:
        APIConfig.validate_keys()  
        st.session_state.advisor_agent = StockAdvisorAgent(
            config=STOCK_ADVISOR_CONFIG,
            instructions=[
                "Synthesize data from financial, technical, and market research agents",
                "Provide comprehensive stock analysis and recommendations"
            ]
        )

def main():
    st.title("🤖 AI Stock Advisor")
    st.markdown("""
    This application provides comprehensive stock analysis using multiple AI agents
    to analyze market data, financials, and technical indicators.
    """)
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar inputs
    with st.sidebar:
        st.header("Analysis Parameters")
        symbol = st.text_input("Enter Stock Symbol (e.g., AAPL)", value="AAPL")
        
        if st.button("Generate Analysis"):
            if not symbol:
                st.error("Please enter a stock symbol")
                return
                
            with st.spinner("Generating comprehensive analysis..."):
                # Run analysis
                try:
                    result = asyncio.run(
                        st.session_state.advisor_agent.generate_recommendation(symbol)
                    )
                    
                    # Store results in session state
                    st.session_state.latest_analysis = result
                    st.success("Analysis completed!")
                except Exception as e:
                    st.error(f"Error generating analysis: {str(e)}")
                    return
    
    # Main content area
    if 'latest_analysis' in st.session_state:
        result = st.session_state.latest_analysis
        
        # Market Research
        st.header("📰 Market Research")
        st.markdown(result['web_research']['analysis'])
        
        # Financial Analysis
        st.header("📊 Financial Analysis")
        with st.expander("View Financial Details", expanded=True):
            st.markdown(result['financials']['analysis'])
            
            # Display key financial metrics
            if 'financial_data' in result['financials']:
                financial_data = result['financials']['financial_data']
                fundamentals = result['financials'].get('fundamentals', {})
                key_ratios = financial_data.get('key_ratios', {})
                company_info = financial_data.get('company_info', {})
                
                # Basic Metrics
                st.subheader("Key Metrics")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Current Price", 
                             f"${financial_data.get('current_price', 'N/A')}")
                with col2:
                    st.metric("Market Cap", 
                             fundamentals.get('market_cap', 'N/A'))
                with col3:
                    formatted_pe = f"{fundamentals.get('pe_ratio', 'N/A')}"
                    st.metric("P/E Ratio", formatted_pe)
                with col4:
                    formatted_beta = f"{fundamentals.get('beta', 'N/A')}"
                    st.metric("Beta", formatted_beta)

                # Fundamentals
                st.subheader("Fundamentals")
                col1, col2, col3 = st.columns(3)
                with col1:
                    formatted_eps = f"{fundamentals.get('eps', 'N/A')}"
                    st.metric("EPS", formatted_eps)
                with col2:
                    formatted_pb = f"{fundamentals.get('pb_ratio', 'N/A')}"
                    st.metric("P/B Ratio", formatted_pb)
                with col3:
                    dividend_yield = fundamentals.get('dividend_yield', 'N/A')
                    if dividend_yield != 'N/A':
                        dividend_yield = f"{float(dividend_yield) * 100:.2f}%"
                    st.metric("Dividend Yield", dividend_yield)

                # 52 Week Range
                st.subheader("52 Week Range")
                col1, col2 = st.columns(2)
                with col1:
                    formatted_high = f"${fundamentals.get('52_week_high', 'N/A')}"
                    st.metric("52 Week High", formatted_high)
                with col2:
                    formatted_low = f"${fundamentals.get('52_week_low', 'N/A')}"
                    st.metric("52 Week Low", formatted_low)

                # Additional Financial Ratios
                if key_ratios:
                    st.subheader("Additional Financial Ratios")
                    selected_ratios = {
                        "Return on Equity": key_ratios.get('returnOnEquity', 'N/A'),
                        "Debt to Equity": key_ratios.get('debtToEquity', 'N/A'),
                        "Operating Margin": key_ratios.get('operatingMargins', 'N/A'),
                        "Profit Margin": key_ratios.get('profitMargins', 'N/A')
                    }
                    
                    cols = st.columns(len(selected_ratios))
                    for i, (label, value) in enumerate(selected_ratios.items()):
                        with cols[i]:
                            if value != 'N/A':
                                value = f"{float(value) * 100:.2f}%" if "Margin" in label or "Return" in label else f"{float(value):.2f}"
                            st.metric(label, value)

        # Technical Analysis
        st.header("📈 Technical Analysis")
        with st.expander("View Technical Details", expanded=True):
            st.markdown(result['technicals']['analysis'])
            
            # Display technical indicators
            if 'technical_data' in result['technicals']:
                tech_data = result['technicals']['technical_data'].get('technical', {})
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("RSI", f"{tech_data.get('rsi', 'N/A'):.2f}")
                with col2:
                    st.metric("MACD", f"{tech_data.get('macd', 'N/A'):.2f}")
                with col3:
                    st.metric("Signal Line", f"{tech_data.get('macd_signal', 'N/A'):.2f}")

        # Final Recommendation
        st.header("🎯 Investment Recommendation")
        with st.container():
            st.markdown("### Summary")
            st.markdown(result['recommendation'])
            
            # Add download button for full report
            full_report = f"""
            # AI Stock Advisor Report - {symbol}
            
            ## Market Research
            {result['web_research']['analysis']}
            
            ## Financial Analysis
            {result['financials']['analysis']}
            
            ## Technical Analysis
            {result['technicals']['analysis']}
            
            ## Final Recommendation
            {result['recommendation']}
            """
            
            st.download_button(
                label="Download Full Report",
                data=full_report,
                file_name=f"stock_analysis_{symbol}.md",
                mime="text/markdown"
            )

if __name__ == "__main__":
    main()