async function loadResults() {
  const [scoresRes, graphsRes, advicesRes] = await Promise.all([
    fetch("/analysis/members_page/"),
    fetch("/analysis/graphs/me/"),
    fetch("/analysis/advices/me/")
  ])

  const scores = await scoresRes.json()
  const graphs = await graphsRes.json()
  const advices = await advicesRes.json()

  renderGraph(scores)
  renderGraphData(graphs)
  renderAdvice(advices)
}

loadResults()
