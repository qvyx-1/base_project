# windows/__init__.py -- UI windows for NeoPulse Studio
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from desktop.windows.live_control import LiveControlWindow
from desktop.windows.project_manager import ProjectManagerWindow
from desktop.windows.setup_wizard import SetupWizardWindow
from desktop.windows.show_editor import ShowEditorWindow

__all__ = ["SetupWizardWindow", "ShowEditorWindow", "LiveControlWindow", "ProjectManagerWindow"]
