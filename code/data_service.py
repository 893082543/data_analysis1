from utils import DatabaseConnector, categorize_product_name, convert_symbols_to_english
import pandas as pd
from datetime import datetime

class DataService:
    def __init__(self):
        self.db = DatabaseConnector()
    
    def get_cleaned_sales_details(self, start_date, end_date):
        """获取清洗后的销售明细数据"""
        query = """
        SELECT * FROM product_order_sales_return_details 
        WHERE 单据日期 BETWEEN %s AND %s 
        AND 单据状态 IN ('完结', '已审核')
        AND 会员名称 NOT IN ('陈思', '郭霏')
        """
        
        df = self.db.query_to_dataframe(query, (start_date, end_date))
        
        if df.empty:
            return df
        
        # 数据清洗
        df['商品名称'] = df['商品名称'].apply(convert_symbols_to_english)
        df['产品类别'] = df['商品名称'].apply(categorize_product_name)
        
        # 排除"其他"类别的产品
        df = df[df['产品类别'] != '其他']
        
        return df
    
    def get_cleaned_orders(self, start_date, end_date):
        """获取清洗后的订单数据"""
        query = """
        SELECT * FROM product_order 
        WHERE 单据日期 BETWEEN %s AND %s 
        AND 单据状态 IN ('开始送货', '拆单', '订单完结')
        AND 会员名称 NOT IN ('陈思', '郭霏')
        """
        
        df = self.db.query_to_dataframe(query, (start_date, end_date))
        return df
    
    def get_monthly_sales_trend(self, start_date, end_date):
        """获取月度销售趋势数据"""
        df = self.get_cleaned_sales_details(start_date, end_date)
        
        if df.empty:
            return pd.DataFrame()
        
        # 转换为月份
        df['月份'] = pd.to_datetime(df['单据日期']).dt.to_period('M')
        
        # 按月汇总
        monthly_sales = df.groupby('月份').agg({
            '销售金额': 'sum',
            '业绩额': 'sum'
        }).reset_index()
        
        monthly_sales['月份'] = monthly_sales['月份'].astype(str)
        
        return monthly_sales
    
    def get_monthly_dealer_champions(self, start_date, end_date):
        """获取月度销冠经销商数据"""
        df = self.get_cleaned_orders(start_date, end_date)
        
        if df.empty:
            return pd.DataFrame()
        
        df['月份'] = pd.to_datetime(df['单据日期']).dt.to_period('M')
        monthly_dealer_sales = df.groupby(['月份', '门店名称']).agg({
            '已付金额': 'sum'
        }).reset_index()
        
        # 找出每个月的销冠
        champion_idx = monthly_dealer_sales.groupby('月份')['已付金额'].idxmax()
        monthly_champions = monthly_dealer_sales.loc[champion_idx]
        
        monthly_champions['月份'] = monthly_champions['月份'].astype(str)
        
        return monthly_champions
    
    def get_monthly_product_champions(self, start_date, end_date):
        """获取月度销冠产品数据"""
        df = self.get_cleaned_sales_details(start_date, end_date)
        
        if df.empty:
            return pd.DataFrame()
        
        df['月份'] = pd.to_datetime(df['单据日期']).dt.to_period('M')
        monthly_product_sales = df.groupby(['月份', '产品类别']).agg({
            '销售金额': 'sum'
        }).reset_index()
        
        # 找出每个月的销冠产品
        champion_idx = monthly_product_sales.groupby('月份')['销售金额'].idxmax()
        monthly_champions = monthly_product_sales.loc[champion_idx]
        
        monthly_champions['月份'] = monthly_champions['月份'].astype(str)
        
        return monthly_champions
    
    def get_dealer_sales_details(self, start_date, end_date):
        """获取经销商销售明细"""
        df = self.get_cleaned_orders(start_date, end_date)
        
        if df.empty:
            return pd.DataFrame()
        
        dealer_sales = df.groupby('门店名称').agg({
            '已付金额': 'sum'
        }).reset_index().sort_values('已付金额', ascending=False)
        
        dealer_sales['排名'] = range(1, len(dealer_sales) + 1)
        
        return dealer_sales
    
    def get_product_sales_details(self, start_date, end_date):
        """获取产品销售明细"""
        df = self.get_cleaned_sales_details(start_date, end_date)
        
        if df.empty:
            return pd.DataFrame()
        
        product_sales = df.groupby('产品类别').agg({
            '销售金额': 'sum'
        }).reset_index().sort_values('销售金额', ascending=False)
        
        product_sales['排名'] = range(1, len(product_sales) + 1)
        
        return product_sales
    
    def get_top_dealers_monthly_trend(self, start_date, end_date, top_n=5):
        """获取前N名经销商月度趋势"""
        df = self.get_cleaned_orders(start_date, end_date)
        
        if df.empty:
            return {}
        
        # 获取总销售额前N的经销商
        total_dealer_sales = df.groupby('门店名称')['已付金额'].sum().nlargest(top_n)
        top_dealers = total_dealer_sales.index.tolist()
        
        # 获取每个经销商的月度数据
        df['月份'] = pd.to_datetime(df['单据日期']).dt.to_period('M')
        
        dealer_trends = {}
        for dealer in top_dealers:
            dealer_data = df[df['门店名称'] == dealer]
            monthly_data = dealer_data.groupby('月份')['已付金额'].sum().reset_index()
            monthly_data['月份'] = monthly_data['月份'].astype(str)
            dealer_trends[dealer] = monthly_data
        
        return dealer_trends
    
    def get_top_products_monthly_trend(self, start_date, end_date, top_n=5):
        """获取前N名产品月度趋势"""
        df = self.get_cleaned_sales_details(start_date, end_date)
        
        if df.empty:
            return {}
        
        # 获取总销售额前N的产品
        total_product_sales = df.groupby('产品类别')['销售金额'].sum().nlargest(top_n)
        top_products = total_product_sales.index.tolist()
        
        # 获取每个产品的月度数据
        df['月份'] = pd.to_datetime(df['单据日期']).dt.to_period('M')
        
        product_trends = {}
        for product in top_products:
            product_data = df[df['产品类别'] == product]
            monthly_data = product_data.groupby('月份')['销售金额'].sum().reset_index()
            monthly_data['月份'] = monthly_data['月份'].astype(str)
            product_trends[product] = monthly_data
        
        return product_trends
    
    def get_top_dealers_product_composition(self, start_date, end_date, top_n=5):
        """获取前N名经销商的产品组成"""
        df = self.get_cleaned_sales_details(start_date, end_date)
        
        if df.empty:
            return {}
        
        # 获取总销售额前N的经销商
        total_dealer_sales = df.groupby('门店名称')['销售金额'].sum().nlargest(top_n)
        top_dealers = total_dealer_sales.index.tolist()
        
        # 获取每个经销商的产品组成
        dealer_compositions = {}
        for dealer in top_dealers:
            dealer_data = df[df['门店名称'] == dealer]
            product_composition = dealer_data.groupby('产品类别')['销售金额'].sum().reset_index()
            
            # 将小于5%的部分归类为"其他"
            total_sales = product_composition['销售金额'].sum()
            product_composition['占比'] = product_composition['销售金额'] / total_sales * 100
            
            # 分离主要产品和次要产品
            major_products = product_composition[product_composition['占比'] >= 5]
            minor_products = product_composition[product_composition['占比'] < 5]
            
            if not minor_products.empty:
                other_sales = minor_products['销售金额'].sum()
                other_percentage = minor_products['占比'].sum()
                
                major_products = pd.concat([
                    major_products,
                    pd.DataFrame([{
                        '产品类别': '其他',
                        '销售金额': other_sales,
                        '占比': other_percentage
                    }])
                ], ignore_index=True)
            
            dealer_compositions[dealer] = major_products.sort_values('销售金额', ascending=False)
        
        return dealer_compositions