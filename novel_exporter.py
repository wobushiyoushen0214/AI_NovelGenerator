# novel_exporter.py
# -*- coding: utf-8 -*-
import os
import re
import logging


def get_sorted_chapters(filepath: str) -> list:
    chapters_dir = os.path.join(filepath, "chapters")
    if not os.path.exists(chapters_dir):
        return []

    files = []
    for f in os.listdir(chapters_dir):
        if f.startswith("chapter_") and f.endswith(".txt"):
            num_part = f.replace("chapter_", "").replace(".txt", "")
            if num_part.isdigit():
                files.append((int(num_part), f))

    files.sort(key=lambda x: x[0])
    return files


def get_chapter_title_from_blueprint(blueprint_text: str, chapter_num: int) -> str:
    from chapter_directory_parser import get_chapter_info_from_blueprint
    try:
        info = get_chapter_info_from_blueprint(blueprint_text, chapter_num)
        title = info.get("chapter_title", "")
        if title and title != "未命名":
            return title
    except Exception:
        pass
    return ""


def export_to_txt(filepath: str, output_path: str, title: str = "") -> str:
    chapters = get_sorted_chapters(filepath)
    if not chapters:
        raise ValueError("没有找到任何章节文件")

    blueprint_file = os.path.join(filepath, "Novel_directory.txt")
    blueprint_text = ""
    if os.path.exists(blueprint_file):
        with open(blueprint_file, "r", encoding="utf-8") as f:
            blueprint_text = f.read()

    with open(output_path, "w", encoding="utf-8") as out:
        if title:
            out.write(f"{title}\n")
            out.write("=" * len(title.encode('gbk', errors='replace')) + "\n\n")

        for chapter_num, filename in chapters:
            chapter_path = os.path.join(filepath, "chapters", filename)
            with open(chapter_path, "r", encoding="utf-8") as f:
                content = f.read().strip()

            chapter_title = get_chapter_title_from_blueprint(blueprint_text, chapter_num)
            if chapter_title:
                out.write(f"第{chapter_num}章 {chapter_title}\n\n")
            else:
                out.write(f"第{chapter_num}章\n\n")

            out.write(content)
            out.write("\n\n\n")

    return output_path


def export_to_epub(filepath: str, output_path: str, title: str = "", author: str = "") -> str:
    try:
        from ebooklib import epub
    except ImportError:
        raise ImportError("导出EPUB需要安装 ebooklib 库：pip install ebooklib")

    chapters = get_sorted_chapters(filepath)
    if not chapters:
        raise ValueError("没有找到任何章节文件")

    blueprint_file = os.path.join(filepath, "Novel_directory.txt")
    blueprint_text = ""
    if os.path.exists(blueprint_file):
        with open(blueprint_file, "r", encoding="utf-8") as f:
            blueprint_text = f.read()

    book = epub.EpubBook()
    book.set_identifier(f"novel-{hash(title or 'untitled')}")
    book.set_title(title or "AI Generated Novel")
    book.set_language("zh")
    if author:
        book.add_author(author)

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    style = epub.EpubItem(
        uid="style",
        file_name="style/default.css",
        media_type="text/css",
        content=b"body { font-family: serif; line-height: 1.8; } "
                b"h1 { text-align: center; margin: 2em 0 1em; } "
                b"p { text-indent: 2em; margin: 0.5em 0; }"
    )
    book.add_item(style)

    epub_chapters = []
    for chapter_num, filename in chapters:
        chapter_path = os.path.join(filepath, "chapters", filename)
        with open(chapter_path, "r", encoding="utf-8") as f:
            content = f.read().strip()

        chapter_title = get_chapter_title_from_blueprint(blueprint_text, chapter_num)
        display_title = f"第{chapter_num}章 {chapter_title}" if chapter_title else f"第{chapter_num}章"

        paragraphs = content.split("\n")
        html_paragraphs = "".join(
            f"<p>{p.strip()}</p>" for p in paragraphs if p.strip()
        )
        html_content = f"<h1>{display_title}</h1>{html_paragraphs}"

        ch = epub.EpubHtml(
            title=display_title,
            file_name=f"chapter_{chapter_num}.xhtml",
            lang="zh"
        )
        ch.content = html_content.encode("utf-8")
        ch.add_item(style)
        book.add_item(ch)
        epub_chapters.append(ch)

    book.toc = epub_chapters
    book.spine = ["nav"] + epub_chapters

    epub.write_epub(output_path, book)
    return output_path
