import pandas as pd

csv_url = "https://raw.githubusercontent.com/hachori/databack/main/202504_202504_%EC%97%B0%EB%A0%B9%EB%B3%84%EC%9D%B8%EA%B5%AC%ED%98%84%ED%99%A9_%EC%9B%94%EA%B0%84_%EB%82%A8%EB%85%80%ED%95%A9%EA%B3%84.csv"

try:
    # euc-kr 인코딩으로 시도
    df = pd.read_csv(csv_url, encoding='euc-kr')
    print("euc-kr 인코딩으로 파일을 성공적으로 읽었습니다.")
except UnicodeDecodeError:
    try:
        # cp949 인코딩으로 시도
        df = pd.read_csv(csv_url, encoding='cp949')
        print("cp949 인코딩으로 파일을 성공적으로 읽었습니다.")
    except Exception as e:
        print(f"다른 인코딩으로도 파일을 읽는 데 실패했습니다: {e}")
        # UTF-8로 다시 시도 (기본값)
        df = pd.read_csv(csv_url, encoding='utf-8')
        print("utf-8 인코딩으로 파일을 시도했습니다 (오류가 다시 발생할 수 있음).")
except Exception as e:
    print(f"파일을 읽는 도중 예기치 않은 오류가 발생했습니다: {e}")

# 이하 기존 코드 계속...
# '행정구역' 컬럼에서 '서울특별시' 데이터만 필터링
seoul_df = df[df['행정구역'].str.contains('서울특별시')].copy() # SettingWithCopyWarning 방지

# '총인구수'와 '연령구간인구수' 컬럼 제거
seoul_age_df = seoul_df.drop(columns=['2025년04월_계_총인구수', '2025년04월_계_연령구간인구수'])

# 연령별 인구수 컬럼들을 녹여서 '연령'과 '인구수' 컬럼 생성
seoul_age_melted = seoul_age_df.melt(
    id_vars=['행정구역'],
    value_vars=[col for col in seoul_age_df.columns if col.startswith('2025년04월_계_')],
    var_name='연령_원문',
    value_name='총인구수'
)

# '연령_원문' 컬럼에서 불필요한 prefix 제거 및 정수형으로 변환 가능한 형태로 정리
seoul_age_melted['연령'] = seoul_age_melted['연령_원문'].str.replace('2025년04월_계_', '').str.replace('세', '').str.replace(' 이상', '+')

# 연령대 정렬을 위한 임시 컬럼 생성
seoul_age_melted['연령_정렬_값'] = seoul_age_melted['연령'].apply(lambda x: int(x.replace('+', '1000')) if '+' in x else int(x))

# 데이터를 연령_정렬_값 기준으로 정렬
seoul_age_melted = seoul_age_melted.sort_values(by='연령_정렬_값', ascending=True)

# 인구 피라미드 시각화를 위해 남녀 인구수 컬럼 생성 (가상의 비율 적용)
# 실제 남녀 데이터가 있다면 이 부분을 대체합니다.
seoul_age_melted['남성인구수'] = seoul_age_melted['총인구수'] * 0.49 # 예시: 남성 49%
seoul_age_melted['여성인구수'] = seoul_age_melted['총인구수'] * 0.51 # 예시: 여성 51%

# 남성 인구수를 음수로 만들어 피라미드 형태로 표시
seoul_age_melted['남성인구수_음수'] = -seoul_age_melted['남성인구수']

# Plotly를 이용한 인구 피라미드 시각화 (이 부분은 이전 답변의 코드와 동일)
import plotly.graph_objects as go
from plotly.subplots import make_subplots

fig = make_subplots(rows=1, cols=2, specs=[[{}, {}]], shared_yaxes=True,
                    horizontal_spacing=0.01)

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

fig.update_layout(
    title_text='서울특별시 연령별 인구 피라미드 (2025년 4월)',
    title_x=0.5,
    barmode='overlay',
    bargap=0.1,
    height=800,
    xaxis_title='인구수',
    yaxis_title='연령',
    xaxis=dict(
        tickvals=seoul_age_melted['남성인구수_음수'].unique().tolist() + seoul_age_melted['여성인구수'].unique().tolist(),
        ticktext=[f"{abs(x):,}" for x in seoul_age_melted['남성인구수_음수'].unique().tolist()] + [f"{x:,}" for x in seoul_age_melted['여성인구수'].unique().tolist()],
        range=[min(seoul_age_melted['남성인구수_음수']) * 1.1, max(seoul_age_melted['여성인구수']) * 1.1],
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
    tickvals=seoul_age_melted['남성인구수_음수'].unique().tolist(),
    ticktext=[f"{abs(val):,}" for val in seoul_age_melted['남성인구수_음수'].unique().tolist()],
    title_text='인구수',
)

fig.update_xaxes(
    col=2,
    title_text='인구수',
)

# Streamlit 앱에서 Plotly 그래프를 표시하는 코드
import streamlit as st
st.plotly_chart(fig, use_container_width=True)
