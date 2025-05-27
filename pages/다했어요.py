import streamlit as st
import pandas as pd
from datetime import datetime
import random

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="✨ 다했어요 현황판! ✨",  # 브라우저 탭에 표시될 제목
    page_icon="🎉",  # 브라우저 탭에 표시될 아이콘
    layout="centered"  # 페이지 레이아웃 (wide 또는 centered)
)

# --- CSS 스타일링 (이모지 및 텍스트 강조) ---
st.markdown("""
<style>
    .main-header {
        font-size: 3.5em;
        text-align: center;
        color: #FF69B4; /* 핑크색 */
        text-shadow: 2px 2px #FFD700; /* 금색 그림자 */
        margin-bottom: 30px;
    }
    .sub-header {
        font-size: 2.2em;
        color: #8A2BE2; /* 보라색 */
        text-align: center;
        margin-top: 40px;
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #4CAF50; /* 초록색 */
        color: white;
        padding: 15px 30px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 24px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 12px;
        border: 3px solid #388E3C; /* 진한 초록색 테두리 */
        box-shadow: 0 9px #999;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: #45a049;
        box-shadow: 0 5px #666;
        transform: translateY(4px);
    }
    .stButton>button:active {
        background-color: #3e8e41;
        box-shadow: 0 3px #666;
        transform: translateY(6px);
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
        border: 2px solid #ADD8E6; /* 연한 파란색 테두리 */
        padding: 10px;
        font-size: 1.2em;
    }
    .stSuccess {
        background-color: #D4EDDA; /* 연한 초록색 배경 */
        color: #155724; /* 진한 초록색 글씨 */
        border-radius: 10px;
        padding: 15px;
        margin-top: 20px;
        font-size: 1.3em;
        text-align: center;
    }
    .stWarning {
        background-color: #FFF3CD; /* 연한 노란색 배경 */
        color: #856404; /* 진한 노란색 글씨 */
        border-radius: 10px;
        padding: 15px;
        margin-top: 20px;
        font-size: 1.3em;
        text-align: center;
    }
    .stInfo {
        background-color: #CCE5FF; /* 연한 파란색 배경 */
        color: #004085; /* 진한 파란색 글씨 */
        border-radius: 10px;
        padding: 15px;
        margin-top: 20px;
        font-size: 1.3em;
        text-align: center;
    }
    .dataframe-container {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        margin-top: 30px;
    }
    .emoji-message {
        font-size: 1.5em;
        text-align: center;
        margin-top: 20px;
        color: #FF4500; /* 주황색 */
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 세션 상태 초기화 (데이터 저장) ---
# 'completed_tasks' 리스트에 완료한 친구들의 이름과 시간을 저장합니다.
if 'completed_tasks' not in st.session_state:
    st.session_state.completed_tasks = []
# 'show_name_input'은 이름 입력 필드를 보여줄지 말지를 결정합니다.
if 'show_name_input' not in st.session_state:
    st.session_state.show_name_input = False

# --- 메인 타이틀 ---
st.markdown("<h1 class='main-header'>✨ 숙제 다 했어요! 현황판 ✨</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2em; color: #555;'>오늘 할 일을 모두 마친 멋진 친구들을 만나보세요!</p>", unsafe_allow_html=True)
st.markdown("---") # 구분선

# --- '다했어요!' 버튼 섹션 ---
st.markdown("<h2 class='sub-header'>👏 다 했으면 클릭! 👏</h2>", unsafe_allow_html=True)

# 버튼과 이름 입력 필드를 위한 컬럼 분할
col1, col2 = st.columns([1, 2])

with col1:
    # '다했어요!' 버튼
    if st.button("✅ 다했어요!"):
        st.session_state.show_name_input = True # 버튼 클릭 시 이름 입력 필드 표시
        st.session_state.name_input_key = str(random.random()) # 이름 입력 필드 초기화를 위한 고유 키

with col2:
    if st.session_state.show_name_input:
        # 이름 입력 필드
        name = st.text_input(
            "이름을 입력해주세요. 👇",
            key=st.session_state.name_input_key, # 고유 키를 사용하여 입력 필드 초기화
            placeholder="예: 김철수"
        )
        if name:
            # 중복 이름 체크
            if name.strip() not in [item['name'] for item in st.session_state.completed_tasks]:
                # 새로운 완료 기록 추가
                st.session_state.completed_tasks.append({
                    "name": name.strip(),
                    "timestamp": datetime.now()
                })
                st.success(f"🎉 **{name.strip()}** 친구, 정말 대단해요! 숙제를 완료했어요! 🎉")
                st.session_state.show_name_input = False # 입력 후 필드 숨기기
            else:
                st.warning(f"앗, **{name.strip()}** 친구는 이미 완료했다고 표시했어요! 😊")
                # st.session_state.show_name_input = False # 중복 시에도 필드 숨기기
        # 이름 입력 필드가 활성화된 상태에서 '다했어요!' 버튼을 다시 누르면 이름 입력 필드 초기화
        # 이 부분은 필요에 따라 주석 처리하거나 제거할 수 있습니다.
        # if st.session_state.show_name_input and not name:
        #     st.session_state.name_input_key = str(random.random())

st.markdown("---") # 구분선

# --- 현재까지 완료한 친구들 현황판 ---
st.markdown("<h2 class='sub-header'>🌈 완료한 친구들 현황 🌈</h2>", unsafe_allow_html=True)

if st.session_state.completed_tasks:
    # 데이터프레임 생성
    df = pd.DataFrame(st.session_state.completed_tasks)
    df.columns = ["이름", "완료 시간"] # 컬럼 이름 설정

    # 완료 시간 포맷을 보기 좋게 변경
    df['완료 시간'] = df['완료 시간'].dt.strftime("%Y년 %m월 %d일 %H시 %M분")

    # 데이터프레임을 예쁘게 스타일링하여 표시
    st.markdown("<div class='dataframe-container'>", unsafe_allow_html=True)
    st.dataframe(
        df.style.set_properties(**{
            'background-color': '#F0F8FF', # 연한 하늘색 배경
            'color': 'black',
            'border-color': '#ADD8E6', # 연한 파란색 테두리
            'font-size': '1.1em'
        }).set_table_styles([
            {'selector': 'th', 'props': [('background-color', '#B0E0E6'), ('color', 'white'), ('font-size', '1.2em')]}, # 헤더 스타일
            {'selector': 'td', 'props': [('padding', '10px')]} # 셀 패딩
        ]),
        hide_index=True # 인덱스 숨기기
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # 이모지 응원 메시지
    emojis = ["😊", "🥳", "🤩", "👍", "💯", "💖", "🌟", "🎈", "🚀", "🏆", "👏", "✨", "🌈"]
    # 완료한 친구들의 이름과 함께 랜덤 이모지 표시
    emoji_message_parts = []
    for i, item in enumerate(st.session_state.completed_tasks):
        emoji_message_parts.append(f"{item['name']} {random.choice(emojis)}")
    st.markdown(f"<p class='emoji-message'>오늘도 모두 멋진 하루였어요! {' '.join(emoji_message_parts)}</p>", unsafe_allow_html=True)

else:
    st.info("아직 숙제를 완료한 친구가 없어요. 첫 번째 친구가 되어보세요! 🚀")

st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 1.1em; color: #777;'>Made with ❤️ for awesome kids!</p>", unsafe_allow_html=True)
