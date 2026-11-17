const required = ["FireRed3DS.3dsx", "FireRed3DS.smdh", "firered3ds.pak"];
const optional = ["followers.bin", "followers-credits.txt"];
const managed = [...required, ...optional].map((name) => name.toLowerCase());

export async function azaharSd(root) {
  if (root.name === "sdmc") return root;
  return root.getDirectoryHandle("sdmc");
}

export async function writableAzaharSd(root) {
  if (root.queryPermission && await root.queryPermission({ mode: "readwrite" }) !== "granted") {
    throw new DOMException("Allow write access to your Azahar folder.", "NotAllowedError");
  }
  return azaharSd(root);
}

export async function savedFolder(folder, key = "folder") {
  const db = await new Promise((resolve, reject) => {
    const request = indexedDB.open("firered3ds-azahar", 1);
    request.onupgradeneeded = () => request.result.createObjectStore("settings");
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
  try {
    return await new Promise((resolve, reject) => {
      const transaction = db.transaction("settings", folder ? "readwrite" : "readonly");
      const store = transaction.objectStore("settings");
      const request = folder ? store.put(folder, key) : store.get(key);
      transaction.oncomplete = () => resolve(request.result);
      transaction.onabort = () => reject(transaction.error);
    });
  } finally {
    db.close();
  }
}

async function writeFile(directory, name, data) {
  const handle = await directory.getFileHandle(name, { create: true });
  const writer = await handle.createWritable();
  try {
    await writer.write(data);
    await writer.close();
    if ((await handle.getFile()).size !== data.byteLength) {
      throw new Error(`Could not verify ${name} after writing it.`);
    }
  } catch (err) {
    await writer.abort().catch(() => {});
    throw err;
  }
}

export async function enableAzaharAudio(sd) {
  const apps = await sd.getDirectoryHandle("3ds", { create: true });
  try {
    await apps.getFileHandle("dspfirm.cdc");
    return;
  } catch (err) {
    if (err.name !== "NotFoundError") throw err;
  }
  // libctru needs a component to submit. Azahar's HLE DSP logs its hash
  // and runs its own implementation. Physical consoles need real firmware.
  await writeFile(apps, "dspfirm.cdc", new Uint8Array(64));
}

export async function installAzaharLauncher(games, files) {
  const name = required[0];
  await writeFile(games, name, new Map(files).get(name));
}

export async function installAzaharCartridge(games, image) {
  const magic = new Uint8Array(image).subarray(0x100, 0x104);
  if (String.fromCharCode(...magic) !== "NCSD") throw new Error("Invalid cartridge image.");
  await writeFile(games, "FireRed3DS.3ds", image);
}

export async function installAzahar(sd, files) {
  const incoming = new Map(files);
  if (!required.every((name) => incoming.get(name)?.byteLength) ||
      [...incoming.keys()].some((name) => !required.includes(name) && !optional.includes(name))) {
    throw new Error("The build did not provide a complete FireRed installation.");
  }

  const apps = await sd.getDirectoryHandle("3ds", { create: true });
  const game = await apps.getDirectoryHandle("firered3ds", { create: true });
  const old = new Map();
  for await (const [name, entry] of game.entries()) {
    if (entry.kind === "file" && managed.includes(name.toLowerCase())) old.set(name, entry);
  }
  const replaced = [];
  try {
    // Keep a snapshot of each destination until the complete build is installed.
    for (const [name, bytes] of incoming) {
      const handle = old.get(name) ?? await game.getFileHandle(name).catch((err) => {
        if (err.name !== "NotFoundError") throw err;
      });
      const previous = handle ? await (await handle.getFile()).arrayBuffer() : null;
      replaced.push({ name, previous });
      await writeFile(game, name, bytes);
    }
  } catch (err) {
    const failures = [];
    for (const { name, previous } of replaced.reverse()) {
      try {
        if (previous) await writeFile(game, name, previous);
        else await game.removeEntry(name);
      } catch (failure) {
        if (previous || failure.name !== "NotFoundError") failures.push(String(failure));
      }
    }
    if (failures.length) throw new Error(`${err}. Recovery errors: ${failures.join("; ")}`);
    throw err;
  }

  // Cleanup is scoped to known FireRed outputs and leftovers from older
  // installs. Saves, settings, logs and files elsewhere are outside this list.
  for await (const [name, entry] of game.entries()) {
    if (entry.kind !== "file" || incoming.has(name)) continue;
    const lower = name.toLowerCase();
    const replacement = [...incoming.keys()].find((key) => key.toLowerCase() === lower);
    if (replacement && await entry.isSameEntry(await game.getFileHandle(replacement))) continue;
    if (managed.includes(lower.replace(/\.(partial|tmp)$/, ""))) await game.removeEntry(name);
  }
}
