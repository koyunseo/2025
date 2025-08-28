import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

st.set_page_config(page_title="블로그", layout="wide")

# ---------- JSON 안전 처리 ----------
def safe_json_loads(x):
    try:
        if isinstance(x, str) and x.strip() != "":
            return json.loads(x)
        else:
            return []
    except json.JSONDecodeError:
        return []

# ---------- 설정 ----------
SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {"blog_title": "📚 친구 공유 블로그"}

if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        settings = json.load(f)
else:
    settings = DEFAULT_SETTINGS
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False)

# ---------- 블로그 제목 ----------
st.title(settings["blog_title"])
new_title = st.text_input("블로그 제목 변경", settings["blog_title"])
if st.button("제목 저장"):
    if new_title.strip():
        settings["blog_title"] = new_title.strip()
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False)
        st.success("✅ 블로그 제목이 변경되었습니다! 새로고침 후 반영됩니다.")

# ---------- 게시글 CSV ----------
POSTS_FILE = "posts.csv"
if not os.path.exists(POSTS_FILE):
    df = pd.DataFrame(columns=["id","title","content","author","category","date","image","likes","comments"])
    df.to_csv(POSTS_FILE, index=False)

# ---------- 로드 및 컬럼 처리 ----------
df = pd.read_csv(POSTS_FILE)
if "id" not in df.columns:
    df.insert(0, "id", range(1,len(df)+1))
if "likes" not in df.columns:
    df["likes"] = 0
if "comments" not in df.columns:
    df["comments"] = [[] for _ in range(len(df))]
else:
    df["comments"] = df["comments"].apply(safe_json_loads)
df.to_csv(POSTS_FILE, index=False)

# ---------- 탭 ----------
tab1, tab2 = st.tabs(["글 보기", "글 작성"])

# ---------- 글 보기 ----------
with tab1:
    st.header("📖 글 목록")
    df = pd.read_csv(POSTS_FILE)
    df["comments"] = df["comments"].apply(safe_json_loads)

    if df.empty:
        st.info("아직 작성된 글이 없습니다.")
    else:
        categories = ["전체"] + sorted(df["category"].dropna().unique().tolist())
        selected_category = st.selectbox("카테고리 선택", categories)
        display_df = df if selected_category=="전체" else df[df["category"]==selected_category]

        # --- 세션 상태 초기화 ---
        for row in display_df.itertuples():
            author_key = f"comment_author_{row.id}"
            text_key = f"comment_text_{row.id}"
            submitted_key = f"comment_submitted_{row.id}"
            like_key = f"like_{row.id}"

            if author_key not in st.session_state:
                st.session_state[author_key] = ""
            if text_key not in st.session_state:
                st.session_state[text_key] = ""
            if submitted_key not in st.session_state:
                st.session_state[submitted_key] = False
            if like_key not in st.session_state:
                st.session_state[like_key] = row.likes

        # --- 글 표시 ---
        for idx, row in display_df.iterrows():
            container = st.container()
            with container:
                st.subheader(row["title"])
                st.caption(f"작성자: {row['author']} | 작성일: {row['date']} | 카테고리: {row['category']}")
                if isinstance(row["image"], str) and row["image"] and os.path.exists(row["image"]):
                    st.image(row["image"], use_column_width=True)
                st.write(row["content"])

                # --- 좋아요 ---
                like_key = f"like_{row['id']}"
                if st.button(f"👍 좋아요 ({st.session_state[like_key]})", key=like_key+"_btn"):
                    st.session_state[like_key] += 1
                    df.at[idx,"likes"] = st.session_state[like_key]
                    df.to_csv(POSTS_FILE,index=False)
                    st.experimental_rerun()

# ---------- 글 작성 ----------
with tab2:
    st.header("✏️ 글 작성하기")

    # 세션 상태 사용
    if "new_title" not in st.session_state:
        st.session_state["new_title"] = ""
    if "new_content" not in st.session_state:
        st.session_state["new_content"] = ""
    if "new_author" not in st.session_state:
        st.session_state["new_author"] = ""
    if "new_category" not in st.session_state:
        st.session_state["new_category"] = ""

    st.session_state["new_title"] = st.text_input("제목", st.session_state["new_title"])
    st.session_state["new_content"] = st.text_area("내용", st.session_state["new_content"])
    st.session_state["new_author"] = st.text_input("작성자 이름", st.session_state["new_author"])

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
        if st.session_state["new_title"].strip()=="" or st.session_state["new_content"].strip()=="" or st.session_state["new_author"].strip()=="":
            st.warning("제목, 내용, 작성자를 모두 입력해야 합니다!")
        else:
            img_path = ""
            if image is not None:
                os.makedirs("images", exist_ok=True)
                img_path = os.path.join("images", image.name)
                with open(img_path,"wb") as f:
                    f.write(image.getbuffer())

            new_post = {
                "id": len(df)+1,
                "title": st.session_state["new_title"],
                "content": st.session_state["new_content"],
                "author": st.session_state["new_author"],
                "category": final_category,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "image": img_path,
                "likes":0,
                "comments":json.dumps([])
            }
            df = pd.concat([df, pd.DataFrame([new_post])], ignore_index=True)
            df.to_csv(POSTS_FILE,index=False)

            # 입력 초기화 후 rerun
            st.session_state["new_title"] = ""
            st.session_state["new_content"] = ""
            st.session_state["new_author"] = ""
            st.session_state["new_category"] = ""
            st.success("✅ 글이 저장되었습니다! 글 목록 탭에서 확인하세요.")
            st.experimental_rerun()
