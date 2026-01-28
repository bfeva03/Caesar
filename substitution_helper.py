from __future__ import annotations

import string
import tkinter as tk
from tkinter import ttk
from collections import Counter

ALPHA = string.ascii_uppercase

# English letter frequency order (most common first)
EN_FREQ_ORDER = "ETAOINSHRDLCUMWFGYPBVKJXQZ"


def apply_substitution(
    text: str, mapping: dict[str, str], keep_case: bool = True, keep_punct: bool = True
) -> str:
    out = []
    for ch in text:
        if ch.isalpha():
            up = ch.upper()
            rep = mapping.get(up, "")
            if rep and rep.isalpha():
                rep_up = rep.upper()
                if keep_case and ch.islower():
                    out.append(rep_up.lower())
                else:
                    out.append(rep_up)
            else:
                # If unmapped, keep original letter (best for partial solving)
                out.append(ch)
        else:
            if keep_punct:
                out.append(ch)
            else:
                # drop non-letters if user wants
                if ch.isspace():
                    out.append(ch)
    return "".join(out)


class SubstitutionHelper(ttk.Frame):
    def __init__(self, parent, on_apply):
        super().__init__(parent, style="Card.TFrame", padding=14)
        self.on_apply = on_apply

        # Manual-substitution UX state
        self.active_letter: str | None = None
        self.locked: set[str] = set()
        self.ciphertext: str = ""

        self.columnconfigure(0, weight=1)

        ttk.Label(self, text="Substitution helper", style="Muted.TLabel").grid(
            row=0, column=0, sticky="w"
        )

        hint = "Type plaintext for each ciphertext letter. Unmapped letters stay unchanged."
        ttk.Label(
            self, text=hint, style="Subtle.TLabel", wraplength=520, justify="left"
        ).grid(row=1, column=0, sticky="w", pady=(6, 10))

        grid = ttk.Frame(self, style="Card.TFrame")
        grid.grid(row=2, column=0, sticky="ew")
        for c in range(13):
            grid.columnconfigure(c, weight=1)

        self.vars: dict[str, tk.StringVar] = {}
        self.entries: dict[str, tk.Entry] = {}

        # Two rows of 13 letters
        letters = list(ALPHA)
        for r in range(2):
            for c in range(13):
                idx = r * 13 + c
                L = letters[idx]

                cell = ttk.Frame(grid, style="Card.TFrame")
                cell.grid(row=r * 2, column=c, padx=3, pady=3, sticky="ew")

                ttk.Label(cell, text=L, style="Subtle.TLabel").grid(
                    row=0, column=0, sticky="w"
                )

                v = tk.StringVar(value="")
                e = tk.Entry(
                    cell,
                    width=2,
                    textvariable=v,
                    justify="center",
                    highlightthickness=1,
                    highlightbackground="#2A3A55",
                )
                e.grid(row=1, column=0, sticky="ew", pady=(2, 0))
                e.bind(
                    "<Button-1>", lambda evt, _ch=L: (self._set_active(_ch), "break")
                )
                e.bind(
                    "<Button-2>", lambda evt, _ch=L: (self._toggle_lock(_ch), "break")
                )
                e.bind(
                    "<Button-3>", lambda evt, _ch=L: (self._toggle_lock(_ch), "break")
                )

                # keep only A-Z and 1 char
                def _on_write(var=v):
                    s = var.get().upper()
                    s = "".join(ch for ch in s if ch.isalpha())
                    var.set(s[:1])

                v.trace_add("write", lambda *_, var=v: _on_write(var))

                self.vars[L] = v
                self.entries[L] = e

        self._refresh_entry_styles()

        btns = ttk.Frame(self, style="Card.TFrame")
        btns.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        btns.columnconfigure(0, weight=1)

        self.btn_apply = ttk.Button(btns, text="Apply mapping", command=self._apply)
        self.btn_apply.grid(row=0, column=0, sticky="w")

        self.btn_clear = ttk.Button(btns, text="Clear mapping", command=self.clear)
        self.btn_clear.grid(row=0, column=1, sticky="w", padx=(10, 0))

        self.btn_freq = ttk.Button(
            btns, text="Suggest by frequency", command=self._suggest_frequency
        )
        self.btn_freq.grid(row=0, column=2, sticky="w", padx=(10, 0))

        self.set_enabled(False)

    def _set_active(self, letter: str):
        self.active_letter = letter
        self._refresh_entry_styles()

    def _toggle_lock(self, letter: str):
        if letter in self.locked:
            self.locked.remove(letter)
        else:
            self.locked.add(letter)
        self._refresh_entry_styles()

    def _refresh_entry_styles(self):
        # Visual: active gets brighter border, locked gets disabled feel
        for ch, ent in self.entries.items():
            is_active = ch == self.active_letter
            is_locked = ch in self.locked

            # These colors match your darker blue theme reasonably well
            if is_active:
                ent.configure(
                    highlightthickness=2,
                    highlightbackground="#2D6BFF",
                    highlightcolor="#2D6BFF",
                )
            else:
                ent.configure(
                    highlightthickness=1,
                    highlightbackground="#2A3A55",
                    highlightcolor="#2A3A55",
                )

            if is_locked:
                ent.configure(state="disabled")
            else:
                ent.configure(state="normal")

    def handle_keypress(self, event):
        # If we have an active letter, route typing to that entry.
        if not self.active_letter:
            return
        ch = self.active_letter
        ent = self.entries.get(ch)
        if not ent:
            return
        if ch in self.locked:
            return "break"

        # Accept A-Z letters only for plaintext mapping
        if event.keysym == "BackSpace":
            ent.configure(state="normal")
            ent.delete(0, "end")
            ent.configure(state="disabled" if ch in self.locked else "normal")
            return "break"

        if not event.char:
            return
        c = event.char.upper()
        if "A" <= c <= "Z":
            ent.configure(state="normal")
            ent.delete(0, "end")
            ent.insert(0, c)
            ent.icursor("end")
            ent.configure(state="disabled" if ch in self.locked else "normal")
            return "break"

    def get_mapping(self) -> dict[str, str]:
        m: dict[str, str] = {}
        for k, v in self.vars.items():
            val = v.get().strip().upper()
            if val and val.isalpha():
                m[k] = val
        return m

    def clear(self):
        for v in self.vars.values():
            v.set("")
        self._apply()

    def _suggest_frequency(self):
        """Suggest mappings based on frequency analysis."""
        if not self.ciphertext:
            return

        # Get letter frequencies from ciphertext
        letters_only = "".join(ch.upper() for ch in self.ciphertext if ch.isalpha())
        if not letters_only:
            return

        freq = Counter(letters_only)
        # Sort by frequency (most common first)
        cipher_order = [letter for letter, _ in freq.most_common()]

        # Map to English frequency order
        for i, cipher_letter in enumerate(cipher_order):
            if i < len(EN_FREQ_ORDER) and cipher_letter not in self.locked:
                self.vars[cipher_letter].set(EN_FREQ_ORDER[i])

        self._apply()

    def update_ciphertext(self, text: str):
        """Update the ciphertext for frequency analysis."""
        self.ciphertext = text

    def _apply(self):
        if callable(self.on_apply):
            self.on_apply(self.get_mapping())

    def set_enabled(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        for e in self.entries.values():
            e.configure(state=state)
        self.btn_apply.configure(state=state)
        self.btn_clear.configure(state=state)
        self.btn_freq.configure(state=state)
