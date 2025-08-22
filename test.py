import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="나의 블로그", layout="centered")

import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="나의 블로그", layout="centered")

FILE_PATH = "posts.csv"

# CSV 불러오기 → 컬럼 없으면 새로 생성
if os.path.exists(FILE_PATH):
    try:
        df = pd.read_csv(FILE_PATH)
        # 필수 컬럼 확인
        for col in ["category", "title", "body"]:
            if col not in df.columns:
                raise ValueError("CSV 구조 불일치")
        # 혹시 다른 컬럼만 있으면 덮어쓰기
        df = df[["category", "title", "body"]]
    except Exception:
        df = pd.DataFrame(columns=["category", "title", "body"])
        df.to_csv(FILE_PATH, index=False)
else:
    df = pd.DataFrame(columns=["category", "title", "body"])
    df.to_csv(FILE_PATH, index=False)

# -------------------------------
# 1. CSV 불러오기 또는 새로 생성
# -------------------------------
FILE_PATH = "posts.csv"

# CSV 읽기
if os.path.exists(FILE_PATH):
    try:
        df = pd.read_csv(FILE_PATH)
    except Exception:
        df = pd.DataFrame(columns=["category", "title", "body"])
        df.to_csv(FILE_PATH, index=False)
else:
    df = pd.DataFrame(columns=["category", "title", "body"])
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
        # 카테고리 필터 옵션 준비
        categories = ["전체"] + sorted(df["category"].dropna().unique().tolist())
        selected_cat = st.selectbox("카테고리 선택", categories)

        # 필터 적용
        if selected_cat != "전체":
            filtered_df = df[df["category"] == selected_cat]
        else:
            filtered_df = df

        # 글 목록 표시
        if len(filtered_df) == 0:
            st.warning("선택한 카테고리에 글이 없습니다.")
        else:
            titles = filtered_df["title"].tolist()
            choice = st.selectbox("읽고 싶은 글을 선택하세요", titles)
            if choice:
                row = filtered_df[filtered_df["title"] == choice].iloc[0]
                st.subheader(row["title"])
                st.caption(f"카테고리: {row['category']}")
                st.write(row["body"])

# -------------------------------
# 5. 글 작성하기
# -------------------------------
elif menu == "글 작성":
    st.subheader("새 글 작성")
    with st.form("post_form"):
        # 기존 카테고리 목록
        existing_cats = sorted(df["category"].dropna().unique().tolist())
        # 첫 번째 옵션: 새 카테고리
        category_choice = st.selectbox("카테고리 선택", ["(새 카테고리 추가)"] + existing_cats)

        new_category = ""
        if category_choice == "(새 카테고리 추가)":
            new_category = st.text_input("새 카테고리 입력")

        title = st.text_input("글 제목")
        body = st.text_area("글 내용", height=200)
        submitted = st.form_submit_button("저장하기")

        if submitted:
            final_category = new_category.strip() if category_choice == "(새 카테고리 추가)" else category_choice
            if final_category == "" or title.strip() == "" or body.strip() == "":
                st.warning("카테고리, 제목, 내용을 모두 입력하세요.")
            else:
                new_row = pd.DataFrame([[final_category, title.strip(), body.strip()]],
                                       columns=["category", "title", "body"])
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(FILE_PATH, index=False)
                st.success("글이 저장되었습니다! 왼쪽 메뉴에서 확인하세요.")
