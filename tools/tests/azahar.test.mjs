import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const code = await readFile(new URL("../../site/assets/js/azahar.js", import.meta.url));
const { azaharSd, installAzahar } = await import("data:text/javascript;base64," + code.toString("base64"));

function directory() {
  const entries = new Map();
  return {
    kind: "directory",
    entries: () => entries.entries(),
    failOnce: null,
    async getDirectoryHandle(name, { create = false } = {}) {
      if (!entries.has(name) && create) entries.set(name, directory());
      if (!entries.has(name)) throw new DOMException(name, "NotFoundError");
      return entries.get(name);
    },
    async getFileHandle(name, { create = false } = {}) {
      if (!entries.has(name) && create) {
        const entry = {
          kind: "file",
          data: new ArrayBuffer(0),
          async isSameEntry(other) { return other === this; },
          async getFile() { return new Blob([this.data]); },
          createWritable: async () => {
            let data;
            return {
              write: async (next) => {
                if (this.failOnce === name) {
                  this.failOnce = null;
                  throw new Error("Disk full");
                }
                data = next;
              },
              close: async () => { entry.data = data; },
              abort: async () => {},
            };
          },
        };
        entries.set(name, entry);
      }
      if (!entries.has(name)) throw new DOMException(name, "NotFoundError");
      return entries.get(name);
    },
    async removeEntry(name) { entries.delete(name); },
  };
}

const files = ["FireRed3DS.3dsx", "FireRed3DS.smdh", "firered3ds.pak"]
  .map((name) => [name, Uint8Array.of(2).buffer]);

async function fixture() {
  const root = directory();
  await root.getDirectoryHandle("sdmc", { create: true });
  const sd = await azaharSd(root);
  const apps = await sd.getDirectoryHandle("3ds", { create: true });
  const game = await apps.getDirectoryHandle("firered3ds", { create: true });
  for (const name of ["FireRed3DS.3dsx", "firered3ds.3dsx", "firered3ds.pak.partial",
                      "followers.bin", "followers-credits.txt", "firered3ds.sav", "settings.txt"]) {
    const file = await game.getFileHandle(name, { create: true });
    file.data = Uint8Array.of(1).buffer;
  }
  return { sd, game };
}

test("installs the matching files, removes known conflicts, and preserves saves and settings", async () => {
  const { sd, game } = await fixture();
  await installAzahar(sd, files);
  const actual = Object.fromEntries([...game.entries()].map(([name, file]) => [name, new Uint8Array(file.data)[0]]));
  assert.deepEqual(actual, {
    "FireRed3DS.3dsx": 2, "FireRed3DS.smdh": 2, "firered3ds.pak": 2,
    "firered3ds.sav": 1, "settings.txt": 1,
  });
});

test("restores old files and leaves conflicts alone if installation fails", async () => {
  const { sd, game } = await fixture();
  game.failOnce = "firered3ds.pak";
  const before = [...game.entries()].map(([name, file]) => [name, file.data]);
  await assert.rejects(installAzahar(sd, files), /Disk full/);
  const after = [...game.entries()].map(([name, file]) => [name, file.data]);
  assert.deepEqual(after, before);
});

test("rejects a folder without an existing Azahar SD directory", async () => {
  await assert.rejects(azaharSd(directory()), { name: "NotFoundError" });
});
