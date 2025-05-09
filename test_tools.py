from tools import *


st = EnhancedYFinanceTools({'stock_price': True, 'analyst_recommendations': True, 'company_info': True, 'income_statements': True, 'key_financial_ratios': True, 'stock_fundamentals': True,'technical_indicators': True, 'historical_prices': True})

symbol = "AAPL"
# print(st._get_company_info(symbol))

print(st.get_stock_fundamentals(symbol))