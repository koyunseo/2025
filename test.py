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

            # 댓글 초기화
            if st.session_state[submitted_key]:
                st.session_state[author_key] = ""
                st.session_state[text_key] = ""
                st.session_state[submitted_key] = False

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

                # --- 댓글 표시 ---
                comments = row["comments"]
                st.markdown("💬 댓글")
                for c in comments:
                    st.write(f"{c['author']} ({c['date']}): {c['text']}")

                # --- 댓글 작성 ---
                author_key = f"comment_author_{row['id']}"
                text_key = f"comment_text_{row['id']}"
                submitted_key = f"comment_submitted_{row['id']}"
                col1, col2 = st.columns([1,4])
                with col1:
                    comment_author = st.text_input("댓글 작성자", key=author_key)
                with col2:
                    comment_text = st.text_area("댓글 내용", key=text_key)
                if st.button("댓글 작성", key=f"comment_btn_{row['id']}"):
                    if comment_author.strip() and comment_text.strip():
                        comments.append({
                            "author": comment_author.strip(),
                            "text": comment_text.strip(),
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                        df.at[idx,"comments"] = json.dumps(comments, ensure_ascii=False)
                        df.to_csv(POSTS_FILE,index=False)
                        st.session_state[submitted_key] = True
                        st.experimental_rerun()

                st.markdown("---")

# ---------- 글 작성 ----------
with tab2:
    st.header("✏️ 글 작성하기")
    title = st.text_input("제목")
    content = st.text_area("내용")
    author = st.text_input("작성자 이름")

    existing_categories = df["category"].dropna().unique().tolist()
    category = st.selectbox("카테고리 선택", existing_categories + ["새 카테고리 추가"])
    new_category = ""
    if category=="새 카테고리 추가":
        new_category = st.text_input("새 카테고리 이름 입력")
    final_category = new_category if category=="새 카테고리 추가" else category

    image = st.file_uploader("이미지 업로드", type=["png","jpg","jpeg"])

    if st.button("글 저장하기"):
        if title.strip()=="" or content.strip()=="" or author.strip()=="":
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
                "title": title,
                "content": content,
                "author": author,
                "category": final_category,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "image": img_path,
                "likes":0,
                "comments":json.dumps([])
            }
            df = pd.concat([df, pd.DataFrame([new_post])], ignore_index=True)
            df.to_csv(POSTS_FILE,index=False)
            st.success("✅ 글이 저장되었습니다! 글 목록 탭에서 확인하세요.")
