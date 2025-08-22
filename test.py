<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>나의 블로그</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header>
        <h1>나의 블로그</h1>
        <p>개발 · 일상 · 기록</p>
    </header>

    <main>
        <section id="posts">
            <!-- 글 목록 -->
            <article onclick="showPost(1)">
                <h2>첫 번째 글 제목</h2>
                <p>첫 글의 간단한 요약...</p>
            </article>

            <article onclick="showPost(2)">
                <h2>두 번째 글 제목</h2>
                <p>두 번째 글의 간단한 요약...</p>
            </article>
        </section>

        <!-- 글 본문 -->
        <section id="post-content" class="hidden">
            <button onclick="goBack()">← 목록으로</button>
            <h2 id="post-title"></h2>
            <p id="post-body"></p>
        </section>
    </main>

    <footer>
        <p>© 2025 나의 블로그</p>
    </footer>

    <script src="script.js"></script>
</body>
</html>

body {
    font-family: 'Arial', sans-serif;
    margin: 0;
    background: #f9f9f9;
    color: #333;
}

header {
    background: #4b6cb7;
    color: white;
    text-align: center;
    padding: 2rem 1rem;
}

main {
    max-width: 800px;
    margin: 2rem auto;
    padding: 0 1rem;
}

article {
    background: white;
    padding: 1rem;
    margin-bottom: 1rem;
    border-radius: 10px;
    cursor: pointer;
    transition: transform 0.2s ease;
}

article:hover {
    transform: translateY(-5px);
    background: #eef2ff;
}

.hidden {
    display: none;
}

button {
    background: #4b6cb7;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 5px;
    cursor: pointer;
}

const posts = {
    1: {
        title: "첫 번째 글 제목",
        body: "여기에 첫 번째 글의 본문 내용을 작성합니다. HTML 태그를 넣을 수도 있어요!"
    },
    2: {
        title: "두 번째 글 제목",
        body: "여기에 두 번째 글의 본문 내용을 작성합니다. 여러 문단도 가능합니다."
    }
};

function showPost(id) {
    document.getElementById("posts").classList.add("hidden");
    document.getElementById("post-content").classList.remove("hidden");
    document.getElementById("post-title").innerText = posts[id].title;
    document.getElementById("post-body").innerText = posts[id].body;
}

function goBack() {
    document.getElementById("post-content").classList.add("hidden");
    document.getElementById("posts").classList.remove("hidden");
}
