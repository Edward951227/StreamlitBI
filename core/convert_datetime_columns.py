import pandas as pd
import streamlit as st


# 转换日期时间列函数
def convert_datetime_columns(df):
    """将表头包含'日期'或'时间'的列转换为datetime类型"""
    for col in df.columns:
        # 检查列名是否包含'日期'或'时间'
        if '日期' in col or '时间' in col:
            try:
                # 尝试转换为datetime类型
                df[col] = pd.to_datetime(df[col], errors='coerce')
                st.success(f"已将列 '{col}' 转换为日期时间类型")
            except Exception as e:
                st.warning(f"列 '{col}' 转换为日期时间类型失败: {str(e)}")
    return df