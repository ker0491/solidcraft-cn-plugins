// SolidCraft 中文插件站：读取 data/plugins.json，提供搜索、状态与分类筛选。
const $ = (s) => document.querySelector(s);
let plugins = [];
let category = new URLSearchParams(location.search).get("category");
let state = "all";

function searchable(p) {
  return [
    p.name, p.nameOriginal, p.description, p.descriptionOriginal,
    p.owner, p.repo, p.category, p.categoryOriginal, ...(p.topics || []),
  ].join(" ").toLowerCase();
}

function message(s) {
  const el = document.createElement("p");
  el.className = "empty-list";
  el.textContent = s;
  return el;
}

function initials(name) {
  return (name || "?").trim().charAt(0).toUpperCase();
}

function card(p) {
  const node = $("#card").content.cloneNode(true);
  const page = `https://github.com/${p.repo}`;

  const pic = node.querySelector(".pic");
  pic.href = page;
  pic.querySelector(".ph").textContent = initials(p.name);
  const img = pic.querySelector("img");
  if (p.image) {
    img.src = p.image;
    img.alt = `${p.name} 插件预览`;
    img.onerror = () => pic.classList.add("empty");
  } else {
    pic.classList.add("empty");
  }

  node.querySelector(".cat").textContent = p.category || "";
  const badge = node.querySelector(".status");
  badge.textContent = p.localized ? "已汉化" : "待汉化";
  badge.classList.add(p.localized ? "on" : "off");

  node.querySelector(".name").textContent = p.name;
  node.querySelector(".ver").textContent = p.localizedVersion || p.version || "";
  const by = node.querySelector(".by");
  by.href = `https://github.com/${p.owner}`;
  by.querySelector("img").src = `${p.avatar}&s=40`;
  by.querySelector("span").textContent = p.owner;
  node.querySelector(".desc").textContent = p.description || "";
  node.querySelector(".original").textContent =
    p.nameZh && p.nameOriginal && p.nameZh !== p.nameOriginal ? p.nameOriginal : "";

  const chips = node.querySelector(".chips");
  for (const topic of (p.topics || []).slice(0, 5)) {
    const span = document.createElement("span");
    span.textContent = topic;
    chips.append(span);
  }

  node.querySelector(".verified").textContent =
    p.wasmSha ? `wasm ${p.wasmSha.slice(0, 12)}… · 与上游一致` : "";

  const zip = node.querySelector(".zip");
  if (p.localizedZip) {
    zip.href = p.localizedZip;
    zip.textContent = "下载中文包";
    zip.title = `${p.localizedVersion}：仅界面文本汉化，执行组件未改动`;
  } else if (p.upstreamZip) {
    zip.href = p.upstreamZip;
    zip.textContent = "下载原版";
    zip.classList.remove("primary");
    zip.title = `${p.upstreamTag || "latest"}：尚未汉化，来自插件作者的原始发布包`;
  } else {
    zip.classList.add("disabled");
    zip.textContent = "暂无安装包";
    zip.removeAttribute("href");
  }
  node.querySelector(".gh").href = page;
  return node;
}

function show() {
  const words = $("#q").value.trim().toLowerCase().split(/\s+/).filter(Boolean);
  const sortKey = $("#sort").value;
  const compare = {
    stars: (a, b) => b.stars - a.stars,
    downloads: (a, b) => b.downloads - a.downloads,
    updated: (a, b) => (b.updated || "").localeCompare(a.updated || ""),
    name: (a, b) => a.name.localeCompare(b.name, "zh-CN"),
    localized: (a, b) => b.stars - a.stars,
  }[sortKey];

  const list = plugins
    .filter((p) => words.every((w) => searchable(p).includes(w)))
    .filter((p) => state === "all" || (state === "localized" ? p.localized : !p.localized))
    .filter((p) => !category || p.category === category)
    .sort((a, b) => Number(b.localized) - Number(a.localized) || compare(a, b));

  $("#list").replaceChildren(...(list.length ? list.map(card) : [message("没有符合条件的插件。")]));
  $("#count").textContent = `显示 ${list.length} / ${plugins.length} 个插件`;
}

function renderCategories() {
  const counts = {};
  for (const p of plugins) counts[p.category] = (counts[p.category] || 0) + 1;
  if (category && !counts[category]) category = null;

  const box = $("#tags");
  const names = [null, ...Object.keys(counts).sort((a, b) => counts[b] - counts[a] || a.localeCompare(b, "zh-CN"))];
  for (const name of names) {
    const button = document.createElement("button");
    button.className = "tag" + (name === category ? " on" : "");
    button.textContent = name ? `${name} (${counts[name]})` : "全部";
    button.onclick = () => {
      category = name;
      box.querySelectorAll(".tag").forEach((el) => el.classList.toggle("on", el === button));
      const url = new URL(location.href);
      if (name) url.searchParams.set("category", name); else url.searchParams.delete("category");
      history.replaceState(null, "", url);
      show();
    };
    box.append(button);
  }
}

function renderStats(data) {
  const items = [
    [data.total, "收录插件"],
    [data.localized, "已汉化"],
    [data.downloadable, "可下载安装包"],
  ];
  $("#stats").replaceChildren(...items.map(([value, label]) => {
    const box = document.createElement("div");
    box.className = "stat";
    const b = document.createElement("b");
    b.textContent = value;
    const span = document.createElement("span");
    span.textContent = label;
    box.append(b, span);
    return box;
  }));
  const date = new Date(data.catalogGenerated || data.generated);
  $("#updated").textContent = `目录更新于 ${date.toLocaleDateString("zh-CN", { year: "numeric", month: "long", day: "numeric" })}`;
}

fetch("data/plugins.json")
  .then((r) => r.json())
  .then((data) => {
    plugins = data.plugins || [];
    renderStats(data);
    renderCategories();
    show();
  })
  .catch(() => $("#list").replaceChildren(message("插件列表加载失败，请稍后重试。")));

$("#q").addEventListener("input", show);
$("#sort").addEventListener("change", show);
$("#state").addEventListener("change", (ev) => { state = ev.target.value; show(); });
