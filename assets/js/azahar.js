const required = ["FireRed3DS.3dsx", "FireRed3DS.smdh", "firered3ds.pak"];
const optional = ["followers.bin", "followers-credits.txt"];
const managed = [...required, ...optional].map((name) => name.toLowerCase());

export async function azaharSd(root) {
  // Require Azahar's existing SD directory before creating any game files.
  return root.getDirectoryHandle("sdmc");
}

export async function savedFolder(folder) {
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
      const request = folder ? store.put(folder, "folder") : store.get("folder");
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
  } catch (err) {
    await writer.abort().catch(() => {});
    throw err;
  }
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
