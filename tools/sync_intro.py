#!/usr/bin/env python3
"""Copy viewer.html and presenter.html into intro/ as that deck's own pages.

Usage: sync_intro.py <repo dir>
The copies differ only in the deck name (data-deck="intro", which keeps this deck's
windows and notes apart from the main deck's) and in the page titles.
"""
import os, sys
repo = sys.argv[1]
TITLE = '日琉諸語における連合複数とその周辺　趣旨説明'
for name, old_title, new_title in (
        ('viewer.html', '<title>代名詞複数と仲間性：北琉球今帰仁謝名方言の包括代名詞（HTML版）</title>', '<title>%s（HTML版）</title>' % TITLE),
        ('presenter.html', '<title>発表者ビュー｜代名詞複数と仲間性</title>', '<title>発表者ビュー｜WS趣旨説明</title>')):
    s = open(os.path.join(repo, name), encoding='utf-8').read()
    assert s.count('<html lang="ja">') == 1 and s.count(old_title) == 1, name
    s = s.replace('<html lang="ja">', '<html lang="ja" data-deck="intro">').replace(old_title, new_title)
    open(os.path.join(repo, 'intro', name), 'w', encoding='utf-8').write(s)
print('synced intro/viewer.html and intro/presenter.html')
