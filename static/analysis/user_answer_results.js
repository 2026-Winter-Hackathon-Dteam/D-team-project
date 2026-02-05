function getCookie(name) {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop().split(";").shift()
}

async function loadResults() {
  if (!window.TEAM_ID) {
    console.warn("TEAM_ID is missing")
    return
  }

  const payload = JSON.stringify({ team_id: window.TEAM_ID })

  const [graphsRes, advicesRes] = await Promise.all([
    fetch("/analysis/graphs/me/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: payload,
    }),
    fetch("/analysis/advices/me/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: payload,
    }),
  ])

  const graphs = await graphsRes.json()
  const advices = await advicesRes.json()

  if (typeof renderGraphData === "function") {
    renderGraphData(graphs)
  } else {
    console.log("graphs:", graphs)
  }

  if (typeof renderAdvice === "function") {
    renderAdvice(advices)
  } else {
    console.log("advices:", advices)
  }
}

loadResults()
