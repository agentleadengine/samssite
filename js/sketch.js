/*
 * sketch.js - Blueprint × Purple Marker on Cream diagram library.
 *
 * Usage inside any HTML page:
 *
 *   <div class="sketch" data-viewbox="0 0 920 340">
 *     <svg></svg>
 *   </div>
 *   <script>
 *   document.addEventListener('sketch:ready', () => {
 *     const svg = document.querySelector('.sketch svg');
 *     const rc  = sketch.rc(svg);
 *     sketch.box(svg, rc, { x: 40,  y: 90, w: 240, h: 140, title: 'Model',  sub: '(Claude)' });
 *     sketch.box(svg, rc, { x: 340, y: 90, w: 240, h: 140, title: 'Client', sub: '(Claude Code)' });
 *     sketch.box(svg, rc, { x: 640, y: 90, w: 240, h: 140, title: 'Server', sub: '(Gmail MCP)' });
 *     sketch.arrow(svg, rc, { x1: 280, x2: 340, y: 160, label: 'MCP' });
 *     sketch.arrow(svg, rc, { x1: 580, x2: 640, y: 160, label: 'MCP' });
 *   });
 *   </script>
 *
 * The library auto-sets viewBox from the wrapper's data-viewbox attribute,
 * loads rough.js from CDN, and fires `sketch:ready` on document once both
 * are available. Every diagram on every page uses the same visual grammar.
 */
(function() {
  // Inject sketch-wrapper CSS on load so diagrams look right even if the
  // page's main stylesheet is cached, outdated, or fails to load.
  (function injectCss() {
    if (document.getElementById('sketch-css')) return;
    const css = '' +
      '.sketch{position:relative;margin:36px auto;max-width:940px;padding:28px 20px;' +
        'border-radius:18px;background:#faf7f2;' +
        'background-image:linear-gradient(rgba(74,0,224,0.08) 1px, transparent 1px),' +
        'linear-gradient(90deg, rgba(74,0,224,0.08) 1px, transparent 1px);' +
        'background-size:24px 24px;box-shadow:0 4px 20px rgba(0,0,0,0.04);' +
        'box-sizing:border-box;}' +
      '.sketch svg{display:block;width:100%;height:auto;max-width:960px;margin:0 auto;}' +
      '.sketch svg text{fill:#1d1d23;}' +
      '.sketch-caption{text-align:center;font-family:\'Caveat\',\'Kalam\',cursive;' +
        'color:#8b5cf6;font-size:20px;font-weight:700;margin-top:8px;' +
        'letter-spacing:0.02em;}';
    const s = document.createElement('style');
    s.id = 'sketch-css';
    s.textContent = css;
    (document.head || document.documentElement).appendChild(s);
  })();

  const NS = 'http://www.w3.org/2000/svg';
  const COLORS = {
    stroke:     '#4a00e0',
    strokeSoft: '#8b5cf6',
    fill:       '#f1ecff',
    text:       '#4a00e0',
    sub:        '#6b21a8',
    dim:        '#8b5cf6',
    page:       '#faf7f2'
  };

  // ---- Low-level helpers -------------------------------------------------
  function el(tag, attrs) {
    const e = document.createElementNS(NS, tag);
    for (const k in (attrs || {})) e.setAttribute(k, attrs[k]);
    return e;
  }
  function text(svg, x, y, s, opts) {
    opts = opts || {};
    const t = el('text', {
      x, y,
      'text-anchor': opts.anchor || 'middle',
      fill: opts.color || COLORS.text,
      'font-size': opts.size || 20,
      'font-weight': opts.weight || 400,
      'font-family': opts.font || "'Kalam', cursive"
    });
    if (opts.style) t.setAttribute('font-style', opts.style);
    if (opts.transform) t.setAttribute('transform', opts.transform);
    t.textContent = s;
    svg.appendChild(t);
    return t;
  }

  // ---- Crosshair corner marks (blueprint touch) --------------------------
  function crosshair(svg, x, y, color) {
    svg.appendChild(el('circle', {
      cx: x, cy: y, r: 4,
      fill: COLORS.page,
      stroke: color || COLORS.stroke,
      'stroke-width': 1.5
    }));
  }

  // ---- The boxed node (hand-drawn + corner crosshairs + dim label) ------
  function box(svg, rc, b) {
    // Hand-drawn rectangle with lavender fill
    svg.appendChild(rc.rectangle(b.x, b.y, b.w, b.h, {
      roughness: 1.8,
      stroke: b.strokeColor || COLORS.stroke,
      strokeWidth: 2.5,
      fill: b.fillColor || COLORS.fill,
      fillStyle: 'solid'
    }));
    // Corner crosshairs
    [[b.x, b.y], [b.x+b.w, b.y], [b.x, b.y+b.h], [b.x+b.w, b.y+b.h]].forEach(pt => {
      crosshair(svg, pt[0], pt[1], b.strokeColor);
    });
    // Title + subtitle (handwritten)
    if (b.title) {
      text(svg, b.x + b.w/2, b.y + (b.titleY || 68), b.title, {
        size: b.titleSize || 30, weight: 700, color: b.textColor || COLORS.text
      });
    }
    if (b.sub) {
      text(svg, b.x + b.w/2, b.y + (b.subY || 102), b.sub, {
        size: b.subSize || 20, weight: 400, color: b.subColor || COLORS.sub
      });
    }
    // Optional mono dimension label below
    if (b.dim) {
      text(svg, b.x + b.w/2, b.y + b.h + 26, b.dim, {
        size: 11, color: COLORS.dim, font: "'JetBrains Mono', monospace"
      });
    }
  }

  // ---- Circle node (for cases where a box doesn't fit the idea) ---------
  function circle(svg, rc, c) {
    svg.appendChild(rc.circle(c.cx, c.cy, (c.r || 60) * 2, {
      roughness: 1.8,
      stroke: c.strokeColor || COLORS.stroke,
      strokeWidth: 2.5,
      fill: c.fillColor || COLORS.fill,
      fillStyle: 'solid'
    }));
    if (c.title) text(svg, c.cx, c.cy - 2, c.title, { size: 24, weight: 700, color: COLORS.text });
    if (c.sub)   text(svg, c.cx, c.cy + 24, c.sub,   { size: 15, weight: 400, color: COLORS.sub });
  }

  // ---- Arrow between two points (horizontal by default) -----------------
  function arrow(svg, rc, a) {
    // Hand-drawn line
    svg.appendChild(rc.line(a.x1, a.y1 != null ? a.y1 : a.y, a.x2, a.y2 != null ? a.y2 : a.y, {
      roughness: 1.8, stroke: a.color || COLORS.stroke, strokeWidth: 2.5
    }));
    // Arrowhead on the destination side
    const y2 = a.y2 != null ? a.y2 : a.y;
    const y1 = a.y1 != null ? a.y1 : a.y;
    // Simple right-pointing arrowhead
    svg.appendChild(rc.polygon(
      [[a.x2-14, y2-8], [a.x2, y2], [a.x2-14, y2+8]],
      { roughness: 1.4, stroke: a.color || COLORS.stroke, strokeWidth: 2,
        fill: a.color || COLORS.stroke, fillStyle: 'solid' }
    ));
    // Opposite arrowhead if bidirectional
    if (a.bidirectional !== false) {
      svg.appendChild(rc.polygon(
        [[a.x1+14, y1-8], [a.x1, y1], [a.x1+14, y1+8]],
        { roughness: 1.4, stroke: a.color || COLORS.stroke, strokeWidth: 2,
          fill: a.color || COLORS.stroke, fillStyle: 'solid' }
      ));
    }
    // Small handwritten label over the arrow
    if (a.label) {
      const mx = (a.x1 + a.x2) / 2;
      const my = ((y1 + y2) / 2) - 14;
      text(svg, mx, my, a.label, {
        size: 16, color: COLORS.strokeSoft, weight: 700
      });
    }
  }

  // ---- Freehand scribble label (annotation) -----------------------------
  function note(svg, x, y, s, opts) {
    opts = opts || {};
    return text(svg, x, y, s, Object.assign({
      size: 18, color: COLORS.strokeSoft, weight: 700
    }, opts));
  }

  // ---- Stack of layered boxes (for layered architectures) ---------------
  // cfg: { x, y, w, layers: [{label, sub, color?}, ...], layerH? }
  function stack(svg, rc, cfg) {
    const lh = cfg.layerH || 60;
    const gap = 6;
    cfg.layers.forEach((layer, i) => {
      const by = cfg.y + i * (lh + gap);
      box(svg, rc, {
        x: cfg.x, y: by, w: cfg.w, h: lh,
        title: layer.label,
        sub: layer.sub,
        titleY: 30, subY: 48, titleSize: 18, subSize: 13,
        fillColor: layer.color || COLORS.fill,
        strokeColor: layer.stroke || COLORS.stroke,
        textColor: layer.textColor || COLORS.text
      });
    });
  }

  // ---- Numbered steps (a vertical or horizontal sequence of numbered nodes)
  // cfg: { items: [{title, sub}...], x, y, w, direction: 'h'|'v' }
  function numberedSteps(svg, rc, cfg) {
    const dir = cfg.direction || 'h';
    const N = cfg.items.length;
    const stepGap = cfg.gap || 30;
    const radius = cfg.radius || 28;
    cfg.items.forEach((it, i) => {
      let cx, cy;
      if (dir === 'h') {
        const totalW = (cfg.w || 800) - radius * 2;
        cx = cfg.x + radius + (totalW / Math.max(N-1, 1)) * i;
        cy = cfg.y;
      } else {
        cx = cfg.x;
        cy = cfg.y + (radius * 2 + stepGap) * i;
      }
      // Rough circle
      svg.appendChild(rc.circle(cx, cy, radius * 2, {
        roughness: 1.8, stroke: COLORS.stroke, strokeWidth: 2.5,
        fill: COLORS.fill, fillStyle: 'solid'
      }));
      text(svg, cx, cy + 7, String(i + 1), {
        size: 22, weight: 700, color: COLORS.text, font: "'Kalam', cursive"
      });
      // Title below (or to the right for vertical)
      if (dir === 'h') {
        text(svg, cx, cy + radius + 22, it.title, {
          size: 17, weight: 700, color: COLORS.text
        });
        if (it.sub) text(svg, cx, cy + radius + 44, it.sub, {
          size: 13, weight: 400, color: COLORS.sub
        });
      } else {
        text(svg, cx + radius + 14, cy - 2, it.title, {
          anchor: 'start', size: 18, weight: 700, color: COLORS.text
        });
        if (it.sub) text(svg, cx + radius + 14, cy + 20, it.sub, {
          anchor: 'start', size: 13, weight: 400, color: COLORS.sub
        });
      }
      // Arrow to next item
      if (i < N - 1) {
        if (dir === 'h') {
          const nextCx = cfg.x + radius + ((cfg.w || 800) - radius * 2) / Math.max(N-1, 1) * (i + 1);
          svg.appendChild(rc.line(cx + radius + 2, cy, nextCx - radius - 2, cy, {
            roughness: 1.8, stroke: COLORS.strokeSoft, strokeWidth: 2
          }));
          svg.appendChild(rc.polygon(
            [[nextCx - radius - 8, cy - 6], [nextCx - radius - 2, cy], [nextCx - radius - 8, cy + 6]],
            { roughness: 1.4, stroke: COLORS.strokeSoft, strokeWidth: 1.5, fill: COLORS.strokeSoft, fillStyle: 'solid' }
          ));
        } else {
          svg.appendChild(rc.line(cx, cy + radius + 2, cx, cy + radius * 2 + stepGap - 2, {
            roughness: 1.8, stroke: COLORS.strokeSoft, strokeWidth: 2
          }));
        }
      }
    });
  }

  // ---- Simple bar chart (horizontal bars) -------------------------------
  // cfg: { x, y, w, barH?, gap?, items: [{label, value, max, note?}] }
  function bars(svg, rc, cfg) {
    const barH = cfg.barH || 32;
    const gap = cfg.gap || 14;
    const labelW = cfg.labelW || 140;
    const chartW = cfg.w - labelW - 60;
    const maxVal = cfg.max || Math.max(...cfg.items.map(it => it.value));
    cfg.items.forEach((it, i) => {
      const by = cfg.y + i * (barH + gap);
      // Label to the left
      text(svg, cfg.x + labelW - 10, by + barH / 2 + 6, it.label, {
        anchor: 'end', size: 15, weight: 600, color: COLORS.text
      });
      // Bar
      const bw = Math.max(4, chartW * (it.value / maxVal));
      svg.appendChild(rc.rectangle(cfg.x + labelW, by, bw, barH, {
        roughness: 1.6, stroke: COLORS.stroke, strokeWidth: 2,
        fill: it.color || COLORS.fill, fillStyle: 'solid'
      }));
      // Value note at end of bar
      const noteText = it.note != null ? it.note : String(it.value);
      text(svg, cfg.x + labelW + bw + 8, by + barH / 2 + 6, noteText, {
        anchor: 'start', size: 14, weight: 700, color: COLORS.strokeSoft,
        font: "'JetBrains Mono', monospace"
      });
    });
  }

  // ---- Side-by-side comparison (two columns) ----------------------------
  // cfg: { x, y, w, h, left: {title, items: [...]}, right: {...} }
  function compare(svg, rc, cfg) {
    const halfW = (cfg.w - 30) / 2;
    ['left', 'right'].forEach((side, i) => {
      const col = cfg[side];
      const cx = cfg.x + (i === 0 ? 0 : halfW + 30);
      // Column box
      svg.appendChild(rc.rectangle(cx, cfg.y, halfW, cfg.h, {
        roughness: 1.8, stroke: COLORS.stroke, strokeWidth: 2.5,
        fill: i === 0 ? '#fef3f2' : COLORS.fill, fillStyle: 'solid'
      }));
      // Title header
      text(svg, cx + halfW / 2, cfg.y + 32, col.title, {
        size: 22, weight: 800, color: i === 0 ? '#dc2626' : COLORS.text
      });
      // Items
      (col.items || []).forEach((item, j) => {
        text(svg, cx + 16, cfg.y + 62 + j * 26, '• ' + item, {
          anchor: 'start', size: 14, weight: 500,
          color: i === 0 ? '#7f1d1d' : COLORS.sub
        });
      });
    });
  }

  // ---- Annotation: arrow from a point to a text label -------------------
  // cfg: { fromX, fromY, toX, toY, text }
  function annotate(svg, rc, cfg) {
    // Curved path
    const ctrlX = (cfg.fromX + cfg.toX) / 2;
    const ctrlY = cfg.fromY - 30;
    const p = el('path', {
      d: `M ${cfg.fromX} ${cfg.fromY} Q ${ctrlX} ${ctrlY} ${cfg.toX} ${cfg.toY}`,
      fill: 'none', stroke: COLORS.strokeSoft, 'stroke-width': '2', 'stroke-dasharray': '5 3'
    });
    svg.appendChild(p);
    // Small arrowhead at destination
    const dx = cfg.toX - ctrlX, dy = cfg.toY - ctrlY;
    const len = Math.sqrt(dx*dx + dy*dy);
    const ux = dx/len, uy = dy/len;
    const hx = cfg.toX - 10*ux, hy = cfg.toY - 10*uy;
    svg.appendChild(rc.polygon([
      [hx - 4*uy, hy + 4*ux],
      [cfg.toX, cfg.toY],
      [hx + 4*uy, hy - 4*ux]
    ], { roughness: 1.3, stroke: COLORS.strokeSoft, fill: COLORS.strokeSoft, fillStyle: 'solid' }));
    // Label at from side
    text(svg, cfg.fromX, cfg.fromY - 8, cfg.text, {
      size: 17, weight: 700, color: COLORS.strokeSoft, font: "'Kalam', cursive"
    });
  }

  // ---- Venn diagram (two or three overlapping circles) ------------------
  // cfg: { x, y, sets: [{label, fill?}, ...], r? }
  function venn(svg, rc, cfg) {
    const R = cfg.r || 100;
    const N = cfg.sets.length;
    const overlap = R * 0.7;
    cfg.sets.forEach((s, i) => {
      const cx = cfg.x + i * overlap;
      svg.appendChild(rc.circle(cx, cfg.y, R * 2, {
        roughness: 1.8, stroke: COLORS.stroke, strokeWidth: 2.5,
        fill: s.fill || (i === 0 ? 'rgba(139,92,246,0.15)' : 'rgba(236,72,153,0.15)'),
        fillStyle: 'solid'
      }));
      // Label positioned away from overlap
      const lx = i === 0 ? cx - R * 0.6 : cx + R * 0.6;
      text(svg, lx, cfg.y + 5, s.label, {
        size: 18, weight: 700, color: COLORS.text
      });
    });
  }

  // ---- Hand-drawn table (rows + columns) --------------------------------
  // cfg: { x, y, cols: [{title, w}], rows: [[cell, cell, ...]] }
  function table(svg, rc, cfg) {
    const rowH = cfg.rowH || 36;
    const headerH = cfg.headerH || 42;
    let totalW = 0;
    cfg.cols.forEach(c => totalW += c.w);
    const totalH = headerH + cfg.rows.length * rowH;
    // Outer rect
    svg.appendChild(rc.rectangle(cfg.x, cfg.y, totalW, totalH, {
      roughness: 1.4, stroke: COLORS.stroke, strokeWidth: 2.5,
      fill: COLORS.fill, fillStyle: 'solid'
    }));
    // Header row background darker
    svg.appendChild(rc.rectangle(cfg.x, cfg.y, totalW, headerH, {
      roughness: 1.2, stroke: COLORS.stroke, strokeWidth: 1.5,
      fill: '#e9d5ff', fillStyle: 'solid'
    }));
    // Column dividers
    let curX = cfg.x;
    cfg.cols.forEach((c, i) => {
      if (i > 0) {
        svg.appendChild(rc.line(curX, cfg.y, curX, cfg.y + totalH, {
          roughness: 1.4, stroke: COLORS.stroke, strokeWidth: 1
        }));
      }
      // Header text
      text(svg, curX + c.w / 2, cfg.y + headerH / 2 + 7, c.title, {
        size: 15, weight: 800, color: COLORS.text
      });
      curX += c.w;
    });
    // Row dividers + cell content
    cfg.rows.forEach((row, ri) => {
      const ry = cfg.y + headerH + ri * rowH;
      if (ri > 0) {
        svg.appendChild(rc.line(cfg.x, ry, cfg.x + totalW, ry, {
          roughness: 1.2, stroke: COLORS.stroke, strokeWidth: 0.75
        }));
      }
      let colX = cfg.x;
      cfg.cols.forEach((c, ci) => {
        const cell = row[ci] || '';
        text(svg, colX + c.w / 2, ry + rowH / 2 + 5, cell, {
          size: 13, weight: 500, color: COLORS.sub
        });
        colX += c.w;
      });
    });
  }

  // ---- rough.js convenience ---------------------------------------------
  function rc(svg) {
    if (!window.rough) throw new Error('rough.js not loaded yet');
    return rough.svg(svg);
  }

  // ---- createSvg: ensure/resize an SVG inside a wrapper -----------------
  // If the wrapper already has a data-viewbox, that takes precedence - it lets
  // authors resize a diagram by changing only the wrapper attribute without
  // hunting down the createSvg() call in the inline script.
  function createSvg(wrapper, w, h) {
    let svg = wrapper.querySelector('svg');
    if (!svg) {
      svg = el('svg');
      wrapper.appendChild(svg);
    }
    const existingVb = wrapper.dataset.viewbox;
    const vb = existingVb || ('0 0 ' + w + ' ' + h);
    svg.setAttribute('viewBox', vb);
    svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
    svg.setAttribute('class', 'sketch-svg');
    if (!existingVb) wrapper.dataset.viewbox = vb;
    return svg;
  }

  // ---- title: a big headline at top of a diagram ------------------------
  function title(svg, x, y, s, opts) {
    opts = opts || {};
    return text(svg, x, y, s, Object.assign({
      size: 24, weight: 700, color: COLORS.text
    }, opts));
  }

  // ---- Auto-setup on DOM load -------------------------------------------
  function setupWrappers() {
    document.querySelectorAll('.sketch').forEach(wrap => {
      let svg = wrap.querySelector('svg');
      if (!svg) {
        svg = el('svg');
        wrap.appendChild(svg);
      }
      const vb = wrap.dataset.viewbox || '0 0 920 340';
      svg.setAttribute('viewBox', vb);
      svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
      svg.setAttribute('class', 'sketch-svg');
    });
  }

  function loadRough(cb) {
    if (window.rough) return cb();
    const s = document.createElement('script');
    s.src = 'https://unpkg.com/roughjs@4.6.6/bundled/rough.js';
    s.onload = cb;
    document.head.appendChild(s);
  }

  function ready() {
    setupWrappers();
    loadRough(() => {
      document.dispatchEvent(new Event('sketch:ready'));
      window.dispatchEvent(new Event('sketch:ready'));
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', ready);
  } else {
    ready();
  }

  // Expose API
  window.sketch = {
    COLORS, el, text, crosshair, box, circle, arrow, note, rc,
    stack, numberedSteps, bars, compare, annotate, venn, table,
    createSvg, title
  };
})();

// Framework sidebar mobile collapse toggle.
// On viewports <=960px, wrap the sidebar in a collapsible toggle so it doesn't
// push article content below the fold.
(function() {
  function initFrameworkSidebarToggle() {
    const sidebar = document.querySelector('.framework-sidebar');
    if (!sidebar || sidebar.dataset.collapseInit) return;
    sidebar.dataset.collapseInit = '1';

    const mql = window.matchMedia('(max-width: 960px)');

    const toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'framework-sidebar-toggle';
    const activeText = sidebar.querySelector('a.active');
    const label = activeText ? `On this page: ${activeText.textContent}` : 'On this page';
    toggle.textContent = label;
    toggle.setAttribute('aria-expanded', 'false');
    sidebar.insertBefore(toggle, sidebar.firstChild);

    function apply() {
      if (mql.matches) {
        sidebar.classList.add('is-collapsed');
        toggle.setAttribute('aria-expanded', 'false');
      } else {
        sidebar.classList.remove('is-collapsed');
        toggle.setAttribute('aria-expanded', 'true');
      }
    }

    toggle.addEventListener('click', function() {
      sidebar.classList.toggle('is-collapsed');
      toggle.setAttribute('aria-expanded', sidebar.classList.contains('is-collapsed') ? 'false' : 'true');
    });

    mql.addEventListener ? mql.addEventListener('change', apply) : mql.addListener(apply);
    apply();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFrameworkSidebarToggle);
  } else {
    initFrameworkSidebarToggle();
  }
})();
