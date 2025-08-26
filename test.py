import streamlit as st
import pandas as pd
import os
import base64

st.set_page_config(page_title="친구 공유 블로그", layout="wide")

DATA_FILE = "posts.csv"

# CSV 불러오기 또는 새 생성
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["title", "content", "category", "image"])

# ----- 블로그 설정 -----
st.sidebar.header("블로그 설정")
blog_title = st.sidebar.text_input("블로그 제목", "친구 공유 블로그")
font_option = st.sidebar.selectbox(
    "폰트 선택",
    ["Nanum Gothic", "Noto Sans KR", "Roboto", "Song Myung", "Gamja Flower"]
)
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family={font_option.replace(' ', '+')}&display=swap');
html, body, [class*="css"] {{
    font-family: '{font_option}', sans-serif;
}}
</style>
""", unsafe_allow_html=True)
st.title(blog_title)

# ----- 새 글 작성 -----
st.subheader("새 글 작성")
with st.form("write_form"):
    new_title = st.text_input("제목")
    new_content = st.text_area("내용")
    new_category = st.text_input("카테고리")
    new_image = st.file_uploader("이미지 업로드", type=["png", "jpg", "jpeg"])
    submitted = st.form_submit_button("글 저장하기")
    
    if submitted:
        image_data = ""
        if new_image:
            image_data = base64.b64encode(new_image.read()).decode()
        new_post = pd.DataFrame([{
            "title": new_title,
            "content": new_content,
            "category": new_category,
            "image": image_data
        }])
        df = pd.concat([df, new_post], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.success("글이 저장되었습니다! 새로고침 후 확인하세요.")

# ----- 카테고리 필터 -----
st.sidebar.subheader("목록 선택")
categories = ["전체"] + sorted(df["category"].dropna().unique().tolist())
selected_category = st.sidebar.selectbox("보기", categories)

if selected_category != "전체":
    display_df = df[df["category"] == selected_category]
else:
    display_df = df

# ----- 글 출력 -----
st.subheader("블로그 글")
if display_df.empty:
    st.info("아직 작성된 글이 없습니다.")
else:
    for i, row in display_df.iterrows():
        st.markdown(f"### {row['title']}")
        st.markdown(row['content'])
        if row['image']:
            st.image(base64.b64decode(row['image']), use_column_width=True)
