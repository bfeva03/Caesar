from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, List, Optional


class ResultsTable(ttk.Frame):
    def __init__(self, parent, on_select: Optional[Callable[[Dict], None]] = None):
        super().__init__(parent)
        self._on_select = on_select
        self._rows: List[Dict] = []

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            self,
            columns=("key", "score", "preview"),
            show="headings",
            selectmode="browse",
        )
        self.tree.grid(row=0, column=0, sticky="nsew")

        self.tree.heading("key", text="Key / Shift")
        self.tree.heading("score", text="Score")
        self.tree.heading("preview", text="Preview")

        self.tree.column("key", width=120, anchor="w", stretch=False)
        self.tree.column("score", width=90, anchor="e", stretch=False)
        self.tree.column("preview", width=520, anchor="w", stretch=True)

        sb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", self._handle_select)
        self.tree.bind("<Double-1>", self._handle_select)

    def set_rows(self, rows: List[Dict]):
        self._rows = rows
        for item in self.tree.get_children():
            self.tree.delete(item)

        for i, r in enumerate(rows):
            preview = r["text"].replace("\n", " ")
            if len(preview) > 80:
                preview = preview[:80].rstrip() + "…"

            key = str(r.get("key", ""))
            score = float(r.get("score", 0.0))

            self.tree.insert(
                "",
                "end",
                iid=str(i),
                values=(key, f"{score:.2f}", preview),
            )

    def get_rows(self) -> List[Dict]:
        return list(self._rows)

    def select_index(self, idx: int):
        iid = str(idx)
        if iid in self.tree.get_children():
            self.tree.selection_set(iid)
            self.tree.see(iid)
            self._emit_selected()

    def get_selected(self) -> Optional[Dict]:
        sel = self.tree.selection()
        if not sel:
            return None
        try:
            idx = int(sel[0])
        except ValueError:
            return None
        if 0 <= idx < len(self._rows):
            return self._rows[idx]
        return None

    def _handle_select(self, _event=None):
        self._emit_selected()

    def _emit_selected(self):
        if not self._on_select:
            return
        row = self.get_selected()
        if row:
            self._on_select(row)


class Toast:
    def __init__(self, root: tk.Tk):
        self.root = root
        self._label = ttk.Label(root, text="", style="Toast.TLabel")
        self._after_id = None
        self._label.place_forget()

    def show(self, msg: str, ms: int = 1800):
        if self._after_id is not None:
            try:
                self.root.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

        self._label.configure(text=msg)
        self._label.place(relx=0.02, rely=0.97, anchor="sw")
        self._after_id = self.root.after(ms, self._hide)

    def _hide(self):
        self._label.place_forget()
        self._after_id = None


class DiffView(ttk.Frame):
    """
    Side-by-side diff view for original vs candidate.
    Highlights differing characters with a blue background (theme-aware).
    """

    def __init__(self, parent, style_text_fn, root):
        super().__init__(parent)
        self._style_text_fn = style_text_fn
        self._root = root

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        hdr = ttk.Frame(self)
        hdr.grid(row=0, column=0, columnspan=2, sticky="ew")
        hdr.columnconfigure(0, weight=1)
        hdr.columnconfigure(1, weight=1)

        ttk.Label(hdr, text="Original", style="Muted.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(hdr, text="Candidate", style="Muted.TLabel").grid(
            row=0, column=1, sticky="w"
        )

        self.left = tk.Text(
            self, wrap="word", height=9, borderwidth=0, highlightthickness=1
        )
        self.right = tk.Text(
            self, wrap="word", height=9, borderwidth=0, highlightthickness=1
        )
        self.left.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        self.right.grid(row=1, column=1, sticky="nsew", padx=(8, 0))

        self._style_text_fn(self.left)
        self._style_text_fn(self.right)

        self.refresh_theme()

        for w in (self.left, self.right):
            w.configure(state="disabled")

    def refresh_theme(self):
        diff_bg = self._root.option_get("caeser.text.selbg", "") or "#1F4B8F"
        diff_fg = self._root.option_get("caeser.text.fg", "") or "#E7F0FF"
        for w in (self.left, self.right):
            w.tag_configure("diff", background=diff_bg, foreground=diff_fg)

    def set_texts(self, original: str, candidate: str, max_chars: int = 6000):
        original = original[:max_chars]
        candidate = candidate[:max_chars]

        for w in (self.left, self.right):
            w.configure(state="normal")
            w.delete("1.0", "end")
            w.tag_remove("diff", "1.0", "end")

        self.left.insert("1.0", original)
        self.right.insert("1.0", candidate)

        # Only highlight differences if the texts are reasonably similar
        # (i.e., not completely different like cipher vs plaintext)
        n = min(len(original), len(candidate))
        diff_count = 0

        # Count differences first
        for i in range(n):
            if original[i] != candidate[i]:
                diff_count += 1

        for i in range(n, len(original)):
            diff_count += 1
        for i in range(n, len(candidate)):
            diff_count += 1

        # Only highlight if less than 60% of text is different
        # This prevents highlighting entire text when comparing cipher vs plaintext
        total_chars = max(len(original), len(candidate))
        if total_chars > 0 and (diff_count / total_chars) < 0.6:
            for i in range(n):
                if original[i] != candidate[i]:
                    self._tag_char(self.left, i)
                    self._tag_char(self.right, i)

            for i in range(n, len(original)):
                self._tag_char(self.left, i)
            for i in range(n, len(candidate)):
                self._tag_char(self.right, i)

        for w in (self.left, self.right):
            w.configure(state="disabled")

    def _tag_char(self, widget: tk.Text, idx: int):
        start = f"1.0 + {idx} chars"
        end = f"1.0 + {idx+1} chars"
        widget.tag_add("diff", start, end)
