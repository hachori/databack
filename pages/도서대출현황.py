# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

# CSV 파일 읽기
@st.cache_data
def load_data():
    return pd.read_csv("BestLoanList_20250527071549.csv", encoding="cp949")

df = load_data()

st.title("📚 도서 대출 현황 대시보드")

# 상위 n권 슬라이더
top_n = st.slider("상위 몇 권의 도서를 볼까요?", min_value=5, max_value=50, value=20)

# 정렬된 상위 n개 데이터
top_books = df.sort_values(by="대출건수", ascending=False).head(top_n)

# 막대그래프 시각화
fig = px.bar(
    top_books,
    x="서명",
    y="대출건수",
    hover_data=["저자", "출판사", "출판년도", "권"],
    title=f"📈 상위 {top_n}권 도서 대출 건수",
    labels={"서명": "책 제목", "대출건수": "대출 건수"},
)

fig.update_layout(xaxis_tickangle=-45)

st.plotly_chart(fig, use_container_width=True)

# 데이터 테이블 보기 옵션
if st.checkbox("📄 데이터 테이블 보기"):
    st.dataframe(top_books)
