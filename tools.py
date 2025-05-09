# tools.py
from typing import Dict, Any, List
import pandas as pd
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from newsapi import NewsApiClient
from config import APIConfig
import json 

class WebResearchTool:
    """Custom web research tool implementation"""
    
    def __init__(self):
        self.news_api = NewsApiClient(api_key=APIConfig.NEWS_API_KEY)
        
    def search_news(self, query: str, days: int = 7) -> List[Dict[str, Any]]:
        """Search recent news articles"""
        try:
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            # Get company name from Yahoo Finance
            try:
                company_name = self._get_company_name(query)
            except:
                company_name = query
            
            response = self.news_api.get_everything(
                q=company_name,
                from_param=from_date,
                language='en',
                sort_by='relevancy'
            )
            return response['articles']
        except Exception as e:
            print(f"Error fetching news: {str(e)}")
            return []
    
    def _get_company_name(self, ticker: str) -> str:
        """Get company name from Yahoo Finance"""
        url = f"https://finance.yahoo.com/quote/{ticker}"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return ticker
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the company name
        h1_element = soup.find('h1')
        if h1_element:
            return h1_element.text.strip()
        
        return ticker

class EnhancedYFinanceTools:
    """Enhanced Finance tools with BeautifulSoup web scraping"""
    
    def __init__(self, config: Dict[str, bool]):
        self.config = config
        
    def get_stock_data(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive stock data"""
        try:
            data = {}
            
            if self.config.get('stock_price'):
                data['current_price'] = self._get_current_price(symbol)
                
            if self.config.get('company_info'):
                data['company_info'] = self._get_company_info(symbol)
                
            if self.config.get('analyst_recommendations'):
                data['recommendations'] = self._get_analyst_recommendations(symbol)
                
            if self.config.get('income_statements'):
                data['financials'] = self._get_income_statements(symbol)
                
            if self.config.get('technical_indicators'):
                hist = self._fetch_yahoo_finance_history(symbol)
                data['technical'] = self._calculate_technical_indicators(hist)
                
            return data
            
        except Exception as e:
            print(f"Error fetching stock data: {str(e)}")
            return {}
    
    def _get_current_price(self, symbol: str) -> float:
        """Get current stock price"""
        url = f"https://finance.yahoo.com/quote/{symbol}"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to retrieve data: Status code {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the current price
        price_element = soup.find('fin-streamer', {'data-field': 'regularMarketPrice'})
        if price_element:
            try:
                return float(price_element['value'])
            except (ValueError, KeyError):
                return float(price_element.text.strip().replace(',', ''))
        
        return 0.0
    
    def _get_company_info(self, symbol: str) -> Dict[str, Any]:
        """Get detailed company information from Yahoo Finance profile page"""
        url = f"https://finance.yahoo.com/quote/{symbol}/profile"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                print(f"Failed to retrieve company info: Status code {response.status_code}")
                return {
                    'name': '',
                    'address': '',
                    'phone': '',
                    'website': '',
                    'sector': '',
                    'industry': '',
                    'employees': '',
                    'description': ''
                }
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Initialize company info dictionary
            company_info = {
                'name': '',
                'address': '',
                'phone': '',
                'website': '',
                'sector': '',
                'industry': '',
                'employees': '',
                'description': ''
            }
            
            # Extract company name
            name_element = soup.find('section', {'data-testid': 'asset-profile'}).find('h3')
            if name_element:
                company_info['name'] = name_element.text.strip()
            
            # Extract address
            address_div = soup.find('div', {'class': 'address'})
            if address_div:
                address_lines = address_div.find_all('div')
                company_info['address'] = ' '.join([line.text.strip() for line in address_lines])
            
            # Extract phone and website
            phone_link = soup.find('a', {'aria-label': 'phone number'})
            if phone_link:
                company_info['phone'] = phone_link.text.strip()
            
            website_link = soup.find('a', {'aria-label': 'website link'})
            if website_link:
                company_info['website'] = website_link.text.strip()
            
            # Extract sector and industry
            sector_element = soup.find('dt', string=lambda text: 'Sector' in text if text else False)
            if sector_element and sector_element.find_next('a'):
                company_info['sector'] = sector_element.find_next('a').text.strip()
            
            industry_element = soup.find('dt', string=lambda text: 'Industry' in text if text else False)
            if industry_element and industry_element.find_next('a'):
                company_info['industry'] = industry_element.find_next('a').text.strip()
            
            # Extract employees
            employees_element = soup.find('dt', string=lambda text: 'Full Time Employees' in text if text else False)
            if employees_element and employees_element.find_next('strong'):
                company_info['employees'] = employees_element.find_next('strong').text.strip()
            
            # Extract description
            description_section = soup.find('section', {'data-testid': 'description'})
            if description_section:
                description_paragraph = description_section.find('p')
                if description_paragraph:
                    company_info['description'] = description_paragraph.text.strip()
            
            return company_info
            
        except Exception as e:
            print(f"Error fetching company info: {str(e)}")
            return {
                'name': '',
                'address': '',
                'phone': '',
                'website': '',
                'sector': '',
                'industry': '',
                'employees': '',
                'description': ''
            }
    def _get_analyst_recommendations(self, symbol: str) -> Dict[str, Any]:
        """Get analyst recommendations"""
        url = f"https://finance.yahoo.com/quote/{symbol}/analysis"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to retrieve data: Status code {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the recommendation table
        recommendation_table = None
        tables = soup.find_all('table')
        for table in tables:
            if table.find('th') and 'Recommendation' in table.find('th').text:
                recommendation_table = table
                break
        
        if not recommendation_table:
            return {}
        
        # Extract recommendation data
        recommendations = {}
        rows = recommendation_table.find_all('tr')
        
        for row in rows[1:]:  # Skip header row
            cells = row.find_all('td')
            if len(cells) >= 2:
                rating = cells[0].text.strip()
                count = cells[1].text.strip()
                try:
                    recommendations[rating] = int(count)
                except ValueError:
                    recommendations[rating] = 0
        print("recommendations",recommendations)
        return recommendations
    
    def _get_income_statements(self, symbol: str) -> Dict[str, Any]:
        """Get income statements"""
        url = f"https://finance.yahoo.com/quote/{symbol}/financials"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to retrieve data: Status code {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the income statement table
        income_table = None
        tables = soup.find_all('div', {'class': 'D(tbr)'})
        
        if not tables:
            return {}
        
        # Extract income statement data
        financials = {}
        for row in tables:
            cells = row.find_all('div', {'class': 'D(tbc)'})
            if cells and len(cells) > 1:
                key = cells[0].text.strip()
                values = [cell.text.strip() for cell in cells[1:]]
                financials[key] = values
        print("income" ,financials)
        return financials
    
    def _fetch_yahoo_finance_history(self, ticker, start_date=None, end_date=None):
        """
        Fetch historical stock data from Yahoo Finance using web scraping.
        
        Args:
            ticker (str): Stock ticker symbol (e.g., 'AAPL')
            start_date (str, optional): Start date in format 'YYYY-MM-DD'
            end_date (str, optional): End date in format 'YYYY-MM-DD'
        
        Returns:
            pandas.DataFrame: Historical stock data
        """
        try:
            # Convert dates to UNIX timestamp if provided
            params = {}
            if start_date:
                start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
                params['period1'] = start_timestamp
            if end_date:
                end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())
                params['period2'] = end_timestamp
            else:
                # Current time if end_date not provided
                params['period2'] = int(datetime.now().timestamp())
            
            # Default parameters
            if 'period1' not in params:
                # Default to 1 year ago if start_date not provided
                one_year_ago = int(datetime.now().timestamp()) - 31536000
                params['period1'] = one_year_ago
            
            params['interval'] = '1d'  # Daily data
            
            # Create URL
            base_url = f"https://finance.yahoo.com/quote/{ticker}/history"
            
            # Send request with headers to mimic browser
            headers = {
                'User-Agent': 'Mozilla/5.0'
            }
            
            print(f"Fetching data from: {base_url}")
            response = requests.get(base_url, params=params, headers=headers)
            
            if response.status_code != 200:
                print(f"Failed to fetch data: Status code {response.status_code}")
                # Return a minimal DataFrame with the necessary columns as fallback
                return pd.DataFrame({
                    'Date': pd.date_range(end=datetime.now(), periods=100),
                    'Close': [100.0] * 100,
                    'Volume': [1000000] * 100
                })
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the data table using the specific class
            data_table = soup.find('table', {'class': 'W(100%) M(0)'})
            
            if not data_table:
                data_table = soup.find('table', {'data-test': 'historical-prices'})
                
            if not data_table:
                data_table = soup.find('table', {'class': 'table yf-1jecxey noDl hideOnPrint'})
            
            if not data_table:
                print("Could not find historical data table on the page")
                # Return a minimal DataFrame with the necessary columns as fallback
                return pd.DataFrame({
                    'Date': pd.date_range(end=datetime.now(), periods=100),
                    'Close': [100.0] * 100,
                    'Volume': [1000000] * 100
                })
            
            # Extract table headers
            headers = []
            header_row = data_table.find('thead').find_all('th')
            for header in header_row:
                headers.append(header.text.strip())
            
            # Extract table data
            rows = []
            data_rows = data_table.find('tbody').find_all('tr')
            
            for row in data_rows:
                cols = row.find_all('td')
                if len(cols) >= 6:  # Make sure it's a data row, not a dividend row
                    row_data = []
                    for col in cols:
                        row_data.append(col.text.strip())
                    rows.append(row_data)
            
            # Create DataFrame
            df = pd.DataFrame(rows, columns=headers)
            
            if df.empty:
                print("No data rows found in the table")
                # Return a minimal DataFrame with the necessary columns as fallback
                return pd.DataFrame({
                    'Date': pd.date_range(end=datetime.now(), periods=100),
                    'Close': [100.0] * 100,
                    'Volume': [1000000] * 100
                })
            
            # Convert data types
            if 'Date' in df.columns:
                try:
                    # Try converting with a specific format for dates like "Apr 30, 2025"
                    df['Date'] = pd.to_datetime(df['Date'], format='%b %d, %Y', errors='coerce')
                except Exception as e:
                    print(f"Error converting dates with specific format: {str(e)}")
                    try:
                        # Try parsing with pandas' automatic parser
                        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                    except Exception as e:
                        print(f"Error with automatic date parsing: {str(e)}")
                        # Last resort - create a date range
                        df['Date'] = pd.date_range(end=datetime.now(), periods=len(df))
            
            # Handle numeric columns
            numeric_columns = ['Open', 'High', 'Low', 'Close*', 'Adj Close**', 'Volume']
            for col in numeric_columns:
                if col in df.columns:
                    # Remove commas and convert to float
                    df[col] = df[col].replace('-', '0')  # Replace dash with 0
                    df[col] = df[col].str.replace(',', '')
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Special handling for column names that may contain descriptions
            adj_close_col = None
            for col in df.columns:
                if col.startswith('Adj Close'):
                    adj_close_col = col
                    break
            
            close_col = None
            for col in df.columns:
                if col.startswith('Close') and col != 'Close':
                    close_col = col
                    break
            
            # Create standardized Close and Adj Close columns
            if adj_close_col:
                df['Adj Close'] = df[adj_close_col].astype(float)
            
            if close_col:
                df['Close'] = df[close_col].astype(float)
            
            # If we have all the necessary columns, drop the redundant ones
            if 'Close' in df.columns and 'Adj Close' in df.columns:
                # Find the indices to drop
                drop_cols = []
                for i, col in enumerate(df.columns):
                    if (col.startswith('Close') and col != 'Close') or (col.startswith('Adj Close') and col != 'Adj Close'):
                        drop_cols.append(i)
                
                if drop_cols:
                    df = df.drop(df.columns[drop_cols], axis=1, errors='ignore')
            
            # Ensure we have the Close column
            if 'Close' not in df.columns and 'Adj Close' in df.columns:
                df['Close'] = df['Adj Close']
            
            # print(df.head())
            return df
            
        except Exception as e:
            print(f"Error in fetch_yahoo_finance_history: {str(e)}")
            # Return a minimal DataFrame with the necessary columns
            return pd.DataFrame({
                'Date': pd.date_range(end=datetime.now(), periods=100),
                'Close': [100.0] * 100,
                'Volume': [1000000] * 100
            })
            
    def _calculate_technical_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate technical indicators"""
        try:
            # Calculate RSI
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # Calculate MACD
            exp1 = data['Close'].ewm(span=12, adjust=False).mean()
            exp2 = data['Close'].ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            
            # print({
            #     'rsi': float(rsi.iloc[-1]) if not rsi.empty else 0.0,
            #     'macd': float(macd.iloc[-1]) if not macd.empty else 0.0,
            #     'macd_signal': float(signal.iloc[-1]) if not signal.empty else 0.0,
            #     'sma_50': float(data['Close'].rolling(window=50).mean().iloc[-1]) if len(data) >= 50 else 0.0,
            #     'sma_200': float(data['Close'].rolling(window=200).mean().iloc[-1]) if len(data) >= 200 else 0.0
            # })
            
            # Return numerical values (not strings) to avoid formatting issues in app.py
            return {
                'rsi': float(rsi.iloc[-1]) if not rsi.empty else 0.0,
                'macd': float(macd.iloc[-1]) if not macd.empty else 0.0,
                'macd_signal': float(signal.iloc[-1]) if not signal.empty else 0.0,
                'sma_50': float(data['Close'].rolling(window=50).mean().iloc[-1]) if len(data) >= 50 else 0.0,
                'sma_200': float(data['Close'].rolling(window=200).mean().iloc[-1]) if len(data) >= 200 else 0.0
            }
            
        except Exception as e:
            print(f"Error calculating technical indicators: {str(e)}")
            # Return default numeric values instead of empty dict
            
            return {
                'rsi': 50.0,
                'macd': 0.0,
                'macd_signal': 0.0,
                'sma_50': 0.0,
                'sma_200': 0.0
            }
        
    def get_stock_fundamentals(self, symbol: str) -> str:
        """Use this function to get comprehensive fundamental data for a given stock symbol using web scraping.

        Args:
            symbol (str): The stock symbol (e.g., 'AAPL').

        Returns:
            str: A JSON string containing fundamental data or an error message.
        """
        try:
            # Construct the URLs for different pages
            summary_url = f"https://finance.yahoo.com/quote/{symbol}"
           
            
            # Use a proper User-Agent to avoid being blocked
            headers = {
                "User-Agent": "Mozilla/5.0"
            }
            
            # Initialize the fundamentals dictionary
            fundamentals = {}
            
            # Get additional data from summary page
            summary_response = requests.get(summary_url, headers=headers)
            if summary_response.status_code == 200:
                summary_soup = BeautifulSoup(summary_response.text, 'html.parser')
                
                # Try to extract any missing important metrics
                quote_statistics = summary_soup.find('div', {'data-testid': 'quote-statistics'})
                if quote_statistics:
                    stats_items = quote_statistics.find_all('li')
                    for item in stats_items:
                        label_elem = item.find('span', {'class': 'label'})
                        value_elem = item.find('span', {'class': 'value'})
                        if label_elem and value_elem:
                            label = label_elem.get('title') or label_elem.text.strip()
                            value = value_elem.text.strip()
                            fundamentals[label] = value
            
            return json.dumps(fundamentals, indent=2)
        
        except Exception as e:
            return f"Error getting fundamentals for {symbol}: {str(e)}"
        
        
    def get_key_financial_ratios(self, symbol: str) -> str:
        """Use this function to get key financial ratios for a given stock symbol.
        
        Args:
            symbol (str): The stock symbol.
            
        Returns:
            dict: JSON containing key financial ratios.
        """
        try:
            # Construct the URL
            url = f"https://finance.yahoo.com/quote/{symbol}/key-statistics"
            
            # Use a proper User-Agent to avoid being blocked
            headers = {
                "User-Agent": "Mozilla/5.0"
            }
            
            # Send the request
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                return f"Failed to retrieve data: Status code {response.status_code}"
            
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Initialize dictionary to store the results
            ratios = {}
            
            # Find all tables with financial information
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        label = cells[0].text.strip()
                        value = cells[1].text.strip()
                        ratios[label] = value
            # print("get_key_financial_ratios",ratios)
            return json.dumps(ratios, indent=2)
        except Exception as e:
            return f"Error fetching key financial ratios for {symbol}: {e}"

def save_to_csv(df, filename):
    """Save DataFrame to CSV file"""
    df.to_csv(filename, index=False)
    # print(f"Data saved to {filename}")
    # A:\Uttam\Apps\temp\ai-stock-advisor-main\tools.py