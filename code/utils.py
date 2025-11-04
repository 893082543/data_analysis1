import pymysql
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import seaborn as sns
import numpy as np
from datetime import datetime, timedelta
import io
import base64
import re
import warnings
warnings.filterwarnings("ignore")

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

class DatabaseConnector:
    def __init__(self):
        # 请根据您的实际数据库配置修改这里
        self.config = {
            'host': 'localhost',  # 数据库主机地址
            'user': 'root',       # 数据库用户名
            'password': '12345678', # 数据库密码
            'database': 'lvnonghe', # 数据库名
            'charset': 'utf8mb4',
            'port': 3306          # MySQL端口，默认3306
        }
    
    def get_connection(self):
        try:
            conn = pymysql.connect(**self.config)
            print("数据库连接成功")
            return conn
        except Exception as e:
            print(f"数据库连接失败: {e}")
            return None
    
    def query_to_dataframe(self, query, params=None):
        conn = self.get_connection()
        if conn is None:
            print("无法建立数据库连接")
            return pd.DataFrame()
            
        try:
            df = pd.read_sql(query, conn, params=params)
            print(f"查询成功，返回 {len(df)} 行数据")
            return df
        except Exception as e:
            print(f"查询失败: {e}")
            return pd.DataFrame()
        finally:
            conn.close()

# 其他工具函数保持不变...
def convert_symbols_to_english(text):
    """将中文符号转换为英文符号"""
    if not isinstance(text, str):
        return text
    
    # 中文符号到英文符号的映射
    symbol_map = {
        '，': ',', '。': '.', '；': ';', '：': ':', '！': '!', 
        '？': '?', '（': '(', '）': ')', '【': '[', '】': ']',
        '"': '"', '＂': '"', '＇': "'", '《': '<', '》': '>'
    }
    
    for chinese, english in symbol_map.items():
        text = text.replace(chinese, english)
    
    return text

def categorize_product_name(name):
    """根据规则对商品名称进行分类"""
    if not isinstance(name, str):
        return '其他'
    
    name = convert_symbols_to_english(name)
    
    # 聚类规则（简化版）
    if '极银双星' in name:
        return '雷力闷棚专用极银双星套餐'
    elif '海德丰' in name:
        return '雷力海德丰'
    elif '多葆' in name and '3B' in name:
        return '雷力多葆(3B)'
    elif '海補1号' in name:
        return '雷力海補1号 海藻有机颗粒肥'
    elif '呼吸基' in name:
        return '雷力呼吸基 微生物菌剂'
    elif '壮能' in name and '10-6-9' in name:
        return '雷力壮能 10-6-9'
    elif '大美收' in name:
        if '20-20-20+TE' in name:
            return '雷力大美收 20-20-20+TE'
        elif '14-6-30+TE' in name:
            return '雷力大美收 14-6-30+TE'
        else:
            return '雷力大美收'
    elif '海聚收' in name:
        return '雷力海聚收'
    elif '海乐速' in name:
        return '雷力海乐速'
    elif '绿库' in name:
        return '雷力绿库系列'
    elif '壤护生' in name:
        return '壤护生 绿色木霉菌剂'
    elif '上好拌' in name:
        return '上好拌'
    elif '福达' in name:
        return '福达水剂'
    else:
        return '其他'

def format_currency(amount):
    """格式化金额为xxxx万元（xxxxxx元）形式"""
    if pd.isna(amount) or amount == 0:
        return "0万元（0元）"
    
    wan = amount / 10000
    yuan = amount
    return f"{wan:.2f}万元（{yuan:.0f}元）"

def plot_to_base64():
    """将当前图表转换为base64字符串"""
    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=100, bbox_inches='tight')
    img.seek(0)
    plot_data = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return plot_data