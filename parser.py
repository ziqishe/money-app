import re
from datetime import date, datetime, timedelta
from dateutil.parser import parse as dtparse

CATEGORY_HINTS = {

    # 买菜（超市日常食材）
    "tesco": "买菜", "sainsbury": "买菜", "aldi": "买菜",
    "lidl": "买菜", "asda": "买菜", "waitrose": "买菜",
    "超市": "买菜", "买菜": "买菜","中超": "买菜",

    # 零食（非正餐小吃饮料）
    "零食": "零食", "奶茶": "零食", "咖啡": "零食",
    "starbucks": "零食", "饮料": "零食", "买零食": "零食",

    # 外食（正餐）
    "外卖": "外食", "外食": "外食",
    "餐厅": "外食", "吃饭": "外食",
    "kfc": "外食", "mcdonald": "外食",
    "麦当劳": "外食", "肯德基": "外食",

    # 杂货（非食品购物）
    "杂货": "杂货",

    # 交通
    "uber": "交通", "bolt": "交通",
    "地铁": "交通", "公交": "交通",
    "train": "交通", "火车": "交通",

    # 水电网
    "电费": "水电网", "水费": "水电网",
    "gas": "水电网", "燃气": "水电网",
    "网费": "水电网", "wifi": "水电网",

    # 购物
    "购物":"购物","买衣服":"购物",
    "买包":"购物","买鞋":"购物",
    

}
def guess_category(text: str) -> str:
    t = text.lower()
    for k, v in CATEGORY_HINTS.items():
        if k in t:
            return v
    return "其他"

import re

def detect_currency(text: str) -> str:
    t = text.lower().strip()

    # GBP：£ / gbp / 英镑 / 磅 / 金额后跟 p（如 50p）
    if "£" in t or "gbp" in t or "英镑" in t or "磅" in t:
        return "GBP"
    if re.search(r"\b\d+(\.\d+)?\s*p\b", t):  # 50p / 120 p
        return "GBP"

    # CNY：cny / rmb / 人民币 / 块 / 元
    if "cny" in t or "rmb" in t or "人民币" in t or "块" in t:
        return "CNY"
    if re.search(r"\b\d+(\.\d+)?\s*元\b", t):
        return "CNY"

    # 默认币种：按你生活地选一个
    return "GBP"

def detect_date(t: str) -> str:
    from datetime import date
    today = date.today()

    # 1) 中文：3月5日
    m = re.search(r"(\d{1,2})\s*月\s*(\d{1,2})\s*[日号]?", t)
    if m:
        mo, d = map(int, m.groups())
        try:
            return date(today.year, mo, d).isoformat()
        except ValueError:
            return today.isoformat()

    # 2) 月.日：2.28 / 12.31
    m = re.search(r"\b(\d{1,2})\.(\d{1,2})\b", t)
    if m:
        mo, d = map(int, m.groups())
        try:
            return date(today.year, mo, d).isoformat()
        except ValueError:
            return today.isoformat()

    # 3) 3/5 或 3-5
    m = re.search(r"\b(\d{1,2})[/-](\d{1,2})\b", t)
    if m:
        mo, d = map(int, m.groups())
        try:
            return date(today.year, mo, d).isoformat()
        except ValueError:
            return today.isoformat()

    # 没找到就用今天
    return today.isoformat()

def parse_text(text: str) -> dict:
    t = text.strip()

    # --- 1) 从原始文本中“抠出”日期片段（支持 2.28 / 2/28 / 2-28 / 3月5）
    date_str = None

    # 3月5 / 3月5日
    m = re.search(r"(\d{1,2})\s*月\s*(\d{1,2})\s*[日号]?", t)
    if m:
        mo, d = map(int, m.groups())
        try:
            date_str = date(date.today().year, mo, d).isoformat()
        except ValueError:
            date_str = date.today().isoformat()
        # 从文本里删掉这个日期片段
        t = re.sub(r"(\d{1,2})\s*月\s*(\d{1,2})\s*[日号]?", " ", t, count=1)

    # 2.28 / 2/28 / 2-28
    if date_str is None:
        m = re.search(r"\b(\d{1,2})[./-](\d{1,2})\b", t)
        if m:
            mo, d = map(int, m.groups())
            try:
                date_str = date(date.today().year, mo, d).isoformat()
            except ValueError:
                date_str = date.today().isoformat()
            # 从文本里删掉这个日期片段（关键！）
            t = re.sub(r"\b(\d{1,2})[./-](\d{1,2})\b", " ", t, count=1)

    if date_str is None:
        date_str = date.today().isoformat()

    # --- 2) 现在 t 里已经没有日期了，再找金额（就不会抓到 2.28）
    t_for_amount = re.sub(r"\s+", " ", t).strip()
    m = re.search(r"(-?\d+(?:\.\d{1,2})?)", t_for_amount)
    if not m:
        return {"ok": False, "error": "没找到金额（例如 26.5）"}

    amount = float(m.group(1))

    income_keywords = ["收入", "收到", "工资", "报销", "退款", "入账"]
    type_ = "income" if any(k in t for k in income_keywords) else "expense"
    amount = abs(amount)
    category = guess_category(t)

    note = re.sub(r"(\d{4}[-/.]\d{1,2}[-/.]\d{1,2}|\d{1,2}[-/.]\d{1,2})", "", t)
    note = re.sub(r"(-?\d+(?:\.\d{1,2})?)", "", note).strip(" ，,。;；")

    currency = detect_currency(t)

    return {
        "ok": True,
        "date": date_str,
        "amount": float(amount),
        "type": type_,
        "category": category,
        "merchant": "",
        "note": note,
        "currency": currency,
    }
