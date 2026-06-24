"""Scene tree widget for NeoPulse Studio."""

import tkinter as tk
from tkinter import ttk


class SceneTreeWidget(ttk.Frame):
    """Tree view widget for managing scenes in a show."""

    def __init__(self, parent, on_scene_select=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_scene_select = on_scene_select
        self.scenes = []
        self.selected_idx = -1

        # Treeview for scene hierarchy
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("name", "duration", "keyframes")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="tree headings", height=15)

        self.tree.heading("#0", text="Szene")
        self.tree.heading("duration", text="Dauer")
        self.tree.heading("keyframes", text="Keyframes")

        self.tree.column("#0", width=150)
        self.tree.column("duration", width=60)
        self.tree.column("keyframes", width=60)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind selection
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.bind("<Double-1>", self.on_double_click)

    def set_scenes(self, scenes):
        """Update the tree with a list of scenes."""
        self.scenes = scenes
        self.tree.delete(*self.tree.get_children())

        for idx, scene in enumerate(scenes):
            name = scene.get("name", f"Szene {idx + 1}")
            duration = f"{scene.get('duration', 10):.1f}s"
            kfs = len(scene.get("keyframes", []))

            self.tree.insert(
                "", tk.END, text=name, values=(name, duration, kfs), tags=(idx,), iid=str(idx)
            )

        if scenes:
            self.tree.selection_set(str(0))
            self.selected_idx = 0

    def on_select(self, event):
        """Handle scene selection."""
        selected = self.tree.selection()
        if selected:
            idx = int(selected[0])
            self.selected_idx = idx
            if self.on_scene_select:
                self.on_scene_select(idx, self.scenes[idx] if idx < len(self.scenes) else None)

    def on_double_click(self, event):
        """Handle double click - could open scene editor."""
        selected = self.tree.selection()
        if selected:
            idx = int(selected[0])
            if self.on_scene_select:
                self.on_scene_select(
                    idx, self.scenes[idx] if idx < len(self.scenes) else None, edit=True
                )

    def get_selected_scene(self):
        """Get the currently selected scene."""
        if 0 <= self.selected_idx < len(self.scenes):
            return self.scenes[self.selected_idx]
        return None

    def add_scene(self, scene_data):
        """Add a new scene to the tree."""
        idx = len(self.scenes)
        self.scenes.append(scene_data)
        name = scene_data.get("name", f"Szene {idx + 1}")
        duration = f"{scene_data.get('duration', 10):.1f}s"
        kfs = len(scene_data.get("keyframes", []))

        self.tree.insert(
            "", tk.END, text=name, values=(name, duration, kfs), tags=(idx,), iid=str(idx)
        )
        self.tree.selection_set(str(idx))
        self.selected_idx = idx

    def remove_scene(self, idx):
        """Remove a scene from the tree."""
        if 0 <= idx < len(self.scenes):
            self.tree.delete(str(idx))
            self.scenes.pop(idx)
            # Rebuild tree
            self.set_scenes(self.scenes)

    def update_scene(self, idx, data):
        """Update a scene in the tree."""
        if 0 <= idx < len(self.scenes):
            self.scenes[idx].update(data)
            name = data.get("name", self.scenes[idx].get("name"))
            duration = f"{data.get('duration', self.scenes[idx].get('duration', 10)):.1f}s"
            kfs = len(data.get("keyframes", self.scenes[idx].get("keyframes", [])))
            self.tree.item(str(idx), text=name, values=(name, duration, kfs))
