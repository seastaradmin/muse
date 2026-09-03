#!/usr/bin/env python3
"""从维基百科（中文优先，缺失/太薄回退英文）批量拉取审美信源，产出三类文件到 data/_raw/<layer>/：

  1. 纯文本   <标题>.md          干净正文纯文本
  2. 正文 HTML <标题>.html        渲染好的文章正文（浏览器打开即读，含在线图片）
  3. 整页 HTML <标题>.full.html   整页原始 HTML（备份）

仅用 Python 标准库（urllib/json），无第三方依赖。
用法：
    python3 scripts/fetch_wikipedia.py --layer ui
    python3 scripts/fetch_wikipedia.py --layer foundation --dry-run
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

UA = "MuseDataFetcher/0.1 (aesthetics principles seed)"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 脚本只写"原料"到 _raw 暂存区，绝不触碰各层成品目录
OUT_ROOT = os.path.join(SCRIPT_DIR, "..", "data", "_raw")
# 中文条目正文短于此值视为"小作品"，回退英文
MIN_EXTRACT_CHARS = 800

# (cat, 中文标题, 英文标题) —— 中文优先，缺失/太薄回退英文
TOPICS_BY_LAYER = {
    "principles": [
        ("color", "色彩理论", "Color theory"),
        ("color", "配色", "Color scheme"),
        ("color", "色彩和谐", "Color harmony"),
        ("composition", "三分法", "Rule of thirds"),
        ("composition", "黄金比例", "Golden ratio"),
        ("composition", "构图", "Composition (visual arts)"),
        ("typography", "排版", "Typography"),
        ("typography", "网格", "Grid (graphic design)"),
        ("space", "留白", "Negative space"),
        ("space", "视觉层次", "Visual hierarchy"),
    ],
    "ui": [
        ("system", "设计系统", "Design system"),
        ("layout", "响应式网页设计", "Responsive web design"),
        ("system", "用户界面设计", "User interface design"),
        ("system", "用户界面", "User interface"),
        ("accessibility", "网页无障碍", "Web accessibility"),
        ("typography", "Web字体排印", "Web typography"),
        ("layout", "栅格", "Grid (graphic design)"),
        ("system", "视觉传达设计", "Communication design"),
        ("style", "极简主义", "Minimalism"),
    ],
    "foundation": [
        ("theory", "美学", "Aesthetics"),
        ("theory", "美学史", "History of aesthetics"),
        ("theory", "艺术史", "History of art"),
        ("art", "印象派", "Impressionism"),
        ("art", "现代主义", "Modernism"),
        ("art", "极简主义", "Minimalism"),
    ],
}


def http_get(url):
    """GET 一个 URL 返回字节；带 429 退避重试。出错抛异常。"""
    for attempt in range(4):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                print(f"      (429 限流，{2 ** (attempt + 1)}s 后重试…)")
                time.sleep(2 ** (attempt + 1))
                continue
            raise
        except urllib.error.URLError as e:
            raise RuntimeError(f"网络错误: {e}") from e
    raise RuntimeError("重试次数用尽")


def api_get(params, lang):
    """调用 MediaWiki API，返回 JSON dict。"""
    params.setdefault("format", "json")
    params.setdefault("formatversion", "2")
    url = f"https://{lang}.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params)
    return json.loads(http_get(url).decode("utf-8"))


def fetch_extract(page, lang):
    """返回 (解析后的真实标题, 全文纯文本)；页面缺失返回 (None, None)。"""
    data = api_get({"action": "query", "prop": "extracts", "explaintext": 1,
                    "redirects": 1, "titles": page}, lang)
    for pg in data.get("query", {}).get("pages", []):
        if pg.get("missing"):
            return None, None
        extract = pg.get("extract", "").strip()
        if extract:
            return pg.get("title", page), extract
    return None, None


def search_title(query, lang):
    """按关键词搜一个最佳匹配标题（处理繁体/别名差异），找不到返回 None。"""
    data = api_get({"action": "query", "list": "search", "srsearch": query, "srlimit": 1}, lang)
    for hit in data.get("query", {}).get("search", []):
        return hit.get("title")
    return None


def resolve(page_zh, page_en):
    """解析目标页面：中文优先（缺失时搜索别名），太薄回退英文。
    返回 (lang, content_title, extract)。"""
    lang, content_title, extract = "zh", page_zh, None
    title, extract = fetch_extract(page_zh, "zh")
    if title is not None:
        content_title = title
    else:
        alt = search_title(page_zh, "zh")  # 中文精确缺失 → 搜索别名
        if alt:
            content_title, extract = fetch_extract(alt, "zh")
    # 中文缺失或太薄 → 回退英文
    if extract is None or len(extract) < MIN_EXTRACT_CHARS:
        en_title, en_extract = fetch_extract(page_en, "en")
        if en_extract and (extract is None or len(en_extract) > len(extract) * 1.5):
            return "en", en_title, en_extract
    return lang, content_title, extract


def fetch_body_html(page, lang):
    """返回渲染后的文章正文 HTML（无站点导航，图片用在线原图 URL）；页面不存在返回 None。"""
    data = api_get({"action": "parse", "prop": "text", "redirects": 1, "page": page}, lang)
    if "error" in data:
        return None
    return data.get("parse", {}).get("text", "")


def wrap_html(body, lang, title):
    """把文章片段包成可独立打开的完整 HTML：加编码、引用维基正文样式、图片地址补全为 https。"""
    css = (f"https://{lang}.wikipedia.org/w/load.php"
           "?modules=mediawiki.skinning.content&only=styles&skin=vector")
    # 协议相对地址（//upload…）在本地文件打开时无法解析，补全为 https://
    body = body.replace('srcset="//', 'srcset="https://').replace('src="//', 'src="https://')
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Muse 知识库信源</title>
<link rel="stylesheet" href="{css}">
</head>
<body class="mw-body">
<div id="content" class="mw-body-content" style="max-width:62em;margin:0 auto;padding:1.2em 1.6em;">
{body}
</div>
</body>
</html>
"""


def fetch_full_html(page, lang):
    """返回整页原始 HTML（含站点导航）作为备份。"""
    url = f"https://{lang}.wikipedia.org/wiki/" + urllib.parse.quote(page)
    return http_get(url).decode("utf-8", "replace")


def build_markdown(cat, title, extract, lang, content_title):
    url = urllib.parse.quote(content_title)
    return f"""---
title: {title}
category: {cat}
domain: 通用
related: []
source: Wikipedia（{lang} 拉取，待清洗） (https://{lang}.wikipedia.org/wiki/{url})
---

# 原文（全文，待清洗）

{extract}

# 核心要点（待清洗整理）

# 适用范围

# 常见误区

# 来源

- https://{lang}.wikipedia.org/wiki/{url}
"""


def main():
    parser = argparse.ArgumentParser(description="从维基百科拉取审美信源")
    parser.add_argument("--layer", choices=list(TOPICS_BY_LAYER), default="principles",
                        help="拉取哪一层")
    parser.add_argument("--dry-run", action="store_true", help="只打印将写入的文件，不写盘")
    parser.add_argument("--skip-html", action="store_true",
                        help="只写纯文本 .md，不抓 HTML")
    parser.add_argument("--force", action="store_true",
                        help="覆盖所有已存在文件（默认只更新仍标'待清洗'的 .md；HTML 始终覆盖）")
    args = parser.parse_args()

    out_root = os.path.join(OUT_ROOT, args.layer)
    for cat, zh, en in TOPICS_BY_LAYER[args.layer]:
        dirpath = os.path.join(out_root, cat)
        os.makedirs(dirpath, exist_ok=True)
        md_path = os.path.join(dirpath, f"{zh}.md")
        html_path = os.path.join(dirpath, f"{zh}.html")
        full_path = os.path.join(dirpath, f"{zh}.full.html")

        if args.dry_run:
            kinds = [f"{zh}.md"]
            if not args.skip_html:
                kinds += [f"{zh}.html", f"{zh}.full.html"]
            print(f"[dry-run] {args.layer}/{cat}/" + ", ".join(kinds))
            continue

        # 保护已清洗/精编的 .md：默认不覆盖
        if not args.force and os.path.exists(md_path):
            existing = open(md_path, encoding="utf-8").read()
            if "待清洗" not in existing:
                print(f"[keep]  已清洗/精编，跳过文本: {cat}/{zh}（用 --force 强制覆盖）")

        # 解析目标页面（中文优先 + 搜索别名 + 小作品回退英文）
        try:
            lang, content_title, extract = resolve(zh, en)
        except Exception as e:
            print(f"[error] {cat}/{zh}: {e}")
            continue

        if extract is None:
            print(f"[skip] 未找到: {cat}/{zh}")
            continue

        # 1) 纯文本
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(build_markdown(cat, zh, extract, lang, content_title))
        print(f"[ok]   {lang} {cat}/{zh}.md")

        # 2) 正文 HTML + 3) 整页 HTML
        if not args.skip_html:
            try:
                body = fetch_body_html(content_title, lang)
                if body is not None:
                    with open(html_path, "w", encoding="utf-8") as f:
                        f.write(wrap_html(body, lang, zh))
                    print(f"[ok]   {lang} {cat}/{zh}.html（正文）")
                full = fetch_full_html(content_title, lang)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(full)
                print(f"[ok]   {lang} {cat}/{zh}.full.html（整页）")
            except Exception as e:
                print(f"[error] {cat}/{zh} HTML: {e}")
            time.sleep(1)  # 礼貌限速，避免 429

    if args.dry_run:
        print("dry-run 完成（未写盘）")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
