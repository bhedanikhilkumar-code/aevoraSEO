#!/usr/bin/env node

/**
 * AevoraSEO CLI — Official Command-Line Interface
 * Distributed via NPM with zero-source leakage compiled native engine runner.
 * 
 * Powered by AevoraSEO Engine
 * Author: Bheda Nikhilkumar
 * License: MIT
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

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
  ${c.bold}Autonomous SEO & AEO Intelligence Engine${c.reset} ${c.dim}| Native Runner v1.0.0${c.reset}
  ${c.dim}https://github.com/bhedanikhilkumar-code/aevoraSEO${c.reset}
`);
}

const args = process.argv.slice(2);

// Resolve compiled binary runner path
const runnerDir = path.join(__dirname, 'runner');
let binaryPath = '';

if (process.platform === 'win32') {
  binaryPath = path.join(runnerDir, 'aevoraseo.exe');
} else if (process.platform === 'darwin') {
  binaryPath = path.join(runnerDir, 'aevoraseo-darwin');
} else {
  binaryPath = path.join(runnerDir, 'aevoraseo-linux');
}

// Check if binary exists
if (fs.existsSync(binaryPath)) {
  // If no args or asking for help, display banner then binary help
  if (args.length === 0) {
    banner();
  }

  // Execute native compiled engine
  const child = spawn(binaryPath, args, {
    stdio: 'inherit',
    windowsHide: true,
  });

  child.on('error', (err) => {
    console.error(`${c.red}Failed to execute native runner:${c.reset}`, err.message);
    process.exit(1);
  });

  child.on('exit', (code) => {
    process.exit(code || 0);
  });

} else {
  // Fallback if binary is not yet available for current platform
  banner();
  console.log(`${c.yellow}Notice: Native runner binary not found at:${c.reset} ${binaryPath}`);
  console.log(`${c.dim}Please ensure bin/runner/ contains the compiled binary for ${process.platform}.${c.reset}`);
  console.log(`\nVisit: ${c.cyan}https://github.com/bhedanikhilkumar-code/aevoraSEO${c.reset} for instructions.\n`);
  process.exit(1);
}
