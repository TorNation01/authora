#!/usr/bin/env node
/** Cross-platform API dev server - sets PYTHONPATH and runs uvicorn */
import { spawn } from "child_process";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
const apiPath = path.join(root, "apps", "api");

const env = { ...process.env, PYTHONPATH: apiPath };
const child = spawn(
  "python",
  ["-m", "uvicorn", "authora.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
  { cwd: root, env, stdio: "inherit" }
);
child.on("exit", (code) => process.exit(code ?? 0));
