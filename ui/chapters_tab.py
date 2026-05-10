# ui/chapters_tab.py
# -*- coding: utf-8 -*-
import os
import customtkinter as ctk
from tkinter import messagebox, filedialog
from ui.context_menu import TextWidgetContextMenu
from utils import read_file, save_string_to_txt, clear_file_content, get_word_count

def build_chapters_tab(self):
    self.chapters_view_tab = self.tabview.add("Chapters Manage")
    self.chapters_view_tab.rowconfigure(0, weight=0)
    self.chapters_view_tab.rowconfigure(1, weight=1)
    self.chapters_view_tab.columnconfigure(0, weight=1)

    top_frame = ctk.CTkFrame(self.chapters_view_tab)
    top_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
    top_frame.columnconfigure(0, weight=0)
    top_frame.columnconfigure(1, weight=0)
    top_frame.columnconfigure(2, weight=0)
    top_frame.columnconfigure(3, weight=0)
    top_frame.columnconfigure(4, weight=1)

    prev_btn = ctk.CTkButton(top_frame, text="<< 上一章", command=self.prev_chapter, font=("Microsoft YaHei", 12))
    prev_btn.grid(row=0, column=0, padx=5, pady=5, sticky="w")

    next_btn = ctk.CTkButton(top_frame, text="下一章 >>", command=self.next_chapter, font=("Microsoft YaHei", 12))
    next_btn.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    self.chapter_select_var = ctk.StringVar(value="")
    self.chapter_select_menu = ctk.CTkOptionMenu(top_frame, values=[], variable=self.chapter_select_var, command=self.on_chapter_selected, font=("Microsoft YaHei", 12))
    self.chapter_select_menu.grid(row=0, column=2, padx=5, pady=5, sticky="w")

    save_btn = ctk.CTkButton(top_frame, text="保存修改", command=self.save_current_chapter, font=("Microsoft YaHei", 12))
    save_btn.grid(row=0, column=3, padx=5, pady=5, sticky="w")

    refresh_btn = ctk.CTkButton(top_frame, text="刷新章节列表", command=self.refresh_chapters_list, font=("Microsoft YaHei", 12))
    refresh_btn.grid(row=0, column=5, padx=5, pady=5, sticky="e")

    export_btn = ctk.CTkButton(top_frame, text="导出小说", command=lambda: export_novel_dialog(self), font=("Microsoft YaHei", 12))
    export_btn.grid(row=0, column=6, padx=5, pady=5, sticky="e")

    self.chapters_word_count_label = ctk.CTkLabel(top_frame, text="字数：0", font=("Microsoft YaHei", 12))
    self.chapters_word_count_label.grid(row=0, column=4, padx=(0,10), sticky="e")

    self.chapter_view_text = ctk.CTkTextbox(self.chapters_view_tab, wrap="word", font=("Microsoft YaHei", 12))
    
    def update_word_count(event=None):
        text = self.chapter_view_text.get("0.0", "end-1c")
        text_length = get_word_count(text)
        self.chapters_word_count_label.configure(text=f"字数：{text_length}")
    
    self.chapter_view_text.bind("<KeyRelease>", update_word_count)
    self.chapter_view_text.bind("<ButtonRelease>", update_word_count)
    TextWidgetContextMenu(self.chapter_view_text)
    self.chapter_view_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=5, columnspan=6)

    self.chapters_list = []
    refresh_chapters_list(self)

def refresh_chapters_list(self):
    filepath = self.filepath_var.get().strip()
    chapters_dir = os.path.join(filepath, "chapters")
    if not os.path.exists(chapters_dir):
        self.safe_log("尚未找到 chapters 文件夹，请先生成章节或检查保存路径。")
        self.chapter_select_menu.configure(values=[])
        return

    all_files = os.listdir(chapters_dir)
    chapter_nums = []
    for f in all_files:
        if f.startswith("chapter_") and f.endswith(".txt"):
            number_part = f.replace("chapter_", "").replace(".txt", "")
            if number_part.isdigit():
                chapter_nums.append(number_part)
    chapter_nums.sort(key=lambda x: int(x))
    self.chapters_list = chapter_nums
    self.chapter_select_menu.configure(values=self.chapters_list)
    current_selected = self.chapter_select_var.get()
    if current_selected not in self.chapters_list:
        if self.chapters_list:
            self.chapter_select_var.set(self.chapters_list[0])
            load_chapter_content(self, self.chapters_list[0])
        else:
            self.chapter_select_var.set("")
            self.chapter_view_text.delete("0.0", "end")

def on_chapter_selected(self, value):
    load_chapter_content(self, value)

def load_chapter_content(self, chapter_number_str):
    if not chapter_number_str:
        return
    filepath = self.filepath_var.get().strip()
    chapter_file = os.path.join(filepath, "chapters", f"chapter_{chapter_number_str}.txt")
    if not os.path.exists(chapter_file):
        self.safe_log(f"章节文件 {chapter_file} 不存在！")
        return
    content = read_file(chapter_file)
    self.chapter_view_text.delete("0.0", "end")
    self.chapter_view_text.insert("0.0", content)

def save_current_chapter(self):
    chapter_number_str = self.chapter_select_var.get()
    if not chapter_number_str:
        messagebox.showwarning("警告", "尚未选择章节，无法保存。")
        return
    filepath = self.filepath_var.get().strip()
    if not filepath:
        messagebox.showwarning("警告", "请先配置保存文件路径")
        return
    chapter_file = os.path.join(filepath, "chapters", f"chapter_{chapter_number_str}.txt")
    content = self.chapter_view_text.get("0.0", "end").strip()
    clear_file_content(chapter_file)
    save_string_to_txt(content, chapter_file)
    self.safe_log(f"已保存对第 {chapter_number_str} 章的修改。")

def prev_chapter(self):
    if not self.chapters_list:
        return
    current = self.chapter_select_var.get()
    if current not in self.chapters_list:
        return
    idx = self.chapters_list.index(current)
    if idx > 0:
        new_idx = idx - 1
        self.chapter_select_var.set(self.chapters_list[new_idx])
        load_chapter_content(self, self.chapters_list[new_idx])
    else:
        messagebox.showinfo("提示", "已经是第一章了。")

def next_chapter(self):
    if not self.chapters_list:
        return
    current = self.chapter_select_var.get()
    if current not in self.chapters_list:
        return
    idx = self.chapters_list.index(current)
    if idx < len(self.chapters_list) - 1:
        new_idx = idx + 1
        self.chapter_select_var.set(self.chapters_list[new_idx])
        load_chapter_content(self, self.chapters_list[new_idx])
    else:
        messagebox.showinfo("提示", "已经是最后一章了。")


def export_novel_dialog(self):
    filepath = self.filepath_var.get().strip()
    if not filepath:
        messagebox.showwarning("警告", "请先配置保存文件路径")
        return

    dialog = ctk.CTkToplevel(self.master)
    dialog.title("导出小说")
    dialog.geometry("400x220")
    dialog.resizable(False, False)
    dialog.transient(self.master)
    dialog.grab_set()

    dialog.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(dialog, text="小说标题:", font=("Microsoft YaHei", 12)).grid(row=0, column=0, padx=10, pady=8, sticky="w")
    title_entry = ctk.CTkEntry(dialog, font=("Microsoft YaHei", 12))
    title_entry.grid(row=0, column=1, padx=10, pady=8, sticky="ew")

    ctk.CTkLabel(dialog, text="作者:", font=("Microsoft YaHei", 12)).grid(row=1, column=0, padx=10, pady=8, sticky="w")
    author_entry = ctk.CTkEntry(dialog, font=("Microsoft YaHei", 12))
    author_entry.grid(row=1, column=1, padx=10, pady=8, sticky="ew")

    ctk.CTkLabel(dialog, text="导出格式:", font=("Microsoft YaHei", 12)).grid(row=2, column=0, padx=10, pady=8, sticky="w")
    format_var = ctk.StringVar(value="TXT")
    format_menu = ctk.CTkOptionMenu(dialog, values=["TXT", "EPUB"], variable=format_var, font=("Microsoft YaHei", 12))
    format_menu.grid(row=2, column=1, padx=10, pady=8, sticky="w")

    def do_export():
        title = title_entry.get().strip()
        author = author_entry.get().strip()
        fmt = format_var.get()

        if fmt == "TXT":
            output_path = filedialog.asksaveasfilename(
                title="保存TXT文件",
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt")],
                initialfile=f"{title or 'novel'}.txt"
            )
        else:
            output_path = filedialog.asksaveasfilename(
                title="保存EPUB文件",
                defaultextension=".epub",
                filetypes=[("EPUB Files", "*.epub")],
                initialfile=f"{title or 'novel'}.epub"
            )

        if not output_path:
            return

        try:
            from novel_exporter import export_to_txt, export_to_epub
            if fmt == "TXT":
                export_to_txt(filepath, output_path, title=title)
            else:
                export_to_epub(filepath, output_path, title=title, author=author)
            dialog.destroy()
            messagebox.showinfo("导出成功", f"小说已导出到:\n{output_path}")
            self.safe_log(f"✅ 小说导出成功: {output_path}")
        except ImportError as e:
            messagebox.showerror("缺少依赖", str(e))
        except Exception as e:
            messagebox.showerror("导出失败", f"导出时出错: {str(e)}")

    btn_frame = ctk.CTkFrame(dialog)
    btn_frame.grid(row=3, column=0, columnspan=2, pady=15)
    ctk.CTkButton(btn_frame, text="导出", command=do_export, font=("Microsoft YaHei", 12)).pack(side="left", padx=10)
    ctk.CTkButton(btn_frame, text="取消", command=dialog.destroy, font=("Microsoft YaHei", 12)).pack(side="left", padx=10)
