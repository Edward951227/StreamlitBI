import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts
from core.convert_datetime_columns import convert_datetime_columns
from core.generate_option import generate_option
from core.get_data_types import get_data_types
from core.init_session_state import init_session_state


def main():
    # 初始化会话状态
    init_session_state()

    # 设置页面配置
    st.set_page_config(
        page_title="数据可视化看板",
        page_icon="📊",
        layout="wide"
    )

    # 侧边栏 - 数据筛选
    with (st.sidebar):
        st.header("📂 数据上传")

        # 上传CSV文件（支持多个文件，最大200MB）
        uploaded_files = st.file_uploader(
            "选择CSV文件",
            type="csv",
            accept_multiple_files=True,
            key="file_uploader"
        )

        # 处理上传的文件
        if uploaded_files:
            for file in uploaded_files:
                if file.name not in st.session_state.uploaded_files:
                    try:
                        df = pd.read_csv(file)
                        # 转换日期时间列
                        df = convert_datetime_columns(df)
                        st.session_state.uploaded_files[file.name] = df
                        st.success(f"已成功上传: {file.name}")
                    except Exception as e:
                        st.error(f"上传 {file.name} 失败: {str(e)}")

    # 页面标题
    st.title('🎈 数据可视化看板v0.5')

    # tab页
    tab1, tab2 = st.tabs(["筛选", "展示"])
    with tab1:
        # 完成初始化
        if st.session_state.uploaded_files:
            dataset_options = list(st.session_state.uploaded_files.keys())
            col1, col2 = st.columns([1, 4])

            # 选择框
            with col1:
                # 选择数据
                selected_file = st.selectbox(
                    "选择要处理的数据",
                    dataset_options,
                    # index=dataset_options.index(st.session_state.selected_file) if st.session_state.selected_file in dataset_options else 0
                )

                if selected_file != st.session_state.selected_file:
                    st.session_state.selected_file = selected_file
                    # 重置筛选数据
                    st.session_state.filtered_data = None
                    st.session_state.index = None

                # 获取所选数据
                df = st.session_state.uploaded_files[selected_file]

                # 获取数据类型
                data_types = get_data_types(df)

                # 复制数据用于筛选
                filtered_df = df.copy()

                # 获取字段
                columns = filtered_df.columns.tolist()

                # 数据分组
                st.subheader("数据分组")

                # 是否分组选项
                st.session_state.use_grouping = st.toggle("使用分组展示", value=False)
                if st.session_state.use_grouping:
                    # 分组字段
                    column = st.selectbox(
                        "分组字段",
                        columns
                    )

                    # 标签字段
                    index_options = [col for col in columns if col != column]
                    index = st.selectbox(
                        "标签字段",
                        index_options
                    )
                    # 保存index状态
                    st.session_state.index = index

                    # 值字段
                    value_options = [col for col in columns if col != column and col != index]
                    value_options = [col for col in value_options if data_types[col] == 'numeric']
                    value = st.selectbox(
                        "值字段",
                        value_options
                    )

                    try:
                        # 将分组后的数据保存
                        filtered_df = filtered_df.pivot(index=index, columns=column, values=value)
                        # 保存筛选后的数据到会话状态
                        st.session_state.filtered_data = filtered_df
                        # 加上index列
                        filtered_df[index] = filtered_df.index
                        # 重新获取数据类型
                        data_types = get_data_types(filtered_df)
                        # 重新获取字段
                        columns = filtered_df.columns.tolist()
                    except Exception as e:
                        st.warning(e)

                # 数据筛选
                st.subheader("数据筛选")

                # 选择要筛选的字段
                selected_filter_columns = st.multiselect(
                    "选择筛选字段",
                    columns
                )

                # 为每个字段创建筛选控件
                for col in selected_filter_columns:
                    if data_types[col] == 'datetime':
                        # 日期型字段
                        try:
                            min_date = filtered_df[col].min()
                            max_date = filtered_df[col].max()

                            if not pd.isna(min_date) and not pd.isna(max_date) and min_date < max_date:
                                date_range = st.date_input(
                                    f"{col} 范围",
                                    value=[min_date, max_date],
                                    min_value=min_date,
                                    max_value=max_date,
                                    key=f"date_{col}"
                                )
                                if len(date_range) == 2:
                                    filtered_df = filtered_df[
                                        (filtered_df[col] >= pd.to_datetime(date_range[0])) &
                                        (filtered_df[col] <= pd.to_datetime(date_range[1]))
                                        ]
                        except Exception as e:
                            st.warning(e)

                    elif data_types[col] == 'numeric':
                        # 数值型字段
                        min_val = float(filtered_df[col].min())
                        max_val = float(filtered_df[col].max())

                        # 只有当最大值大于最小值时才显示滑块
                        if max_val > min_val:
                            selected_range = st.slider(
                                f"{col} 范围",
                                min_value=min_val,
                                max_value=max_val,
                                value=(min_val, max_val),
                                key=f"slider_{col}"
                            )
                            filtered_df = filtered_df[
                                (filtered_df[col] >= selected_range[0]) &
                                (filtered_df[col] <= selected_range[1])
                            ]

                    else:
                        # 类别型字段
                        unique_vals = sorted(filtered_df[col].dropna().unique())
                        selected_vals = st.multiselect(
                            f"选择 {col} 的值",
                            unique_vals,
                            default=unique_vals,
                            key=f"multiselect_{col}"
                        )
                        filtered_df = filtered_df[filtered_df[col].isin(selected_vals)]

                # 保存筛选后的数据到会话状态
                st.session_state.filtered_data = filtered_df

            with col2:
                st.dataframe(filtered_df, use_container_width=True)

        else:
            st.warning("请上传数据，亲")

    with tab2:
        # 检查是否有可用数据
        if st.session_state.filtered_data is None or len(st.session_state.filtered_data) == 0:
            st.warning("没有可用数据，请先在首页上传并筛选数据")
        else:
            df = st.session_state.filtered_data

            # 如果index数据参与了筛选，需要去掉
            if st.session_state.use_grouping:
                df = df.reset_index(drop=True)

            # 重新获取数据类型
            data_types = get_data_types(df)
            # 重新获取字段
            columns = df.columns.tolist()
            # 选择框
            col1, col2 = st.columns([1, 4])
            with col1:
                chart_type = st.selectbox(
                    "图表类型",
                    ['bar', 'line', 'scatter']
                )

                # 选择X轴字段
                x_axis = st.selectbox(
                    "X轴字段",
                    columns
                )

                # 选择Y轴字段
                numeric_cols = [col for col in columns if data_types[col] == 'numeric']
                y_axes = st.multiselect(
                    "Y轴字段（可多选）",
                    numeric_cols
                )

                # 选择Y轴数据聚合类型（仅支持非分组）
                if not st.session_state.use_grouping:
                    agg_type = st.selectbox(
                        "聚合类型",
                        ["求和", "平均值", "最大值", "最小值", "中位数", "计数"]
                    )
                    # 更新聚合类型状态
                    st.session_state.agg_type = agg_type

            with col2:
                option = generate_option(df, x_axis, y_axes, data_types, chart_type)

                # 绘图
                st_echarts(
                    option,
                    height="600px"
                )

if __name__ == "__main__":
    main()