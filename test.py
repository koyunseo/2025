import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

st.set_page_config(page_title="블로그", layout="wide")

# --- 설정 파일 ---
SETTINGS_FILE = "settings.json"
POSTS_FILE = "posts.csv"
COMMENTS_FILE = "comments.csv"
DEFAULT_SETTINGS = {"blog_title": "📚 카테고리 블로그"}

# 설정 로드
if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        settings = json.load(f)
else:
    settings = DEFAULT_SETTINGS
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False)

# 블로그 제목
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
if not os.path.exists(POSTS_FILE):
    pd.DataFrame(columns=["title", "content", "author", "category", "date", "image", "likes"]).to_csv(POSTS_FILE, index=False)

# 기존 파일에 likes 없으면 추가
df_posts = pd.read_csv(POSTS_FILE)
if "likes" not in df_posts.columns:
    df_posts["likes"] = 0
    df_posts.to_csv(POSTS_FILE, index=False)

# --- 댓글 CSV 초기화 ---
if not os.path.exists(COMMENTS_FILE):
    pd.DataFrame(columns=["post_title", "author", "comment", "date"]).to_csv(COMMENTS_FILE, index=False)

# 탭 UI
tab1, tab2 = st.tabs(["글 보기", "글 작성"])

# --- 글 보기 ---
with tab1:
    st.header("📖 글 목록")
    df = pd.read_csv(POSTS_FILE)
    comments_df = pd.read_csv(COMMENTS_FILE)

    if df.empty:
        st.info("아직 작성된 글이 없습니다.")
    else:
        categories = ["전체"] + sorted(df["category"].dropna().unique().tolist())
        selected_category = st.selectbox("카테고리 선택", categories)

        if selected_category != "전체":
            df = df[df["category"] == selected_category]

        if df.empty:
            st.info("해당 카테고리에는 글이 없습니다.")
        else:
            for idx, row in df.iterrows():
                expander_label = f"{row['title']}  |  {row['author']}"
                with st.expander(expander_label):
                    st.caption(f"작성일: {row['date']} | 카테고리: {row['category']}")
                    if isinstance(row["image"], str) and row["image"] and os.path.exists(row["image"]):
                        st.image(row["image"], use_container_width=True)
                    st.write(row["content"])
                    st.markdown("---")

                    # --- 좋아요 기능 ---
                    col1, col2 = st.columns([1,4])
                    with col1:
                        if st.button("👍 좋아요", key=f"like_{idx}"):
                            df.loc[idx, "likes"] = int(row["likes"]) + 1
                            df.to_csv(POSTS_FILE, index=False)
                            st.rerun()
                    with col2:
                        st.write(f"좋아요 수 : {int(row['likes'])}")

                    st.markdown("---")

                    # --- 댓글 표시 ---
                    st.subheader("💬 댓글")
                    post_comments = comments_df[comments_df["post_title"] == row["title"]]
                    if post_comments.empty:
                        st.info("아직 댓글이 없습니다.")
                    else:
                        for _, c in post_comments.iterrows():
                            st.markdown(f"- **{c['author']}** ({c['date']}) : {c['comment']}")

                    # --- 댓글 작성 ---
                    st.markdown("**댓글 작성하기**")
                    comment_author = st.text_input(f"작성자 이름 ({row['title']})", key=f"author_{idx}")
                    comment_text = st.text_area(f"댓글 내용 ({row['title']})", key=f"text_{idx}")
                    if st.button("댓글 저장", key=f"btn_{idx}"):
                        if comment_author.strip() == "" or comment_text.strip() == "":
                            st.warning("작성자와 댓글 내용을 모두 입력해주세요!")
                        else:
                            new_comment = {
                                "post_title": row["title"],
                                "author": comment_author.strip(),
                                "comment": comment_text.strip(),
                                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                            }
                            comments_df = pd.concat([comments_df, pd.DataFrame([new_comment])], ignore_index=True)
                            comments_df.to_csv(COMMENTS_FILE, index=False)
                            st.success("✅ 댓글이 저장되었습니다!")
                            st.rerun()

# --- 글 작성 ---
with tab2:
    st.header("✏️ 글 작성하기")
    title = st.text_input("제목")
    content = st.text_area("내용")
    author = st.text_input("작성자 이름")

    df = pd.read_csv(POSTS_FILE)
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

            img_path = ""
            if image is not None:
                img_path = os.path.join("images", image.name)
                os.makedirs("images", exist_ok=True)
                with open(img_path, "wb") as f:
                    f.write(image.getbuffer())

            new_post = {
                "title": title,
                "content": content,
                "author": author,
                "category": final_category,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "image": img_path,
                "likes": 0
            }
            df = pd.concat([df, pd.DataFrame([new_post])], ignore_index=True)
            df.to_csv(POSTS_FILE, index=False)
            st.success("✅ 글이 저장되었습니다! 글 목록 탭에서 확인하세요.")
            st.rerun()
