import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="나의 블로그", layout="centered")

# -------------------------------
# 파일 경로
# -------------------------------
POST_FILE = "posts.csv"
DESIGN_FILE = "design.csv"

# -------------------------------
# CSV 초기화
# -------------------------------
if not os.path.exists(POST_FILE):
    pd.DataFrame(columns=["category", "title", "body"]).to_csv(POST_FILE, index=False)

if not os.path.exists(DESIGN_FILE):
    pd.DataFrame([{
        "blog_title": "나의 블로그",
        "blog_intro": "개발 · 일상 · 기록",
        "font": "Nanum Gothic",
        "header_color": "#000000"
    }]).to_csv(DESIGN_FILE, index=False)

# -------------------------------
# 디자인 설정 불러오기
# -------------------------------
design_df = pd.read_csv(DESIGN_FILE)
blog_title = design_df.loc[0, "blog_title"]
blog_intro = design_df.loc[0, "blog_intro"]
selected_font = design_df.loc[0, "font"]
header_color = design_df.loc[0, "header_color"]

# -------------------------------
# Google Fonts 적용
# -------------------------------
if selected_font:
    font_css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family={selected_font.replace(' ', '+')}&display=swap');
    html, body, [class*="css"] {{
        font-family: '{selected_font}', sans-serif;
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: {header_color};
    }}
    </style>
    """
    st.markdown(font_css, unsafe_allow_html=True)

# -------------------------------
# 메뉴 선택
# -------------------------------
menu = st.sidebar.radio("메뉴", ["글 목록", "글 작성", "관리자 모드"])

# -------------------------------
# 글 목록 페이지
# -------------------------------
df = pd.read_csv(POST_FILE)
if menu == "글 목록":
    st.title(blog_title)
    st.write(blog_intro)
    st.markdown("---")
    if len(df) == 0:
        st.info("아직 작성된 글이 없습니다. 왼쪽 메뉴에서 글을 작성하세요!")
    else:
        lists = ["전체"] + sorted(df["category"].dropna().unique().tolist())
        selected_list = st.selectbox("목록 선택", lists)
        filtered_df = df if selected_list == "전체" else df[df["category"] == selected_list]
        if len(filtered_df) == 0:
            st.warning("선택한 목록에 글이 없습니다.")
        else:
            titles = filtered_df["title"].tolist()
            choice = st.selectbox("읽고 싶은 글을 선택하세요", titles)
            if choice:
                row = filtered_df[df["title"] == choice].iloc[0]
                st.subheader(row["title"])
                st.caption(f"목록: {row['category']}")
                st.write(row["body"])

# -------------------------------
# 글 작성 페이지
# -------------------------------
elif menu == "글 작성":
    st.subheader("새 글 작성")
    with st.form("post_form"):
        existing_lists = sorted(df["category"].dropna().unique().tolist())
        list_choice = st.selectbox("목록 선택", ["(새 목록 추가)"] + existing_lists)
        new_list = ""
        if list_choice == "(새 목록 추가)":
            new_list = st.text_input("새 목록 입력")
        title = st.text_input("글 제목")
        body = st.text_area("글 내용", height=200)
        submitted = st.form_submit_button("저장하기")
        if submitted:
            final_list = new_list.strip() if list_choice == "(새 목록 추가)" else list_choice
            if final_list == "" or title.strip() == "" or body.strip() == "":
                st.warning("목록, 제목, 내용을 모두 입력하세요.")
            else:
                new_row = pd.DataFrame([[final_list, title.strip(), body.strip()]],
                                       columns=["category", "title", "body"])
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(POST_FILE, index=False)
                st.success("글이 저장되었습니다! 왼쪽 메뉴에서 확인하세요.")

# -------------------------------
# 관리자 모드 페이지
# -------------------------------
elif menu == "관리자 모드":
    st.subheader("관리자 로그인")
    admin_pass = st.text_input("비밀번호를 입력하세요", type="password")
    
    if admin_pass == "1234":  # 임시 비밀번호
        st.success("관리자 모드에 접속했습니다!")

        admin_menu = st.radio("관리자 메뉴", ["글 관리", "디자인 설정"])

        # 글 관리
        if admin_menu == "글 관리":
            st.subheader("글 삭제")
            if len(df) == 0:
                st.info("삭제할 글이 없습니다.")
            else:
                delete_title = st.selectbox("삭제할 글 선택", df["title"].tolist())
                if st.button("선택한 글 삭제"):
                    df = df[df["title"] != delete_title]
                    df.to_csv(POST_FILE, index=False)
                    st.success("글이 삭제되었습니다.")
        
        # 디자인 설정
        elif admin_menu == "디자인 설정":
            st.subheader("블로그 디자인 변경")
            new_title = st.text_input("블로그 제목", value=blog_title)
            new_intro = st.text_input("소개 문구", value=blog_intro)
            font_options = [
                "Nanum Gothic", "Noto Sans KR", "Roboto", 
                "Open Sans", "M PLUS Rounded 1c"
            ]
            new_font = st.selectbox("폰트 선택", font_options, index=font_options.index(selected_font))
            new_color = st.color_picker("헤더 색상 선택", value=header_color)

            if st.button("디자인 저장"):
                design_df.loc[0] = [new_title, new_intro, new_font, new_color]
                design_df.to_csv(DESIGN_FILE, index=False)
                st.success("디자인이 변경되었습니다. 페이지를 새로고침하세요.")
    elif admin_pass != "":
        st.error("비밀번호가 올바르지 않습니다.")
