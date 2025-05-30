import streamlit as st
import pandas as pd
from datetime import datetime
import random
from streamlit_gsheets import GSheetsConnection # streamlit-gsheets

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
@st.cache_resource # 연결 객체 캐싱
def init_connection():
    """구글 시트 연결 객체를 초기화하고 반환합니다."""
    try:
        return st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        st.error(f"구글 시트 연결 설정에 실패했습니다: {e}")
        st.error("'.streamlit/secrets.toml' 파일에 올바른 'gsheets' 연결 정보가 있는지 확인해주세요.")
        return None

def load_data_from_sheets():
    """구글 시트에서 데이터를 불러오는 함수"""
    try:
        conn = init_connection()
        if conn is None:
            return [] # 연결 실패 시 빈 리스트 반환
        
        # ttl=0으로 설정하여 캐시를 사용하지 않고 항상 최신 데이터를 읽어옴
        df = conn.read(worksheet="시트1", ttl=0) 

        if df.empty:
            return []

        required_columns = ['이름', '완료시간']
        if not all(col in df.columns for col in required_columns):
            st.warning(
                f"시트에서 필수 컬럼({', '.join(required_columns)}) 중 일부를 찾을 수 없습니다. "
                "데이터를 올바르게 로드할 수 없습니다. 시트에 '이름', '완료시간' 컬럼이 있는지 확인해주세요."
            )
            return [] # 필수 컬럼 없으면 빈 리스트 반환
            
        loaded_entries = []
        for index, row in df.iterrows():
            name = row.get('이름', '알 수 없음') # 이름이 없는 경우 대비
            time_str = row.get('완료시간', None) # 완료시간이 없는 경우 대비

            if time_str is None:
                st.warning(f"이름 '{name}'의 '완료시간' 데이터가 없습니다. 이 항목은 건너뜁니다.")
                continue
            try:
                timestamp = pd.to_datetime(time_str)
                if pd.isna(timestamp): # NaT (Not a Time)인 경우
                    st.warning(f"이름 '{name}'의 완료시간 '{time_str}'을 올바른 날짜 형식으로 변환할 수 없습니다. 이 항목은 건너뜁니다.")
                    continue
                loaded_entries.append({"name": str(name), "timestamp": timestamp})
            except Exception as e:
                st.warning(f"이름 '{name}', 완료시간 '{time_str}' 처리 중 오류 발생: {e}. 이 항목은 건너뜁니다.")
                continue
        return loaded_entries
    except Exception as e:
        st.error(f"구글 시트에서 데이터를 불러오는 중 예외가 발생했습니다: {e}")
        return []

def save_to_sheets(name, timestamp):
    """새로운 완료 기록을 구글 시트에 저장하는 함수"""
    try:
        conn = init_connection()
        if conn is None:
            return False # 연결 실패 시 False 반환

        # 기존 데이터 읽기 (ttl=0으로 캐시 비활성화)
        try:
            # conn.read는 worksheet가 없으면 에러를 발생시키지 않고 빈 DataFrame을 반환할 수 있음.
            # 또는 gspread.exceptions.WorksheetNotFound 발생 가능.
            existing_data = conn.read(worksheet="시트1", ttl=0)
            # 컬럼이 정상적으로 있는지 확인
            expected_columns = ['이름', '완료시간', '등록일']
            if existing_data.empty or not all(col in existing_data.columns for col in expected_columns):
                # 시트가 비어있거나, 컬럼이 제대로 설정되지 않은 경우
                existing_data = pd.DataFrame(columns=expected_columns)
        except Exception as e: # WorksheetNotFound 등
            st.info(f"기존 '시트1'을 읽는 중 정보: {e}. 새 시트 또는 빈 데이터프레임으로 진행합니다.")
            existing_data = pd.DataFrame(columns=['이름', '완료시간', '등록일'])
        
        # 새 데이터 추가
        new_row = pd.DataFrame({
            '이름': [name],
            '완료시간': [timestamp.strftime("%Y-%m-%d %H:%M:%S")],
            '등록일': [timestamp.strftime("%Y-%m-%d")] # 오늘 날짜 (문자열)
        })
        
        # 데이터 합치기 (기존 데이터가 비어있어도 정상 작동)
        updated_data = pd.concat([existing_data, new_row], ignore_index=True)
        
        # 구글 시트 업데이트 (conn.update는 시트 전체를 덮어씀)
        conn.update(worksheet="시트1", data=updated_data)
        return True
        
    except Exception as e:
        st.error(f"구글 시트에 저장 중 오류가 발생했습니다: {e}")
        return False

# --- 세션 상태 초기화 ---
if 'completed_tasks' not in st.session_state:
    st.session_state.completed_tasks = load_data_from_sheets()

if 'show_name_input' not in st.session_state:
    st.session_state.show_name_input = False

if 'last_sync' not in st.session_state:
    st.session_state.last_sync = datetime.now()

# --- 메인 타이틀 ---
st.markdown("<h1 class='main-header'>✨ 할일 다 했어요! ✨</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2em; color: #555;'>오늘 할 일을 모두 마친 멋진 친구들을 만나보세요!</p>", unsafe_allow_html=True)

# 구글 시트 동기화 상태 표시
# 실제 구글 시트 링크로 변경해주세요. (예시 링크 사용)
GOOGLE_SHEET_LINK = "https://docs.google.com/spreadsheets/d/1d0z3fyutTRpfRTtYy4yvcjjTtm7lQP5zCIZs0AsUdkc/edit?usp=sharing"
# secrets.toml에 설정된 스프레드시트 ID를 여기에 직접 넣거나, 다른 방식으로 관리할 수 있습니다.
# 예시로, st.secrets["connections"]["gsheets"]["spreadsheet"] 를 파싱하여 URL 생성 가능
try:
    spreadsheet_id = st.secrets.get("connections", {}).get("gsheets", {}).get("spreadsheet")
    if spreadsheet_id and "docs.google.com" not in spreadsheet_id: # ID만 있는 경우
         GOOGLE_SHEET_LINK = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit?usp=sharing"
    elif spreadsheet_id and "docs.google.com" in spreadsheet_id: # 전체 URL인 경우
        GOOGLE_SHEET_LINK = spreadsheet_id
except Exception:
    pass # secrets 접근 실패 시 기본 링크 사용


st.markdown(f"""
<div class='sync-status'>
    📊 구글 시트와 연동됨 | 마지막 동기화: {st.session_state.last_sync.strftime('%Y-%m-%d %H:%M:%S')}
    <br><a href="{GOOGLE_SHEET_LINK}" target="_blank">📋 구글 시트에서 보기</a>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- '다했어요!' 버튼 섹션 ---
st.markdown("<h2 class='sub-header'>👏 다 했으면 클릭! 👏</h2>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    if st.button("✅ 다했어요!"):
        st.session_state.show_name_input = True
        st.session_state.name_input_key = str(random.random()) # 입력 필드 초기화를 위한 키 변경

with col2:
    if st.session_state.show_name_input:
        name = st.text_input(
            "이름을 입력해주세요. 👇",
            key=st.session_state.get('name_input_key', 'default_name_input'), # 키 존재 확인
            placeholder="예: 김철수"
        )
        if name:
            clean_name = name.strip()
            # 중복 이름 체크 (세션 상태 기준)
            if clean_name not in [item['name'] for item in st.session_state.completed_tasks]:
                current_time = datetime.now()
                
                # 구글 시트에 저장
                if save_to_sheets(clean_name, current_time):
                    # 세션 상태에도 추가
                    st.session_state.completed_tasks.append({
                        "name": clean_name,
                        "timestamp": current_time
                    })
                    st.session_state.last_sync = current_time
                    
                    st.success(f"🎉 **{clean_name}** 친구, 정말 대단해요! 할일을 완료했어요! 구글 시트에도 저장되었어요! 🎉")
                    st.balloons()
                    st.session_state.show_name_input = False # 성공 후 입력창 숨김
                    # st.experimental_rerun() # 필요시 사용 (입력창을 확실히 닫기 위해)
                else:
                    st.error("저장에 실패했습니다. 네트워크 연결을 확인하거나 잠시 후 다시 시도해주세요.")
            else:
                st.warning(f"앗, **{clean_name}** 친구는 이미 완료했다고 표시했어요! 😊")
                st.session_state.show_name_input = False # 중복 시 입력창 숨김

# 새로고침 버튼 추가
col_refresh1, col_refresh2, col_refresh3 = st.columns([1, 1, 1]) # 중앙 정렬을 위해 3개 컬럼 사용
with col_refresh2: # 가운데 컬럼에 버튼 배치
    if st.button("🔄 데이터 새로고침"):
        st.session_state.completed_tasks = load_data_from_sheets()
        st.session_state.last_sync = datetime.now()
        st.success("데이터를 새로고침했습니다!")
        st.rerun()

st.markdown("---")

# --- 현재까지 완료한 친구들 현황판 ---
st.markdown("<h2 class='sub-header'>🌈 완료한 친구들 현황 🌈</h2>", unsafe_allow_html=True)

if st.session_state.completed_tasks:
    df_display = pd.DataFrame(st.session_state.completed_tasks)
    # DataFrame 컬럼명 변경 (표시용)
    df_display.columns = ["이름", "완료 시간"] 

    df_display['완료 시간'] = pd.to_datetime(df_display['완료 시간']).dt.strftime("%Y년 %m월 %d일 %H시 %M분")
    
    df_display = df_display.sort_values(by='완료 시간', ascending=False).reset_index(drop=True)

    st.markdown("<div class='dataframe-container'>", unsafe_allow_html=True)
    st.dataframe(
        df_display.style.set_properties(**{
            'background-color': '#F0F8FF',
            'color': 'black',
            'border-color': '#ADD8E6',
            'font-size': '1.1em'
        }).set_table_styles([
            {'selector': 'th', 'props': [('background-color', '#B0E0E6'), ('color', 'black'), ('font-size', '1.2em')]}, # 헤더 텍스트 색상 변경
            {'selector': 'td', 'props': [('padding', '10px')]}
        ]),
        hide_index=True,
        use_container_width=True # 컨테이너 너비에 맞춤
    )
    st.markdown("</div>", unsafe_allow_html=True)

    total_completed = len(st.session_state.completed_tasks)
    today_completed_tasks = [
        task for task in st.session_state.completed_tasks 
        if task['timestamp'].date() == datetime.now().date()
    ]
    today_completed = len(today_completed_tasks)
    
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.metric("📈 총 완료 수", total_completed)
    with col_stat2:
        st.metric("🗓️ 오늘 완료 수", today_completed)

    emojis = ["😊", "🥳", "🤩", "👍", "💯", "💖", "🌟", "🎈", "🚀", "🏆", "👏", "✨", "🌈"]
    if today_completed_tasks:
        emoji_message_parts = []
        # 최근 5명의 오늘 완료자 또는 전체 오늘 완료자 중 적은 쪽
        for item in today_completed_tasks[:5]: 
            emoji_message_parts.append(f"{item['name']} {random.choice(emojis)}")
        st.markdown(f"<p class='emoji-message'>오늘도 멋진 하루! {' '.join(emoji_message_parts)}</p>", unsafe_allow_html=True)
    elif total_completed > 0:
         st.markdown(f"<p class='emoji-message'>모두 잘하고 있어요! {random.choice(emojis)}</p>", unsafe_allow_html=True)


else:
    st.info("아직 할일을 완료한 친구가 없어요. 첫 번째 친구가 되어보세요! 🚀")

st.markdown("---")

# 관리자 기능
with st.expander("🔧 관리자 도구"):
    st.write("**주의:** 이 기능들은 구글 시트의 데이터를 직접 변경합니다. 신중하게 사용해주세요!")
    
    col_admin1, col_admin2 = st.columns(2)
    
    with col_admin1:
        if st.button("🗑️ 오늘 데이터 초기화 (시트 반영)"):
            if st.session_state.get('confirm_delete_today', False):
                try:
                    conn = init_connection()
                    if conn:
                        # 1. 구글 시트에서 현재 데이터 읽기 (ttl=0으로 항상 최신 데이터)
                        gsheet_df = conn.read(worksheet="시트1", ttl=0)
                        data_to_keep_df = pd.DataFrame(columns=['이름', '완료시간', '등록일']) # 기본 빈 데이터프레임

                        if not gsheet_df.empty:
                            today_date_obj = datetime.now().date()
                            # '등록일' 컬럼이 있는지 확인
                            if '등록일' in gsheet_df.columns:
                                # '등록일' 컬럼 값(문자열)을 날짜 객체로 변환 시도 후 비교
                                temp_date_series = pd.to_datetime(gsheet_df['등록일'], errors='coerce').dt.date
                                data_to_keep_df = gsheet_df[temp_date_series != today_date_obj]
                            elif '완료시간' in gsheet_df.columns:
                                st.info("'등록일' 컬럼이 없어 '완료시간' 기준으로 초기화합니다.")
                                temp_timestamp_series = pd.to_datetime(gsheet_df['완료시간'], errors='coerce').dt.date
                                data_to_keep_df = gsheet_df[temp_timestamp_series != today_date_obj]
                            else: # 필수 날짜 컬럼이 없는 경우
                                st.warning("날짜 정보를 포함하는 '등록일' 또는 '완료시간' 컬럼이 시트에 없어 초기화를 진행할 수 없습니다.")
                                data_to_keep_df = gsheet_df # 변경 없이 유지
                        
                        # 2. 필터링된 데이터로 구글 시트 업데이트
                        # data_to_keep_df가 비어있어도 컬럼 정보는 유지하여 헤더가 써지도록 함
                        if data_to_keep_df.empty and not all(c in data_to_keep_df.columns for c in ['이름', '완료시간', '등록일']):
                             data_to_keep_df = pd.DataFrame(columns=['이름', '완료시간', '등록일'])

                        conn.update(worksheet="시트1", data=data_to_keep_df)
                        
                        # 3. 세션 상태도 업데이트
                        st.session_state.completed_tasks = [
                            task for task in st.session_state.completed_tasks 
                            if task['timestamp'].date() != today_date_obj
                        ]
                        st.session_state.last_sync = datetime.now()
                        st.success("오늘 데이터가 구글 시트와 앱에서 초기화되었습니다.")
                    else:
                        st.error("구글 시트 연결에 실패하여 초기화할 수 없습니다.")
                except Exception as e:
                    st.error(f"오늘 데이터 초기화 중 오류 발생: {e}")
                finally:
                    st.session_state.confirm_delete_today = False
                    st.rerun()
            else:
                st.session_state.confirm_delete_today = True
                st.warning("정말로 오늘 데이터를 삭제하시겠습니까? 이 작업은 구글 시트의 데이터를 영구적으로 변경합니다. 다시 한 번 클릭하여 확인하세요.")
                st.rerun() # 경고 후 버튼 상태 유지를 위해
    
    with col_admin2:
        if st.button("🔄 전체 데이터 다시 로드 (시트 기준)"):
            st.session_state.completed_tasks = load_data_from_sheets() # 시트에서 다시 로드
            st.session_state.last_sync = datetime.now()
            st.success("구글 시트에서 전체 데이터를 다시 로드했습니다!")
            st.rerun()

st.markdown("<p style='text-align: center; font-size: 1.1em; color: #777;'>Made with ❤️ for awesome kids!</p>", unsafe_allow_html=True)
