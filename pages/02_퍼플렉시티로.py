import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(
    page_title="글로벌 시가총액 Top 10 주식 대시보드",
    page_icon="📈",
    layout="wide"
)

# 제목
st.title("📈 글로벌 시가총액 Top 10 기업 주식 변화 (최근 1년)")
st.markdown("---")

# 글로벌 시가총액 Top 10 기업 (2025년 5월 기준)
top_10_companies = {
    'Microsoft': 'MSFT',
    'Apple': 'AAPL', 
    'NVIDIA': 'NVDA',
    'Alphabet': 'GOOGL',
    'Amazon': 'AMZN',
    'Saudi Aramco': '2222.SR',
    'Meta': 'META',
    'Berkshire Hathaway': 'BRK-B',
    'Broadcom': 'AVGO',
    'TSMC': 'TSM'
}

# 사이드바 설정
st.sidebar.header("📊 설정 옵션")
selected_companies = st.sidebar.multiselect(
    "분석할 기업 선택:",
    options=list(top_10_companies.keys()),
    default=list(top_10_companies.keys())[:5]
)

chart_type = st.sidebar.selectbox(
    "차트 타입:",
    ["라인 차트", "캔들스틱 차트"]
)

show_volume = st.sidebar.checkbox("거래량 표시", value=True)

# 데이터 로딩 함수
@st.cache_data
def load_stock_data(ticker, period="1y"):
    """주식 데이터를 로드하는 함수"""
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period)
        return data
    except:
        return None

# 메인 대시보드
if selected_companies:
    # 데이터 로딩
    stock_data = {}
    for company in selected_companies:
        ticker = top_10_companies[company]
        data = load_stock_data(ticker)
        if data is not None and not data.empty:
            stock_data[company] = data

    if stock_data:
        # 성과 요약 테이블
        st.subheader("📊 성과 요약 (최근 1년)")
        
        performance_data = []
        for company, data in stock_data.items():
            if len(data) > 0:
                start_price = data['Close'].iloc[0]
                end_price = data['Close'].iloc[-1]
                change_pct = ((end_price - start_price) / start_price) * 100
                
                performance_data.append({
                    '기업명': company,
                    '시작가': f"${start_price:.2f}",
                    '현재가': f"${end_price:.2f}",
                    '변화율': f"{change_pct:.2f}%",
                    '최고가': f"${data['High'].max():.2f}",
                    '최저가': f"${data['Low'].min():.2f}"
                })
        
        performance_df = pd.DataFrame(performance_data)
        st.dataframe(performance_df, use_container_width=True)
        
        # 주가 차트
        st.subheader("📈 주가 변화 차트")
        
        if chart_type == "라인 차트":
            # 라인 차트 생성
            fig = go.Figure()
            
            for company, data in stock_data.items():
                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=data['Close'],
                    mode='lines',
                    name=company,
                    line=dict(width=2)
                ))
            
            fig.update_layout(
                title="주가 변화 (라인 차트)",
                xaxis_title="날짜",
                yaxis_title="주가 (USD)",
                height=600,
                hovermode='x unified'
            )
            
        else:
            # 캔들스틱 차트 (첫 번째 선택된 기업만)
            if selected_companies:
                company = selected_companies[0]
                data = stock_data[company]
                
                fig = go.Figure(data=go.Candlestick(
                    x=data.index,
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    name=company
                ))
                
                fig.update_layout(
                    title=f"{company} 캔들스틱 차트",
                    xaxis_title="날짜",
                    yaxis_title="주가 (USD)",
                    height=600
                )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 거래량 차트
        if show_volume and chart_type == "라인 차트":
            st.subheader("📊 거래량 변화")
            
            fig_volume = go.Figure()
            
            for company, data in stock_data.items():
                fig_volume.add_trace(go.Scatter(
                    x=data.index,
                    y=data['Volume'],
                    mode='lines',
                    name=f"{company} 거래량",
                    fill='tonexty' if company != list(stock_data.keys())[0] else 'tozeroy'
                ))
            
            fig_volume.update_layout(
                title="거래량 변화",
                xaxis_title="날짜",
                yaxis_title="거래량",
                height=400
            )
            
            st.plotly_chart(fig_volume, use_container_width=True)
        
        # 상관관계 분석
        if len(selected_companies) > 1:
            st.subheader("🔗 주가 상관관계 분석")
            
            # 상관관계 매트릭스 생성
            price_data = pd.DataFrame()
            for company, data in stock_data.items():
                price_data[company] = data['Close']
            
            correlation_matrix = price_data.corr()
            
            # 히트맵 생성
            fig_corr = go.Figure(data=go.Heatmap(
                z=correlation_matrix.values,
                x=correlation_matrix.columns,
                y=correlation_matrix.index,
                colorscale='RdBu',
                zmid=0,
                text=correlation_matrix.round(3).values,
                texttemplate="%{text}",
                textfont={"size": 10}
            ))
            
            fig_corr.update_layout(
                title="주가 상관관계 매트릭스",
                height=500
            )
            
            st.plotly_chart(fig_corr, use_container_width=True)
        
        # 개별 기업 상세 정보
        st.subheader("🏢 개별 기업 상세 분석")
        
        selected_detail = st.selectbox(
            "상세 분석할 기업 선택:",
            options=selected_companies
        )
        
        if selected_detail:
            detail_data = stock_data[selected_detail]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "현재가",
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
            
            # 이동평균선 추가
            detail_data['MA20'] = detail_data['Close'].rolling(window=20).mean()
            detail_data['MA50'] = detail_data['Close'].rolling(window=50).mean()
            
            fig_detail = go.Figure()
            
            fig_detail.add_trace(go.Scatter(
                x=detail_data.index,
                y=detail_data['Close'],
                mode='lines',
                name='종가',
                line=dict(color='blue', width=2)
            ))
            
            fig_detail.add_trace(go.Scatter(
                x=detail_data.index,
                y=detail_data['MA20'],
                mode='lines',
                name='20일 이동평균',
                line=dict(color='orange', width=1)
            ))
            
            fig_detail.add_trace(go.Scatter(
                x=detail_data.index,
                y=detail_data['MA50'],
                mode='lines',
                name='50일 이동평균',
                line=dict(color='red', width=1)
            ))
            
            fig_detail.update_layout(
                title=f"{selected_detail} 상세 차트 (이동평균선 포함)",
                xaxis_title="날짜",
                yaxis_title="주가 (USD)",
                height=500
            )
            
            st.plotly_chart(fig_detail, use_container_width=True)
    
    else:
        st.error("선택된 기업들의 데이터를 불러올 수 없습니다.")

else:
    st.warning("분석할 기업을 선택해주세요.")

# 푸터
st.markdown("---")
st.markdown(
    """
    **데이터 출처:** Yahoo Finance  
    **업데이트:** 실시간  
    **기준:** 2025년 5월 글로벌 시가총액 Top 10 기업
    """
)
