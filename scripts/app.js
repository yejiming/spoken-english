const data = window.SPOKEN_ENGLISH_DATA;
const inviteCodes = new Set((window.SPOKEN_ENGLISH_INVITE_CODES || []).map((code) => String(code).toUpperCase()));

const state = {
  unlocked: false,
  sceneIndex: 0,
  lessonIndex: 0,
  durations: new Map(),
};

const els = {};

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function formatCount(value) {
  return new Intl.NumberFormat("en-US").format(value);
}

function highlightSentence(sentence, slot) {
  const safeSentence = escapeHtml(sentence);
  const safeSlot = escapeHtml(slot);
  if (!slot) return safeSentence;
  return safeSentence.replace(safeSlot, `<mark>${safeSlot}</mark>`);
}

function getCurrentScene() {
  return data.scenes[state.sceneIndex];
}

function getCurrentLesson() {
  return getCurrentScene().lessons[state.lessonIndex];
}

function getLibraryTotals() {
  return data.scenes.reduce((totals, scene) => {
    totals.lessonCount += scene.lessons.length;
    totals.exampleCount += scene.lessons.reduce((sum, lesson) => sum + lesson.examples.length, 0);
    return totals;
  }, {
    sceneCount: data.scenes.length,
    lessonCount: 0,
    exampleCount: 0,
  });
}

function shouldJumpToDetail() {
  return window.matchMedia("(max-width: 1024px)").matches;
}

function normalizeInviteCode(value) {
  return String(value || "")
    .trim()
    .toUpperCase()
    .replace(/\s+/g, "");
}

function isValidInviteCode(value) {
  return inviteCodes.has(normalizeInviteCode(value));
}

function setAccessGranted(granted) {
  state.unlocked = granted;
  document.body.classList.toggle("locked", !granted);
  if (els.gateOverlay) {
    els.gateOverlay.hidden = granted;
    els.gateOverlay.setAttribute("aria-hidden", granted ? "true" : "false");
  }
  if (els.appShell) {
    els.appShell.hidden = !granted;
    els.appShell.setAttribute("aria-hidden", granted ? "false" : "true");
  }
}

function showGateMessage(message, isSuccess = false) {
  if (!els.gateMessage) return;
  els.gateMessage.textContent = message;
  els.gateMessage.classList.toggle("success", isSuccess);
}

function unlockSite() {
  showGateMessage("验证通过，正在进入页面。", true);
  setAccessGranted(true);
  renderAll();
  window.requestAnimationFrame(() => {
    window.scrollTo(0, 0);
  });
}

function renderHeroSummary() {
  const scene = getCurrentScene();
  const totals = getLibraryTotals();
  const sceneExampleCount = scene.lessons.reduce((sum, lesson) => sum + lesson.examples.length, 0);

  if (els.statScenes) els.statScenes.textContent = formatCount(totals.sceneCount);
  if (els.statLessons) els.statLessons.textContent = formatCount(totals.lessonCount);
  if (els.statExamples) els.statExamples.textContent = formatCount(totals.exampleCount);
  if (els.heroCurrentScene) {
    els.heroCurrentScene.textContent = `${scene.nameEn} / ${scene.nameCn}`;
  }
  if (els.heroCurrentMeta) {
    els.heroCurrentMeta.textContent = `${formatCount(scene.lessons.length)} patterns and ${formatCount(sceneExampleCount)} audio lines in this scene.`;
  }
}

function renderScenes() {
  els.sceneBar.innerHTML = "";
  data.scenes.forEach((scene, idx) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `scene-pill ${idx === state.sceneIndex ? "active" : ""}`;
    button.setAttribute("aria-label", `${scene.nameEn} / ${scene.nameCn}`);
    button.innerHTML = `
      <span class="scene-pill-en">${escapeHtml(scene.nameEn)}</span>
      <span class="scene-pill-cn">${escapeHtml(scene.nameCn)}</span>
    `;
    button.addEventListener("click", () => {
      state.sceneIndex = idx;
      state.lessonIndex = 0;
      renderAll();
    });
    els.sceneBar.appendChild(button);
  });

  const activeButton = els.sceneBar.querySelector(".scene-pill.active");
  if (activeButton) {
    activeButton.scrollIntoView({ block: "nearest", inline: "center" });
  }
}

function renderLessons() {
  const scene = getCurrentScene();
  els.lessonList.innerHTML = "";

  if (els.lessonSelect) {
    els.lessonSelect.innerHTML = "";
    scene.lessons.forEach((lesson, idx) => {
      const option = document.createElement("option");
      option.value = String(idx);
      option.textContent = `${lesson.slug} · ${lesson.title}`;
      els.lessonSelect.appendChild(option);
    });
    els.lessonSelect.value = String(state.lessonIndex);
  }

  scene.lessons.forEach((lesson, idx) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `lesson-button ${idx === state.lessonIndex ? "active" : ""}`;
    button.innerHTML = `
      <span class="num">${escapeHtml(lesson.slug)}</span>
      <span class="title">${escapeHtml(lesson.title)}</span>
      <span class="pattern">${escapeHtml(lesson.pattern)}</span>
    `;
    button.addEventListener("click", () => {
      state.lessonIndex = idx;
      renderAll();
      if (shouldJumpToDetail()) {
        els.detail.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
    els.lessonList.appendChild(button);
  });

  const activeButton = els.lessonList.querySelector(".lesson-button.active");
  if (activeButton) {
    activeButton.scrollIntoView({ block: "nearest", inline: "nearest" });
  }
}

function renderLessonDetail() {
  const scene = getCurrentScene();
  const lesson = getCurrentLesson();
  const lessonNumber = lesson.slug.split("-")[0];
  els.detail.innerHTML = `
    <div class="detail-frame">
      <div class="lesson-head">
        <div class="lesson-heading">
          <div class="scene-tag">${escapeHtml(scene.nameEn)} / ${escapeHtml(scene.nameCn)}</div>
          <h3>${escapeHtml(lesson.title)}</h3>
        </div>
        <div class="lesson-index">
          <span>Pattern No.</span>
          <strong>#${escapeHtml(lessonNumber)}</strong>
        </div>
      </div>
      <div class="meta-grid">
        <article class="meta-card">
          <span class="label">Sentence Pattern</span>
          <div class="value">${escapeHtml(lesson.pattern)}</div>
        </article>
        <article class="meta-card">
          <span class="label">Meaning / 意思</span>
          <div class="value">${escapeHtml(lesson.meaning)}</div>
        </article>
        <article class="meta-card meta-card-wide">
          <span class="label">Usage Note / 用法</span>
          <div class="value">${escapeHtml(lesson.note)}</div>
        </article>
      </div>
      <div class="detail-divider" aria-hidden="true"></div>
      <div class="section-head">
        <div class="section-copy">
          <div class="section-kicker">Practice Lines</div>
          <h4>${escapeHtml(String(lesson.examples.length))} example${lesson.examples.length === 1 ? "" : "s"} with audio</h4>
        </div>
      </div>
      <div class="examples">
        ${lesson.examples.map((example, index) => renderExample(example, index)).join("")}
      </div>
    </div>
  `;
}

function renderExample(example, index) {
  const escaped = highlightSentence(example.english, example.slotEn);
  const duration = state.durations.get(example.audio);
  return `
    <article class="example-card">
      <div class="example-number">${String(index + 1).padStart(2, "0")}</div>
      <div class="example-main">
        <div class="example-top">
          <div class="english">${escaped}</div>
          <div class="audio-wrap">
            <audio controls preload="metadata" data-audio="${escapeHtml(example.audio)}" src="${escapeHtml(example.audio)}"></audio>
            <div class="duration">${duration ? `${duration.toFixed(1)}s` : "..."}</div>
          </div>
        </div>
        <div class="example-cn">${escapeHtml(example.chinese)}</div>
      </div>
    </article>
  `;
}

function preloadDurations() {
  document.querySelectorAll("audio[data-audio]").forEach((audioEl) => {
    audioEl.addEventListener("loadedmetadata", () => {
      const path = audioEl.dataset.audio;
      if (!path) return;
      state.durations.set(path, audioEl.duration);
      const card = audioEl.closest(".audio-wrap");
      if (card) {
        const durationEl = card.querySelector(".duration");
        if (durationEl) durationEl.textContent = `${audioEl.duration.toFixed(1)}s`;
      }
    }, { once: true });

    audioEl.addEventListener("error", () => {
      const card = audioEl.closest(".audio-wrap");
      if (!card) return;
      const durationEl = card.querySelector(".duration");
      if (durationEl) durationEl.textContent = "Unavailable";
    }, { once: true });

    // Mobile browsers are less reliable about fetching metadata for dynamically
    // inserted audio elements unless loading is triggered explicitly.
    audioEl.load();
  });
}

function renderAll() {
  if (!state.unlocked) return;
  renderHeroSummary();
  renderScenes();
  renderLessons();
  renderLessonDetail();
  preloadDurations();
}

function initGate() {
  setAccessGranted(false);
  els.inviteInput.value = "";
  showGateMessage("");
  els.inviteInput.focus();
}

function init() {
  els.gateOverlay = document.getElementById("gateOverlay");
  els.gateForm = document.getElementById("inviteForm");
  els.inviteInput = document.getElementById("inviteCode");
  els.gateMessage = document.getElementById("gateMessage");
  els.appShell = document.getElementById("appShell");
  els.sceneBar = document.getElementById("sceneBar");
  els.lessonList = document.getElementById("lessonList");
  els.lessonSelect = document.getElementById("lessonSelect");
  els.detail = document.getElementById("detail");
  els.heroCurrentScene = document.getElementById("heroCurrentScene");
  els.heroCurrentMeta = document.getElementById("heroCurrentMeta");
  els.statScenes = document.getElementById("statScenes");
  els.statLessons = document.getElementById("statLessons");
  els.statExamples = document.getElementById("statExamples");

  els.gateForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const code = normalizeInviteCode(els.inviteInput.value);
    if (!code) {
      showGateMessage("请输入邀请码。");
      return;
    }
    if (!isValidInviteCode(code)) {
      showGateMessage("邀请码不正确，请重新输入。");
      els.inviteInput.select();
      return;
    }
    unlockSite();
  });

  els.inviteInput.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      els.inviteInput.value = "";
      showGateMessage("");
    }
  });

  if (els.lessonSelect) {
    els.lessonSelect.addEventListener("change", (event) => {
      const nextIndex = Number(event.target.value);
      if (Number.isNaN(nextIndex)) return;
      state.lessonIndex = nextIndex;
      renderAll();
      if (shouldJumpToDetail()) {
        els.detail.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  }

  initGate();
}

document.addEventListener("DOMContentLoaded", init);
