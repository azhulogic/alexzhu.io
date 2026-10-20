import { readdir, readFile, writeFile } from "node:fs/promises";
import { spawnSync } from "node:child_process";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { parse, parseFragment, serialize } from "parse5";

const base = "/dev/";
const site = "https://alexzhu.io";

// Astro handles generated asset URLs; content also contains root-relative media
// and navigation links that must stay inside the preview.
function previewUrl(value) {
  if (value.startsWith(`${site}/`)) {
    return site + previewUrl(value.slice(site.length));
  }
  if (!value.startsWith("/") || value.startsWith("//") ||
      value === "/dev" || value.startsWith(base)) {
    return value;
  }
  return base + value.slice(1);
}

export function preparePreviewHtml(html) {
  const document = parse(html);
  function visit(node) {
    const attrs = node.attrs ?? [];
    for (const attr of attrs) {
      if (["href", "src", "poster", "action"].includes(attr.name)) {
        attr.value = previewUrl(attr.value);
      }
      if (attr.name === "content" && attrs.some((item) =>
        item.name === "http-equiv" && item.value.toLowerCase() === "refresh")) {
        attr.value = attr.value.replace(/(url=)(.*)$/i, (_, prefix, url) =>
          prefix + previewUrl(url));
      }
    }
    if (node.tagName === "head") {
      const robots = node.childNodes.filter((child) => child.tagName === "meta" &&
        child.attrs.some((attr) => attr.name === "name" && attr.value === "robots"));
      for (const meta of robots) {
        meta.attrs = meta.attrs.filter((attr) => attr.name !== "content");
        meta.attrs.push({ name: "content", value: "noindex, nofollow" });
      }
      if (robots.length === 0) {
        const meta = parseFragment('<meta name="robots" content="noindex, nofollow">').childNodes[0];
        meta.parentNode = node;
        node.childNodes.push(meta);
      }
    }
    for (const child of node.childNodes ?? []) visit(child);
    if (node.content) visit(node.content);
  }
  visit(document);
  return serialize(document);
}

async function prepareDirectory(directory) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const path = join(directory, entry.name);
    if (entry.isDirectory()) await prepareDirectory(path);
    else if (entry.name.endsWith(".html")) {
      await writeFile(path, preparePreviewHtml(await readFile(path, "utf8")));
    }
  }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
  const result = spawnSync(process.execPath,
    [join(root, "node_modules/astro/bin/astro.mjs"), "build", "--base", base], {
      cwd: root,
      env: { ...process.env, SHOW_PROJECT_DRAFTS: "true" },
      stdio: "inherit"
    });
  if (result.error) throw result.error;
  if (result.status !== 0) process.exit(result.status ?? 1);
  await prepareDirectory(join(root, "dist"));
}
