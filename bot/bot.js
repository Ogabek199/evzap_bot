const { spawn } = require("child_process");
const path = require("path");

const python = path.join(__dirname, ".venv", "bin", "python");
const script = path.join(__dirname, "bot.py");

const proc = spawn(python, [script], {
  cwd: __dirname,
  stdio: "inherit",
});

proc.on("close", (code) => process.exit(code ?? 0));
proc.on("error", (err) => {
  console.error("Bot ishga tushmadi:", err.message);
  process.exit(1);
});
