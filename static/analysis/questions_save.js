const STORAGE_KEY = "answers"

/* 取得 */
function getAnswers() {
  return JSON.parse(sessionStorage.getItem(STORAGE_KEY) || "{}")
}

/* 最終送信 */
async function submitAll() {
  const answers = getAnswers()
  
  // is_profile_public の値を取得（チェックされていればtrue、なければfalse）
  const isProfilePublicCheckbox = document.querySelector('input[name="is_profile_public"]')
  const isProfilePublic = isProfilePublicCheckbox ? isProfilePublicCheckbox.checked : false

  try {
    const res = await fetch("/analysis/answers/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify({ 
        answers,
        is_profile_public: isProfilePublic
      })
    })

    if (res.ok) {
      const data = await res.json()
      sessionStorage.removeItem(STORAGE_KEY)
      // personal_analysisにリダイレクト
      window.location.href = data.redirect_url || "/analysis/personal_analysis/"
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
