# -*- coding: utf-8 -*-
"""
Unicode Large Character Viewer  v5
PySide6 / Qt6   /   pip install PySide6
"""

import sys
import unicodedata

from PySide6.QtCore import Qt, Signal, QMimeData, QPoint
from PySide6.QtGui import (
    QFont, QAction, QKeySequence, QFontDatabase,
    QPainter, QPen, QColor, QDrag,
)
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QComboBox, QSpinBox, QPushButton, QLineEdit, QTabWidget,
    QSizePolicy, QScrollArea, QGridLayout, QFrame, QSplitter,
    QTextEdit,
)

# ════════════════════════════════════════════════════════════
# 定数
# ════════════════════════════════════════════════════════════

WINDOW_W        = 980
WINDOW_H        = 840
DEFAULT_CHAR    = "驫"
DEFAULT_CMP_L   = "髙"
DEFAULT_CMP_R   = "高"
DEFAULT_PT_MAIN = 300
DEFAULT_PT_CMP  = 200
FAV_MARKER      = "★ "

_BORDER_LIGHT  = "#aaaaaa"
_BORDER_DARK   = "#555555"
_BG_CELL_LIGHT = "#ffffff"
_BG_CELL_DARK  = "#2a2a2a"

# ── スタイル ──────────────────────────────────────────────────

DARK_STYLE = """
QWidget { background-color:#1e1e1e; color:#dddddd; font-size:11pt; }
QLineEdit,QComboBox,QSpinBox {
    background-color:#2b2b2b; color:#fff; border:1px solid #555; padding:3px 5px; }
QComboBox QAbstractItemView {
    background-color:#2b2b2b; color:#fff; selection-background-color:#3a4a7a; }
QSpinBox::up-button,QSpinBox::down-button {
    background-color:#3a3a3a; border:1px solid #666; width:16px; }
QSpinBox::up-arrow {
    border-left:4px solid transparent; border-right:4px solid transparent;
    border-bottom:6px solid #ccc; margin:3px; }
QSpinBox::down-arrow {
    border-left:4px solid transparent; border-right:4px solid transparent;
    border-top:6px solid #ccc; margin:3px; }
QPushButton {
    background-color:#2e2e2e; color:#ccc; border:1px solid #555;
    padding:4px 10px; border-radius:3px; }
QPushButton:hover   { background-color:#3a3a3a; }
QPushButton:checked { background-color:#3a4a7a; border-color:#6677cc; color:#fff; }
QTabWidget::pane { border:1px solid #444; }
QTabBar::tab { background:#2a2a2a; color:#aaa; padding:6px 16px; margin-right:2px; }
QTabBar::tab:selected { background:#444; color:#fff; }
QScrollArea { border:none; }
QToolTip    { background-color:#333; color:#eee; border:1px solid #777; }
QTextEdit   { background-color:#2b2b2b; color:#ddd; border:1px solid #555; }
"""

LIGHT_STYLE = """
QWidget { background-color:#f5f5f5; color:#222; font-size:11pt; }
QLineEdit,QComboBox,QSpinBox {
    background-color:#fff; color:#222; border:1px solid #aaa; padding:3px 5px; }
QComboBox QAbstractItemView {
    background-color:#fff; color:#222; selection-background-color:#cce0ff; }
QPushButton {
    background-color:#e8e8e8; color:#222; border:1px solid #aaa;
    padding:4px 10px; border-radius:3px; }
QPushButton:hover   { background-color:#d8d8d8; }
QPushButton:checked { background-color:#b0c8f0; border-color:#5577cc; color:#111; }
QTabWidget::pane { border:1px solid #bbb; }
QTabBar::tab { background:#e0e0e0; color:#444; padding:6px 16px; margin-right:2px; }
QTabBar::tab:selected { background:#fff; color:#111; }
QScrollArea { border:none; }
QToolTip    { background-color:#fffde7; color:#222; border:1px solid #bbb; }
QTextEdit   { background-color:#fff; color:#222; border:1px solid #aaa; }
"""

# ════════════════════════════════════════════════════════════
# 新字旧字・異体字データ
# ════════════════════════════════════════════════════════════

# (新字, 旧字/異体字, 読み, 備考)
ITAIJI_DATA: list[tuple[str, str, str, str]] = [
    # よく使う旧字体（note記事・bookprint参考）
    ("竜","龍","りゅう","常用 → 旧字"),
    ("悪","惡","あく","常用 → 旧字"),
    ("桜","櫻","さくら","常用 → 旧字"),
    ("応","應","おう","常用 → 旧字"),
    ("楽","樂","たの/がく","常用 → 旧字"),
    ("薬","藥","くすり","常用 → 旧字"),
    ("変","變","へん","常用 → 旧字"),
    ("湾","灣","わん","常用 → 旧字"),
    ("青","靑","あお","常用 → 旧字"),
    ("斎","齋","さい","常用 → 旧字"),
    ("斉","齊","せい","常用 → 旧字"),
    ("並","竝","なら","常用 → 旧字"),
    ("抜","拔","ぬく","常用 → 旧字"),
    ("浄","淨","きよ","常用 → 旧字"),
    ("国","國","くに","常用 → 旧字"),
    ("学","學","まな","常用 → 旧字"),
    ("気","氣","き","常用 → 旧字"),
    ("来","來","く","常用 → 旧字"),
    ("様","樣","さま","常用 → 旧字"),
    ("発","發","はつ","常用 → 旧字"),
    ("転","轉","てん","常用 → 旧字"),
    ("声","聲","こえ","常用 → 旧字"),
    ("体","體","からだ","常用 → 旧字"),
    ("売","賣","うる","常用 → 旧字"),
    ("読","讀","よむ","常用 → 旧字"),
    ("関","關","かん","常用 → 旧字"),
    ("広","廣","ひろ","常用 → 旧字"),
    ("図","圖","ず","常用 → 旧字"),
    ("台","臺","だい","常用 → 旧字"),
    #("祈","祈","いのる","同字"),
    ("旧","舊","きゅう","常用 → 旧字"),
    ("円","圓","えん","常用 → 旧字"),
    # 人名異体字（bookprint参考）
    ("高","髙","こう","はしごだか（異体字）U+9AD9"),
    ("崎","﨑","さき","異体字 U+FA11"),
    ("柳","栁","やなぎ","異体字 U+6801"),
    ("柳","桺","やなぎ","異体字 U+687A"),
    ("喜","㐂","き","草書体 U+3402"),
    ("土","圡","つち","異体字 U+5721"),
    ("橋","槗","はし","異体字 U+69D7"),
    ("昇","曻","のぼる","異体字 U+66FB"),
    ("辺","邉","へん","異体字 U+9089"),
    ("辺","邊","へん","異体字 U+908A"),
    ("浜","濵","はま","異体字 U+6FF5"),
    # 厚労省告示（itaiji.pdf 参考 - 代表的なもの）
    ("亜","亞","あ","旧字体"),
    ("悪","惡","あく","旧字体"),
    ("囲","圍","い","旧字体"),
    ("医","醫","い","旧字体"),
    ("壱","壹","いち","旧字体"),
    ("逸","逸","いつ","同字"),
    ("稲","稻","いね","旧字体"),
    ("飲","飮","のむ","旧字体"),
    ("隠","隱","かく","旧字体"),
    ("宇","宇","う","同字"),
    ("栄","榮","さか","旧字体"),
    ("営","營","いとな","旧字体"),
    ("衛","衞","まも","旧字体"),
    ("駅","驛","えき","旧字体"),
    #("謁","謁","えつ","同字"),
    ("縁","緣","えん","旧字体"),
    ("艶","艷","つや","旧字体"),
    ("横","橫","よこ","旧字体"),
    ("欧","歐","おう","旧字体"),
    ("殴","毆","なぐ","旧字体"),
    ("翁","翁","おきな","同字"),
    ("奥","奧","おく","旧字体"),
    ("仮","假","かり","旧字体"),
    ("価","價","ね","旧字体"),
    ("画","畫","え","旧字体"),
    ("会","會","あう","旧字体"),
    ("壊","壞","こわ","旧字体"),
    ("懐","懷","なつ","旧字体"),
    ("拡","擴","ひろ","旧字体"),
    ("覚","覺","さと","旧字体"),
    ("岳","嶽","たけ","旧字体"),
    ("缶","罐","かん","旧字体"),
    ("歓","歡","よろこ","旧字体"),
    ("観","觀","み","旧字体"),
    #("漢","漢","かん","同字"),
    #("器","器","うつわ","同字"),
    ("帰","歸","かえ","旧字体"),
    #("既","既","すで","同字"),
    #("祈","祈","いの","同字"),
    ("区","區","く","旧字体"),
    ("駆","驅","か","旧字体"),
    ("勲","勳","いさお","旧字体"),
    ("恵","惠","めぐ","旧字体"),
    ("渓","溪","たに","旧字体"),
    ("経","經","たて","旧字体"),
    ("継","繼","つ","旧字体"),
    ("欠","缺","か","旧字体"),
    ("権","權","けん","旧字体"),
    ("検","檢","しら","旧字体"),
    ("献","獻","たてまつ","旧字体"),
    ("験","驗","しるし","旧字体"),
    ("研","硏","とぐ","異体字"),
    ("剣","劍","つるぎ","旧字体"),
    #("絹","絹","きぬ","同字"),
    ("顕","顯","あきら","旧字体"),
    ("号","號","ごう","旧字体"),
    ("効","效","きき","旧字体"),
    ("広","廣","ひろ","旧字体"),
    ("恒","恆","つね","旧字体"),
    ("鉱","鑛","あら","旧字体"),
    #("溝","溝","みぞ","同字"),
    ("穀","穀","こく","旧字体"),
    ("砕","碎","くだ","旧字体"),
    ("済","濟","す","旧字体"),
    ("斎","齋","さい","旧字体"),
    ("剤","劑","ざい","旧字体"),
    #("殺","殺","ころ","旧字体"),
    ("雑","雜","まじ","旧字体"),
    ("蚕","蠶","かいこ","旧字体"),
    ("賛","贊","たす","旧字体"),
    ("糸","絲","いと","旧字体"),
    ("歯","齒","は","旧字体"),
    ("児","兒","こ","旧字体"),
    ("辞","辭","や","旧字体"),
    ("湿","濕","しめ","旧字体"),
    ("実","實","み","旧字体"),
    #("社","社","やしろ","異体字"),
    #("者","者","もの","異体字"),
    ("写","寫","うつ","旧字体"),
    ("寿","壽","ことぶき","旧字体"),
    ("将","將","しょう","旧字体"),
    ("奨","奬","すす","旧字体"),
    ("焼","燒","や","旧字体"),
    ("称","稱","たた","旧字体"),
    ("条","條","すじ","旧字体"),
    ("証","證","あかし","旧字体"),
    ("乗","乘","の","旧字体"),
    ("剰","剩","あま","旧字体"),
    ("嬢","孃","むすめ","旧字体"),
    ("醸","釀","かも","旧字体"),
    ("触","觸","ふ","旧字体"),
    ("寝","寢","ね","旧字体"),
    ("尽","盡","つ","旧字体"),
    ("図","圖","ず","旧字体"),
    ("粋","粹","いき","旧字体"),
    ("穂","穗","ほ","旧字体"),
    ("随","隨","したが","旧字体"),
    ("髄","髓","ずい","旧字体"),
    ("数","數","かず","旧字体"),
    ("静","靜","しず","旧字体"),
    ("席","席","せき","同字"),
    #("節","節","ふし","旧字体"),
    ("専","專","もっぱ","旧字体"),
    ("浅","淺","あさ","旧字体"),
    ("禅","禪","ぜん","旧字体"),
    ("争","爭","あらそ","旧字体"),
    ("総","總","す","旧字体"),
    ("騒","騷","さわ","旧字体"),
    #("贈","贈","おく","旧字体"),
    ("属","屬","ぞく","旧字体"),
    ("続","續","つづ","旧字体"),
    ("堕","墮","お","旧字体"),
    ("滞","滯","とどこ","旧字体"),
    ("択","擇","えら","旧字体"),
    ("担","擔","にな","旧字体"),
    ("胆","膽","きも","旧字体"),
    ("断","斷","た","旧字体"),
    ("伝","傳","つた","旧字体"),
    #("塗","塗","ぬ","旧字体"),
    ("当","當","あた","旧字体"),
    ("稲","稻","いね","旧字体"),
    ("読","讀","よむ","旧字体"),
    ("独","獨","ひと","旧字体"),
    #("豚","豚","ぶた","同字"),
    #("難","難","むずか","旧字体"),
    ("弐","貳","に","旧字体"),
    ("脳","腦","のう","旧字体"),
    ("廃","廢","すた","旧字体"),
    ("拝","拜","おが","旧字体"),
    #("梅","梅","うめ","異体字"),
    ("発","發","はつ","旧字体"),
    ("蛮","蠻","ばん","旧字体"),
    ("秘","祕","ひ","旧字体"),
    ("浜","濱","はま","旧字体"),
    ("瓶","甁","びん","旧字体"),
    #("怖","怖","こわ","異体字"),
    ("払","拂","はら","旧字体"),
    ("仏","佛","ほとけ","旧字体"),
    ("辺","邊","へん","旧字体"),
    ("変","變","へん","旧字体"),
    ("弁","辯","べん","旧字体"),
    ("弁","辨","べん","旧字体"),
    ("豊","豐","ゆたか","旧字体"),
    #("墨","墨","すみ","異体字"),
    ("没","沒","しず","旧字体"),
    ("翻","飜","ひるが","旧字体"),
    ("毎","每","まい","旧字体"),
    ("万","萬","まん","旧字体"),
    ("満","滿","み","旧字体"),
    #("免","免","まぬか","旧字体"),
    ("麺","麵","めん","旧字体"),
    ("黙","默","だま","旧字体"),
    ("訳","譯","わけ","旧字体"),
    ("薬","藥","くすり","旧字体"),
    ("与","與","あた","旧字体"),
    ("余","餘","あま","旧字体"),
    ("預","預","あず","旧字体"),
    ("予","豫","あらかじ","旧字体"),
    ("様","樣","さま","旧字体"),
    ("来","來","く","旧字体"),
    ("乱","亂","みだ","旧字体"),
    ("覧","覽","み","旧字体"),
    ("龍","竜","りゅう","旧字 → 常用"),
    ("両","兩","りょう","旧字体"),
    ("励","勵","はげ","旧字体"),
    ("礼","禮","れい","旧字体"),
    ("隷","隸","れい","旧字体"),
    ("霊","靈","たま","旧字体"),
    ("齢","齡","とし","旧字体"),
    ("恋","戀","こい","旧字体"),
    ("楼","樓","たかどの","旧字体"),
    ("炉","爐","いろり","旧字体"),
    ("朗","朖","ほが","異体字"),
    ("録","錄","しる","旧字体"),
    ("湾","灣","わん","旧字体"),
    #ここから修正加えた部分
    ("祈", "祷", "いのる", "略字"),
    ("祈", "禱", "いのる", "旧字体"),
    ("謁", "謁", "えつ", "旧字体"),
    ("漢", "漢", "かん", "同字"),
    ("器", "器", "うつわ", "旧字体"),
    ("既", "既", "すで", "旧字体"),
    ("絹", "绢", "きぬ", "異体字"),
    #("溝","溝","みぞ","同字"),
    ("殺", "殺", "ころ", "旧字体"),
    ("社", "社", "やしろ", "旧字体"),
    ("者", "者", "もの", "旧字体"),
    ("節", "節", "ふし", "旧字体"),
    ("贈", "贈", "おく", "旧字体"),
    ("塗", "涂", "ぬ", "異体字"),
    ("塗", "𡍼", "ぬ", "同字"),
    ("塗", "𭏚", "ぬ", "同字"),
    ("塗", "𮓨", "ぬ", "同字"),
    ("豚", "豘", "ぶた", "異体字"),
    ("難", "難", "むずか", "旧字体"),
    ("梅", "梅", "うめ", "旧字体"),
    ("梅", "䊈", "うめ", "異体字"),
    ("怖", "悑", "こわ", "異体字"),
    ("墨", "墨", "すみ", "旧字体"),
    ("免", "免", "まぬか", "旧字体"),
]

# ════════════════════════════════════════════════════════════
# お気に入りフォント（メモリ内シングルトン）
# ════════════════════════════════════════════════════════════

class FavFonts:
    def __init__(self):
        self._favs: list[str] = []
        self._listeners: list = []
    def toggle(self, family):
        if family in self._favs: self._favs.remove(family)
        else: self._favs.append(family)
        self._fire()
    def is_fav(self, f): return f in self._favs
    def sorted_list(self, all_):
        return [FAV_MARKER+f for f in self._favs if f in all_] + \
               [f for f in all_ if f not in self._favs]
    @staticmethod
    def strip(d): return d.removeprefix(FAV_MARKER)
    def on_change(self, cb): self._listeners.append(cb)
    def _fire(self):
        for cb in self._listeners: cb()

FAV = FavFonts()

# ════════════════════════════════════════════════════════════
# FontCombo
# ════════════════════════════════════════════════════════════

class FontCombo(QWidget):
    changed = Signal(str)
    def __init__(self, all_families, parent=None):
        super().__init__(parent)
        self._all = all_families
        self._combo = QComboBox(); self._combo.setMaximumWidth(300)
        self._btn = QPushButton("☆"); self._btn.setFixedWidth(30)
        self._btn.setToolTip("お気に入りに追加/削除")
        self._btn.clicked.connect(self._toggle)
        lay = QHBoxLayout(self); lay.setContentsMargins(0,0,0,0); lay.setSpacing(3)
        lay.addWidget(self._combo); lay.addWidget(self._btn)
        self._rebuild()
        FAV.on_change(self._rebuild)
        self._combo.currentTextChanged.connect(self._on_change)
    def _rebuild(self):
        prev = self.currentFamily()
        self._combo.blockSignals(True); self._combo.clear()
        self._combo.addItems(FAV.sorted_list(self._all))
        for c in (FAV_MARKER+prev, prev):
            i = self._combo.findText(c)
            if i >= 0: self._combo.setCurrentIndex(i); break
        self._combo.blockSignals(False); self._update_btn()
    def _on_change(self, _): self._update_btn(); self.changed.emit(self.currentFamily())
    def _update_btn(self): self._btn.setText("★" if FAV.is_fav(self.currentFamily()) else "☆")
    def _toggle(self): FAV.toggle(self.currentFamily())
    def currentFamily(self): return FAV.strip(self._combo.currentText())

# ════════════════════════════════════════════════════════════
# CharCanvas — QPainter 中央描画（コピー対応）
# ════════════════════════════════════════════════════════════

class CharCanvas(QWidget):
    def __init__(self, draggable=False, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(80, 80)
        self._text   = DEFAULT_CHAR
        self._family = ""
        self._max_pt = DEFAULT_PT_MAIN
        self._dark   = False
        self._drag   = draggable
        self._drag_start: QPoint | None = None

    def setText(self, t):   self._text = t or DEFAULT_CHAR; self.update()
    def setDisplayFont(self, f, p): self._family=f; self._max_pt=p; self.update()
    def setDark(self, d):   self._dark=d; self.update()
    def currentText(self):  return self._text

    def paintEvent(self, _):
        if not self._family: return
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        bg = QColor(_BG_CELL_DARK if self._dark else _BG_CELL_LIGHT)
        bdr= QColor(_BORDER_DARK  if self._dark else _BORDER_LIGHT)
        p.fillRect(self.rect(), bg)
        p.setPen(QPen(bdr, 1))
        p.drawRect(self.rect().adjusted(0,0,-1,-1))
        pt = min(self._max_pt, max(16, int(self.height()*0.78)))
        p.setFont(QFont(self._family, pt))
        p.setPen(QColor("#dddddd" if self._dark else "#222222"))
        p.drawText(self.rect(), Qt.AlignHCenter|Qt.AlignVCenter, self._text)
        p.end()

    def resizeEvent(self, e): super().resizeEvent(e); self.update()

    # ── ドラッグ ──
    def mousePressEvent(self, e):
        if self._drag and e.button() == Qt.LeftButton:
            self._drag_start = e.pos()

    def mouseMoveEvent(self, e):
        if not (self._drag and self._drag_start): return
        if (e.pos()-self._drag_start).manhattanLength() < 10: return
        drag = QDrag(self)
        mime = QMimeData(); mime.setText(self._text)
        drag.setMimeData(mime)
        drag.exec(Qt.CopyAction)
        self._drag_start = None

    def mouseReleaseEvent(self, e): self._drag_start = None

# ════════════════════════════════════════════════════════════
# ヘルパー
# ════════════════════════════════════════════════════════════

def _lbl(text, bold=False):
    w = QLabel(text)
    if bold: f=w.font(); f.setBold(True); w.setFont(f)
    return w

def _char_info(char):
    cp = f"U+{ord(char):04X}"
    try: name = unicodedata.name(char)
    except ValueError: name = "（名称未定義）"
    return cp, name

def _spinbox(val, lo=16, hi=1024, w=72):
    sb = QSpinBox(); sb.setRange(lo,hi); sb.setValue(val); sb.setFixedWidth(w)
    return sb

def _copy_btn(get_text):
    btn = QPushButton("コピー")
    btn.setFixedWidth(72)
    btn.clicked.connect(lambda: QApplication.clipboard().setText(get_text()))
    return btn

# ════════════════════════════════════════════════════════════
# MainTab
# ════════════════════════════════════════════════════════════

class MainTab(QWidget):
    def __init__(self, families, dark, parent=None):
        super().__init__(parent)
        self._families=families; self._umode=False; self._dark=dark
        self._build(); self._conn(); self.refresh()

    def _build(self):
        root=QVBoxLayout(self); root.setSpacing(4); root.setContentsMargins(6,6,6,6)
        ctrl=QHBoxLayout(); ctrl.setSpacing(6)
        self.btn_mode=QPushButton("文字入力"); self.btn_mode.setCheckable(True)
        self.btn_mode.setFixedWidth(100); self.btn_mode.clicked.connect(self._toggle_mode)
        self.edit_char=QLineEdit(); self.edit_char.setPlaceholderText("文字を入力")
        self.edit_char.setFixedWidth(120)
        self.font_combo=FontCombo(self._families)
        self.spin_pt=_spinbox(DEFAULT_PT_MAIN)
        self.btn_reset=QPushButton("リセット"); self.btn_reset.clicked.connect(self.reset)
        ctrl.addWidget(self.btn_mode); ctrl.addWidget(self.edit_char)
        ctrl.addSpacing(6); ctrl.addWidget(_lbl("フォント:")); ctrl.addWidget(self.font_combo)
        ctrl.addSpacing(6); ctrl.addWidget(_lbl("上限pt:")); ctrl.addWidget(self.spin_pt)
        ctrl.addWidget(self.btn_reset); ctrl.addStretch(); root.addLayout(ctrl)
        self.canvas=CharCanvas(draggable=False); self.canvas.setDark(self._dark)
        root.addWidget(self.canvas, stretch=1)
        info=QHBoxLayout(); info.setSpacing(12)
        self.lbl_code=QLabel("-"); self.lbl_name=QLabel("-"); self.lbl_utf8=QLabel("-")
        for h,l in [("コードポイント:",self.lbl_code),("Unicode名:",self.lbl_name),("UTF-8:",self.lbl_utf8)]:
            info.addWidget(_lbl(h,bold=True)); info.addWidget(l)
        info.addStretch(); root.addLayout(info)

    def _conn(self):
        self.edit_char.textChanged.connect(self.refresh)
        self.font_combo.changed.connect(lambda _: self.refresh())
        self.spin_pt.valueChanged.connect(self.refresh)

    def _toggle_mode(self):
        self._umode=self.btn_mode.isChecked()
        self.btn_mode.setText("U+ 入力" if self._umode else "文字入力")
        self.edit_char.setPlaceholderText("U+4E00" if self._umode else "文字を入力")
        self.edit_char.clear()

    def set_dark(self, d): self._dark=d; self.canvas.setDark(d)
    def reset(self):
        self.edit_char.clear(); self.spin_pt.setValue(DEFAULT_PT_MAIN)
        if self.btn_mode.isChecked(): self.btn_mode.setChecked(False); self._toggle_mode()

    @property
    def current_char(self):
        t=self.edit_char.text().strip()
        if not t: return DEFAULT_CHAR
        if self._umode:
            s=t.upper().lstrip("U").lstrip("+")
            try:
                cp=int(s,16)
                if 0<=cp<=0x10FFFF: return chr(cp)
            except ValueError: pass
            return DEFAULT_CHAR
        return t[0]

    def refresh(self):
        char=self.current_char; family=self.font_combo.currentFamily(); maxp=self.spin_pt.value()
        self.canvas.setText(char); self.canvas.setDisplayFont(family, maxp)
        cp,name=_char_info(char)
        self.lbl_code.setText(cp); self.lbl_name.setText(name)
        self.lbl_utf8.setText(" ".join(f"{b:02X}" for b in char.encode("utf-8")))

# ════════════════════════════════════════════════════════════
# MultiTab
# ════════════════════════════════════════════════════════════

class MultiTab(QWidget):
    def __init__(self, families, dark, parent=None):
        super().__init__(parent)
        self._families=families; self._dark=dark
        self._build(); self._conn(); self.refresh()

    def _build(self):
        root=QVBoxLayout(self); root.setSpacing(4); root.setContentsMargins(6,6,6,6)
        ctrl=QHBoxLayout(); ctrl.setSpacing(6)
        self.edit=QLineEdit(); self.edit.setPlaceholderText("複数文字 例: 魑魅魍魎")
        self.edit.setMinimumWidth(200)
        self.font_combo=FontCombo(self._families)
        self.spin_pt=_spinbox(DEFAULT_PT_MAIN)
        self.btn_reset=QPushButton("リセット"); self.btn_reset.clicked.connect(self.reset)
        ctrl.addWidget(_lbl("文字列:")); ctrl.addWidget(self.edit)
        ctrl.addSpacing(6); ctrl.addWidget(_lbl("フォント:")); ctrl.addWidget(self.font_combo)
        ctrl.addSpacing(6); ctrl.addWidget(_lbl("上限pt:")); ctrl.addWidget(self.spin_pt)
        ctrl.addWidget(self.btn_reset); ctrl.addStretch(); root.addLayout(ctrl)
        self.canvas=CharCanvas(); self.canvas.setDark(self._dark)
        root.addWidget(self.canvas, stretch=1)

    def _conn(self):
        self.edit.textChanged.connect(self.refresh)
        self.font_combo.changed.connect(lambda _: self.refresh())
        self.spin_pt.valueChanged.connect(self.refresh)

    def set_dark(self, d): self._dark=d; self.canvas.setDark(d)
    def reset(self): self.edit.clear(); self.spin_pt.setValue(DEFAULT_PT_MAIN)
    def refresh(self):
        self.canvas.setText(self.edit.text() or "魑魅魍魎")
        self.canvas.setDisplayFont(self.font_combo.currentFamily(), self.spin_pt.value())

# ════════════════════════════════════════════════════════════
# CharPane（比較タブ用、コピー対応）
# ════════════════════════════════════════════════════════════

class CharPane(QWidget):
    def __init__(self, families, default, show_font=True, show_input=True, dark=False, parent=None):
        super().__init__(parent)
        self._default=default; self._dark=dark
        root=QVBoxLayout(self); root.setSpacing(3); root.setContentsMargins(3,3,3,3)
        if show_input:
            self.edit=QLineEdit(); self.edit.setPlaceholderText(default); root.addWidget(self.edit)
        else: self.edit=None
        if show_font:
            self.font_combo=FontCombo(families); root.addWidget(self.font_combo)
            self.font_combo.changed.connect(lambda _: self._do())
        else: self.font_combo=None
        # ドラッグコピー対応
        self.canvas=CharCanvas(draggable=True); self.canvas.setDark(dark)
        root.addWidget(self.canvas, stretch=1)
        # コピーボタン行
        copy_row=QHBoxLayout()
        self.lbl_cp=QLabel("-"); self.lbl_name=QLabel("-")
        for l in (self.lbl_cp, self.lbl_name):
            l.setAlignment(Qt.AlignCenter); l.setWordWrap(True)
        copy_row.addWidget(self.lbl_cp); copy_row.addWidget(self.lbl_name)
        root.addLayout(copy_row)
        # 文字コピー／CP コピー
        btn_row=QHBoxLayout()
        btn_row.addWidget(_copy_btn(lambda: self.canvas.currentText()))
        btn_row.addWidget(_copy_btn(lambda: self.lbl_cp.text()))
        btn_row.addStretch()
        root.addLayout(btn_row)
        if self.edit: self.edit.textChanged.connect(self._do)

    def _cur(self):
        if self.edit:
            t=self.edit.text(); return t[0] if t else self._default
        return self._default

    def _do(self, family="", maxp=DEFAULT_PT_CMP):
        if not family and self.font_combo: family=self.font_combo.currentFamily()
        char=self._cur()
        self.canvas.setText(char)
        if family: self.canvas.setDisplayFont(family, maxp)
        cp,name=_char_info(char); self.lbl_cp.setText(cp); self.lbl_name.setText(name)

    def refresh_shared(self, family, maxp=DEFAULT_PT_CMP): self._do(family, maxp)
    def set_char(self, char): self._default=char; self._do()
    def set_dark(self, d): self._dark=d; self.canvas.setDark(d)

# ════════════════════════════════════════════════════════════
# CompareTab（異体字比較）
# ════════════════════════════════════════════════════════════

class CompareTab(QWidget):
    def __init__(self, families, dark, parent=None):
        super().__init__(parent)
        self._families=families; self._dark=dark
        self._build(); self._conn(); self.refresh()

    def _build(self):
        root=QVBoxLayout(self); root.setSpacing(4); root.setContentsMargins(6,6,6,6)
        top=QHBoxLayout()
        self.font_combo=FontCombo(self._families); self.font_combo.setMaximumWidth(340)
        self.spin_pt=_spinbox(DEFAULT_PT_CMP)
        self.btn_reset=QPushButton("リセット"); self.btn_reset.clicked.connect(self.reset)
        top.addWidget(_lbl("共通フォント:")); top.addWidget(self.font_combo)
        top.addSpacing(10); top.addWidget(_lbl("上限pt:")); top.addWidget(self.spin_pt)
        top.addSpacing(10); top.addWidget(self.btn_reset); top.addStretch()
        root.addLayout(top)
        cols=QHBoxLayout(); cols.setSpacing(8)
        self.pane_l=CharPane(self._families, DEFAULT_CMP_L, show_font=False, dark=self._dark)
        self.pane_r=CharPane(self._families, DEFAULT_CMP_R, show_font=False, dark=self._dark)
        cols.addWidget(self.pane_l); cols.addWidget(self.pane_r)
        root.addLayout(cols, stretch=1)

    def _conn(self):
        self.font_combo.changed.connect(lambda _: self.refresh())
        self.spin_pt.valueChanged.connect(self.refresh)
        self.pane_l.edit.textChanged.connect(self.refresh)
        self.pane_r.edit.textChanged.connect(self.refresh)

    def set_dark(self, d): self.pane_l.set_dark(d); self.pane_r.set_dark(d)
    def reset(self):
        self.pane_l.edit.clear(); self.pane_r.edit.clear(); self.spin_pt.setValue(DEFAULT_PT_CMP)

    def refresh(self):
        f=self.font_combo.currentFamily(); p=self.spin_pt.value()
        self.pane_l.refresh_shared(f,p); self.pane_r.refresh_shared(f,p)

# ════════════════════════════════════════════════════════════
# FontCompareTab
# ════════════════════════════════════════════════════════════

class FontCompareTab(QWidget):
    def __init__(self, families, dark, parent=None):
        super().__init__(parent)
        self._families=families; self._dark=dark; self._char=DEFAULT_CHAR
        self._build(); self._conn(); self.refresh()

    def _build(self):
        root=QVBoxLayout(self); root.setSpacing(4); root.setContentsMargins(6,6,6,6)
        top=QHBoxLayout()
        self.spin_pt=_spinbox(DEFAULT_PT_CMP)
        self.btn_reset=QPushButton("リセット"); self.btn_reset.clicked.connect(self.reset)
        top.addWidget(_lbl("上限pt:")); top.addWidget(self.spin_pt)
        top.addWidget(self.btn_reset); top.addStretch(); root.addLayout(top)
        cols=QHBoxLayout(); cols.setSpacing(8)
        self.pane_l=CharPane(self._families,DEFAULT_CHAR,show_font=True,show_input=False,dark=self._dark)
        self.pane_r=CharPane(self._families,DEFAULT_CHAR,show_font=True,show_input=False,dark=self._dark)
        cols.addWidget(self.pane_l); cols.addWidget(self.pane_r)
        root.addLayout(cols, stretch=1)

    def _conn(self):
        self.pane_l.font_combo.changed.connect(lambda _: self.refresh())
        self.pane_r.font_combo.changed.connect(lambda _: self.refresh())
        self.spin_pt.valueChanged.connect(self.refresh)

    def set_dark(self, d): self.pane_l.set_dark(d); self.pane_r.set_dark(d)
    def set_char(self, c): self._char=c; self.refresh()
    def reset(self): self.spin_pt.setValue(DEFAULT_PT_CMP)

    def refresh(self):
        p=self.spin_pt.value()
        for pane in (self.pane_l, self.pane_r):
            f=pane.font_combo.currentFamily()
            pane.canvas.setText(self._char); pane.canvas.setDisplayFont(f,p)
            cp,name=_char_info(self._char); pane.lbl_cp.setText(cp); pane.lbl_name.setText(name)

# ════════════════════════════════════════════════════════════
# 新字旧字タブ (ItaijiTab)
# ════════════════════════════════════════════════════════════

class ItaijiTab(QWidget):
    """
    新字旧字・異体字の一覧表。
    クリックで右側の詳細パネルに大きく表示。
    """
    def __init__(self, families, dark, parent=None):
        super().__init__(parent)
        self._families=families; self._dark=dark
        self._build()

    def _build(self):
        root=QHBoxLayout(self); root.setContentsMargins(4,4,4,4); root.setSpacing(4)

        # ── 左: テーブル ──
        left=QWidget(); llay=QVBoxLayout(left); llay.setSpacing(4); llay.setContentsMargins(0,0,0,0)

        self.search_edit=QLineEdit(); self.search_edit.setPlaceholderText("検索（新字/旧字/読み）")
        self.search_edit.textChanged.connect(self._filter)
        llay.addWidget(self.search_edit)

        self.font_combo=FontCombo(self._families)
        llay.addWidget(self.font_combo)
        self.font_combo.changed.connect(self._rebuild_grid)

        self.scroll=QScrollArea(); self.scroll.setWidgetResizable(True)
        self._container=QWidget(); self._grid=QGridLayout(self._container); self._grid.setSpacing(2)
        self.scroll.setWidget(self._container)
        llay.addWidget(self.scroll, stretch=1)

        # ── 右: 詳細パネル ──
        right=QWidget(); rlay=QVBoxLayout(right); rlay.setSpacing(6); rlay.setContentsMargins(4,4,4,4)
        right.setFixedWidth(320)

        self.canvas_new=CharCanvas(draggable=True); self.canvas_new.setDark(self._dark)
        self.canvas_new.setMinimumHeight(180)
        self.canvas_old=CharCanvas(draggable=True); self.canvas_old.setDark(self._dark)
        self.canvas_old.setMinimumHeight(180)

        self.lbl_new_cp=QLabel("-"); self.lbl_old_cp=QLabel("-")
        self.lbl_new_name=QLabel("-"); self.lbl_old_name=QLabel("-")
        self.lbl_yomi=QLabel("-"); self.lbl_note=QLabel("-")
        for l in (self.lbl_new_cp,self.lbl_old_cp,self.lbl_new_name,self.lbl_old_name,
                  self.lbl_yomi,self.lbl_note):
            l.setAlignment(Qt.AlignCenter); l.setWordWrap(True)

        def _pair_row(canvas, lbl_cp, lbl_name, title):
            box=QVBoxLayout()
            box.addWidget(_lbl(title, bold=True))
            box.addWidget(canvas, stretch=1)
            box.addWidget(lbl_cp); box.addWidget(lbl_name)
            btn_c=_copy_btn(canvas.currentText)
            btn_cp=_copy_btn(lbl_cp.text)
            r=QHBoxLayout(); r.addWidget(btn_c); r.addWidget(btn_cp); r.addStretch()
            box.addLayout(r)
            return box

        h=QHBoxLayout()
        h.addLayout(_pair_row(self.canvas_new, self.lbl_new_cp, self.lbl_new_name, "新字"))
        h.addLayout(_pair_row(self.canvas_old, self.lbl_old_cp, self.lbl_old_name, "旧字/異体字"))
        rlay.addLayout(h, stretch=1)

        rlay.addWidget(_lbl("読み:", bold=True)); rlay.addWidget(self.lbl_yomi)
        rlay.addWidget(_lbl("備考:", bold=True)); rlay.addWidget(self.lbl_note)

        splitter=QSplitter(Qt.Horizontal)
        splitter.addWidget(left); splitter.addWidget(right)
        splitter.setSizes([560, 320])
        root.addWidget(splitter)

        self._all_data=list(ITAIJI_DATA)
        self._rebuild_grid()

    def _rebuild_grid(self):
        self._populate(self._all_data)

    def _filter(self, text):
        t=text.strip().lower()
        if not t: self._populate(self._all_data); return
        filtered=[row for row in self._all_data if
                  t in row[0] or t in row[1] or t in row[2] or t in row[3].lower()]
        self._populate(filtered)

    def _populate(self, data):
        # グリッドをクリア
        while self._grid.count():
            w=self._grid.takeAt(0).widget()
            if w: w.deleteLater()

        family=self.font_combo.currentFamily()
        headers=["新字","旧字/異体字","読み","備考"]
        for col,h in enumerate(headers):
            lbl=_lbl(h, bold=True); lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("padding:2px 6px; border-bottom:1px solid #aaa;")
            self._grid.addWidget(lbl, 0, col)

        for row_i,(shin,kyu,yomi,note) in enumerate(data, start=1):
            for col,(ch,is_char) in enumerate([(shin,True),(kyu,True),(yomi,False),(note,False)]):
                if is_char:
                    btn=QPushButton(ch)
                    btn.setFont(QFont(family, 18))
                    btn.setFixedSize(52, 52)
                    btn.setToolTip(f"U+{ord(ch):04X}  {unicodedata.name(ch, '')}")
                    btn.setStyleSheet("QPushButton{border:1px solid #aaa;border-radius:3px;}")
                    # クロージャで値をキャプチャ
                    def _handler(checked=False, s=shin, k=kyu, y=yomi, n=note):
                        self._show_detail(s,k,y,n)
                    btn.clicked.connect(_handler)
                    self._grid.addWidget(btn, row_i, col)
                else:
                    lbl=QLabel(ch); lbl.setAlignment(Qt.AlignCenter)
                    lbl.setStyleSheet("padding:2px 4px;")
                    self._grid.addWidget(lbl, row_i, col)

    def _show_detail(self, shin, kyu, yomi, note):
        family=self.font_combo.currentFamily()
        for canvas, char, lbl_cp, lbl_name in [
            (self.canvas_new, shin, self.lbl_new_cp, self.lbl_new_name),
            (self.canvas_old, kyu,  self.lbl_old_cp, self.lbl_old_name),
        ]:
            canvas.setText(char); canvas.setDisplayFont(family, 160)
            cp, nm = _char_info(char)
            lbl_cp.setText(cp); lbl_name.setText(nm)
        self.lbl_yomi.setText(yomi); self.lbl_note.setText(note)

    def set_dark(self, d):
        self._dark=d
        self.canvas_new.setDark(d); self.canvas_old.setDark(d)

# ════════════════════════════════════════════════════════════
# 詳細表示パネル（フローティングウィンドウ内で使う）
# ════════════════════════════════════════════════════════════

class CharDetailPanel(QWidget):
    """
    クリックされた文字をここに大きく表示し、
    コードポイント・Unicode名・コピーボタンを提供する。
    """
    def __init__(self, families, dark, parent=None):
        super().__init__(parent)
        self._families=families; self._dark=dark
        self._build()

    def _build(self):
        root=QVBoxLayout(self); root.setSpacing(6); root.setContentsMargins(8,8,8,8)

        self.font_combo=FontCombo(self._families)
        self.font_combo.setMaximumWidth(260)
        self.font_combo.changed.connect(self._refresh)
        root.addWidget(self.font_combo)

        self.canvas=CharCanvas(draggable=True); self.canvas.setDark(self._dark)
        self.canvas.setMinimumHeight(200)
        root.addWidget(self.canvas, stretch=1)

        self.lbl_char=QLabel("-"); self.lbl_char.setAlignment(Qt.AlignCenter)
        self.lbl_char.setStyleSheet("font-size:20pt;")
        self.lbl_cp  =QLabel("-"); self.lbl_cp.setAlignment(Qt.AlignCenter)
        self.lbl_name=QLabel("-"); self.lbl_name.setAlignment(Qt.AlignCenter)
        self.lbl_name.setWordWrap(True)
        root.addWidget(self.lbl_char)
        root.addWidget(self.lbl_cp)
        root.addWidget(self.lbl_name)

        btn_row=QHBoxLayout()
        btn_row.addWidget(_lbl("コピー:", bold=True))
        btn_row.addWidget(_copy_btn(lambda: self.canvas.currentText()))
        btn_row.addWidget(_copy_btn(lambda: self.lbl_cp.text()))
        btn_row.addWidget(_copy_btn(lambda: self.lbl_name.text()))
        btn_row.addStretch()
        root.addLayout(btn_row)

        self._char=""

    def show_char(self, char: str):
        self._char=char
        self._refresh()

    def _refresh(self):
        if not self._char: return
        family=self.font_combo.currentFamily()
        self.canvas.setText(self._char)
        self.canvas.setDisplayFont(family, 200)
        cp,name=_char_info(self._char)
        self.lbl_char.setText(self._char)
        self.lbl_cp.setText(cp)
        self.lbl_name.setText(name)

    def set_dark(self, d): self._dark=d; self.canvas.setDark(d)

# ════════════════════════════════════════════════════════════
# フローティングウィンドウ基底
# ════════════════════════════════════════════════════════════

class FloatWindow(QWidget):
    def __init__(self, title, families, dark, parent=None):
        super().__init__(parent, Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setWindowTitle(title)
        self._families=families; self._dark=dark
        self.resize(820, 580)

    def _make_detail_panel(self):
        self._detail=CharDetailPanel(self._families, self._dark)
        return self._detail

    def _make_scroll_grid(self, items):
        container=QWidget()
        grid=QGridLayout(container); grid.setSpacing(3)
        cols=16
        for i,(ch,tip) in enumerate(items):
            btn=QPushButton(ch)
            btn.setFixedSize(42,42)
            btn.setToolTip(tip)   # "U+XXXX\n名前" の形式
            btn.setStyleSheet(
                "QPushButton{border:1px solid #888;border-radius:3px;"
                "font-size:17pt;background:#fff;color:#222;}"
                "QPushButton:hover{background:#e8f0ff;}"
            )
            def _h(checked=False, c=ch): self._detail.show_char(c)
            btn.clicked.connect(_h)
            grid.addWidget(btn, i//cols, i%cols)
        scroll=QScrollArea(); scroll.setWidget(container); scroll.setWidgetResizable(True)
        return scroll

    def set_dark(self, d):
        self._dark=d
        if hasattr(self,"_detail"): self._detail.set_dark(d)

# ════════════════════════════════════════════════════════════
# 絵文字フローティング
# ════════════════════════════════════════════════════════════

_EMOJI_RANGES=[(0x1F600,0x1F64F),(0x1F300,0x1F5FF),(0x1F680,0x1F6FF),
               (0x1F900,0x1F9FF),(0x2600,0x26FF),(0x2700,0x27BF)]

def _build_emoji_list():
    items=[]
    for s,e in _EMOJI_RANGES:
        for cp in range(s,e+1):
            try:
                ch=chr(cp); name=unicodedata.name(ch,"")
                items.append((ch, f"U+{cp:04X}\n{name}" if name else f"U+{cp:04X}"))
            except: pass
    return items

class EmojiWindow(FloatWindow):
    def __init__(self, families, dark, parent=None):
        super().__init__("絵文字一覧（クリックで詳細表示）", families, dark, parent)
        items=_build_emoji_list()
        root=QHBoxLayout(self)
        sp=QSplitter(Qt.Horizontal)
        left=QWidget(); ll=QVBoxLayout(left)
        ll.addWidget(_lbl(f"  {len(items)} 文字  ／  クリックで詳細表示・コピー"))
        ll.addWidget(self._make_scroll_grid(items))
        sp.addWidget(left); sp.addWidget(self._make_detail_panel())
        sp.setSizes([520,280]); root.addWidget(sp)

# ════════════════════════════════════════════════════════════
# 難漢字フローティング
# ════════════════════════════════════════════════════════════

_NOTABLE_KANJI=["鬱","薔","薇","麒","麟","鸞","驫","龘","靐","飝","齉","爨","癰","髑","髏",
                "魑","魅","魍","魎","纜","讒","讖","讙","讛","讜","讞","髙","﨑","濵","德","諸","朗"]
_KANJI_RANGES=[(0x3400,0x3400+299),(0x20000,0x20000+299),(0x2A700,0x2A700+199),
               (0x2B740,0x2B740+199),(0x2B820,0x2B820+199)]

def _build_kanji_list():
    items=[]; seen=set()
    for ch in _NOTABLE_KANJI:
        cp=ord(ch); name=unicodedata.name(ch,f"U+{cp:04X}")
        items.append((ch,f"U+{cp:04X}\n{name}")); seen.add(cp)
    for s,e in _KANJI_RANGES:
        for cp in range(s,e+1):
            if cp in seen: continue
            try:
                ch=chr(cp); name=unicodedata.name(ch,f"U+{cp:04X}")
                items.append((ch,f"U+{cp:04X}\n{name}")); seen.add(cp)
            except: pass
    return items

class KanjiWindow(FloatWindow):
    def __init__(self, families, dark, parent=None):
        super().__init__("難漢字・異体字一覧（クリックで詳細表示）", families, dark, parent)
        items=_build_kanji_list()
        root=QHBoxLayout(self)
        sp=QSplitter(Qt.Horizontal)
        left=QWidget(); ll=QVBoxLayout(left)
        ll.addWidget(_lbl(f"  {len(items)} 文字  ／  クリックで詳細表示・コピー"))
        ll.addWidget(self._make_scroll_grid(items))
        sp.addWidget(left); sp.addWidget(self._make_detail_panel())
        sp.setSizes([520,280]); root.addWidget(sp)

# ════════════════════════════════════════════════════════════
# メインウィンドウ
# ════════════════════════════════════════════════════════════

class LargeCharViewer(QWidget):
    def __init__(self):
        super().__init__()
        self._dark=False; self._borderless=False
        self._emoji_win=None; self._kanji_win=None
        self.setWindowTitle("Unicode Large Character Viewer")
        self.resize(WINDOW_W, WINDOW_H)
        self._build(); self._shortcuts(); self._style()

    def _build(self):
        root=QVBoxLayout(self); root.setContentsMargins(6,6,6,6); root.setSpacing(4)
        root.addLayout(self._toolbar())
        families=sorted(set(QFontDatabase.families()))
        dark=self._dark
        self.tab_main    =MainTab(families, dark)
        self.tab_multi   =MultiTab(families, dark)
        self.tab_compare =CompareTab(families, dark)
        self.tab_font    =FontCompareTab(families, dark)
        self.tab_itaiji  =ItaijiTab(families, dark)
        self.tab_main.edit_char.textChanged.connect(
            lambda: self.tab_font.set_char(self.tab_main.current_char))
        self.tabs=QTabWidget()
        self.tabs.addTab(self.tab_main,    "巨大表示")
        self.tabs.addTab(self.tab_multi,   "複数文字")
        self.tabs.addTab(self.tab_compare, "異体字比較")
        self.tabs.addTab(self.tab_font,    "フォント比較")
        self.tabs.addTab(self.tab_itaiji,  "簡易新字旧字表")
        root.addWidget(self.tabs, stretch=1)

    def _toolbar(self):
        bar=QHBoxLayout(); bar.setSpacing(6)
        self.btn_dark=QPushButton("ダークモード")
        self.btn_dark.setCheckable(True); self.btn_dark.setChecked(False)
        self.btn_dark.clicked.connect(self._toggle_dark)
        self.btn_full=QPushButton("⛶ フルスクリーン")
        self.btn_full.setCheckable(True); self.btn_full.setToolTip("F11")
        self.btn_full.clicked.connect(self._toggle_full)
        self.btn_border=QPushButton("□ 枠なし")
        self.btn_border.setCheckable(True); self.btn_border.setToolTip("F10")
        self.btn_border.clicked.connect(self._toggle_border)
        sep=QFrame(); sep.setFrameShape(QFrame.VLine); sep.setFrameShadow(QFrame.Sunken); sep.setFixedWidth(12)
        self.btn_emoji=QPushButton("絵文字一覧")
        self.btn_emoji.setToolTip("絵文字フローティングウィンドウ（クリックで詳細）")
        self.btn_emoji.clicked.connect(self._show_emoji)
        self.btn_kanji=QPushButton("簡易難漢字一覧")
        self.btn_kanji.setToolTip("難漢字フローティングウィンドウ（クリックで詳細）")
        self.btn_kanji.clicked.connect(self._show_kanji)
        for w in (self.btn_dark,self.btn_full,self.btn_border,sep,self.btn_emoji,self.btn_kanji):
            bar.addWidget(w)
        bar.addStretch(); return bar

    def _shortcuts(self):
        for key,slot in [("F11",self._toggle_full),("F10",self._toggle_border)]:
            a=QAction(self); a.setShortcut(QKeySequence(key)); a.triggered.connect(slot); self.addAction(a)

    def _style(self):
        QApplication.instance().setStyleSheet(DARK_STYLE if self._dark else LIGHT_STYLE)
        for t in (self.tab_main,self.tab_multi):
            t.set_dark(self._dark)
        for t in (self.tab_compare,self.tab_font,self.tab_itaiji):
            t.set_dark(self._dark)
        if self._emoji_win: self._emoji_win.set_dark(self._dark)
        if self._kanji_win: self._kanji_win.set_dark(self._dark)

    def _toggle_dark(self):
        self._dark=not self._dark
        self.btn_dark.setChecked(self._dark)
        self.btn_dark.setText("ダークモード" if self._dark else "ライトモード")
        self._style()

    def _toggle_full(self):
        if self.isFullScreen(): self.showNormal(); self.btn_full.setChecked(False)
        else: self.showFullScreen(); self.btn_full.setChecked(True)

    def _toggle_border(self):
        self._borderless=not self._borderless; self.btn_border.setChecked(self._borderless)
        flags=Qt.Window|(Qt.FramelessWindowHint if self._borderless else Qt.Widget)
        geo=self.geometry(); self.setWindowFlags(flags); self.setGeometry(geo); self.show()

    def _show_emoji(self):
        if self._emoji_win is None:
            families=sorted(set(QFontDatabase.families()))
            self._emoji_win=EmojiWindow(families, self._dark, self)
        self._emoji_win.show(); self._emoji_win.raise_()

    def _show_kanji(self):
        if self._kanji_win is None:
            families=sorted(set(QFontDatabase.families()))
            self._kanji_win=KanjiWindow(families, self._dark, self)
        self._kanji_win.show(); self._kanji_win.raise_()

# ════════════════════════════════════════════════════════════
# エントリポイント
# ════════════════════════════════════════════════════════════

def main():
    app=QApplication(sys.argv)
    app.setApplicationName("Unicode Large Character Viewer")
    win=LargeCharViewer(); win.show()
    sys.exit(app.exec())

if __name__=="__main__":
    main()
