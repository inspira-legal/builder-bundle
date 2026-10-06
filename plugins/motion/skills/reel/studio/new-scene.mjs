// npm run new -- <name> [base-scene]: starts scenes/<name> as a copy of a base scene (fonts and assets included).
// Exists so a scene starts without mkdir/cp in the shell, which a non-technical user would have to approve one by one.
import { cpSync, existsSync } from "node:fs";

const [name, base = "demo"] = process.argv.slice(2);
if (!/^[a-z0-9][a-z0-9-]*$/.test(name ?? "")) {
  console.error("usage: npm run new -- <kebab-case-name> [base-scene]");
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
