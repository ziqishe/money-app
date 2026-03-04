import streamlit as st
import pandas as pd
from datetime import date
from db import fetch_txns, delete_txn

st.header("📊 账单")

colA, colB = st.columns(2)
with colA:
    date_from = st.date_input("开始日期", value=date(date.today().year, date.today().month, 1))
with colB:
    date_to = st.date_input("结束日期", value=date.today())

rows = fetch_txns(date_from.isoformat(), date_to.isoformat())
df = pd.DataFrame(rows, columns=["id","date","amount","type","category","merchant","note","currency"])
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.sort_values(by=["date", "id"], ascending=[False, False])
if df.empty:
    st.info("这段时间还没有记录。")
    st.stop()

st.subheader("汇总（按币种）")

for cur in ["GBP", "CNY"]:
    sub = df[df["currency"] == cur]
    inc = sub[sub["type"] == "income"]["amount"].sum()
    exp = sub[sub["type"] == "expense"]["amount"].sum()
    bal = inc - exp

    c1, c2, c3 = st.columns(3)
    c1.metric(f"{cur} 总收入", f"{inc:.2f}")
    c2.metric(f"{cur} 总支出", f"{exp:.2f}")
    c3.metric(f"{cur} 结余", f"{bal:.2f}")

st.subheader("分类汇总（支出）— 按币种")

for cur in ["GBP", "CNY"]:
    sub = df[(df["type"] == "expense") & (df["currency"] == cur)]
    st.markdown(f"### {cur}")
    if sub.empty:
        st.caption("这段时间没有支出记录。")
        continue
    exp_cat = sub.groupby("category")["amount"].sum().sort_values(ascending=False)
    st.bar_chart(exp_cat)
st.subheader("明细")
st.dataframe(
    df.drop(columns=["id"]),
    use_container_width=True,
    hide_index=True
)

st.subheader("明细（逐条删除）")

# 逐条展示 + 删除按钮（不显示 id）
show_cols = ["date", "amount", "currency", "type", "category", "note"]

# 表头
h1, h2, h3, h4, h5, h6, h7 = st.columns([2, 2, 1, 1.5, 2, 4, 1])
h1.write("日期")
h2.write("金额")
h3.write("币种")
h4.write("类型")
h5.write("分类")
h6.write("备注")
h7.write("删除")

for _, row in df.iterrows():
    c1, c2, c3, c4, c5, c6, c7 = st.columns([2, 2, 1, 1.5, 2, 4, 1])

    # date 可能是 Timestamp
    d = row["date"]
    try:
        d_show = d.date()
    except Exception:
        d_show = d

    c1.write(d_show)
    c2.write(f'{float(row["amount"]):.2f}')
    c3.write(row["currency"])
    c4.write(row["type"])
    c5.write(row["category"])
    c6.write(row["note"])

    if c7.button("🗑", key=f"del_{int(row['id'])}"):
        delete_txn(int(row["id"]))
        st.rerun()
