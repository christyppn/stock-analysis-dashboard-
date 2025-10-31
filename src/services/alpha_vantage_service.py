import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time

class AlphaVantageService:
    """Alpha Vantage API服務類"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.last_request_time = 0
        self.request_interval = 12  # Alpha Vantage免費版限制每分鐘5次請求
        
        # 美股和港股的主要指數
        self.market_indices = {
            'US': [
                ('SPY', 'S&P 500 ETF'),
                ('DIA', 'Dow Jones ETF'),
                ('QQQ', 'NASDAQ ETF')
            ],
            'HK': [
                ('2800.HK', 'Tracker Fund of Hong Kong'),
                ('2828.HK', 'Hang Seng H-Share Index ETF')
            ]
        }
        
        # 熱門股票列表
        self.popular_stocks = {
            'US': [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
                'AMD', 'INTC', 'CRM', 'ORCL', 'ADBE', 'PYPL', 'UBER', 'ZOOM'
            ],
            'HK': [
                '0700.HK', '0941.HK', '0005.HK', '0388.HK', '1299.HK', '2318.HK',
                '0883.HK', '1810.HK', '3690.HK', '9988.HK', '1024.HK', '2020.HK'
            ]
        }
    
    def _make_request(self, params: Dict) -> Optional[Dict]:
        """發送API請求並處理限制"""
        # 確保請求間隔
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_interval:
            time.sleep(self.request_interval - time_since_last)
        
        params['apikey'] = self.api_key
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            self.last_request_time = time.time()
            data = response.json()
            
            # 檢查API錯誤
            if 'Error Message' in data:
                print(f"Alpha Vantage API錯誤: {data['Error Message']}")
                return None
            
            if 'Note' in data:
                print(f"Alpha Vantage API限制: {data['Note']}")
                return None
                
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"API請求失敗: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON解析失敗: {e}")
            return None
    
    def get_stock_quote(self, symbol: str) -> Optional[Dict]:
        """獲取股票即時報價"""
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol
        }
        
        data = self._make_request(params)
        if not data or 'Global Quote' not in data:
            return None
        
        quote = data['Global Quote']
        
        try:
            return {
                'symbol': quote.get('01. symbol', symbol),
                'price': float(quote.get('05. price', 0)),
                'change': float(quote.get('09. change', 0)),
                'change_percent': quote.get('10. change percent', '0%').replace('%', ''),
                'volume': int(quote.get('06. volume', 0)),
                'latest_trading_day': quote.get('07. latest trading day'),
                'previous_close': float(quote.get('08. previous close', 0)),
                'open': float(quote.get('02. open', 0)),
                'high': float(quote.get('03. high', 0)),
                'low': float(quote.get('04. low', 0))
            }
        except (ValueError, TypeError) as e:
            print(f"數據解析錯誤: {e}")
            return None
    
    def get_daily_data(self, symbol: str, outputsize: str = 'compact') -> Optional[Dict]:
        """獲取日線數據"""
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': outputsize  # compact (100天) 或 full (20年)
        }
        
        data = self._make_request(params)
        if not data or 'Time Series (Daily)' not in data:
            return None
        
        time_series = data['Time Series (Daily)']
        
        # 轉換數據格式
        daily_data = []
        for date_str, values in sorted(time_series.items()):
            try:
                daily_data.append({
                    'date': date_str,
                    'open': float(values['1. open']),
                    'high': float(values['2. high']),
                    'low': float(values['3. low']),
                    'close': float(values['4. close']),
                    'volume': int(values['5. volume'])
                })
            except (ValueError, TypeError, KeyError):
                continue
        
        return {
            'symbol': symbol,
            'data': daily_data,
            'metadata': data.get('Meta Data', {})
        }
    
    def get_technical_indicators(self, symbol: str, indicator: str, **kwargs) -> Optional[Dict]:
        """獲取技術指標"""
        params = {
            'function': indicator,
            'symbol': symbol,
            'interval': kwargs.get('interval', 'daily'),
            'time_period': kwargs.get('time_period', 20),
            'series_type': kwargs.get('series_type', 'close')
        }
        
        # 添加其他參數
        for key, value in kwargs.items():
            if key not in ['interval', 'time_period', 'series_type']:
                params[key] = value
        
        data = self._make_request(params)
        if not data:
            return None
        
        # 根據指標類型解析數據
        for key in data.keys():
            if 'Technical Analysis' in key or 'SMA' in key or 'RSI' in key or 'MACD' in key:
                return {
                    'symbol': symbol,
                    'indicator': indicator,
                    'data': data[key],
                    'metadata': data.get('Meta Data', {})
                }
        
        return None
    
    def calculate_volume_surge(self, daily_data: List[Dict], threshold: float = 2.0) -> List[Dict]:
        """計算交易量激增信號"""
        if len(daily_data) < 20:
            return []
        
        signals = []
        
        # 計算20日平均交易量
        for i in range(19, len(daily_data)):
            current_volume = daily_data[i]['volume']
            
            # 計算前20天平均交易量
            avg_volume = sum(daily_data[j]['volume'] for j in range(i-19, i)) / 20
            
            if avg_volume > 0:
                volume_ratio = current_volume / avg_volume
                
                if volume_ratio >= threshold:
                    signals.append({
                        'date': daily_data[i]['date'],
                        'type': 'volume_surge',
                        'strength': min(volume_ratio * 20, 100),
                        'price': daily_data[i]['close'],
                        'volume': current_volume,
                        'volume_ratio': volume_ratio,
                        'description': f"交易量激增 {volume_ratio:.1f}倍"
                    })
        
        return signals
    
    def calculate_sma_signals(self, daily_data: List[Dict], period: int = 20) -> List[Dict]:
        """計算移動平均線信號"""
        if len(daily_data) < period + 1:
            return []
        
        signals = []
        
        # 計算SMA
        for i in range(period, len(daily_data)):
            current_price = daily_data[i]['close']
            prev_price = daily_data[i-1]['close']
            
            # 計算當前和前一天的SMA
            current_sma = sum(daily_data[j]['close'] for j in range(i-period+1, i+1)) / period
            prev_sma = sum(daily_data[j]['close'] for j in range(i-period, i)) / period
            
            # 檢測突破
            if prev_price <= prev_sma and current_price > current_sma:
                signals.append({
                    'date': daily_data[i]['date'],
                    'type': 'sma_breakout',
                    'strength': 60,
                    'price': current_price,
                    'volume': daily_data[i]['volume'],
                    'sma_value': current_sma,
                    'description': f"突破{period}日均線 (${current_sma:.2f})"
                })
        
        return signals
    
    def analyze_stock(self, symbol: str) -> Dict:
        """綜合分析股票"""
        # 獲取即時報價
        quote = self.get_stock_quote(symbol)
        if not quote:
            return {'error': f'無法獲取 {symbol} 的即時數據'}
        
        # 獲取日線數據
        daily_result = self.get_daily_data(symbol, 'compact')
        if not daily_result or not daily_result['data']:
            return {'error': f'無法獲取 {symbol} 的歷史數據'}
        
        daily_data = daily_result['data']
        
        # 計算各種信號
        volume_signals = self.calculate_volume_surge(daily_data)
        sma_signals = self.calculate_sma_signals(daily_data, 20)
        
        all_signals = volume_signals + sma_signals
        
        # 計算綜合評分
        recent_signals = [s for s in all_signals if 
                         (datetime.now() - datetime.strptime(s['date'], '%Y-%m-%d')).days <= 30]
        
        total_score = sum(s['strength'] for s in recent_signals) / len(recent_signals) if recent_signals else 0
        
        return {
            'symbol': symbol,
            'latest_data': {
                'date': quote['latest_trading_day'],
                'close': quote['price'],
                'volume': quote['volume'],
                'change_pct': float(quote['change_percent'].replace('%', '')) if quote['change_percent'] else 0,
                'open': quote['open'],
                'high': quote['high'],
                'low': quote['low']
            },
            'signals': all_signals[-10:],  # 最近10個信號
            'score': round(total_score, 2),
            'technical_indicators': {
                'volume_ratio': volume_signals[-1]['volume_ratio'] if volume_signals else 1.0,
                'sma_20': sma_signals[-1]['sma_value'] if sma_signals else quote['price']
            }
        }
    
    def get_market_overview(self, market: str = 'US') -> Dict:
        """獲取市場概覽"""
        indices_data = []
        
        for symbol, name in self.market_indices.get(market, []):
            quote = self.get_stock_quote(symbol)
            if quote:
                indices_data.append({
                    'symbol': symbol,
                    'name': name,
                    'price': quote['price'],
                    'change': quote['change'],
                    'change_pct': float(quote['change_percent'].replace('%', '')) if quote['change_percent'] else 0,
                    'volume': quote['volume']
                })
        
        return {
            'market': market,
            'indices': indices_data,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_potential_stocks(self, market: str = 'US', limit: int = 10) -> List[Dict]:
        """獲取潛力股票列表"""
        stocks = self.popular_stocks.get(market, [])
        results = []
        
        for symbol in stocks[:min(limit, 5)]:  # 限制API請求數量
            try:
                analysis = self.analyze_stock(symbol)
                if 'error' not in analysis and analysis['score'] > 30:
                    results.append({
                        'symbol': symbol,
                        'name': symbol,  # Alpha Vantage不提供公司名稱
                        'score': analysis['score'],
                        'latest_price': analysis['latest_data']['close'],
                        'change_pct': analysis['latest_data']['change_pct'],
                        'recent_signals': len(analysis['signals']),
                        'volume_ratio': analysis['technical_indicators'].get('volume_ratio', 1.0)
                    })
            except Exception as e:
                print(f"Error analyzing {symbol}: {e}")
                continue
        
        # 按評分排序
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]
    
    def search_stocks(self, query: str, market: str = 'ALL') -> List[Dict]:
        """搜索股票（基於預定義列表）"""
        results = []
        markets_to_search = ['US', 'HK'] if market == 'ALL' else [market]
        
        for mkt in markets_to_search:
            if mkt in self.popular_stocks:
                for symbol in self.popular_stocks[mkt]:
                    if query.upper() in symbol.upper():
                        results.append({
                            'symbol': symbol,
                            'name': symbol,
                            'market': mkt,
                            'sector': 'Technology'  # 簡化處理
                        })
        
        return results[:20]
