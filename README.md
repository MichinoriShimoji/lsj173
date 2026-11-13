# 代名詞複数と仲間性：北琉球今帰仁謝名方言の包括代名詞

日本言語学会 第173回大会（長崎大）ワークショップ W-6 の発表スライド（下地理則）。

- スライド（聴衆用）: https://michinorishimoji.github.io/lsj173/
- 発表者ビュー（ノート・次のスライド・タイマー）: https://michinorishimoji.github.io/lsj173/presenter.html
- 操作: ← → キー、またはスライド左右の端の矢印で移動。場面の絵や例文カードにカーソルを載せると拡大

## 構成

- `index.html` … 聴衆用スライド。スライド・画像・フォントを1ファイルに収めたもの（保存すればネットなしでも開ける）。`tools/build_single_file.py` で下の材料から作る
- `viewer.html` … 表示プログラム本体（スライドのファイルを読み込んで 1920×1080 で表示）。発表者ビューが使う
- `presenter.html` … 発表者ビュー。「聴衆用ウィンドウを開く」で開いたスライドと連動する
- `project/deck.json` … スライドの並び順
- `project/slides/*.html` … スライド1枚ごとの内容
- `img/` … スライドで使う画像
- `tools/build_single_file.py` … `index.html` を作るスクリプト
