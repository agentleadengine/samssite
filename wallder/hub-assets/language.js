(() => {
  const root = document.documentElement;
  const address = new URL(window.location.href);
  const requested = address.searchParams.get("lang")?.toLowerCase();
  const storageKey = "wallder-hub-language";
  const supported = (value) => value === "en" || value === "es";
  let saved;
  try {
    saved = localStorage.getItem(storageKey);
  } catch {
    // The URL works when storage is unavailable.
  }
  const lang = supported(requested) ? requested : supported(saved) ? saved : "es";
  root.lang = lang;
  document.title = document.querySelector("head title").dataset[lang];
  const description = document.querySelector('meta[name="description"]');
  description.content = description.dataset[lang];

  document.addEventListener("DOMContentLoaded", () => {
    const active = document.querySelector(`[data-lang="${lang}"]`);
    for (const video of active.querySelectorAll(".hub-video video")) {
      const status = video.parentElement.querySelector(".video-status");
      function updateVideo() {
        video.hidden = Boolean(video.error);
        status.hidden = !video.error;
      }
      video.addEventListener("error", updateVideo);
      video.addEventListener("loadedmetadata", updateVideo);
      updateVideo();
    }
    function updateLinks() {
      const hash = location.hash.replace(/^#(?:en|es)-/, "");
      for (const link of active.querySelectorAll("[data-switch]")) {
        const target = link.dataset.switch;
        const section = /^[a-z][a-z0-9-]*$/.test(hash) && document.getElementById(`${target}-${hash}`);
        link.href = `?lang=${target}${section ? `#${section.id}` : ""}`;
      }
    }
    updateLinks();
    active.addEventListener("click", (event) => {
      const link = event.target.closest("a");
      if (link?.dataset.switch) {
        try { localStorage.setItem(storageKey, link.dataset.switch); } catch {}
      }
      if (link?.getAttribute("href")?.startsWith("#")) {
        reveal(document.getElementById(link.hash.slice(1)));
      }
    });

    function reveal(target) {
      for (let ancestor = target?.parentElement; ancestor; ancestor = ancestor.parentElement) {
        if (ancestor.tagName === "DETAILS") ancestor.open = true;
      }
    }
    function showFragment() {
      const alternate = location.hash.match(/^#(?:en|es)-([a-z0-9-]+)$/);
      const target = alternate && document.getElementById(`${lang}-${alternate[1]}`);
      if (target) {
        reveal(target);
        if (`#${target.id}` !== location.hash) {
          try { history.replaceState(null, "", `#${target.id}`); } catch {}
        }
        target.scrollIntoView();
      }
      updateLinks();
    }
    if (location.hash) showFragment();
    window.addEventListener("hashchange", showFragment);
    const nav = active.querySelector(".part-nav");
    if (nav) {
      const links = [...nav.querySelectorAll("a")];
      const sections = links.map((link) => document.getElementById(link.hash.slice(1)));
      function highlightPart() {
        const current = sections.findLastIndex((section) => section.getBoundingClientRect().top <= 68);
        links.forEach((link, index) => {
          if (index === current) link.setAttribute("aria-current", "location");
          else link.removeAttribute("aria-current");
        });
      }
      window.addEventListener("scroll", highlightPart, { passive: true });
      window.addEventListener("resize", highlightPart, { passive: true });
      highlightPart();
    }
  });
})();
