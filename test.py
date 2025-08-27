import streamlit as st
import pandas as pd
import os
import base64

st.set_page_config(page_title="친구 블로그", layout="wide")

DATA_FILE = "posts.csv"

# --- 데이터 파일 불러오기 / 없으면 생성 ---
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["title", "content", "category", "image"])
    df.to_csv(DATA_FILE, index=False)

# --- 블로그 기본 설정 ---
st.sidebar.header("블로그 설정")
blog_title = st.sidebar.text_input("블로그 제목", "우리끼리 블로그")
font_choice = st.sidebar.selectbox(
    "폰트 선택",
    ["Nanum Gothic", "Noto Sans KR", "Roboto", "Song Myung", "Gamja Flower"]
)

# Google Fonts 적용
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family={font_choice.replace(' ', '+')}&display=swap');
html, body, [class*="css"] {{
    font-family: '{font_choice}', sans-serif;
}}
</style>
""", unsafe_allow_html=True)

st.title(blog_title)

# --- 글 작성 ---
st.subheader("✏️ 새 글 작성")
with st.form("write_form"):
    title = st.text_input("제목")
    content = st.text_area("내용")
    category = st.text_input("목록")
    image = st.file_uploader("이미지 업로드", type=["png", "jpg", "jpeg"])
    submit = st.form_submit_button("저장하기")
    if submit:
        image_data = ""
        if image:
            image_data = base64.b64encode(image.read()).decode()
        new_post = pd.DataFrame([{
            "title": title,
            "content": content,
            "category": category,
            "image": image_data
        }])
        df = pd.concat([df, new_post], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.success("저장 완료! 새로고침 후 확인하세요.")

# --- 카테고리 선택 ---
st.sidebar.subheader("목록 필터")
categories = ["전체"] + sorted(df["category"].dropna().unique().tolist())
selected = st.sidebar.selectbox("선택", categories)
if selected == "전체":
    display_df = df
else:
    display_df = df[df["category"] == selected]

# --- 글 표시 ---
st.subheader("📖 블로그 글")
if display_df.empty:
    st.info("아직 글이 없습니다.")
else:
    for _, row in display_df.iterrows():
        st.markdown(f"### {row['title']}")
        st.markdown(row['content'])
        if row["image"]:
            st.image(base64.b64decode(row["image"]), use_column_width=True)
        st.markdown("---")
