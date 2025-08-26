import streamlit as st
import pandas as pd
import os
from PIL import Image

st.set_page_config(page_title="나의 블로그", layout="centered")

# -------------------------------
# 0. 사이드바에서 블로그 스타일 지정
# -------------------------------
st.sidebar.header("🛠 블로그 디자인 설정")

# 블로그 제목/소개
blog_title = st.sidebar.text_input("블로그 제목", value="나의 블로그")
blog_intro = st.sidebar.text_input("소개 문구", value="개발 · 일상 · 기록")

# 폰트 선택
font_options = [
    "Nanum Gothic",
    "Noto Sans KR",
    "Roboto",
    "Open Sans",
    "M PLUS Rounded 1c"
]
selected_font = st.sidebar.selectbox("폰트 선택 (Google Fonts)", font_options)

# 색상 선택
bg_color = st.sidebar.color_picker("배경색", value="#FFFFFF")
header_color = st.sidebar.color_picker("헤더색 (제목)", value="#000000")
body_color = st.sidebar.color_picker("본문 글씨 색상", value="#333333")
intro_color = st.sidebar.color_picker("소개 문구 색상", value="#555555")

# 크기 및 정렬
intro_size = st.sidebar.slider("소개 문구 크기(px)", 12, 40, 18)
intro_align = st.sidebar.radio("소개 문구 정렬", ["left", "center", "right"], index=1)
body_size = st.sidebar.slider("본문 글자 크기(px)", 12, 24, 16)

# Google Fonts 적용
if selected_font:
    font_css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family={selected_font.replace(' ', '+')}&display=swap');
    html, body, [class*="css"] {{
        font-family: '{selected_font}', sans-serif !important;
        background-color: {bg_color} !important;
        color: {body_color} !important;
        font-size: {body_size}px !important;
    }}
    </style>
    """
    st.markdown(font_css, unsafe_allow_html=True)

# -------------------------------
# 1. 데이터 불러오기 또는 새로 생성
# -------------------------------
POSTS_FILE = "posts.csv"
META_FILE = "meta.csv"
IMG_DIR = "images"

if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

# 글 데이터
if os.path.exists(POSTS_FILE):
    try:
        posts_df = pd.read_csv(POSTS_FILE)
        for col in ["category", "title", "body", "image"]:
            if col not in posts_df.columns:
                raise ValueError("CSV 구조 불일치")
        posts_df = posts_df[["category", "title", "body", "image"]]
    except Exception:
        posts_df = pd.DataFrame(columns=["category", "title", "body", "image"])
        posts_df.to_csv(POSTS_FILE, index=False)
else:
    posts_df = pd.DataFrame(columns=["category", "title", "body", "image"])
    posts_df.to_csv(POSTS_FILE, index=False)

# 좋아요/조회수 메타데이터
if os.path.exists(META_FILE):
    try:
        meta_df = pd.read_csv(META_FILE)
        for col in ["title", "views", "likes"]:
            if col not in meta_df.columns:
                raise ValueError("CSV 구조 불일치")
        meta_df = meta_df[["title", "views", "likes"]]
    except Exception:
        meta_df = pd.DataFrame(columns=["title", "views", "likes"])
        meta_df.to_csv(META_FILE, index=False)
else:
    meta_df = pd.DataFrame(columns=["title", "views", "likes"])
    meta_df.to_csv(META_FILE, index=False)

# -------------------------------
# 블로그 헤더
# -------------------------------
st.markdown(
    f"<h1 style='color:{header_color}; text-align:center; margin-bottom:0;'>{blog_title}</h1>", 
    unsafe_allow_html=True
)
intro_html = f"""
<p style='color:{intro_color}; font-size:{intro_size}px; text-align:{intro_align}; margin-bottom:20px;'>
{blog_intro}
</p>
"""
st.markdown(intro_html, unsafe_allow_html=True)
st.markdown("---")

# -------------------------------
# 메뉴 선택
# -------------------------------
menu = st.sidebar.radio("메뉴", ["글 목록", "글 작성"])

# -------------------------------
# 글 목록 보기
# -------------------------------
if menu == "글 목록":
    if len(posts_df) == 0:
        st.info("아직 작성된 글이 없습니다. 왼쪽 메뉴에서 글을 작성하세요!")
    else:
        lists = ["전체"] + sorted(posts_df["category"].dropna().unique().tolist())
        selected_list = st.selectbox("목록 선택", lists)

        filtered_df = posts_df if selected_list == "전체" else posts_df[posts_df["category"] == selected_list]

        if len(filtered_df) == 0:
            st.warning("선택한 목록에 글이 없습니다.")
        else:
            titles = filtered_df["title"].tolist()
            choice = st.selectbox("읽고 싶은 글을 선택하세요", titles)
            if choice:
                row = filtered_df[filtered_df["title"] == choice].iloc[0]

                # 조회수 증가
                if choice in meta_df["title"].values:
                    meta_df.loc[meta_df["title"] == choice, "views"] += 1
                else:
                    meta_df = pd.concat([meta_df, pd.DataFrame([[choice, 1, 0]], columns=["title", "views", "likes"])], ignore_index=True)
                meta_df.to_csv(META_FILE, index=False)

                # 본문 표시
                st.markdown(
                    f"<h2 style='color:{header_color};'>{row['title']}</h2>",
                    unsafe_allow_html=True
                )
                st.caption(f"목록: {row['category']}")

                # 이미지 표시
                if row["image"] and os.path.exists(row["image"]):
                    st.image(row["image"], use_column_width=True)

                # 본문 (Markdown)
                st.markdown(
                    f"<div style='color:{body_color}; font-size:{body_size}px; line-height:1.6;'>{row['body']}</div>",
                    unsafe_allow_html=True
                )

                # 좋아요 버튼
                like_count = int(meta_df.loc[meta_df["title"] == choice, "likes"].iloc[0])
                if st.button("❤️ 좋아요"):
                    meta_df.loc[meta_df["title"] == choice, "likes"] += 1
                    meta_df.to_csv(META_FILE, index=False)
                    st.success("좋아요를 눌렀습니다!")

                # 조회수 / 좋아요 현황
                view_count = int(meta_df.loc[meta_df["title"] == choice, "views"].iloc[0])
                like_count = int(meta_df.loc[meta_df["title"] == choice, "likes"].iloc[0])
                st.caption(f"조회수: {view_count} | 좋아요: {like_count}")

# -------------------------------
# 글 작성하기
# -------------------------------
elif menu == "글 작성":
    st.subheader("새 글 작성")
    with st.form("post_form"):
        existing_lists = sorted(posts_df["category"].dropna().unique().tolist())
        list_choice = st.selectbox("목록 선택", ["(새 목록 추가)"] + existing_lists)

        new_list = ""
        if list_choice == "(새 목록 추가)":
            new_list = st.text_input("새 목록 입력")

        title = st.text_input("글 제목")
        body = st.text_area("글 내용 (Markdown 지원)", height=200)
        uploaded_image = st.file_uploader("대표 이미지 업로드", type=["png", "jpg", "jpeg"])
        submitted = st.form_submit_button("저장하기")

        if submitted:
            final_list = new_list.strip() if list_choice == "(새 목록 추가)" else list_choice
            if final_list == "" or title.strip() == "" or body.strip() == "":
                st.warning("목록, 제목, 내용을 모두 입력하세요.")
            else:
                image_path = ""
                if uploaded_image is not None:
                    image_path = os.path.join(IMG_DIR, uploaded_image.name)
                    with open(image_path, "wb") as f:
                        f.write(uploaded_image.read())

                new_row = pd.DataFrame([[final_list, title.strip(), body.strip(), image_path]],
                                       columns=["category", "title", "body", "image"])
                posts_df = pd.concat([posts_df, new_row], ignore_index=True)
                posts_df.to_csv(POSTS_FILE, index=False)
                st.success("글이 저장되었습니다! 왼쪽 메뉴에서 확인하세요.")
