import { cpSync, existsSync, mkdirSync, readdirSync, rmSync, statSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const rootDir = resolve(scriptDir, "..");
const distDir = resolve(rootDir, "dist");

mkdirSync(distDir, { recursive: true });

const sourceHtmlEntries = [];

for (const entry of readdirSync(rootDir)) {
  const sourcePath = join(rootDir, entry);
  const stats = statSync(sourcePath);

  if (stats.isFile() && entry.endsWith(".html")) {
    sourceHtmlEntries.push(entry);
  }
}

for (const entry of readdirSync(distDir)) {
  if (entry.endsWith(".html") && !sourceHtmlEntries.includes(entry)) {
    rmSync(join(distDir, entry), { force: true });
  }
}

for (const entry of sourceHtmlEntries) {
  cpSync(join(rootDir, entry), join(distDir, entry));
  }

for (const directory of ["css", "js"]) {
  const sourcePath = join(rootDir, directory);

  if (existsSync(sourcePath)) {
    cpSync(sourcePath, join(distDir, directory), { recursive: true });
  }
}
