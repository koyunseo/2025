streamlit
pandas
title,content,category,likes,views,image
import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime

st.set_page_config(page_title="나만의 블로그", layout="wide")

DATA_FILE = "posts.csv"

# CSV 불러오기
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["title", "content", "category", "likes", "views", "image"])

# ----- 블로그 기본 설정 -----
st.sidebar.header("블로그 설정")
blog_title = st.sidebar.text_input("블로그 제목", "나의 블로그")
font_option = st.sidebar.selectbox(
    "폰트 선택",
    ["Nanum Gothic", "Noto Sans KR", "Roboto", "Song Myung", "Gamja Flower"]
)
font_css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family={font_option.replace(" ", "+")}&display=swap');
    html, body, [class*="css"]  {{
        font-family: '{font_option}', sans-serif;
    }}
    </style>
"""
st.markdown(font_css, unsafe_allow_html=True)
st.title(blog_title)

# ----- 관리자 페이지 -----
st.sidebar.subheader("관리자 모드")
admin_pw = st.sidebar.text_input("비밀번호 입력", type="password")
if admin_pw == "admin123":  # 관리자 비번
    st.sidebar.success("관리자 모드 활성화")
    st.subheader("새 글 작성")

    new_title = st.text_input("제목")
    new_content = st.text_area("내용")
    new_category = st.text_input("목록(카테고리)")
    new_image = st.file_uploader("이미지 업로드", type=["png", "jpg", "jpeg"])

    if st.button("글 저장하기"):
        image_data = ""
        if new_image:
            img_bytes = new_image.read()
            image_data = base64.b64encode(img_bytes).decode()

        new_post = pd.DataFrame([{
            "title": new_title,
            "content": new_content,
            "category": new_category,
            "likes": 0,
            "views": 0,
            "image": image_data
        }])
        df = pd.concat([df, new_post], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.success("저장되었습니다! 새로고침 후 확인하세요.")
else:
    st.sidebar.warning("관리자 모드는 비밀번호 필요")

# ----- 포스트 필터 -----
st.sidebar.subheader("목록 선택")
categories = ["전체"] + sorted(df["category"].dropna().unique().tolist())
selected_category = st.sidebar.selectbox("보기", categories)

if selected_category != "전체":
    display_df = df[df["category"] == selected_category]
else:
    display_df = df

# ----- 포스트 출력 -----
st.subheader("블로그 글")
if display_df.empty:
    st.info("아직 작성된 글이 없습니다.")
else:
    for i, row in display_df.iterrows():
        st.markdown(f"### {row['title']}")
        st.markdown(row['content'])
        if row['image']:
            st.image(base64.b64decode(row['image']), use_column_width=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"❤️ {int(row['likes'])}", key=f"like_{i}"):
                df.at[i, "likes"] = int(row["likes"]) + 1
                df.to_csv(DATA_FILE, index=False)
                st.experimental_rerun()
        with col2:
            st.write(f"조회수: {int(row['views'])+1}")
            df.at[i, "views"] = int(row["views"]) + 1
            df.to_csv(DATA_FILE, index=False)
