# -*- coding: utf-8 -*-
"""
デプロイ前の整合性チェッカー
guitar_app.html の構造的バグを事前検出する。

使い方:
  py validate.py

全チェックがPASSすれば安全にデプロイ可能。
FAILが出たらそのチェックの説明に従って修正してください。
"""
import sys, io, re, pathlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

_win_path = pathlib.Path(r'C:\Users\toyota shinnnosuke\guitar_app.html')
_local    = pathlib.Path('index.html')
HTML_PATH = _win_path if _win_path.exists() else _local
html = HTML_PATH.read_text(encoding='utf-8')

errors   = []
warnings = []

def chk(label, condition, fix_hint=''):
    if condition:
        print(f'  [PASS] {label}')
    else:
        print(f'  [FAIL] {label}')
        if fix_hint:
            print(f'         → {fix_hint}')
        errors.append(label)

def warn(label, condition, hint=''):
    if condition:
        print(f'  [PASS] {label}')
    else:
        print(f'  [WARN] {label}')
        if hint:
            print(f'         → {hint}')
        warnings.append(label)

print('=' * 55)
print('  guitar_app.html 整合性チェック')
print(f'  ファイルサイズ: {HTML_PATH.stat().st_size // 1024} KB')
print('=' * 55)

# ── CSS ──
print('\n[CSS]')
chk('.d-wrap にfloatYがない（キャラだけ浮かせる）',
    'animation:floatY' not in re.search(r'\.d-wrap\{[^}]+\}', html).group(0) if re.search(r'\.d-wrap\{[^}]+\}', html) else False,
    '.d-wrap CSS から animation を削除してください')
chk('.d-svg にfloatYがある',
    bool(re.search(r'\.d-svg\{[^}]*animation:floatY', html)),
    '.d-svg CSS に animation:floatY 3s ease-in-out infinite を追加してください')
chk('.d-char-img にfloatYがある',
    bool(re.search(r'\.d-char-img\{[^}]*animation:floatY', html)),
    '.d-char-img CSS に animation:floatY を追加してください')
chk('.d-char-bg CSS 存在',
    '.d-char-bg{' in html,
    '.d-char-bg CSS を追加してください')
chk('.stage-bg-grid CSS 存在',
    '.stage-bg-grid{' in html,
    '.stage-bg-grid CSS を追加してください')
chk('.stage-bg-card CSS 存在',
    '.stage-bg-card{' in html,
    '.stage-bg-card CSS を追加してください')

# ── HTML構造 ──
print('\n[HTML構造]')
chk('charBgEl 要素存在',
    'id="charBgEl"' in html,
    '<img class="d-char-bg" id="charBgEl"> を .d-wrap 内に追加してください')
chk('charImgEl 要素存在',
    'id="charImgEl"' in html)
chk('dolphinSvg 要素存在',
    'id="dolphinSvg"' in html)
chk('歯車ボタン(s-setting-btn)が削除済み',
    'onclick="switchSTab(\'setting\')"' not in html,
    '<button class="s-setting-btn"> を削除してください')
chk('homeRewardContent 存在',
    'id="homeRewardContent"' in html)

# ── JS データ定数 ──
print('\n[JS定数]')
chk('_kumanomiImg 定義',  bool(re.search(r"const _kumanomiImg = '(data:image/|images/)", html)))
chk('_kaniImg 定義',      bool(re.search(r"const _kaniImg = '(data:image/|images/)", html)))
chk('_kameImg 定義',      bool(re.search(r"const _kameImg = '(data:image/|images/)", html)))
chk('_kurageImg 定義',    bool(re.search(r"const _kurageImg = '(data:image/|images/)", html)))
chk('_kaiBgImg 定義',     bool(re.search(r"const _kaiBgImg = '(data:image/|images/)", html)))
chk('_isogiBgImg 定義',   bool(re.search(r"const _isogiBgImg = '(data:image/|images/)", html)))

# ── JS ロジック ──
print('\n[JSロジック]')
chk('CHARS 配列存在',
    'const CHARS = [' in html)
chk('STAGE_BKGS 配列存在',
    'const STAGE_BKGS = [' in html)
chk('selectChar 関数存在',
    'function selectChar(' in html)
chk('selectStageBg 関数存在',
    'function selectStageBg(' in html)
chk('stage_bg_ localStorage使用',
    "localStorage.getItem('stage_bg_'" in html or 'stage_bg_' in html)
chk('_activeChar でサイズ取得',
    '_activeChar && _activeChar.size' in html)

# CHARS に bg が残っていないか（分離済みチェック）
m_chars = re.search(r'const CHARS = \[(.*?)\];', html, re.DOTALL)
if m_chars:
    chars_body = m_chars.group(1)
    warn('CHARS に bg プロパティが残っていない（ステージと分離済み）',
         'bg:_' not in chars_body,
         'CHARS エントリから bg: を削除し STAGE_BKGS に移してください')

# STAGE_BKGS エントリ数
m_bkgs = re.findall(r"\{id:'[^']+', name:'[^']+', img:", html)
bkgs_count = len([x for x in m_bkgs])
warn(f'STAGE_BKGS エントリが1件以上ある ({bkgs_count} 件)',
     bkgs_count >= 1)

# ── ご褒美パネル ──
print('\n[ご褒美パネル]')
chk('「ステージ」アコーディオンが存在 (「エリア」ではない)',
    '<span>ステージ</span>' in html,
    'エリア → ステージ にリネームしてください')
chk('stage-bg-grid が使われている',
    'stage-bg-grid' in html)

# ── 最終判定 ──
print('\n' + '=' * 55)
if not errors:
    print(f'  ✓ 全チェックPASS ({len(warnings)} warnings)')
    print('  デプロイOKです。')
else:
    print(f'  ✗ {len(errors)} エラー / {len(warnings)} warnings')
    print('  上記の [FAIL] を修正してからデプロイしてください。')
print('=' * 55)

sys.exit(0 if not errors else 1)
