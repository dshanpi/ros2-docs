"""Convert the supplied OOXML manual without re-encoding its embedded images.

Usage: python scripts/convert_docx.py path/to/manual.docx
Requires lxml and Pillow. Original tutorial commands are data, never executed.
"""
import argparse
import collections
import hashlib
import html
import io
import json
import re
import zipfile
from pathlib import Path
from lxml import etree as ET
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
NS = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math',
    'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
}
LEVEL = {'3': 1, '4': 2, '5': 3, '116': 4}
CODE = {'95', '172', '174'}

def val(node, path, default=None):
    element = node.find(path, NS) if node is not None else None
    return element.get(f'{{{NS["w"]}}}val', default) if element is not None else default

def sha(data):
    return hashlib.sha256(data).hexdigest()

def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8', newline='\n')

def json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + '\n'

def escape(text):
    def literal(value):
        value = html.escape(value, quote=False)
        return re.sub(r'([\\`*_[\]{}|])', r'\\\1', value)
    parts = []
    last = 0
    # Word often puts Chinese prose immediately after URLs. Explicit anchors
    # prevent GFM autolinks from consuming that prose as part of the hostname.
    for match in re.finditer(r'(?:https?://|www\.)[\x21-\x7e]+', text):
        url = match.group().rstrip('.,;:!?)>"')
        parts.append(literal(text[last:match.start()]))
        href = 'https://' + url if url.startswith('www.') else url
        parts.append(f'<a href="{html.escape(href, quote=True)}">{html.escape(url)}</a>')
        last = match.start() + len(url)
    parts.append(literal(text[last:]))
    return ''.join(parts)

def normalize(text):
    return re.sub(r'\s+', '', text)

def effective(element):
    """Select only one DrawingML/VML fallback; accept inserted, omit deleted text."""
    name = ET.QName(element).localname
    if name == 'AlternateContent':
        choice = element.find('mc:Choice', NS)
        if choice is None:
            choice = element.find('mc:Fallback', NS)
        if choice is not None:
            for child in choice:
                yield from effective(child)
    elif name not in {'del', 'moveFrom', 'Fallback'}:
        yield element

def visible_text(element):
    out = []
    def walk(el):
        for e in effective(el):
            name = ET.QName(e).localname
            if e.tag in {f'{{{NS["w"]}}}t', f'{{{NS["m"]}}}t'}:
                out.append(e.text or '')
            elif name == 'tab':
                out.append('\t')
            elif name in {'br', 'cr'}:
                if e.get(f'{{{NS["w"]}}}type') not in {'page', 'column'}:
                    out.append('\n')
            elif name not in {'pPr', 'rPr', 'instrText', 'delText'}:
                for child in e:
                    walk(child)
    walk(element)
    return ''.join(out)

class Converter:
    def __init__(self, source):
        self.source = source
        self.zip = zipfile.ZipFile(source)
        self.doc = ET.fromstring(self.zip.read('word/document.xml'))
        self.body = list(self.doc.find('w:body', NS))
        self.styles = {s.get(f'{{{NS["w"]}}}styleId'): s for s in ET.fromstring(self.zip.read('word/styles.xml')).findall('w:style', NS)}
        self.numbering = ET.fromstring(self.zip.read('word/numbering.xml'))
        self.nums = {n.get(f'{{{NS["w"]}}}numId'): n for n in self.numbering.findall('w:num', NS)}
        self.abstracts = {n.get(f'{{{NS["w"]}}}abstractNumId'): n for n in self.numbering.findall('w:abstractNum', NS)}
        rels = ET.fromstring(self.zip.read('word/_rels/document.xml.rels'))
        self.rels = {r.get('Id'): r.get('Target') for r in rels}
        self.list_counts = {}
        self.counts = collections.Counter()
        self.images = []
        self.image_uses = collections.Counter()
        self.pages = []
        self.chapters = []
        self.audit = []
        self.headings = []
        self.heading_counts = [0, 0, 0, 0]
        self.current = None
        self.section = ''

    def style(self, p):
        return val(p, 'w:pPr/w:pStyle', 'Normal')

    def numbering_prefix(self, p):
        sid = self.style(p)
        numid = val(p, 'w:pPr/w:numPr/w:numId')
        level = val(p, 'w:pPr/w:numPr/w:ilvl')
        if numid is None:
            s = self.styles.get(sid)
            numid = val(s, 'w:pPr/w:numPr/w:numId')
            level = val(s, 'w:pPr/w:numPr/w:ilvl', '0')
        if numid in {None, '0', '1'}:
            return ''
        level = level or '0'
        num = self.nums.get(numid)
        abstract = self.abstracts.get(val(num, 'w:abstractNumId'))
        if abstract is None:
            return ''
        lvl = abstract.find(f'w:lvl[@w:ilvl="{level}"]', NS)
        if lvl is None:
            return ''
        fmt = val(lvl, 'w:numFmt')
        key = (numid, level)
        override = num.find(f'w:lvlOverride[@w:ilvl="{level}"]', NS)
        start = int(val(override, 'w:startOverride', val(lvl, 'w:start', '1')))
        count = self.list_counts.get(key, start - 1) + 1
        self.list_counts[key] = count
        if fmt == 'bullet':
            return '  ' * int(level) + '- '
        if fmt == 'decimalEnclosedCircleChinese' and count <= 20:
            return chr(0x245F + count) + ' '
        return f'{count}. '

    def extract_images(self):
        for name in self.zip.namelist():
            if not name.startswith('word/media/') or name.endswith('/'):
                continue
            data = self.zip.read(name)
            dest = ROOT / 'static/img/manual' / Path(name).name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            with Image.open(io.BytesIO(data)) as im:
                width, height = im.size
            self.images.append({'source': name, 'path': dest.relative_to(ROOT).as_posix(), 'bytes': len(data), 'sha256': sha(data), 'width': width, 'height': height})

    def image(self, rid, alt):
        target = self.rels.get(rid, '')
        if not target.startswith('media/'):
            raise ValueError(f'Unsupported image relationship: {rid} {target}')
        filename = Path(target).name
        self.image_uses[filename] += 1
        url = f'/img/manual/{filename}'
        return f'\n\n[![{escape(alt)}]({url})]({url})\n\n'

    def mathml(self, el):
        name = ET.QName(el).localname
        if name == 'f':
            return '<mfrac>' + self.mathml(el.find('m:num', NS)) + self.mathml(el.find('m:den', NS)) + '</mfrac>'
        if name == 't':
            return '<mtext>' + html.escape(el.text or '') + '</mtext>'
        if name.endswith('Pr'):
            return ''
        return '<mrow>' + ''.join(self.mathml(c) for c in el) + '</mrow>'

    def inline(self, element, alt='教程配图', plain=False):
        parts = []
        def walk(el):
            for e in effective(el):
                name = ET.QName(e).localname
                if e.tag == f'{{{NS["w"]}}}t':
                    parts.append((e.text or '') if plain else escape(e.text or ''))
                elif name in {'pPr', 'rPr', 'instrText', 'delText'}:
                    continue
                elif name == 'tab':
                    parts.append('\t')
                elif name in {'br', 'cr'}:
                    if e.get(f'{{{NS["w"]}}}type') not in {'page', 'column'}:
                        parts.append('\n' if plain else '  \n')
                elif name == 'oMath':
                    self.counts['equations'] += 1
                    parts.append('<math xmlns="http://www.w3.org/1998/Math/MathML" display="block">' + self.mathml(e) + '</math>')
                elif name == 'blip':
                    rid = e.get(f'{{{NS["r"]}}}embed')
                    if rid:
                        parts.append(self.image(rid, alt))
                elif name == 'imagedata':
                    rid = e.get(f'{{{NS["r"]}}}id')
                    if rid:
                        parts.append(self.image(rid, alt))
                else:
                    # Render emphasis at run level only when not splitting a word.
                    start = len(parts)
                    for child in e:
                        walk(child)
                    if name == 'r' and not plain and e.find('w:rPr/w:b', NS) is not None:
                        joined = ''.join(parts[start:])
                        if joined.strip() and '\n' not in joined and not joined.startswith('<math'):
                            parts[start:] = [f'<strong>{joined}</strong>']
        walk(element)
        return ''.join(parts)

    def add_audit(self, element, kind):
        text = visible_text(element)
        self.audit.append({'page': self.current['path'], 'kind': kind, 'text': text})
        self.counts[kind] += 1

    def table(self, element):
        rows = []
        active = {}
        for ri, tr in enumerate(element.findall('w:tr', NS)):
            row = []
            col = 0
            for tc in tr.findall('w:tc', NS):
                span = int(val(tc, 'w:tcPr/w:gridSpan', '1'))
                merge = tc.find('w:tcPr/w:vMerge', NS)
                if merge is not None and merge.get(f'{{{NS["w"]}}}val') != 'restart' and col in active:
                    active[col]['rowspan'] += 1
                    col += span
                    continue
                cell = {'text': '<br/>'.join(self.inline(p, self.section).replace('\n', ' ') for p in tc.findall('w:p', NS)), 'colspan': span, 'rowspan': 1, 'header': ri == 0}
                row.append(cell)
                if merge is not None:
                    active[col] = cell
                else:
                    active.pop(col, None)
                col += span
            rows.append(row)
        result = ['<table>', '<tbody>']
        for row in rows:
            result.append('<tr>')
            for cell in row:
                tag = 'th' if cell['header'] else 'td'
                attrs = (' scope="col"' if cell['header'] else '')
                for key in ['colspan', 'rowspan']:
                    if cell[key] > 1:
                        attrs += f' {key}="{cell[key]}"'
                # Markdown escapes are not needed inside raw HTML tables.
                txt = re.sub(r'\\([\\`*_[\]{}|])', r'\1', cell['text'])
                result.append(f'<{tag}{attrs}>{txt}</{tag}>')
            result.append('</tr>')
        result += ['</tbody>', '</table>']
        return '\n'.join(result)

    def new_page(self, title, path, slug, number, level):
        page = {'title': title, 'path': path, 'slug': slug, 'number': number, 'level': level, 'content': []}
        self.pages.append(page)
        self.current = page
        return page

    def code_language(self, text, style):
        if style in {'172', '174'}:
            return 'bash'
        if re.search(r'^\s*(from \S+ import|import \w|def \w|class \w.*:)', text, re.M):
            return 'python'
        if '#include' in text or re.search(r'\b(int main|struct |std::|rclcpp::)', text):
            return 'cpp' if 'std::' in text or 'rclcpp' in text else 'c'
        if re.search(r'^\s*(cmake_minimum_required|find_package|add_executable|project)\(', text, re.M):
            return 'cmake'
        if '<package' in text or '<?xml' in text:
            return 'xml'
        if self.heading_counts[0] == 5 and (':=' in text or re.search(r'^\w[^\n]*:', text, re.M)):
            return 'makefile'
        return 'text'

    def convert(self):
        self.extract_images()
        intro = self.new_page('基于 MUSE-PI-PRO 嵌入式机器人教程手册', 'intro.md', '/', '', 0)
        intro['content'] = ['百问科技 · MUSE-PI-PRO 嵌入式 Linux 与 ROS2 机器人开发教程。', '原手册日期：2025/03/12。', '按原手册的 15 章顺序阅读，也可以通过左侧目录或顶部搜索查找内容。点击教程图片可打开原图。']
        started = False
        i = 0
        while i < len(self.body):
            el = self.body[i]
            i += 1
            name = ET.QName(el).localname
            if name not in {'p', 'tbl'}:
                continue
            sid = self.style(el) if name == 'p' else ''
            lvl = LEVEL.get(sid)
            if not started and lvl != 1:
                # Preserve original cover graphics; replace duplicate textboxes with title/date.
                if el.xpath('.//a:blip', namespaces=NS):
                    cover = self.inline(el, '原手册封面')
                    imgs = re.findall(r'\[!\[.*?\]\(.*?\)\]\(.*?\)', cover)
                    # image2 is a page-size decorative border, not a teaching
                    # illustration. Retain its original file without a huge blank cover.
                    intro['content'].extend(img for img in imgs if '/image2.png' not in img)
                continue
            started = True
            if lvl:
                self.heading_counts[lvl - 1] += 1
                for k in range(lvl, 4):
                    self.heading_counts[k] = 0
                chapter, section, third, fourth = self.heading_counts
                title = visible_text(el).strip()
                number = '.'.join(str(n) for n in self.heading_counts[:lvl])
                display = f'第{chapter}章 {title}' if lvl == 1 else f'{number if lvl < 4 else fourth} {title}'
                if lvl == 1:
                    self.new_page(display, f'chapter-{chapter:02}/index.md', f'/chapter-{chapter:02}/', number, lvl)
                    self.chapters.append({'title': display, 'path': self.current['path'], 'number': chapter, 'sections': []})
                elif lvl == 2:
                    self.new_page(display, f'chapter-{chapter:02}/section-{section:02}.md', f'/chapter-{chapter:02}/section-{section:02}/', number, lvl)
                    self.chapters[-1]['sections'].append({'title': display, 'path': self.current['path']})
                else:
                    self.current['content'].append(f'{"#" * (lvl - 1)} {escape(display)}')
                self.section = display
                self.headings.append({'level': lvl, 'title': title, 'number': number, 'page': self.current['path']})
                self.add_audit(el, 'headings')
            elif name == 'tbl':
                self.current['content'].append(self.table(el))
                self.add_audit(el, 'tables')
            elif sid in CODE:
                lines = [visible_text(el)]
                self.add_audit(el, 'code_paragraphs')
                while i < len(self.body) and ET.QName(self.body[i]).localname == 'p' and self.style(self.body[i]) == sid:
                    lines.append(visible_text(self.body[i]))
                    self.add_audit(self.body[i], 'code_paragraphs')
                    i += 1
                text = '\n'.join(lines).replace('\u00a0', ' ')
                fence = '`' * max(3, 1 + max([len(x) for x in re.findall(r'`+', text)] or [0]))
                self.current['content'].append(f'{fence}{self.code_language(text, sid)}\n{text}\n{fence}')
                self.counts['code_blocks'] += 1
            else:
                alt = self.section
                if i < len(self.body) and self.style(self.body[i]) == '22':
                    alt = visible_text(self.body[i]).strip()
                text = self.inline(el, alt).strip()
                self.add_audit(el, 'paragraphs')
                if text:
                    prefix = self.numbering_prefix(el)
                    if sid == '22':
                        text = f'*{text}*'
                    elif sid in {'126', '128', '129'} and not text.startswith('<strong>'):
                        text = f'<strong>{text}</strong>'
                    # Prevent accidental Markdown block syntax in prose/terminal output.
                    if not prefix and re.match(r'^(?:\d+\.|[#>+\-])\s', text):
                        text = re.sub(r'^(\d+)\.', r'\1\\.', text) if text[0].isdigit() else '\\' + text
                    self.current['content'].append(prefix + text)
        intro['content'].append('## 课程目录\n\n' + '\n'.join(f'- [{c["title"]}](./{c["path"]})' for c in self.chapters))
        for chapter in self.chapters:
            page = next(p for p in self.pages if p['path'] == chapter['path'])
            page['content'].append('## 本章目录\n\n' + '\n'.join(f'- [{s["title"]}](./{Path(s["path"]).name})' for s in chapter['sections']))
        page_manifest = []
        for page in self.pages:
            fm = f'---\ntitle: {json.dumps(page["title"], ensure_ascii=False)}\nsidebar_label: {json.dumps(page["title"], ensure_ascii=False)}\nslug: {page["slug"]}\n---\n\n'
            content = fm + '\n\n'.join(page['content']) + '\n'
            write(ROOT / 'docs' / page['path'], content)
            page_manifest.append({k: page[k] for k in ['title', 'path', 'slug', 'number', 'level']} | {'sha256': sha(content.encode()), 'bytes': len(content.encode())})
        sidebar = ['intro'] + [{'type': 'category', 'label': c['title'], 'link': {'type': 'doc', 'id': c['path'][:-3]}, 'items': [s['path'][:-3] for s in c['sections']]} for c in self.chapters]
        write(ROOT / 'sidebars.js', '// Original Word chapter order. Generated by scripts/convert_docx.py.\nexport default ' + json.dumps({'tutorialSidebar': sidebar}, ensure_ascii=False, indent=2) + ';\n')
        for image in self.images:
            image['references'] = self.image_uses[Path(image['path']).name]
        manifest = {'source': {'name': self.source.name, 'bytes': self.source.stat().st_size, 'sha256': sha(self.source.read_bytes())}, 'template': {'repository': 'https://github.com/dshanpi/Docs', 'commit': '07cc305c1640f9802b7dc75acccc1647b0c1bad4'}, 'counts': dict(self.counts) | {'chapters': len(self.chapters), 'sections': sum(len(c['sections']) for c in self.chapters), 'pages': len(self.pages), 'images': len(self.images), 'image_occurrences': sum(self.image_uses.values())}, 'normalization': ['Word cover fallback textboxes are deduplicated into the site title and original date.', 'Code non-breaking spaces are converted to ordinary spaces; tabs and line breaks are preserved.', 'Word page/section breaks and blank layout paragraphs are omitted.', 'Original heading numbering, captions, merged table cells and equations are retained.'], 'pages': page_manifest, 'headings': self.headings, 'images': self.images}
        write(ROOT / 'migration/manifest.json', json_text(manifest))
        write(ROOT / '.work/source-audit.json', json_text(self.audit))
        print(json_text(manifest['counts']))
        unused = [im['path'] for im in self.images if not im['references']]
        print('Unreferenced original media retained:', unused)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    Converter(args.source.resolve()).convert()
