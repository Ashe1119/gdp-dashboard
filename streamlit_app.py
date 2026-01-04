# dashboard_complete.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

# 设置页面配置（必须放在最前面）
st.set_page_config(
    page_title="魔鬼匹配数据分析看板",
    page_icon="🎮",
    layout="wide",  # 宽屏模式
    initial_sidebar_state="expanded"  # 侧边栏默认展开
)


# ======================
# 1. 数据加载函数
# ======================
@st.cache_data(ttl=3600)  # 缓存1小时
def load_data():
    """加载清洗后的数据"""
    try:
        # 自动查找最新数据文件
        data_dir = Path("./data")
        excel_files = list(data_dir.glob("dayresult*.xlsx"))

        if not excel_files:
            st.warning("未找到数据文件，请先运行数据处理脚本")
            return pd.DataFrame()

        # 加载最新的文件
        latest_file = max(excel_files, key=os.path.getctime)
        df = pd.read_excel(latest_file)

        # 数据类型转换
        if '结束时间' in df.columns:
            df['结束时间'] = pd.to_datetime(df['结束时间'])
            df['日期'] = df['结束时间'].dt.date
            df['小时'] = df['结束时间'].dt.hour

        return df
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return pd.DataFrame()


# ======================
# 2. 侧边栏配置
# ======================
with st.sidebar:
    st.title("⚙️ 控制面板")

    # 日期选择器
    st.subheader("📅 日期筛选")
    if 'df' in locals():
        min_date = df['日期'].min() if not df.empty else datetime.now().date()
        max_date = df['日期'].max() if not df.empty else datetime.now().date()

        selected_date = st.date_input(
            "选择日期",
            value=max_date,
            min_value=min_date,
            max_value=max_date
        )
    else:
        selected_date = st.date_input("选择日期", value=datetime.now().date())

    # 数据刷新
    st.subheader("🔄 数据管理")
    if st.button("刷新数据", type="primary"):
        st.cache_data.clear()
        st.rerun()

    # 文件上传
    uploaded_file = st.file_uploader("上传新数据文件", type=['xlsx', 'csv'])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
            else:
                df = pd.read_csv(uploaded_file)

            # 保存文件
            save_path = Path("./data") / f"uploaded_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            save_path.parent.mkdir(exist_ok=True)
            df.to_excel(save_path, index=False)
            st.success("文件上传成功！")
            st.cache_data.clear()
        except Exception as e:
            st.error(f"文件上传失败: {e}")

    # 看板主题设置
    st.subheader("🎨 显示设置")
    theme = st.selectbox("选择图表主题", ["plotly", "plotly_white", "plotly_dark"])

    st.divider()
    st.caption(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ======================
# 3. 主页面布局
# ======================
# 页面标题
st.title("🎮 魔鬼匹配数据监控看板")
st.markdown("---")

# 加载数据
df = load_data()

if df.empty:
    st.error("⚠️ 没有可用的数据，请先运行数据处理流程或上传数据文件")
    st.stop()

# ======================
# 4. 关键指标卡片
# ======================
st.header("📊 核心指标概览")

# 创建指标卡片
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_players = df['玩家id'].nunique()
    st.metric(
        label="总参与人数",
        value=f"{total_players:,}",
        delta="+5%" if total_players > 5000 else None
    )

with col2:
    total_matches = df['对局id'].nunique()
    st.metric(
        label="对局总数",
        value=f"{total_matches:,}",
        delta=f"{(total_matches / 6):.0f}局/场"
    )

with col3:
    avg_time = df['对局时间'].mean()
    st.metric(
        label="平均对局时间",
        value=f"{avg_time:.1f}秒",
        delta=f"{(avg_time - 720):.1f}秒" if avg_time > 720 else None
    )

with col4:
    win_rate = (df['是否获胜'].sum() / len(df) * 100)
    st.metric(
        label="总体胜率",
        value=f"{win_rate:.1f}%",
        delta="平衡" if 48 <= win_rate <= 52 else "偏高" if win_rate > 52 else "偏低"
    )

with col5:
    comeback_matches = len(df[df['是否翻盘'] == 1]['对局id'].unique())
    comeback_rate = (comeback_matches / total_matches * 100) if total_matches > 0 else 0
    st.metric(
        label="翻盘局数",
        value=f"{comeback_matches}局",
        delta=f"{comeback_rate:.1f}%"
    )

st.markdown("---")

# ======================
# 5. 图表展示区域
# ======================
tab1, tab2, tab3, tab4 = st.tabs(["📈 趋势分析", "👥 玩家分析", "⚔️ 对局分析", "📋 详细数据"])

with tab1:
    # 趋势分析标签页
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("每小时对局数量")
        hourly_matches = df.groupby('小时')['对局id'].nunique().reset_index()
        fig1 = px.line(
            hourly_matches,
            x='小时',
            y='对局id',
            markers=True,
            title="对局时间分布",
            template=theme
        )
        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("每日参与人数趋势")
        daily_players = df.groupby('日期')['玩家id'].nunique().reset_index()
        fig2 = px.bar(
            daily_players,
            x='日期',
            y='玩家id',
            title="日活跃玩家数",
            template=theme
        )
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)

    # 胜率趋势
    st.subheader("胜率变化趋势")
    df_sorted = df.sort_values('结束时间')
    df_sorted['累计对局'] = range(1, len(df_sorted) + 1)
    df_sorted['累计胜率'] = df_sorted['是否获胜'].expanding().mean() * 100

    fig3 = px.line(
        df_sorted,
        x='累计对局',
        y='累计胜率',
        title="累计胜率变化曲线",
        template=theme
    )
    fig3.add_hline(y=50, line_dash="dash", line_color="red",
                   annotation_text="50%平衡线",
                   annotation_position="bottom right")
    st.plotly_chart(fig3, use_container_width=True)

with tab2:
    # 玩家分析标签页
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("玩家段位分布")
        if '段位' in df.columns:
            rank_dist = df[['玩家id', '段位']].drop_duplicates()['段位'].value_counts().reset_index()
            rank_dist.columns = ['段位', '人数']

            fig4 = px.bar(
                rank_dist,
                x='段位',
                y='人数',
                color='段位',
                title="玩家段位分布",
                template=theme
            )
            fig4.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig4, use_container_width=True)

    with col2:
        st.subheader("新人类型分布")
        if '新人类型' in df.columns:
            newcomer_dist = df[['玩家id', '新人类型']].drop_duplicates()['新人类型'].value_counts()

            fig5 = px.pie(
                values=newcomer_dist.values,
                names=newcomer_dist.index,
                title="新人类型占比",
                template=theme,
                hole=0.3
            )
            fig5.update_layout(height=400)
            st.plotly_chart(fig5, use_container_width=True)

    # KDA分布
    st.subheader("KDA分布热图")
    col1, col2, col3 = st.columns(3)

    with col1:
        kda_bins = st.slider("KDA分段数", 5, 20, 10)

    with col2:
        min_kda = st.number_input("最小KDA", 0.0, 10.0, 0.0)

    with col3:
        max_kda = st.number_input("最大KDA", 0.0, 20.0, 10.0)

    if 'KDA' in df.columns:
        filtered_df = df[(df['KDA'] >= min_kda) & (df['KDA'] <= max_kda)].copy()

        # 创建热图数据
        filtered_df['KDA_bin'] = pd.cut(filter_df['KDA'], bins=kda_bins)
        heatmap_data = pd.crosstab(
            filtered_df['段位'] if '段位' in filtered_df.columns else filtered_df['新人类型'],
            filtered_df['KDA_bin']
        )

        fig6 = px.imshow(
            heatmap_data,
            title="KDA vs 段位热力图",
            color_continuous_scale="Viridis",
            aspect="auto"
        )
        st.plotly_chart(fig6, use_container_width=True)

with tab3:
    # 对局分析标签页
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("对局时长分布")
        fig7 = px.histogram(
            df,
            x='对局时间',
            nbins=30,
            title="对局时长分布直方图",
            template=theme
        )
        fig7.add_vline(x=df['对局时间'].mean(), line_dash="dash",
                       line_color="red", annotation_text=f"平均{df['对局时间'].mean():.1f}秒")
        st.plotly_chart(fig7, use_container_width=True)

    with col2:
        st.subheader("战力差 vs 胜率")
        if '双方队伍战力差' in df.columns:
            # 计算不同战力差区间的胜率
            df['战力差区间'] = pd.cut(df['双方队伍战力差'], bins=10)
            win_rate_by_diff = df.groupby('战力差区间')['是否获胜'].mean().reset_index()
            win_rate_by_diff['战力差区间'] = win_rate_by_diff['战力差区间'].astype(str)

            fig8 = px.bar(
                win_rate_by_diff,
                x='战力差区间',
                y='是否获胜',
                title="不同战力差下的胜率",
                template=theme
            )
            fig8.update_layout(xaxis_title="战力差区间", yaxis_title="胜率")
            st.plotly_chart(fig8, use_container_width=True)

    # 翻盘局分析
    st.subheader("翻盘局特征分析")
    comeback_df = df[df['是否翻盘'] == 1]
    normal_df = df[df['是否翻盘'] == 0]

    if not comeback_df.empty:
        col1, col2, col3 = st.columns(3)

        with col1:
            # 翻盘局平均等级差
            if '己方5分钟平均等级' in df.columns and '敌方5分钟平均等级' in df.columns:
                comeback_df['5分钟等级差'] = comeback_df['敌方5分钟平均等级'] - comeback_df['己方5分钟平均等级']
                avg_diff = comeback_df['5分钟等级差'].mean()
                st.metric("翻盘局平均5分钟等级差", f"{avg_diff:.2f}级")

        with col2:
            # 翻盘局平均战力差
            if '双方队伍战力差' in df.columns:
                avg_power_diff = comeback_df['双方队伍战力差'].mean()
                st.metric("翻盘局平均战力差", f"{avg_power_diff:.2f}")

        with col3:
            # 翻盘局时长
            avg_time_comeback = comeback_df['对局时间'].mean()
            avg_time_normal = normal_df['对局时间'].mean()
            st.metric("翻盘局平均时长", f"{avg_time_comeback:.1f}秒",
                      delta=f"{(avg_time_comeback - avg_time_normal):.1f}秒")

with tab4:
    # 详细数据标签页
    st.subheader("原始数据表格")

    # 数据筛选器
    with st.expander("🔍 数据筛选", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            selected_ranks = st.multiselect(
                "选择段位",
                options=df['段位'].unique() if '段位' in df.columns else [],
                default=[]
            )

        with col2:
            min_kda_filter = st.number_input("最小KDA", 0.0, 20.0, 0.0, key="kda_min_filter")
            max_kda_filter = st.number_input("最大KDA", 0.0, 20.0, 10.0, key="kda_max_filter")

        with col3:
            win_filter = st.selectbox(
                "是否获胜",
                options=["全部", "是", "否"],
                index=0
            )

    # 应用筛选
    filtered_data = df.copy()

    if selected_ranks and '段位' in filtered_data.columns:
        filtered_data = filtered_data[filtered_data['段位'].isin(selected_ranks)]

    if 'KDA' in filtered_data.columns:
        filtered_data = filtered_data[
            (filtered_data['KDA'] >= min_kda_filter) &
            (filtered_data['KDA'] <= max_kda_filter)
            ]

    if win_filter == "是":
        filtered_data = filtered_data[filtered_data['是否获胜'] == 1]
    elif win_filter == "否":
        filtered_data = filtered_data[filtered_data['是否获胜'] == 0]

    # 显示数据
    st.dataframe(
        filtered_data,
        use_container_width=True,
        height=400,
        column_config={
            "玩家id": st.column_config.TextColumn(width="medium"),
            "昵称": st.column_config.TextColumn(width="medium"),
            "KDA": st.column_config.NumberColumn(format="%.2f"),
            "对局时间": st.column_config.NumberColumn(format="%.1f")
        }
    )

    # 下载按钮
    csv = filtered_data.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 下载筛选数据 (CSV)",
        data=csv,
        file_name=f"魔鬼匹配_筛选数据_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

    # 数据摘要
    st.subheader("数据摘要")
    col1, col2 = st.columns(2)

    with col1:
        st.json({
            "数据行数": len(filtered_data),
            "玩家数": filtered_data['玩家id'].nunique(),
            "对局数": filtered_data['对局id'].nunique(),
            "平均KDA": filtered_data['KDA'].mean() if 'KDA' in filtered_data.columns else "N/A"
        })

    with col2:
        st.json({
            "开始时间": filtered_data['结束时间'].min().strftime(
                '%Y-%m-%d %H:%M') if not filtered_data.empty else "N/A",
            "结束时间": filtered_data['结束时间'].max().strftime(
                '%Y-%m-%d %H:%M') if not filtered_data.empty else "N/A",
            "最长对局": filtered_data['对局时间'].max() if '对局时间' in filtered_data.columns else "N/A",
            "最短对局": filtered_data['对局时间'].min() if '对局时间' in filtered_data.columns else "N/A"
        })

# ======================
# 6. 底部信息
# ======================
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.caption("👤 玩家总数: " + str(df['玩家id'].nunique()))

with col2:
    st.caption("🎯 数据更新时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

with col3:
    if st.button("🔄 手动刷新数据", type="secondary"):
        st.cache_data.clear()
        st.rerun()

# ======================
# 7. 运行说明
# ======================
# 在终端运行: streamlit run dashboard_complete.py
