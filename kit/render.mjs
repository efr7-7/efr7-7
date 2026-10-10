// Renders the profile README's header and contributions card as SVGs, in
// Newsreader (SIL OFL) set as outlines so they look the same everywhere.
// Palette from Immiscible's brand: ink, paper, one coral accent.
// Run: GH_TOKEN=... node kit/render.mjs   (the daily workflow does this)
import { readFileSync, writeFileSync } from "node:fs";
const dir = new URL(".", import.meta.url).pathname;
const G = JSON.parse(readFileSync(dir + "glyphs.json", "utf8"));
const USER = "eoinforker", FIRST = 2020;
const THEMES = {
  light: { ink: "#0E1019", muted: "#5B6170", bar: "#CDD2DC" },
  dark: { ink: "#EEF1F6", muted: "#8B91A1", bar: "#2F3443" },
};
const CORAL = "#F0563A";

function width(style, s, size) {
  const f = G[style];
  return [...s].reduce((w, c) => w + (f.glyphs[c]?.w ?? f.upm * 0.3), 0) * size / f.upm;
}
let used = new Map();
const gid = (style, c) => {
  const id = `${style[0]}${c.codePointAt(0).toString(16)}`;
  used.set(id, G[style].glyphs[c].d);
  return id;
};
function text(style, s, size, x, y, fill, anchor = "start") {
  const f = G[style], k = size / f.upm;
  if (anchor === "middle") x -= width(style, s, size) / 2;
  if (anchor === "end") x -= width(style, s, size);
  let out = "", cx = 0;
  for (const c of s) {
    const g = f.glyphs[c];
    if (g?.d) out += `<use href="#${gid(style, c)}" transform="translate(${(x + cx * k).toFixed(2)} ${y}) scale(${k.toFixed(5)} ${(-k).toFixed(5)})"/>`;
    cx += g?.w ?? f.upm * 0.3;
  }
  return `<g fill="${fill}">${out}</g>`;
}
const svg = (w, h, title, body) => {
  const defs = [...used].map(([id, d]) => `<path id="${id}" d="${d}"/>`).join("");
  used = new Map();
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" role="img" aria-label="${title}"><title>${title}</title><defs>${defs}</defs>${body}</svg>\n`;
};
const fmt = (n) => n.toLocaleString("en-GB");

async function totals() {
  const now = new Date().getUTCFullYear(), years = [];
  for (let y = FIRST; y <= now; y++) years.push(y);
  const q = `{user(login:"${USER}"){${years.map((y) =>
    `y${y}:contributionsCollection(from:"${y}-01-01T00:00:00Z",to:"${y}-12-31T23:59:59Z"){contributionCalendar{totalContributions}}`).join(" ")}}}`;
  const r = await fetch("https://api.github.com/graphql", {
    method: "POST",
    headers: { Authorization: `bearer ${process.env.GH_TOKEN}`, "Content-Type": "application/json" },
    body: JSON.stringify({ query: q }),
  });
  const j = await r.json();
  if (!j.data) throw new Error(JSON.stringify(j));
  return years.map((y) => ({ y, n: j.data.user[`y${y}`].contributionCalendar.totalContributions }));
}

function header(t) {
  const name = "eóin forker", size = 64, x = 2, y = 84;
  return svg(840, 140, "eóin forker, building on my own in oxford",
    text("display", name, size, x, y, t.ink) +
    text("display", ".", size, x + width("display", name, size), y, CORAL) +
    text("italic", "building on my own in oxford", 22, x + 2, 124, t.muted));
}

function card(t, rows) {
  const cur = rows.at(-1), all = rows.reduce((s, r) => s + r.n, 0);
  const max = Math.max(...rows.map((r) => r.n)), bw = 30, x0 = 400, x1 = 836;
  const gap = (x1 - x0 - bw * rows.length) / (rows.length - 1), base = 170, hmax = 128;
  let bars = "";
  rows.forEach((r, i) => {
    const h = Math.max(2, Math.round((r.n / max) * hmax)), x = x0 + i * (bw + gap);
    bars += `<rect x="${x.toFixed(1)}" y="${base - h}" width="${bw}" height="${h}" rx="2" fill="${r === cur ? CORAL : t.bar}"/>`;
    bars += text("text", `’${String(r.y).slice(2)}`, 14, x + bw / 2, base + 24, r === cur ? t.ink : t.muted, "middle");
  });
  return svg(840, 210, `${fmt(cur.n)} contributions in ${cur.y}, ${fmt(all)} since ${FIRST}`,
    text("display", fmt(cur.n), 76, 0, 112, t.ink) +
    text("italic", `contributions in ${cur.y}`, 22, 2, 150, t.muted) +
    text("text", `${fmt(all)} since ${FIRST}`, 16, 2, 186, t.muted) + bars);
}

const rows = await totals();
for (const [k, t] of Object.entries(THEMES)) {
  writeFileSync(dir + `../header-${k}.svg`, header(t));
  writeFileSync(dir + `../contributions-${k}.svg`, card(t, rows));
}
console.log(rows.map((r) => `${r.y}:${r.n}`).join(" "));
