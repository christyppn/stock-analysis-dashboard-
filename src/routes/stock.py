from flask import Blueprint, request, jsonify
from src.services.alpha_vantage_service import AlphaVantageService
from datetime import datetime, timedelta
import traceback
import os

stock_bp = Blueprint('stock', __name__)

# 從環境變量獲取API密鑰，如果沒有則使用提供的密鑰
API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '516YUUJAI4IMIUBG')
stock_service = AlphaVantageService(API_KEY)

@stock_bp.route('/health', methods=['GET'])
def health_check():
    """健康檢查端點"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Stock Analyzer API'
    })

@stock_bp.route('/market/overview', methods=['GET'])
def get_market_overview():
    """獲取市場概覽"""
    try:
        market = request.args.get('market', 'US')
        if market not in ['US', 'HK']:
            return jsonify({'error': '無效的市場參數'}), 400
        
        overview = stock_service.get_market_overview(market)
        return jsonify(overview)
        
    except Exception as e:
        return jsonify({'error': f'獲取市場概覽失敗: {str(e)}'}), 500

@stock_bp.route('/market/potential', methods=['GET'])
def get_potential_stocks():
    """獲取潛力股票"""
    try:
        market = request.args.get('market', 'US')
        limit = int(request.args.get('limit', 10))
        
        if market not in ['US', 'HK']:
            return jsonify({'error': '無效的市場參數'}), 400
        
        if limit > 50:
            limit = 50
        
        potential_stocks = stock_service.get_potential_stocks(market, limit)
        
        return jsonify({
            'market': market,
            'stocks': potential_stocks,
            'count': len(potential_stocks),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'獲取潛力股票失敗: {str(e)}'}), 500

@stock_bp.route('/stocks/<symbol>/analysis', methods=['GET'])
def get_stock_analysis(symbol):
    """獲取股票詳細分析"""
    try:
        symbol = symbol.upper()
        analysis = stock_service.analyze_stock(symbol)
        
        if 'error' in analysis:
            return jsonify(analysis), 404
        
        # 獲取股票基本信息
        stock_info = stock_service.get_stock_info(symbol)
        if stock_info:
            analysis['info'] = stock_info
        
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({'error': f'分析股票失敗: {str(e)}'}), 500

@stock_bp.route('/stocks/<symbol>/data', methods=['GET'])
def get_stock_data(symbol):
    """獲取股票歷史數據"""
    try:
        symbol = symbol.upper()
        period = request.args.get('period', '3mo')  # 默認3個月
        
        # 驗證period參數
        valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
        if period not in valid_periods:
            return jsonify({'error': '無效的時間週期參數'}), 400
        
        data = stock_service.get_historical_data(symbol, period)
        if data is None or data.empty:
            return jsonify({'error': f'無法獲取 {symbol} 的數據'}), 404
        
        # 計算技術指標
        data = stock_service.calculate_technical_indicators(data)
        
        # 轉換為JSON格式
        result = {
            'symbol': symbol,
            'period': period,
            'data': data.to_dict('records'),
            'count': len(data),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'獲取股票數據失敗: {str(e)}'}), 500

@stock_bp.route('/stocks/<symbol>/signals', methods=['GET'])
def get_stock_signals(symbol):
    """獲取股票信號"""
    try:
        symbol = symbol.upper()
        days = int(request.args.get('days', 30))  # 默認30天
        
        # 獲取歷史數據
        data = stock_service.get_historical_data(symbol, '1y')
        if data is None or data.empty:
            return jsonify({'error': f'無法獲取 {symbol} 的數據'}), 404
        
        # 計算技術指標
        data = stock_service.calculate_technical_indicators(data)
        
        # 檢測信號
        volume_signals = stock_service.detect_volume_surge(data)
        breakout_signals = stock_service.detect_breakout_signals(data)
        reversal_signals = stock_service.detect_reversal_signals(data)
        
        all_signals = volume_signals + breakout_signals + reversal_signals
        
        # 篩選指定天數內的信號
        cutoff_date = datetime.now().date() - timedelta(days=days)
        recent_signals = [s for s in all_signals if s['date'].date() >= cutoff_date]
        
        # 按日期排序
        recent_signals.sort(key=lambda x: x['date'], reverse=True)
        
        return jsonify({
            'symbol': symbol,
            'signals': recent_signals,
            'count': len(recent_signals),
            'days': days,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'獲取股票信號失敗: {str(e)}'}), 500

@stock_bp.route('/stocks/search', methods=['GET'])
def search_stocks():
    """搜索股票"""
    try:
        query = request.args.get('q', '').strip()
        market = request.args.get('market', 'ALL')
        
        if not query:
            return jsonify({'error': '請提供搜索關鍵字'}), 400
        
        results = stock_service.search_stocks(query, market)
        
        return jsonify({
            'query': query,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': f'搜索失敗: {str(e)}'}), 500

@stock_bp.route('/stocks/volume-surge', methods=['GET'])
def get_volume_surge_stocks():
    """獲取交易量激增的股票"""
    try:
        market = request.args.get('market', 'US')
        threshold = float(request.args.get('threshold', 2.0))
        
        if market not in ['US', 'HK']:
            return jsonify({'error': '無效的市場參數'}), 400
        
        surge_stocks = stock_service.get_volume_surge_stocks(market, threshold)
        
        return jsonify({
            'market': market,
            'threshold': threshold,
            'stocks': surge_stocks,
            'count': len(surge_stocks),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'獲取交易量激增股票失敗: {str(e)}'}), 500

@stock_bp.route('/stocks/batch-analysis', methods=['POST'])
def batch_analyze_stocks():
    """批量分析股票"""
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        
        if not symbols:
            return jsonify({'error': '請提供股票代碼列表'}), 400
        
        if len(symbols) > 20:
            return jsonify({'error': '一次最多分析20隻股票'}), 400
        
        results = []
        
        for symbol in symbols:
            try:
                symbol = symbol.upper()
                analysis = stock_service.analyze_stock(symbol)
                
                if 'error' not in analysis:
                    stock_info = stock_service.get_stock_info(symbol)
                    results.append({
                        'symbol': symbol,
                        'name': stock_info['name'] if stock_info else symbol,
                        'score': analysis['score'],
                        'latest_data': analysis['latest_data'],
                        'signal_count': len(analysis['signals']),
                        'technical_indicators': analysis['technical_indicators']
                    })
            except Exception as e:
                print(f"Error analyzing {symbol}: {e}")
                continue
        
        return jsonify({
            'results': results,
            'count': len(results),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'批量分析失敗: {str(e)}'}), 500

@stock_bp.route('/data/update', methods=['POST'])
def update_stock_data():
    """更新股票數據（管理員功能）"""
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        
        if not symbols:
            # 使用默認股票列表
            symbols = (stock_service.popular_stocks['US'][:10] + 
                      stock_service.popular_stocks['HK'][:10])
        
        updated_count = 0
        errors = []
        
        for symbol in symbols:
            try:
                # 獲取並保存數據
                hist_data = stock_service.get_historical_data(symbol, '1y')
                if hist_data is not None and not hist_data.empty:
                    hist_data = stock_service.calculate_technical_indicators(hist_data)
                    
                    if db_service.save_stock_data(symbol, hist_data):
                        # 檢測並保存信號
                        volume_signals = stock_service.detect_volume_surge(hist_data)
                        breakout_signals = stock_service.detect_breakout_signals(hist_data)
                        reversal_signals = stock_service.detect_reversal_signals(hist_data)
                        
                        all_signals = volume_signals + breakout_signals + reversal_signals
                        db_service.save_signals(symbol, all_signals)
                        
                        updated_count += 1
                    else:
                        errors.append(f"保存 {symbol} 數據失敗")
                else:
                    errors.append(f"無法獲取 {symbol} 數據")
                    
            except Exception as e:
                errors.append(f"處理 {symbol} 時出錯: {str(e)}")
        
        return jsonify({
            'updated_count': updated_count,
            'total_symbols': len(symbols),
            'errors': errors,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'更新數據失敗: {str(e)}'}), 500

@stock_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': '端點不存在'}), 404

@stock_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '內部服務器錯誤'}), 500

