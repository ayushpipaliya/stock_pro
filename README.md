Live Link : [ai-stock-advisor](https://ai-stock-advisor.streamlit.app/)

# AI Stock Advisor

A comprehensive stock analysis tool powered by multiple AI agents using Google's Gemini model. This application provides detailed market research, financial analysis, and technical analysis for any given stock.

## Features

- 🔍 **Web Research Agent**: Gathers and analyzes recent news, market trends, and competitor analysis
- 📊 **Financial Data Agent**: Analyzes stock fundamentals, financial statements, and key ratios
- 📈 **Technical Analysis Agent**: Provides technical indicators and chart pattern analysis
- 🤖 **Stock Advisor Agent**: Synthesizes all data to generate comprehensive investment recommendations

## Setup

1. Clone the repository:
```bash
git clone https://github.com/Uttampatel1/ai-stock-advisor.git
cd ai-stock-advisor
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your API keys:
```env
GEMINI_API_KEY=your_gemini_api_key
NEWS_API_KEY=your_newsapi_key
```

## Project Structure

```
ai-stock-advisor/
├── config.py           # Configuration settings
├── tools.py           # Custom tools implementation
├── agents.py          # AI agent implementations
├── app.py            # Streamlit application
├── requirements.txt   # Project dependencies
└── README.md         # Project documentation
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Enter a stock symbol in the sidebar (e.g., "AAPL" for Apple Inc.)

3. Click "Generate Analysis" to run the comprehensive analysis

4. View the results in different sections:
   - Market Research
   - Financial Analysis
   - Technical Analysis
   - Final Recommendation

5. Download the full report as a markdown file

## API Keys Required

- Google Gemini API key: [Get it here](https://makersuite.google.com/app/apikey)
- News API key: [Get it here](https://newsapi.org/register)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
