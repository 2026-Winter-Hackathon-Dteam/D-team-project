async function loadResults() {
  const [scoresRes, advicesRes] = await Promise.all([
    fetch("/analysis/results/"),
    fetch("/analysis/advices/me/")
  ])

  const scores = await scoresRes.json()
  const advices = await advicesRes.json()

  renderGraph(scores)
  renderAdvice(advices)
}

loadResults()
