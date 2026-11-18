const $ = (selector) => document.querySelector(selector);
const games = $("[data-games]");
const input = $("[data-rom]");
const build = $("[data-build]");
const cancel = $("[data-cancel]");
const download = $("[data-download]");
const status = $("[data-status]");
const progress = $("[data-progress]");
const filename = $("[data-file]");
const drop = $("[data-drop]");

let selected;
let rom;
let worker;
let outputUrl;
let buildId = 0;

function announce(message, error = false) {
  status.textContent = message;
  status.toggleAttribute("data-error", error);
}

function clearDownload() {
  if (outputUrl) URL.revokeObjectURL(outputUrl);
  outputUrl = undefined;
  download.hidden = true;
  download.removeAttribute("href");
}

function setBusy(busy) {
  games.querySelectorAll("button").forEach((game) => {
    game.disabled = busy || !game.dataset.ready;
  });
  input.disabled = busy || !selected;
  build.disabled = busy || !selected || !rom;
  cancel.hidden = !busy;
  progress.hidden = !busy;
}

function choose(port, button) {
  selected = port;
  games.querySelectorAll("button").forEach((game) => game.setAttribute("aria-pressed", String(game === button)));
  $("#build-title").textContent = "Build " + port.name;
  $("[data-rom-help]").textContent = "Required ROM: " + port.input;
  build.textContent = port.format === "homebrew" ? "Build Azahar ZIP" : "Build .3ds cartridge";
  $("[data-install]").textContent = port.format === "homebrew"
    ? "Unzip the download and copy its 3ds folder into Azahar’s sdmc folder. Open PokeClassicVoxel.3dsx from Azahar."
    : "Copy the finished file into your Azahar 3DS games folder and launch it from the library.";
  chooseFile(undefined);
}

function chooseFile(file) {
  if (!selected || worker || input.disabled && file) return;
  clearDownload();
  announce("");
  rom = file;
  filename.textContent = file?.name ?? "";
  filename.hidden = !file;
  setBusy(false);
}

function stop() {
  buildId++;
  worker?.terminate();
  worker = undefined;
  setBusy(false);
}

function receive(event) {
  const message = event.data;
  if (message.type === "progress") {
    const weight = { runtime: [0, .12], payload: [.12, .2], zip: [.94, 1] };
    const limits = weight[message.stage];
    const value = limits
      ? limits[0] + (limits[1] - limits[0]) * message.fraction
      : .2 + .74 * message.fraction;
    progress.value = Math.max(progress.value, value);
    if (message.message) announce(message.message);
  } else if (message.type === "phase") {
    const phases = { runtime: "Loading builder…", payload: "Downloading build files…",
                     data: "Checking and extracting the ROM…", zip: "Assembling the download…" };
    if (phases[message.phase]) announce(phases[message.phase]);
  } else if (message.type === "error") {
    stop();
    announce([message.message || "The build could not finish.", message.hint].filter(Boolean).join(" "), true);
  } else if (message.type === "done") {
    stop();
    const blob = message.zip
      ? new Blob([message.zip], { type: "application/zip" })
      : new Blob([message.cartridge], { type: "application/octet-stream" });
    outputUrl = URL.createObjectURL(blob);
    download.href = outputUrl;
    download.download = selected.output;
    download.textContent = "Download " + selected.output;
    download.hidden = false;
    announce("Download ready.");
    download.focus();
  }
}

$("[data-form]").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!selected || !rom || build.disabled) return;
  if (rom.size === 0 || rom.size > 64 * 1024 * 1024) {
    announce("Choose a nonempty ROM or ZIP under 64 MB.", true);
    return;
  }
  clearDownload();
  setBusy(true);
  progress.value = 0;
  announce("Reading the ROM on this device…");
  const id = ++buildId;
  try {
    const bytes = await rom.arrayBuffer();
    if (buildId !== id) return;
    worker = new Worker(new URL("./builder.worker.js?v=voxel-2", import.meta.url), { type: "module" });
    worker.onmessage = receive;
    worker.onerror = () => { stop(); announce("The browser could not start the builder.", true); };
    worker.postMessage({
      type: "start", base: new URL(selected.base, document.baseURI).href,
      rom: bytes, romName: rom.name, cartridge: selected.format !== "homebrew",
      classic: selected.format === "homebrew", followers: false, direct: false,
    }, [bytes]);
  } catch (error) {
    if (buildId !== id) return;
    stop();
    announce(String(error), true);
  }
});
cancel.addEventListener("click", () => { stop(); announce("Build canceled."); });
input.addEventListener("change", () => {
  chooseFile(input.files[0]);
  input.value = "";
});
drop.addEventListener("dragover", (event) => event.preventDefault());
drop.addEventListener("drop", (event) => {
  event.preventDefault();
  chooseFile(event.dataTransfer.files[0]);
});

async function loadGames() {
  const response = await fetch("voxel-catalog.json");
  if (!response.ok) throw new Error("Could not load the game catalog.");
  const catalog = await response.json();
  for (const port of catalog) {
    const button = document.createElement("button");
    button.className = "voxel-game";
    button.type = "button";
    button.setAttribute("aria-pressed", "false");
    const title = document.createElement("strong");
    title.textContent = port.name;
    const description = document.createElement("span");
    description.className = "small muted";
    description.textContent = port.base ? port.input : "In development";
    button.append(title, description);
    if (port.base && port.output) {
      button.dataset.ready = "true";
      button.addEventListener("click", () => choose(port, button));
    } else {
      button.disabled = true;
    }
    games.append(button);
    if (!selected && port.base && port.output) choose(port, button);
  }
}

loadGames().catch((error) => announce(String(error), true));
