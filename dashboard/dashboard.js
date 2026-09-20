"use strict";

const refreshButton = document.querySelector("#refresh-dashboard");
const renderedAt = document.querySelector("#rendered-at");

if (refreshButton) {
  refreshButton.addEventListener("click", () => window.location.reload());
}

if (renderedAt) {
  renderedAt.textContent = `Shell loaded ${new Date().toLocaleTimeString()}`;
}