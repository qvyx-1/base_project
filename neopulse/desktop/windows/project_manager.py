"""Project Manager window for NeoPulse Studio."""
import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class ProjectManagerWindow(tk.Toplevel):
    """Manage NeoPulse project files (.npulse format)."""

    def __init__(self, parent):
        super().__init__(parent)

        self.title("NeoPulse — Projekt-Manager")
        self.geometry("600x500")

        self.transient(parent)
        self.grab_set()

        self.projects = []
        self._load_projects()

        self._build_ui()
        self._refresh_list()

    def _build_ui(self):
        """Build the project manager UI."""
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Toolbar
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(toolbar, text="+ Neues Projekt", command=self._new_project).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📂 Öffnen", command=self._open_project).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="💾 Speichern", command=self._save_project).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🗑 Löschen", command=self._delete_project).pack(side=tk.LEFT, padx=2)

        # Project list
        list_frame = ttk.LabelFrame(main_frame, text="Projekte", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("name", "shows", "modified")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="tree headings", height=12)

        self.tree.heading("#0", text="Name")
        self.tree.heading("shows", text="Shows")
        self.tree.heading("modified", text="Geändert")

        self.tree.column("#0", width=250)
        self.tree.column("shows", width=80)
        self.tree.column("modified", width=150)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", self._on_double_click)

        # Project info
        info_frame = ttk.LabelFrame(main_frame, text="Projekt-Details", padding=10)
        info_frame.pack(fill=tk.X, pady=(10, 0))

        self.info_text = tk.Text(info_frame, height=6, font=("Courier", 9), state="disabled")
        info_scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=info_scrollbar.set)

        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _load_projects(self):
        """Load project list from config."""
        config_path = os.path.expanduser("~/.config/neopulse/projects.json")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)

        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    self.projects = json.load(f)
            except:
                self.projects = []

    def _save_projects(self):
        """Save project list to config."""
        config_path = os.path.expanduser("~/.config/neopulse/projects.json")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)

        with open(config_path, "w") as f:
            json.dump(self.projects, f, indent=2)

    def _refresh_list(self):
        """Refresh the project list display."""
        self.tree.delete(*self.tree.get_children())

        for proj in self.projects:
            self.tree.insert("", tk.END, text=proj["name"],
                           values=(proj["name"], len(proj.get("shows", [])),
                                  proj.get("modified", "Nie")))

    def _new_project(self):
        """Create a new project."""
        dialog = tk.Toplevel(self)
        dialog.title("Neues Projekt")
        dialog.geometry("350x200")

        ttk.Label(dialog, text="Projektname:").pack(pady=(10, 5))
        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var).pack(pady=5)

        ttk.Label(dialog, text="Speicherort:").pack(pady=(5, 0))
        path_var = tk.StringVar(value=os.path.expanduser("~/neopulse_projects"))
        ttk.Entry(dialog, textvariable=path_var).pack(fill=tk.X, padx=20, pady=5)

        ttk.Button(dialog, text="Ordner wählen", command=lambda: path_var.set(filedialog.askdirectory())).pack(pady=(0, 5))

        def confirm():
            name = name_var.get()
            if not name:
                return

            project = {
                "name": name,
                "path": path_var.get(),
                "shows": [],
                "modified": "Nie",
            }

            self.projects.append(project)
            self._save_projects()
            self._refresh_list()
            dialog.destroy()

        ttk.Button(dialog, text="Erstellen", command=confirm).pack(pady=(10, 5))

    def _open_project(self):
        """Open a project."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie ein Projekt aus.")
            return

        idx = self.tree.index(selection[0])
        proj = self.projects[idx]

        # Try to load project file
        project_file = os.path.join(proj["path"], f'{proj["name"]}.npulse')
        if os.path.exists(project_file):
            with open(project_file, "r") as f:
                data = json.load(f)

            # Return data to parent for loading into editor
            self.destroy()
            return data

        messagebox.showinfo("Info", f'Projekt "{proj["name"]}" wird geöffnet.\nPfad: {proj["path"]}')

    def _save_project(self):
        """Save current project."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie ein Projekt aus.")
            return

        idx = self.tree.index(selection[0])
        proj = self.projects[idx]

        # Save project file
        project_file = os.path.join(proj["path"], f'{proj["name"]}.npulse')
        os.makedirs(proj["path"], exist_ok=True)

        with open(project_file, "w") as f:
            json.dump(proj, f, indent=2)

        messagebox.showinfo("Erfolg", f'Projekt "{proj["name"]}" gespeichert.')

    def _delete_project(self):
        """Delete selected project."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie ein Projekt aus.")
            return

        idx = self.tree.index(selection[0])
        proj = self.projects[idx]

        if messagebox.askyesno("Bestätigung", f'Projekt "{proj["name"]}" wirklich löschen?'):
            # Try to delete project folder
            try:
                import shutil
                if os.path.exists(proj["path"]):
                    shutil.rmtree(proj["path"], ignore_errors=True)
            except:
                pass

            self.projects.pop(idx)
            self._save_projects()
            self._refresh_list()

    def _on_select(self, event):
        """Show project details on selection."""
        selection = self.tree.selection()
        if not selection:
            return

        idx = self.tree.index(selection[0])
        proj = self.projects[idx]

        self.info_text.config(state="normal")
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, f'Name: {proj["name"]}\nPfad: {proj["path"]}\nShows: {len(proj.get("shows", []))}\nGeändert: {proj.get("modified", "Nie")}')
        self.info_text.config(state="disabled")

    def _on_double_click(self, event):
        """Open project on double click."""
        self._open_project()
