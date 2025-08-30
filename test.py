import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json

st.set_page_config(page_title="블로그", layout="wide")

# --- 설정 파일 ---
SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {"blog_title": "📚 공유 블로그"}

if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        settings = json.load(f)
else:
    settings = DEFAULT_SETTINGS
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False)

# 블로그 제목 표시
st.title(settings["blog_title"])
new_title = st.text_input("블로그 제목 변경", settings["blog_title"])
if st.button("제목 저장"):
    if new_title.strip():
        settings["blog_title"] = new_title.strip()
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False)
        st.success("✅ 블로그 제목이 변경되었습니다! 새로고침 시 적용됩니다.")

# --- 게시글 CSV 초기화 ---
if not os.path.exists("posts.csv"):
    df = pd.DataFrame(columns=["title","content","author","category","date","image","likes","comments"])
    df.to_csv("posts.csv", index=False)

# --- 탭 정의 ---
tab1, tab2 = st.tabs(["글 보기", "글 작성"])

# --- 글 보기 탭 ---
with tab1:
    st.header("📖 글 목록")
    df = pd.read_csv("posts.csv")

    if df.empty:
        st.info("아직 작성된 글이 없습니다.")
    else:
        # 카테고리 선택
        categories = ["전체"] + sorted(df["category"].dropna().unique().tolist())
        selected_category = st.selectbox("카테고리 선택", categories)

        # 정렬 선택
        sort_order = st.radio("정렬 순서", ["최신순","오래된순","좋아요순"], horizontal=True)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

        # 카테고리 필터링
        if selected_category != "전체":
            df = df[df["category"] == selected_category]

        # 정렬 적용
        if sort_order == "최신순":
            df = df.sort_values("date", ascending=False)
        elif sort_order == "오래된순":
            df = df.sort_values("date", ascending=True)
        elif sort_order == "좋아요순":
            df = df.sort_values("likes", ascending=False)

        if df.empty:
            st.info("해당 카테고리에는 글이 없습니다.")
        else:
            for i, row in df.iterrows():
                with st.expander(f"{row['title']} (작성자: {row['author']})", expanded=False):
                    # 이미지 표시
                    if isinstance(row["image"], str) and row["image"] and os.path.exists(row["image"]):
                        st.image(row["image"], use_container_width=True)
                    st.write(row["content"])

                    # 좋아요
                    like_key = f"like_{i}"  # 글 고유 키
                    if like_key not in st.session_state:
                        st.session_state[like_key] = int(row["likes"])
                    # 좋아요 버튼과 안내 문구를 한 줄에 배치
                    col1, col2 = st.columns([1, 3])  # 버튼:문구 비율을 1:3으로 조절
                    with col1:
                    if st.button(f"👍 {st.session_state[like_key]}", key=f"like_btn_{i}"):
                      st.session_state[like_key] += 1
                      df.loc[i, "likes"] = st.session_state[like_key]
                      df.to_csv("posts.csv", index=False)
                      st.success("좋아요가 반영되었습니다!")
                    with col2:
                        st.markdown("<p style='margin-left:5px;'>_(두 번 클릭해야 반영될 수 있습니다)_</p>", unsafe_allow_html=True)
                    



                    # 댓글
                    st.markdown("**댓글**")
                    comments = eval(row["comments"]) if isinstance(row["comments"], str) else row["comments"]
                    if comments:
                        for c in comments:
                            st.write(f"- {c}")
                    else:
                        st.write("아직 댓글이 없습니다.")

                    new_comment = st.text_input("댓글 작성", key=f"comment_input_{i}")
                    if st.button("댓글 달기", key=f"comment_btn_{i}") and new_comment.strip()!="":
                        comments.append(new_comment)
                        df.loc[i,"comments"] = str(comments)
                        df.to_csv("posts.csv", index=False)
                        st.success("댓글이 추가되었습니다!")

                    # 수정 / 삭제
                    st.markdown("---")
                    if st.button("✏️ 글 수정", key=f"edit_{i}"):
                        st.session_state["edit_index"] = i
                        st.session_state["edit_trigger"] = True
                        st.success("글 수정 모드로 전환되었습니다! 작성 탭에서 수정 가능합니다.")

                    if st.button("🗑️ 글 삭제", key=f"delete_{i}"):
                        df = df.drop(i).reset_index(drop=True)
                        df.to_csv("posts.csv", index=False)
                        st.success("글이 삭제되었습니다! 새로고침 시 적용됩니다.")

# --- 글 작성 탭 ---
with tab2:
    st.header("✏️ 글 작성하기")
    df = pd.read_csv("posts.csv")

    # 수정 모드
    if "edit_trigger" in st.session_state and st.session_state["edit_trigger"]:
        edit_idx = st.session_state["edit_index"]
        row = df.loc[edit_idx]
        title = st.text_input("제목", row["title"])
        content = st.text_area("내용", row["content"])
        author = st.text_input("작성자 이름", row["author"])
        existing_categories = df["category"].dropna().unique().tolist()
        category = st.selectbox("카테고리 선택", existing_categories+["새 카테고리 추가"],
                                index=existing_categories.index(row["category"]) if row["category"] in existing_categories else 0)
        new_category = ""
        image = st.file_uploader("이미지 업로드", type=["png","jpg","jpeg"])
    else:
        title = st.text_input("제목")
        content = st.text_area("내용")
        author = st.text_input("작성자 이름")
        existing_categories = df["category"].dropna().unique().tolist()
        category = st.selectbox("카테고리 선택", existing_categories+["추가할 새 카테고리를 작성해주세요."])
        new_category = ""
        if category=="새 카테고리 추가":
            new_category = st.text_input("새 카테고리 이름 입력")
        image = st.file_uploader("이미지 업로드(최대 1장)", type=["png","jpg","jpeg"])

    if st.button("글 저장하기"):
        if title.strip()=="" or content.strip()=="" or author.strip()=="":
            st.warning("제목, 내용, 작성자를 모두 입력해야 합니다!")
        else:
            final_category = new_category if category=="새 카테고리 추가" else category
            img_path = ""
            if image is not None:
                os.makedirs("images", exist_ok=True)
                img_path = os.path.join("images", image.name)
                with open(img_path, "wb") as f:
                    f.write(image.getbuffer())

            if "edit_trigger" in st.session_state and st.session_state.get("edit_trigger",False):
                idx = st.session_state["edit_index"]
                df.loc[idx,"title"] = title
                df.loc[idx,"content"] = content
                df.loc[idx,"author"] = author
                df.loc[idx,"category"] = final_category
                if img_path:
                    df.loc[idx,"image"] = img_path
                df.to_csv("posts.csv", index=False)
                st.success("✅ 글이 수정되었습니다! 새로고침 시 적용됩니다.")
                st.session_state["edit_trigger"] = False
            else:
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
                df = pd.concat([df,pd.DataFrame([new_post])], ignore_index=True)
                df.to_csv("posts.csv", index=False)
                st.success("✅ 글이 저장되었습니다! 새로고침 후 보기 탭에서 확인하세요.")
