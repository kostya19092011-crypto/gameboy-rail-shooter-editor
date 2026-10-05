import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from app.rom_builder import export_rom, generate_rom


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
    "levels": [
        {
            "name": "Level 1",
            "theme": "sunset",
            "segments": [
                {"time": 0, "type": "enemy", "label": "E1", "pattern": "left"},
                {"time": 1, "type": "enemy", "label": "E2", "pattern": "right"},
                {"time": 2, "type": "pickup", "label": "P", "pattern": "bonus"},
                {"time": 3, "type": "enemy", "label": "E3", "pattern": "center"},
                {"time": 4, "type": "boss", "label": "B", "pattern": "boss"},
                {"time": 5, "type": "enemy", "label": "E4", "pattern": "left"},
                {"time": 6, "type": "pickup", "label": "P", "pattern": "bonus"},
                {"time": 7, "type": "enemy", "label": "E5", "pattern": "right"},
            ],
        },
        {
            "name": "Level 2",
            "theme": "midnight",
            "segments": [
                {"time": 0, "type": "enemy", "label": "E1", "pattern": "zigzag"},
                {"time": 1, "type": "pickup", "label": "P", "pattern": "bonus"},
                {"time": 2, "type": "enemy", "label": "E2", "pattern": "cross"},
                {"time": 3, "type": "enemy", "label": "E3", "pattern": "center"},
                {"time": 4, "type": "boss", "label": "B", "pattern": "boss"},
            ],
        },
    ],
}


class LevelEditorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Game Boy Rail Shooter Editor")
        self.geometry("1120x680")
        self.minsize(980, 560)
        self.project = json.loads(json.dumps(DEFAULT_PROJECT))
        self.level_index = 0
        self.selected_segment_index = 0
        self.segment_types = ["empty", "enemy", "pickup", "boss"]
        self.segment_type_var = tk.StringVar()
        self.segment_label_var = tk.StringVar()
        self.segment_time_var = tk.StringVar()
        self.segment_pattern_var = tk.StringVar()
        self.level_name_var = tk.StringVar()

        self._build_ui()
        self._load_demo_project()

    def _build_ui(self):
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=3)
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
            entry = ttk.Entry(left, width=30)
            entry.grid(row=index, column=1, sticky="ew", padx=(8, 0), pady=4)
            self.entries[key] = entry

        level_frame = ttk.LabelFrame(left, text="Levels", padding=8)
        level_frame.grid(row=20, column=0, columnspan=2, sticky="ew", pady=(12, 0))

        self.level_combo = ttk.Combobox(level_frame, state="readonly", width=25)
        self.level_combo.grid(row=0, column=0, sticky="ew")
        ttk.Button(level_frame, text="Add", command=self._add_level).grid(row=0, column=1, padx=(8, 0))
        ttk.Button(level_frame, text="Delete", command=self._delete_level).grid(row=0, column=2, padx=(8, 0))
        ttk.Label(level_frame, text="Level name").grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(level_frame, textvariable=self.level_name_var, width=25).grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(8, 0), columnspan=2)
        ttk.Button(level_frame, text="Rename", command=self._rename_current_level).grid(row=2, column=0, columnspan=3, sticky="ew", pady=(8, 0))

        track_frame = ttk.LabelFrame(left, text="Level track", padding=8)
        track_frame.grid(row=21, column=0, columnspan=2, sticky="ew", pady=(12, 0))

        self.segment_canvas = tk.Canvas(track_frame, width=620, height=160, bg="#f4f4f4")
        self.segment_canvas.pack(fill="x")

        stage_buttons = ttk.Frame(track_frame)
        stage_buttons.pack(fill="x", pady=(8, 0))

        ttk.Button(stage_buttons, text="Add Enemy", command=lambda: self._add_segment("enemy")).pack(side="left", padx=(0, 6))
        ttk.Button(stage_buttons, text="Add Pickup", command=lambda: self._add_segment("pickup")).pack(side="left", padx=(0, 6))
        ttk.Button(stage_buttons, text="Add Boss", command=lambda: self._add_segment("boss")).pack(side="left", padx=(0, 6))
        ttk.Button(stage_buttons, text="Remove Selected", command=self._remove_selected_segment).pack(side="left", padx=(0, 6))
        ttk.Button(stage_buttons, text="Apply Selected", command=self._apply_selected_segment).pack(side="left")

        select_block = ttk.LabelFrame(left, text="Selected segment", padding=8)
        select_block.grid(row=22, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        ttk.Label(select_block, text="Type").grid(row=0, column=0, sticky="w")
        self.segment_type_combo = ttk.Combobox(select_block, textvariable=self.segment_type_var, values=self.segment_types, state="readonly", width=18)
        self.segment_type_combo.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        ttk.Label(select_block, text="Time").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.segment_time_entry = ttk.Entry(select_block, textvariable=self.segment_time_var, width=18)
        self.segment_time_entry.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(8, 0))

        ttk.Label(select_block, text="Label").grid(row=2, column=0, sticky="w", pady=(8, 0))
        self.segment_label_entry = ttk.Entry(select_block, textvariable=self.segment_label_var, width=18)
        self.segment_label_entry.grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=(8, 0))

        ttk.Label(select_block, text="Pattern").grid(row=3, column=0, sticky="w", pady=(8, 0))
        self.segment_pattern_entry = ttk.Entry(select_block, textvariable=self.segment_pattern_var, width=18)
        self.segment_pattern_entry.grid(row=3, column=1, sticky="ew", padx=(8, 0), pady=(8, 0))

        timeline_frame = ttk.LabelFrame(right, text="Timeline", padding=8)
        timeline_frame.pack(fill="both", expand=True)

        self.timeline_tree = ttk.Treeview(timeline_frame, columns=("time", "type", "label", "pattern"), show="headings")
        self.timeline_tree.heading("time", text="Time")
        self.timeline_tree.heading("type", text="Type")
        self.timeline_tree.heading("label", text="Label")
        self.timeline_tree.heading("pattern", text="Pattern")
        self.timeline_tree.column("time", width=60, anchor="center")
        self.timeline_tree.column("type", width=90, anchor="center")
        self.timeline_tree.column("label", width=80, anchor="center")
        self.timeline_tree.column("pattern", width=120, anchor="center")
        self.timeline_tree.pack(fill="both", expand=True)
        self.timeline_tree.bind("<<TreeviewSelect>>", self._on_timeline_select)

        actions = ttk.Frame(right)
        actions.pack(fill="x", pady=(12, 0))
        ttk.Button(actions, text="Load Demo", command=self._load_demo_project).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Save Project", command=self._save_project).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Export .gb", command=self._export_rom).pack(side="left")

        self.export_status = tk.StringVar(value="Ready")
        ttk.Label(right, textvariable=self.export_status, foreground="#1a7f37").pack(anchor="w", pady=(12, 0))

        self._refresh_level_list()
        self._render_segments()
        self._refresh_timeline()

    def _current_level(self):
        levels = self.project.get("levels", [])
        if not levels:
            return None
        if 0 <= self.level_index < len(levels):
            return levels[self.level_index]
        self.level_index = 0
        return levels[0]

    def _refresh_level_list(self):
        current = self._current_level()
        names = [level.get("name", f"Level {i + 1}") for i, level in enumerate(self.project.get("levels", []))]
        self.level_combo["values"] = names
        if names:
            self.level_combo.set(names[self.level_index if self.level_index < len(names) else 0])
            self.level_name_var.set(current.get("name", "Level 1") if current else "Level 1")

    def _select_level(self, idx):
        levels = self.project.get("levels", [])
        if not levels:
            return
        self.level_index = max(0, min(int(idx), len(levels) - 1))
        self.selected_segment_index = 0
        self._apply_project_to_form()

    def _add_level(self):
        levels = self.project.get("levels", [])
        new_name = f"Level {len(levels) + 1}"
        levels.append({"name": new_name, "theme": self.project.get("theme", "sunset"), "segments": []})
        self.project["levels"] = levels
        self.level_index = len(levels) - 1
        self.selected_segment_index = 0
        self._refresh_level_list()
        self._sync_selected_segment_controls()
        self._render_segments()
        self._refresh_timeline()

    def _delete_level(self):
        levels = self.project.get("levels", [])
        if len(levels) <= 1:
            return
        del levels[self.level_index]
        self.level_index = max(0, min(self.level_index, len(levels) - 1))
        self.project["levels"] = levels
        self.selected_segment_index = 0
        self._refresh_level_list()
        self._sync_selected_segment_controls()
        self._render_segments()
        self._refresh_timeline()

    def _rename_current_level(self):
        level = self._current_level()
        if not level:
            return
        name = self.level_name_var.get().strip()
        if not name:
            name = f"Level {self.level_index + 1}"
        level["name"] = name
        self._refresh_level_list()
        self._refresh_timeline()

    def _apply_project_to_form(self):
        for key, entry in self.entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, str(self.project.get(key, "")))
        current = self._current_level()
        if current:
            current_theme = current.get("theme", self.project.get("theme", "sunset"))
            self.project["theme"] = current_theme
            self.entries["theme"].delete(0, tk.END)
            self.entries["theme"].insert(0, current_theme)
        self._sync_selected_segment_controls()
        self._render_segments()
        self._refresh_timeline()

    def _load_demo_project(self):
        self.project = json.loads(json.dumps(DEFAULT_PROJECT))
        self.level_index = 0
        self.selected_segment_index = 0
        self._apply_project_to_form()
        self._refresh_level_list()
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
        data["levels"] = self.project.get("levels", [])
        return data

    def _refresh_timeline(self):
        for row in self.timeline_tree.get_children():
            self.timeline_tree.delete(row)

        level = self._current_level()
        segments = level.get("segments", []) if level else []
        for idx, segment in enumerate(segments):
            self.timeline_tree.insert(
                "",
                "end",
                iid=str(idx),
                values=(
                    segment.get("time", idx),
                    segment.get("type", "empty"),
                    segment.get("label", ""),
                    segment.get("pattern", ""),
                ),
            )

        if segments:
            self.timeline_tree.selection_set(str(self.selected_segment_index))

    def _on_timeline_select(self, event):
        selection = self.timeline_tree.selection()
        if not selection:
            return
        idx = int(selection[0])
        level = self._current_level()
        segments = level.get("segments", []) if level else []
        if 0 <= idx < len(segments):
            self.selected_segment_index = idx
            self._sync_selected_segment_controls()
            self._render_segments()

    def _sync_selected_segment_controls(self):
        level = self._current_level()
        segments = level.get("segments", []) if level else []
        if not segments:
            self.segment_type_var.set("empty")
            self.segment_label_var.set("")
            self.segment_time_var.set("0")
            self.segment_pattern_var.set("")
            return

        if 0 <= self.selected_segment_index < len(segments):
            segment = segments[self.selected_segment_index]
            self.segment_type_var.set(segment.get("type", "empty"))
            self.segment_label_var.set(segment.get("label", ""))
            self.segment_time_var.set(str(segment.get("time", 0)))
            self.segment_pattern_var.set(segment.get("pattern", ""))
        else:
            self.selected_segment_index = 0
            segment = segments[0]
            self.segment_type_var.set(segment.get("type", "empty"))
            self.segment_label_var.set(segment.get("label", ""))
            self.segment_time_var.set(str(segment.get("time", 0)))
            self.segment_pattern_var.set(segment.get("pattern", ""))

    def _render_segments(self):
        self.segment_canvas.delete("all")
        level = self._current_level()
        segments = level.get("segments", []) if level else []
        if not segments:
            segments = [{"time": 0, "type": "empty", "label": "", "pattern": ""}]

        x_step = 52
        width = max(50, len(segments) * x_step)
        self.segment_canvas.config(width=max(430, width), height=160)

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
            label = segment.get("label") or (segment.get("type", "")[:1].upper() if segment.get("type") else "")
            self.segment_canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text=label, font=("Arial", 11, "bold"))
            self.segment_canvas.create_text((x0 + x1) / 2, y1 + 18, text=f"{segment.get('time', idx)}", font=("Arial", 8))

            if idx == self.selected_segment_index:
                self.segment_canvas.create_rectangle(x0 - 4, y0 - 4, x1 + 4, y1 + 4, outline="#1f77b4", width=3)

        self.segment_canvas.bind("<Button-1>", self._click_segment)

    def _click_segment(self, event):
        level = self._current_level()
        segments = level.get("segments", []) if level else []
        if not segments:
            return
        index = int((event.x - 20) // 52)
        if 0 <= index < len(segments):
            self.selected_segment_index = index
            self._sync_selected_segment_controls()
            self._render_segments()
            self._refresh_timeline()

    def _apply_selected_segment(self):
        level = self._current_level()
        if not level:
            return
        segments = level.get("segments", [])
        if not segments or not (0 <= self.selected_segment_index < len(segments)):
            return

        segment = segments[self.selected_segment_index]
        segment["type"] = self.segment_type_var.get() or "empty"
        try:
            segment["time"] = int(self.segment_time_var.get().strip())
        except ValueError:
            segment["time"] = self.selected_segment_index
        segment["label"] = self.segment_label_var.get().strip() or {
            "empty": "",
            "enemy": f"E{self.selected_segment_index + 1}",
            "pickup": "P",
            "boss": "B",
        }.get(segment["type"], "")
        segment["pattern"] = self.segment_pattern_var.get().strip() or "generic"

        level["segments"] = segments
        self._render_segments()
        self._refresh_timeline()

    def _add_segment(self, segment_type: str):
        level = self._current_level()
        if not level:
            return
        segments = level.get("segments", [])
        new_index = len(segments)
        segment = {
            "time": new_index,
            "type": segment_type,
            "label": {
                "empty": "",
                "enemy": f"E{new_index + 1}",
                "pickup": "P",
                "boss": "B",
            }.get(segment_type, ""),
            "pattern": "generic" if segment_type != "empty" else "",
        }
        segments.append(segment)
        level["segments"] = segments
        self.selected_segment_index = new_index
        self._sync_selected_segment_controls()
        self._render_segments()
        self._refresh_timeline()

    def _remove_selected_segment(self):
        level = self._current_level()
        if not level:
            return
        segments = level.get("segments", [])
        if not segments:
            return
        if 0 <= self.selected_segment_index < len(segments):
            del segments[self.selected_segment_index]
            level["segments"] = segments
            self.selected_segment_index = max(0, min(self.selected_segment_index, len(segments) - 1))
            self._sync_selected_segment_controls()
            self._render_segments()
            self._refresh_timeline()

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
