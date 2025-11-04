from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta
import json
import pandas as pd
import warnings

# 忽略类型相关的警告
warnings.filterwarnings("ignore", message=".*TypingOnly.*")

try:
    from data_service import DataService
    from chart_service import ChartService
except ImportError as e:
    print(f"导入错误: {e}")
    # 如果导入失败，尝试直接定义必要的类
    class DataService:
        def __init__(self):
            pass
        
        def get_cleaned_sales_details(self, start_date, end_date):
            return pd.DataFrame()
        
        def get_cleaned_orders(self, start_date, end_date):
            return pd.DataFrame()

    class ChartService:
        def __init__(self):
            pass

app = Flask(__name__)

# 初始化服务
def initialize_services():
    try:
        data_service = DataService()
        chart_service = ChartService()
        return data_service, chart_service
    except Exception as e:
        print(f"服务初始化失败: {e}")
        return DataService(), ChartService()
# 在应用启动时初始化
data_service, chart_service = initialize_services()   



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_data():
    global data_service, chart_service

    try:
        data = request.get_json()
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        analysis_type = data.get('analysis_type')
        
        if not all([start_date, end_date, analysis_type]):
            return jsonify({'error': '缺少必要参数'}), 400
        
        result = {}
        
        if analysis_type == 'overall_trend':
            # 整体销售趋势
            monthly_data = data_service.get_monthly_sales_trend(start_date, end_date)
            chart, analysis = chart_service.create_monthly_sales_trend_chart(monthly_data)
            result = {
                'chart': chart,
                'analysis': analysis,
                'type': 'single_chart'
            }
        
        elif analysis_type == 'monthly_champion_dealer':
            # 月度销冠经销商
            champion_data = data_service.get_monthly_dealer_champions(start_date, end_date)
            chart, analysis = chart_service.create_monthly_dealer_champions_chart(champion_data)
            result = {
                'chart': chart,
                'analysis': analysis,
                'type': 'single_chart',
                'table_data': champion_data.to_dict('records') if not champion_data.empty else []
            }
        
        elif analysis_type == 'dealer_sales_details':
            # 经销商销售明细
            dealer_data = data_service.get_dealer_sales_details(start_date, end_date)
            chart, analysis = chart_service.create_dealer_sales_details_chart(dealer_data)
            result = {
                'chart': chart,
                'analysis': analysis,
                'type': 'single_chart',
                'table_data': dealer_data.to_dict('records') if not dealer_data.empty else []
            }
        
        elif analysis_type == 'top_dealers_trend':
            # 前五名经销商趋势
            dealer_trends = data_service.get_top_dealers_monthly_trend(start_date, end_date)
            charts_data, analysis = chart_service.create_top_dealers_trend_charts(dealer_trends)
            result = {
                'charts': charts_data,
                'analysis': analysis,
                'type': 'multiple_charts'
            }
        
        elif analysis_type == 'dealer_product_composition':
            # 经销商产品组成
            dealer_compositions = data_service.get_top_dealers_product_composition(start_date, end_date)
            charts_data, analysis = chart_service.create_dealer_product_composition_charts(dealer_compositions)
            result = {
                'charts': charts_data,
                'analysis': analysis,
                'type': 'multiple_charts'
            }
        
        # ========== 新增的产品分析角度 ==========
        elif analysis_type == 'product_sales_details':
            # 产品销售明细
            product_data = data_service.get_product_sales_details(start_date, end_date)
            chart, analysis = chart_service.create_product_sales_details_chart(product_data)
            result = {
                'chart': chart,
                'analysis': analysis,
                'type': 'single_chart',
                'table_data': product_data.to_dict('records') if not product_data.empty else []
            }
        
        elif analysis_type == 'monthly_champion_product':
            # 月度销冠产品
            champion_product_data = data_service.get_monthly_product_champions(start_date, end_date)
            chart, analysis = chart_service.create_monthly_product_champions_chart(champion_product_data)
            result = {
                'chart': chart,
                'analysis': analysis,
                'type': 'single_chart',
                'table_data': champion_product_data.to_dict('records') if not champion_product_data.empty else []
            }
        
        elif analysis_type == 'top_products_trend':
            # 前五名产品趋势
            product_trends = data_service.get_top_products_monthly_trend(start_date, end_date)
            charts_data, analysis = chart_service.create_top_products_trend_charts(product_trends)
            result = {
                'charts': charts_data,
                'analysis': analysis,
                'type': 'multiple_charts'
            }
        # ========== 新增结束 ==========
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': f'分析失败: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)