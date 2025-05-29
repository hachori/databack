import streamlit as st
import pandas as pd
from datetime import datetime
import random
from streamlit_gsheets import GSheetsConnection

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="✨ 다했어요 현황판! ✨",
    page_icon="🎉",
    layout="centered"
)

# --- CSS 스타일링 (기존 스타일 유지) ---
st.markdown("""
<style>
    .main-header {
        font-size: 3.5em;
        text-align: center;
        color: #FF69B4;
        text-shadow: 2px 2px #FFD700;
        margin-bottom: 30px;
    }
    .sub-header {
        font-size: 2.2em;
        color: #8A2BE2;
        text-align: center;
        margin-top: 40px;
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 15px 30px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 24px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 12px;
        border: 3px solid #388E3C;
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
        border: 2px solid #ADD8E6;
        padding: 10px;
        font-size: 1.2em;
    }
    .stSuccess {
        background-color: #D4EDDA;
        color: #155724;
        border-radius: 10px;
        padding: 15px;
        margin-top: 20px;
        font-size: 1.3em;
        text-align: center;
    }
    .stWarning {
        background-color: #FFF3CD;
        color: #856404;
        border-radius: 10px;
        padding: 15px;
        margin-top: 20px;
        font-size: 1.3em;
        text-align: center;
    }
    .stInfo {
        background-color: #CCE5FF;
        color: #004085;
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
        color: #FF4500;
        font-weight: bold;
    }
    .sync-status {
        background-color: #E8F5E8;
        color: #2E7D32;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        margin: 10px 0;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

# --- 구글 시트 연결 설정 ---
@st.cache_resource
def init_connection():
    try:
        return st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        st.error(f"구글 시트 연결에 실패했습니다: {e}")
        return None

def load_data_from_sheets():
    """구글 시트에서 데이터를 불러오는 함수"""
    try:
        conn = init_connection()
        if conn is None:
            return []
        
        existing_data = conn.read(worksheet="시트1")
        if existing_data.empty:
            return []
        
        # 구글 시트 데이터를 세션 상태 형식으로 변환
        loaded_data = []
        for _, row in existing_data.iterrows():
            try:
                # 시간 문자열을 datetime 객체로 변환
                timestamp = pd.to_datetime(row['완료시간'])
                loaded_data.append({
                    "name": row['이름'],
                    "timestamp": timestamp
                })
            except:
                continue
        
        return loaded_data
    except Exception as e:
        st.warning(f"데이터 로드 중 오류가 발생했습니다: {e}")
        return []

def save_to_sheets(name, timestamp):
    """새로운 완료 기록을 구글 시트에 저장하는 함수"""
    try:
        conn = init_connection()
        if conn is None:
            return False
        
        # 기존 데이터 읽기
        try:
            existing_data = conn.read(worksheet="시트1")
            if existing_data.empty:
                existing_data = pd.DataFrame(columns=['이름', '완료시간', '등록일'])
        except:
            existing_data = pd.DataFrame(columns=['이름', '완료시간', '등록일'])
        
        # 새 데이터 추가
        new_row = pd.DataFrame({
            '이름': [name],
            '완료시간': [timestamp.strftime("%Y-%m-%d %H:%M:%S")],
            '등록일': [timestamp.strftime("%Y-%m-%d")]
        })
        
        # 데이터 합치기
        updated_data = pd.concat([existing_data, new_row], ignore_index=True)
        
        # 구글 시트 업데이트
        conn.update(worksheet="시트1", data=updated_data)
        return True
        
    except Exception as e:
        st.error(f"저장 중 오류가 발생했습니다: {e}")
        return False

# --- 세션 상태 초기화 ---
if 'completed_tasks' not in st.session_state:
    # 구글 시트에서 기존 데이터 로드
    st.session_state.completed_tasks = load_data_from_sheets()

if 'show_name_input' not in st.session_state:
    st.session_state.show_name_input = False

if 'last_sync' not in st.session_state:
    st.session_state.last_sync = datetime.now()

# --- 메인 타이틀 ---
st.markdown("<h1 class='main-header'>✨ 할일 다 했어요! ✨</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2em; color: #555;'>오늘 할 일을 모두 마친 멋진 친구들을 만나보세요!</p>", unsafe_allow_html=True)

# 구글 시트 동기화 상태 표시
st.markdown(f"""
<div class='sync-status'>
    📊 구글 시트와 연동됨 | 마지막 동기화: {st.session_state.last_sync.strftime('%H:%M:%S')}
    <br><a href="https://docs.google.com/spreadsheets/d/1d0z3fyutTRpfRTtYy4yvcjjTtm7lQP5zCIZs0AsUdkc/edit?usp=sharing" target="_blank">📋 구글 시트에서 보기</a>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- '다했어요!' 버튼 섹션 ---
st.markdown("<h2 class='sub-header'>👏 다 했으면 클릭! 👏</h2>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    if st.button("✅ 다했어요!"):
        st.session_state.show_name_input = True
        st.session_state.name_input_key = str(random.random())

with col2:
    if st.session_state.show_name_input:
        name = st.text_input(
            "이름을 입력해주세요. 👇",
            key=st.session_state.name_input_key,
            placeholder="예: 김철수"
        )
        if name:
            # 중복 이름 체크
            if name.strip() not in [item['name'] for item in st.session_state.completed_tasks]:
                current_time = datetime.now()
                
                # 구글 시트에 저장
                if save_to_sheets(name.strip(), current_time):
                    # 세션 상태에도 추가
                    st.session_state.completed_tasks.append({
                        "name": name.strip(),
                        "timestamp": current_time
                    })
                    st.session_state.last_sync = current_time
                    
                    st.success(f"🎉 **{name.strip()}** 친구, 정말 대단해요! 할일을 완료했어요! 구글 시트에도 저장되었어요! 🎉")
                    st.session_state.show_name_input = False
                else:
                    st.error("저장에 실패했습니다. 다시 시도해주세요.")
            else:
                st.warning(f"앗, **{name.strip()}** 친구는 이미 완료했다고 표시했어요! 😊")

# 새로고침 버튼 추가
col_refresh1, col_refresh2, col_refresh3 = st.columns([1, 1, 1])
with col_refresh2:
    if st.button("🔄 데이터 새로고침"):
        st.session_state.completed_tasks = load_data_from_sheets()
        st.session_state.last_sync = datetime.now()
        st.success("데이터를 새로고침했습니다!")
        st.rerun()

st.markdown("---")

# --- 현재까지 완료한 친구들 현황판 ---
st.markdown("<h2 class='sub-header'>🌈 완료한 친구들 현황 🌈</h2>", unsafe_allow_html=True)

if st.session_state.completed_tasks:
    # 데이터프레임 생성
    df = pd.DataFrame(st.session_state.completed_tasks)
    df.columns = ["이름", "완료 시간"]

    # 완료 시간 포맷을 보기 좋게 변경
    df['완료 시간'] = df['완료 시간'].dt.strftime("%Y년 %m월 %d일 %H시 %M분")
    
    # 최신 순으로 정렬
    df = df.sort_values('완료 시간', ascending=False).reset_index(drop=True)

    # 데이터프레임을 예쁘게 스타일링하여 표시
    st.markdown("<div class='dataframe-container'>", unsafe_allow_html=True)
    st.dataframe(
        df.style.set_properties(**{
            'background-color': '#F0F8FF',
            'color': 'black',
            'border-color': '#ADD8E6',
            'font-size': '1.1em'
        }).set_table_styles([
            {'selector': 'th', 'props': [('background-color', '#B0E0E6'), ('color', 'white'), ('font-size', '1.2em')]},
            {'selector': 'td', 'props': [('padding', '10px')]}
        ]),
        hide_index=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # 통계 정보 표시
    total_completed = len(st.session_state.completed_tasks)
    today_completed = len([task for task in st.session_state.completed_tasks 
                          if task['timestamp'].date() == datetime.now().date()])
    
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.metric("📈 총 완료 수", total_completed)
    with col_stat2:
        st.metric("🗓️ 오늘 완료 수", today_completed)

    # 이모지 응원 메시지
    emojis = ["😊", "🥳", "🤩", "👍", "💯", "💖", "🌟", "🎈", "🚀", "🏆", "👏", "✨", "🌈"]
    emoji_message_parts = []
    for item in st.session_state.completed_tasks[-5:]:  # 최근 5명만 표시
        emoji_message_parts.append(f"{item['name']} {random.choice(emojis)}")
    st.markdown(f"<p class='emoji-message'>오늘도 모두 멋진 하루였어요! {' '.join(emoji_message_parts)}</p>", unsafe_allow_html=True)

else:
    st.info("아직 할일을 완료한 친구가 없어요. 첫 번째 친구가 되어보세요! 🚀")

st.markdown("---")

# 관리자 기능 (선택사항)
with st.expander("🔧 관리자 도구"):
    st.write("**주의:** 이 기능들은 신중하게 사용해주세요!")
    
    col_admin1, col_admin2 = st.columns(2)
    
    with col_admin1:
        if st.button("🗑️ 오늘 데이터 초기화"):
            if st.session_state.get('confirm_delete_today', False):
                # 오늘 데이터만 삭제
                st.session_state.completed_tasks = [
                    task for task in st.session_state.completed_tasks 
                    if task['timestamp'].date() != datetime.now().date()
                ]
                st.success("오늘 데이터가 초기화되었습니다.")
                st.session_state.confirm_delete_today = False
                st.rerun()
            else:
                st.session_state.confirm_delete_today = True
                st.warning("정말로 오늘 데이터를 삭제하시겠습니까? 다시 한 번 클릭하세요.")
    
    with col_admin2:
        if st.button("📊 전체 데이터 다시 로드"):
            st.session_state.completed_tasks = load_data_from_sheets()
            st.session_state.last_sync = datetime.now()
            st.success("구글 시트에서 전체 데이터를 다시 로드했습니다!")
            st.rerun()

st.markdown("<p style='text-align: center; font-size: 1.1em; color: #777;'>Made with ❤️ for awesome kids!</p>", unsafe_allow_html=True)
