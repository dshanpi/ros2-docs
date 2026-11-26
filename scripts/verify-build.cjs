const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const {load} = require('cheerio');
const root = path.resolve(__dirname, '..');
const build = path.resolve(root, process.env.DOCS_BUILD_DIR || 'build');
const manifest = require('../migration/manifest.json');
const digest = data => crypto.createHash('sha256').update(data).digest('hex');
let tables = 0, codeBlocks = 0, equations = 0;
const textByPage = new Map();
const norm = text => text.replace(/\s+/g, '');
const base = process.env.DOCS_BASE_URL || '/';
const localPath = url => path.join(build, url.startsWith(base) ? url.slice(base.length) : url.replace(/^\//, ''));
for (const page of manifest.pages) {
  const file = path.join(build, page.slug, 'index.html');
  assert.ok(fs.existsSync(file), `Missing page ${page.slug}`);
  const $ = load(fs.readFileSync(file, 'utf8'));
  const article = $('article .markdown');
  assert.equal(article.length, 1, `Missing article ${page.slug}`);
  assert.equal(article.find('h1').text(), page.title);
  tables += article.find('table').length;
  codeBlocks += article.find('pre').length;
  equations += article.find('math').length;
  textByPage.set(page.path, norm(article.text()));
  for (const img of article.find('img').toArray()) {
    const src = $(img).attr('src');
    assert.ok(src && $(img).attr('alt'), `Missing image source/alt in ${page.path}`);
    assert.ok(fs.existsSync(localPath(src)), `Missing built image ${src}`);
    const original = $(img).parent('a').attr('href');
    assert.ok(original && fs.existsSync(localPath(original)), `Image must link to its original: ${src}`);
    assert.equal(digest(fs.readFileSync(localPath(src))), digest(fs.readFileSync(localPath(original))), `Displayed image differs from original: ${src}`);
    const sourceImage = manifest.images.find(im => path.basename(im.path).split('.')[0] === path.basename(src).split(/[-.]/)[0]);
    assert.ok(sourceImage, `Unknown displayed image: ${src}`);
    assert.equal(digest(fs.readFileSync(localPath(src))), sourceImage.sha256, `Displayed image was re-encoded: ${src}`);
  }
}
for (const im of manifest.images) {
  assert.equal(digest(fs.readFileSync(path.join(build, im.path.replace(/^static\//, '')))), im.sha256, `Build altered image ${im.path}`);
}
assert.equal(tables, manifest.counts.tables, 'Table count changed');
assert.equal(codeBlocks, manifest.counts.code_blocks, 'Code block count changed');
assert.equal(equations, manifest.counts.equations, 'Equation count changed');
assert.equal(fs.readFileSync(path.join(build, 'CNAME'), 'utf8').trim(), 'ros2.100ask.net');
assert.ok(fs.readdirSync(build).some(name => /^search-index.*\.json$/.test(name)), 'Missing local search index');
// On the conversion workstation, compare every source paragraph/table with rendered text.
const auditPath = path.join(root, '.work/source-audit.json');
if (fs.existsSync(auditPath)) {
  const offsets = new Map();
  for (const block of JSON.parse(fs.readFileSync(auditPath, 'utf8'))) {
    const needle = norm(block.text);
    if (!needle) continue;
    const haystack = textByPage.get(block.page);
    const start = offsets.get(block.page) || 0;
    const index = haystack.indexOf(needle, start);
    assert.ok(index >= 0, `Source text missing/reordered in ${block.page} (${block.kind}): ${block.text.slice(0, 140)}`);
    offsets.set(block.page, index + needle.length);
  }
  console.log('Every source body paragraph, code line, heading and table matched the rendered pages in order.');
}
console.log(`Verified ${manifest.pages.length} rendered pages, ${tables} tables, ${codeBlocks} code blocks, ${equations} equations and all original image hashes.`);
