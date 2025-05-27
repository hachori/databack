import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st # Streamlit 사용을 위해 추가

# --- 데이터 로드 ---
csv_url = "https://raw.githubusercontent.com/hachori/databack/main/202504_202504_%EC%97%B0%EB%A0%B9%EB%B3%84%EC%9D%B8%EA%B5%AC%ED%98%84%ED%99%A9_%EC%9B%94%EA%B0%84_%EB%82%A8%EB%85%80%ED%95%A9%EA%B3%84.csv"

try:
    # euc-kr 인코딩으로 시도
    df = pd.read_csv(csv_url, encoding='euc-kr')
    # print("euc-kr 인코딩으로 파일을 성공적으로 읽었습니다.") # Streamlit에서는 print 대신 st.write 사용 권장
except UnicodeDecodeError:
    try:
        # cp949 인코딩으로 시도
        df = pd.read_csv(csv_url, encoding='cp949')
        # print("cp949 인코딩으로 파일을 성공적으로 읽었습니다.")
    except Exception as e:
        # print(f"다른 인코딩으로도 파일을 읽는 데 실패했습니다: {e}")
        # UTF-8로 다시 시도 (기본값)
        df = pd.read_csv(csv_url, encoding='utf-8')
        # print("utf-8 인코딩으로 파일을 시도했습니다 (오류가 다시 발생할 수 있음).")
except Exception as e:
    # print(f"파일을 읽는 도중 예기치 않은 오류가 발생했습니다: {e}")
    st.error(f"데이터를 로드하는 중 오류가 발생했습니다: {e}. 인코딩 문제일 수 있습니다.")
    st.stop() # 오류 발생 시 앱 중단

# '행정구역' 컬럼에서 '서울특별시' 데이터만 필터링
seoul_df = df[df['행정구역'].str.contains('서울특별시')].copy()

# '총인구수'와 '연령구간인구수' 컬럼 제거
# '2025년04월_계_총인구수' 및 '2025년04월_계_연령구간인구수' 컬럼은 melt 대상이 아니므로 제거
columns_to_drop = [col for col in seoul_df.columns if '총인구수' in col or '연령구간인구수' in col]
seoul_age_df = seoul_df.drop(columns=columns_to_drop, errors='ignore') # errors='ignore'로 컬럼이 없어도 에러 발생 안 함

# 연령별 인구수 컬럼들을 녹여서 '연령'과 '인구수' 컬럼 생성
# value_vars는 제거된 컬럼을 제외한 '2025년04월_계_'로 시작하는 컬럼만 선택
value_vars_cols = [col for col in seoul_age_df.columns if col.startswith('2025년04월_계_')]

seoul_age_melted = seoul_age_df.melt(
    id_vars=['행정구역'],
    value_vars=value_vars_cols,
    var_name='연령_원문',
    value_name='총인구수'
)

# --- 총인구수 컬럼을 숫자형으로 변환 ---
# 숫자로 변환할 수 없는 값은 NaN으로 처리 (errors='coerce')
# 그리고 NaN 값은 0으로 채우거나, 분석 목적에 따라 드롭할 수 있습니다.
seoul_age_melted['총인구수'] = pd.to_numeric(seoul_age_melted['총인구수'], errors='coerce')
seoul_age_melted['총인구수'] = seoul_age_melted['총인구수'].fillna(0) # NaN 값은 0으로 채우기 (선택 사항)
# -------------------------------------

# '연령_원문' 컬럼에서 불필요한 prefix 제거 및 정수형으로 변환 가능한 형태로 정리
seoul_age_melted['연령'] = seoul_age_melted['연령_원문'].str.replace('2025년04월_계_', '').str.replace('세', '').str.replace(' 이상', '+')

# 연령대 정렬을 위한 임시 컬럼 생성
seoul_age_melted['연령_정렬_값'] = seoul_age_melted['연령'].apply(lambda x: int(x.replace('+', '1000')) if '+' in x else int(x))

# 데이터를 연령_정렬_값 기준으로 정렬
seoul_age_melted = seoul_age_melted.sort_values(by='연령_정렬_값', ascending=True)

# 인구 피라미드 시각화를 위해 남녀 인구수 컬럼 생성 (가상의 비율 적용)
seoul_age_melted['남성인구수'] = seoul_age_melted['총인구수'] * 0.49
seoul_age_melted['여성인구수'] = seoul_age_melted['총인구수'] * 0.51

# 남성 인구수를 음수로 만들어 피라미드 형태로 표시
seoul_age_melted['남성인구수_음수'] = -seoul_age_melted['남성인구수']

# --- Plotly를 이용한 인구 피라미드 시각화 ---
fig = make_subplots(rows=1, cols=2, specs=[[{}, {}]], shared_yaxes=True,
                    horizontal_spacing=0.01)

# 남성 인구 그래프
fig.add_trace(
    go.Bar(
        y=seoul_age_melted['연령'],
        x=seoul_age_melted['남성인구수_음수'],
        name='남성',
        orientation='h',
        marker=dict(color='skyblue')
    ),
    row=1, col=1
)

# 여성 인구 그래프
fig.add_trace(
    go.Bar(
        y=seoul_age_melted['연령'],
        x=seoul_age_melted['여성인구수'],
        name='여성',
        orientation='h',
        marker=dict(color='lightcoral')
    ),
    row=1, col=2
)

# 레이아웃 설정
fig.update_layout(
    title_text='서울특별시 연령별 인구 피라미드 (2025년 4월)',
    title_x=0.5,
    barmode='overlay',
    bargap=0.1,
    height=800,
    xaxis_title='인구수',
    yaxis_title='연령',
    xaxis=dict(
        # tickvals와 ticktext를 동적으로 생성
        tickvals=sorted(list(set(seoul_age_melted['남성인구수_음수'].dropna().unique().tolist() + seoul_age_melted['여성인구수'].dropna().unique().tolist()))),
        ticktext=[f"{abs(x):,}" for x in sorted(list(set(seoul_age_melted['남성인구수_음수'].dropna().unique().tolist() + seoul_age_melted['여성인구수'].dropna().unique().tolist())))],
        range=[min(seoul_age_melted['남성인구수_음수']) * 1.1 if not seoul_age_melted['남성인구수_음수'].empty else -100,
               max(seoul_age_melted['여성인구수']) * 1.1 if not seoul_age_melted['여성인구수'].empty else 100], # X축 범위 조정
        showgrid=True,
        zeroline=False
    ),
    yaxis=dict(
        categoryorder='array',
        categoryarray=seoul_age_melted['연령'].tolist()
    ),
    annotations=[
        dict(
            x=0.25, y=1.05, xref='paper', yref='paper',
            text='남성', showarrow=False, font=dict(size=14, color='skyblue')
        ),
        dict(
            x=0.75, y=1.05, xref='paper', yref='paper',
            text='여성', showarrow=False, font=dict(size=14, color='lightcoral')
        )
    ]
)

fig.update_xaxes(
    tickprefix='',
    col=1,
    tickvals=seoul_age_melted['남성인구수_음수'].dropna().unique().tolist(),
    ticktext=[f"{abs(val):,}" for val in seoul_age_melted['남성인구수_음수'].dropna().unique().tolist()],
    title_text='인구수',
)

fig.update_xaxes(
    col=2,
    title_text='인구수',
)

# Streamlit 앱에서 Plotly 그래프를 표시
st.plotly_chart(fig, use_container_width=True)
