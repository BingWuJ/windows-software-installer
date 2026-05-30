#!/usr/bin/env node
'use strict';

/**
 * 开发辅助脚本：将父目录中的 skill 源文件同步到 npm-publish/skill/ 下。
 * 在 npm publish 之前自动运行（prepublishOnly），也可以手动运行：npm run sync
 */

const path = require('path');
const fs = require('fs');

const GREEN = '\x1b[32m';
const RESET = '\x1b[0m';

const pkgRoot     = __dirname;
const skillSource = path.resolve(pkgRoot, '..');   // 父目录：windows-software-installer/
const skillDest   = path.join(pkgRoot, 'skill');   // 目标：npm-publish/skill/

// 要同步的文件和目录
const FILES_TO_COPY = ['SKILL.md', 'evals'];
const DIRS_TO_COPY  = ['scripts', 'references'];

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
console.log('正在同步 skill 文件到 npm-publish/skill/ ...\n');

// 清理旧目录
if (fs.existsSync(skillDest)) {
  fs.rmSync(skillDest, { recursive: true, force: true });
}
fs.mkdirSync(skillDest, { recursive: true });

// 复制单文件
for (const file of FILES_TO_COPY) {
  const src = path.join(skillSource, file);
  if (!fs.existsSync(src)) {
    console.warn(`  [SKIP] ${file} (源文件不存在)`);
    continue;
  }
  const dest = path.join(skillDest, file);
  const stat = fs.statSync(src);
  if (stat.isDirectory()) {
    copyRecursiveSync(src, dest);
  } else {
    fs.copyFileSync(src, dest);
  }
  console.log(`  ${GREEN}[OK]${RESET} ${file}`);
}

// 复制目录
for (const dir of DIRS_TO_COPY) {
  const src = path.join(skillSource, dir);
  if (!fs.existsSync(src)) {
    console.warn(`  [SKIP] ${dir}/ (源目录不存在)`);
    continue;
  }
  copyRecursiveSync(src, path.join(skillDest, dir));
  console.log(`  ${GREEN}[OK]${RESET} ${dir}/`);
}

// 验证关键文件
const skillMd = path.join(skillDest, 'SKILL.md');
if (!fs.existsSync(skillMd)) {
  console.error('\n[ERROR] SKILL.md 缺失，无法发布。');
  process.exit(1);
}

console.log('\n同步完成，可以执行 npm publish。');
