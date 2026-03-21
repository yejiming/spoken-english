const data = window.SPOKEN_ENGLISH_DATA;

const state = {
  sceneIndex: 0,
  lessonIndex: 0,
  durations: new Map(),
};

const els = {};

function escapeHtml(value) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
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

function renderScenes() {
  els.sceneBar.innerHTML = "";
  data.scenes.forEach((scene, idx) => {
    const button = document.createElement("button");
    button.className = `scene-pill ${idx === state.sceneIndex ? "active" : ""}`;
    button.textContent = `${scene.nameEn} / ${scene.nameCn}`;
    button.addEventListener("click", () => {
      state.sceneIndex = idx;
      state.lessonIndex = 0;
      renderAll();
    });
    els.sceneBar.appendChild(button);
  });
}

function renderLessons() {
  const scene = getCurrentScene();
  els.lessonList.innerHTML = "";
  scene.lessons.forEach((lesson, idx) => {
    const button = document.createElement("button");
    button.className = `lesson-button ${idx === state.lessonIndex ? "active" : ""}`;
    button.innerHTML = `
      <span class="num">${String(idx + 1).padStart(2, "0")} · ${escapeHtml(lesson.slug)}</span>
      <span class="title">${escapeHtml(lesson.title)}</span>
      <span class="pattern">${escapeHtml(lesson.pattern)}</span>
    `;
    button.addEventListener("click", () => {
      state.lessonIndex = idx;
      renderAll();
    });
    els.lessonList.appendChild(button);
  });
}

function renderLessonDetail() {
  const scene = getCurrentScene();
  const lesson = getCurrentLesson();
  els.detail.innerHTML = `
    <div class="lesson-head">
      <div>
        <div class="scene-tag">${escapeHtml(scene.nameEn)} / ${escapeHtml(scene.nameCn)}</div>
        <h3>${escapeHtml(lesson.title)}</h3>
      </div>
      <div class="scene-tag">#${String(state.lessonIndex + 1).padStart(2, "0")}</div>
    </div>
    <div class="meta-grid">
      <div class="meta-card">
        <span class="label">Sentence Pattern</span>
        <div class="value">${escapeHtml(lesson.pattern)}</div>
      </div>
      <div class="meta-card">
        <span class="label">Meaning / 意思</span>
        <div class="value">${escapeHtml(lesson.meaning)}</div>
      </div>
      <div class="meta-card" style="grid-column: 1 / -1;">
        <span class="label">Usage Note / 用法</span>
        <div class="value">${escapeHtml(lesson.note)}</div>
      </div>
    </div>
    <div class="examples">
      ${lesson.examples.map(renderExample).join("")}
    </div>
  `;
}

function renderExample(example) {
  const escaped = highlightSentence(example.english, example.slotEn);
  const duration = state.durations.get(example.audio);
  return `
    <article class="example-card">
      <div class="example-top">
        <div class="english">${escaped}</div>
        <div class="audio-wrap">
          <audio controls preload="metadata" data-audio="${escapeHtml(example.audio)}" src="${escapeHtml(example.audio)}"></audio>
          <div class="duration">${duration ? `${duration.toFixed(1)}s` : "..."}</div>
        </div>
      </div>
      <div class="example-cn">${escapeHtml(example.chinese)}</div>
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
  });
}

function renderAll() {
  renderScenes();
  renderLessons();
  renderLessonDetail();
  preloadDurations();
}

function init() {
  els.sceneBar = document.getElementById("sceneBar");
  els.lessonList = document.getElementById("lessonList");
  els.detail = document.getElementById("detail");
  renderAll();
}

document.addEventListener("DOMContentLoaded", init);
