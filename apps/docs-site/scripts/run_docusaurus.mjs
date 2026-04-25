import {spawnSync} from "node:child_process";
import {createRequire} from "node:module";

process.env.NO_UPDATE_NOTIFIER ??= "1";

const require = createRequire(import.meta.url);
const docusaurusBin = require.resolve("@docusaurus/core/bin/docusaurus.mjs");
const args = process.argv.slice(2);
const command = args[0];

if (
  (command === "start" || command === "serve") &&
  !args.includes("--open") &&
  !args.includes("--no-open")
) {
  args.splice(1, 0, "--no-open");
}

if (
  command === "start" &&
  !args.includes("--poll") &&
  process.env.DOCUSAURUS_POLL_MS
) {
  const pollMs = process.env.DOCUSAURUS_POLL_MS;
  args.splice(1, 0, "--poll", pollMs);
}

const result = spawnSync(process.execPath, [docusaurusBin, ...args], {
  stdio: "inherit",
  env: process.env,
});

if (result.error) {
  throw result.error;
}

process.exit(result.status ?? 1);
