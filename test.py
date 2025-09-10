import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime


    # ✅ 누락된 컬럼 자동 추가
    for col in ["title", "content", "author", "category", "date", "image", "likes", "comments"]:
        if col not in df.columns:
            if col == "likes":
                df[col] = 0
            elif col == "comments":
                df[col] = "[]"
            else:
                df[col] = ""
    df.to_csv("posts.csv", index=False)

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

# --- CSV 초기화 ---
if not os.path.exists("posts.csv"):
    df = pd.DataFrame(columns=["title","content","author","date","image","likes","comments"])
    df.to_csv("posts.csv", index=False)

df = pd.read_csv("posts.csv")

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

        # 카테고리 필터링
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
                    st.write(row["content"])

                    # 좋아요 표시
                    like_key = f"like_{i}"  # 각 글 고유 키
                    if like_key not in st.session_state:
                        st.session_state[like_key] = int(row["likes"])
                    
                    if st.button(f"👍 두번 클릭! ({st.session_state[like_key]})", key=f"like_btn_{i}"):
                        st.session_state[like_key] += 1
                        df.loc[i, "likes"] = st.session_state[like_key]  # df에도 즉시 반영
                        df.to_csv("posts.csv", index=False)
                        
                    # 댓글 초기화
                    if "comments" not in row or pd.isna(row["comments"]):
                        comments = []
                    else:
                        comments = eval(row["comments"])  # 문자열 리스트 -> 실제 리스트
            
                    if f"comments_{i}" not in st.session_state:
                        st.session_state[f"comments_{i}"] = comments
            
                    comments = st.session_state[f"comments_{i}"]
            
                    # 댓글 표시
                    st.markdown("**댓글:**")
                    if comments:
                        for c in comments:
                            st.write(f"- {c}")
                    else:
                        st.write("아직 댓글이 없습니다.")
            
                    # 댓글 작성
                    new_comment = st.text_input("댓글 작성", key=f"comment_input_{i}")
                    if st.button("댓글 달기", key=f"comment_btn_{i}") and new_comment.strip() != "":
                        comments.append(new_comment)
                        st.session_state[f"comments_{i}"] = comments
                        df.loc[i,"comments"] = str(comments)
                        df.to_csv("posts.csv", index=False)
                        st.success("댓글이 추가되었습니다! 새로고침 시 적용됩니다.")


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

    # --- 수정 모드 ---
    if "edit_trigger" in st.session_state and st.session_state["edit_trigger"]:
        edit_idx = st.session_state["edit_index"]
        row = df.loc[edit_idx]

        title = st.text_input("제목", row["title"])
        content = st.text_area("내용", row["content"])
        author = st.text_input("작성자 이름", row["author"])

        # 기존 카테고리 + 새 카테고리 옵션
        existing_categories = df["category"].dropna().unique().tolist()
        category = st.selectbox(
            "카테고리 선택",
            existing_categories + ["새 카테고리 추가"],
            index=existing_categories.index(row["category"]) if row["category"] in existing_categories else 0
        )

        new_category = ""
        if category == "새 카테고리 추가":
            new_category = st.text_input("새 카테고리 이름 입력")

        image = st.file_uploader("이미지 업로드", type=["png", "jpg", "jpeg"])

    # --- 새 글 작성 모드 ---
    else:
        title = st.text_input("제목")
        content = st.text_area("내용")
        author = st.text_input("작성자 이름")

        existing_categories = df["category"].dropna().unique().tolist()
        category = st.selectbox("카테고리 선택", existing_categories + ["새 카테고리 추가"])

        new_category = ""
        if category == "새 카테고리 추가":
            new_category = st.text_input("새 카테고리 이름 입력")

        image = st.file_uploader("이미지 업로드(최대 1장)", type=["png", "jpg", "jpeg"])

    # --- 저장 버튼 ---
    if st.button("글 저장하기"):
        if title.strip() == "" or content.strip() == "" or author.strip() == "":
            st.warning("제목, 내용, 작성자를 모두 입력해야 합니다!")
        else:
            # 최종 카테고리 결정
            final_category = new_category if category == "새 카테고리 추가" and new_category.strip() else category

            # 이미지 저장
            img_path = ""
            if image is not None:
                os.makedirs("images", exist_ok=True)
                img_path = os.path.join("images", image.name)
                with open(img_path, "wb") as f:
                    f.write(image.getbuffer())

            # 수정 모드 저장
            if "edit_trigger" in st.session_state and st.session_state.get("edit_trigger", False):
                idx = st.session_state["edit_index"]
                df.loc[idx, "title"] = title
                df.loc[idx, "content"] = content
                df.loc[idx, "author"] = author
                df.loc[idx, "category"] = final_category
                if img_path:
                    df.loc[idx, "image"] = img_path

                df.to_csv("posts.csv", index=False)
                st.success("✅ 글이 수정되었습니다! 새로고침 시 적용됩니다.")
                st.session_state["edit_trigger"] = False

            # 새 글 저장
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
                df = pd.concat([df, pd.DataFrame([new_post])], ignore_index=True)
                df.to_csv("posts.csv", index=False)
                st.success("✅ 글이 저장되었습니다! 새로고침 시 적용됩니다.")

