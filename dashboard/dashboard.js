"use strict";

const refreshButton = document.querySelector("#refresh-dashboard");
const renderedAt = document.querySelector("#rendered-at");

function showChartEmpty(container, message) {
  if (!container) {
    return;
  }
  container.replaceChildren();
  const empty = document.createElement("div");
  empty.className = "chart-empty";
  empty.textContent = message;
  container.appendChild(empty);
}

function makeBarLine(label, value, maximum, fillClass, suffix) {
  const line = document.createElement("div");
  line.className = "bar-line";

  const name = document.createElement("span");
  name.className = "bar-name";
  name.textContent = label;

  const track = document.createElement("span");
  track.className = "bar-track";
  const fill = document.createElement("span");
  fill.className = `bar-fill ${fillClass}`;
  fill.style.width = `${Math.max(0, Math.min(100, (value / maximum) * 100))}%`;
  track.appendChild(fill);

  const formattedValue = document.createElement("span");
  formattedValue.className = "bar-value";
  formattedValue.textContent = `${value.toFixed(1)}${suffix}`;

  line.append(name, track, formattedValue);
  return line;
}

function makeChartRow(label) {
  const row = document.createElement("div");
  row.className = "chart-row";
  const rowLabel = document.createElement("span");
  rowLabel.className = "chart-row-label";
  rowLabel.textContent = label;
  row.appendChild(rowLabel);
  return row;
}

function renderPerformanceChart(results) {
  const container = document.querySelector("#performance-chart");
  if (!Array.isArray(results) || results.length === 0) {
    showChartEmpty(container, "Benchmark data will appear here.");
    return;
  }

  const rows = results.slice(0, 6);
  const maximum = Math.max(...rows.map((row) => Number(row.before_avg_ms) || 0), 1);
  container.replaceChildren();
  rows.forEach((result) => {
    const row = makeChartRow(result.query_id || "Query");
    row.append(
      makeBarLine("Before", Number(result.before_avg_ms) || 0, maximum, "bar-fill-before", " ms"),
      makeBarLine("After", Number(result.after_avg_ms) || 0, maximum, "bar-fill-after", " ms"),
    );
    container.appendChild(row);
  });
}

function renderRecommendationChart(recommendations) {
  const container = document.querySelector("#recommendation-chart");
  if (!Array.isArray(recommendations) || recommendations.length === 0) {
    showChartEmpty(container, "Recommendation scores will appear here.");
    return;
  }

  const rows = recommendations.slice(0, 6);
  const maximum = Math.max(...rows.map((row) => Number(row.score) || 0), 1);
  container.replaceChildren();
  rows.forEach((recommendation) => {
    const row = makeChartRow(recommendation.candidate_id || "Candidate");
    row.append(makeBarLine("Score", Number(recommendation.score) || 0, maximum, "bar-fill-score", ""));
    container.appendChild(row);
  });
}

function renderFrequencyChart(queries) {
  const container = document.querySelector("#frequency-chart");
  if (!Array.isArray(queries) || queries.length === 0) {
    showChartEmpty(container, "Workload frequency will appear here.");
    return;
  }

  const grouped = new Map();
  queries.forEach((query) => {
    const current = grouped.get(query.query_id) || { count: 0, totalMs: 0 };
    current.count += 1;
    current.totalMs += Number(query.execution_time_ms) || 0;
    grouped.set(query.query_id, current);
  });
  const rows = [...grouped.entries()].sort((left, right) => right[1].count - left[1].count).slice(0, 8);
  const maximum = Math.max(...rows.map(([, value]) => value.count), 1);
  container.replaceChildren();
  rows.forEach(([queryId, value]) => {
    const row = makeChartRow(queryId || "Query");
    row.append(makeBarLine("Runs", value.count, maximum, "bar-fill-frequency", ""));
    const average = document.createElement("span");
    average.className = "chart-row-value";
    average.textContent = `Average latency ${ (value.totalMs / value.count).toFixed(1) } ms`;
    row.appendChild(average);
    container.appendChild(row);
  });
}

showChartEmpty(document.querySelector("#performance-chart"), "Benchmark data will appear here.");
showChartEmpty(document.querySelector("#recommendation-chart"), "Recommendation scores will appear here.");
showChartEmpty(document.querySelector("#frequency-chart"), "Workload frequency will appear here.");

window.QueryScaleDashboard = Object.freeze({
  renderPerformanceChart,
  renderRecommendationChart,
  renderFrequencyChart,
});

if (refreshButton) {
  refreshButton.addEventListener("click", () => window.location.reload());
}

if (renderedAt) {
  renderedAt.textContent = `Shell loaded ${new Date().toLocaleTimeString()}`;
}