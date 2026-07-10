# 🔍 Screen Color Monitor & Desktop Automation

A visually premium desktop utility that monitors specific regions of the screen for color changes and executes a sequence of simulated actions (a macro) when triggers are met.

---

## 🚀 Quick Start

You can launch the tool directly from the root directory:

* **Linux / macOS**:
  ```bash
  ./monitor.sh
  ```
* **Windows**:
  ```cmd
  monitor.bat
  ```

The startup scripts will automatically check for and install all required system and Python dependencies (such as Tkinter, Pillow, numpy, and X11 test libraries) before launching the application.

---

## 📂 Repository Structure

* **`python/color_monitor/`**: Contains the source code of the tool:
  * **`color_monitor.py`**: Main application entry point.
  * **`i18n.py`**: Localization dictionaries (EN, DE, ES, FR).
  * **`controllers.py`**: OS-specific mouse/keyboard simulation controllers.
  * **`widgets.py`**: UI components (ActionDialog, RegionOverlayBorder).
* **`monitor.sh`**: Launch and setup script for Linux/macOS.
* **`monitor.bat`**: Launch and setup script for Windows.
