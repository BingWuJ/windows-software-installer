#!/usr/bin/env node
'use strict';

const path = require('path');
const fs = require('fs');
const os = require('os');

// ─── 常量 ───────────────────────────────────────────────────────────────────
const SKILL_NAME = 'windows-software-installer';
const GREEN  = '\x1b[32m';
const RED    = '\x1b[31m';
const YELLOW = '\x1b[33m';
const CYAN   = '\x1b[36m';
const BOLD   = '\x1b[1m';
const RESET  = '\x1b[0m';

// ─── 工具函数 ───────────────────────────────────────────────────────────────
function log(msg, color = '') {
  console.log(`${color}${msg}${RESET}`);
}

function fail(msg) {
  log(`\n[ERROR] ${msg}`, RED);
  process.exit(1);
}

/**
 * 递归复制目录，跳过 __pycache__ 和 .pyc 文件
 */
function copyRecursiveSync(src, dest) {
  const stat = fs.statSync(src);
  if (stat.isDirectory()) {
    fs.mkdirSync(dest, { recursive: true });
    for (const entry of fs.readdirSync(src)) {
      if (entry === '__pycache__' || entry.endsWith('.pyc')) continue;
      copyRecursiveSync(path.join(src, entry), path.join(dest, entry));
    }
  } else {
    fs.copyFileSync(src, dest);
  }
}

// ─── 主流程 ─────────────────────────────────────────────────────────────────

// 1. 检测操作系统
if (process.platform !== 'win32') {
  fail('此 skill 仅支持 Windows 系统。');
}

// 2. 确定路径
const pkgRoot   = path.resolve(__dirname, '..');
const skillSrc  = path.join(pkgRoot, 'skill');
const homeDir   = os.homedir();
const agentsDir = path.join(homeDir, '.agents', 'skills', SKILL_NAME);
const claudeDir = path.join(homeDir, '.claude', 'skills', SKILL_NAME);

// 3. 检查包内 skill 文件是否存在
if (!fs.existsSync(path.join(skillSrc, 'SKILL.md'))) {
  fail(
    `未找到 skill 源文件: ${skillSrc}\n` +
    `npm 包可能已损坏，请尝试清除 npx 缓存后重试。`
  );
}

// 4. 安装到 ~/.agents/skills/
log(`\n${BOLD}正在安装 ${SKILL_NAME} skill...${RESET}`, CYAN);
log(`  目标: ${agentsDir}\n`);

// 清理已有安装
if (fs.existsSync(agentsDir)) {
  fs.rmSync(agentsDir, { recursive: true, force: true });
}
fs.mkdirSync(agentsDir, { recursive: true });

// 复制 SKILL.md
fs.copyFileSync(
  path.join(skillSrc, 'SKILL.md'),
  path.join(agentsDir, 'SKILL.md')
);
log('  [OK] SKILL.md', GREEN);

// 复制 scripts/
const scriptsSrc = path.join(skillSrc, 'scripts');
if (fs.existsSync(scriptsSrc)) {
  copyRecursiveSync(scriptsSrc, path.join(agentsDir, 'scripts'));
  log('  [OK] scripts/', GREEN);
}

// 复制 references/
const refsSrc = path.join(skillSrc, 'references');
if (fs.existsSync(refsSrc)) {
  copyRecursiveSync(refsSrc, path.join(agentsDir, 'references'));
  log('  [OK] references/', GREEN);
}

// 5. 在 ~/.claude/skills/ 创建 Junction
log(`\n${BOLD}设置 Claude Code 链接...${RESET}`, CYAN);

const claudeSkillsDir = path.join(homeDir, '.claude', 'skills');
if (!fs.existsSync(claudeSkillsDir)) {
  fs.mkdirSync(claudeSkillsDir, { recursive: true });
}

// 移除已有的 junction / 目录
// 注意：必须先判断是否为 symlink（junction），用 unlink 而非 rmSync
// rmSync 对 junction 可能会递归删除目标内容
if (fs.existsSync(claudeDir)) {
  const stat = fs.lstatSync(claudeDir);
  if (stat.isSymbolicLink()) {
    fs.unlinkSync(claudeDir);
  } else {
    fs.rmSync(claudeDir, { recursive: true, force: true });
  }
}

// 创建 Junction（Windows 目录联接，不需要管理员权限）
try {
  fs.symlinkSync(agentsDir, claudeDir, 'junction');
  log(`  [OK] Junction: ${claudeDir}`, GREEN);
  log(`       -> ${agentsDir}`, GREEN);
} catch (err) {
  log(`  [WARN] 无法创建 Junction: ${err.message}`, YELLOW);
  log(`  请手动执行:`, YELLOW);
  log(`  New-Item -ItemType Junction -Path "${claudeDir}" -Target "${agentsDir}"`, YELLOW);
}

// 6. 安装成功
log(`\n${'='.repeat(55)}`, GREEN);
log(`  ${SKILL_NAME} 安装成功!`, GREEN);
log(`${'='.repeat(55)}`, GREEN);
log(`\n${BOLD}在 pi 或 Claude Code 中使用:${RESET}`);
log(`  /INSTALL vscode`);
log(`  /INSTALL D:\\Downloads\\setup.exe`);
log(`  /INSTALL https://vendor.example/app.exe`);
log(`\n${BOLD}文件安装位置:${RESET}`);
log(`  ${agentsDir}\n`);
