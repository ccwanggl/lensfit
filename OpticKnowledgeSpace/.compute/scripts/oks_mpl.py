"""
Matplotlib font setup helper for OpticKnowledgeSpace visualizations.

Usage:
    from oks_mpl import setup_fonts
    setup_fonts()

This module tries to find a Chinese-capable font on Windows, macOS and Linux
and configures matplotlib to use it as the default sans-serif font.
"""

import sys
from pathlib import Path

import matplotlib
import matplotlib.font_manager as fm


# Common Chinese-capable fonts across platforms, ordered by preference.
_FONT_CANDIDATES = [
    # Windows
    'Noto Sans SC',
    'Microsoft YaHei',
    'SimHei',
    'SimSun',
    # macOS
    'PingFang SC',
    'Heiti SC',
    'STHeiti',
    'Arial Unicode MS',
    # Linux
    'Noto Sans CJK SC',
    'WenQuanYi Micro Hei',
    'WenQuanYi Zen Hei',
    'Source Han Sans SC',
    'Droid Sans Fallback',
]


def _find_system_font():
    """Return the path to a Chinese-capable system font, or None."""
    # First try matplotlib's font manager by family name.
    available_names = {f.name for f in fm.fontManager.ttflist}
    for name in _FONT_CANDIDATES:
        if name in available_names:
            prop = fm.FontProperties(family=name)
            path = fm.findfont(prop)
            if path and 'DejaVuSans' not in path:
                return path

    # Fallback: probe common Windows font paths.
    if sys.platform == 'win32':
        windows_fonts = Path(r'C:\Windows\Fonts')
        candidates = [
            windows_fonts / 'NotoSansSC-VF.ttf',
            windows_fonts / 'msyh.ttc',
            windows_fonts / 'simhei.ttf',
            windows_fonts / 'simsun.ttc',
        ]
        for path in candidates:
            if path.exists():
                return str(path)

    return None


def setup_fonts(font_size=11):
    """Configure matplotlib to use a Chinese-capable font."""
    path = _find_system_font()
    if path:
        # Register the font file explicitly.
        try:
            fm.fontManager.addfont(path)
        except Exception:
            pass
        prop = fm.FontProperties(fname=path)
        matplotlib.rcParams['font.family'] = prop.get_name()
        matplotlib.rcParams['axes.unicode_minus'] = False
        print(f'Using font: {prop.get_name()} ({path})')
    else:
        print('Warning: no Chinese-capable font found; labels may be missing.')

    matplotlib.rcParams['font.size'] = font_size


if __name__ == '__main__':
    setup_fonts()
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(4, 2))
    ax.set_title('测试中文标题 Test')
    ax.set_xlabel('横轴')
    ax.set_ylabel('纵轴')
    fig.savefig('/tmp/oks_font_test.png', dpi=100)
    print('Saved test figure to /tmp/oks_font_test.png')
