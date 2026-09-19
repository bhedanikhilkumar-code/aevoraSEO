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
  console.log("aevoraseo v1.0.0");
  process.exit(0);
}

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
  // If no args, show help
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
    // When binary runs --help or doctor, clean exit
    process.exit(code === 0 || code === null ? 0 : code);
  });

} else {
  // If binary not found on this platform, show JS help or notice
  if (args.length === 0 || args.includes('-h') || args.includes('--help') || args[0] === 'help') {
    showHelp();
    process.exit(0);
  }

  banner();
  console.log(`${c.yellow}Notice: Native runner binary not found at:${c.reset} ${binaryPath}`);
  console.log(`${c.dim}Compiled runner is currently available for Windows x64.${c.reset}`);
  console.log(`\nVisit: ${c.cyan}https://github.com/bhedanikhilkumar-code/aevoraSEO${c.reset} for instructions.\n`);
  process.exit(0);
}
