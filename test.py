import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="블로그", layout="wide")

# --- 게시글 CSV 초기화 ---
POSTS_FILE = "posts.csv"
if not os.path.exists(POSTS_FILE):
    df = pd.DataFrame(columns=["title","content","author","category","date","image"])
    df.to_csv(POSTS_FILE, index=False)

# --- 세션 상태 초기화 ---
for key in ["title","content","author","new_category"]:
    if key not in st.session_state:
        st.session_state[key] = ""

# --- 탭 ---
tab1, tab2 = st.tabs(["글 보기","글 작성"])

# --- 글 보기 ---
with tab1:
    st.header("📖 글 목록")
    df = pd.read_csv(POSTS_FILE)
    if df.empty:
        st.info("아직 작성된 글이 없습니다.")
    else:
        for i, row in df.iterrows():
            st.subheader(row["title"])
            st.caption(f"작성자: {row['author']} | 작성일: {row['date']} | 카테고리: {row['category']}")
            if isinstance(row["image"], str) and row["image"] and os.path.exists(row["image"]):
                st.image(row["image"], use_column_width=True)
            st.write(row["content"])
            st.markdown("---")

# --- 글 작성 ---
with tab2:
    st.header("✏️ 글 작성하기")

    st.session_state["title"] = st.text_input("제목", st.session_state["title"])
    st.session_state["content"] = st.text_area("내용", st.session_state["content"])
    st.session_state["author"] = st.text_input("작성자 이름", st.session_state["author"])

    # 카테고리
    df = pd.read_csv(POSTS_FILE)
    existing_categories = df["category"].dropna().unique().tolist()
    category_option = existing_categories + ["새 카테고리 추가"]
    selected_category = st.selectbox("카테고리 선택", category_option)
    if selected_category == "새 카테고리 추가":
        st.session_state["new_category"] = st.text_input("새 카테고리 이름 입력", st.session_state["new_category"])
        final_category = st.session_state["new_category"]
    else:
        final_category = selected_category

    image = st.file_uploader("이미지 업로드", type=["png","jpg","jpeg"])

    if st.button("글 저장하기"):
        if st.session_state["title"].strip()=="" or st.session_state["content"].strip()=="" or st.session_state["author"].strip()=="":
            st.warning("제목, 내용, 작성자를 모두 입력해야 합니다!")
        else:
            # 이미지 저장
            img_path = ""
            if image is not None:
                os.makedirs("images", exist_ok=True)
                img_path = os.path.join("images", image.name)
                with open(img_path, "wb") as f:
                    f.write(image.getbuffer())

            # 글 저장
            df = pd.read_csv(POSTS_FILE)
            new_post = {
                "title": st.session_state["title"],
                "content": st.session_state["content"],
                "author": st.session_state["author"],
                "category": final_category,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "image": img_path
            }
            df = pd.concat([df, pd.DataFrame([new_post])], ignore_index=True)
            df.to_csv(POSTS_FILE, index=False)

            # 입력값 초기화
            st.session_state["title"] = ""
            st.session_state["content"] = ""
            st.session_state["author"] = ""
            st.session_state["new_category"] = ""

            st.success("✅ 글이 저장되었습니다! 글 목록 탭에서 확인하세요.")
