const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '..');
const file = path.join(root, 'migration/manifest.json');
const manifest = JSON.parse(fs.readFileSync(file, 'utf8'));
for (const page of manifest.pages) {
  const data = fs.readFileSync(path.join(root, 'docs', page.path));
  page.sha256 = crypto.createHash('sha256').update(data).digest('hex');
  page.bytes = data.length;
}
fs.writeFileSync(file, JSON.stringify(manifest, null, 2) + '\n');
console.log('Updated Markdown page hashes. Original image checksums remain unchanged.');
