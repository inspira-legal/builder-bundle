// node new-scene.mjs <name> [base-scene]: starts scenes/<name> as a copy of a base scene (fonts and assets included).
// Exists so a scene starts without mkdir/cp in the shell, which a non-technical user would have to approve one by one.
import { cpSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";

process.chdir(fileURLToPath(new URL(".", import.meta.url)));
const slug = /^[a-z0-9][a-z0-9-]*$/;
const [name, base = "demo"] = process.argv.slice(2);
// The same rule for both names keeps `../` from reaching outside scenes/.
if (!slug.test(name ?? "") || !slug.test(base)) {
  console.error("usage: node new-scene.mjs <kebab-case-name> [kebab-case-base-scene]");
  process.exit(1);
}
if (!existsSync(`scenes/${base}`)) {
  console.error(`base scene not found: scenes/${base}`);
  process.exit(1);
}
if (existsSync(`scenes/${name}`)) {
  console.error(`scenes/${name} already exists: edit it instead`);
  process.exit(1);
}
cpSync(`scenes/${base}`, `scenes/${name}`, { recursive: true });
console.log(`scenes/${name} (from ${base})`);
