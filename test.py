with tab1:
    st.header("📖 글 목록")
    df = pd.read_csv(POSTS_FILE)
    comments_df = pd.read_csv(COMMENTS_FILE)

    if df.empty:
        st.info("아직 작성된 글이 없습니다.")
    else:
        # 카테고리 필터
        categories = ["전체"] + sorted(df["category"].dropna().unique().tolist())
        selected_category = st.selectbox("카테고리 선택", categories)

        if selected_category != "전체":
            df = df[df["category"] == selected_category]

        if df.empty:
            st.info("해당 카테고리에는 글이 없습니다.")
        else:
            # --- 정렬 순서 선택 ---
            sort_order = st.radio("정렬 순서", ["최신순", "오래된순"], horizontal=True)
            df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d %H:%M", errors="coerce")
            df = df.sort_values("date", ascending=(sort_order == "오래된순")).reset_index(drop=True)

            for idx, row in df.iterrows():
                expander_label = f"{row['title']}  |  {row['author']}"
                with st.expander(expander_label):
                    st.caption(f"작성일: {row['date'].strftime('%Y-%m-%d %H:%M')} | 카테고리: {row['category']}")
                    if isinstance(row["image"], str) and row["image"] and os.path.exists(row["image"]):
                        st.image(row["image"], use_container_width=True)
                    st.write(row["content"])
                    st.markdown("---")

                    # --- 좋아요 기능 ---
                    col1, col2 = st.columns([1,4])
                    with col1:
                        if st.button("👍 좋아요", key=f"like_{idx}"):
                            df_all = pd.read_csv(POSTS_FILE)
                            # title로 찾아 likes 증가
                            post_idx = df_all[df_all["title"] == row["title"]].index[0]
                            df_all.loc[post_idx, "likes"] = int(df_all.loc[post_idx, "likes"]) + 1
                            df_all.to_csv(POSTS_FILE, index=False)
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
