from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Stock(db.Model):
    __tablename__ = 'stocks'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    market = db.Column(db.String(10), nullable=False)  # US or HK
    sector = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    market_cap = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關聯到日線數據
    daily_data = db.relationship('DailyData', backref='stock', lazy=True, cascade='all, delete-orphan')
    signals = db.relationship('Signal', backref='stock', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'name': self.name,
            'market': self.market,
            'sector': self.sector,
            'industry': self.industry,
            'market_cap': self.market_cap,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class DailyData(db.Model):
    __tablename__ = 'daily_data'
    
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    open_price = db.Column(db.Float, nullable=False)
    high_price = db.Column(db.Float, nullable=False)
    low_price = db.Column(db.Float, nullable=False)
    close_price = db.Column(db.Float, nullable=False)
    volume = db.Column(db.BigInteger, nullable=False)
    adj_close = db.Column(db.Float)
    
    # 技術指標
    sma_20 = db.Column(db.Float)  # 20日移動平均
    sma_50 = db.Column(db.Float)  # 50日移動平均
    rsi = db.Column(db.Float)     # 相對強弱指標
    macd = db.Column(db.Float)    # MACD
    macd_signal = db.Column(db.Float)  # MACD信號線
    bb_upper = db.Column(db.Float)     # 布林帶上軌
    bb_lower = db.Column(db.Float)     # 布林帶下軌
    
    # 交易量分析
    volume_sma_20 = db.Column(db.Float)  # 20日平均交易量
    volume_ratio = db.Column(db.Float)   # 交易量比率
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('stock_id', 'date', name='_stock_date_uc'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'stock_id': self.stock_id,
            'date': self.date.isoformat() if self.date else None,
            'open': self.open_price,
            'high': self.high_price,
            'low': self.low_price,
            'close': self.close_price,
            'volume': self.volume,
            'adj_close': self.adj_close,
            'sma_20': self.sma_20,
            'sma_50': self.sma_50,
            'rsi': self.rsi,
            'macd': self.macd,
            'macd_signal': self.macd_signal,
            'bb_upper': self.bb_upper,
            'bb_lower': self.bb_lower,
            'volume_sma_20': self.volume_sma_20,
            'volume_ratio': self.volume_ratio
        }

class Signal(db.Model):
    __tablename__ = 'signals'
    
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    signal_type = db.Column(db.String(50), nullable=False)  # 信號類型
    strength = db.Column(db.Float, nullable=False)  # 信號強度 (0-100)
    price = db.Column(db.Float, nullable=False)     # 信號產生時的價格
    volume = db.Column(db.BigInteger)               # 信號產生時的交易量
    description = db.Column(db.Text)                # 信號描述
    
    # 預測相關
    target_price = db.Column(db.Float)              # 目標價格
    confidence = db.Column(db.Float)                # 信心度
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'stock_id': self.stock_id,
            'date': self.date.isoformat() if self.date else None,
            'signal_type': self.signal_type,
            'strength': self.strength,
            'price': self.price,
            'volume': self.volume,
            'description': self.description,
            'target_price': self.target_price,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class MarketIndex(db.Model):
    __tablename__ = 'market_indices'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)  # ^GSPC, ^HSI 等
    name = db.Column(db.String(100), nullable=False)
    market = db.Column(db.String(10), nullable=False)  # US or HK
    date = db.Column(db.Date, nullable=False)
    open_price = db.Column(db.Float, nullable=False)
    high_price = db.Column(db.Float, nullable=False)
    low_price = db.Column(db.Float, nullable=False)
    close_price = db.Column(db.Float, nullable=False)
    volume = db.Column(db.BigInteger)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('symbol', 'date', name='_index_date_uc'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'name': self.name,
            'market': self.market,
            'date': self.date.isoformat() if self.date else None,
            'open': self.open_price,
            'high': self.high_price,
            'low': self.low_price,
            'close': self.close_price,
            'volume': self.volume
        }

