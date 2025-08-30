import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

st.set_page_config(page_title="블로그", layout="wide")

# --- 설정 파일 관리 ---
SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {"blog_title": "📚 카테고리 블로그"}

# 설정 로드
if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        settings = json.load(f)
else:
    settings = DEFAULT_SETTINGS
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False)

# --- 블로그 제목 표시 ---
st.title(settings["blog_title"])

# 제목 변경 UI
new_title = st.text_input("블로그 제목 변경", settings["blog_title"])
if st.button("제목 저장"):
    if new_title.strip():
        settings["blog_title"] = new_title.strip()
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False)
        st.success("✅ 블로그 제목이 변경되었습니다! 새로고침하면 반영됩니다.")
        st.rerun()

# --- 게시글 CSV 초기화 ---
if not os.path.exists("posts.csv"):
    df = pd.DataFrame(columns=["title", "content", "author", "category", "date", "image", "likes", "comments"])
    df.to_csv("posts.csv", index=False)

# --- 탭 UI ---
tab1, tab2 = st.tabs(["글 보기", "글 작성"])

# --- 글 보기 ---
with tab1:
    st.header("📖 글 목록")
    df = pd.read_csv("posts.csv")

    # 좋아요/댓글 필드 초기화 (없으면 추가)
    if "likes" not in df.columns:
        df["likes"] = 0
    if "comments" not in df.columns:
        df["comments"] = [[] for _ in range(len(df))]

    # 카테고리 선택
    if not df.empty:
        categories = ["전체"] + sorted(df["category"].dropna().unique().tolist())
        selected_category = st.selectbox("카테고리 선택", categories)

        # 정렬 방식 선택 (좋아요순 추가)
        sort_order = st.radio("정렬 순서", ["최신순", "오래된순", "좋아요순"], horizontal=True)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

        if sort_order == "최신순":
            df = df.sort_values("date", ascending=False)
        elif sort_order == "오래된순":
            df = df.sort_values("date", ascending=True)
        elif sort_order == "좋아요순":
            df = df.sort_values("likes", ascending=False)

        if selected_category != "전체":
            df = df[df["category"] == selected_category]

        if df.empty:
            st.info("해당 카테고리에는 글이 없습니다.")
        else:
            for i, row in df.iterrows():
                with st.expander(f"{row['title']} (작성자: {row['author']})", expanded=False):
                    # 이미지 표시
                    if isinstance(row["image"], str) and row["image"] and os.path.exists(row["image"]):
                        st.image(row["image"], use_container_width=True)
                    # 본문
                    st.write(row["content"])
                    # 좋아요 버튼
                    if st.button(f"👍 좋아요 ({int(row['likes'])})", key=f"like_{i}"):
                        df.loc[i, "likes"] = int(row["likes"]) + 1
                        df.to_csv("posts.csv", index=False)
                        st.rerun()
                    # 댓글 작성
                    comment = st.text_input("댓글 작성", key=f"comment_{i}")
                    if st.button("댓글 달기", key=f"btn_comment_{i}"):
                        comments = eval(row["comments"]) if isinstance(row["comments"], str) else row["comments"]
                        comments.append(comment)
                        df.loc[i, "comments"] = str(comments)
                        df.to_csv("posts.csv", index=False)
                        st.success("댓글이 추가되었습니다!")
                        st.rerun()
                    # 댓글 목록 표시
                    st.markdown("**댓글:**")
                    comments = eval(row["comments"]) if isinstance(row["comments"], str) else row["comments"]
                    if comments:
                        for c in comments:
                            st.write(f"- {c}")
                    else:
                        st.write("아직 댓글이 없습니다.")

    else:
        st.info("아직 작성된 글이 없습니다.")

# --- 글 작성 ---
with tab2:
    st.header("✏️ 글 작성하기")

    title = st.text_input("제목")
    content = st.text_area("내용")
    author = st.text_input("작성자 이름")

    # 카테고리 선택
    df = pd.read_csv("posts.csv")
    existing_categories = df["category"].dropna().unique().tolist()
    category = st.selectbox("카테고리 선택", existing_categories + ["새 카테고리 추가"])
    new_category = ""
    if category == "새 카테고리 추가":
        new_category = st.text_input("새 카테고리 이름 입력")

    image = st.file_uploader("이미지 업로드", type=["png", "jpg", "jpeg"])

    if st.button("글 저장하기"):
        if title.strip() == "" or content.strip() == "" or author.strip() == "":
            st.warning("제목, 내용, 작성자를 모두 입력해야 합니다!")
        else:
            final_category = new_category if category == "새 카테고리 추가" else category

            # 이미지 저장
            img_path = ""
            if image is not None:
                os.makedirs("images", exist_ok=True)
                img_path = os.path.join("images", image.name)
                with open(img_path, "wb") as f:
                    f.write(image.getbuffer())

            # 새 글 추가
            new_post = {
                "title": title,
                "content": content,
                "author": author,
                "category": final_category,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "image": img_path,
                "likes": 0,
                "comments": []
            }
            df = pd.concat([df, pd.DataFrame([new_post])], ignore_index=True)
            df.to_csv("posts.csv", index=False)
            st.success("✅ 글이 저장되었습니다! 글 목록 탭에서 확인하세요.")
            st.rerun()
