import assert from "node:assert/strict";
import test from "node:test";
import { preparePreviewHtml } from "./build-preview.mjs";

test("preview navigation, media and canonicals stay under /dev/", () => {
  const html = preparePreviewHtml(`<!doctype html><html><head>
    <link rel="canonical" href="https://alexzhu.io/travel/japan26/">
    <link rel="stylesheet" href="/css/styles.css">
  </head><body>
    <a href="/">Home</a><a href="/travel/">Travel</a>
    <img src="/assets/photos/japan26/IMG_7307.jpg">
    <audio src="/assets/audio/debussy_arabesque1.mp3"></audio>
    <video poster="/assets/poster.jpg"><source src="/assets/trip.mp4"></video>
    <script src="/js/main.js"></script>
  </body></html>`);
  for (const url of ["/dev/", "/dev/travel/", "/dev/css/styles.css",
    "/dev/assets/photos/japan26/IMG_7307.jpg",
    "/dev/assets/audio/debussy_arabesque1.mp3", "/dev/assets/poster.jpg",
    "/dev/assets/trip.mp4", "/dev/js/main.js"]) {
    assert.ok(html.includes(`="${url}"`), url);
  }
  assert.ok(html.includes('href="https://alexzhu.io/dev/travel/japan26/"'));
  assert.ok(html.includes('name="robots" content="noindex, nofollow"'));
});

test("external URLs, fragments, generated assets and inline scripts are preserved", () => {
  const html = preparePreviewHtml(`<a href="https://example.com/">External</a>
    <a href="//cdn.example.com/">CDN</a><a href="#trips">Jump</a>
    <a href="mailto:alex@alexzhu.io">Mail</a>
    <script src="/dev/_astro/page.js"></script>
    <script>const example = '<img src="/example.jpg">';</script>`);
  for (const url of ["https://example.com/", "//cdn.example.com/", "#trips",
    "mailto:alex@alexzhu.io", "/dev/_astro/page.js"]) {
    assert.ok(html.includes(`="${url}"`), url);
  }
  assert.ok(html.includes(`const example = '<img src="/example.jpg">';`));
  assert.ok(!html.includes("/dev/dev/"));
});

test("legacy page redirects point into the preview", () => {
  const html = preparePreviewHtml(`<meta name="robots" content="noindex">
    <meta http-equiv="refresh" content="0;url=/travel/">
    <a href="/travel/">Redirect</a>`);
  assert.ok(html.includes('content="0;url=/dev/travel/"'));
  assert.ok(html.includes('href="/dev/travel/"'));
  assert.equal(html.match(/name="robots"/g).length, 1);
});
