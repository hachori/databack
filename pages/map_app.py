import streamlit as st
import folium
from geopy.geocoders import Nominatim
from streamlit_folium import folium_static # Streamlit에 Folium 지도를 띄우기 위함

# 1. 지명으로부터 위도, 경도를 얻는 함수 정의
@st.cache_data # Streamlit 캐싱을 사용하여 API 호출을 줄이고 성능 향상
def get_coordinates(place_name):
    geolocator = Nominatim(user_agent="my-map-app") # user_agent는 고유하게 설정하는 것이 좋습니다.
    try:
        location = geolocator.geocode(place_name)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except Exception as e:
        st.error(f"지명을 찾는 중 오류가 발생했습니다: {e}")
        return None, None

# 2. Streamlit 앱 제목 설정
st.title("🗺️ 지명으로 지도에 핀 찍기")
st.markdown("원하는 지명을 입력하고 지도에서 확인해 보세요!")

# 3. 사용자로부터 지명 입력받기
place_input = st.text_input("지명을 입력하세요 (예: 서울역, N서울타워, 에펠탑)", "서울역")

# 4. 입력 버튼
if st.button("지도에 표시"):
    if place_input:
        latitude, longitude = get_coordinates(place_input)

        if latitude is not None and longitude is not None:
            st.success(f"'{place_input}'의 위도: {latitude}, 경도: {longitude}")

            # 5. Folium 지도 생성 (초기 중심은 입력받은 지명)
            m = folium.Map(location=[latitude, longitude], zoom_start=15)

            # 6. 마커 추가
            folium.Marker(
                [latitude, longitude],
                tooltip=place_input, # 마커 위에 마우스를 올렸을 때 나타나는 텍스트
                popup=f"<b>{place_input}</b><br>위도: {latitude}<br>경도: {longitude}", # 마커 클릭 시 나타나는 팝업
                icon=folium.Icon(color="red", icon="info-sign") # 마커 아이콘 설정
            ).add_to(m)

            # 7. Streamlit에 Folium 지도 표시
            folium_static(m)
        else:
            st.warning("입력하신 지명의 위치를 찾을 수 없습니다. 다시 시도해 주세요.")
    else:
        st.warning("지명을 입력해주세요!")

# 참고: Nominatim은 OpenStreetMap 기반으로, API 호출 빈도에 제한이 있을 수 있습니다.
# 과도한 요청은 차단될 수 있으니 주의하세요.
