function initCustomSelect(wrapper) {
  const select = wrapper.querySelector("select");
  const trigger = wrapper.querySelector(".custom-select-trigger");
  const display = wrapper.querySelector(".custom-select-value");
  const menu = wrapper.querySelector(".custom-select-menu");

  menu.innerHTML = "";
  [...select.options].forEach((opt) => {
    const li = document.createElement("li");
    li.className = "custom-select-option";
    li.role = "option";
    li.tabIndex = -1;
    li.dataset.value = opt.value;
    li.textContent = opt.textContent;
    li.setAttribute("aria-selected", opt.selected ? "true" : "false");
    menu.appendChild(li);
  });

  const options = () => [...menu.querySelectorAll(".custom-select-option")];

  function setValue(value) {
    select.value = value;
    const opt = select.options[select.selectedIndex];
    display.textContent = opt.textContent;
    options().forEach((li) => {
      li.setAttribute("aria-selected", li.dataset.value === value ? "true" : "false");
    });
  }

  function open() {
    wrapper.classList.add("open");
    trigger.setAttribute("aria-expanded", "true");
    menu.hidden = false;
    const selected = menu.querySelector('[aria-selected="true"]');
    (selected || options()[0])?.focus();
  }

  function close(focusTrigger = true) {
    wrapper.classList.remove("open");
    trigger.setAttribute("aria-expanded", "false");
    menu.hidden = true;
    if (focusTrigger) trigger.focus();
  }

  setValue(select.value);

  trigger.addEventListener("click", () => {
    if (wrapper.classList.contains("open")) close(false);
    else open();
  });

  menu.addEventListener("click", (e) => {
    const li = e.target.closest(".custom-select-option");
    if (!li) return;
    setValue(li.dataset.value);
    close();
  });

  menu.addEventListener("keydown", (e) => {
    const items = options();
    const idx = items.indexOf(document.activeElement);
    if (e.key === "Escape") {
      e.preventDefault();
      close();
      return;
    }
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      if (idx >= 0) {
        setValue(items[idx].dataset.value);
        close();
      }
      return;
    }
    if (e.key === "ArrowDown") {
      e.preventDefault();
      (items[idx + 1] || items[0]).focus();
    }
    if (e.key === "ArrowUp") {
      e.preventDefault();
      (items[idx - 1] || items[items.length - 1]).focus();
    }
  });

  document.addEventListener("click", (e) => {
    if (!wrapper.contains(e.target)) close(false);
  });
}

document.querySelectorAll("[data-custom-select]").forEach(initCustomSelect);

const form = document.getElementById("profile-form");
const results = document.getElementById("results");
const errorMsg = document.getElementById("error-msg");
const submitBtn = document.getElementById("submit-btn");
const btnLabel = submitBtn.querySelector(".btn-label");
const limerickResults = document.getElementById("limerick-results");
const nameInput = document.getElementById("name");
const subjectNameEl = document.getElementById("limerick-subject-name");
const limerickEl = document.getElementById("limerick");
let hasGenerated = false;

function updateLimerickHeading(name) {
  const display = (name ?? nameInput.value).trim();
  subjectNameEl.textContent = display ? ` ${display}` : "…";
}

nameInput.addEventListener("input", () => updateLimerickHeading());
updateLimerickHeading();

function setLoading(loading) {
  submitBtn.disabled = loading;
  if (loading) {
    btnLabel.textContent = "Composing…";
  } else {
    btnLabel.textContent = hasGenerated ? "Regenerate Limerick" : "Generate Limerick";
  }
}

function showError(message) {
  errorMsg.textContent = message;
  errorMsg.hidden = !message;
  if (message) {
    limerickEl.hidden = true;
    scrollToLimerick();
  } else {
    limerickEl.hidden = false;
  }
}

function scrollToLimerick() {
  requestAnimationFrame(() => {
    limerickResults.scrollIntoView({ behavior: "smooth", block: "start" });
  });
}

function renderKit(kit, profile) {
  showError("");
  if (profile?.name) updateLimerickHeading(profile.name);
  limerickEl.textContent = kit.limerick || "";
  limerickEl.hidden = false;
  hasGenerated = true;
  scrollToLimerick();
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  showError("");
  if (hasGenerated) scrollToLimerick();
  setLoading(true);

  const data = Object.fromEntries(new FormData(form));

  try {
    const res = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    const payload = await res.json();
    if (!res.ok) {
      throw new Error(
        payload.error
          || (res.status === 429
            ? "Too many requests. Please wait a moment and try again."
            : "Something went wrong.")
      );
    }

    renderKit(payload.kit, payload.profile);
  } catch (err) {
    showError(err.message);
  } finally {
    setLoading(false);
  }
});

if ("scrollRestoration" in history) {
  history.scrollRestoration = "manual";
}
window.scrollTo(0, 0);
