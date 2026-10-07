import streamlit as st
from ai_helper import ask_ai
import json
import os
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="내 취향은 누구지?",
    page_icon="💕",
    layout="centered"
)

# CSS 스타일 적용 (핑크 배경 + 하트 애니메이션)
st.markdown("""
    <style>
    /* 배경 색상 */
    .stApp {
        background: linear-gradient(135deg, #ffe0ec 0%, #ffb3d9 100%);
        min-height: 100vh;
    }

    /* 하트 애니메이션 */
    @keyframes falling-hearts {
        0% {
            transform: translateY(-10vh) rotate(0deg);
            opacity: 1;
        }
        100% {
            transform: translateY(100vh) rotate(360deg);
            opacity: 0;
        }
    }

    .heart-animation {
        position: fixed;
        pointer-events: none;
        font-size: 2rem;
        animation: falling-hearts 6s infinite linear;
    }

    /* 메인 컨테이너 스타일 */
    .main {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(255, 105, 180, 0.2);
    }

    /* 버튼 스타일 */
    .stButton > button {
        background-color: #ff69b4;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background-color: #ff1493;
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(255, 20, 147, 0.3);
    }

    /* 선택된 버튼 스타일 */
    .selected-button {
        background-color: #ff1493 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 하트 애니메이션 자바스크립트
st.markdown("""
    <script>
    // 하트 애니메이션 생성
    function createFallingHearts() {
        setInterval(() => {
            const heart = document.createElement('div');
            heart.textContent = '💕';
            heart.style.position = 'fixed';
            heart.style.pointerEvents = 'none';
            heart.style.fontSize = '2rem';
            heart.style.left = Math.random() * window.innerWidth + 'px';
            heart.style.top = '-30px';
            heart.style.animation = `falling-hearts ${4 + Math.random() * 3}s linear forwards`;
            document.body.appendChild(heart);

            setTimeout(() => heart.remove(), 7000);
        }, 500);
    }

    // 페이지 로드 시 하트 애니메이션 시작
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createFallingHearts);
    } else {
        createFallingHearts();
    }
    </script>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'selected_personality' not in st.session_state:
    st.session_state.selected_personality = None
if 'selected_mood' not in st.session_state:
    st.session_state.selected_mood = None
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = None
if 'loading' not in st.session_state:
    st.session_state.loading = False

# 제목
st.title("💕 내 취향은 누구지?")
st.markdown("---")

# 소개
st.markdown("""
당신의 성격과 기분을 알려주면, AI가 당신과 잘 맞는 사람을 추천해드립니다! 💫
""")

# 성격 선택 섹션
st.subheader("1️⃣ 당신의 성격을 선택해주세요")
personality_options = ["밝고 긍정적", "침착하고 차분", "감정적이고 감수성 있음", "재미있고 활발함", "차갑고 논리적"]

col1, col2, col3 = st.columns(3)
cols = [col1, col2, col3]

for idx, personality in enumerate(personality_options):
    with cols[idx % 3]:
        if st.button(personality, key=f"personality_{idx}", use_container_width=True):
            st.session_state.selected_personality = personality

if st.session_state.selected_personality:
    st.success(f"✅ 선택됨: {st.session_state.selected_personality}")

st.markdown("")

# 기분 선택 섹션
st.subheader("2️⃣ 평소 기분을 선택해주세요")
mood_options = ["행복함", "외로움", "설렘", "피로함", "무표정함"]

col1, col2, col3 = st.columns(3)
cols = [col1, col2, col3]

for idx, mood in enumerate(mood_options):
    with cols[idx % 3]:
        if st.button(mood, key=f"mood_{idx}", use_container_width=True):
            st.session_state.selected_mood = mood

if st.session_state.selected_mood:
    st.success(f"✅ 선택됨: {st.session_state.selected_mood}")

st.markdown("")
st.markdown("---")

# 추천 버튼
if st.session_state.selected_personality and st.session_state.selected_mood:
    if st.button("💫 내 취향의 사람을 찾아주세요!", use_container_width=True):
        st.session_state.loading = True

        # AI 프롬프트 작성
        prompt = f"""You must respond with ONLY valid JSON. No explanations, no markdown, no code blocks. Just raw JSON.

성격: {st.session_state.selected_personality}
기분: {st.session_state.selected_mood}

이 사람과 잘 맞는 5명의 가상의 인물을 JSON으로 생성하세요.

Required JSON structure (no variations):
{{"recommendations": [{{"name": "Korean name", "age": 25, "personality": "personality traits", "interests": "shared interests", "activities": ["activity1", "activity2", "activity3"]}}]}}

Generate exactly 5 people in the recommendations array. ONLY output the JSON object, nothing else."""

        with st.spinner("AI가 당신과 잘 맞는 사람을 찾고 있습니다... 💭"):
            try:
                # AI 호출
                response = ask_ai(prompt)

                # JSON 파싱
                recommendations_data = json.loads(response)
                st.session_state.recommendations = recommendations_data.get('recommendations', [])
                st.session_state.loading = False
            except json.JSONDecodeError as e:
                st.error(f"❌ JSON 파싱 오류: {str(e)}")
                st.session_state.loading = False
                st.stop()
            except Exception as e:
                st.error(f"❌ 오류 발생: {str(e)}")
                st.session_state.loading = False

# 추천 결과 표시
if st.session_state.recommendations:
    st.markdown("---")
    st.subheader("🎯 당신과 잘 맞는 사람들")

    for idx, person in enumerate(st.session_state.recommendations, 1):
        with st.container():
            col1, col2 = st.columns([1, 3])

            with col1:
                st.markdown(f"### 💑 #{idx}")

            with col2:
                st.markdown(f"### {person.get('name', 'N/A')} ({person.get('age', 'N/A')}세)")

            # 성격 특징
            st.markdown(f"**성격**: {person.get('personality', 'N/A')}")

            # 공통 관심사
            st.markdown(f"**공통 관심사**: {person.get('interests', 'N/A')}")

            # 함께 하면 좋을 활동
            st.markdown("**함께 하면 좋은 활동** 🎉")
            activities = person.get('activities', [])
            for activity in activities:
                st.markdown(f"  • {activity}")

            st.markdown("")

    # 저장 및 다시 선택 버튼
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    # 결과를 저장할 데이터 구성
    save_data = {
        "성격": st.session_state.selected_personality,
        "기분": st.session_state.selected_mood,
        "추천_날짜": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "추천_결과": st.session_state.recommendations
    }
    json_str = json.dumps(save_data, ensure_ascii=False, indent=2)

    with col1:
        st.download_button(
            label="📥 JSON 다운로드",
            data=json_str,
            file_name=f"추천_결과_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

    with col2:
        if st.button("💾 로컬에 저장", use_container_width=True):
            # saved_recommendations 폴더 생성
            os.makedirs("saved_recommendations", exist_ok=True)

            # 파일 저장
            filename = f"saved_recommendations/추천_결과_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)

            st.success(f"✅ 저장 완료!\n📁 위치: {os.path.abspath(filename)}")

    with col3:
        if st.button("🔄 다시 선택하기", use_container_width=True):
            st.session_state.selected_personality = None
            st.session_state.selected_mood = None
            st.session_state.recommendations = None
            st.rerun()

elif st.session_state.loading:
    st.info("⏳ 처리 중입니다...")

else:
    if st.session_state.selected_personality and st.session_state.selected_mood:
        st.info("💫 위의 버튼을 클릭하여 추천을 받아보세요!")
    else:
        st.info("👆 성격과 기분을 먼저 선택해주세요!")
