/* ================= API ================= */
// Change this to point at your backend.
const API_BASE_URL = "http://localhost:8000";

async function analyzeRepo(githubUrl) {
  let res;
  try {
    res = await fetch(`${API_BASE_URL}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ github_url: githubUrl }),
    });
  } catch {
    throw { kind: "network" };
  }
  if (res.status === 404) throw { kind: "not_found" };
  if (res.status === 400 || res.status === 422) throw { kind: "invalid" };
  if (!res.ok) throw { kind: "server" };
  const isJson = (res.headers.get("content-type") || "").includes("json");
  return extractText(isJson ? await res.json() : await res.text());
}

// Response shape isn't fixed: accept a string or a common field name.
function extractText(data) {
  if (typeof data === "string") return data;

  const repo = data.repository || {};
  const summary = data.summary || {};
  const architecture = data.architecture || {};

  let output = "";

  // Repository
  if (repo.name) {
    output += `# ${repo.name}\n\n`;
  }

  if (repo.full_name) {
    output += `**Repository:** ${repo.full_name}\n\n`;
  }

  if (repo.language) {
    output += `**Primary Language:** ${repo.language}\n\n`;
  }

  // Summary
  if (summary.overview) {
    output += `## Overview\n\n${summary.overview}\n\n`;
  }

  if (summary.architecture) {
    output += `## Architecture\n\n${summary.architecture}\n\n`;
  }

  // Technologies
  if (Array.isArray(summary.technologies) && summary.technologies.length) {
    output += `## Technologies\n\n`;

    summary.technologies.forEach((tech) => {
      output += `- ${tech}\n`;
    });

    output += `\n`;
  }

  // Main components
  if (Array.isArray(summary.main_components) && summary.main_components.length) {
    output += `## Main Components\n\n`;

    summary.main_components.forEach((component) => {
      output += `- ${component}\n`;
    });

    output += `\n`;
  }

  // Entry points
  const entryPoints =
    summary.entry_points || architecture.entry_points || [];

  if (Array.isArray(entryPoints) && entryPoints.length) {
    output += `## Entry Points\n\n`;

    entryPoints.forEach((entry) => {
      output += `- \`${entry}\`\n`;
    });

    output += `\n`;
  }

  // Architecture components
  if (
    Array.isArray(architecture.components) &&
    architecture.components.length
  ) {
    output += `## Architecture Components\n\n`;

    architecture.components.forEach((component) => {
      output += `- ${component}\n`;
    });

    output += `\n`;
  }

  // Relationships
  if (
    Array.isArray(architecture.relationships) &&
    architecture.relationships.length
  ) {
    output += `## Relationships\n\n`;

    architecture.relationships.forEach((relationship) => {
      output += `- ${relationship}\n`;
    });

    output += `\n`;
  }

  // Data flow
  if (
    Array.isArray(architecture.data_flow) &&
    architecture.data_flow.length
  ) {
    output += `## Data Flow\n\n`;

    architecture.data_flow.forEach((flow) => {
      output += `- ${flow}\n`;
    });

    output += `\n`;
  }

  // Fallback if the backend response doesn't match the expected structure
  if (!output.trim()) {
    return "No readable analysis was returned.";
  }

  return output.trim();
}

/* ================= UI ================= */
const $ = (id) => document.getElementById(id);
const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const field = () => document.querySelector(".field");

const MESSAGES = {
  empty: "Paste a GitHub repository URL first.",
  invalid: "Please enter a valid GitHub repository URL.",
  not_found: "Repository could not be found.",
  server: "Something went wrong while analyzing the repository.",
  network: "Could not connect to RepoMind backend.",
};

function setBusy(busy) {
  $("repo-url").disabled = busy;
  $("analyze-btn").disabled = busy;
  $("analyze-btn").textContent = busy ? "ANALYZING…" : "ANALYZE";
  field().classList.toggle("disabled", busy);
}

function clearAll() {
  $("status").innerHTML = "";
  $("result").innerHTML = "";
  field().classList.remove("invalid");
}

function showError(kind) {
  clearAll();
  if (kind === "empty" || kind === "invalid") field().classList.add("invalid");
  $("status").innerHTML = `<div class="panel error" role="alert"><div class="panel-head">ERROR</div><div class="panel-body"><p>${MESSAGES[kind] || MESSAGES.server}</p></div></div>`;
}

const STEPS = ["Fetching repository", "Reading repository structure", "Understanding source files", "Generating explanation"];

// The API reports no progress, so stages advance on a timer; the last waits for the response.
function showLoading() {
  clearAll();
  $("status").innerHTML = `<div class="panel"><div class="panel-head">ANALYZING REPOSITORY...</div><div class="panel-body"><ul class="steps">${STEPS.map((s) => `<li>${s}</li>`).join("")}</ul><div class="bar"><i></i></div></div></div>`;
  const items = [...document.querySelectorAll(".steps li")];
  let i = 0;
  const tick = () => {
    items.forEach((li, n) => { li.className = n < i ? "done" : n === i ? "active" : ""; });
    if (i < items.length - 1) i++;
  };
  tick();
  const timer = setInterval(tick, 1800);
  return () => clearInterval(timer);
}

function showResult(text) {
  clearAll();
  $("result").innerHTML = `<article class="panel"><div class="panel-head"><span>REPOSITORY ANALYSIS</span><button type="button" class="btn small" id="copy-btn">COPY ↗</button></div><div class="panel-body doc">${renderMarkdown(text)}</div></article>`;
  const btn = $("copy-btn");
  btn.addEventListener("click", async () => {
    try { await navigator.clipboard.writeText(text); } catch { return; }
    btn.textContent = "COPIED ✓";
    btn.classList.add("done");
    setTimeout(() => { btn.textContent = "COPY ↗"; btn.classList.remove("done"); }, 1800);
  });
  const calm = matchMedia("(prefers-reduced-motion: reduce)").matches;
  $("result").scrollIntoView({ behavior: calm ? "auto" : "smooth", block: "start" });
}

const inline = (s) => esc(s).replace(/`([^`]+)`/g, "<code>$1</code>").replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");

// Minimal, escaped markdown: headings, bullets, fenced code, paragraphs.
function renderMarkdown(md) {
  const out = []; let list = false, code = null;
  const closeList = () => { if (list) { out.push("</ul>"); list = false; } };
  for (const line of md.split("\n")) {
    if (line.startsWith("```")) {
      if (code === null) { closeList(); code = []; }
      else { out.push(`<pre><code>${esc(code.join("\n"))}</code></pre>`); code = null; }
      continue;
    }
    if (code !== null) { code.push(line); continue; }
    const h = line.match(/^(#{1,6})\s+(.*)/), li = line.match(/^\s*[-*•]\s+(.*)/);
    if (h) { closeList(); const t = h[1].length === 1 ? 2 : 3; out.push(`<h${t}>${inline(h[2])}</h${t}>`); }
    else if (li) { if (!list) { out.push("<ul>"); list = true; } out.push(`<li>${inline(li[1])}</li>`); }
    else if (line.trim()) { closeList(); out.push(`<p>${inline(line)}</p>`); }
    else closeList();
  }
  closeList();
  return out.join("");
}

/* ================= ROUTER ================= */
// Hash routes: #/ (analyzer) and #/about. Works from any static server or file://.
function route() {
  const name = location.hash.replace(/^#\/?/, "") === "about" ? "about" : "home";
  document.querySelectorAll("[data-view]").forEach((v) => { v.hidden = v.dataset.view !== name; });
  document.querySelectorAll("[data-nav]").forEach((a) => {
    a.toggleAttribute("aria-current", a.dataset.nav === name);
  });
  window.scrollTo(0, 0);
}
window.addEventListener("hashchange", route);

/* ================= APP ================= */
const GITHUB_REPO = /^https?:\/\/(www\.)?github\.com\/[\w.-]+\/[\w.-]+?(\.git)?\/?$/i;

$("repo-url").addEventListener("input", clearAll);

$("analyze-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const url = $("repo-url").value.trim();
  if (!url) return showError("empty");
  if (!GITHUB_REPO.test(url)) return showError("invalid");

  setBusy(true);
  const stopLoading = showLoading();
  try {
    showResult(await analyzeRepo(url));
  } catch (err) {
    showError(err && err.kind ? err.kind : "server");
  } finally {
    stopLoading();
    setBusy(false);
  }
});

route();
