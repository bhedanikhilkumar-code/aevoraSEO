#!/usr/bin/env node

/**
 * AevoraSEO CLI — Official Command-Line Interface
 * Dual native binary runner and Python engine runtime.
 * 
 * Powered by AevoraSEO Engine
 * Author: Bheda Nikhilkumar
 * License: MIT
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const pkg = require('../package.json');

const c = {
  reset: "\x1b[0m",
  bold: "\x1b[1m",
  dim: "\x1b[2m",
  red: "\x1b[31m",
  green: "\x1b[32m",
  yellow: "\x1b[33m",
  blue: "\x1b[34m",
  cyan: "\x1b[36m",
};

function banner() {
  console.log(`
${c.cyan}${c.bold}  █████╗ ███████╗██╗   ██╗ ██████╗ ██████╗  █████╗ ███████╗███████╗ ██████╗ 
 ██╔══██╗██╔════╝██║   ██║██╔═══██╗██╔══██╗██╔══██╗██╔════╝██╔════╝██╔═══██╗
 ███████║█████╗  ██║   ██║██║   ██║██████╔╝███████║███████╗█████╗  ██║   ██║
 ██╔══██║██╔══╝  ╚██╗ ██╔╝██║   ██║██╔══██╗██╔══██║╚════██║██╔══╝  ██║   ██║
 ██║  ██║███████╗ ╚████╔╝ ╚██████╔╝██║  ██║██║  ██║███████║███████╗╚██████╔╝
 ╚═╝  ╚═╝╚══════╝  ╚═══╝   ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝ ╚═════╝ ${c.reset}
  ${c.bold}Autonomous SEO & AEO Intelligence Engine${c.reset} ${c.dim}| Native Runner v${pkg.version}${c.reset}
  ${c.dim}https://github.com/bhedanikhilkumar-code/aevoraSEO${c.reset}
`);
}

function showHelp() {
  banner();
  console.log(`${c.bold}USAGE:${c.reset}`);
  console.log(`  ${c.green}npx aevoraseo${c.reset} <command> [options]`);
  console.log(`  ${c.green}aevoraseo${c.reset} <command> [options]\n`);
  
  console.log(`${c.bold}COMMANDS:${c.reset}`);
  console.log(`  ${c.cyan}audit${c.reset} <target-url>        Run complete SEO, AEO & performance audit`);
  console.log(`  ${c.cyan}aeo${c.reset} <snapshot-dir>       Analyze AEO answer readiness and GEO signals`);
  console.log(`  ${c.cyan}aeo-compare${c.reset}              Compare AEO/GEO readiness between two snapshots`);
  console.log(`  ${c.cyan}entity${c.reset} <target>          Extract Schema.org entities, knowledge graph & authority`);
  console.log(`  ${c.cyan}entity-compare${c.reset}           Compare entity snapshots for evolution & conflict deltas`);
  console.log(`  ${c.cyan}search${c.reset} <target>          Analyze search intent, cannibalization, local & commercial CTAs`);
  console.log(`  ${c.cyan}search-compare${c.reset}           Compare search & commercial snapshots across crawls`);
  console.log(`  ${c.cyan}optimize${c.reset} <target>        Audit content quality, titles, headings, answer boxes & clusters`);
  console.log(`  ${c.cyan}optimize-compare${c.reset}         Compare content optimization snapshots across crawls`);
  console.log(`  ${c.cyan}report${c.reset} <snapshot-dir>     Generate unified multi-dimensional audit report (HTML, PDF, MD, CSV)`);
  console.log(`  ${c.cyan}audit-verify${c.reset}               Verify if prior audit recommendations are resolved in new crawl`);
  console.log(`  ${c.cyan}remediate${c.reset} <action>        Automated remediation & code patch engine: generate, preview, apply, rollback, list`);
  console.log(`  ${c.cyan}progress${c.reset}                   Track multi-snapshot score trajectory across historical crawls`);
  console.log(`  ${c.cyan}agent${c.reset} <action>           Multi-agent platform compatibility: detect, list, inspect, adapt, verify`);
  console.log(`  ${c.cyan}reputation${c.reset} <domain>      Calculate Aevora Reputation & Entity score`);
  console.log(`  ${c.cyan}backlinks${c.reset} <domain>       Discover and score high-authority backlink sources`);
  console.log(`  ${c.cyan}crawl${c.reset} <target-url>        Crawl website structure and discover search links`);
  console.log(`  ${c.cyan}compare${c.reset}                  Compare two crawl snapshots for added/changed/removed URLs`);
  console.log(`  ${c.cyan}doctor${c.reset}                  Check CLI environment, connectivity & engine status`);
  console.log(`  ${c.cyan}version${c.reset}                 Print version information\n`);

  console.log(`${c.bold}OPTIONS:${c.reset}`);
  console.log(`  ${c.yellow}--help, -h${c.reset}              Show this help message`);
  console.log(`  ${c.yellow}--version, -v${c.reset}           Print version information\n`);

  console.log(`${c.bold}EXAMPLES:${c.reset}`);
  console.log(`  $ npx aevoraseo audit https://example.com`);
  console.log(`  $ npx aevoraseo crawl https://example.com --profile quick --out ./crawl1`);
  console.log(`  $ npx aevoraseo aeo ./crawl1 --format terminal`);
  console.log(`  $ npx aevoraseo aeo-compare --before ./crawl1 --after ./crawl2 --out ./aeo_diff`);
  console.log(`  $ npx aevoraseo entity ./crawl1 --format terminal`);
  console.log(`  $ npx aevoraseo entity-compare --before ./crawl1 --after ./crawl2 --out ./entity_diff`);
  console.log(`  $ npx aevoraseo search ./crawl1 --format terminal`);
  console.log(`  $ npx aevoraseo search-compare --before ./crawl1 --after ./crawl2 --out ./search_diff`);
  console.log(`  $ npx aevoraseo optimize ./crawl1 --format terminal`);
  console.log(`  $ npx aevoraseo optimize-compare --before ./crawl1 --after ./crawl2 --out ./opt_diff`);
  console.log(`  $ npx aevoraseo report ./crawl1 --format terminal`);
  console.log(`  $ npx aevoraseo report ./crawl1 --format html --out ./client_report`);
  console.log(`  $ npx aevoraseo remediate generate --site ./my-site --crawl ./crawl1`);
  console.log(`  $ npx aevoraseo remediate preview --plan ./crawl1/plan_12345678.json`);
  console.log(`  $ npx aevoraseo remediate apply --plan ./crawl1/plan_12345678.json --dry-run`);
  console.log(`  $ npx aevoraseo audit-verify --audit ./audit.json --crawl ./crawl2`);
  console.log(`  $ npx aevoraseo progress --crawls ./crawl1 ./crawl2 ./crawl3`);
  console.log(`  $ npx aevoraseo agent list`);
  console.log(`  $ npx aevoraseo agent detect`);
  console.log(`  $ npx aevoraseo agent inspect claude-code`);
  console.log(`  $ npx aevoraseo agent verify --host claude-code`);
  console.log(`  $ npx aevoraseo compare --before ./crawl1 --after ./crawl2 --out ./diff`);
  console.log(`  $ npx aevoraseo reputation example.com`);
  console.log(`  $ npx aevoraseo doctor\n`);
}

const args = process.argv.slice(2);

// Handle version flag
if (args.includes('-v') || args.includes('--version') || args[0] === 'version') {
  console.log(`aevoraseo v${pkg.version}`);
  process.exit(0);
}

// Resolve runner: First check compiled native binary, then fallback to Python runtime
const runnerDir = path.join(__dirname, 'runner');
let binaryPath = '';

if (process.platform === 'win32') {
  binaryPath = path.join(runnerDir, 'aevoraseo.exe');
} else if (process.platform === 'darwin') {
  binaryPath = path.join(runnerDir, 'aevoraseo-darwin');
} else {
  binaryPath = path.join(runnerDir, 'aevoraseo-linux');
}

function runNativeBinary(binPath) {
  if (args.length === 0) {
    banner();
  }

  const child = spawn(binPath, args, {
    stdio: 'inherit',
    windowsHide: true,
  });

  child.on('error', (err) => {
    console.error(`${c.red}Failed to execute native runner:${c.reset}`, err.message);
    process.exit(1);
  });

  child.on('exit', (code) => {
    if (args[0] === 'doctor' || args.includes('--help') || args.includes('-h') || args.includes('--version') || args.includes('-v')) {
      process.exit(0);
    }
    process.exit(code === 0 || code === null ? 0 : code);
  });
}

function runPythonEngine() {
  const venvPythonWin = path.join(__dirname, '..', '.venv', 'Scripts', 'python.exe');
  const venvPythonUnix = path.join(__dirname, '..', '.venv', 'bin', 'python');
  
  let pythonCmd = '';
  let pythonArgs = [];

  if (process.platform === 'win32' && fs.existsSync(venvPythonWin)) {
    pythonCmd = venvPythonWin;
  } else if (fs.existsSync(venvPythonUnix)) {
    pythonCmd = venvPythonUnix;
  } else {
    pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
  }

  // Always launch the package module instead of executing cli.py directly.
  // Direct script execution breaks relative imports (e.g. "from . import __version__")
  // on Unix/macOS fallback runners. Keep src/ on PYTHONPATH so a source checkout
  // works even when the package has not been installed yet.
  pythonArgs = ['-m', 'aevoraseo', ...args];

  if (args.length === 0) {
    banner();
  }

  const sourceRoot = path.join(__dirname, '..', 'src');
  const env = {
    ...process.env,
    PYTHONPATH: [sourceRoot, process.env.PYTHONPATH].filter(Boolean).join(path.delimiter),
  };

  const child = spawn(pythonCmd, pythonArgs, {
    stdio: 'inherit',
    windowsHide: true,
    env,
  });

  child.on('error', () => {
    showMissingEngineNotice();
  });

  child.on('exit', (code) => {
    process.exit(code === 0 || code === null ? 0 : code);
  });
}

function showMissingEngineNotice() {
  if (args.length === 0 || args.includes('-h') || args.includes('--help') || args[0] === 'help') {
    showHelp();
    process.exit(0);
  }

  banner();
  console.log(`${c.yellow}AevoraSEO runtime not found.${c.reset}`);
  console.log(`\nTo run AevoraSEO via Python:`);
  console.log(`  ${c.green}pip install aevoraseo${c.reset}  OR  ${c.green}pip install -e .${c.reset}`);
  console.log(`\nTo build the standalone native runner:`);
  console.log(`  ${c.green}python scripts/release.py${c.reset}`);
  console.log(`\nVisit: ${c.cyan}https://github.com/bhedanikhilkumar-code/aevoraSEO${c.reset}\n`);
  process.exit(1);
}

if (fs.existsSync(binaryPath)) {
  runNativeBinary(binaryPath);
} else {
  runPythonEngine();
}
