#!/usr/bin/env python3
"""从斯坦福哲学百科（SEP）拉取美学理论条目。

SEP 无公开 JSON API，直接抓条目 HTML：存整页 HTML 到 data/_raw/foundation/theory/，
并提取纯文本存同名 .md。

仅用 Python 标准库。用法：
    python3 scripts/fetch_sep.py
"""

import argparse
import html as html_mod
import os
import re
import sys
import time
import urllib.request
from html.parser import HTMLParser

UA = "MuseDataFetcher/0.1 (aesthetics principles seed)"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SCRIPT_DIR, "..", "data", "_raw", "foundation", "theory")

# (entry_id, 中文标签) —— entry_id 对应 plato.stanford.edu/entries/<id>/
ENTRIES = [
    ("beauty", "美"),
    ("aesthetic-judgment", "审美判断"),
    ("aesthetic-concept", "审美的概念"),
    ("kant-aesthetics", "康德美学"),
    ("hume-aesthetics", "休谟美学"),
    ("plato-aesthetics", "柏拉图美学"),
    ("hegel-aesthetics", "黑格尔美学"),
]


class _TextExtract(HTMLParser):
    """提取 SEP 正文纯文本（去 script/style/导航菜单，正文从首个标题开始）。"""

    _skip_tags = {"script", "style", "head", "nav", "header", "footer"}
    _skip_depth = 0
    _in_title = False
    _started = False  # 从首个 h1/h2 才开始记录正文，去掉页头菜单噪音

    def __init__(self):
        super().__init__()
        self.parts = []
        self.title = None

    def handle_starttag(self, tag, attrs):
        if tag in self._skip_tags:
            self._skip_depth += 1
        if tag == "title":
            self._in_title = True
        if tag in ("h1", "h2") and not self._started:
            self._started = True
        if self._started and tag in ("p", "h1", "h2", "h3", "h4", "li", "div"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self._skip_tags and self._skip_depth:
            self._skip_depth -= 1
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._skip_depth or not self._started:
            return
        if self._in_title:
            self.title = (self.title or "") + data
            return
        self.parts.append(data)

    def text(self):
        s = "".join(self.parts)
        s = re.sub(r"[ \t]+", " ", s)
        s = re.sub(r"\n\s*\n+", "\n\n", s)
        return s.strip()


def fetch_entry(entry_id):
    url = f"https://plato.stanford.edu/entries/{entry_id}/"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def main():
    parser = argparse.ArgumentParser(description="抓斯坦福哲学百科美学条目")
    parser.add_argument("--dry-run", action="store_true", help="只打印将写入的文件，不写盘")
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    for entry_id, label in ENTRIES:
        html_path = os.path.join(OUT_DIR, f"{label}.html")
        md_path = os.path.join(OUT_DIR, f"{label}.md")
        if args.dry_run:
            print(f"[dry-run] foundation/theory/{label}.html + {label}.md  ({entry_id})")
            continue
        try:
            raw = fetch_entry(entry_id)
        except Exception as e:
            print(f"[error] {entry_id}: {e}")
            continue
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(raw)
        parser = _TextExtract()
        try:
            parser.feed(raw)
        except Exception:
            pass
        text = parser.text()
        title = parser.title or entry_id
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"---\nentry: {entry_id}\n# {label}\nsource: SEP ({title}) (https://plato.stanford.edu/entries/{entry_id}/)\n---\n\n{text}\n")
        print(f"[ok]   foundation/theory/{label}  ({entry_id}, {len(text)} 字符)")
        time.sleep(2)  # SEP 限速较严，礼貌间隔

    if args.dry_run:
        print("dry-run 完成（未写盘）")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
