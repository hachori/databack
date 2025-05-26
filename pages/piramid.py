import pandas as pd
import plotly.express as px

# --- 데이터 로드 부분 추가 ---
# 깃허브의 Raw CSV 파일 URL
csv_url = "https://raw.githubusercontent.com/hachori/databack/main/202504_202504_%EC%97%B0%EB%A0%B9%EB%B3%84%EC%9D%B8%EA%B5%AC%ED%98%84%ED%99%A9_%EC%9B%94%EA%B0%84_%EB%82%A8%EB%85%80%ED%95%A9%EA%B3%84.csv"

# URL에서 CSV 파일 읽어오기
df = pd.read_csv(csv_url)
# -----------------------------

# '행정구역' 컬럼에서 '서울특별시' 데이터만 필터링
seoul_df = df[df['행정구역'].str.contains('서울특별시')]

# '2025년04월_계_총인구수'와 '2025년04월_계_연령구간인구수' 컬럼 제거
seoul_age_df = seoul_df.drop(columns=['2025년04월_계_총인구수', '2025년04월_계_연령구간인구수'])

# 연령별 인구수 컬럼들을 녹여서 '연령'과 '인구수' 컬럼 생성
seoul_age_melted = seoul_age_df.melt(
    id_vars=['행정구역'],
    value_vars=[col for col in seoul_age_df.columns if col.startswith('2025년04월_계_') and '총인구수' not in col and '연령구간인구수' not in col],
    var_name='연령',
    value_name='인구수'
)

# '연령' 컬럼에서 불필요한 prefix 제거 및 정수형으로 변환
# ' 이상'과 '+' 처리를 통합하여 정렬이 잘 되도록 수정
seoul_age_melted['연령_정렬'] = seoul_age_melted['연령'].str.replace('2025년04월_계_', '').str.replace('세', '').str.replace(' 이상', '+')

# '연령_정렬' 컬럼을 숫자로 변환하여 정렬에 사용 (예: '100+'는 1000 등으로 변환)
seoul_age_melted['연령_정렬_값'] = seoul_age_melted['연령_정렬'].apply(lambda x: int(x.replace('+', '1000')) if '+' in x else int(x))

# 막대 그래프 생성
fig = px.bar(
    seoul_age_melted,
    x='연령_정렬', # 정렬을 위해 생성한 컬럼 사용
    y='인구수',
    title='서울특별시 연령별 인구 분포 (2025년 4월)',
    labels={'연령_정렬': '연령', '인구수': '인구수'} # 레이블은 원래대로 '연령'으로 표시
)

# X축 순서 정렬 (숫자 기준으로 정렬되도록)
fig.update_layout(xaxis={'categoryorder':'array', 'categoryarray': sorted(seoul_age_melted['연령_정렬'].unique(), key=lambda x: seoul_age_melted[seoul_age_melted['연령_정렬'] == x]['연령_정렬_값'].iloc[0])})

fig.show()
fig.write_json("seoul_age_distribution.json")
