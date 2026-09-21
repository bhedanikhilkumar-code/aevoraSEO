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
  console.log(`  ${c.cyan}reputation${c.reset} <domain>      Calculate Aevora Reputation & Entity score`);
  console.log(`  ${c.cyan}backlinks${c.reset} <domain>       Discover and score high-authority backlink sources`);
  console.log(`  ${c.cyan}crawl${c.reset} <target-url>        Crawl website structure and discover search links`);
  console.log(`  ${c.cyan}doctor${c.reset}                  Check CLI environment, connectivity & engine status`);
  console.log(`  ${c.cyan}version${c.reset}                 Print version information\n`);

  console.log(`${c.bold}OPTIONS:${c.reset}`);
  console.log(`  ${c.yellow}--help, -h${c.reset}              Show this help message`);
  console.log(`  ${c.yellow}--version, -v${c.reset}           Print version information\n`);

  console.log(`${c.bold}EXAMPLES:${c.reset}`);
  console.log(`  $ npx aevoraseo audit https://example.com`);
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

  const cliPath = path.join(__dirname, '..', 'src', 'aevoraseo', 'cli.py');
  if (fs.existsSync(cliPath)) {
    pythonArgs = [cliPath, ...args];
  } else {
    pythonArgs = ['-m', 'aevoraseo', ...args];
  }

  if (args.length === 0) {
    banner();
  }

  const child = spawn(pythonCmd, pythonArgs, {
    stdio: 'inherit',
    windowsHide: true,
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
