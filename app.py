import streamlit as st
from db import init_db

st.set_page_config(page_title="记账助手", page_icon="💰", layout="wide")
init_db()

st.title("💰 记账助手")
st.write("左侧选择：Page 1 记账 / Page 2 账单")
