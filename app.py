import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import random
import time
import json
import warnings
warnings.filterwarnings('ignore')

# 页面配置
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

.js-plotly-plot {
    touch-action: pan-y !important;
    -webkit-touch-callout: none;
    -webkit-user-select: none;
    user-select: none;
}

.main {
    touch-action: pan-y;
}
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
    }
    .help-text {
        background: #f8f9fa;
        border-left: 4px solid #17a2b8;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .prediction-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        border: 2px solid #fff;
        transition: transform 0.3s;
    }
    .prediction-card:hover {
        transform: translateY(-5px);
    }
    .red-ball {
        display: inline-block;
        background: linear-gradient(135deg, #ff6b6b, #ee5a6f);
        color: white;
        width: 40px;
        height: 40px;
        line-height: 40px;
        border-radius: 50%;
        text-align: center;
        margin: 3px;
        font-weight: bold;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .blue-ball {
        display: inline-block;
        background: linear-gradient(135deg, #3498db, #2980b9);
        color: white;
        width: 40px;
        height: 40px;
        line-height: 40px;
        border-radius: 50%;
        text-align: center;
        margin: 3px;
        font-weight: bold;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .drag-code {
        display: inline-block;
        background: linear-gradient(135deg, #f39c12, #e74c3c);
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        margin: 2px;
        font-weight: bold;
        font-size: 18px;
    }
    .kill-code {
        display: inline-block;
        background: linear-gradient(135deg, #95a5a6, #7f8c8d);
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        margin: 2px;
        font-weight: bold;
        font-size: 18px;
        text-decoration: line-through;
        opacity: 0.7;
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
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #3498db;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def fetch_ssq_data_async():
    """异步获取双色球历史数据 - 500期"""
    data = []
    base_date = datetime.now()
    
    batch_size = 100
    total_batches = 5
    
    for batch in range(total_batches):
        start_idx = batch * batch_size
        end_idx = start_idx + batch_size
        
        for i in range(start_idx, end_idx):
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
        
        time.sleep(0.01)
    
    df = pd.DataFrame(data)
    return df.sort_values('期号', ascending=False)

@st.cache_data(ttl=3600)
def generate_sample_data():
    """生成初始展示数据 - 500期"""
    data = []
    base_date = datetime(2023, 1, 1)
    
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

def analyze_omission(df):
    """分析红球遗漏值"""
    all_numbers = list(range(1, 34))
    last_appear = {num: 0 for num in all_numbers}
    
    for idx, row in df.iterrows():
        current_reds = [int(row[f'红球{i}']) for i in range(1, 7)]
        for num in all_numbers:
            if num in current_reds:
                last_appear[num] = idx
    
    omit_data = [{'号码': k, '遗漏期数': v} for k, v in last_appear.items()]
    return pd.DataFrame(omit_data)

def get_drag_codes(df):
    """
    智能胆码推荐（2个）
    策略：热号前3 + 遗漏适中（10-20期）+ 近期趋势上升
    """
    red_freq = analyze_red_ball_frequency(df)
    omission_df = analyze_omission(df)
    
    # 合并数据
    analysis_df = red_freq.merge(omission_df, on='号码')
    
    # 计算综合得分
    # 频率得分（归一化）
    max_freq = analysis_df['出现次数'].max()
    analysis_df['频率得分'] = analysis_df['出现次数'] / max_freq * 40
    
    # 遗漏得分：遗漏10-20期得分最高，太短或太长都降低
    def calc_omit_score(x):
        if 10 <= x <= 20:
            return 30
        elif 5 <= x < 10 or 20 < x <= 25:
            return 20
        elif x < 5:
            return 10
        else:
            return 25  # 长期遗漏也有反弹可能
    
    analysis_df['遗漏得分'] = analysis_df['遗漏期数'].apply(calc_omit_score)
    
    # 综合得分
    analysis_df['总得分'] = analysis_df['频率得分'] + analysis_df['遗漏得分']
    
    # 选择前2名
    top2 = analysis_df.nlargest(2, '总得分')
    return top2['号码'].tolist()

def get_kill_codes(df):
    """
    智能杀号（5个）
    策略：连续出现2期以上 + 遗漏小于3期 + 历史最大连出后
    """
    # 获取最近几期的热号
    recent_hot = set()
    for i in range(min(3, len(df))):
        row = df.iloc[i]
        recent_hot.update([int(row[f'红球{j}']) for j in range(1, 7)])
    
    # 获取冷号（遗漏小于3期）
    omission_df = analyze_omission(df)
    cold_codes = omission_df[omission_df['遗漏期数'] < 3]['号码'].tolist()
    
    # 获取低频号
    red_freq = analyze_red_ball_frequency(df)
    low_freq = red_freq.tail(10)['号码'].tolist()
    
    # 合并并去重，选择5个
    kill_candidates = list(set(recent_hot) & set(cold_codes)) + low_freq
    kill_codes = kill_candidates[:5] if len(kill_candidates) >= 5 else kill_candidates + random.sample([x for x in range(1,34) if x not in kill_candidates], 5-len(kill_candidates))
    
    return sorted(kill_codes[:5])

def analyze_sum_range(df):
    """和值范围分析"""
    sums = df['红球和值'].tolist()
    return {
        'min': min(sums),
        'max': max(sums),
        'mean': np.mean(sums),
        'median': np.median(sums),
        'q1': np.percentile(sums, 25),
        'q3': np.percentile(sums, 75),
        'recommended_min': int(np.percentile(sums, 20)),  # 推荐范围80%分位数
        'recommended_max': int(np.percentile(sums, 80))
    }

def analyze_zone_distribution(df):
    """区间分布分析"""
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

def check_historical_match(df, red_balls, blue_ball):
    """检查号码组合是否中过奖"""
    for _, row in df.iterrows():
        historical_reds = sorted([int(row[f'红球{i}']) for i in range(1, 7)])
        historical_blue = int(row['蓝球'])
        
        # 检查红球匹配数
        match_red = len(set(red_balls) & set(historical_reds))
        match_blue = (blue_ball == historical_blue)
        
        if match_red >= 4:  # 4红或以上就算中奖
            prize = ""
            if match_red == 6 and match_blue:
                prize = "一等奖！"
            elif match_red == 6:
                prize = "二等奖"
            elif match_red == 5 and match_blue:
                prize = "三等奖"
            elif match_red == 5 or (match_red == 4 and match_blue):
                prize = "四等奖"
            elif match_red == 4 or (match_red == 3 and match_blue):
                prize = "五等奖"
            elif match_blue:
                prize = "六等奖"
            
            if prize:
                return {
                    'matched': True,
                    'issue': row['期号'],
                    'date': row['开奖日期'],
                    'red_match': match_red,
                    'blue_match': match_blue,
                    'prize': prize,
                    'historical_reds': historical_reds,
                    'historical_blue': historical_blue
                }
    
    return {'matched': False}

def analyze_odd_even_ratio(df):
    """奇偶比例分析"""
    ratios = []
    for _, row in df.iterrows():
        reds = [row[f'红球{i}'] for i in range(1, 7)]
        odd_count = sum(1 for x in reds if x % 2 == 1)
        ratios.append(f"{odd_count}:{6-odd_count}")
    
    ratio_freq = Counter(ratios)
    return pd.DataFrame(list(ratio_freq.items()), columns=['奇偶比', '出现次数'])

def generate_smart_numbers(df, strategy_type='balanced', kill_codes=None, drag_codes=None):
    """
    基于历史数据的智能预测算法
    支持胆码和杀号
    """
    red_freq = analyze_red_ball_frequency(df)
    omission_df = analyze_omission(df)
    blue_freq = analyze_blue_ball_frequency(df)
    sum_stats = analyze_sum_range(df)
    
    # 构建红球权重池
    red_weights = {}
    for num in range(1, 34):
        if kill_codes and num in kill_codes:
            red_weights[num] = 0.1  # 杀号权重极低
            continue
            
        weight = 1.0
        
        freq_row = red_freq[red_freq['号码'] == num]
        omit_row = omission_df[omission_df['号码'] == num]
        
        freq = freq_row['出现次数'].values[0] if len(freq_row) > 0 else 0
        omission = omit_row['遗漏期数'].values[0] if len(omit_row) > 0 else 0
        
        if strategy_type == 'hot':
            weight += freq * 0.5
        elif strategy_type == 'cold':
            weight += omission * 0.3
        elif strategy_type == 'balanced':
            weight = (freq * 0.4) + (omission * 0.3) + 10
        elif strategy_type == 'consecutive':
            weight = 10
        else:
            weight = 10 + freq * 0.2 + omission * 0.1
        
        # 胆码加权
        if drag_codes and num in drag_codes:
            weight *= 3
            
        red_weights[num] = max(weight, 0.1)
    
    # 选择红球
    if strategy_type == 'consecutive':
        consecutive_starts = list(range(1, 29))
        selected_consecutive = random.sample(consecutive_starts, 2)
        hot_numbers = []
        for start in selected_consecutive:
            hot_numbers.extend([start, start+1])
        hot_numbers = list(set(hot_numbers))[:4]
        
        remaining = 6 - len(hot_numbers)
        other_numbers = [n for n in range(1, 34) if n not in hot_numbers]
        other_weights = [red_weights[n] for n in other_numbers]
        other_selected = random.choices(other_numbers, weights=other_weights, k=remaining)
        
        red_balls = sorted(hot_numbers + other_selected)
    else:
        numbers = list(range(1, 34))
        weights = [red_weights[n] for n in numbers]
        
        red_balls = []
        temp_numbers = numbers.copy()
        temp_weights = weights.copy()
        
        for _ in range(6):
            selected = random.choices(temp_numbers, weights=temp_weights, k=1)[0]
            red_balls.append(selected)
            idx = temp_numbers.index(selected)
            temp_numbers.pop(idx)
            temp_weights.pop(idx)
        
        red_balls = sorted(red_balls)
    
    # 和值过滤
    current_sum = sum(red_balls)
    recommended_min = sum_stats['recommended_min']
    recommended_max = sum_stats['recommended_max']
    
    # 如果和值不在推荐范围，尝试调整（简单策略：替换最大或最小号）
    attempts = 0
    while (current_sum < recommended_min or current_sum > recommended_max) and attempts < 10:
        if current_sum > recommended_max:
            # 替换最大号为更小的
            max_idx = red_balls.index(max(red_balls))
            candidates = [x for x in range(1, red_balls[max_idx]) if x not in red_balls]
            if candidates:
                new_num = random.choice(candidates)
                red_balls[max_idx] = new_num
                red_balls = sorted(red_balls)
        elif current_sum < recommended_min:
            # 替换最小号为更大的
            min_idx = red_balls.index(min(red_balls))
            candidates = [x for x in range(red_balls[min_idx]+1, 34) if x not in red_balls]
            if candidates:
                new_num = random.choice(candidates)
                red_balls[min_idx] = new_num
                red_balls = sorted(red_balls)
        
        current_sum = sum(red_balls)
        attempts += 1
    
    # 蓝球选择
    blue_weights = {}
    for num in range(1, 17):
        freq_row = blue_freq[blue_freq['号码'] == num]
        freq = freq_row['出现次数'].values[0] if len(freq_row) > 0 else 0
        blue_weights[num] = freq + 5
    
    blue_numbers = list(range(1, 17))
    blue_weights_list = [blue_weights[n] for n in blue_numbers]
    blue_ball = random.choices(blue_numbers, weights=blue_weights_list, k=1)[0]
    
    return red_balls, blue_ball

def generate_5_predictions(df, kill_codes=None, drag_codes=None):
    """生成5组不同策略的预测号码"""
    strategies = [
        ('hot', '🔥 热号追击', '优先选择近期高频出现的号码'),
        ('cold', '❄️ 冷号反弹', '选择长期未出的遗漏号码'),
        ('balanced', '⚖️ 平衡优选', '综合考虑热度和遗漏'),
        ('consecutive', '🔗 连号策略', '倾向选择有连号组合'),
        ('random_weighted', '🎲 加权随机', '基于历史权重的随机')
    ]
    
    predictions = []
    for strategy, name, desc in strategies:
        red, blue = generate_smart_numbers(df, strategy, kill_codes, drag_codes)
        
        # 检查是否中过奖
        match_result = check_historical_match(df, red, blue)
        
        predictions.append({
            'name': name,
            'desc': desc,
            'red': red,
            'blue': blue,
            'sum': sum(red),
            'span': max(red) - min(red),
            'odd_even': f"{sum(1 for x in red if x % 2 == 1)}:{sum(1 for x in red if x % 2 == 0)}",
            'historical_match': match_result
        })
    
    return predictions

def plot_red_heatmap(df):
    """红球热力图"""
    display_count = min(100, len(df))
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
        height=800,
        xaxis=dict(tickmode='linear', dtick=1, fixedrange=True),
        yaxis=dict(tickmode='linear', dtick=5, fixedrange=True),
        dragmode=False,
        selectdirection=None,
        hovermode='closest'
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
        xaxis=dict(fixedrange=True),
        yaxis=dict(fixedrange=True),
        dragmode=False,
        showlegend=False
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
        marker=dict(size=4)
    ))
    
    df['MA10'] = df['红球和值'].rolling(window=10).mean()
    fig.add_trace(go.Scatter(
        x=df['期号'],
        y=df['MA10'],
        mode='lines',
        name='10期移动平均',
        line=dict(color='#3498db', width=2, dash='dash')
    ))
    
    # 添加推荐范围区域
    sum_stats = analyze_sum_range(df)
    fig.add_hrect(
        y0=sum_stats['recommended_min'], 
        y1=sum_stats['recommended_max'],
        fillcolor="green", 
        opacity=0.1,
        line_width=0,
        annotation_text="推荐范围", 
        annotation_position="right"
    )
    
    fig.update_layout(
        title="红球和值走势趋势（绿色区域为推荐范围）",
        xaxis=dict(fixedrange=True),
        yaxis=dict(fixedrange=True),
        dragmode=False,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def plot_pie_chart(ratio_df, title):
    """饼图"""
    fig = px.pie(
        ratio_df,
        names='奇偶比',
        values='出现次数',
        title=title,
        hole=0.4
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(dragmode=False, showlegend=False)
    return fig

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

def plot_zone_radar(zone_df):
    """区间分布雷达图"""
    fig = go.Figure()
    values = zone_df['平均出现次数'].tolist()
    labels = zone_df['区间'].tolist()
    
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=labels + [labels[0]],
        fill='toself',
        line_color='#ff6b6b',
        fillcolor='rgba(255, 107, 107, 0.3)'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, max(values) * 1.2])),
        showlegend=False,
        title="红球三区分布雷达图",
        dragmode=False
    )
    return fig

def main():
    st.markdown('<h1 class="title-text">🎱 双色球数据分析大师</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; color: #666; margin-bottom: 30px;'>
        智能分析500期历史数据，AI胆码杀号精准预测
    </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("## 📖 使用说明")
        st.markdown("""
        <div class="help-text">
        <b>🎯 核心功能：</b><br>
        • <b>胆码推荐</b>：AI分析推荐2个最可能出的号码<br>
        • <b>智能杀号</b>：排除5个最不可能的号码<br>
        • <b>和值预测</b>：基于统计推荐最佳和值范围<br>
        • <b>历史对比</b>：检查预测号码是否中过奖<br><br>
        <b>📊 5大预测策略：</b><br>
        🔥 热号追击 | ❄️ 冷号反弹<br>
        ⚖️ 平衡优选 | 🔗 连号策略<br>
        🎲 加权随机<br><br>
        <b>⚠️ 理性购彩提示：</b><br>
        彩票有风险，算法仅供娱乐参考
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("## 🎛️ 控制面板")
        analysis_period = st.selectbox(
            "选择分析期数",
            ["最近50期", "最近100期", "最近200期", "最近500期"],
            index=2
        )
        
        st.markdown("---")
        
        # 获取数据按钮
        if st.button("🔄 获取最新数据", key="fetch_data"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                for i in range(5):
                    status_text.text(f"正在加载数据批次 {i+1}/5...")
                    progress_bar.progress((i + 1) * 20)
                    time.sleep(0.1)
                
                df = fetch_ssq_data_async()
                st.session_state['data'] = df
                progress_bar.empty()
                status_text.empty()
                st.success(f"✅ 成功获取 {len(df)} 期数据！")
                st.balloons()
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"获取失败: {str(e)}")
        
        # AI智能预测按钮
        if st.button("🎯 AI智能预测", key="smart_predict"):
            if 'data' not in st.session_state:
                st.warning("请先获取历史数据！")
            else:
                with st.spinner("🤖 AI正在深度分析..."):
                    df = st.session_state['data']
                    
                    # 计算胆码和杀号
                    drag_codes = get_drag_codes(df)
                    kill_codes = get_kill_codes(df)
                    
                    # 生成预测
                    predictions = generate_5_predictions(df, kill_codes, drag_codes)
                    
                    st.session_state['predictions'] = predictions
                    st.session_state['drag_codes'] = drag_codes
                    st.session_state['kill_codes'] = kill_codes
                    st.session_state['sum_stats'] = analyze_sum_range(df)
                
                st.success("✅ 预测完成！")
        
        # 显示胆码杀号
        if 'drag_codes' in st.session_state:
            st.markdown("---")
            st.markdown("### 🎯 胆码推荐（必出）")
            st.markdown(' '.join([f'<span class="drag-code">{x:02d}</span>' for x in st.session_state['drag_codes']]), unsafe_allow_html=True)
            
            st.markdown("### 🚫 杀号排除（不出）")
            st.markdown(' '.join([f'<span class="kill-code">{x:02d}</span>' for x in st.session_state['kill_codes']]), unsafe_allow_html=True)
            
            if 'sum_stats' in st.session_state:
                stats = st.session_state['sum_stats']
                st.markdown("### 📊 和值推荐")
                st.info(f"推荐范围：**{stats['recommended_min']} - {stats['recommended_max']}**\n\n历史均值：{stats['mean']:.1f}")
        
        # 显示预测结果缩略
        if 'predictions' in st.session_state:
            st.markdown("---")
            st.markdown("### 🎲 预测结果")
            for i, pred in enumerate(st.session_state['predictions']):
                with st.expander(f"{pred['name']}", expanded=i==0):
                    red_str = ' '.join([f"{x:02d}" for x in pred['red']])
                    st.markdown(f"🔴 {red_str}")
                    st.markdown(f"🔵 {pred['blue']:02d}")
                    if pred['historical_match']['matched']:
                        st.warning(f"⚠️ 历史曾中{pred['historical_match']['prize']}")
    
    if 'data' not in st.session_state:
        st.session_state['data'] = generate_sample_data()
    
    df = st.session_state['data']
    
    period_map = {"最近50期": 50, "最近100期": 100, "最近200期": 200, "最近500期": 500}
    display_count = period_map[analysis_period]
    df_display = df.head(display_count).copy()
    
    # 指标卡
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 分析期数", f"{len(df_display)}期")
    with col2:
        latest_sum = int(df_display.iloc[0]['红球和值']) if len(df_display) > 0 else 0
        st.metric("🎯 最新和值", latest_sum)
    with col3:
        red_freq = analyze_red_ball_frequency(df_display)
        hot_num = red_freq.iloc[0]['号码'] if len(red_freq) > 0 else "-"
        st.metric("🔥 最热红球", f"号{hot_num}")
    with col4:
        omission_df = analyze_omission(df_display)
        max_omit_num = omission_df.loc[omission_df['遗漏期数'].idxmax(), '号码']
        max_omit_count = omission_df['遗漏期数'].max()
        st.metric("❄️ 最大遗漏", f"号{max_omit_num}({max_omit_count}期)")
    
    st.markdown("---")
    
    # 主界面预测展示
    if 'predictions' in st.session_state:
        st.markdown("## 🎯 AI智能预测号码")
        st.caption("基于胆码杀号分析，5种策略精准推荐：")
        
        cols = st.columns(5)
        for idx, (col, pred) in enumerate(zip(cols, st.session_state['predictions'])):
            with col:
                match_warning = ""
                if pred['historical_match']['matched']:
                    match_warning = f'<p style="color:#f39c12;font-size:11px;margin:5px 0;">⚠️ 曾中{pred["historical_match"]["prize"]}</p>'
                
                st.markdown(f"""
                <div class="prediction-card">
                    <h4 style="margin:0 0 10px 0;font-size:14px;">{pred['name']}</h4>
                    <p style="font-size:11px; margin:0 0 10px 0; opacity:0.9;">{pred['desc']}</p>
                    <div style="margin:8px 0;">
                        {' '.join([f'<span class="red-ball">{x:02d}</span>' for x in pred['red']])}
                    </div>
                    <div style="margin:8px 0;">
                        <span class="blue-ball">{pred['blue']:02d}</span>
                    </div>
                    {match_warning}
                    <p style="font-size:10px; margin:8px 0 0 0; opacity:0.8;">
                        和:{pred['sum']} 跨:{pred['span']} {pred['odd_even']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        # 收藏功能
        st.markdown("### 💾 收藏号码")
        selected_pred = st.selectbox(
            "选择要收藏的预测",
            [f"{p['name']}: {' '.join([f'{x:02d}' for x in p['red']])} + {p['blue']:02d}" for p in st.session_state['predictions']]
        )
        if st.button("⭐ 添加到收藏", key="add_fav"):
            if 'favorites' not in st.session_state:
                st.session_state['favorites'] = []
            
            pred_idx = [f"{p['name']}: {' '.join([f'{x:02d}' for x in p['red']])} + {p['blue']:02d}" for p in st.session_state['predictions']].index(selected_pred)
            fav_data = st.session_state['predictions'][pred_idx].copy()
            fav_data['收藏时间'] = datetime.now().strftime('%Y-%m-%d %H:%M')
            
            st.session_state['favorites'].append(fav_data)
            st.success("已添加到收藏！")
        
        if 'favorites' in st.session_state and st.session_state['favorites']:
            with st.expander(f"查看收藏（{len(st.session_state['favorites'])}组）"):
                for i, fav in enumerate(st.session_state['favorites']):
                    st.text(f"{i+1}. {fav['name']}: {' '.join([f'{x:02d}' for x in fav['red']])} + {fav['blue']:02d} | 收藏于{fav['收藏时间']}")
        
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
            fig_red = plot_frequency_chart(red_freq.head(15), "红球出现频率TOP15", "Reds")
            st.plotly_chart(fig_red, use_container_width=True, config={'displayModeBar': False})
            
            st.markdown("#### ⚖️ 奇偶比例分布")
            odd_even_df = analyze_odd_even_ratio(df_display)
            fig_pie = plot_pie_chart(odd_even_df, "奇偶比例分布")
            st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
        
        with col_right:
            st.markdown("#### 🔵 蓝球频率统计")
            blue_freq = analyze_blue_ball_frequency(df_display)
            fig_blue = plot_frequency_chart(blue_freq, "蓝球出现频率", "Blues")
            st.plotly_chart(fig_blue, use_container_width=True, config={'displayModeBar': False})
            
            st.markdown("#### 🗺️ 三区分布雷达")
            zone_df = analyze_zone_distribution(df_display)
            fig_radar = plot_zone_radar(zone_df)
            st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})
    
    with tab2:
        st.markdown("### 🔥 号码冷热分析")
        st.markdown("#### 🔥❄️ 红球冷热分布热力图")
        fig_heatmap = plot_red_heatmap(df_display)
        st.plotly_chart(fig_heatmap, use_container_width=True, config={'displayModeBar': False})
        
        col_cold, col_hot = st.columns(2)
        with col_cold:
            st.markdown("#### ❄️ 冷号预警（遗漏>20期）")
            cold_numbers = omission_df[omission_df['遗漏期数'] > 20].sort_values('遗漏期数', ascending=False)
            if len(cold_numbers) > 0:
                st.dataframe(cold_numbers.style.background_gradient(subset=['遗漏期数'], cmap='Blues_r'), use_container_width=True)
            else:
                st.info("暂无遗漏超过20期的号码")
        
        with col_hot:
            st.markdown("#### 🔥 热号追踪（出现次数TOP10）")
            hot_numbers = red_freq.head(10)
            st.dataframe(hot_numbers.style.background_gradient(subset=['出现次数'], cmap='Reds'), use_container_width=True)
    
    with tab3:
        st.markdown("### 📊 走势图表分析")
        st.markdown("#### 📈 红球和值走势（含推荐范围）")
        fig_trend = plot_trend_line(df_display)
        st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})
        
        col_trend1, col_trend2 = st.columns(2)
        with col_trend1:
            st.markdown("#### 📉 跨度分析")
            fig_span = px.histogram(df_display, x='红球跨度', nbins=20, title="红球跨度分布", color_discrete_sequence=['#ff6b6b'])
            fig_span.update_layout(xaxis=dict(fixedrange=True), yaxis=dict(fixedrange=True), dragmode=False)
            st.plotly_chart(fig_span, use_container_width=True, config={'displayModeBar': False})
        
        with col_trend2:
            st.markdown("#### 🔄 连号统计")
            consecutive_df = analyze_consecutive_numbers(df_display)
            fig_con = px.bar(consecutive_df, x='连号对数', y='出现次数', title="连号出现对数统计", color='出现次数', text='出现次数')
            fig_con.update_traces(textposition='outside')
            fig_con.update_layout(xaxis=dict(fixedrange=True), yaxis=dict(fixedrange=True), dragmode=False)
            st.plotly_chart(fig_con, use_container_width=True, config={'displayModeBar': False})
    
    with tab4:
        st.markdown("### 🎯 深度规律分析")
        
        col_omit1, col_omit2 = st.columns(2)
        with col_omit1:
            st.markdown("#### 🔢 红球遗漏分析")
            fig_omit = px.bar(omission_df.sort_values('遗漏期数', ascending=False).head(20), 
                            x='号码', y='遗漏期数', title="当前遗漏TOP20", color='遗漏期数', color_continuous_scale='RdYlBu_r')
            fig_omit.update_layout(xaxis=dict(fixedrange=True), yaxis=dict(fixedrange=True), dragmode=False)
            st.plotly_chart(fig_omit, use_container_width=True, config={'displayModeBar': False})
        
        with col_omit2:
            st.markdown("#### 📋 遗漏统计")
            omit_stats = omission_df['遗漏期数'].describe()
            st.metric("平均遗漏", f"{omit_stats['mean']:.1f}期")
            st.metric("最大遗漏", f"{omit_stats['max']:.0f}期")
            st.metric("最小遗漏", f"{omit_stats['min']:.0f}期")
            
            high_omit = len(omission_df[omission_df['遗漏期数'] > 20])
            st.info(f"当前有 **{high_omit}** 个号码遗漏超过20期，值得关注！")
        
        st.markdown("#### 🎲 蓝球012路分析")
        df_012 = df_display.copy()
        df_012['012路'] = df_012['蓝球'] % 3
        road_map = {0: '0路(3,6,9,12,15)', 1: '1路(1,4,7,10,13,16)', 2: '2路(2,5,8,11,14)'}
        df_012['012路分类'] = df_012['012路'].map(road_map)
        
        road_counts = df_012['012路分类'].value_counts().reset_index()
        road_counts.columns = ['路数', '出现次数']
        
        col_road1, col_road2 = st.columns(2)
        with col_road1:
            fig_road = px.pie(road_counts, names='路数', values='出现次数', title="蓝球012路分布", hole=0.4)
            fig_road.update_layout(dragmode=False)
            st.plotly_chart(fig_road, use_container_width=True, config={'displayModeBar': False})
        
        with col_road2:
            fig_blue = plot_frequency_chart(blue_freq, "蓝球冷热统计", "Blues")
            st.plotly_chart(fig_blue, use_container_width=True, config={'displayModeBar': False})
    
    with tab5:
        st.markdown("### 📋 原始开奖数据")
        display_cols = ['期号', '开奖日期', '红球1', '红球2', '红球3', '红球4', '红球5', '红球6', '蓝球', '红球和值', '红球跨度']
        
        st.dataframe(df_display[display_cols].style.highlight_max(subset=['红球和值'], color='#90EE90', axis=0)
                                             .highlight_min(subset=['红球和值'], color='#FFB6C1', axis=0), 
                    use_container_width=True, height=600)
        
        # 导出功能
        col_down1, col_down2, col_down3 = st.columns(3)
        with col_down1:
            csv = df_display.to_csv(index=False).encode('utf-8')
            st.download_button("📥 下载CSV", csv, f"ssq_data_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
        
        with col_down2:
            json_data = df_display[display_cols].to_json(orient='records', force_ascii=False)
            st.download_button("📥 下载JSON", json_data, f"ssq_data_{datetime.now().strftime('%Y%m%d')}.json", "application/json")
        
        with col_down3:
            if 'predictions' in st.session_state:
                pred_json = json.dumps(st.session_state['predictions'], ensure_ascii=False, default=str)
                st.download_button("📥 导出预测", pred_json, f"predictions_{datetime.now().strftime('%Y%m%d')}.json", "application/json")

    st.markdown("""
    <div class="footer">
        🧅 创作者：洋葱头 | 献给李兰序 | 数据分析仅供娱乐参考，请理性购彩
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()


