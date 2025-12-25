import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// 読み込むファイル、パスの定義
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = path.resolve(__dirname, '..');
const IGNORE_DIRS = new Set(['node_modules', '.git', 'dist', '.observablehq']);

function getPages(dir) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  const pages = [];

  for (const entry of entries) {
    // 隠しファイルや除外ディレクトリはスキップ
    if (entry.name.startsWith('.') || IGNORE_DIRS.has(entry.name)) continue;

    const fullPath = path.join(dir, entry.name);

    // ディレクトリなら再帰探索
    if (entry.isDirectory()) {
      pages.push(...getPages(fullPath));
      continue;
    }

    // スキップするファイル
    if (!entry.name.endsWith('.md') || entry.name === 'index.md') continue;

    const content = fs.readFileSync(fullPath, 'utf8');
    const frontMatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
    let title = entry.name.replace('.md', '');

    // titleがあればそれを使う
    if (frontMatterMatch) {
      const titleLine = frontMatterMatch[1].match(/^title:\s*(.*)$/m);
      if (titleLine) {
        title = titleLine[1].replace(/^['"]|['"]$/g, '').trim();
      }
    }

    // パス生成
    const relPath = path.relative(PROJECT_ROOT, fullPath);
    const urlPath = '/' + relPath.replace(/\.md$/, '').split(path.sep).join('/');

    pages.push({ title, path: urlPath, file: relPath });
  }

  return pages;
}

// 実行
const pages = getPages(PROJECT_ROOT).sort((a, b) => a.title.localeCompare(b.title));
process.stdout.write(JSON.stringify(pages, null, 2));
