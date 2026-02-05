const STORAGE_KEY = "analysis_answers"

/* 取得 */
function getAnswers() {
  return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}")
}

/* 保存 */
function saveAnswers() {
  const answers = getAnswers()

  document.querySelectorAll(".answer").forEach(el => {
    if (el.value !== "") {
      answers[el.dataset.qid] = el.value
    }
  })

  localStorage.setItem(STORAGE_KEY, JSON.stringify(answers))
}

/* 次ページ */
function nextPage(page) {
  saveAnswers()
  window.location.href = `/analysis/questions/${page}/`
}

/* 最終送信 */
async function submitAll() {
  saveAnswers()

  const answers = getAnswers()

  try {
    const res = await fetch("/analysis/answers/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify({ answers })
    })

    if (res.ok) {
      const data = await res.json()
      localStorage.removeItem(STORAGE_KEY)
      // members_pageにリダイレクト
      window.location.href = data.redirect_url || "/analysis/members_page/"
    } else {
      alert(`エラーが発生しました: ${res.status}`)
    }
  } catch (error) {
    console.error("通信エラー:", error)
    alert("通信エラーが発生しました")
  }
}

/* CSRF */
function getCookie(name) {
  return document.cookie
    .split("; ")
    .find(row => row.startsWith(name))
    ?.split("=")[1]
}

window.submitAll = submitAll
window.nextPage = nextPage
