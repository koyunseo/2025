# --- 글 보기 탭 ---
with tab1:
    st.header("📖 글 목록")
    df = pd.read_csv("posts.csv")

    # 좋아요/댓글 필드 초기화
    if "likes" not in df.columns:
        df["likes"] = 0
    if "comments" not in df.columns:
        df["comments"] = [[] for _ in range(len(df))]

    if not df.empty:
        categories = ["전체"] + sorted(df["category"].dropna().unique().tolist())
        selected_category = st.selectbox("카테고리 선택", categories)

        # 정렬 옵션
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
                    if isinstance(row["image"], str) and row["image"] and os.path.exists(row["image"]):
                        st.image(row["image"], use_container_width=True)
                    st.write(row["content"])
                    # 좋아요 버튼
                    if st.button(f"👍 좋아요 ({int(row['likes'])})", key=f"like_{i}"):
                        df.loc[i, "likes"] = int(row["likes"]) + 1
                        df.to_csv("posts.csv", index=False)
                        st.rerun()

                    # 댓글 표시 및 작성 (이전 코드 유지)
                    st.markdown("**댓글:**")
                    comments = eval(row["comments"]) if isinstance(row["comments"], str) else row["comments"]
                    if comments:
                        for c in comments:
                            st.write(f"- {c}")
                    else:
                        st.write("아직 댓글이 없습니다.")

                    comment = st.text_input("댓글 작성", key=f"comment_{i}")
                    if st.button("댓글 달기", key=f"btn_comment_{i}"):
                        comments.append(comment)
                        df.loc[i, "comments"] = str(comments)
                        df.to_csv("posts.csv", index=False)
                        st.success("댓글이 추가되었습니다!")
                        st.rerun()

                    # --- 글 수정/삭제 버튼 ---
                    st.markdown("---")
                    if st.button("✏️ 글 수정", key=f"edit_{i}"):
                        st.session_state["edit_index"] = i
                        st.session_state["edit_trigger"] = True
                        st.rerun()

                    if st.button("🗑️ 글 삭제", key=f"delete_{i}"):
                        df = df.drop(i).reset_index(drop=True)
                        df.to_csv("posts.csv", index=False)
                        st.success("글이 삭제되었습니다!")
                        st.rerun()

# --- 글 작성 탭 (수정 기능 포함) ---
with tab2:
    st.header("✏️ 글 작성하기")

    # 수정 모드 확인
    if "edit_trigger" in st.session_state and st.session_state["edit_trigger"]:
        edit_idx = st.session_state["edit_index"]
        df = pd.read_csv("posts.csv")
        row = df.loc[edit_idx]
        title = st.text_input("제목", row["title"])
        content = st.text_area("내용", row["content"])
        author = st.text_input("작성자 이름", row["author"])
        existing_categories = df["category"].dropna().unique().tolist()
        category = st.selectbox("카테고리 선택", existing_categories + ["새 카테고리 추가"], index=existing_categories.index(row["category"]) if row["category"] in existing_categories else 0)
        new_category = ""
        image = st.file_uploader("이미지 업로드", type=["png", "jpg", "jpeg"])
    else:
        title = st.text_input("제목")
        content = st.text_area("내용")
        author = st.text_input("작성자 이름")
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
            img_path = ""
            if image is not None:
                os.makedirs("images", exist_ok=True)
                img_path = os.path.join("images", image.name)
                with open(img_path, "wb") as f:
                    f.write(image.getbuffer())

            df = pd.read_csv("posts.csv")

            if "edit_trigger" in st.session_state and st.session_state.get("edit_trigger", False):
                # 수정 모드
                idx = st.session_state["edit_index"]
                df.loc[idx, "title"] = title
                df.loc[idx, "content"] = content
                df.loc[idx, "author"] = author
                df.loc[idx, "category"] = final_category
                if img_path:
                    df.loc[idx, "image"] = img_path
                df.to_csv("posts.csv", index=False)
                st.success("✅ 글이 수정되었습니다!")
                st.session_state["edit_trigger"] = False
                st.rerun()
            else:
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
