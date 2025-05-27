import streamlit as st
import pandas as pd

# 엑셀 파일 불러오기
@st.cache_data
def load_data():
    df = pd.read_excel("정보.xlsx")
    return df

df = load_data()

# 사용자 입력
st.title("아이디 찾기 페이지")

name = st.text_input("이름을 입력하세요:")
number = st.text_input("번호를 입력하세요:")

if st.button("아이디 찾기"):
    if not name or not number:
        st.warning("이름과 번호를 모두 입력해주세요.")
    else:
        # 이름과 번호로 필터링
        result = df[(df["이름"] == name) & (df["번호"].astype(str) == number)]
        
        if not result.empty:
            user_id = result.iloc[0]["ID"]
            st.success(f"아이디는: **{user_id}** 입니다.")
        else:
            st.error("일치하는 정보를 찾을 수 없습니다.")
