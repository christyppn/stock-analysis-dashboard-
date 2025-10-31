from datetime import datetime, timedelta, date
from typing import List, Dict, Optional
import random

class MockStockDataService:
    """模擬股票數據服務類"""
    
    def __init__(self):
        # 美股和港股的主要指數
        self.market_indices = {
            'US': [
                ('^GSPC', 'S&P 500'),
                ('^DJI', 'Dow Jones'),
                ('^IXIC', 'NASDAQ')
            ],
            'HK': [
                ('^HSI', 'Hang Seng Index'),
                ('0000.HK', 'HSI Tech Index')
            ]
        }
        
        # 熱門股票列表
        self.popular_stocks = {
            'US': [
                {'symbol': 'AAPL', 'name': 'Apple Inc.', 'sector': 'Technology'},
                {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'sector': 'Technology'},
                {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'sector': 'Technology'},
                {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'sector': 'Consumer Discretionary'},
                {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'sector': 'Consumer Discretionary'},
                {'symbol': 'META', 'name': 'Meta Platforms, Inc.', 'sector': 'Technology'},
                {'symbol': 'NVDA', 'name': 'NVIDIA Corporation', 'sector': 'Technology'},
                {'symbol': 'NFLX', 'name': 'Netflix Inc.', 'sector': 'Communication Services'},
                {'symbol': 'AMD', 'name': 'Advanced Micro Devices', 'sector': 'Technology'},
                {'symbol': 'INTC', 'name': 'Intel Corporation', 'sector': 'Technology'},
                {'symbol': 'CRM', 'name': 'Salesforce, Inc.', 'sector': 'Technology'},
                {'symbol': 'ORCL', 'name': 'Oracle Corporation', 'sector': 'Technology'},
                {'symbol': 'ADBE', 'name': 'Adobe Inc.', 'sector': 'Technology'},
                {'symbol': 'PYPL', 'name': 'PayPal Holdings, Inc.', 'sector': 'Financial Services'},
                {'symbol': 'UBER', 'name': 'Uber Technologies, Inc.', 'sector': 'Technology'},
                {'symbol': 'ZOOM', 'name': 'Zoom Video Communications', 'sector': 'Technology'}
            ],
            'HK': [
                {'symbol': '0700.HK', 'name': 'TENCENT', 'sector': 'Technology'},
                {'symbol': '0941.HK', 'name': 'CHINA MOBILE', 'sector': 'Telecommunications'},
                {'symbol': '0005.HK', 'name': 'HSBC HOLDINGS', 'sector': 'Financial Services'},
                {'symbol': '0388.HK', 'name': 'HKEX', 'sector': 'Financial Services'},
                {'symbol': '1299.HK', 'name': 'AIA', 'sector': 'Insurance'},
                {'symbol': '2318.HK', 'name': 'Ping An Insurance Group', 'sector': 'Insurance'},
                {'symbol': '0883.HK', 'name': 'CNOOC', 'sector': 'Energy'},
                {'symbol': '1810.HK', 'name': 'Xiaomi Corporation', 'sector': 'Technology'},
                {'symbol': '3690.HK', 'name': 'Meituan', 'sector': 'Consumer Services'},
                {'symbol': '9988.HK', 'name': 'Alibaba Group Holding Limited', 'sector': 'Technology'},
                {'symbol': '1024.HK', 'name': 'Kuaishou Technology', 'sector': 'Technology'},
                {'symbol': '2020.HK', 'name': 'ANTA Sports Products', 'sector': 'Consumer Goods'}
            ]
        }
    
    def get_stock_info(self, symbol: str) -> Optional[Dict]:
        """獲取股票基本信息"""
        market = 'HK' if '.HK' in symbol else 'US'
        stocks = self.popular_stocks.get(market, [])
        
        for stock in stocks:
            if stock['symbol'] == symbol:
                return {
                    'symbol': symbol,
                    'name': stock['name'],
                    'sector': stock['sector'],
                    'industry': stock['sector'],
                    'market_cap': random.randint(10000000000, 3000000000000),
                    'market': market
                }
        return None
    
    def analyze_stock(self, symbol: str) -> Dict:
        """綜合分析股票"""
        stock_info = self.get_stock_info(symbol)
        if not stock_info:
            return {'error': f'無法獲取 {symbol} 的數據'}
        
        # 生成模擬數據
        base_price = random.uniform(50, 800)
        change_pct = random.uniform(-5, 5)
        
        # 生成模擬信號
        signals = []
        for i in range(5):
            signal_date = datetime.now() - timedelta(days=random.randint(1, 30))
            signals.append({
                'date': signal_date,
                'type': random.choice(['volume_surge', 'sma_breakout', 'bollinger_breakout', 'macd_golden_cross']),
                'strength': random.uniform(50, 90),
                'price': base_price * random.uniform(0.95, 1.05),
                'volume': random.randint(1000000, 50000000),
                'description': random.choice([
                    '交易量激增 2.5倍',
                    '突破20日均線',
                    '突破布林帶上軌',
                    'MACD金叉信號',
                    '錘子線反轉信號'
                ])
            })
        
        # 計算綜合評分
        total_score = sum(s['strength'] for s in signals) / len(signals) if signals else 0
        
        return {
            'symbol': symbol,
            'info': stock_info,
            'latest_data': {
                'date': datetime.now(),
                'close': base_price,
                'volume': random.randint(5000000, 100000000),
                'change_pct': change_pct
            },
            'signals': signals,
            'score': round(total_score, 2),
            'technical_indicators': {
                'rsi': random.uniform(30, 70),
                'macd': random.uniform(-2, 2),
                'sma_20': base_price * random.uniform(0.98, 1.02),
                'sma_50': base_price * random.uniform(0.95, 1.05),
                'volume_ratio': random.uniform(0.8, 3.0)
            }
        }
    
    def get_market_overview(self, market: str = 'US') -> Dict:
        """獲取市場概覽"""
        indices_data = []
        
        for symbol, name in self.market_indices.get(market, []):
            price = random.uniform(3000, 40000)
            change = random.uniform(-200, 200)
            change_pct = (change / price) * 100
            
            indices_data.append({
                'symbol': symbol,
                'name': name,
                'price': price,
                'change': change,
                'change_pct': change_pct,
                'volume': random.randint(1000000000, 5000000000)
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
        
        for stock in stocks[:limit]:
            analysis = self.analyze_stock(stock['symbol'])
            if 'error' not in analysis:
                results.append({
                    'symbol': stock['symbol'],
                    'name': stock['name'],
                    'score': analysis['score'],
                    'latest_price': analysis['latest_data']['close'],
                    'change_pct': analysis['latest_data']['change_pct'],
                    'recent_signals': len(analysis['signals']),
                    'rsi': analysis['technical_indicators']['rsi']
                })
        
        # 按評分排序
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]
    
    def get_volume_surge_stocks(self, market: str = 'US', threshold: float = 2.0) -> List[Dict]:
        """獲取交易量激增的股票"""
        stocks = self.popular_stocks.get(market, [])
        surge_stocks = []
        
        # 隨機選擇一些股票作為交易量激增的股票
        selected_stocks = random.sample(stocks, min(3, len(stocks)))
        
        for stock in selected_stocks:
            if random.random() > 0.5:  # 50%概率有交易量激增
                base_price = random.uniform(50, 800)
                volume_ratio = random.uniform(threshold, 5.0)
                
                surge_stocks.append({
                    'symbol': stock['symbol'],
                    'name': stock['name'],
                    'latest_price': base_price,
                    'volume_ratio': volume_ratio,
                    'signals': [{
                        'date': datetime.now() - timedelta(days=random.randint(0, 2)),
                        'type': 'volume_surge',
                        'strength': volume_ratio * 20,
                        'description': f'交易量激增 {volume_ratio:.1f}倍'
                    }],
                    'signal_count': 1
                })
        
        # 按交易量比率排序
        surge_stocks.sort(key=lambda x: x['volume_ratio'], reverse=True)
        return surge_stocks
    
    def search_stocks(self, query: str, market: str = 'ALL') -> List[Dict]:
        """搜索股票"""
        results = []
        markets_to_search = ['US', 'HK'] if market == 'ALL' else [market]
        
        for mkt in markets_to_search:
            if mkt in self.popular_stocks:
                for stock in self.popular_stocks[mkt]:
                    if query.upper() in stock['symbol'].upper() or query.upper() in stock['name'].upper():
                        results.append({
                            'symbol': stock['symbol'],
                            'name': stock['name'],
                            'market': mkt,
                            'sector': stock['sector']
                        })
        
        return results[:20]  # 限制結果數量

