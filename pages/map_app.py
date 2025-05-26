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
st.markdown("원하는 지명을 입력하고 **엔터를 치거나 '지도에 표시' 버튼을 누르세요!**")

# --- 추가/변경된 부분 시작 ---

# 3. Streamlit 세션 상태 초기화
# 세션 상태에 'current_place_input' 키가 없으면 초기값 설정
if 'current_place_input' not in st.session_state:
    st.session_state.current_place_input = "서울역" # 초기 지명

# 4. 입력창 값 변경 시 호출될 콜백 함수
# 이 함수는 텍스트 입력창에 엔터를 쳤을 때 실행됩니다.
def update_place_from_input():
    # 텍스트 입력 위젯의 현재 값으로 세션 상태 업데이트
    st.session_state.current_place_input = st.session_state.text_input_widget

# 5. 사용자로부터 지명 입력받기 (엔터 입력 시 콜백 함수 호출)
place_input_widget = st.text_input(
    "지명을 입력하세요 (예: 서울역, N서울타워, 에펠탑)",
    value=st.session_state.current_place_input, # 세션 상태의 값을 초기값으로 사용
    key="text_input_widget", # 콜백 함수에서 참조할 위젯 키
    on_change=update_place_from_input # 엔터 입력 시 호출될 콜백 함수
)

# 6. '지도에 표시' 버튼
# 버튼 클릭 시에도 동일한 로직이 실행되도록 합니다.
if st.button("지도에 표시"):
    # 버튼 클릭 시에는 현재 입력된 값을 바로 사용
    st.session_state.current_place_input = place_input_widget # 버튼 클릭 시에도 세션 상태 업데이트

# 이제 실제로 지도를 그리는 로직은 st.session_state.current_place_input 값을 사용합니다.
# 이 값은 엔터를 치거나 버튼을 눌렀을 때 업데이트됩니다.
display_place = st.session_state.current_place_input

# --- 추가/변경된 부분 끝 ---

# 7. 지도 표시 로직
if display_place:
    latitude, longitude = get_coordinates(display_place)

    if latitude is not None and longitude is not None:
        st.success(f"'{display_place}'의 위도: {latitude}, 경도: {longitude}")

        # 8. Folium 지도 생성 (초기 중심은 입력받은 지명)
        m = folium.Map(location=[latitude, longitude], zoom_start=15)

        # 9. 마커 추가
        folium.Marker(
            [latitude, longitude],
            tooltip=display_place, # 마커 위에 마우스를 올렸을 때 나타나는 텍스트
            popup=f"<b>{display_place}</b><br>위도: {latitude}<br>경도: {longitude}", # 마커 클릭 시 나타나는 팝업
            icon=folium.Icon(color="red", icon="info-sign") # 마커 아이콘 설정
        ).add_to(m)

        # 10. Streamlit에 Folium 지도 표시
        folium_static(m)
    else:
        st.warning("입력하신 지명의 위치를 찾을 수 없습니다. 다시 시도해 주세요.")
else:
    st.warning("지명을 입력해주세요!")

# 참고: Nominatim은 OpenStreetMap 기반으로, API 호출 빈도에 제한이 있을 수 있습니다.
# 과도한 요청은 차단될 수 있으니 주의하세요.
