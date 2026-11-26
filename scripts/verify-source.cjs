const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const manifest = require('../migration/manifest.json');
const digest = data => crypto.createHash('sha256').update(data).digest('hex');
for (const image of manifest.images) {
  const data = fs.readFileSync(path.join(root, image.path));
  assert.equal(data.length, image.bytes, `${image.path}: original byte length changed`);
  assert.equal(digest(data), image.sha256, `${image.path}: original image changed`);
}
for (const page of manifest.pages) {
  const data = fs.readFileSync(path.join(root, 'docs', page.path));
  assert.equal(digest(data), page.sha256, `${page.path}: update migration manifest after an intentional content edit`);
  const markdown = data.toString('utf8');
  for (const [, filename] of markdown.matchAll(/\/img\/manual\/([^\s)"<>]+)/g)) {
    assert.ok(fs.existsSync(path.join(root, 'static/img/manual', filename)), `Missing image ${filename}`);
  }
}
assert.equal(manifest.counts.chapters, 15);
assert.equal(manifest.counts.sections, 53);
assert.equal(manifest.images.length, 189);
assert.equal(manifest.headings.length, 270);
console.log(`Verified ${manifest.pages.length} Markdown pages, 270 original headings and 189 byte-identical source images.`);
