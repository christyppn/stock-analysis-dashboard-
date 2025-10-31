import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional, Tuple
import requests
from src.models.stock import Stock, DailyData, Signal, MarketIndex, db

class StockDataService:
    """股票數據服務類"""
    
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
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
                'AMD', 'INTC', 'CRM', 'ORCL', 'ADBE', 'PYPL', 'UBER', 'ZOOM'
            ],
            'HK': [
                '0700.HK', '0941.HK', '0005.HK', '0388.HK', '1299.HK', '2318.HK',
                '0883.HK', '1810.HK', '3690.HK', '9988.HK', '1024.HK', '2020.HK'
            ]
        }
    
    def get_stock_info(self, symbol: str) -> Optional[Dict]:
        """獲取股票基本信息"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'name': info.get('longName', info.get('shortName', symbol)),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'market_cap': info.get('marketCap'),
                'market': 'HK' if '.HK' in symbol else 'US'
            }
        except Exception as e:
            print(f"Error getting stock info for {symbol}: {e}")
            return None
    
    def get_historical_data(self, symbol: str, period: str = '1y') -> Optional[pd.DataFrame]:
        """獲取歷史數據"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            
            if data.empty:
                return None
                
            # 重置索引，將日期作為列
            data.reset_index(inplace=True)
            data.columns = [col.lower().replace(' ', '_') for col in data.columns]
            
            return data
        except Exception as e:
            print(f"Error getting historical data for {symbol}: {e}")
            return None
    
    def calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """計算技術指標"""
        if data.empty:
            return data
            
        # 移動平均線
        data['sma_20'] = data['close'].rolling(window=20).mean()
        data['sma_50'] = data['close'].rolling(window=50).mean()
        
        # RSI
        data['rsi'] = self._calculate_rsi(data['close'])
        
        # MACD
        macd_data = self._calculate_macd(data['close'])
        data['macd'] = macd_data['macd']
        data['macd_signal'] = macd_data['signal']
        
        # 布林帶
        bb_data = self._calculate_bollinger_bands(data['close'])
        data['bb_upper'] = bb_data['upper']
        data['bb_lower'] = bb_data['lower']
        
        # 交易量指標
        data['volume_sma_20'] = data['volume'].rolling(window=20).mean()
        data['volume_ratio'] = data['volume'] / data['volume_sma_20']
        
        return data
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """計算RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """計算MACD"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal).mean()
        
        return {
            'macd': macd,
            'signal': macd_signal,
            'histogram': macd - macd_signal
        }
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2) -> Dict:
        """計算布林帶"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        
        return {
            'upper': sma + (std * std_dev),
            'lower': sma - (std * std_dev),
            'middle': sma
        }
    
    def detect_volume_surge(self, data: pd.DataFrame, threshold: float = 2.0) -> List[Dict]:
        """檢測交易量激增"""
        signals = []
        
        if 'volume_ratio' not in data.columns:
            return signals
            
        # 找出交易量比率超過閾值的日期
        surge_days = data[data['volume_ratio'] > threshold]
        
        for idx, row in surge_days.iterrows():
            if pd.notna(row['volume_ratio']):
                signals.append({
                    'date': row['date'],
                    'type': 'volume_surge',
                    'strength': min(row['volume_ratio'] * 20, 100),  # 轉換為0-100分數
                    'price': row['close'],
                    'volume': row['volume'],
                    'description': f"交易量激增 {row['volume_ratio']:.1f}倍"
                })
        
        return signals
    
    def detect_breakout_signals(self, data: pd.DataFrame) -> List[Dict]:
        """檢測突破信號"""
        signals = []
        
        if len(data) < 50:  # 需要足夠的數據
            return signals
            
        for i in range(50, len(data)):
            current = data.iloc[i]
            previous = data.iloc[i-1]
            
            # 價格突破20日均線
            if (current['close'] > current['sma_20'] and 
                previous['close'] <= previous['sma_20'] and
                pd.notna(current['sma_20'])):
                
                strength = 60
                if current['volume'] > current.get('volume_sma_20', 0) * 1.5:
                    strength += 20  # 成交量配合
                
                signals.append({
                    'date': current['date'],
                    'type': 'sma_breakout',
                    'strength': strength,
                    'price': current['close'],
                    'volume': current['volume'],
                    'description': f"突破20日均線 (${current['sma_20']:.2f})"
                })
            
            # 布林帶突破
            if (pd.notna(current['bb_upper']) and 
                current['close'] > current['bb_upper'] and
                previous['close'] <= previous['bb_upper']):
                
                signals.append({
                    'date': current['date'],
                    'type': 'bollinger_breakout',
                    'strength': 70,
                    'price': current['close'],
                    'volume': current['volume'],
                    'description': f"突破布林帶上軌 (${current['bb_upper']:.2f})"
                })
        
        return signals
    
    def detect_reversal_signals(self, data: pd.DataFrame) -> List[Dict]:
        """檢測反轉信號"""
        signals = []
        
        if len(data) < 30:
            return signals
            
        for i in range(2, len(data)):
            current = data.iloc[i]
            prev1 = data.iloc[i-1]
            prev2 = data.iloc[i-2]
            
            # 錘子線形態
            body = abs(current['close'] - current['open'])
            upper_shadow = current['high'] - max(current['close'], current['open'])
            lower_shadow = min(current['close'], current['open']) - current['low']
            
            if (lower_shadow > body * 2 and upper_shadow < body * 0.5 and
                current['close'] > current['open']):  # 陽線錘子
                
                signals.append({
                    'date': current['date'],
                    'type': 'hammer_reversal',
                    'strength': 65,
                    'price': current['close'],
                    'volume': current['volume'],
                    'description': "錘子線反轉信號"
                })
            
            # MACD金叉
            if (pd.notna(current['macd']) and pd.notna(current['macd_signal']) and
                current['macd'] > current['macd_signal'] and
                prev1['macd'] <= prev1['macd_signal']):
                
                signals.append({
                    'date': current['date'],
                    'type': 'macd_golden_cross',
                    'strength': 55,
                    'price': current['close'],
                    'volume': current['volume'],
                    'description': "MACD金叉信號"
                })
        
        return signals
    
    def analyze_stock(self, symbol: str) -> Dict:
        """綜合分析股票"""
        # 獲取歷史數據
        data = self.get_historical_data(symbol, '1y')
        if data is None or data.empty:
            return {'error': f'無法獲取 {symbol} 的數據'}
        
        # 計算技術指標
        data = self.calculate_technical_indicators(data)
        
        # 檢測各種信號
        volume_signals = self.detect_volume_surge(data)
        breakout_signals = self.detect_breakout_signals(data)
        reversal_signals = self.detect_reversal_signals(data)
        
        all_signals = volume_signals + breakout_signals + reversal_signals
        
        # 計算綜合評分
        recent_signals = [s for s in all_signals if 
                         (datetime.now().date() - s['date'].date()).days <= 30]
        
        total_score = sum(s['strength'] for s in recent_signals) / len(recent_signals) if recent_signals else 0
        
        # 獲取最新數據
        latest = data.iloc[-1] if not data.empty else {}
        
        return {
            'symbol': symbol,
            'latest_data': {
                'date': latest.get('date'),
                'close': latest.get('close'),
                'volume': latest.get('volume'),
                'change_pct': ((latest.get('close', 0) - data.iloc[-2].get('close', 0)) / 
                              data.iloc[-2].get('close', 1) * 100) if len(data) > 1 else 0
            },
            'signals': all_signals[-10:],  # 最近10個信號
            'score': round(total_score, 2),
            'technical_indicators': {
                'rsi': latest.get('rsi'),
                'macd': latest.get('macd'),
                'sma_20': latest.get('sma_20'),
                'sma_50': latest.get('sma_50'),
                'volume_ratio': latest.get('volume_ratio')
            }
        }
    
    def get_market_overview(self, market: str = 'US') -> Dict:
        """獲取市場概覽"""
        indices_data = []
        
        for symbol, name in self.market_indices.get(market, []):
            data = self.get_historical_data(symbol, '5d')
            if data is not None and not data.empty:
                latest = data.iloc[-1]
                prev = data.iloc[-2] if len(data) > 1 else latest
                
                change = latest['close'] - prev['close']
                change_pct = (change / prev['close']) * 100
                
                indices_data.append({
                    'symbol': symbol,
                    'name': name,
                    'price': latest['close'],
                    'change': change,
                    'change_pct': change_pct,
                    'volume': latest['volume']
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
        
        for symbol in stocks[:20]:  # 分析前20隻股票
            try:
                analysis = self.analyze_stock(symbol)
                if 'error' not in analysis and analysis['score'] > 30:
                    stock_info = self.get_stock_info(symbol)
                    if stock_info:
                        results.append({
                            'symbol': symbol,
                            'name': stock_info['name'],
                            'score': analysis['score'],
                            'latest_price': analysis['latest_data']['close'],
                            'change_pct': analysis['latest_data']['change_pct'],
                            'recent_signals': len(analysis['signals']),
                            'rsi': analysis['technical_indicators']['rsi']
                        })
            except Exception as e:
                print(f"Error analyzing {symbol}: {e}")
                continue
        
        # 按評分排序
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]

class DatabaseService:
    """數據庫服務類"""
    
    @staticmethod
    def save_stock_data(symbol: str, data: pd.DataFrame):
        """保存股票數據到數據庫"""
        try:
            # 獲取或創建股票記錄
            stock = Stock.query.filter_by(symbol=symbol).first()
            if not stock:
                stock_info = StockDataService().get_stock_info(symbol)
                if stock_info:
                    stock = Stock(
                        symbol=symbol,
                        name=stock_info['name'],
                        market=stock_info['market'],
                        sector=stock_info['sector'],
                        industry=stock_info['industry'],
                        market_cap=stock_info['market_cap']
                    )
                    db.session.add(stock)
                    db.session.commit()
            
            if not stock:
                return False
            
            # 保存日線數據
            for _, row in data.iterrows():
                existing = DailyData.query.filter_by(
                    stock_id=stock.id, 
                    date=row['date'].date()
                ).first()
                
                if not existing:
                    daily_data = DailyData(
                        stock_id=stock.id,
                        date=row['date'].date(),
                        open_price=row['open'],
                        high_price=row['high'],
                        low_price=row['low'],
                        close_price=row['close'],
                        volume=row['volume'],
                        adj_close=row.get('adj_close'),
                        sma_20=row.get('sma_20'),
                        sma_50=row.get('sma_50'),
                        rsi=row.get('rsi'),
                        macd=row.get('macd'),
                        macd_signal=row.get('macd_signal'),
                        bb_upper=row.get('bb_upper'),
                        bb_lower=row.get('bb_lower'),
                        volume_sma_20=row.get('volume_sma_20'),
                        volume_ratio=row.get('volume_ratio')
                    )
                    db.session.add(daily_data)
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Error saving stock data: {e}")
            return False
    
    @staticmethod
    def save_signals(symbol: str, signals: List[Dict]):
        """保存信號到數據庫"""
        try:
            stock = Stock.query.filter_by(symbol=symbol).first()
            if not stock:
                return False
            
            for signal_data in signals:
                existing = Signal.query.filter_by(
                    stock_id=stock.id,
                    date=signal_data['date'].date(),
                    signal_type=signal_data['type']
                ).first()
                
                if not existing:
                    signal = Signal(
                        stock_id=stock.id,
                        date=signal_data['date'].date(),
                        signal_type=signal_data['type'],
                        strength=signal_data['strength'],
                        price=signal_data['price'],
                        volume=signal_data['volume'],
                        description=signal_data['description']
                    )
                    db.session.add(signal)
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Error saving signals: {e}")
            return False

