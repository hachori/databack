import streamlit as st
import yfinance as yf
import plotly.express as px
from datetime import datetime, timedelta

def get_top_global_stocks():
    """
    일반적으로 글로벌 시가총액 상위에 있는 기업들의 티커를 반환합니다.
    (수동으로 선정되었으며, 실시간 시가총액 순위가 아님)
    """
    # 실제 시가총액 Top 10은 변동이 심하므로, 일반적으로 상위에 랭크되는 기업들로 구성
    # 필요에 따라 이 리스트를 수정할 수 있습니다.
    return {
        "Apple": "AAPL",
        "Microsoft": "MSFT",
        "NVIDIA": "NVDA",
        "Amazon": "AMZN",
        "Alphabet (Google) A": "GOOGL",
        "Alphabet (Google) C": "GOOG",
        "Meta Platforms": "META",
        "Tesla": "TSLA",
        "Berkshire Hathaway B": "BRK-B",
        "Eli Lilly and Company": "LLY", # 헬스케어 분야 대표
        # "TSMC": "TSM", # 대만 기업 추가
        # "Saudi Aramco": "2222.SR" # 사우디 아람코는 야후 파이낸스에서 심볼이 다를 수 있음
    }

def fetch_stock_data(tickers, period="1y"):
    """
    야후 파이낸스에서 주식 데이터를 가져옵니다.
    """
    data = yf.download(list(tickers.values()), period=period, progress=False)
    # 'Adj Close' 가격만 사용하고, 컬럼 이름을 티커 이름으로 변경
    df = data['Adj Close']
    df.columns = tickers.keys() # 티커 대신 회사 이름으로 컬럼 이름 변경
    return df

st.set_page_config(layout="wide")
st.title("글로벌 시가총액 Top 기업 주식 변화 (지난 1년)")

st.write(
    """
    이 앱은 Streamlit, Yahoo Finance, Plotly를 사용하여 일반적으로 글로벌 시가총액 상위에 랭크되는 기업들의
    지난 1년간 주식 가격 변화를 시각화합니다.
    """
)

# Top N 기업 가져오기
top_companies = get_top_global_stocks()

st.subheader("데이터를 불러오는 중...")
with st.spinner('데이터를 불러오고 시각화하는 중입니다. 잠시만 기다려 주세요...'):
    try:
        # 데이터 가져오기
        stock_data = fetch_stock_data(top_companies, period="1y")

        if not stock_data.empty:
            # Plotly를 사용하여 라인 차트 생성
            # 데이터를 melt하여 'Date', 'Company', 'Price' 컬럼으로 만듭니다.
            # Plotly Express는 wide-form 데이터도 잘 처리하지만, 명확한 라벨링을 위해 melt할 수 있습니다.
            df_melted = stock_data.reset_index().melt(id_vars=['Date'], var_name='Company', value_name='Price')

            fig = px.line(df_melted, x="Date", y="Price", color="Company",
                          title="글로벌 시가총액 상위 기업 주식 변화 (지난 1년)",
                          labels={"Price": "종가 (USD)"},
                          hover_data={"Price": ":.2f"}) # 호버 시 가격 소수점 둘째 자리까지 표시

            fig.update_layout(
                hovermode="x unified", # X축에 걸쳐 호버 정보를 통합 표시
                xaxis_title="날짜",
                yaxis_title="주가 (USD)",
                legend_title="기업"
            )
            st.plotly_chart(fig, use_container_width=True)
            st.subheader("원시 데이터")
            st.dataframe(stock_data)

        else:
            st.warning("주식 데이터를 가져오지 못했습니다. 티커를 확인하거나 잠시 후 다시 시도해 주세요.")

    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
        st.info("인터넷 연결을 확인하거나, 야후 파이낸스에서 해당 티커의 데이터를 제공하는지 확인해 주세요.")

st.markdown(
    """
    ---
    **참고:**
    * 이 시가총액 Top 기업 리스트는 고정되어 있으며, 실시간 시가총액 순위를 반영하지 않습니다.
    * 데이터는 야후 파이낸스에서 제공됩니다.
    """
)
