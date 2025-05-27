# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

# 데이터 불러오기
@st.cache_data
def load_data():
    return pd.read_csv("BestLoanList_20250527071549.csv", encoding="cp949")

df = load_data()

st.title("📚 도서 대출 현황 대시보드")

# ─────────────────────────────────────
# 📌 도서명 검색 기능
# ─────────────────────────────────────
st.header("🔍 도서명으로 대출 순위 확인")

book_name = st.text_input("도서명을 입력하세요 (예: 흔한남매)").strip()

if book_name:
    matched_books = df[df["서명"].str.contains(book_name, case=False, na=False)]

    if not matched_books.empty:
        st.success(f"🔎 총 {len(matched_books)}권이 검색되었습니다.")
        st.dataframe(matched_books[["순위", "서명", "저자", "출판사", "출판년도", "대출건수"]].sort_values(by="순위"))
    else:
        st.warning("❗ 해당 도서를 찾을 수 없습니다. 정확한 도서명을 확인해 주세요.")

# ─────────────────────────────────────
# 1. 상위 대출 도서 시각화
# ─────────────────────────────────────
st.header("📈 상위 대출 도서")

top_n = st.slider("상위 몇 권의 도서를 볼까요?", 5, 50, 20)
top_books = df.sort_values(by="대출건수", ascending=False).head(top_n)

fig1 = px.bar(top_books, x="서명", y="대출건수",
              hover_data=["저자", "출판사", "출판년도"],
              title=f"Top {top_n} 대출 도서",
              labels={"서명": "책 제목", "대출건수": "대출 건수"})
fig1.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig1, use_container_width=True)

# ─────────────────────────────────────
# 2. 출판년도별 대출 건수
# ─────────────────────────────────────
st.header("📅 출판년도별 대출 건수")
yearly = df.groupby("출판년도")["대출건수"].sum().reset_index().sort_values("출판년도")

fig2 = px.line(yearly, x="출판년도", y="대출건수",
               title="출판년도별 총 대출 건수 추이")
st.plotly_chart(fig2, use_container_width=True)

# ─────────────────────────────────────
# 3. 출판사별 대출 현황
# ─────────────────────────────────────
st.header("🏢 출판사별 대출 건수 (상위 10개)")
publisher = df.groupby("출판사")["대출건수"].sum().reset_index()
top_publishers = publisher.sort_values(by="대출건수", ascending=False).head(10)

fig3 = px.bar(top_publishers, x="출판사", y="대출건수",
              title="대출 건수 상위 출판사", text="대출건수")
st.plotly_chart(fig3, use_container_width=True)

# ─────────────────────────────────────
# 4. 저자별 대출 건수 (상위 10명)
# ─────────────────────────────────────
st.header("✍️ 저자별 대출 건수 (상위 10명)")
author = df.groupby("저자")["대출건수"].sum().reset_index()
top_authors = author.sort_values(by="대출건수", ascending=False).head(10)

fig4 = px.bar(top_authors, x="저자", y="대출건수",
              title="대출 건수 상위 저자", text="대출건수")
st.plotly_chart(fig4, use_container_width=True)

# ─────────────────────────────────────
# 5. KDC 분류별 대출 건수
# ─────────────────────────────────────
st.header("📚 KDC 분류별 대출 건수")
df["KDC"] = df["KDC"].astype(str).str[:1]  # 대분류만 사용 (0~9)
kdc = df.groupby("KDC")["대출건수"].sum().reset_index()

fig5 = px.pie(kdc, names="KDC", values="대출건수", title="KDC 대분류별 대출 비율")
st.plotly_chart(fig5, use_container_width=True)

# ─────────────────────────────────────
# 6. 원본 데이터 확인
# ─────────────────────────────────────
if st.checkbox("🔍 원본 데이터 보기"):
    st.dataframe(df)
