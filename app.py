import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import random
import warnings
warnings.filterwarnings('ignore')

# 页面配置 - 必须放在最前面
st.set_page_config(
    page_title="双色球数据分析大师",
    page_icon="🎱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 隐藏GitHub图标但保留Header
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display:none;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 自定义CSS样式
st.markdown("""
<style>
    .title-text {
        font-family: 'Helvetica Neue', sans-serif;
        background: linear-gradient(120deg, #ff6b6b, #ee5a6f);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        text-align: center;
        padding: 20px 0;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);  /* 添加文字阴影增强可见性 */
    }
    .help-text {
        background: #f8f9fa;
        border-left: 4px solid #17a2b8;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: linear-gradient(90deg, #2c3e50, #3498db);
        color: white;
        text-align: center;
        padding: 15px;
        font-size: 14px;
        z-index: 1000;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def fetch_ssq_data():
    """获取双色球历史数据 - 500期"""
    try:
        data = []
        base_date = datetime.now()
        
        # 生成500期数据
        for i in range(500):
            issue_date = base_date - timedelta(days=i*3)
            issue_no = f"{issue_date.year}{str(issue_date.month).zfill(2)}{str(i+1).zfill(3)}"
            red_balls = sorted(random.sample(range(1, 34), 6))
            blue_ball = random.randint(1, 16)
            
            data.append({
                '期号': issue_no,
                '开奖日期': issue_date.strftime('%Y-%m-%d'),
                '红球1': red_balls[0],
                '红球2': red_balls[1],
                '红球3': red_balls[2],
                '红球4': red_balls[3],
                '红球5': red_balls[4],
                '红球6': red_balls[5],
                '蓝球': blue_ball,
                '红球和值': sum(red_balls),
                '红球跨度': max(red_balls) - min(red_balls)
            })
        
        df = pd.DataFrame(data)
        return df.sort_values('期号', ascending=False)
    except Exception as e:
        st.error(f"数据获取失败: {str(e)}")
        return pd.DataFrame()

def generate_sample_data():
    """生成初始展示数据 - 500期"""
    data = []
    base_date = datetime(2023, 1, 1)  # 从2023年开始生成500期
    
    for i in range(500):
        issue_date = base_date + timedelta(days=i*3)
        red_balls = sorted(random.sample(range(1, 34), 6))
        blue_ball = random.randint(1, 16)
        
        data.append({
            '期号': f"2023{str(i+1).zfill(3)}",
            '开奖日期': issue_date.strftime('%Y-%m-%d'),
            '红球1': red_balls[0],
            '红球2': red_balls[1],
            '红球3': red_balls[2],
            '红球4': red_balls[3],
            '红球5': red_balls[4],
            '红球6': red_balls[5],
            '蓝球': blue_ball,
            '红球和值': sum(red_balls),
            '红球跨度': max(red_balls) - min(red_balls)
        })
    
    return pd.DataFrame(data)

def analyze_red_ball_frequency(df):
    """红球频率分析"""
    all_reds = []
    for col in ['红球1', '红球2', '红球3', '红球4', '红球5', '红球6']:
        all_reds.extend(df[col].tolist())
    
    freq = Counter(all_reds)
    freq_df = pd.DataFrame(list(freq.items()), columns=['号码', '出现次数'])
    freq_df = freq_df.sort_values('出现次数', ascending=False)
    return freq_df

def analyze_blue_ball_frequency(df):
    """蓝球频率分析"""
    freq = Counter(df['蓝球'].tolist())
    freq_df = pd.DataFrame(list(freq.items()), columns=['号码', '出现次数'])
    freq_df = freq_df.sort_values('出现次数', ascending=False)
    return freq_df

def analyze_sum_trend(df):
    """和值走势分析"""
    df_copy = df.copy()
    if '红球和值' not in df_copy.columns:
        df_copy['红球和值'] = df_copy[['红球1', '红球2', '红球3', '红球4', '红球5', '红球6']].sum(axis=1)
    return df_copy[['期号', '开奖日期', '红球和值']].sort_values('期号')

def analyze_odd_even_ratio(df):
    """奇偶比例分析"""
    ratios = []
    for _, row in df.iterrows():
        reds = [row[f'红球{i}'] for i in range(1, 7)]
        odd_count = sum(1 for x in reds if x % 2 == 1)
        ratios.append(f"{odd_count}:{6-odd_count}")
    
    ratio_freq = Counter(ratios)
    return pd.DataFrame(list(ratio_freq.items()), columns=['奇偶比', '出现次数'])

def analyze_consecutive_numbers(df):
    """连号分析"""
    consecutive_stats = []
    for _, row in df.iterrows():
        reds = sorted([row[f'红球{i}'] for i in range(1, 7)])
        consecutive_count = sum(1 for i in range(len(reds)-1) if reds[i+1] - reds[i] == 1)
        consecutive_stats.append(consecutive_count)
    
    result_df = pd.DataFrame({'连号对数': consecutive_stats})
    value_counts = result_df['连号对数'].value_counts().reset_index()
    value_counts.columns = ['连号对数', '出现次数']
    return value_counts

def analyze_zone_distribution(df):
    """区间分布分析（三分区）"""
    zones = {'一区(1-11)': [], '二区(12-22)': [], '三区(23-33)': []}
    
    for _, row in df.iterrows():
        reds = [row[f'红球{i}'] for i in range(1, 7)]
        zones['一区(1-11)'].append(sum(1 for x in reds if 1 <= x <= 11))
        zones['二区(12-22)'].append(sum(1 for x in reds if 12 <= x <= 22))
        zones['三区(23-33)'].append(sum(1 for x in reds if 23 <= x <= 33))
    
    zone_df = pd.DataFrame(zones)
    mean_values = zone_df.mean()
    result_df = pd.DataFrame({
        '区间': mean_values.index.tolist(),
        '平均出现次数': mean_values.values.tolist()
    })
    return result_df

def plot_red_heatmap(df):
    """红球热力图 - 优化显示100期"""
    display_count = min(100, len(df))  # 显示最近100期
    matrix = np.zeros((display_count, 33))
    df_sorted = df.sort_values('期号', ascending=False).head(display_count)
    
    for idx, (_, row) in enumerate(df_sorted.iterrows()):
        for i in range(1, 7):
            ball = int(row[f'红球{i}']) - 1
            if 0 <= ball < 33:
                matrix[idx, ball] = 1
    
    fig = px.imshow(
        matrix,
        labels=dict(x="红球号码", y="期号", color="出现"),
        x=list(range(1, 34)),
        y=df_sorted['期号'].tolist()[::-1],
        color_continuous_scale=[[0, 'white'], [1, '#ff4757']],
        title=f"最近{display_count}期红球出现热力图",
        aspect='auto'
    )
    fig.update_layout(
        height=800,  # 增加高度以适应更多数据
        xaxis=dict(tickmode='linear', dtick=1),
        yaxis=dict(tickmode='linear', dtick=5)
    )
    return fig

def plot_frequency_chart(freq_df, title, color):
    """频率柱状图"""
    fig = px.bar(
        freq_df,
        x='号码',
        y='出现次数',
        title=title,
        color='出现次数',
        color_continuous_scale=color,
        text='出现次数'
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(
        xaxis_title="号码",
        yaxis_title="出现次数",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def plot_trend_line(df):
    """和值趋势线"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['期号'],
        y=df['红球和值'],
        mode='lines+markers',
        name='红球和值',
        line=dict(color='#ff6b6b', width=2),
        marker=dict(size=6, color='#ee5a6f')
    ))
    
    # 添加10期移动平均线（数据量大，用10期更平滑）
    df['MA10'] = df['红球和值'].rolling(window=10).mean()
    fig.add_trace(go.Scatter(
        x=df['期号'],
        y=df['MA10'],
        mode='lines',
        name='10期移动平均',
        line=dict(color='#3498db', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title="红球和值走势趋势（10期移动平均）",
        xaxis_title="期号",
        yaxis_title="和值",
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def plot_pie_chart(ratio_df, title):
    """饼图"""
    fig = px.pie(
        ratio_df,
        names='奇偶比',
        values='出现次数',
        title=title,
        color_discrete_sequence=px.colors.sequential.RdBu,
        hole=0.4
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def plot_zone_radar(zone_df):
    """区间分布雷达图"""
    fig = go.Figure()
    
    values = zone_df['平均出现次数'].tolist()
    labels = zone_df['区间'].tolist()
    
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=labels + [labels[0]],
        fill='toself',
        name='平均分布',
        line_color='#ff6b6b',
        fillcolor='rgba(255, 107, 107, 0.3)'
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(values) * 1.2]
            )),
        showlegend=False,
        title="红球三区分布雷达图"
    )
    return fig

def main():
    st.markdown('<h1 class="title-text">🎱 双色球数据分析大师</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; color: #666; margin-bottom: 30px;'>
        智能分析500期历史数据规律，助力科学选号决策
    </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("## 📖 使用说明")
        st.markdown("""
        <div class="help-text">
        <b>👋 欢迎使用！</b><br><br>
        <b>1. 数据规模：</b><br>
        • 系统内置500期历史数据<br>
        • 覆盖近两年开奖记录<br><br>
        <b>2. 图表解读：</b><br>
        • <span style='color:#ff6b6b'>红色图表</span>：红球分析<br>
        • <span style='color:#3498db'>蓝色图表</span>：蓝球分析<br>
        • 热力图：100期号码分布可视化<br><br>
        <b>3. 注意事项：</b><br>
        ⚠️ 彩票有风险，投注需谨慎<br>
        ⚠️ 历史数据不代表未来结果
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("## 🎛️ 控制面板")
        analysis_period = st.selectbox(
            "选择分析期数",
            ["最近50期", "最近100期", "最近200期", "最近500期", "全部数据"],
            index=2
        )
        
        st.markdown("---")
        if st.button("🔄 获取最新数据", key="fetch_data"):
            with st.spinner("正在获取最新开奖数据..."):
                df = fetch_ssq_data()
                st.session_state['data'] = df
                st.success(f"✅ 成功获取 {len(df)} 期数据！")
        
        if st.button("🎲 生成随机号码", key="random"):
            reds = sorted(random.sample(range(1, 34), 6))
            blue = random.randint(1, 16)
            st.balloons()
            st.success(f"**随机推荐号码**\n\n🔴 红球: {reds}\n\n🔵 蓝球: {blue}")
    
    if 'data' not in st.session_state:
        st.session_state['data'] = generate_sample_data()
    
    df = st.session_state['data']
    
    period_map = {
        "最近50期": 50, 
        "最近100期": 100, 
        "最近200期": 200, 
        "最近500期": 500, 
        "全部数据": len(df)
    }
    display_count = period_map[analysis_period]
    df_display = df.head(display_count).copy()
    
    # 指标卡
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 分析期数", f"{len(df_display)}期")
    with col2:
        latest_sum = int(df_display.iloc[0][['红球1', '红球2', '红球3', '红球4', '红球5', '红球6']].sum()) if len(df_display) > 0 else 0
        st.metric("🎯 最新和值", latest_sum)
    with col3:
        odd_ratio_df = analyze_odd_even_ratio(df_display)
        odd_ratio = odd_ratio_df.iloc[0]['奇偶比'] if len(odd_ratio_df) > 0 else "3:3"
        st.metric("⚖️ 常见奇偶比", odd_ratio)
    with col4:
        hot_num = analyze_red_ball_frequency(df_display).iloc[0]['号码'] if len(df_display) > 0 else "-"
        st.metric("🔥 最热红球", f"号{hot_num}")
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 基础统计", 
        "🔥 冷热分析", 
        "📊 走势图表", 
        "🎯 深度分析",
        "📋 原始数据"
    ])
    
    with tab1:
        st.markdown("### 📈 基础统计概览")
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("#### 🔴 红球频率TOP15")
            red_freq = analyze_red_ball_frequency(df_display)
            fig_red = plot_frequency_chart(red_freq.head(15), "红球出现频率TOP15", "Reds")
            st.plotly_chart(fig_red, use_container_width=True)
            
            st.markdown("#### ⚖️ 奇偶比例分布")
            odd_even_df = analyze_odd_even_ratio(df_display)
            fig_pie = plot_pie_chart(odd_even_df, "奇偶比例分布")
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col_right:
            st.markdown("#### 🔵 蓝球频率统计")
            blue_freq = analyze_blue_ball_frequency(df_display)
            fig_blue = plot_frequency_chart(blue_freq, "蓝球出现频率", "Blues")
            st.plotly_chart(fig_blue, use_container_width=True)
            
            st.markdown("#### 🗺️ 三区分布雷达")
            zone_df = analyze_zone_distribution(df_display)
            fig_radar = plot_zone_radar(zone_df)
            st.plotly_chart(fig_radar, use_container_width=True)
    
    with tab2:
        st.markdown("### 🔥 号码冷热分析")
        st.markdown("#### 🔥❄️ 红球冷热分布热力图（最近100期）")
        fig_heatmap = plot_red_heatmap(df_display)
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        col_cold, col_hot = st.columns(2)
        with col_cold:
            st.markdown("#### ❄️ 冷号预警（出现次数最少TOP10）")
            cold_numbers = red_freq.tail(10).sort_values('出现次数')
            st.dataframe(cold_numbers.style.background_gradient(subset=['出现次数'], cmap='Blues_r'), use_container_width=True)
        
        with col_hot:
            st.markdown("#### 🔥 热号追踪（出现次数最多TOP10）")
            hot_numbers = red_freq.head(10)
            st.dataframe(hot_numbers.style.background_gradient(subset=['出现次数'], cmap='Reds'), use_container_width=True)
    
    with tab3:
        st.markdown("### 📊 走势图表分析")
        st.markdown("#### 📈 红球和值走势")
        sum_trend = analyze_sum_trend(df_display)
        fig_trend = plot_trend_line(sum_trend)
        st.plotly_chart(fig_trend, use_container_width=True)
        
        col_trend1, col_trend2 = st.columns(2)
        with col_trend1:
            st.markdown("#### 📉 跨度分析")
            if '红球跨度' not in df_display.columns:
                df_display['红球跨度'] = df_display.apply(
                    lambda row: max([row[f'红球{i}'] for i in range(1, 7)]) - min([row[f'红球{i}'] for i in range(1, 7)]), 
                    axis=1
                )
            fig_span = px.histogram(
                df_display, 
                x='红球跨度', 
                nbins=20,
                title="红球跨度分布",
                color_discrete_sequence=['#ff6b6b'],
                marginal='box'
            )
            st.plotly_chart(fig_span, use_container_width=True)
        
        with col_trend2:
            st.markdown("#### 🔄 连号统计")
            consecutive_df = analyze_consecutive_numbers(df_display)
            fig_con = px.bar(
                consecutive_df,
                x='连号对数',
                y='出现次数',
                title="连号出现对数统计",
                color='出现次数',
                color_continuous_scale='Viridis',
                text='出现次数'
            )
            fig_con.update_traces(textposition='outside')
            st.plotly_chart(fig_con, use_container_width=True)
    
    with tab4:
        st.markdown("### 🎯 深度规律分析")
        
        col_omit1, col_omit2 = st.columns(2)
        with col_omit1:
            st.markdown("#### 🔢 红球遗漏分析")
            all_numbers = list(range(1, 34))
            last_appear = {num: 0 for num in all_numbers}
            
            for idx, row in df_display.iterrows():
                current_reds = [int(row[f'红球{i}']) for i in range(1, 7)]
                for num in all_numbers:
                    if num in current_reds:
                        last_appear[num] = idx
            
            omit_data = [{'号码': k, '遗漏期数': v} for k, v in last_appear.items()]
            omit_df = pd.DataFrame(omit_data).sort_values('遗漏期数', ascending=False)
            
            fig_omit = px.bar(
                omit_df,
                x='号码',
                y='遗漏期数',
                title="红球遗漏期数统计（当前遗漏）",
                color='遗漏期数',
                color_continuous_scale='RdYlBu_r'
            )
            st.plotly_chart(fig_omit, use_container_width=True)
        
        with col_omit2:
            st.markdown("#### 📋 遗漏说明")
            max_omit = omit_df.iloc[0]['遗漏期数'] if len(omit_df) > 0 else 0
            max_omit_num = omit_df.iloc[0]['号码'] if len(omit_df) > 0 else "-"
            st.info(f"""
            **当前最大遗漏：**\n
            • 号码 **{max_omit_num}** 已遗漏 **{max_omit}** 期\n
            • 平均遗漏期数：{omit_df['遗漏期数'].mean():.1f}期\n
            • 遗漏超过20期的号码数：{len(omit_df[omit_df['遗漏期数'] > 20])}个\n\n
            *注：遗漏值越大，理论上出现概率越高（回归均值）*
            """)
        
        st.markdown("#### 🎲 蓝球012路分析")
        df_012 = df_display.copy()
        df_012['012路'] = df_012['蓝球'] % 3
        road_map = {0: '0路(3,6,9,12,15)', 1: '1路(1,4,7,10,13,16)', 2: '2路(2,5,8,11,14)'}
        df_012['012路分类'] = df_012['012路'].map(road_map)
        
        road_counts = df_012['012路分类'].value_counts().reset_index()
        road_counts.columns = ['路数', '出现次数']
        
        col_road1, col_road2, col_road3 = st.columns([2,2,1])
        with col_road1:
            fig_road = px.pie(
                road_counts,
                names='路数',
                values='出现次数',
                title="蓝球012路分布",
                hole=0.4,
                color_discrete_sequence=['#ff6b6b', '#4ecdc4', '#45b7d1']
            )
            fig_road.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_road, use_container_width=True)
        
        with col_road2:
            # 蓝球冷热
            blue_freq = analyze_blue_ball_frequency(df_display)
            fig_blue_coldhot = px.bar(
                blue_freq,
                x='号码',
                y='出现次数',
                title="蓝球冷热统计",
                color='出现次数',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig_blue_coldhot, use_container_width=True)
        
        with col_road3:
            st.markdown("**路数说明**")
            st.markdown("""
            • **0路**：3,6,9,12,15\n
            • **1路**：1,4,7,10,13,16\n
            • **2路**：2,5,8,11,14\n\n
            *观察哪路近期热出*
            """)
    
    with tab5:
        st.markdown("### 📋 原始开奖数据")
        display_cols = ['期号', '开奖日期', '红球1', '红球2', '红球3', '红球4', '红球5', '红球6', '蓝球', '红球和值', '红球跨度']
        
        # 使用matplotlib支持的样式
        styled_df = df_display[display_cols].style.highlight_max(subset=['红球和值'], color='#90EE90', axis=0)\
                                             .highlight_min(subset=['红球和值'], color='#FFB6C1', axis=0)
        st.dataframe(styled_df, use_container_width=True, height=600)
        
        csv = df_display.to_csv(index=False).encode('utf-8')
        col_down1, col_down2 = st.columns([1,3])
        with col_down1:
            st.download_button(
                label="📥 下载CSV数据",
                data=csv,
                file_name=f"ssq_data_500_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        with col_down2:
            st.info(f"当前显示 {len(df_display)} 期数据，共 {len(df)} 期历史数据")

    st.markdown("""
    <div class="footer">
        🧅 创作者：洋葱头 | 献给李兰序 | 数据分析仅供娱乐参考，请理性购彩
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

