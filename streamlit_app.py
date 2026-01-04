import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --------------------------
# 页面基础配置
# --------------------------
st.set_page_config(
    page_title="魔鬼匹配数据统计看板",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自定义样式（优化视觉效果）
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .title-text {
        font-size: 24px;
        font-weight: 600;
        color: #2e4057;
    }
    .sub-title {
        font-size: 18px;
        font-weight: 500;
        color: #4a6fa5;
        margin-top: 20px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------
# 数据初始化（模拟当日数据）
# --------------------------
date = "01月02日"
data = {
    # 核心指标
    "总参与人数": 5783,
    "总对局数": 1883,
    "真人对局数": 1518,
    "人机对局数": 365,
    "翻盘局数": 355,
    "翻盘局占比": 23.39,
    "平均对局时长(秒)": 752.9,
    "战力差平均值": 31.18,
    "战力差中位数": 28.80,
    "战力差最大值": 459.93,
    "战力差超100局数": 27,
    
    # 新人等级分布
    "一级新人": 604,
    "二级新人": 583,
    "三级新人": 1821,
    "四级新人": 2601,
    "非新人": 174,
    
    # 各局参与人数&胜率
    "局数": [1, 2, 3, 4, 5, 6],
    "参与人数": [2831, 2677, 2415, 2671, 2405, 2080],
    "总体胜率": [52.56, 55.47, 60.50, 55.30, 62.54, 73.12],
    
    # 玩家参与场次分布
    "参与场次": [1, 2, 3, 4, 5, 6],
    "玩家数": [458, 650, 3907, 468, 169, 131]
}

# 转换为DataFrame方便可视化
df_round = pd.DataFrame({
    "局数": data["局数"],
    "参与人数": data["参与人数"],
    "总体胜率": data["总体胜率"]
})

df_play_times = pd.DataFrame({
    "参与场次": data["参与场次"],
    "玩家数": data["玩家数"]
})

df_newbie = pd.DataFrame({
    "新人等级": ["一级新人", "二级新人", "三级新人", "四级新人", "非新人"],
    "人数": [data["一级新人"], data["二级新人"], data["三级新人"], 
            data["四级新人"], data["非新人"]]
})

# --------------------------
# 页面主体布局
# --------------------------
# 标题栏
st.markdown(f"<div class='title-text'>{date} 魔鬼匹配数据统计报告</div>", unsafe_allow_html=True)
st.divider()

# 第一行：核心指标卡片（4列）
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.metric("总参与人数", f"{data['总参与人数']} 人")
    st.metric("总对局数", f"{data['总对局数']} 局")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.metric("真人对局数", f"{data['真人对局数']} 局")
    st.metric("人机对局数", f"{data['人机对局数']} 局")
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.metric("翻盘局数", f"{data['翻盘局数']} 局")
    st.metric("翻盘局占比", f"{data['翻盘局占比']}%")
    st.markdown("</div>", unsafe_allow_html=True)

with col4:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.metric("平均对局时长", f"{data['平均对局时长(秒)']:.1f} 秒")
    st.metric("战力差超100局数", f"{data['战力差超100局数']} 局")
    st.markdown("</div>", unsafe_allow_html=True)

# 第二行：战力差统计 + 新人等级分布
col5, col6 = st.columns(2)

with col5:
    st.markdown("<div class='sub-title'>战力差统计</div>", unsafe_allow_html=True)
    # 战力差指标+柱状图
    fig_power = go.Figure()
    fig_power.add_trace(go.Bar(
        x=["平均值", "中位数", "最大值"],
        y=[data["战力差平均值"], data["战力差中位数"], data["战力差最大值"]],
        marker_color=["#3274A1", "#E1812C", "#C03D3E"]
    ))
    fig_power.update_layout(
        height=300,
        yaxis_title="战力差值",
        xaxis_title="统计维度",
        showlegend=False
    )
    st.plotly_chart(fig_power, use_container_width=True)

with col6:
    st.markdown("<div class='sub-title'>新人等级分布</div>", unsafe_allow_html=True)
    fig_newbie = px.pie(
        df_newbie,
        values="人数",
        names="新人等级",
        hole=0.3,
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    fig_newbie.update_layout(height=300)
    st.plotly_chart(fig_newbie, use_container_width=True)

# 第三行：各局参与人数&胜率 + 玩家参与场次分布
col7, col8 = st.columns(2)

with col7:
    st.markdown("<div class='sub-title'>各局参与人数&胜率</div>", unsafe_allow_html=True)
    # 双Y轴图表：参与人数（柱状）+ 胜率（折线）
    fig_round = make_subplots(specs=[[{"secondary_y": True}]])
    # 参与人数柱状图
    fig_round.add_trace(
        go.Bar(x=df_round["局数"], y=df_round["参与人数"], name="参与人数", marker_color="#6C9EAF"),
        secondary_y=False
    )
    # 胜率折线图
    fig_round.add_trace(
        go.Line(x=df_round["局数"], y=df_round["总体胜率"], name="总体胜率(%)", marker_color="#E57C23"),
        secondary_y=True
    )
    # 配置轴标签
    fig_round.update_layout(
        height=300,
        xaxis_title="局数",
        yaxis_title="参与人数",
        yaxis2_title="总体胜率(%)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_round, use_container_width=True)

with col8:
    st.markdown("<div class='sub-title'>玩家参与场次分布</div>", unsafe_allow_html=True)
    fig_play = px.bar(
        df_play_times,
        x="参与场次",
        y="玩家数",
        color="玩家数",
        color_continuous_scale="Blues",
        text="玩家数"
    )
    fig_play.update_layout(
        height=300,
        xaxis_title="参与场次",
        yaxis_title="玩家数",
        coloraxis_showscale=False
    )
    fig_play.update_traces(textposition="outside")
    st.plotly_chart(fig_play, use_container_width=True)

# 数据详情展开栏
with st.expander("📋 完整数据详情", expanded=False):
    col9, col10 = st.columns(2)
    with col9:
        st.subheader("基础数据")
        base_data = pd.DataFrame({
            "指标": ["总参与人数", "总对局数", "真人对局数", "人机对局数", "翻盘局数", "翻盘局占比",
                    "平均对局时长(秒)", "战力差平均值", "战力差中位数", "战力差最大值", "战力差超100局数"],
            "数值": [data["总参与人数"], data["总对局数"], data["真人对局数"], data["人机对局数"],
                    data["翻盘局数"], f"{data['翻盘局占比']}%", data["平均对局时长(秒)"],
                    data["战力差平均值"], data["战力差中位数"], data["战力差最大值"], data["战力差超100局数"]]
        })
        st.dataframe(base_data, use_container_width=True)
    
    with col10:
        st.subheader("各局数据")
        st.dataframe(df_round, use_container_width=True)
    
    st.subheader("新人等级&参与场次数据")
    col11, col12 = st.columns(2)
    with col11:
        st.dataframe(df_newbie, use_container_width=True)
    with col12:
        st.dataframe(df_play_times, use_container_width=True)
