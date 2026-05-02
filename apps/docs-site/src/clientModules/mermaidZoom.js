/**
 * Mermaid Zoom — Docusaurus client module
 *
 * 给 `@docusaurus/theme-mermaid` 渲染出来的 mermaid 图增加:
 *   - hover 时提示"点击放大"
 *   - 点击后全屏查看 SVG 克隆
 *   - 滚轮缩放 / 拖拽移动 / 双击复位 / ESC 或点外部关闭
 *
 * 特点:
 *   - 不修改任何 mermaid 源码或 Docusaurus 主题,只监听 DOM
 *   - 初次通过 DOM + MutationObserver,SPA 路由切换靠 onRouteDidUpdate 兜底
 *   - `dataset.zoomBound` 防止重复绑定
 *   - 样式一次性注入 <style>,不污染全局 CSS
 */

import ExecutionEnvironment from "@docusaurus/ExecutionEnvironment";

const CONTAINER_SELECTOR = ".docusaurus-mermaid-container";
const BOUND_FLAG = "zoomBound";
const STYLE_ID = "mermaid-zoom-style";

function ensureStyle() {
  if (document.getElementById(STYLE_ID)) return;
  const style = document.createElement("style");
  style.id = STYLE_ID;
  style.textContent = `
    ${CONTAINER_SELECTOR} {
      position: relative;
      cursor: zoom-in;
      transition: box-shadow 0.18s ease, transform 0.18s ease;
      border-radius: 24px;
    }
    ${CONTAINER_SELECTOR}:hover {
      transform: translateY(-1px);
      box-shadow:
        0 20px 44px -34px rgba(15, 23, 42, 0.32),
        0 0 0 1px rgba(15, 107, 76, 0.14),
        0 0 0 4px rgba(15, 107, 76, 0.08);
    }
    ${CONTAINER_SELECTOR}::after {
      content: "\\1F50D  \u70B9\u51FB\u653E\u5927";
      position: absolute;
      top: 8px;
      right: 8px;
      padding: 3px 10px;
      font-size: 12px;
      line-height: 1.4;
      color: var(--ifm-font-color-base, #2c2c2c);
      background: var(--ifm-background-color, rgba(255, 255, 255, 0.95));
      border: 1px solid var(--ifm-color-emphasis-200, #e6e6e6);
      border-radius: 999px;
      opacity: 0;
      transition: opacity 0.18s ease;
      pointer-events: none;
      z-index: 2;
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
    }
    ${CONTAINER_SELECTOR}:hover::after {
      opacity: 1;
    }

    .mermaid-zoom-overlay {
      position: fixed;
      inset: 0;
      background: rgba(10, 14, 22, 0.85);
      backdrop-filter: blur(4px);
      -webkit-backdrop-filter: blur(4px);
      z-index: 9999;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: grab;
      animation: mermaid-zoom-fade 0.16s ease-out;
      user-select: none;
    }
    .mermaid-zoom-overlay.grabbing { cursor: grabbing; }

    .mermaid-zoom-stage {
      transform-origin: center center;
      will-change: transform;
      /* 跟随 docusaurus 主题色,保持与 mermaid 节点颜色一致的视觉 context */
      background: var(--ifm-background-surface-color, #ffffff);
      padding: 24px 28px;
      border-radius: 24px;
      border: 1px solid rgba(27, 46, 39, 0.1);
      box-shadow: 0 24px 60px -32px rgba(0, 0, 0, 0.5);
      box-sizing: border-box;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .mermaid-zoom-stage > .docusaurus-mermaid-container,
    .mermaid-zoom-stage > svg {
      display: block;
      width: 100%;
      height: 100%;
      background: transparent;
      box-shadow: none;
      cursor: default;
      margin: 0;
    }
    .mermaid-zoom-stage > .docusaurus-mermaid-container {
      overflow: hidden !important;
    }
    /* 克隆进来的 container 在 overlay 内不再需要 hover 提示气泡 */
    .mermaid-zoom-stage > .docusaurus-mermaid-container::after {
      display: none !important;
    }
    .mermaid-zoom-stage > .docusaurus-mermaid-container > svg {
      width: 100% !important;
      height: 100% !important;
      max-width: none !important;
      max-height: none !important;
    }

    .mermaid-zoom-hint {
      position: fixed;
      bottom: 22px;
      left: 50%;
      transform: translateX(-50%);
      padding: 8px 18px;
      background: rgba(255, 255, 255, 0.08);
      color: #f0f0f0;
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: 999px;
      font-size: 13px;
      letter-spacing: 0.3px;
      pointer-events: none;
      z-index: 10000;
    }

    .mermaid-zoom-close {
      position: fixed;
      top: 18px;
      right: 22px;
      width: 40px;
      height: 40px;
      border-radius: 50%;
      border: none;
      background: rgba(255, 255, 255, 0.92);
      color: #333;
      font-size: 24px;
      line-height: 1;
      font-weight: 600;
      cursor: pointer;
      z-index: 10001;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
      transition: transform 0.12s ease, background 0.12s ease;
    }
    .mermaid-zoom-close:hover {
      background: #ffffff;
      transform: scale(1.08);
    }

    @keyframes mermaid-zoom-fade {
      from { opacity: 0; }
      to { opacity: 1; }
    }

    @media (max-width: 640px) {
      ${CONTAINER_SELECTOR}::after {
        font-size: 11px;
        padding: 2px 8px;
      }
      .mermaid-zoom-hint { font-size: 11px; padding: 6px 12px; }
    }
  `;
  document.head.appendChild(style);
}

function parseViewBox(svg, fallbackWidth, fallbackHeight) {
  const raw = svg.getAttribute("viewBox");
  const values = raw ? raw.trim().split(/[\s,]+/).map(Number) : [];
  if (
    values.length === 4 &&
    values.every(Number.isFinite) &&
    values[2] > 0 &&
    values[3] > 0
  ) {
    return {
      x: values[0],
      y: values[1],
      width: values[2],
      height: values[3],
    };
  }
  return {
    x: 0,
    y: 0,
    width: Math.max(1, fallbackWidth),
    height: Math.max(1, fallbackHeight),
  };
}

function formatViewBox(viewBox) {
  return [
    viewBox.x,
    viewBox.y,
    viewBox.width,
    viewBox.height,
  ]
    .map((value) => Number(value.toFixed(3)))
    .join(" ");
}

function openZoom(sourceSvg) {
  const overlay = document.createElement("div");
  overlay.className = "mermaid-zoom-overlay";
  overlay.setAttribute("role", "dialog");
  overlay.setAttribute("aria-modal", "true");
  overlay.setAttribute("aria-label", "放大查看流程图");

  const stage = document.createElement("div");
  stage.className = "mermaid-zoom-stage";

  // 按原 SVG 的宽高比,算出一个恰好贴合视口 90% / 88% 的目标尺寸
  const srcRect = sourceSvg.getBoundingClientRect();
  const aspect =
    srcRect.width > 0 && srcRect.height > 0
      ? srcRect.width / srcRect.height
      : 16 / 9;
  const maxW = window.innerWidth * 0.9;
  const maxH = window.innerHeight * 0.88;
  let w = maxW;
  let h = w / aspect;
  if (h > maxH) {
    h = maxH;
    w = h * aspect;
  }

  // 关键:克隆整个 container(带着 docusaurus 注入的 class / attr),
  // 不是只克隆 SVG。同时不要抹掉 SVG 的 id ——
  // mermaid 内嵌的 <style> 选择器形如 `#mermaid-xxx .node rect { fill: ... }`,
  // 一旦 id 丢失所有节点色会 fallback 到黑。
  const sourceContainer =
    sourceSvg.closest(CONTAINER_SELECTOR) || sourceSvg.parentElement;
  const containerClone = sourceContainer
    ? sourceContainer.cloneNode(true)
    : null;
  const clone = containerClone
    ? containerClone.querySelector("svg")
    : sourceSvg.cloneNode(true);

  // 克隆进 overlay 的 container 视为"已绑定",防止 MutationObserver 把它
  // 当作新 mermaid 容器再次绑定点击 → 否则会套娃:在放大图里再点一次又弹一层
  if (containerClone) {
    containerClone.dataset[BOUND_FLAG] = "1";
  }

  // 覆盖掉原 SVG 的 style="max-width: ..." 限制,让它按我们算出的尺寸显示
  clone.style.maxWidth = "none";
  clone.style.maxHeight = "none";
  clone.style.width = "100%";
  clone.style.height = "100%";
  clone.setAttribute("preserveAspectRatio", "xMidYMid meet");

  const baseW = Math.round(w);
  const baseH = Math.round(h);
  stage.style.width = `${baseW}px`;
  stage.style.height = `${baseH}px`;

  const baseViewBox = parseViewBox(
    clone,
    srcRect.width || baseW,
    srcRect.height || baseH,
  );
  let currentViewBox = { ...baseViewBox };
  clone.setAttribute("viewBox", formatViewBox(currentViewBox));

  stage.appendChild(containerClone || clone);
  overlay.appendChild(stage);

  const hint = document.createElement("div");
  hint.className = "mermaid-zoom-hint";
  hint.textContent = "滚轮无级缩放 · 拖拽移动 · 双击复位 · ESC / 点外部关闭";
  overlay.appendChild(hint);

  const closeBtn = document.createElement("button");
  closeBtn.className = "mermaid-zoom-close";
  closeBtn.setAttribute("aria-label", "关闭");
  closeBtn.textContent = "\u00D7";
  overlay.appendChild(closeBtn);

  document.body.appendChild(overlay);
  const prevOverflow = document.body.style.overflow;
  document.body.style.overflow = "hidden";

  const minZoom = 0.25;
  const maxZoom = 512;
  let zoom = 1;
  let dragging = false;
  let lastX = 0;
  let lastY = 0;

  function getSvgRect() {
    const rect = clone.getBoundingClientRect();
    if (rect.width > 0 && rect.height > 0) return rect;
    return stage.getBoundingClientRect();
  }

  function apply() {
    clone.setAttribute("viewBox", formatViewBox(currentViewBox));
  }

  function zoomAt(clientX, clientY, factor) {
    const rect = getSvgRect();
    const px =
      rect.width > 0
        ? Math.min(1, Math.max(0, (clientX - rect.left) / rect.width))
        : 0.5;
    const py =
      rect.height > 0
        ? Math.min(1, Math.max(0, (clientY - rect.top) / rect.height))
        : 0.5;
    const anchorX = currentViewBox.x + currentViewBox.width * px;
    const anchorY = currentViewBox.y + currentViewBox.height * py;
    const nextZoom = Math.max(minZoom, Math.min(maxZoom, zoom * factor));
    if (nextZoom === zoom) return;

    const nextWidth = baseViewBox.width / nextZoom;
    const nextHeight = baseViewBox.height / nextZoom;
    currentViewBox = {
      x: anchorX - nextWidth * px,
      y: anchorY - nextHeight * py,
      width: nextWidth,
      height: nextHeight,
    };
    zoom = nextZoom;
    apply();
  }

  function zoomAtCenter(factor) {
    const rect = getSvgRect();
    zoomAt(rect.left + rect.width / 2, rect.top + rect.height / 2, factor);
  }

  function reset() {
    zoom = 1;
    currentViewBox = { ...baseViewBox };
    apply();
  }

  function onWheel(e) {
    e.preventDefault();
    const factor = Math.exp(-e.deltaY * 0.0015);
    zoomAt(e.clientX, e.clientY, factor);
  }

  function onMouseDown(e) {
    if (e.button !== 0) return;
    dragging = true;
    lastX = e.clientX;
    lastY = e.clientY;
    overlay.classList.add("grabbing");
    e.preventDefault();
  }

  function onMouseMove(e) {
    if (!dragging) return;
    const rect = getSvgRect();
    const dx = e.clientX - lastX;
    const dy = e.clientY - lastY;
    currentViewBox = {
      ...currentViewBox,
      x: currentViewBox.x - (dx / Math.max(1, rect.width)) * currentViewBox.width,
      y:
        currentViewBox.y -
        (dy / Math.max(1, rect.height)) * currentViewBox.height,
    };
    lastX = e.clientX;
    lastY = e.clientY;
    apply();
  }

  function onMouseUp() {
    dragging = false;
    overlay.classList.remove("grabbing");
  }

  function close() {
    overlay.remove();
    document.body.style.overflow = prevOverflow;
    document.removeEventListener("keydown", onKey);
    window.removeEventListener("mousemove", onMouseMove);
    window.removeEventListener("mouseup", onMouseUp);
  }

  function onKey(e) {
    if (e.key === "Escape") close();
    else if (e.key === "0" || e.key.toLowerCase() === "f") reset();
    else if (e.key === "+" || e.key === "=") {
      zoomAtCenter(1.2);
    } else if (e.key === "-") {
      zoomAtCenter(1 / 1.2);
    }
  }

  overlay.addEventListener("wheel", onWheel, { passive: false });
  overlay.addEventListener("mousedown", onMouseDown);
  window.addEventListener("mousemove", onMouseMove);
  window.addEventListener("mouseup", onMouseUp);

  overlay.addEventListener("dblclick", (e) => {
    if (e.target === closeBtn) return;
    reset();
  });

  overlay.addEventListener("click", (e) => {
    if (e.target === overlay || e.target === hint) close();
  });
  closeBtn.addEventListener("click", close);
  document.addEventListener("keydown", onKey);
}

function bind(container) {
  if (container.dataset[BOUND_FLAG] === "1") return;
  // 放大 overlay 内部的克隆容器,永远不绑定点击(防止套娃)
  if (container.closest(".mermaid-zoom-overlay")) return;
  const svg = container.querySelector("svg");
  if (!svg) return;
  container.dataset[BOUND_FLAG] = "1";
  container.addEventListener("click", () => {
    const selection = window.getSelection && window.getSelection();
    if (selection && selection.toString()) return;
    openZoom(svg);
  });
}

function scan(root) {
  (root || document).querySelectorAll(CONTAINER_SELECTOR).forEach(bind);
}

if (ExecutionEnvironment.canUseDOM) {
  function boot() {
    ensureStyle();
    scan();
    const mo = new MutationObserver((mutations) => {
      for (const m of mutations) {
        m.addedNodes.forEach((node) => {
          if (!(node instanceof Element)) return;
          if (node.matches && node.matches(CONTAINER_SELECTOR)) {
            bind(node);
          } else if (node.querySelectorAll) {
            scan(node);
          }
        });
      }
    });
    mo.observe(document.body, { childList: true, subtree: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
}

export function onRouteDidUpdate() {
  if (typeof document === "undefined") return;
  // Mermaid 的 SVG 在路由切换后可能异步渲染,延时兜底一次再 scan
  setTimeout(() => {
    ensureStyle();
    scan();
  }, 100);
}
