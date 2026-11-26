// Serve the exact extracted files, without Webpack inlining, duplicate asset
// copies, or route-style trailing slashes on the links that open originals.
const path = require('node:path');
const manifest = require('../migration/manifest.json');
module.exports = function originalImages() {
  const base = process.env.DOCS_BASE_URL || '/';
  return tree => {
    function visit(node) {
      if ((node.type === 'image' || node.type === 'link') && node.url?.startsWith('/img/manual/')) {
        if (node.type === 'image') {
          const im = manifest.images.find(image => path.basename(image.path) === path.basename(node.url));
          if (!im) throw new Error(`Unknown original image: ${node.url}`);
          node.data = {...node.data, hProperties: {...node.data?.hProperties, width: im.width, height: im.height, loading: 'lazy', decoding: 'async'}};
        }
        node.url = `pathname://${base}${node.url.slice(1)}`;
      }
      node.children?.forEach(visit);
    }
    visit(tree);
  };
};
