#!/usr/bin/env python3
"""Build index.html: the audience deck as one file (slides, pictures and fonts inside), which also opens without a network.

Usage: build_single_file.py <repo dir> <fonts dir> <output html>
Source: viewer.html (the page that loads the slide files) + project/deck.json + project/slides/*.html + img/.
The fonts dir holds the unpacked npm packages @fontsource/noto-sans-jp and @fontsource/charis-sil
(npm pack, then untar each into x_<name>/), i.e. x_fontsource-*/package/files/*.woff2.
Speaker notes (<aside>) are left out of the built file.
"""
import base64, glob, html, io, json, os, re, sys
from fontTools import subset
from fontTools.ttLib import TTFont

repo, fonts, out = sys.argv[1], sys.argv[2], sys.argv[3]
page = open(os.path.join(repo, 'viewer.html'), encoding='utf-8').read()
deck = json.load(open(os.path.join(repo, 'project/deck.json'), encoding='utf-8'))
order = deck['order']
slides = {i: re.sub(r'\s*<aside>.*?</aside>', '', open(os.path.join(repo, 'project/slides', i + '.html'), encoding='utf-8').read(), flags=re.S) for i in order}

# ---- pictures used by the slides
images = {}
for s in slides.values():
    for m in re.finditer(r'<img[^>]*\ssrc="([^"]+)"', s):
        src = m.group(1)
        b = re.search(r'/_blob/([0-9a-f]+)', src)
        name = 'img/%s.png' % b.group(1) if b else src
        path = os.path.join(repo, name)
        if name not in images:
            images[name] = 'data:image/png;base64,' + base64.b64encode(open(path, 'rb').read()).decode('ascii')

# ---- characters the deck shows (slides without notes, plus the viewer's own text)
text = page
for s in slides.values():
    text += html.unescape(re.sub(r'<aside>.*?</aside>', '', s, flags=re.S))
chars = sorted(set(ord(c) for c in text if ord(c) >= 0x20))

def find(pattern):
    hits = glob.glob(os.path.join(fonts, pattern))
    assert len(hits) == 1, (pattern, hits)
    return hits[0]

def ranges(cps):
    cps = sorted(cps); outr = []; a = b = cps[0]
    for c in cps[1:]:
        if c == b + 1: b = c
        else: outr.append((a, b)); a = b = c
    outr.append((a, b))
    return ','.join('U+%X' % x if x == y else 'U+%X-%X' % (x, y) for x, y in outr)

faces, report = [], []
def add(family, weight, style, files):
    """files: font files in order of preference; each character goes to the first file that has it."""
    left = set(chars)
    for f in files:
        have = set(TTFont(f).getBestCmap().keys()) & left
        if not have: continue
        left -= have
        opt = subset.Options(); opt.flavor = 'woff2'; opt.layout_features = ['*']; opt.notdef_outline = True
        font = subset.load_font(f, opt)
        sub = subset.Subsetter(opt); sub.populate(unicodes=sorted(have)); sub.subset(font)
        buf = io.BytesIO(); subset.save_font(font, buf, opt)
        faces.append("@font-face{font-family:'%s';font-style:%s;font-weight:%d;font-display:block;src:url(data:font/woff2;base64,%s) format('woff2');unicode-range:%s}" % (
            family, style, weight, base64.b64encode(buf.getvalue()).decode('ascii'), ranges(have)))
        report.append((family, weight, style, os.path.basename(f), len(have), len(buf.getvalue())))
    return left

missing = {}
for w in (400, 500, 700):
    missing[('Noto Sans JP', w)] = add('Noto Sans JP', w, 'normal', [
        find('x_fontsource-noto-sans-jp*/package/files/noto-sans-jp-japanese-%d-normal.woff2' % w),
        find('x_fontsource-noto-sans-jp*/package/files/noto-sans-jp-latin-%d-normal.woff2' % w),
        find('x_fontsource-noto-sans-jp*/package/files/noto-sans-jp-latin-ext-%d-normal.woff2' % w)]
        # the remaining glyphs (arrows, circled digits, ...) sit in the numbered slices
        + sorted(glob.glob(os.path.join(fonts, 'x_fontsource-noto-sans-jp*/package/files/noto-sans-jp-[0-9]*-%d-normal.woff2' % w))))
for w in (400, 700):
    for st in ('normal', 'italic'):
        missing[('Charis SIL', w, st)] = add('Charis SIL', w, st, [
            find('x_fontsource-charis-sil*/package/files/charis-sil-latin-%d-%s.woff2' % (w, st)),
            find('x_fontsource-charis-sil*/package/files/charis-sil-latin-ext-%d-%s.woff2' % (w, st)),
            find('x_fontsource-charis-sil*/package/files/charis-sil-vietnamese-%d-%s.woff2' % (w, st)),
            find('x_fontsource-charis-sil*/package/files/charis-sil-cyrillic-ext-%d-%s.woff2' % (w, st)),
            find('x_fontsource-charis-sil*/package/files/charis-sil-cyrillic-%d-%s.woff2' % (w, st))])

# ---- put everything into the page
a = page.index('<link rel="preconnect" href="https://fonts.googleapis.com">')
b = page.index('>', page.index('<link rel="stylesheet" href="https://fonts.googleapis.com')) + 1
page = page[:a] + '<style>\n' + '\n'.join(faces) + '\n</style>' + page[b:]
data = json.dumps({'order': order, 'slides': slides, 'images': images}, ensure_ascii=False).replace('</', '<\\/')
marker = '<script>\n(function () {'
assert page.count(marker) == 1
page = page.replace(marker, '<script type="application/json" id="deck-data">' + data + '</script>\n' + marker)
assert 'fonts.googleapis.com' not in page and 'https://' not in re.sub(r'data:[^"\')]+', '', page.split('id="deck-data"')[0])
open(out, 'w', encoding='utf-8').write(page)

print('slides', len(order), '| pictures', len(images), '| characters', len(chars), '| size %.1f MB' % (os.path.getsize(out) / 1e6))
for r in report: print('  font', r)
for k, v in missing.items():
    v = [c for c in v if 0x20 < c < 0x2000]
    print('  not in', k, ':', ''.join(chr(c) for c in v)[:80])
