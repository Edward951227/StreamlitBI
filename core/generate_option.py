from datetime import datetime
import streamlit as st

# 生成绘制ECharts图表option（核心函数）
def generate_option(df, x_axis, y_axes, data_types, chart_type):
    # 保证x轴数据唯一
    x_data = df[x_axis].unique().tolist()

    # x轴为时间处理
    if data_types[x_axis] == 'datetime':
        # 将datetime转换为numeric
        x_data = [str(x) for x in x_data]  # 强制转换为字符串
        x_data.sort(key=lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"))

    # x轴为数字处理
    if data_types[x_axis] == 'numeric':
        x_data.sort()

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
            "data": x_data,
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
        # 分组模式：按x轴和分组列同时分组
        grouped = df.groupby(x_axis)[y_axis]
        match st.session_state.agg_type:
            case "求和":
                y_axis_data = grouped.sum()
            case "平均值":
                y_axis_data = grouped.mean()
            case "最大值":
                y_axis_data = grouped.max()
            case "最小值":
                y_axis_data = grouped.min()
            case "中位数":
                y_axis_data = grouped.median()
            case "计数":
                y_axis_data = grouped.count()
            case _:
                # 默认求和
                y_axis_data = grouped.sum()
        y_axis_data = y_axis_data.reindex(option["xAxis"]["data"]).fillna(0).tolist()

        series = {
            "name": y_axis,
            "type": chart_type,
            "data": y_axis_data
        }
        option["series"].append(series)

    return option