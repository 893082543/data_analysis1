from utils import plot_to_base64, format_currency
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

class ChartService:
    def __init__(self):
        pass
    
    def create_monthly_sales_trend_chart(self, monthly_data):
        """创建月度销售趋势图表"""
        if monthly_data.empty:
            return None, "暂无数据"
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # 销售金额折线图
        ax1.plot(monthly_data['月份'], monthly_data['销售金额'] / 10000, 
                marker='o', linewidth=2, markersize=6, color='#2E86AB')
        ax1.set_title('每月销售金额趋势', fontsize=14, fontweight='bold')
        ax1.set_ylabel('销售金额（万元）', fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # 添加数据标签
        for i, (month, sales) in enumerate(zip(monthly_data['月份'], monthly_data['销售金额'])):
            ax1.annotate(f'{sales/10000:.1f}', 
                        (month, sales/10000), 
                        textcoords="offset points", 
                        xytext=(0,10), 
                        ha='center',
                        fontsize=9)
        
        # 业绩额折线图
        ax2.plot(monthly_data['月份'], monthly_data['业绩额'] / 10000, 
                marker='s', linewidth=2, markersize=6, color='#A23B72')
        ax2.set_title('每月业绩额趋势', fontsize=14, fontweight='bold')
        ax2.set_ylabel('业绩额（万元）', fontsize=12)
        ax2.set_xlabel('月份', fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)
        
        # 添加数据标签
        for i, (month, performance) in enumerate(zip(monthly_data['月份'], monthly_data['业绩额'])):
            ax2.annotate(f'{performance/10000:.1f}', 
                        (month, performance/10000), 
                        textcoords="offset points", 
                        xytext=(0,10), 
                        ha='center',
                        fontsize=9)
        
        plt.tight_layout()
        
        # 生成分析文字
        total_sales = monthly_data['销售金额'].sum()
        total_performance = monthly_data['业绩额'].sum()
        avg_monthly_sales = monthly_data['销售金额'].mean()
        max_sales_month = monthly_data.loc[monthly_data['销售金额'].idxmax()]
        
        analysis_text = f"""
        整体销售趋势分析：
        - 总销售金额：{format_currency(total_sales)}
        - 总业绩额：{format_currency(total_performance)}
        - 月均销售金额：{format_currency(avg_monthly_sales)}
        - 销售最高月份：{max_sales_month['月份']}，销售额：{format_currency(max_sales_month['销售金额'])}
        - 销售金额与业绩额趋势基本一致，反映了良好的经营状况
        """
        
        return plot_to_base64(), analysis_text
    
    def create_monthly_dealer_champions_chart(self, champion_data):
        """创建月度销冠经销商图表"""
        if champion_data.empty:
            return None, "暂无数据"
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # 创建柱状图
        bars = ax.bar(champion_data['月份'], champion_data['已付金额'] / 10000, 
                     color='#4ECDC4', alpha=0.7)
        
        ax.set_title('月度销冠经销商销售情况', fontsize=16, fontweight='bold')
        ax.set_ylabel('销售金额（万元）', fontsize=12)
        ax.set_xlabel('月份', fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)
        
        # 添加数据标签
        for bar, dealer in zip(bars, champion_data['门店名称']):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{height:.1f}\n{dealer}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        # 生成分析文字
        total_sales = champion_data['已付金额'].sum()
        most_frequent_champion = champion_data['门店名称'].mode().iloc[0] if not champion_data.empty else "无"
        champion_count = champion_data['门店名称'].value_counts()
        
        analysis_text = f"""
        月度销冠经销商分析：
        - 销冠经销商总销售额：{format_currency(total_sales)}
        - 出现次数最多的销冠：{most_frequent_champion}（{champion_count[most_frequent_champion]}次）
        - 共有{len(champion_data['门店名称'].unique())}个不同的经销商成为月度销冠
        - 销冠经销商分布相对{'' if len(champion_data['门店名称'].unique()) <= 3 else '不'}集中
        """
        
        return plot_to_base64(), analysis_text
    
    def create_dealer_sales_details_chart(self, dealer_data):
        """创建经销商销售明细图表"""
        if dealer_data.empty:
            return None, "暂无数据"
        
        # 只显示前20名，避免图表过于拥挤
        display_data = dealer_data.head(20)
        
        fig, ax = plt.subplots(figsize=(15, 8))
        
        bars = ax.bar(display_data['门店名称'], display_data['已付金额'] / 10000, 
                     color='#45B7D1', alpha=0.7)
        
        ax.set_title('经销商销售金额排名（前20名）', fontsize=16, fontweight='bold')
        ax.set_ylabel('销售金额（万元）', fontsize=12)
        ax.set_xlabel('经销商名称', fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)
        
        # 添加数据标签
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{height:.1f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        # 生成分析文字
        total_sales = dealer_data['已付金额'].sum()
        top_dealer_sales = dealer_data['已付金额'].iloc[0] if not dealer_data.empty else 0
        top_dealer_share = (top_dealer_sales / total_sales * 100) if total_sales > 0 else 0
        
        analysis_text = f"""
        经销商销售明细分析：
        - 总销售金额：{format_currency(total_sales)}
        - 共有{len(dealer_data)}个经销商产生销售
        - 排名第一的经销商：{dealer_data.iloc[0]['门店名称'] if not dealer_data.empty else '无'}
        - 冠军经销商占比：{top_dealer_share:.1f}%
        - 前5名经销商总销售额：{format_currency(dealer_data.head(5)['已付金额'].sum())}
        """
        
        return plot_to_base64(), analysis_text
    
    def create_top_dealers_trend_charts(self, dealer_trends):
        """创建前五名经销商趋势图表"""
        if not dealer_trends:
            return [], "暂无数据"
        
        charts_data = []
        analysis_parts = []
        
        for dealer_name, trend_data in dealer_trends.items():
            fig, ax = plt.subplots(figsize=(10, 6))
            
            ax.plot(trend_data['月份'], trend_data['已付金额'] / 10000, 
                   marker='o', linewidth=2, markersize=6, color='#6A0572')
            ax.set_title(f'{dealer_name} - 月度销售趋势', fontsize=14, fontweight='bold')
            ax.set_ylabel('销售金额（万元）', fontsize=12)
            ax.set_xlabel('月份', fontsize=12)
            ax.tick_params(axis='x', rotation=45)
            ax.grid(True, alpha=0.3)
            
            # 添加数据标签
            for i, (month, sales) in enumerate(zip(trend_data['月份'], trend_data['已付金额'])):
                ax.annotate(f'{sales/10000:.1f}', 
                           (month, sales/10000), 
                           textcoords="offset points", 
                           xytext=(0,10), 
                           ha='center',
                           fontsize=8)
            
            plt.tight_layout()
            
            chart_base64 = plot_to_base64()
            
            # 生成单个经销商的分析
            total_sales = trend_data['已付金额'].sum()
            max_sales = trend_data['已付金额'].max()
            min_sales = trend_data['已付金额'].min()
            growth_rate = ((trend_data['已付金额'].iloc[-1] - trend_data['已付金额'].iloc[0]) / 
                          trend_data['已付金额'].iloc[0] * 100) if len(trend_data) > 1 and trend_data['已付金额'].iloc[0] > 0 else 0
            
            dealer_analysis = f"""
            {dealer_name}销售趋势分析：
            - 总销售额：{format_currency(total_sales)}
            - 最高月销售额：{format_currency(max_sales)}
            - 最低月销售额：{format_currency(min_sales)}
            - 销售增长率：{growth_rate:+.1f}%
            """
            
            charts_data.append({
                'name': dealer_name,
                'chart': chart_base64,
                'analysis': dealer_analysis
            })
            analysis_parts.append(dealer_analysis)
        
        overall_analysis = "前五名经销商逐月变化分析：\n" + "\n".join(analysis_parts)
        
        return charts_data, overall_analysis
    
    def create_dealer_product_composition_charts(self, dealer_compositions):
        """创建经销商产品组成饼图"""
        if not dealer_compositions:
            return [], "暂无数据"
        
        charts_data = []
        analysis_parts = []
        
        for dealer_name, composition in dealer_compositions.items():
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # 准备饼图数据
            labels = composition['产品类别']
            sales = composition['销售金额']
            percentages = composition['占比']
            
            # 创建饼图
            wedges, texts, autotexts = ax.pie(sales, labels=labels, autopct='%1.1f%%',
                                             startangle=90, colors=plt.cm.Set3(np.linspace(0, 1, len(labels))))
            
            # 设置标签样式
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            ax.set_title(f'{dealer_name} - 产品组成分析\n总销售额：{format_currency(sales.sum())}', 
                        fontsize=14, fontweight='bold')
            
            plt.tight_layout()
            
            chart_base64 = plot_to_base64()
            
            # 生成分析文字
            top_product = composition.iloc[0]
            product_diversity = len(composition)
            
            dealer_analysis = f"""
            {dealer_name}产品组成分析：
            - 总销售额：{format_currency(sales.sum())}
            - 主要产品数量：{product_diversity}个
            - 主打产品：{top_product['产品类别']}，占比{top_product['占比']:.1f}%
            - 产品结构{'' if product_diversity >= 5 else '相对'}集中
            """
            
            charts_data.append({
                'name': dealer_name,
                'chart': chart_base64,
                'analysis': dealer_analysis
            })
            analysis_parts.append(dealer_analysis)
        
        overall_analysis = "前五名经销商产品组成分析：\n" + "\n".join(analysis_parts)
        
        return charts_data, overall_analysis
    
    # ========== 新增的产品分析图表方法 ==========
    
    def create_product_sales_details_chart(self, product_data):
        """创建产品销售明细图表"""
        if product_data.empty:
            return None, "暂无数据"
        
        # 只显示前20名，避免图表过于拥挤
        display_data = product_data.head(20)
        
        fig, ax = plt.subplots(figsize=(15, 8))
        
        bars = ax.bar(display_data['产品类别'], display_data['销售金额'] / 10000, 
                     color='#FF6B6B', alpha=0.7)
        
        ax.set_title('产品销售金额排名（前20名）', fontsize=16, fontweight='bold')
        ax.set_ylabel('销售金额（万元）', fontsize=12)
        ax.set_xlabel('产品名称', fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)
        
        # 添加数据标签
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{height:.1f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        # 生成分析文字
        total_sales = product_data['销售金额'].sum()
        top_product_sales = product_data['销售金额'].iloc[0] if not product_data.empty else 0
        top_product_share = (top_product_sales / total_sales * 100) if total_sales > 0 else 0
        
        analysis_text = f"""
        产品销售明细分析：
        - 总销售金额：{format_currency(total_sales)}
        - 共有{len(product_data)}个产品产生销售
        - 排名第一的产品：{product_data.iloc[0]['产品类别'] if not product_data.empty else '无'}
        - 冠军产品占比：{top_product_share:.1f}%
        - 前5名产品总销售额：{format_currency(product_data.head(5)['销售金额'].sum())}
        """
        
        return plot_to_base64(), analysis_text
    
    def create_monthly_product_champions_chart(self, champion_data):
        """创建月度销冠产品图表"""
        if champion_data.empty:
            return None, "暂无数据"
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # 创建柱状图
        bars = ax.bar(champion_data['月份'], champion_data['销售金额'] / 10000, 
                     color='#4ECDC4', alpha=0.7)
        
        ax.set_title('月度销冠产品销售情况', fontsize=16, fontweight='bold')
        ax.set_ylabel('销售金额（万元）', fontsize=12)
        ax.set_xlabel('月份', fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)
        
        # 添加数据标签
        for bar, product in zip(bars, champion_data['产品类别']):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{height:.1f}\n{product}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        # 生成分析文字
        total_sales = champion_data['销售金额'].sum()
        most_frequent_champion = champion_data['产品类别'].mode().iloc[0] if not champion_data.empty else "无"
        champion_count = champion_data['产品类别'].value_counts()
        
        analysis_text = f"""
        月度销冠产品分析：
        - 销冠产品总销售额：{format_currency(total_sales)}
        - 出现次数最多的销冠产品：{most_frequent_champion}（{champion_count[most_frequent_champion]}次）
        - 共有{len(champion_data['产品类别'].unique())}个不同的产品成为月度销冠
        - 销冠产品分布相对{'' if len(champion_data['产品类别'].unique()) <= 3 else '不'}集中
        """
        
        return plot_to_base64(), analysis_text
    
    def create_top_products_trend_charts(self, product_trends):
        """创建前五名产品趋势图表"""
        if not product_trends:
            return [], "暂无数据"
        
        charts_data = []
        analysis_parts = []
        
        for product_name, trend_data in product_trends.items():
            fig, ax = plt.subplots(figsize=(10, 6))
            
            ax.plot(trend_data['月份'], trend_data['销售金额'] / 10000, 
                   marker='o', linewidth=2, markersize=6, color='#6A0572')
            ax.set_title(f'{product_name} - 月度销售趋势', fontsize=14, fontweight='bold')
            ax.set_ylabel('销售金额（万元）', fontsize=12)
            ax.set_xlabel('月份', fontsize=12)
            ax.tick_params(axis='x', rotation=45)
            ax.grid(True, alpha=0.3)
            
            # 添加数据标签
            for i, (month, sales) in enumerate(zip(trend_data['月份'], trend_data['销售金额'])):
                ax.annotate(f'{sales/10000:.1f}', 
                           (month, sales/10000), 
                           textcoords="offset points", 
                           xytext=(0,10), 
                           ha='center',
                           fontsize=8)
            
            plt.tight_layout()
            
            chart_base64 = plot_to_base64()
            
            # 生成单个产品的分析
            total_sales = trend_data['销售金额'].sum()
            max_sales = trend_data['销售金额'].max()
            min_sales = trend_data['销售金额'].min()
            growth_rate = ((trend_data['销售金额'].iloc[-1] - trend_data['销售金额'].iloc[0]) / 
                          trend_data['销售金额'].iloc[0] * 100) if len(trend_data) > 1 and trend_data['销售金额'].iloc[0] > 0 else 0
            
            product_analysis = f"""
            {product_name}销售趋势分析：
            - 总销售额：{format_currency(total_sales)}
            - 最高月销售额：{format_currency(max_sales)}
            - 最低月销售额：{format_currency(min_sales)}
            - 销售增长率：{growth_rate:+.1f}%
            """
            
            charts_data.append({
                'name': product_name,
                'chart': chart_base64,
                'analysis': product_analysis
            })
            analysis_parts.append(product_analysis)
        
        overall_analysis = "前五名产品逐月变化分析：\n" + "\n".join(analysis_parts)
        
        return charts_data, overall_analysis