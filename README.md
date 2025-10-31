# 股票潛力分析系統 (Stock Potential Analyzer)

基於K線信號和交易量分析的股票潛力識別系統，支持美國和香港股市。

## 功能特色

- 🔍 **雙市場支持** - 美國股市和香港股市數據分析
- 📊 **潛力股票排行榜** - 基於綜合評分的股票推薦
- 📈 **K線信號分析** - 多種技術指標和信號檢測
- 📉 **交易量分析** - 識別交易量異常增長的股票
- 🔎 **股票搜索功能** - 支持股票代碼和名稱搜索
- 📱 **響應式設計** - 支持桌面和移動設備

## 技術架構

### 後端
- **框架**: Flask + SQLAlchemy
- **數據源**: Alpha Vantage API
- **分析算法**: 技術指標計算、信號檢測
- **API**: RESTful API with CORS支持

### 前端
- **框架**: React + TypeScript
- **UI庫**: Tailwind CSS + shadcn/ui
- **圖表**: Recharts
- **圖標**: Lucide React

## 安裝和運行

### 環境要求
- Python 3.8+
- Node.js 16+
- Alpha Vantage API Key

### 後端安裝
```bash
cd stock-analyzer-backend
pip install -r requirements.txt
```

### 環境變量設置
創建 `.env` 文件：
```
ALPHA_VANTAGE_API_KEY=your_api_key_here
```

### 運行後端
```bash
python src/main.py
```

### 前端安裝和運行
```bash
cd stock-analyzer-frontend
npm install
npm run dev
```

## API文檔

### 基本端點
- `GET /api/health` - 健康檢查
- `GET /api/stocks/potential?market=US` - 獲取潛力股票
- `GET /api/stocks/search?q=AAPL` - 搜索股票
- `GET /api/stocks/analyze/{symbol}` - 分析特定股票
- `GET /api/market/overview?market=US` - 市場概覽

### 參數說明
- `market`: 市場代碼 (US/HK)
- `symbol`: 股票代碼 (如: AAPL, 0700.HK)
- `limit`: 結果數量限制

## 分析算法

### 1. K線信號識別
- 突破信號檢測（移動平均線突破）
- 反轉信號識別
- 趨勢確認信號

### 2. 交易量異常檢測
- 統計學方法識別交易量激增
- 多重標準差分析
- 歷史交易量對比

### 3. 綜合評分機制
- 技術指標得分（40%）
- 交易量得分（30%）
- 市場環境得分（20%）
- 基本面得分（10%）

## 部署

### 生產環境部署
```bash
# 構建前端
cd stock-analyzer-frontend
npm run build

# 複製到後端static目錄
cp -r dist/* ../stock-analyzer-backend/src/static/

# 部署後端
cd ../stock-analyzer-backend
python src/main.py
```

## 貢獻

歡迎提交Issue和Pull Request來改進這個項目。

## 許可證

MIT License

## 免責聲明

本系統僅供教育和研究目的使用，不構成投資建議。投資有風險，請謹慎決策。
