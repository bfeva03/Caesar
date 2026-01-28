import tkinter as tk
from tkinter import ttk

# Higher-contrast, easier-to-read palette
PALETTES = {
    "dark": {
        "bg": "#0A1020",
        "card": "#111B2E",
        "card2": "#0E1728",
        "text": "#F2F7FF",
        "muted": "#BBD0F5",
        "border": "#233656",
        "accent": "#3B82F6",
        "accent2": "#2563EB",
    },
    "light": {
        "bg": "#F6F9FF",
        "card": "#FFFFFF",
        "card2": "#FFFFFF",
        "text": "#000000",
        "muted": "#2B4C7E",
        "border": "#CFDBF2",
        "accent": "#2563EB",
        "accent2": "#1D4ED8",
    },
}


def apply_theme(root: tk.Tk, mode: str = "dark"):
    if mode not in PALETTES:
        mode = "dark"
    p = PALETTES[mode]

    root.configure(bg=p["bg"])

    # tk.Text styling via option database
    root.option_add("*caeser.text.bg", p["card2"], priority="startupFile")
    root.option_add("*caeser.text.fg", p["text"], priority="startupFile")
    root.option_add("*caeser.text.insert", p["text"], priority="startupFile")
    root.option_add(
        "*caeser.text.selbg", p["accent2"], priority="startupFile"
    )  # also used for diff highlight
    root.option_add("*caeser.text.border", p["border"], priority="startupFile")
    root.option_add("*caeser.font.mono", ("Menlo", 12), priority="startupFile")

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(
        ".", background=p["bg"], foreground=p["text"], font=("Segoe UI", 11)
    )
    style.configure("TFrame", background=p["bg"])
    style.configure("Card.TFrame", background=p["card"], relief="flat")
    style.configure("TLabel", background=p["bg"], foreground=p["text"])
    style.configure("Muted.TLabel", background=p["card"], foreground=p["muted"])
    style.configure("Subtle.TLabel", background=p["bg"], foreground=p["muted"])
    style.configure(
        "Hero.TLabel",
        background=p["bg"],
        foreground=p["text"],
        font=("Segoe UI Semibold", 26),
    )
    style.configure(
        "Section.TLabel",
        background=p["bg"],
        foreground=p["text"],
        font=("Segoe UI Semibold", 14),
    )

    style.configure(
        "TButton",
        background=p["accent"],
        foreground=p["text"],
        borderwidth=0,
        focusthickness=0,
        padding=(12, 8),
    )
    style.map(
        "TButton",
        background=[
            ("active", p["accent2"]),
            ("pressed", p["accent2"]),
            ("disabled", p["border"]),
        ],
        foreground=[("disabled", p["muted"])],
    )

    # Style for menubuttons to match TButton so in-window menu buttons blend with theme
    style.configure(
        "TMenubutton",
        background=p["card2"],
        foreground=p["text"],
        borderwidth=0,
        focusthickness=0,
        padding=(10, 6),
    )
    style.map(
        "TMenubutton",
        background=[("active", p["accent2"]), ("disabled", p["border"])],
        foreground=[("disabled", p["muted"])],
    )

    style.configure(
        "TEntry",
        fieldbackground=p["card2"],
        background=p["card2"],
        foreground=p["text"],
        bordercolor=p["border"],
        lightcolor=p["border"],
        darkcolor=p["border"],
        padding=(10, 8),
    )

    style.configure(
        "TCombobox",
        fieldbackground=p["card2"],
        background=p["card2"],
        foreground=p["text"],
        arrowcolor=p["text"],
        bordercolor=p["border"],
        padding=(10, 6),
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", p["card2"])],
        background=[("readonly", p["card2"])],
        foreground=[("readonly", p["text"])],
    )

    style.configure("TCheckbutton", background=p["bg"], foreground=p["text"])
    style.map("TCheckbutton", foreground=[("disabled", p["muted"])])

    style.configure("TSeparator", background=p["border"])

    style.configure(
        "Treeview",
        background=p["card"],
        fieldbackground=p["card"],
        foreground=p["text"],
        bordercolor=p["border"],
        lightcolor=p["border"],
        darkcolor=p["border"],
        rowheight=28,
    )
    style.configure(
        "Treeview.Heading",
        background=p["card2"],
        foreground=p["text"],
        relief="flat",
        padding=(8, 8),
        font=("Segoe UI Semibold", 11),
    )
    style.map(
        "Treeview",
        background=[("selected", p["accent2"])],
        foreground=[("selected", p["text"])],
    )

    style.configure(
        "Toast.TLabel", background=p["card"], foreground=p["muted"], padding=(10, 8)
    )
    style.configure(
        "Vertical.TScrollbar",
        background=p["bg"],
        troughcolor=p["bg"],
        arrowcolor=p["muted"],
    )
