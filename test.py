import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="나의 블로그", layout="centered")

# -------------------------------
# 1. 글 데이터 불러오기 / 초기화
# -------------------------------
FILE_PATH = "posts.csv"

if os.path.exists(FILE_PATH):
    df = pd.read_csv(FILE_PATH)
else:
    df = pd.DataFrame(columns=["title", "body"])
    df.to_csv(FILE_PATH, index=False)

# -------------------------------
# 2. 블로그 헤더
# -------------------------------
st.title("나의 블로그")
st.write("개발 · 일상 · 기록")
st.markdown("---")

# -------------------------------
# 3. 메뉴 선택
# -------------------------------
menu = st.sidebar.radio("메뉴", ["글 목록", "글 작성"])

# -------------------------------
# 4. 글 목록 보기
# -------------------------------
if menu == "글 목록":
    if len(df) == 0:
        st.info("아직 작성된 글이 없습니다. 왼쪽 메뉴에서 글을 작성하세요!")
    else:
        titles = df["title"].tolist()
        choice = st.selectbox("읽고 싶은 글을 선택하세요", titles)
        if choice:
            row = df[df["title"] == choice].iloc[0]
            st.subheader(row["title"])
            st.write(row["body"])

# -------------------------------
# 5. 글 작성하기
# -------------------------------
elif menu == "글 작성":
    st.subheader("새 글 작성")
    with st.form("post_form"):
        title = st.text_input("글 제목")
        body = st.text_area("글 내용", height=200)
        submitted = st.form_submit_button("저장하기")

        if submitted:
            if title.strip() == "" or body.strip() == "":
                st.warning("제목과 내용을 모두 입력하세요.")
            else:
                new_row = pd.DataFrame([[title, body]], columns=["title", "body"])
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(FILE_PATH, index=False)
                st.success("글이 저장되었습니다! 왼쪽 메뉴에서 확인하세요.")
