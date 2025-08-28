import streamlit as st
import pandas as pd
import os
from datetime import datetime

# CSV 파일이 없으면 새로 생성
if not os.path.exists("posts.csv"):
    df = pd.DataFrame(columns=["title", "content", "author", "date", "image"])
    df.to_csv("posts.csv", index=False)
else:
    df = pd.read_csv("posts.csv")

st.set_page_config(page_title="친구 블로그", layout="wide")

# 사이드바 메뉴
menu = st.sidebar.radio("메뉴 선택", ["글 작성하기", "글 보기"])

# ---------------------
# 글 작성 페이지
# ---------------------
if menu == "글 작성하기":
    st.header("✏️ 글 작성하기")
    title = st.text_input("제목")
    content = st.text_area("내용")
    author = st.text_input("작성자 이름")
    image = st.file_uploader("이미지 업로드", type=["png", "jpg", "jpeg"])

    if st.button("글 저장하기"):
        if title.strip() == "" or content.strip() == "" or author.strip() == "":
            st.warning("제목, 내용, 작성자를 모두 입력해야 합니다!")
        else:
            # 이미지 저장
            img_path = ""
            if image is not None:
                img_path = os.path.join("images", image.name)
                os.makedirs("images", exist_ok=True)
                with open(img_path, "wb") as f:
                    f.write(image.getbuffer())

            # CSV에 추가
            new_post = {
                "title": title,
                "content": content,
                "author": author,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "image": img_path
            }
            df = pd.concat([pd.read_csv("posts.csv"), pd.DataFrame([new_post])], ignore_index=True)
            df.to_csv("posts.csv", index=False)
            st.success("글이 저장되었습니다!")

# ---------------------
# 글 보기 페이지
# ---------------------
elif menu == "글 보기":
    st.header("📖 글 목록")
    df = pd.read_csv("posts.csv")

    if df.empty:
        st.info("아직 작성된 글이 없습니다.")
    else:
        for i, row in df.iterrows():
            st.subheader(row["title"])
            st.caption(f"작성자: {row['author']} | 작성일: {row['date']}")
            if row["image"] and os.path.exists(row["image"]):
                st.image(row["image"], use_column_width=True)
            st.write(row["content"])
            st.markdown("---")
