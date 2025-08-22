import streamlit as st

# 페이지 기본 설정
st.set_page_config(page_title="나의 블로그", layout="centered")

# 헤더 영역
st.title("나의 블로그")
st.write("개발 · 일상 · 기록")

# 글 목록 (딕셔너리로 관리)
posts = {
    1: {
        "title": "첫 번째 글 제목",
        "body": "여기에 첫 번째 글의 본문을 작성하세요. 여러 문단도 가능합니다."
    },
    2: {
        "title": "두 번째 글 제목",
        "body": "여기에 두 번째 글의 본문을 작성하세요. 마크다운도 사용 가능합니다!"
    }
}

# 선택 박스
post_id = st.selectbox("읽고 싶은 글을 선택하세요", options=list(posts.keys()), 
                       format_func=lambda x: posts[x]["title"])

# 본문 출력
st.subheader(posts[post_id]["title"])
st.write(posts[post_id]["body"])

# 푸터
st.markdown("---")
st.caption("© 2025 나의 블로그")
