import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots # 캔들스틱 + 거래량 통합 차트를 위해 필요할 수 있지만, 여기서는 분리하여 사용
import pandas as pd
from datetime import datetime, timedelta

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="글로벌 시가총액 Top 기업 주식 대시보드",
    page_icon="📈",
    layout="wide"
)

st.title("📈 글로벌 시가총액 Top 기업 주식 변화 (최근 1년)")
st.markdown("---")

# --- 2. 글로벌 시가총액 Top 기업 리스트 (예시) ---
# 실제 시가총액 Top 10은 변동이 심하므로, 일반적으로 상위에 랭크되는 기업들로 구성
# 2025년 5월 기준은 예시이며, 필요에 따라 이 리스트를 수정할 수 있습니다.
top_global_companies = {
    'Microsoft': 'MSFT',
    'Apple': 'AAPL',
    'NVIDIA': 'NVDA',
    'Alphabet (Google)': 'GOOGL',
    'Amazon': 'AMZN',
    'Meta Platforms': 'META',
    'Saudi Aramco': '2222.SR', # 사우디 아람코는 야후 파이낸스에서 심볼이 다를 수 있음
    'Berkshire Hathaway': 'BRK-B',
    'Broadcom': 'AVGO',
    'TSMC': 'TSM' # 대만 기업 추가
}

# --- 3. 사이드바 설정 ---
st.sidebar.header("📊 대시보드 설정")
selected_companies_names = st.sidebar.multiselect(
    "분석할 기업을 선택하세요:",
    options=list(top_global_companies.keys()),
    default=list(top_global_companies.keys())[:5] # 기본값으로 상위 5개 선택
)

chart_type = st.sidebar.selectbox(
    "차트 타입 선택:",
    ["라인 차트", "캔들스틱 차트"]
)

show_volume = st.sidebar.checkbox("거래량 차트 표시", value=True)

# --- 4. 데이터 로딩 함수 (캐싱 적용) ---
@st.cache_data(ttl=3600) # 1시간마다 캐시 갱신
def load_stock_data(ticker: str, period: str = "1y") -> pd.DataFrame | None:
    """
    Yahoo Finance에서 특정 티커의 주식 데이터를 로드합니다.
    """
    try:
        # yf.Ticker().history()는 yf.download()보다 더 안정적이고 조정된 데이터를 반환합니다.
        stock = yf.Ticker(ticker)
        # period='1y'는 지난 1년간의 데이터를 의미합니다.
        data = stock.history(period=period)
        if not data.empty:
            return data
        else:
            st.warning(f"'{ticker}'에 대한 데이터를 찾을 수 없거나 비어있습니다.")
            return None
    except Exception as e:
        st.error(f"'{ticker}' 데이터를 불러오는 중 오류 발생: {e}")
        return None

# --- 5. 메인 대시보드 로직 ---
if not selected_companies_names:
    st.warning("분석할 기업을 하나 이상 선택해주세요.")
else:
    # 선택된 기업들의 티커를 딕셔너리 형태로 준비
    selected_tickers = {name: top_global_companies[name] for name in selected_companies_names}

    # 데이터 로딩
    all_stock_data = {}
    with st.spinner("선택된 기업들의 주식 데이터를 불러오는 중입니다..."):
        for company_name, ticker in selected_tickers.items():
            data = load_stock_data(ticker)
            if data is not None:
                all_stock_data[company_name] = data

    if not all_stock_data:
        st.error("선택된 기업들 중 유효한 데이터를 불러올 수 있는 기업이 없습니다. 티커를 확인하거나 잠시 후 다시 시도해 주세요.")
    else:
        # --- 5.1. 성과 요약 테이블 ---
        st.subheader("📊 지난 1년 성과 요약")
        performance_data = []
        for company, data in all_stock_data.items():
            if len(data) > 1: # 시작가와 현재가를 비교하려면 최소 2개 이상의 데이터 필요
                start_price = data['Close'].iloc[0]
                end_price = data['Close'].iloc[-1]
                change_pct = ((end_price - start_price) / start_price) * 100
                performance_data.append({
                    '기업명': company,
                    '시작가': f"${start_price:.2f}",
                    '현재가': f"${end_price:.2f}",
                    '변화율 (1년)': f"{change_pct:.2f}%",
                    '52주 최고가': f"${data['High'].max():.2f}",
                    '52주 최저가': f"${data['Low'].min():.2f}"
                })
        
        if performance_data:
            performance_df = pd.DataFrame(performance_data)
            st.dataframe(performance_df, use_container_width=True, hide_index=True)
        else:
            st.info("성과 요약을 표시할 데이터가 충분하지 않습니다.")

        # --- 5.2. 주가 변화 차트 ---
        st.subheader("📈 주가 변화 차트")
        
        if chart_type == "라인 차트":
            fig_price = go.Figure()
            for company, data in all_stock_data.items():
                fig_price.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name=company))
            
            fig_price.update_layout(
                title="주가 변화 (라인 차트)",
                xaxis_title="날짜",
                yaxis_title="주가 (USD)",
                hovermode='x unified',
                height=500
            )
            st.plotly_chart(fig_price, use_container_width=True)

        elif chart_type == "캔들스틱 차트":
            # 캔들스틱은 보통 개별 종목에 적합하므로, 첫 번째 선택된 기업만 표시
            if all_stock_data and selected_companies_names:
                selected_company_for_candlestick = selected_companies_names[0]
                data = all_stock_data[selected_company_for_candlestick]

                fig_candle = go.Figure(data=[go.Candlestick(
                    x=data.index,
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    name=selected_company_for_candlestick
                )])
                fig_candle.update_layout(
                    title=f"{selected_company_for_candlestick} 캔들스틱 차트",
                    xaxis_title="날짜",
                    yaxis_title="주가 (USD)",
                    height=500
                )
                st.plotly_chart(fig_candle, use_container_width=True)
            else:
                st.info("캔들스틱 차트를 표시할 기업을 선택해주세요.")

        # --- 5.3. 거래량 차트 ---
        if show_volume:
            st.subheader("📊 거래량 변화")
            fig_volume = go.Figure()
            for company, data in all_stock_data.items():
                fig_volume.add_trace(go.Scatter(x=data.index, y=data['Volume'], mode='lines', name=f"{company} 거래량", fill='tozeroy'))
            
            fig_volume.update_layout(
                title="거래량 변화",
                xaxis_title="날짜",
                yaxis_title="거래량",
                hovermode='x unified',
                height=300
            )
            st.plotly_chart(fig_volume, use_container_width=True)

        # --- 5.4. 주가 상관관계 분석 ---
        if len(selected_companies_names) > 1:
            st.subheader("🔗 주가 상관관계 분석")
            price_data_for_corr = pd.DataFrame()
            for company, data in all_stock_data.items():
                # 상관관계 분석을 위해 'Close' 가격만 사용
                price_data_for_corr[company] = data['Close']
            
            # 결측값이 있는 행 제거 (상관관계 계산에 중요)
            price_data_for_corr = price_data_for_corr.dropna()

            if not price_data_for_corr.empty:
                correlation_matrix = price_data_for_corr.corr()
                fig_corr = go.Figure(data=go.Heatmap(
                    z=correlation_matrix.values,
                    x=correlation_matrix.columns,
                    y=correlation_matrix.index,
                    colorscale='RdBu',
                    zmid=0, # 0을 중심으로 색상 스케일 설정
                    text=correlation_matrix.round(2).values, # 텍스트로 값 표시
                    texttemplate="%{text}",
                    textfont={"size": 10}
                ))
                fig_corr.update_layout(
                    title="주가 상관관계 매트릭스",
                    xaxis_title="기업",
                    yaxis_title="기업",
                    height=500,
                    xaxis=dict(side="top") # x축 라벨을 위로 이동
                )
                st.plotly_chart(fig_corr, use_container_width=True)
            else:
                st.info("상관관계 분석을 위한 데이터가 충분하지 않습니다. 선택된 기업들의 데이터가 모두 존재해야 합니다.")
        
        # --- 5.5. 개별 기업 상세 분석 ---
        st.subheader("🏢 개별 기업 상세 분석")
        
        selected_detail_company = st.selectbox(
            "상세 분석할 기업을 선택하세요:",
            options=list(all_stock_data.keys())
        )
        
        if selected_detail_company:
            detail_data = all_stock_data[selected_detail_company].copy() # 원본 데이터 보존을 위해 copy() 사용
            
            # 현재가, 변화율, 52주 최고/최저가, 평균 거래량 메트릭스
            col1, col2, col3, col4 = st.columns(4)
            if len(detail_data) > 1:
                with col1:
                    st.metric(
                        "현재 종가",
                        f"${detail_data['Close'].iloc[-1]:.2f}",
                        f"{((detail_data['Close'].iloc[-1] - detail_data['Close'].iloc[-2]) / detail_data['Close'].iloc[-2] * 100):.2f}%"
                    )
                with col2:
                    st.metric(
                        "52주 최고가",
                        f"${detail_data['High'].max():.2f}"
                    )
                with col3:
                    st.metric(
                        "52주 최저가",
                        f"${detail_data['Low'].min():.2f}"
                    )
                with col4:
                    avg_volume = detail_data['Volume'].mean()
                    st.metric(
                        "평균 거래량",
                        f"{avg_volume:,.0f}"
                    )
            else:
                st.info("선택된 기업의 상세 지표를 표시할 데이터가 부족합니다.")

            # 이동평균선 계산
            detail_data['MA20'] = detail_data['Close'].rolling(window=20).mean()
            detail_data['MA50'] = detail_data['Close'].rolling(window=50).mean()
            
            # 상세 차트 (종가 및 이동평균선)
            fig_detail = go.Figure()
            fig_detail.add_trace(go.Scatter(x=detail_data.index, y=detail_data['Close'], mode='lines', name='종가', line=dict(color='blue', width=2)))
            fig_detail.add_trace(go.Scatter(x=detail_data.index, y=detail_data['MA20'], mode='lines', name='20일 이동평균', line=dict(color='orange', width=1, dash='dot')))
            fig_detail.add_trace(go.Scatter(x=detail_data.index, y=detail_data['MA50'], mode='lines', name='50일 이동평균', line=dict(color='red', width=1, dash='dash')))
            
            fig_detail.update_layout(
                title=f"{selected_detail_company} 상세 차트 (이동평균선 포함)",
                xaxis_title="날짜",
                yaxis_title="주가 (USD)",
                hovermode='x unified',
                height=500
            )
            st.plotly_chart(fig_detail, use_container_width=True)

# --- 6. 푸터 ---
st.markdown("---")
st.markdown(
    """
    **데이터 출처:** Yahoo Finance  
    **업데이트 주기:** 매 시간  
    **기준:** 일반적으로 알려진 글로벌 시가총액 상위 기업들 (실시간 시가총액 순위와 다를 수 있음)
    """
)
