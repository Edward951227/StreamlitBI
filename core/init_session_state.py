import streamlit as st

# 初始化所有状态变量
def init_session_state():
    # 初始化会话状态变量
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = {}  # 存储上传的文件，格式: {文件名: DataFrame}
    # 初始化选中文件
    if 'selected_file' not in st.session_state:
        st.session_state.selected_file = None  # 当前选中的文件名
    # 初始化筛选条件会话状态
    if 'filters' not in st.session_state:
        st.session_state.filters = {}
    # 初始化是否分组
    if 'use_grouping' not in st.session_state:
        st.session_state.use_grouping = False
    # 初始化index
    if 'index' not in st.session_state:
        st.session_state.index = None
    # 绘图时确认是否有数据
    if 'filtered_data' not in st.session_state:
        st.session_state.filtered_data = None
    # 筛选后的数据
    if 'agg_type' not in st.session_state:
        st.session_state.agg_type = None