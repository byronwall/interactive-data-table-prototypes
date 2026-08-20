(() => {
  "use strict";
  const current = document.currentScript;
  const base = new URL("./runtime/", current.src);
  const files = ["payload-part-01.js", "payload-part-02.js", "payload-part-03.js", "payload-part-04.js", "payload-part-05.js", "payload-part-06.js", "payload-part-07.js"];
  window.__TABLE_RUNTIME_PAYLOAD__ = [];
  document.documentElement.style.visibility = "hidden";

  async function unpack() {
    const encoded = window.__TABLE_RUNTIME_PAYLOAD__.join("");
    const compressed = Uint8Array.from(atob(encoded), (character) => character.charCodeAt(0));
    if (!("DecompressionStream" in window)) throw new Error("This browser does not support the built-in gzip stream used by the local prototype runtime.");
    const stream = new Blob([compressed]).stream().pipeThrough(new DecompressionStream("gzip"));
    return new Response(stream).json();
  }

  async function finish() {
    const runtime = await unpack();
    const style = document.createElement("style");
    style.setAttribute("data-table-runtime", "core");
    style.textContent = runtime.css;
    document.head.append(style);

    const script = document.createElement("script");
    script.setAttribute("data-table-runtime", "app");
    script.textContent = runtime.app;
    document.head.append(script);
    delete window.__TABLE_RUNTIME_PAYLOAD__;
    document.documentElement.style.visibility = "";
  }

  function fail(path, error) {
    console.error("[table-variants] runtime load failed", error);
    document.documentElement.style.visibility = "";
    const message = document.createElement("p");
    message.setAttribute("role", "alert");
    message.style.cssText = "margin:2rem;font:600 16px system-ui;color:#8b1e2d";
    message.textContent = `The table runtime could not load ${path}.`;
    document.body.prepend(message);
  }

  function load(index) {
    if (index >= files.length) {
      finish().catch((error) => fail("the compressed payload", error));
      return;
    }
    const script = document.createElement("script");
    script.src = new URL(files[index], base).toString();
    script.async = false;
    script.onload = () => load(index + 1);
    script.onerror = () => fail(files[index], new Error("Script request failed"));
    document.head.append(script);
  }

  load(0);
})();
