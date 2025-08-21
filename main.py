import streamlit as st

st.set_page_config(page_title="MBTI 직업 추천", page_icon="💖", layout="centered")

# ---------- 페이지 상단 ----------
st.markdown(
    """
    <h1 style='text-align: center; color: #FF69B4; font-family: "Comic Sans MS", cursive;'>
        ✨ MBTI로 보는 찰떡 직업 추천 ✨
    </h1>
    <p style='text-align: center; color: #FF1493; font-size:18px;'>
        귀여운 MBTI별 직업 추천! 나에게 맞는 진로를 찾아볼까요? 🌈
    </p>
    <hr style='border: 2px solid #FFB6C1;'>
    """,
    unsafe_allow_html=True
)

# ---------- 직업 데이터 ----------
job_dict = {
    "INTJ": ["데이터 과학자", "경영 전략가", "AI 연구원", "변리사", "건축가"],
    "INTP": ["프로그래머", "시스템 설계자", "연구원", "발명가", "UX 엔지니어"],
    "ENTJ": ["CEO", "변호사", "투자은행가", "프로젝트 매니저", "경영 컨설턴트"],
    "ENTP": ["스타트업 창업가", "마케팅 전문가", "제품 매니저", "혁신 연구원", "VC"],
    "INFJ": ["상담사", "심리학자", "작가", "교사", "사회복지사"],
    "INFP": ["작가", "콘텐츠 크리에이터", "언론인", "예술가", "인권 활동가"],
    "ENFJ": ["교육자", "HR 담당자", "외교관", "리더십 코치", "사회운동가"],
    "ENFP": ["광고 기획자", "홍보 전문가", "예능 PD", "창작자", "이벤트 기획자"],
    "ISTJ": ["회계사", "공무원", "군인", "법률 사무관", "품질관리 전문가"],
    "ISFJ": ["간호사", "초등교사", "행정직", "사회복지사", "비서"],
    "ESTJ": ["기업 관리자", "금융분석가", "운영 관리자", "공공기관 관리자", "경찰"],
    "ESFJ": ["HR 담당자", "초중고 교사", "병원 코디네이터", "영업 관리", "사회사업가"],
    "ISTP": ["기계 엔지니어", "파일럿", "자동차 정비사", "보안 전문가", "프로게이머"],
    "ISFP": ["패션 디자이너", "사진작가", "음악가", "요리사", "플로리스트"],
    "ESTP": ["세일즈 전문가", "창업가", "부동산 투자자", "스포츠 에이전트", "트레이너"],
    "ESFP": ["배우", "방송인", "이벤트 플래너", "여행 크리에이터", "공연 기획자"]
}

# ---------- 직업별 아이콘 매핑 ----------
icon_dict = {
    "데이터 과학자": "💻", "프로그래머": "👨‍💻", "AI 연구원": "🤖", "연구원": "🔬",
    "CEO": "👔", "경영 전략가": "📊", "투자은행가": "💰", "경영 컨설턴트": "📈",
    "변호사": "⚖️", "법률 사무관": "📜", "공무원": "🏛️", "군인": "🎖️",
    "상담사": "🗣️", "심리학자": "🧠", "교사": "📚", "교육자": "🏫",
    "작가": "✍️", "콘텐츠 크리에이터": "🎥", "예술가": "🎨", "음악가": "🎵",
    "간호사": "🏥", "사회복지사": "🤝", "HR 담당자": "👥", "행정직": "🗂️",
    "배우": "🎬", "방송인": "📺", "이벤트 기획자": "🎉", "이벤트 플래너": "🎉",
    "여행 크리에이터": "🌍", "프로게이머": "🎮", "파일럿": "✈️",
    "패션 디자이너": "👗", "사진작가": "📸", "요리사": "🍳", "플로리스트": "💐",
    "세일즈 전문가": "🤝", "부동산 투자자": "🏢", "스포츠 에이전트": "⚽",
    "트레이너": "💪", "제품 매니저": "🛠️", "홍보 전문가": "📢", "광고 기획자": "🖌️",
    "스타트업 창업가": "🚀", "혁신 연구원": "💡", "VC": "🏦",
    "운영 관리자": "🛠️", "기업 관리자": "🏢", "공공기관 관리자": "🏛️",
    "영업 관리": "📞", "사회사업가": "🤲", "비서": "📎",
    "보안 전문가": "🔒", "자동차 정비사": "🔧", "기계 엔지니어": "⚙️",
    "발명가": "💡", "UX 엔지니어": "📱", "리더십 코치": "🏆", "외교관": "🌐",
    "인권 활동가": "✊", "예능 PD": "🎥"
}

# ---------- 입력 ----------
st.markdown(
    "<h3 style='color: #FF69B4; text-align:center;'>당신의 MBTI를 골라보세요 💌</h3>",
    unsafe_allow_html=True
)
selected_mbti = st.selectbox("MBTI 선택", list(job_dict.keys()), index=0)

# ---------- 결과 출력 ----------
if selected_mbti:
    st.markdown(
        f"<h2 style='color:#FF1493;text-align:center;'>🌟 {selected_mbti} 유형 추천 직업 🌟</h2>",
        unsafe_allow_html=True
    )
    for job in job_dict[selected_mbti]:
        icon = icon_dict.get(job, "💖")
        st.markdown(
            f"<div style='background-color:#FFF0F5;padding:10px;margin:8px;border-radius:10px;"
            f"border:1px solid #FFB6C1;font-size:18px;'>"
            f"{icon} <b>{job}</b></div>",
            unsafe_allow_html=True
        )

# ---------- 하단 문구 ----------
st.markdown(
    """
    <hr style='border: 2px solid #FFB6C1;'>
    <p style='text-align:center; color:#FF69B4; font-size:16px;'>
        Made with ❤️ using Streamlit <br>
        <small>진로 상담, 학교 프로젝트, 교육용으로 자유롭게 활용하세요!</small>
    </p>
    """,
    unsafe_allow_html=True
)
