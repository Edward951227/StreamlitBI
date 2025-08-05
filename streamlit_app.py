import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts

def get_data_types(df) -> dict:
    """
    返回每列的数据类型
    :param df: 待判断数据类型的DataFrame
    :return: Dictionary
    """
    data_types = {}
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            data_types[col] = 'datetime'
        elif pd.api.types.is_numeric_dtype(df[col]):
            data_types[col] = 'numeric'
        else:
            data_types[col] = 'categorical'
    return data_types

def main():
    # 可选数据
    dataset_options = []
    # 映射数据集到pandas函数
    table_mapping = {}

    # 设置页面配置
    st.set_page_config(
        page_title="数据可视化看板",
        page_icon="📊",
        layout="wide"
    )

    # 侧边栏 - 数据筛选
    with (st.sidebar):
        st.header("数据上传")

        # 上传数据（支持多个文件，最大200MB）
        uploaded_files = st.file_uploader(
            "选择CSV文件", accept_multiple_files=True
        )

        i = 0
        for uploaded_file in uploaded_files:
            i=+1
            df = pd.read_csv(uploaded_file)
            dataset_options.append(uploaded_file.name)
            table_mapping[uploaded_file.name] = df
            with st.expander("文件：" + uploaded_file.name):
                st.dataframe(df)

    # 页面标题
    st.title('🎈 数据可视化看板v0.1')

    # 完成初始化
    if i:
        col1, col2 = st.columns([1,4])

        # 选择框
        with col1:
            # 选择数据
            selected_dataset = st.selectbox(
                "选择数据集",
                dataset_options
            )
            df = table_mapping[selected_dataset]
            # 获取数据类型
            data_types = get_data_types(df)

            # 选择图表类型
            chart_type = st.selectbox(
                "图表类型",
                ['bar', 'line']
            )

            # 选择X轴字段
            x_axis = st.selectbox(
                "X轴字段",
                df.columns.tolist()
            )

            # 选择Y轴字段
            numeric_cols = [col for col in df.columns if data_types[col] == 'numeric']
            y_axes = st.multiselect(
                "Y轴字段（可多选）",
                numeric_cols
            )

            # 选择Y轴数据聚合类型
            agg_type = st.selectbox(
                "聚合类型",
                ["求和", "平均值", "最大值", "最小值", "中位数", "计数"]
            )

        with col2:
            option = {
                "tooltip": {
                    "trigger": "axis",
                    "axisPointer": {"type": "shadow" if chart_type == 'bar' else "line"}
                },
                "legend": {
                    "data": [],  # 动态填充图例
                    # "top": 30,
                    # "right": 10
                },
                "xAxis": {
                    "type": "category",
                    "data": df[x_axis].unique().tolist(),
                    "axisLabel": {"rotate": 45, "interval": 0}  # x轴标签旋转
                },
                "yAxis": {
                    "type": "value",
                    # "name": ", ".join(y_axes)
                },
                "series": []  # 动态填充数据系列
            }

            # 图例为Y轴字段
            option["legend"]["data"] = y_axes

            # 为每个Y轴字段添加系列
            for y_axis in y_axes:
                match agg_type:
                    case "求和":
                        y_axis_data = df.groupby(x_axis)[y_axis].sum().reindex(option["xAxis"]["data"]).fillna(0).tolist()
                    case "平均值":
                        y_axis_data = df.groupby(x_axis)[y_axis].mean().reindex(option["xAxis"]["data"]).fillna(0).tolist()
                    case "最大值":
                        y_axis_data = df.groupby(x_axis)[y_axis].max().reindex(option["xAxis"]["data"]).fillna(0).tolist()
                    case "最小值":
                        y_axis_data = df.groupby(x_axis)[y_axis].min().reindex(option["xAxis"]["data"]).fillna(0).tolist()
                    case "中位数":
                        y_axis_data = df.groupby(x_axis)[y_axis].median().reindex(option["xAxis"]["data"]).fillna(0).tolist()
                    case "计数":
                        y_axis_data = df.groupby(x_axis)[y_axis].count().reindex(option["xAxis"]["data"]).fillna(0).tolist()
                    case _:
                        # 默认求和
                        y_axis_data = df.groupby(x_axis)[y_axis].sum().reindex(option["xAxis"]["data"]).fillna(0).tolist()

                series = {
                    "name": y_axis,
                    "type": chart_type,
                    "data": y_axis_data
                }
                option["series"].append(series)

            # 绘图
            st_echarts(
                option,
                height="500px"
            )

    else:
        st.write("请上传数据，亲")

if __name__ == "__main__":
    main()