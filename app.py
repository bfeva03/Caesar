import tkinter as tk
from tkinter import ttk, filedialog
import sys
import subprocess
import platform

from theme import apply_theme, PALETTES
from cipher import brute_force, caesar_shift
from widgets import ResultsTable, Toast, DiffView
from analysis_panel import AnalysisPanel
from vigenere_detect import summarize as vigenere_summarize
from substitution_helper import SubstitutionHelper, apply_substitution
from config import Config

from utils import clamp_int, copy_to_clipboard
from samples import SAMPLES


def get_system_theme():
    """Detect system theme (light/dark). Returns 'dark' or 'light'."""
    try:
        if platform.system() == "Darwin":  # macOS
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True,
                text=True,
                timeout=1,
            )
            # If the command succeeds, dark mode is enabled
            return "dark" if result.returncode == 0 else "light"
        else:
            # Default to dark for other platforms
            return "dark"
    except Exception:
        return "dark"


# Cipher categories (UI + logic)
CIPHER_CATEGORIES = {
    "Brute force": [
        "Caesar",
        "Affine",
    ],
    "Instant": [
        "Atbash",
        "ROT47",
        "ROT5 (digits)",
        "Reverse",
    ],
    "Transposition": [
        "Rail Fence",
        "Columnar",
    ],
    "Analysis": [
        "Vigenere (detect)",
    ],
    "Manual": [
        "Substitution (manual)",
    ],
    "Meta": [
        "Try All (Fast)",
    ],
}

# Flat list used internally
CIPHERS = [c for group in CIPHER_CATEGORIES.values() for c in group]

# Ciphers that only produce a single result
SINGLE_RESULT_CIPHERS = {
    "Atbash",
    "ROT47",
    "ROT5 (digits)",
    "Reverse",
}


class CaesarApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Caesar — Cipher Breaker")
        self.root.minsize(1040, 760)

        # Load configuration
        self.config = Config()

        # Always use system theme on startup
        initial_theme = get_system_theme()
        self.var_theme = tk.StringVar(value=initial_theme)
        apply_theme(self.root, self.var_theme.get())

        self.toast = Toast(self.root)

        # Load settings from config
        self.var_cipher = tk.StringVar(
            value=self.config.get("last_cipher", "Try All (Fast)")
        )
        self.var_input_mode = tk.StringVar(
            value=self.config.get("input_mode", "ciphertext")
        )
        self.var_keep_case = tk.BooleanVar(value=self.config.get("keep_case", True))
        self.var_keep_punct = tk.BooleanVar(value=self.config.get("keep_punct", True))
        self.var_show_all = tk.BooleanVar(value=self.config.get("show_all", False))
        self.var_top_n = tk.IntVar(value=self.config.get("top_n", 50))
        self.var_shift_direct = tk.StringVar(value="0")
        self.var_auto_select_best = tk.BooleanVar(
            value=self.config.get("auto_select_best", True)
        )
        self.var_light_mode = tk.BooleanVar(value=self.var_theme.get() == "light")

        self._build_ui()
        self._bind_shortcuts()

        # Restore window geometry if available
        geom = self.config.get("window_geometry")
        if geom:
            try:
                self.root.geometry(geom)
            except Exception:
                pass

        self._refresh_results()

        # Save config on close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _open_settings_menu(self):
        """Open a settings dropdown menu."""
        menu = tk.Menu(self.root, tearoff=False)

        # Keep case
        menu.add_checkbutton(
            label="Keep case",
            variable=self.var_keep_case,
            command=lambda: (
                self._refresh_results(),
                self.config.set("keep_case", self.var_keep_case.get()),
            ),
        )

        # Keep punctuation
        menu.add_checkbutton(
            label="Keep punctuation",
            variable=self.var_keep_punct,
            command=lambda: (
                self._refresh_results(),
                self.config.set("keep_punct", self.var_keep_punct.get()),
            ),
        )

        # Auto select best
        menu.add_checkbutton(
            label="Auto select best result",
            variable=self.var_auto_select_best,
            command=lambda: (
                self._refresh_results(),
                self.config.set("auto_select_best", self.var_auto_select_best.get()),
            ),
        )

        # Show all
        menu.add_checkbutton(
            label="Show all results",
            variable=self.var_show_all,
            command=lambda: (
                self._refresh_results(),
                self.config.set("show_all", self.var_show_all.get()),
            ),
        )

        # Separator
        menu.add_separator()

        # Light mode toggle
        menu.add_checkbutton(
            label="Light mode",
            variable=self.var_light_mode,
            command=self._toggle_theme,
        )

        # Post menu at button location
        x = self.settings_btn.winfo_rootx()
        y = self.settings_btn.winfo_rooty() + self.settings_btn.winfo_height()
        menu.post(x, y)

    def run(self):
        self.root.mainloop()

    def _build_ui(self):
        self.root.columnconfigure(0, weight=3)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(0, weight=1)

        left = ttk.Frame(self.root, padding=16)
        left.grid(row=0, column=0, sticky="nsew")
        left.columnconfigure(0, weight=1)
        left.rowconfigure(4, weight=1)

        header = ttk.Frame(left)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Caesar", style="Hero.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            header,
            text="Brute-force & transform classic ciphers",
            style="Subtle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        input_card = ttk.Frame(left, style="Card.TFrame", padding=14)
        input_card.grid(row=1, column=0, sticky="ew", pady=(14, 10))
        input_card.columnconfigure(0, weight=1)

        top_controls = ttk.Frame(input_card)
        top_controls.grid(row=0, column=0, sticky="ew")
        # Configure columns 8 and 8 to expand (spacer columns on each row)
        top_controls.columnconfigure(8, weight=1)

        ttk.Label(top_controls, text="Cipher:", style="Muted.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        # Build an in-window tk.Menu and open it from a themed ttk.Button so it matches the app colors
        self.cipher_menu = tk.Menu(self.root, tearoff=False)
        for category, ciphers in CIPHER_CATEGORIES.items():
            sub = tk.Menu(self.cipher_menu, tearoff=False)
            for cipher in ciphers:
                sub.add_command(
                    label=cipher, command=lambda c=cipher: self._select_cipher(c)
                )
            self.cipher_menu.add_cascade(label=category, menu=sub)

        # Use ttk.Menubutton styled like TButton so it matches theme on macOS
        self.mb_cipher = ttk.Menubutton(
            top_controls,
            textvariable=self.var_cipher,
            width=14,
            style="TMenubutton",
        )
        self.mb_cipher.grid(row=0, column=1, sticky="w", padx=(6, 14))
        # attach menu to menubutton so macOS Aqua positions submenus correctly
        self.mb_cipher.configure(menu=self.cipher_menu)

        ttk.Label(top_controls, text="Mode:", style="Muted.TLabel").grid(
            row=0, column=2, sticky="w"
        )

        # Input text area
        ttk.Label(input_card, text="Input text", style="Muted.TLabel").grid(
            row=1, column=0, sticky="w"
        )
        self.txt_input = tk.Text(
            input_card, height=8, wrap="word", borderwidth=0, highlightthickness=1
        )
        self.txt_input.grid(row=2, column=0, sticky="ew", pady=(6, 10))
        self._style_text_widget(self.txt_input)
        self.txt_input.bind("<<Modified>>", self._on_input_modified)
        self.txt_input.edit_modified(False)
        cb_mode = ttk.Combobox(
            top_controls,
            values=["ciphertext", "plaintext"],
            textvariable=self.var_input_mode,
            state="readonly",
            width=12,
        )
        cb_mode.grid(row=0, column=3, sticky="w", padx=(6, 14))
        cb_mode.bind(
            "<<ComboboxSelected>>",
            lambda _e: (
                self._refresh_results(),
                self.config.set("input_mode", self.var_input_mode.get()),
            ),
        )

        ttk.Checkbutton(
            top_controls,
            text="Light mode",
            variable=self.var_light_mode,
            command=self._toggle_theme,
        ).grid(row=0, column=4, sticky="w", padx=(0, 10))

        # Settings button
        self.settings_btn = ttk.Button(
            top_controls, text="⚙ Settings", command=self._open_settings_menu
        )
        self.settings_btn.grid(row=0, column=5, sticky="w", padx=(8, 10))

        # Spacer that expands on first row
        ttk.Frame(top_controls).grid(row=0, column=6, sticky="ew")

        actions = ttk.Frame(input_card)
        actions.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        actions.columnconfigure(10, weight=1)

        ttk.Button(actions, text="Break / Apply", command=self._refresh_results).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Button(actions, text="Clear", command=self._clear).grid(
            row=0, column=1, sticky="w", padx=(10, 0)
        )

        ttk.Separator(actions, orient="vertical").grid(
            row=0, column=2, sticky="ns", padx=14
        )

        ttk.Label(actions, text="Direct shift (Caesar):", style="Muted.TLabel").grid(
            row=0, column=3, sticky="w"
        )
        self.ent_shift = ttk.Entry(actions, width=6, textvariable=self.var_shift_direct)
        self.ent_shift.grid(row=0, column=4, sticky="w", padx=(6, 10))
        self.ent_shift.bind("<Return>", lambda _e: self._apply_direct_shift())

        self.btn_shift_apply = ttk.Button(
            actions, text="Apply", command=self._apply_direct_shift
        )
        self.btn_shift_apply.grid(row=0, column=5, sticky="w")

        preview_card = ttk.Frame(left, style="Card.TFrame", padding=14)
        preview_card.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        preview_card.columnconfigure(0, weight=1)

        ttk.Label(preview_card, text="Best guess preview", style="Muted.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        self.lbl_best_meta = ttk.Label(preview_card, text="—", style="Subtle.TLabel")
        self.lbl_best_meta.grid(row=1, column=0, sticky="w", pady=(4, 8))

        self.txt_best = tk.Text(
            preview_card, height=6, wrap="word", borderwidth=0, highlightthickness=1
        )
        self.txt_best.grid(row=2, column=0, sticky="ew")
        self._style_text_widget(self.txt_best)
        self.txt_best.configure(state="disabled")

        preview_actions = ttk.Frame(preview_card)
        preview_actions.grid(row=3, column=0, sticky="ew", pady=(10, 0))

        ttk.Button(preview_actions, text="Copy best", command=self._copy_best).grid(
            row=0, column=0, sticky="w", padx=6
        )

        ttk.Button(
            preview_actions, text="Copy selected", command=self._copy_selected
        ).grid(row=0, column=1, sticky="w", padx=6)

        ttk.Button(preview_actions, text="Load sample", command=self._load_sample).grid(
            row=0, column=2, sticky="w", padx=6
        )

        ttk.Button(preview_actions, text="Self-test", command=self._self_test).grid(
            row=0, column=3, sticky="w", padx=6
        )

        diff_card = ttk.Frame(left, style="Card.TFrame", padding=14)
        diff_card.grid(row=3, column=0, sticky="nsew")
        diff_card.columnconfigure(0, weight=1)
        diff_card.rowconfigure(1, weight=1)

        ttk.Label(diff_card, text="Side-by-side diff", style="Muted.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 8)
        )
        self.diff_view = DiffView(
            diff_card, style_text_fn=self._style_text_widget, root=self.root
        )
        self.diff_view.grid(row=1, column=0, sticky="nsew")

        right = ttk.Frame(self.root, padding=(0, 16, 16, 16))
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        ttk.Label(right, text="Results", style="Section.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 10)
        )
        self.table = ResultsTable(right, on_select=self._on_row_select)
        self.table.grid(row=1, column=0, sticky="nsew")
        self.analysis = AnalysisPanel(right)
        self.analysis.grid(row=2, column=0, sticky="ew", pady=(12, 0))

        self.subst = SubstitutionHelper(right, on_apply=self._on_subst_apply)
        self.subst.grid(row=3, column=0, sticky="ew", pady=(12, 0))

        footer = ttk.Frame(right)
        footer.grid(row=4, column=0, sticky="ew", pady=(10, 0))
        footer.columnconfigure(0, weight=1)
        self.lbl_status = ttk.Label(footer, text="Ready", style="Muted.TLabel")
        self.lbl_status.grid(row=0, column=0, sticky="w")

        ttk.Button(
            footer,
            text="Export selected → input",
            command=self._export_selected_to_input,
        ).grid(row=0, column=1, sticky="e")

        # apply initial state behavior
        self._on_cipher_changed(initial=True)

    def _bind_shortcuts(self):
        self.root.bind_all("<Control-Return>", lambda _e: self._refresh_results())
        self.root.bind_all(
            "<Command-Return>", lambda _e: self._refresh_results()
        )  # macOS
        self.root.bind_all("<Control-l>", lambda _e: self._clear())
        self.root.bind_all("<Command-l>", lambda _e: self._clear())  # macOS
        self.root.bind_all("<Control-b>", lambda _e: self._copy_best())
        self.root.bind_all("<Command-b>", lambda _e: self._copy_best())  # macOS
        self.root.bind_all("<Control-s>", lambda _e: self._load_sample())
        self.root.bind_all("<Command-s>", lambda _e: self._load_sample())  # macOS
        self.root.bind_all("<Control-e>", lambda _e: self._export_selected_to_input())
        self.root.bind_all(
            "<Command-e>", lambda _e: self._export_selected_to_input()
        )  # macOS
        self.root.bind_all("<Control-Shift-E>", lambda _e: self._export_to_file())
        self.root.bind_all(
            "<Command-Shift-E>", lambda _e: self._export_to_file()
        )  # macOS
        self.root.bind_all("<Control-t>", lambda _e: self._toggle_theme())
        self.root.bind_all("<Command-t>", lambda _e: self._toggle_theme())  # macOS

    def _toggle_theme(self):
        self.var_theme.set("light" if self.var_theme.get() == "dark" else "dark")
        apply_theme(self.root, self.var_theme.get())

        # Save theme preference
        self.config.set("theme", self.var_theme.get())
        self.var_light_mode.set(self.var_theme.get() == "light")

        self._style_text_widget(self.txt_input)
        self._style_text_widget(self.txt_best)
        self._style_text_widget(self.diff_view.left)
        self._style_text_widget(self.diff_view.right)
        self.diff_view.refresh_theme()

        self.toast.show(f"Theme: {self.var_theme.get()}")

    def _style_text_widget(self, w: tk.Text):
        # Get current theme and palette
        mode = self.var_theme.get()
        p = PALETTES.get(mode, PALETTES["dark"])

        bg = p["card2"]
        fg = p["text"]
        ins = fg
        sel_bg = p["accent2"]
        border = p["border"]
        font_val = ("Menlo", 12)

        w.configure(
            background=bg,
            foreground=fg,
            insertbackground=ins,
            selectbackground=sel_bg,
            selectforeground=fg,
            highlightbackground=border,
            highlightcolor=border,
            padx=12,
            pady=10,
            font=font_val,
        )

    def _select_cipher(self, cipher_name: str):
        """Called when a cipher is selected from the menu."""
        self.var_cipher.set(cipher_name)
        self.config.set("last_cipher", cipher_name)
        self._on_cipher_changed()

    def _show_cipher_menu(self, event=None):
        """Post the in-window cipher menu directly under the cipher button."""
        x = self.mb_cipher.winfo_rootx()
        # Base position: directly under the menubutton
        y = self.mb_cipher.winfo_rooty() + self.mb_cipher.winfo_height()
        # Sometimes macOS needs a tiny vertical fudge because of borders/relief.
        # Apply a 1px offset on darwin to nudge the menu into perfect alignment.
        if sys.platform == "darwin":
            y += 1
        self.cipher_menu.post(x, y)

    def _on_menubar_cipher_selected(self, cipher_name: str):
        """Handler invoked by the macOS native menubar items.

        Keep logic identical to other selection paths.
        """
        self.var_cipher.set(cipher_name)
        self._on_cipher_changed()

    def _on_cipher_changed(self, initial: bool = False):
        cipher = self.var_cipher.get()

        # Enable substitution panel only in substitution mode
        if hasattr(self, "subst"):
            self.subst.set_enabled(cipher == "Substitution (manual)")

        if cipher == "Vigenere (detect)":
            # No brute force. Show key-length hints in Analysis.
            self.table.set_rows([])
            hint = vigenere_summarize(text, max_len=20)
            # reuse analysis panel for multi-line text
            self.analysis.lbl_stats.configure(text=hint)
            self.analysis.lbl_letters.configure(text="")
            self.analysis.lbl_bigrams.configure(text="")
            self._set_best_preview(None)
            self.diff_view.set_texts(text, "")
            self.lbl_status.configure(text="Vigenère detect • see Analysis")
            return

        if cipher == "Substitution (manual)":
            # No brute force; user applies mapping manually
            self.table.set_rows([])
            self.lbl_status.configure(text="Substitution manual • use mapping panel")
            # apply current mapping (if any)
            try:
                self._on_subst_apply(self.subst.get_mapping())
            except Exception:
                pass
            return

        # Disable Caesar direct shift controls unless Caesar
        caesar_enabled = cipher == "Caesar"
        self.ent_shift.configure(state=("normal" if caesar_enabled else "disabled"))
        self.btn_shift_apply.configure(
            state=("normal" if caesar_enabled else "disabled")
        )

        # For single-result ciphers, Show all / Top N doesn't matter → we lock it down
        if cipher in SINGLE_RESULT_CIPHERS:
            self.var_show_all.set(False)
        else:
            # Keep Top N disabled if Show all is enabled
            pass

        if not initial:
            self._refresh_results()

    def _on_input_modified(self, _event):
        if self.txt_input.edit_modified():
            self.txt_input.edit_modified(False)
            self._refresh_results(live=True)

    def _get_input_text(self) -> str:
        return self.txt_input.get("1.0", "end-1c")

    def _refresh_results(self, live: bool = False):
        try:
            text = self._get_input_text()
            if not text.strip():
                self.table.set_rows([])
                self._set_best_preview(None)
                self.diff_view.set_texts("", "")
                self.lbl_status.configure(text="Ready")
                return

            cipher = self.var_cipher.get()

            # Enable substitution panel only in substitution mode
            if hasattr(self, "subst"):
                self.subst.set_enabled(cipher == "Substitution (manual)")
                if cipher == "Substitution (manual)":
                    self.subst.update_ciphertext(text)

            if cipher == "Vigenere (detect)":
                # No brute force. Show key-length hints in Analysis.
                self.table.set_rows([])
                hint = vigenere_summarize(text, max_len=20)
                # reuse analysis panel for multi-line text
                self.analysis.lbl_stats.configure(text=hint)
                self.analysis.lbl_letters.configure(text="")
                self.analysis.lbl_bigrams.configure(text="")
                self._set_best_preview(None)
                self.diff_view.set_texts(text, "")
                self.lbl_status.configure(text="Vigenère detect • see Analysis")
                return

            # keep Top N enabled/disabled in sync if user toggled Show all
            # Note: spin_topn widget not yet implemented in UI
            # if cipher not in SINGLE_RESULT_CIPHERS:
            #     self.spin_topn.configure(
            #         state=("disabled" if self.var_show_all.get() else "normal")
            #     )

            results = brute_force(
                text=text,
                cipher=cipher,
                input_mode=self.var_input_mode.get(),
                keep_case=bool(self.var_keep_case.get()),
                keep_punct=bool(self.var_keep_punct.get()),
            )

            # ✅ UI polish behavior:
            # - single-result ciphers always show 1
            # - otherwise: show all or Top N
            if cipher in SINGLE_RESULT_CIPHERS:
                results = results[:1]
            else:
                if not self.var_show_all.get():
                    try:
                        topn = int(self.var_top_n.get())
                    except Exception:
                        topn = 50
                    topn = max(1, min(500, topn))
                    results = results[:topn]

            self.table.set_rows(results)

            if results and self.var_auto_select_best.get():
                self.table.select_index(0)

            label = "Live updated" if live else "Updated"
            self.lbl_status.configure(text=f"{label} • {cipher} • {len(results)} shown")

            sel = self.table.get_selected()
            if sel is None and results:
                sel = results[0]
            self._set_best_preview(sel)

        except Exception as e:
            self.toast.show(f"Error: {str(e)}")
            self.lbl_status.configure(text=f"Error: {str(e)}")

    def _set_best_preview(self, row):
        original = self._get_input_text()

        self.txt_best.configure(state="normal")
        self.txt_best.delete("1.0", "end")

        if not row:
            self.lbl_best_meta.configure(text="—")
            self.txt_best.configure(state="disabled")
            return

        key = row.get("key", "")
        score = row.get("score", 0.0)
        note = row.get("note", "")

        meta = f"Key/Shift: {key} • Score: {score:.2f}"
        if note:
            meta += f" • {note}"

        self.lbl_best_meta.configure(text=meta)
        self.txt_best.insert("1.0", row["text"])
        self.txt_best.configure(state="disabled")

        self.diff_view.set_texts(original, row["text"])
        self.analysis.update_text(row["text"] if row else "")

    def _on_row_select(self, row):
        self._set_best_preview(row)

    def _apply_direct_shift(self):
        if self.var_cipher.get() != "Caesar":
            self.toast.show("Direct shift applies to Caesar mode only.")
            return

        text = self._get_input_text()
        if not text.strip():
            self.toast.show("Nothing to shift (input is empty).")
            return

        try:
            s = clamp_int(self.var_shift_direct.get(), -1000, 1000)
        except (ValueError, AttributeError) as e:
            self.toast.show("Direct shift must be a valid integer.")
            return

        try:
            out = caesar_shift(
                text,
                shift=s,
                keep_case=bool(self.var_keep_case.get()),
                keep_punct=bool(self.var_keep_punct.get()),
            )
            self._replace_input(out)
            self.toast.show(f"Applied shift {s:+d} to input.")
            self._refresh_results()
        except Exception as e:
            self.toast.show(f"Error applying shift: {str(e)}")

    def _replace_input(self, new_text: str):
        self.txt_input.delete("1.0", "end")
        self.txt_input.insert("1.0", new_text)
        self.txt_input.edit_modified(False)

    def _on_subst_apply(self, mapping: dict[str, str]):
        # Only active in Substitution (manual) mode
        if self.var_cipher.get() != "Substitution (manual)":
            return
        text = self.txt_input.get("1.0", "end-1c")
        if not text.strip():
            self._set_best_preview(None)
            try:
                self.diff_view.set_texts(text, "")
            except Exception:
                pass
            return

        cand = apply_substitution(
            text,
            mapping,
            keep_case=self.var_keep_case.get(),
            keep_punct=self.var_keep_punct.get(),
        )
        row = {"key": "substitution", "score": 0.0, "text": cand, "mode": "manual"}
        self._set_best_preview(row)

    def _clear(self):
        self._replace_input("")
        self.table.set_rows([])
        self._set_best_preview(None)
        self.diff_view.set_texts("", "")
        self.lbl_status.configure(text="Ready")
        self.toast.show("Cleared.")

    def _copy_best(self):
        row = self.table.get_selected()
        if row is None:
            rows = self.table.get_rows()
            row = rows[0] if rows else None
        if not row:
            self.toast.show("No result to copy.")
            return
        copy_to_clipboard(self.root, row["text"])
        self.toast.show("Copied best/selected result to clipboard.")

    def _copy_selected(self):
        row = self.table.get_selected()
        if not row:
            self.toast.show("No selected row to copy.")
            return
        copy_to_clipboard(self.root, row["text"])
        self.toast.show("Copied selected result to clipboard.")

    def _load_sample(self):
        cipher = self.var_cipher.get()
        sample = SAMPLES.get(cipher)
        if not sample:
            self.toast.show(f"No sample for {cipher}.")
            return
        self._replace_input(sample["ciphertext"])
        self.toast.show(f"Loaded {cipher} sample ({sample['hint']})")
        self._refresh_results()

    def _self_test(self):
        failures = []
        for cipher, sample in SAMPLES.items():
            self.var_cipher.set(cipher)
            self._replace_input(sample["ciphertext"])
            self._refresh_results()
            row = self.table.get_rows()[0] if self.table.get_rows() else None
            if not row or sample["expected"] not in row["text"]:
                failures.append(cipher)
        if failures:
            self.toast.show("Self-test failed: " + ", ".join(failures))
        else:
            self.toast.show("Self-test passed ✓")

    def _export_selected_to_input(self):
        row = self.table.get_selected()
        if not row:
            self.toast.show("No selected row to export.")
            return
        self._replace_input(row["text"])
        self.toast.show("Exported selected result to input.")
        self._refresh_results()

    def _export_to_file(self):
        """Export results to a text file."""
        rows = self.table.get_rows()
        if not rows:
            self.toast.show("No results to export.")
            return

        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Export Results",
            )

            if filename:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(f"Caesar Cipher Analysis Results\\n")
                    f.write(f"Cipher: {self.var_cipher.get()}\\n")
                    f.write(f"Total results: {len(rows)}\\n")
                    f.write("=" * 80 + "\\n\\n")

                    for i, row in enumerate(rows, 1):
                        f.write(f"Result #{i}\\n")
                        f.write(f"Key: {row.get('key', 'N/A')}\\n")
                        f.write(f"Score: {row.get('score', 0):.2f}\\n")
                        f.write(f"Note: {row.get('note', 'N/A')}\\n")
                        f.write(f"Text: {row.get('text', '')}\\n")
                        f.write("-" * 80 + "\\n\\n")

                self.toast.show(f"Exported {len(rows)} results to {filename}")
        except Exception as e:
            self.toast.show(f"Export failed: {str(e)}")

    def _on_close(self):
        """Save configuration before closing."""
        # Save current settings
        self.config.set("keep_case", self.var_keep_case.get())
        self.config.set("keep_punct", self.var_keep_punct.get())
        self.config.set("auto_select_best", self.var_auto_select_best.get())
        self.config.set("show_all", self.var_show_all.get())
        self.config.set("top_n", self.var_top_n.get())
        self.config.set("input_mode", self.var_input_mode.get())

        # Save window geometry
        try:
            self.config.set("window_geometry", self.root.geometry())
        except Exception:
            pass

        self.root.destroy()
