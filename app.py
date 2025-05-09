import streamlit as st
import asyncio
from config import (
    STOCK_ADVISOR_CONFIG,
    APIConfig
)
from agents import StockAdvisorAgent
import json

# Custom CSS styles
custom_css = """
<style>
    /* Main container styling */
    .main {
        padding: 2rem;
    }
    
    /* Custom card styling */
    .stcard {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
    }
    
    /* Metric styling */
    .metric-container {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        color: #6c757d;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .metric-value {
        color: #212529;
        font-size: 1.2rem;
        font-weight: 600;
    }
    
    /* Header styling */
    h1, h2, h3 {
        color: #1a1a1a;
        margin-bottom: 1rem;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #007bff;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        transition: background-color 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #0056b3;
    }
    
    /* Analysis sections styling */
    .analysis-section {
        border-left: 4px solid #007bff;
        padding-left: 1rem;
        margin: 1rem 0;
    }
    
    /* Status indicators */
    .status-positive {
        color: #28a745;
    }
    
    .status-negative {
        color: #dc3545;
    }
    
    .status-neutral {
        color: #ffc107;
    }
</style>
"""

# Page configuration
st.set_page_config(
    page_title="AI Stock Advisor Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS
st.markdown(custom_css, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    # Initialize default instructions if not present
    if 'analysis_instructions' not in st.session_state:
        st.session_state.analysis_instructions = [
            "Synthesize data from financial, technical, and market research agents",
            "Provide comprehensive stock analysis and recommendations"
        ]
    
    if 'advisor_agent' not in st.session_state:
        APIConfig.validate_keys()  
        st.session_state.advisor_agent = StockAdvisorAgent(
            config=STOCK_ADVISOR_CONFIG,
            instructions=st.session_state.analysis_instructions
        )

def create_metric_card(label, value, description=""):
    """Create a custom styled metric card"""
    html = f"""
    <div class="metric-container">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {f'<div class="metric-description">{description}</div>' if description else ''}
    </div>
    """
    return st.markdown(html, unsafe_allow_html=True)

def main():
    # Header section with improved styling
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #007bff;">🤖 AI Stock Advisor Pro</h1>
        <p style="font-size: 1.2rem; color: #6c757d;">
            Advanced stock analysis powered by AI agents
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session_state()
    
    # Improved sidebar
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2 style="color: #007bff;">Analysis Parameters</h2>
        </div>
        """, unsafe_allow_html=True)
        
        symbol = st.text_input("Enter Stock Symbol", 
                             value="AAPL",
                             help="Enter a valid stock symbol (e.g., AAPL, GOOGL, MSFT)")
        
        # Instructions management section
        st.markdown("### 📝 Analysis Instructions")
        
        # Show current instructions
        st.markdown("**Current Instructions:**")
        for i, instruction in enumerate(st.session_state.analysis_instructions):
            st.markdown(f"{i+1}. {instruction}")
        
        # Add new instruction
        new_instruction = st.text_input("Add New Instruction", 
                                      key="new_instruction",
                                      help="Enter a new analysis instruction")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Add Instruction", use_container_width=True):
                if new_instruction:
                    st.session_state.analysis_instructions.append(new_instruction)
                    st.session_state.advisor_agent = StockAdvisorAgent(
                        config=STOCK_ADVISOR_CONFIG,
                        instructions=st.session_state.analysis_instructions
                    )
                    st.experimental_rerun()
        
        with col2:
            if st.button("Reset to Default", use_container_width=True):
                st.session_state.analysis_instructions = [
                    "Synthesize data from financial, technical, and market research agents",
                    "Provide comprehensive stock analysis and recommendations"
                ]
                st.session_state.advisor_agent = StockAdvisorAgent(
                    config=STOCK_ADVISOR_CONFIG,
                    instructions=st.session_state.analysis_instructions
                )
                st.experimental_rerun()
        
        # Remove instructions
        if len(st.session_state.analysis_instructions) > 1:
            st.markdown("**Remove Instruction:**")
            instruction_to_remove = st.selectbox(
                "Select instruction to remove",
                options=range(len(st.session_state.analysis_instructions)),
                format_func=lambda x: st.session_state.analysis_instructions[x]
            )
            
            if st.button("Remove Selected Instruction", use_container_width=True):
                st.session_state.analysis_instructions.pop(instruction_to_remove)
                st.session_state.advisor_agent = StockAdvisorAgent(
                    config=STOCK_ADVISOR_CONFIG,
                    instructions=st.session_state.analysis_instructions
                )
                st.experimental_rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Add separator
        st.markdown("---")
        
        if st.button("Generate Analysis", use_container_width=True):
            if not symbol:
                st.error("Please enter a stock symbol")
                return
                
            with st.spinner("🔄 Generating comprehensive analysis..."):
                try:
                    result = asyncio.run(
                        st.session_state.advisor_agent.generate_recommendation(symbol)
                    )
                    st.session_state.latest_analysis = result
                    st.success("✅ Analysis completed successfully!")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    return
    
    # Main content area with improved layout
    if 'latest_analysis' in st.session_state:
        result = st.session_state.latest_analysis
        
        # Market Research Section
        st.markdown("""
        <div class="analysis-section">
            <h2>📰 Market Research</h2>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown(result['web_research']['analysis'])
        
        # Financial Analysis Section
        st.markdown("""
        <div class="analysis-section">
            <h2>📊 Financial Analysis</h2>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("View Financial Details", expanded=True):
            st.markdown(result['financials']['analysis'])
            
            if 'financial_data' in result['financials']:
                financial_data = result['financials']['financial_data']
                fundamentals = result['financials'].get('fundamentals', {})
                
                # Key Metrics Grid
                st.subheader("📈 Key Metrics")
                cols = st.columns(4)
                
                metrics = [
                    ("Current Price", f"${financial_data.get('current_price', 'N/A')}"),
                    ("Market Cap", fundamentals.get('Market Cap (intraday)', 'N/A')),
                    ("P/E Ratio", f"{fundamentals.get('PE Ratio (TTM)', 'N/A')}"),
                    ("Beta", f"{fundamentals.get('Beta (5Y Monthly)', 'N/A')}")
                ]
                
                for i, (label, value) in enumerate(metrics):
                    with cols[i]:
                        create_metric_card(label, value)
                
                # Fundamentals Grid
                st.subheader("🎯 Fundamentals")
                cols = st.columns(3)
                
                dividend_yield = fundamentals.get('Forward Dividend & Yield', 'N/A')
                
                fundamentals_metrics = [
                    ("EPS", f"{fundamentals.get('EPS (TTM)', 'N/A')}"),
                    ("52 Week Range", f"{fundamentals.get('52 Week Range', 'N/A')}"),
                    ("Forward Dividend & Yield", dividend_yield)
                ]
                # print("-------")
                # print(fundamentals)
                for i, (label, value) in enumerate(fundamentals_metrics):
                    with cols[i]:
                        create_metric_card(label, value)
        
        # Technical Analysis Section
        st.markdown("""
        <div class="analysis-section">
            <h2>📈 Technical Analysis</h2>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("View Technical Details", expanded=True):
            st.markdown(result['technicals']['analysis'])
            
            if 'technical_data' in result['technicals']:
                tech_data = result['technicals']['technical_data'].get('technical', {})
                
                cols = st.columns(3)
                technical_metrics = [
                    ("RSI", f"{tech_data.get('rsi', 'N/A'):.2f}"),
                    ("MACD", f"{tech_data.get('macd', 'N/A'):.2f}"),
                    ("Signal Line", f"{tech_data.get('macd_signal', 'N/A'):.2f}")
                ]
                
                for i, (label, value) in enumerate(technical_metrics):
                    with cols[i]:
                        create_metric_card(label, value)
        
        # Final Recommendation Section
        st.markdown("""
        <div class="analysis-section">
            <h2>🎯 Investment Recommendation</h2>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown("### Summary")
            st.markdown(result['recommendation'])
            
            # Improved download button
            full_report = f"""
            # AI Stock Advisor Pro Report - {symbol}
            
            ## Market Research
            {result['web_research']['analysis']}
            
            ## Financial Analysis
            {result['financials']['analysis']}
            
            ## Technical Analysis
            {result['technicals']['analysis']}
            
            ## Final Recommendation
            {result['recommendation']}
            """
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.download_button(
                    label="📥 Download Full Report",
                    data=full_report,
                    file_name=f"stock_analysis_{symbol}.md",
                    mime="text/markdown",
                    use_container_width=True
                )

if __name__ == "__main__":
    main()