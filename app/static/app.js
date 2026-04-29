const form = document.querySelector("#searchForm");
const rows = document.querySelector("#licenseRows");
const summary = document.querySelector("#resultSummary");
const metricMatches = document.querySelector("#metricMatches");
const metricSoon = document.querySelector("#metricSoon");
const metricStates = document.querySelector("#metricStates");
const activeWindow = document.querySelector("#activeWindow");
const notice = document.querySelector("#notice");
const saveMonitor = document.querySelector("#saveMonitor");
const exportCsv = document.querySelector("#exportCsv");
const resetFilters = document.querySelector("#resetFilters");
const chips = Array.from(document.querySelectorAll(".chip"));

let apiBaseUrl = "";
let currentParams = new URLSearchParams({
  renewal_window_min: "0",
  renewal_window_max: "60",
  limit: "100",
});

function apiUrl(path) {
  return `${apiBaseUrl}${path}`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function activeChip() {
  return chips.find((chip) => chip.classList.contains("active"));
}

function applyFormParams() {
  const data = new FormData(form);
  const params = new URLSearchParams();

  for (const [key, value] of data.entries()) {
    const clean = String(value).trim();
    if (clean) params.set(key, clean);
  }

  const chip = activeChip();
  if (chip) {
    if (chip.dataset.windowMin) params.set("renewal_window_min", chip.dataset.windowMin);
    if (chip.dataset.windowMax) params.set("renewal_window_max", chip.dataset.windowMax);
  }

  params.set("limit", "100");
  currentParams = params;
  activeWindow.textContent = windowLabel(params);
  return params;
}

function windowLabel(params) {
  const min = params.get("renewal_window_min");
  const max = params.get("renewal_window_max");
  if (!min && !max) return "Any renewal window";
  return `${min || 0}-${max} days`;
}

function formatDate(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("en", {
    year: "numeric",
    month: "short",
    day: "numeric",
  }).format(new Date(`${value}T00:00:00`));
}

function freshness(value) {
  if (!value) return "";
  const date = new Date(value);
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}

function renderRows(licenses) {
  if (!licenses.length) {
    rows.innerHTML = `<tr><td class="empty" colspan="6">No records match this search.</td></tr>`;
    return;
  }

  rows.innerHTML = licenses
    .map((license) => {
      const soon = license.renewal_window_days <= 30 ? "soon" : "";
      const fullName = escapeHtml(license.full_name);
      const businessName = escapeHtml(license.business_name || "No business listed");
      const profession = escapeHtml(license.profession);
      const licenseType = escapeHtml(license.license_type_code);
      const licenseNumber = escapeHtml(license.license_number);
      const specialty = escapeHtml(license.specialty || "No specialty");
      const status = escapeHtml(license.status_normalized);
      const city = escapeHtml(license.address_city || "");
      const state = escapeHtml(license.source_state);
      const zip = escapeHtml(license.address_zip || "");
      return `
        <tr>
          <td>
            <div class="primary-line">${fullName}</div>
            <div class="secondary-line">${businessName}</div>
          </td>
          <td>
            <div class="primary-line">${profession}</div>
            <div class="secondary-line">${licenseType} ${licenseNumber} · ${specialty}</div>
          </td>
          <td><span class="status">${status}</span></td>
          <td>
            <div class="days ${soon}">${license.renewal_window_days} days</div>
            <div class="secondary-line">${formatDate(license.expiration_date)}</div>
          </td>
          <td>
            <div class="primary-line">${city}, ${state}</div>
            <div class="secondary-line">${zip}</div>
          </td>
          <td>
            <div class="primary-line">${freshness(license.source_fetched_at)}</div>
            <div class="secondary-line">Source observed</div>
          </td>
        </tr>
      `;
    })
    .join("");
}

function renderMetrics(payload) {
  const licenses = payload.results;
  const states = new Set(licenses.map((license) => license.source_state));
  const soon = licenses.filter((license) => license.renewal_window_days <= 30).length;

  metricMatches.textContent = payload.total;
  metricSoon.textContent = soon;
  metricStates.textContent = states.size;
  summary.textContent = `${payload.total} records sorted by nearest expiration`;
}

async function search() {
  const params = applyFormParams();
  summary.textContent = "Searching license boards...";
  const response = await fetch(apiUrl(`/licenses?${params.toString()}`));
  if (!response.ok) {
    const message = response.status === 503 ? "Data service is temporarily unavailable." : "Search failed.";
    throw new Error(message);
  }
  const payload = await response.json();
  renderMetrics(payload);
  renderRows(payload.results);
}

chips.forEach((chip) => {
  chip.addEventListener("click", () => {
    chips.forEach((item) => item.classList.remove("active"));
    chip.classList.add("active");
    search().catch(showError);
  });
});

form.addEventListener("submit", (event) => {
  event.preventDefault();
  search().catch(showError);
});

resetFilters.addEventListener("click", () => {
  form.reset();
  chips.forEach((chip) => chip.classList.remove("active"));
  chips[0].classList.add("active");
  search().catch(showError);
});

exportCsv.addEventListener("click", () => {
  const params = new URLSearchParams(currentParams);
  window.location.href = apiUrl(`/licenses/export.csv?${params.toString()}`);
});

saveMonitor.addEventListener("click", async () => {
  const params = applyFormParams();
  const response = await fetch(apiUrl("/monitors"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      account_id: "demo-account",
      name: `Renewals: ${windowLabel(params)}`,
      filters: Object.fromEntries(params.entries()),
      window_days: Number(params.get("renewal_window_max") || 60),
    }),
  });

  if (!response.ok) {
    showError(new Error("Monitor could not be saved"));
    return;
  }

  const monitor = await response.json();
  document.querySelector("#monitorState").textContent = "Saved";
  notice.textContent = `Monitor saved: ${monitor.name}`;
});

function showError(error) {
  summary.textContent = "Something went wrong.";
  notice.textContent = error.message;
}

async function boot() {
  const response = await fetch("/config");
  if (response.ok) {
    const config = await response.json();
    apiBaseUrl = config.apiBaseUrl || "";
  }
  await search();
}

boot().catch(showError);
