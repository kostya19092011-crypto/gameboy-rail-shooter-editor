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
    "segments": [
        {"type": "enemy", "label": "E1"},
        {"type": "enemy", "label": "E2"},
        {"type": "pickup", "label": "P"},
        {"type": "enemy", "label": "E3"},
        {"type": "boss", "label": "B"},
        {"type": "enemy", "label": "E4"},
        {"type": "pickup", "label": "P"},
        {"type": "enemy", "label": "E5"},
    ],
}


class LevelEditorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Game Boy Rail Shooter Editor")
        self.geometry("980x620")
        self.minsize(860, 560)
        self.project = {**DEFAULT_PROJECT}

        self.segment_types = ["empty", "enemy", "pickup", "boss"]
        self.selected_segment_index = 0

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
            ttk.Label(left, text=label_text).grid(row=index, column=0, sticky="w", pady=4)
            entry = ttk.Entry(left, width=28)
            entry.grid(row=index, column=1, sticky="ew", padx=(8, 0), pady=4)
            self.entries[key] = entry

        left.columnconfigure(1, weight=1)

        stage_group = ttk.LabelFrame(left, text="Level track", padding=8)
        stage_group.grid(row=20, column=0, columnspan=2, sticky="ew", pady=(12, 0))

        self.segment_canvas = tk.Canvas(stage_group, width=520, height=140, bg="#f4f4f4")
        self.segment_canvas.pack(fill="x")

        stage_buttons = ttk.Frame(stage_group)
        stage_buttons.pack(fill="x", pady=(8, 0))

        ttk.Button(stage_buttons, text="Add Enemy", command=lambda: self._add_segment("enemy")).pack(side="left", padx=(0, 6))
        ttk.Button(stage_buttons, text="Add Pickup", command=lambda: self._add_segment("pickup")).pack(side="left", padx=(0, 6))
        ttk.Button(stage_buttons, text="Add Boss", command=lambda: self._add_segment("boss")).pack(side="left", padx=(0, 6))
        ttk.Button(stage_buttons, text="Clear", command=lambda: self._add_segment("empty")).pack(side="left")

        right_top = ttk.Frame(right)
        right_top.pack(fill="x", pady=(0, 12))
        ttk.Button(right_top, text="Load Demo", command=self._load_demo_project).pack(side="left", padx=(0, 8))
        ttk.Button(right_top, text="Save Project", command=self._save_project).pack(side="left", padx=(0, 8))
        ttk.Button(right_top, text="Export .gb", command=self._export_rom).pack(side="left")

        preview = ttk.Label(
            right,
            text=(
                "Схема на уровне:
"
                "- enemy = враг
"
                "- pickup = бонус
"
                "- boss = босс
"
                "- empty = пустой участок\n\n"
                "Программа генерирует проект в JSON и сохраняет .gb ROM."
            ),
            justify="left",
            wraplength=320,
        )
        preview.pack(anchor="w", pady=12)

        self.export_status = tk.StringVar(value="Ready")
        ttk.Label(right, textvariable=self.export_status, foreground="#1a7f37").pack(anchor="w", pady=(12, 0))

        self._render_segments()

    def _apply_project_to_form(self):
        for key, entry in self.entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, str(self.project.get(key, "")))
        self._render_segments()

    def _load_demo_project(self):
        self.project = {
            **DEFAULT_PROJECT,
            "title": "RAIL RUNNER",
            "difficulty": "normal",
            "theme": "sunset",
            "segments": [
                {"type": "enemy", "label": "E1"},
                {"type": "enemy", "label": "E2"},
                {"type": "pickup", "label": "P"},
                {"type": "enemy", "label": "E3"},
                {"type": "boss", "label": "B"},
                {"type": "enemy", "label": "E4"},
                {"type": "pickup", "label": "P"},
                {"type": "enemy", "label": "E5"},
            ],
        }
        self._apply_project_to_form()
        self.export_status.set("Demo loaded")

    def _collect_project(self):
        data = {}
        for key, entry in self.entries.items():
            raw = entry.get().strip()
            if key in {"enemy_count", "player_speed", "scroll_speed", "boss_health"}:
                try:
                    data[key] = int(raw)
                except ValueError:
                    data[key] = 0
            else:
                data[key] = raw
        data["segments"] = self.project.get("segments", [])
        return data

    def _render_segments(self):
        self.segment_canvas.delete("all")
        segments = self.project.get("segments", [])
        if not segments:
            segments = [{"type": "empty", "label": ""}]

        x_step = 52
        width = max(50, len(segments) * x_step)
        self.segment_canvas.config(width=max(430, width), height=140)

        for idx, segment in enumerate(segments):
            x0 = 20 + idx * x_step
            y0 = 20
            x1 = x0 + 36
            y1 = y0 + 60

            color = {
                "empty": "#d6d6d6",
                "enemy": "#ff6b6b",
                "pickup": "#ffd166",
                "boss": "#7b61ff",
            }.get(segment.get("type", "empty"), "#d6d6d6")

            self.segment_canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="#333333", width=2)
            label = segment.get("label", segment.get("type", "")[0].upper())
            self.segment_canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text=label, font=("Arial", 11, "bold"))

            if idx == self.selected_segment_index:
                self.segment_canvas.create_rectangle(x0 - 4, y0 - 4, x1 + 4, y1 + 4, outline="#1f77b4", width=3)

        self.segment_canvas.bind("<Button-1>", self._click_segment)

    def _click_segment(self, event):
        segments = self.project.get("segments", [])
        if not segments:
            return
        index = int((event.x - 20) // 52)
        if 0 <= index < len(segments):
            self.selected_segment_index = index
            self._render_segments()

    def _add_segment(self, segment_type: str):
        segments = self.project.get("segments", [])
        if segment_type == "empty":
            label = ""
        elif segment_type == "enemy":
            label = f"E{len(segments) + 1}"
        elif segment_type == "pickup":
            label = "P"
        else:
            label = "B"

        segments.append({"type": segment_type, "label": label})
        self.project["segments"] = segments
        self.selected_segment_index = len(segments) - 1
        self._render_segments()

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
