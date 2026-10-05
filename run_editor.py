from pathlib import Path
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from app.rom_builder import generate_rom, export_rom


DEFAULT_PROJECT = {
    "title": "RAIL RUNNER",
    "difficulty": "normal",
    "enemy_count": 18,
    "player_speed": 4,
    "boss": "specter",
    "theme": "sunset",
    "background_color": "#F7B267",
    "music": "neon-ride",
    "scroll_speed": 8,
    "boss_health": 16,
}


class LevelEditorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Game Boy Rail Shooter Editor")
        self.geometry("720x520")
        self.minsize(680, 460)
        self.project = {**DEFAULT_PROJECT}

        self._build_ui()
        self._load_demo_project()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        left = ttk.Frame(self, padding=12)
        left.grid(row=0, column=0, sticky="nsew")
        right = ttk.Frame(self, padding=12)
        right.grid(row=0, column=1, sticky="nsew")

        fields = [
            ("Title", "title"),
            ("Difficulty", "difficulty"),
            ("Enemy Count", "enemy_count"),
            ("Player Speed", "player_speed"),
            ("Boss", "boss"),
            ("Theme", "theme"),
            ("Background Color", "background_color"),
            ("Music", "music"),
            ("Scroll Speed", "scroll_speed"),
            ("Boss Health", "boss_health"),
        ]

        self.entries = {}
        for index, (label_text, key) in enumerate(fields):
            label = ttk.Label(left, text=label_text)
            label.grid(row=index, column=0, sticky="w", pady=4)
            entry = ttk.Entry(left, width=28)
            entry.grid(row=index, column=1, sticky="ew", padx=(8, 0), pady=4)
            self.entries[key] = entry

        left.columnconfigure(1, weight=1)

        button_row = ttk.Frame(right)
        button_row.pack(fill="x", pady=(0, 12))

        ttk.Button(button_row, text="Load Demo", command=self._load_demo_project).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Save Project", command=self._save_project).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Export .gb", command=self._export_rom).pack(side="left")

        preview = ttk.Label(
            right,
            text=(
                "Simple rail shooter prototype for Game Boy Original.\n\n"
                "Project format includes:\n"
                "- title\n"
                "- difficulty\n"
                "- enemy_count\n"
                "- boss\n"
                "- theme\n"
                "- speed and ROM export\n"
            ),
            justify="left",
            wraplength=300,
        )
        preview.pack(anchor="w", pady=12)

        self.export_status = tk.StringVar(value="Ready")
        status = ttk.Label(right, textvariable=self.export_status, foreground="#1a7f37")
        status.pack(anchor="w", pady=(18, 0))

    def _apply_project_to_form(self):
        for key, entry in self.entries.items():
            value = self.project.get(key, "")
            entry.delete(0, tk.END)
            entry.insert(0, str(value))

    def _load_demo_project(self):
        self.project = {
            **DEFAULT_PROJECT,
            "title": "RAIL RUNNER",
            "difficulty": "normal",
            "theme": "sunset",
        }
        self._apply_project_to_form()
        self.export_status.set("Demo loaded")

    def _collect_project(self):
        data = {}
        for key, entry in self.entries.items():
            raw = entry.get().strip()
            if key in {"enemy_count", "player_speed", "scroll_speed", "boss_health"}:
                data[key] = int(raw)
            else:
                data[key] = raw
        return data

    def _save_project(self):
        data = self._collect_project()
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON project", "*.json")],
            initialfile=f"{data['title'].lower().replace(' ', '_')}.json",
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
        self.project = data
        self.export_status.set(f"Saved: {Path(path).name}")

    def _export_rom(self):
        data = self._collect_project()
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"{data['title'].lower().replace(' ', '_')}.gb"
        rom_bytes = generate_rom(data)
        export_rom(rom_bytes, str(output_path))
        self.export_status.set(f"Exported: {output_path.name}")
        messagebox.showinfo("Export complete", f"ROM saved to:\n{output_path}")


if __name__ == "__main__":
    app = LevelEditorApp()
    app.mainloop()
