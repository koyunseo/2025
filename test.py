import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="간단 블로그", layout="wide")

# CSV 파일이 없으면 생성
if not os.path.exists("posts.csv"):
    df = pd.DataFrame(columns=["title", "content", "author", "date", "image"])
    df.to_csv("posts.csv", index=False)
else:
    df = pd.read_csv("posts.csv")

st.title("📚 간단 블로그")

tab1, tab2 = st.tabs(["글 보기", "글 작성"])

# --- 글 보기 탭 ---
with tab1:
    st.header("📖 글 목록")
    if os.path.exists("posts.csv"):
        df = pd.read_csv("posts.csv")
        if df.empty:
            st.info("아직 작성된 글이 없습니다.")
        else:
            for i, row in df.iterrows():
                st.subheader(row["title"])
                st.caption(f"작성자: {row['author']} | 작성일: {row['date']}")
                if isinstance(row["image"], str) and row["image"] and os.path.exists(row["image"]):
                    st.image(row["image"], use_column_width=True)
                st.write(row["content"])
                st.markdown("---")
    else:
        st.info("아직 작성된 글이 없습니다.")

# --- 글 작성 탭 ---
with tab2:
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

            # 새 글 추가
            new_post = {
                "title": title,
                "content": content,
                "author": author,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "image": img_path
            }
            df = pd.concat([pd.read_csv("posts.csv"), pd.DataFrame([new_post])], ignore_index=True)
            df.to_csv("posts.csv", index=False)
            st.success("글이 저장되었습니다! 글 목록 탭에서 확인하세요.")
