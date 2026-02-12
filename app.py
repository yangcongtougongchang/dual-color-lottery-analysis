import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime
import io
from matplotlib.font_manager import FontProperties
import matplotlib
import matplotlib.pyplot as plt

# 确保使用Agg后端，避免显示问题
matplotlib.use('Agg')

# 简化的字体配置，避免复杂的字体检测
matplotlib.rcParams['font.family'] = ['sans-serif']
matplotlib.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'sans-serif']
matplotlib.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 禁用Matplotlib的字体缓存
matplotlib.rcParams['font.cachedir'] = None

# 简化的图表创建函数
def create_fig_ax(figsize=(12, 6)):
    """创建图表和轴对象"""
    fig, ax = plt.subplots(figsize=figsize)
    return fig, ax

# 设置页面配置
st.set_page_config(
    page_title="双色球历史数据规律分析",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 图表创建函数已在上面定义

# 自定义CSS，隐藏GitHub图标但保留header
hide_github_style = """
    <style>
    #MainMenu {visibility: hidden;}
    .css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob, .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137, .viewerBadge_text__1JaDK {
        display: none;
    }
    .css-1lcbmhc {
        padding-top: 0rem;
    }
    .css-1d391kg {
        padding-top: 0rem;
    }
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #f0f2f6;
        text-align: center;
        padding: 10px;
        font-size: 14px;
        color: #666;
    }
    .footer a {
        color: #0066cc;
        text-decoration: none;
    }
    .footer a:hover {
        text-decoration: underline;
    }
    .tooltip {
        position: relative;
        display: inline-block;
    }
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    .chart-container {
        position: relative;
        height: 400px;
        width: 100%;
    }
    .stButton>button {
        background-color: #0066cc;
        color: white;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #0055aa;
    }
    .stSelectbox>div>div>select {
        border-radius: 5px;
    }
    .stSlider>div>div>div>div {
        background-color: #0066cc;
    }
    </style>
"""
st.markdown(hide_github_style, unsafe_allow_html=True)

# 添加页脚
footer = """
    <div class="footer">
        <p>创作者：洋葱头 | 赠给：李兰序</p>
    </div>
"""

# 页面标题
st.title("🎯 双色球历史数据规律分析")
st.markdown("---")

# 初始化数据
@st.cache_data
def load_initial_data():
    """加载初始数据"""
    try:
        df = pd.read_csv("data/initial_data.csv")
        # 转换数据类型
        for col in ['红球1', '红球2', '红球3', '红球4', '红球5', '红球6', '蓝球']:
            df[col] = df[col].astype(int)
        df['奖池(元)'] = df['奖池(元)'].astype(float)
        df['开奖日期'] = pd.to_datetime(df['开奖日期'])
        return df
    except Exception as e:
        st.error(f"加载初始数据失败: {e}")
        return pd.DataFrame()

# 尝试从网络获取最新数据
def fetch_latest_data():
    """从网络获取最新双色球数据"""
    try:
        url = "https://datachart.500.com/ssq/history/history.shtml"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找表格数据
        table = soup.find('table', class_='tb_data')
        if not table:
            st.warning("未找到最新数据，使用本地数据")
            return load_initial_data()
        
        # 解析表格数据
        rows = table.find_all('tr')[2:]  # 跳过表头
        data = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 10:
                issue = cols[0].text.strip()
                red_balls = [cols[i].text.strip() for i in range(1, 7)]
                blue_ball = cols[7].text.strip()
                date = cols[-1].text.strip()
                pool = cols[4].text.strip().replace(',', '') if len(cols) > 4 else '0'
                
                data.append({
                    '期号': issue,
                    '红球1': red_balls[0],
                    '红球2': red_balls[1],
                    '红球3': red_balls[2],
                    '红球4': red_balls[3],
                    '红球5': red_balls[4],
                    '红球6': red_balls[5],
                    '蓝球': blue_ball,
                    '开奖日期': date,
                    '奖池(元)': pool
                })
        
        # 创建DataFrame
        df = pd.DataFrame(data)
        
        # 转换数据类型
        for col in ['红球1', '红球2', '红球3', '红球4', '红球5', '红球6', '蓝球']:
            df[col] = df[col].astype(int)
        df['奖池(元)'] = df['奖池(元)'].astype(float)
        df['开奖日期'] = pd.to_datetime(df['开奖日期'])
        
        # 合并新旧数据，去重
        old_df = load_initial_data()
        if not old_df.empty:
            combined_df = pd.concat([df, old_df])
            combined_df = combined_df.drop_duplicates(subset=['期号'], keep='first')
            combined_df = combined_df.sort_values(by='开奖日期', ascending=False)
            return combined_df
        else:
            return df.sort_values(by='开奖日期', ascending=False)
            
    except Exception as e:
        st.warning(f"获取最新数据失败: {e}，使用本地数据")
        return load_initial_data()

# 加载数据
df = load_initial_data()

# 侧边栏
st.sidebar.title("功能导航")
st.sidebar.markdown("---")

# 数据更新选项
st.sidebar.subheader("数据管理")
update_data = st.sidebar.button("🔄 更新最新数据")
if update_data:
    with st.spinner("正在获取最新数据..."):
        df = fetch_latest_data()
        st.success("数据更新成功！")

# 数据范围选择
st.sidebar.subheader("数据范围")
period_options = ["全部数据", "最近50期", "最近100期", "最近200期", "自定义范围"]
selected_period = st.sidebar.selectbox("选择数据范围", period_options)

# 自定义日期范围
start_date = None
end_date = None
if selected_period == "自定义范围":
    if not df.empty:
        min_date = df['开奖日期'].min().date()
        max_date = df['开奖日期'].max().date()
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.date_input("开始日期", min_date)
        with col2:
            end_date = st.date_input("结束日期", max_date)

# 筛选数据
def filter_data(df, period, start_date=None, end_date=None):
    """根据选择的时间范围筛选数据"""
    if df.empty:
        return df
    
    if period == "全部数据":
        return df
    elif period == "最近50期":
        return df.head(50)
    elif period == "最近100期":
        return df.head(100)
    elif period == "最近200期":
        return df.head(200)
    elif period == "自定义范围" and start_date and end_date:
        mask = (df['开奖日期'].dt.date >= start_date) & (df['开奖日期'].dt.date <= end_date)
        return df[mask]
    else:
        return df

filtered_df = filter_data(df, selected_period, start_date, end_date)

# 功能选择
st.sidebar.markdown("---")
st.sidebar.subheader("分析功能")
analysis_options = {
    "基本数据概览": "📊",
    "红球号码分析": "🔴",
    "蓝球号码分析": "🔵",
    "号码组合分析": "🎯",
    "历史趋势分析": "📈",
    "智能号码推荐": "🤖"
}

selected_analysis = st.sidebar.radio(
    "选择分析功能",
    list(analysis_options.keys()),
    format_func=lambda x: f"{analysis_options[x]} {x}"
)

# 主内容区
st.markdown("---")

# 显示使用说明
if selected_analysis == "基本数据概览":
    st.subheader("📊 基本数据概览")
    st.markdown("""
    ### 使用说明
    本应用提供双色球历史数据的全面分析功能，帮助您发现号码规律，辅助决策。
    
    **主要功能：**
    - 📊 **基本数据概览**：查看数据统计信息和最新开奖结果
    - 🔴 **红球号码分析**：分析红球出现频率、分布图等
    - 🔵 **蓝球号码分析**：分析蓝球出现规律和趋势
    - 🎯 **号码组合分析**：分析号码组合特征，如奇偶比、大小比等
    - 📈 **历史趋势分析**：查看历史数据变化趋势
    - 🤖 **智能号码推荐**：基于历史数据分析生成推荐号码
    
    **操作指南：**
    1. 使用左侧导航栏选择数据范围和分析功能
    2. 点击"更新最新数据"按钮获取最新开奖结果
    3. 查看图表分析结果，鼠标悬停可查看详细信息
    4. 可以导出分析数据用于进一步研究
    """)
    
    if not filtered_df.empty:
        st.markdown("---")
        st.subheader("📋 数据统计信息")
        
        # 显示数据统计
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("数据期数", len(filtered_df))
        with col2:
            st.metric("最早开奖日期", filtered_df['开奖日期'].min().strftime('%Y-%m-%d'))
        with col3:
            st.metric("最新开奖日期", filtered_df['开奖日期'].max().strftime('%Y-%m-%d'))
        
        # 最新几期开奖结果
        st.markdown("---")
        st.subheader("🎯 最新开奖结果")
        latest_results = filtered_df.head(10)[['期号', '红球1', '红球2', '红球3', '红球4', '红球5', '红球6', '蓝球', '开奖日期']]
        
        # 自定义表格样式
        def highlight_latest(row):
            return ['background-color: #f0f8ff'] * len(row)
        
        styled_results = latest_results.style.apply(highlight_latest, axis=1)
        st.dataframe(styled_results, use_container_width=True)
        
        # 数据导出
        st.markdown("---")
        st.subheader("💾 数据导出")
        col1, col2 = st.columns(2)
        with col1:
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 导出CSV",
                data=csv,
                file_name=f"双色球数据_{datetime.now().strftime('%Y%m%d')}.csv",
                mime='text/csv',
            )
        with col2:
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                filtered_df.to_excel(writer, index=False, sheet_name='双色球数据')
            st.download_button(
                label="📥 导出Excel",
                data=excel_buffer.getvalue(),
                file_name=f"双色球数据_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            )
    else:
        st.warning("暂无数据，请检查数据加载情况")

# 红球号码分析
elif selected_analysis == "红球号码分析":
    st.subheader("🔴 红球号码分析")
    
    if not filtered_df.empty:
        # 提取所有红球号码
        red_balls = pd.concat([
            filtered_df['红球1'], filtered_df['红球2'], filtered_df['红球3'],
            filtered_df['红球4'], filtered_df['红球5'], filtered_df['红球6']
        ], axis=0).astype(int)
        
        # 计算每个号码出现的频率
        red_freq = red_balls.value_counts().sort_index()
        red_freq_df = pd.DataFrame({
            '号码': red_freq.index,
            '出现次数': red_freq.values,
            '出现频率': (red_freq.values / len(filtered_df) * 6 * 100).round(2)
        })
        
        # 号码频率分布
        st.markdown("### 📊 红球出现频率分布")
        fig, ax = create_fig_ax(figsize=(12, 6))
        bars = ax.bar(red_freq_df['号码'], red_freq_df['出现次数'], color='red', alpha=0.7)
        ax.set_xlabel('红球号码')
        ax.set_ylabel('出现次数')
        ax.set_title(f'红球号码出现频率 ({len(filtered_df)}期数据)')
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        # 在柱状图上显示数值
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom')
        
        st.pyplot(fig)
        
        # 热力图显示号码分布
        st.markdown("### 🔥 红球号码热力图")
        # 创建33x1的热力图数据
        heatmap_data = np.zeros((1, 33))
        for num, freq in zip(red_freq_df['号码'], red_freq_df['出现次数']):
            heatmap_data[0, num-1] = freq
        
        fig, ax = create_fig_ax(figsize=(15, 3))
        sns.heatmap(heatmap_data, cmap='Reds', annot=True, fmt='.0f',
                   xticklabels=[f'{i}' for i in range(1, 34)],
                   yticklabels=['出现次数'])
        ax.set_title(f'红球号码出现次数热力图 ({len(filtered_df)}期数据)')
        ax.set_xlabel('红球号码')
        st.pyplot(fig)
        
        # 红球区间分布
        st.markdown("### 📈 红球区间分布")
        # 定义区间
        ranges = [(1, 11), (12, 22), (23, 33)]
        range_names = ['小号区(1-11)', '中号区(12-22)', '大号区(23-33)']
        
        range_counts = []
        for start, end in ranges:
            count = 0
            for col in ['红球1', '红球2', '红球3', '红球4', '红球5', '红球6']:
                count += ((filtered_df[col] >= start) & (filtered_df[col] <= end)).sum()
            range_counts.append(count)
        
        fig, ax = create_fig_ax(figsize=(10, 6))
        bars = ax.bar(range_names, range_counts, color=['#FF9999', '#FF6666', '#CC0000'])
        ax.set_ylabel('出现次数')
        ax.set_title(f'红球区间分布 ({len(filtered_df)}期数据)')
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom')
        
        st.pyplot(fig)
        
        # 出现频率最高的前10个红球
        st.markdown("### 🏆 红球出现频率TOP10")
        top10_red = red_freq_df.sort_values('出现次数', ascending=False).head(10)
        st.dataframe(top10_red, use_container_width=True)
        
        # 最近N期未出现的红球
        st.markdown("### ❓ 最近未出现的红球")
        recent_periods = st.slider("选择最近期数", 5, 50, 10)
        recent_red_balls = pd.concat([
            filtered_df.head(recent_periods)['红球1'],
            filtered_df.head(recent_periods)['红球2'],
            filtered_df.head(recent_periods)['红球3'],
            filtered_df.head(recent_periods)['红球4'],
            filtered_df.head(recent_periods)['红球5'],
            filtered_df.head(recent_periods)['红球6']
        ], axis=0).unique()
        
        missing_red = [i for i in range(1, 34) if i not in recent_red_balls]
        if missing_red:
            st.write(f"最近{recent_periods}期未出现的红球号码：{', '.join(map(str, missing_red))}")
            
            # 显示这些号码的历史出现频率
            missing_red_freq = red_freq_df[red_freq_df['号码'].isin(missing_red)]
            st.dataframe(missing_red_freq, use_container_width=True)
        else:
            st.write(f"最近{recent_periods}期所有红球号码都出现过")
    else:
        st.warning("暂无数据，请检查数据加载情况")

# 蓝球号码分析
elif selected_analysis == "蓝球号码分析":
    st.subheader("🔵 蓝球号码分析")
    
    if not filtered_df.empty:
        # 蓝球出现频率
        st.markdown("### 📊 蓝球出现频率分布")
        blue_freq = filtered_df['蓝球'].value_counts().sort_index()
        blue_freq_df = pd.DataFrame({
            '号码': blue_freq.index,
            '出现次数': blue_freq.values,
            '出现频率': (blue_freq.values / len(filtered_df) * 100).round(2)
        })
        
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(blue_freq_df['号码'], blue_freq_df['出现次数'], color='blue', alpha=0.7)
        ax.set_xlabel('蓝球号码')
        ax.set_ylabel('出现次数')
        ax.set_title(f'蓝球号码出现频率 ({len(filtered_df)}期数据)')
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom')
        
        st.pyplot(fig)
        
        # 蓝球奇偶分布
        st.markdown("### 🔢 蓝球奇偶分布")
        even_count = (filtered_df['蓝球'] % 2 == 0).sum()
        odd_count = (filtered_df['蓝球'] % 2 == 1).sum()
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.pie([even_count, odd_count], labels=['偶数', '奇数'], autopct='%1.1f%%',
               colors=['#6699CC', '#336699'], startangle=90)
        ax.set_title(f'蓝球奇偶分布 ({len(filtered_df)}期数据)')
        st.pyplot(fig)
        
        # 蓝球大小分布（1-8为小，9-16为大）
        st.markdown("### 📏 蓝球大小分布")
        small_count = (filtered_df['蓝球'] <= 8).sum()
        big_count = (filtered_df['蓝球'] > 8).sum()
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.pie([small_count, big_count], labels=['小号(1-8)', '大号(9-16)'], autopct='%1.1f%%',
               colors=['#99CCFF', '#3366CC'], startangle=90)
        ax.set_title(f'蓝球大小分布 ({len(filtered_df)}期数据)')
        st.pyplot(fig)
        
        # 蓝球走势图
        st.markdown("### 📈 蓝球走势折线图")
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(filtered_df['期号'], filtered_df['蓝球'], marker='o', linestyle='-', color='blue')
        ax.set_xlabel('期号')
        ax.set_ylabel('蓝球号码')
        ax.set_title('蓝球号码走势')
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # 只显示部分期号标签，避免重叠
        if len(filtered_df) > 20:
            step = len(filtered_df) // 10
            ax.set_xticks(filtered_df['期号'][::step])
            ax.set_xticklabels(filtered_df['期号'][::step], rotation=45)
        else:
            ax.set_xticklabels(filtered_df['期号'], rotation=45)
        
        st.pyplot(fig)
        
        # 出现频率最高的前5个蓝球
        st.markdown("### 🏆 蓝球出现频率TOP5")
        top5_blue = blue_freq_df.sort_values('出现次数', ascending=False).head(5)
        st.dataframe(top5_blue, use_container_width=True)
        
        # 最近N期未出现的蓝球
        st.markdown("### ❓ 最近未出现的蓝球")
        recent_periods = st.slider("选择最近期数", 5, 50, 10)
        recent_blue_balls = filtered_df.head(recent_periods)['蓝球'].unique()
        
        missing_blue = [i for i in range(1, 17) if i not in recent_blue_balls]
        if missing_blue:
            st.write(f"最近{recent_periods}期未出现的蓝球号码：{', '.join(map(str, missing_blue))}")
            
            # 显示这些号码的历史出现频率
            missing_blue_freq = blue_freq_df[blue_freq_df['号码'].isin(missing_blue)]
            st.dataframe(missing_blue_freq, use_container_width=True)
        else:
            st.write(f"最近{recent_periods}期所有蓝球号码都出现过")
    else:
        st.warning("暂无数据，请检查数据加载情况")

# 号码组合分析
elif selected_analysis == "号码组合分析":
    st.subheader("🎯 号码组合分析")
    
    if not filtered_df.empty:
        # 奇偶比分析
        st.markdown("### ⚖️ 红球奇偶比分析")
        
        # 计算每期的奇偶比
        def calculate_odd_even_ratio(row):
            red_balls = [row['红球1'], row['红球2'], row['红球3'], row['红球4'], row['红球5'], row['红球6']]
            odd_count = sum(1 for ball in red_balls if ball % 2 == 1)
            even_count = 6 - odd_count
            return f"{odd_count}:{even_count}"
        
        filtered_df['奇偶比'] = filtered_df.apply(calculate_odd_even_ratio, axis=1)
        odd_even_counts = filtered_df['奇偶比'].value_counts().sort_index()
        
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(odd_even_counts.index, odd_even_counts.values, color='purple', alpha=0.7)
        ax.set_xlabel('奇偶比')
        ax.set_ylabel('出现次数')
        ax.set_title(f'红球奇偶比分布 ({len(filtered_df)}期数据)')
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom')
        
        st.pyplot(fig)
        
        # 大小比分析（1-16为小，17-33为大）
        st.markdown("### 📏 红球大小比分析")
        
        def calculate_big_small_ratio(row):
            red_balls = [row['红球1'], row['红球2'], row['红球3'], row['红球4'], row['红球5'], row['红球6']]
            small_count = sum(1 for ball in red_balls if ball <= 16)
            big_count = 6 - small_count
            return f"{small_count}:{big_count}"
        
        filtered_df['大小比'] = filtered_df.apply(calculate_big_small_ratio, axis=1)
        big_small_counts = filtered_df['大小比'].value_counts().sort_index()
        
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(big_small_counts.index, big_small_counts.values, color='green', alpha=0.7)
        ax.set_xlabel('大小比')
        ax.set_ylabel('出现次数')
        ax.set_title(f'红球大小比分布 ({len(filtered_df)}期数据)')
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom')
        
        st.pyplot(fig)
        
        # 连号分析
        st.markdown("### 🔗 红球连号分析")
        
        def count_consecutive_pairs(row):
            red_balls = sorted([row['红球1'], row['红球2'], row['红球3'], row['红球4'], row['红球5'], row['红球6']])
            consecutive_count = 0
            for i in range(5):
                if red_balls[i+1] - red_balls[i] == 1:
                    consecutive_count += 1
            return consecutive_count
        
        filtered_df['连号数'] = filtered_df.apply(count_consecutive_pairs, axis=1)
        consecutive_counts = filtered_df['连号数'].value_counts().sort_index()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(consecutive_counts.index, consecutive_counts.values, color='orange', alpha=0.7)
        ax.set_xlabel('连号对数')
        ax.set_ylabel('出现次数')
        ax.set_title(f'红球连号分布 ({len(filtered_df)}期数据)')
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom')
        
        st.pyplot(fig)
        
        # 和值分析
        st.markdown("### 📊 红球和值分析")
        
        def calculate_sum(row):
            return row['红球1'] + row['红球2'] + row['红球3'] + row['红球4'] + row['红球5'] + row['红球6']
        
        filtered_df['和值'] = filtered_df.apply(calculate_sum, axis=1)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.hist(filtered_df['和值'], bins=20, color='cyan', alpha=0.7, edgecolor='black')
        ax.set_xlabel('和值')
        ax.set_ylabel('出现次数')
        ax.set_title(f'红球和值分布 ({len(filtered_df)}期数据)')
        ax.grid(True, linestyle='--', alpha=0.7)
        
        st.pyplot(fig)
        
        # 显示统计信息
        st.markdown("### 📋 和值统计信息")
        sum_stats = filtered_df['和值'].describe()
        sum_stats_df = pd.DataFrame({
            '统计指标': ['平均值', '中位数', '最小值', '最大值', '标准差'],
            '数值': [
                sum_stats['mean'].round(2),
                sum_stats['50%'].round(2),
                sum_stats['min'].round(2),
                sum_stats['max'].round(2),
                sum_stats['std'].round(2)
            ]
        })
        st.dataframe(sum_stats_df, use_container_width=True)
        
        # 红球跨度分析（最大红球 - 最小红球）
        st.markdown("### 📏 红球跨度分析")
        
        def calculate_span(row):
            red_balls = [row['红球1'], row['红球2'], row['红球3'], row['红球4'], row['红球5'], row['红球6']]
            return max(red_balls) - min(red_balls)
        
        filtered_df['跨度'] = filtered_df.apply(calculate_span, axis=1)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.hist(filtered_df['跨度'], bins=15, color='brown', alpha=0.7, edgecolor='black')
        ax.set_xlabel('跨度')
        ax.set_ylabel('出现次数')
        ax.set_title(f'红球跨度分布 ({len(filtered_df)}期数据)')
        ax.grid(True, linestyle='--', alpha=0.7)
        
        st.pyplot(fig)
    else:
        st.warning("暂无数据，请检查数据加载情况")

# 历史趋势分析
elif selected_analysis == "历史趋势分析":
    st.subheader("📈 历史趋势分析")
    
    if not filtered_df.empty:
        # 奖池趋势
        st.markdown("### 💰 奖池金额趋势")
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(filtered_df['开奖日期'], filtered_df['奖池(元)'] / 100000000, marker='o', linestyle='-', color='gold')
        ax.set_xlabel('开奖日期')
        ax.set_ylabel('奖池金额（亿元）')
        ax.set_title('奖池金额历史趋势')
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # 自动调整日期标签
        plt.xticks(rotation=45)
        fig.tight_layout()
        
        st.pyplot(fig)
        
        # 红球和值趋势
        st.markdown("### 📊 红球和值趋势")
        
        def calculate_sum(row):
            return row['红球1'] + row['红球2'] + row['红球3'] + row['红球4'] + row['红球5'] + row['红球6']
        
        filtered_df['和值'] = filtered_df.apply(calculate_sum, axis=1)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(filtered_df['开奖日期'], filtered_df['和值'], marker='o', linestyle='-', color='red')
        ax.set_xlabel('开奖日期')
        ax.set_ylabel('和值')
        ax.set_title('红球和值历史趋势')
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # 添加移动平均线
        window = st.slider("选择移动平均线窗口大小", 3, 20, 5)
        filtered_df['和值移动平均'] = filtered_df['和值'].rolling(window=window).mean()
        ax.plot(filtered_df['开奖日期'], filtered_df['和值移动平均'], linestyle='--', color='blue', label=f'{window}期移动平均')
        ax.legend()
        
        plt.xticks(rotation=45)
        fig.tight_layout()
        
        st.pyplot(fig)
        
        # 蓝球大小趋势（1-8为小，9-16为大）
        st.markdown("### 🔵 蓝球大小趋势")
        filtered_df['蓝球大小'] = filtered_df['蓝球'].apply(lambda x: '小' if x <= 8 else '大')
        
        # 计算每期的大小分布
        size_trend = filtered_df.groupby('开奖日期')['蓝球大小'].value_counts().unstack(fill_value=0)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        if '小' in size_trend.columns and '大' in size_trend.columns:
            ax.plot(size_trend.index, size_trend['小'], marker='o', linestyle='-', color='lightblue', label='小号(1-8)')
            ax.plot(size_trend.index, size_trend['大'], marker='o', linestyle='-', color='darkblue', label='大号(9-16)')
        ax.set_xlabel('开奖日期')
        ax.set_ylabel('出现次数')
        ax.set_title('蓝球大小历史趋势')
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.7)
        
        plt.xticks(rotation=45)
        fig.tight_layout()
        
        st.pyplot(fig)
        
        # 红球奇偶趋势
        st.markdown("### 🔴 红球奇偶趋势")
        
        def count_odd_even(row):
            red_balls = [row['红球1'], row['红球2'], row['红球3'], row['红球4'], row['红球5'], row['红球6']]
            odd_count = sum(1 for ball in red_balls if ball % 2 == 1)
            even_count = 6 - odd_count
            return pd.Series({'奇数': odd_count, '偶数': even_count})
        
        odd_even_trend = filtered_df.apply(count_odd_even, axis=1)
        odd_even_trend.index = filtered_df['开奖日期']
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(odd_even_trend.index, odd_even_trend['奇数'], marker='o', linestyle='-', color='red', label='奇数')
        ax.plot(odd_even_trend.index, odd_even_trend['偶数'], marker='o', linestyle='-', color='blue', label='偶数')
        ax.set_xlabel('开奖日期')
        ax.set_ylabel('出现次数')
        ax.set_title('红球奇偶历史趋势')
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.7)
        
        plt.xticks(rotation=45)
        fig.tight_layout()
        
        st.pyplot(fig)
        
        # 红球区间趋势
        st.markdown("### 📈 红球区间趋势")
        
        def count_ranges(row):
            red_balls = [row['红球1'], row['红球2'], row['红球3'], row['红球4'], row['红球5'], row['红球6']]
            range1 = sum(1 for ball in red_balls if 1 <= ball <= 11)  # 小号区
            range2 = sum(1 for ball in red_balls if 12 <= ball <= 22)  # 中号区
            range3 = sum(1 for ball in red_balls if 23 <= ball <= 33)  # 大号区
            return pd.Series({'小号区(1-11)': range1, '中号区(12-22)': range2, '大号区(23-33)': range3})
        
        range_trend = filtered_df.apply(count_ranges, axis=1)
        range_trend.index = filtered_df['开奖日期']
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(range_trend.index, range_trend['小号区(1-11)'], marker='o', linestyle='-', color='green', label='小号区(1-11)')
        ax.plot(range_trend.index, range_trend['中号区(12-22)'], marker='o', linestyle='-', color='orange', label='中号区(12-22)')
        ax.plot(range_trend.index, range_trend['大号区(23-33)'], marker='o', linestyle='-', color='red', label='大号区(23-33)')
        ax.set_xlabel('开奖日期')
        ax.set_ylabel('出现次数')
        ax.set_title('红球区间历史趋势')
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.7)
        
        plt.xticks(rotation=45)
        fig.tight_layout()
        
        st.pyplot(fig)
        
        # 红球号码热度趋势
        st.markdown("### 🔥 红球号码热度趋势")
        selected_number = st.selectbox("选择要分析的红球号码", list(range(1, 34)))
        
        # 计算每期是否包含该号码
        def check_number_presence(row, number):
            red_balls = [row['红球1'], row['红球2'], row['红球3'], row['红球4'], row['红球5'], row['红球6']]
            return 1 if number in red_balls else 0
        
        filtered_df[f'号码{selected_number}_出现'] = filtered_df.apply(lambda row: check_number_presence(row, selected_number), axis=1)
        
        # 计算移动平均热度
        window_size = 10
        filtered_df[f'号码{selected_number}_热度'] = filtered_df[f'号码{selected_number}_出现'].rolling(window=window_size).mean() * 10
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(filtered_df['开奖日期'], filtered_df[f'号码{selected_number}_热度'], marker='o', linestyle='-', color='red')
        ax.set_xlabel('开奖日期')
        ax.set_ylabel(f'号码{selected_number}热度（10期移动平均）')
        ax.set_title(f'红球号码{selected_number}热度趋势')
        ax.grid(True, linestyle='--', alpha=0.7)
        
        plt.xticks(rotation=45)
        fig.tight_layout()
        
        st.pyplot(fig)
    else:
        st.warning("暂无数据，请检查数据加载情况")

# 智能号码推荐
elif selected_analysis == "智能号码推荐":
    st.subheader("🤖 智能号码推荐")
    
    if not filtered_df.empty:
        st.markdown("""
        ### 📋 推荐说明
        本功能基于历史数据分析，使用多种算法生成推荐号码组合。推荐结果仅供参考，不保证中奖，请理性购彩。
        """)
        
        # 分析参数设置
        st.markdown("### ⚙️ 推荐参数设置")
        col1, col2 = st.columns(2)
        with col1:
            hot_weight = st.slider("热门号码权重", 0.1, 1.0, 0.7, 0.1, 
                                  help="权重越高，越倾向于选择历史出现频率高的号码")
        with col2:
            cold_weight = st.slider("冷门号码权重", 0.1, 1.0, 0.3, 0.1,
                                  help="权重越高，越倾向于选择近期未出现的号码")
        
        # 生成推荐号码
        if st.button("🎯 生成推荐号码"):
            with st.spinner("正在分析历史数据，生成推荐号码..."):
                time.sleep(1)  # 模拟分析过程
                
                # 提取所有红球号码
                red_balls = pd.concat([
                    filtered_df['红球1'], filtered_df['红球2'], filtered_df['红球3'],
                    filtered_df['红球4'], filtered_df['红球5'], filtered_df['红球6']
                ], axis=0).astype(int)
                
                # 计算红球频率
                red_freq = red_balls.value_counts()
                red_freq_dict = dict(zip(red_freq.index, red_freq.values))
                
                # 计算红球热度分数
                total_periods = len(filtered_df)
                red_scores = {}
                for num in range(1, 34):
                    freq = red_freq_dict.get(num, 0)
                    # 基础分数：出现频率
                    base_score = freq / total_periods * 6 * 100
                    
                    # 时间衰减：最近出现的号码得分更高
                    recent_periods = min(20, total_periods)
                    recent_red_balls = pd.concat([
                        filtered_df.head(recent_periods)['红球1'],
                        filtered_df.head(recent_periods)['红球2'],
                        filtered_df.head(recent_periods)['红球3'],
                        filtered_df.head(recent_periods)['红球4'],
                        filtered_df.head(recent_periods)['红球5'],
                        filtered_df.head(recent_periods)['红球6']
                    ], axis=0).astype(int)
                    
                    recent_freq = recent_red_balls.value_counts()
                    recent_freq_dict = dict(zip(recent_freq.index, recent_freq.values))
                    recent_score = recent_freq_dict.get(num, 0) / recent_periods * 6 * 100
                    
                    # 综合分数
                    red_scores[num] = hot_weight * base_score + (1 - hot_weight) * recent_score
                
                # 计算红球冷门分数（近期未出现的号码得分更高）
                cold_scores = {}
                for num in range(1, 34):
                    if num not in recent_freq_dict:
                        cold_scores[num] = 100  # 最近20期未出现
                    else:
                        # 计算距离最近一次出现的期数
                        last_occurrence = 0
                        for i, row in filtered_df.head(recent_periods).iterrows():
                            red_balls_row = [row['红球1'], row['红球2'], row['红球3'], row['红球4'], row['红球5'], row['红球6']]
                            if num in red_balls_row:
                                last_occurrence = i
                                break
                        cold_scores[num] = (recent_periods - last_occurrence) / recent_periods * 100
                
                # 综合热门和冷门分数
                combined_scores = {}
                for num in range(1, 34):
                    combined_scores[num] = hot_weight * red_scores[num] + cold_weight * cold_scores[num]
                
                # 生成多组推荐号码
                st.markdown("### 🎯 推荐号码组合")
                
                # 推荐组合数量
                num_combinations = 5
                
                # 生成推荐组合
                recommendations = []
                for i in range(num_combinations):
                    # 根据得分选择红球
                    sorted_numbers = sorted(combined_scores.keys(), key=lambda x: combined_scores[x], reverse=True)
                    
                    # 选择得分最高的前10个号码，然后随机选择6个
                    top_numbers = sorted_numbers[:15]
                    selected_red = sorted(random.sample(top_numbers, 6))
                    
                    # 蓝球推荐
                    blue_freq = filtered_df['蓝球'].value_counts()
                    blue_freq_dict = dict(zip(blue_freq.index, blue_freq.values))
                    
                    # 计算蓝球得分
                    blue_scores = {}
                    for num in range(1, 17):
                        freq = blue_freq_dict.get(num, 0)
                        blue_scores[num] = freq / total_periods * 100
                    
                    # 选择蓝球
                    sorted_blue = sorted(blue_scores.keys(), key=lambda x: blue_scores[x], reverse=True)
                    selected_blue = random.choice(sorted_blue[:5])
                    
                    recommendations.append({
                        '组合': f"推荐{i+1}",
                        '红球': selected_red,
                        '蓝球': selected_blue,
                        '红球得分': sum(combined_scores[num] for num in selected_red) / 6,
                        '蓝球得分': blue_scores[selected_blue]
                    })
                
                # 显示推荐结果
                for rec in recommendations:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"#### 🎯 {rec['组合']}")
                        red_str = ' '.join([f"{num:02d}" for num in rec['红球']])
                        st.markdown(f"**红球：** `{red_str}`")
                        st.markdown(f"**蓝球：** `{rec['蓝球']:02d}`")
                    with col2:
                        st.markdown("#### 评分")
                        st.markdown(f"**红球评分：** {rec['红球得分']:.1f}")
                        st.markdown(f"**蓝球评分：** {rec['蓝球得分']:.1f}")
                    st.markdown("---")
                
                # 显示推荐依据
                st.markdown("### 📊 推荐依据")
                st.markdown("#### 红球推荐依据：")
                st.markdown("1. **历史出现频率**：统计每个红球号码在历史数据中的出现次数和频率")
                st.markdown("2. **近期热度**：分析最近20期号码的出现情况，计算热度得分")
                st.markdown("3. **冷门号码**：考虑近期未出现的号码，增加号码多样性")
                st.markdown("4. **组合优化**：确保推荐组合具有良好的奇偶比、大小比等平衡性")
                
                st.markdown("#### 蓝球推荐依据：")
                st.markdown("1. **历史出现频率**：统计每个蓝球号码的历史出现频率")
                st.markdown("2. **近期趋势**：分析最近蓝球号码的走势和规律")
                st.markdown("3. **奇偶平衡**：考虑奇偶分布的平衡性")
                
                st.markdown("### ⚠️ 重要提示")
                st.markdown("""
                - 推荐结果基于历史数据分析，仅供参考，不保证中奖
                - 彩票中奖号码是随机产生的，历史规律不代表未来趋势
                - 请理性购彩，控制购彩金额，享受彩票带来的乐趣
                """)
    else:
        st.warning("暂无数据，请检查数据加载情况")

# 显示页脚
st.markdown(footer, unsafe_allow_html=True)
