import streamlit as st
from parser import parse_text
from db import insert_txn

st.header("🧾 对话记账（自动识别）")

text = st.text_input("输入一条记账描述：", placeholder="例如：今天星巴克 26.5 咖啡 / 3/1 收到工资 12000 / Tesco 18.5 GBP")

if st.button("识别"):
    st.session_state["last_parse"] = parse_text(text)

result = st.session_state.get("last_parse")
if result:
    if not result.get("ok"):
        st.error(result.get("error"))
    else:
        st.success("识别成功：可直接确认入账，或先编辑。")

        col1, col2, col3 = st.columns(3)
        with col1:
            date_ = st.text_input("日期", value=result["date"])
            type_ = st.selectbox("类型", ["expense", "income"], index=0 if result["type"]=="expense" else 1)
        with col2:
            amount = st.number_input("金额", value=float(result["amount"]), min_value=0.0, step=1.0)
            currency = st.text_input("币种", value=result.get("currency","CNY"))
        with col3:
            category = st.text_input("分类", value=result.get("category","其他"))
            merchant = st.text_input("商户（可空）", value=result.get("merchant",""))

        note = st.text_area("备注", value=result.get("note",""))

        if st.button("✅ 确认入账"):
            insert_txn(date_, float(amount), type_, category, merchant, note, currency)
            st.success("已入账！")
            st.session_state["last_parse"] = None

