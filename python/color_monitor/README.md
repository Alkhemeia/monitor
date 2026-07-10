# Screen Color Monitor & Macro Runner

A visually premium desktop utility that monitors a specific region of the screen for color changes and executes a sequence of simulated actions (a macro) when triggers are met.

## Features

- **Select Screen Region**: Drag-and-drop overlay to define the monitored screen coordinates.
- **Color Picker Eyedropper**: Magnified color picker to capture exact pixel colors.
- **Multiple Trigger Modes**:
  - *Target color appears*: Alerts when the target color matches a specified percentage of pixels in the region.
  - *Target color disappears*: Alerts when the target color is no longer present.
  - *Target color present (continuous)*: Alerts continuously as long as the target color matches the region.
  - *Target color absent (continuous)*: Alerts continuously as long as the target color is absent from the region.
  - *General color change*: Alerts when pixels deviate from a baseline screenshot.
- **Editable Macro Flow**:
  - Define custom sequences of actions to execute in a separate background thread upon alarm.
  - Add, edit, remove, and reorder (move up/down) action lines.
  - Test the macro sequence in real-time with the **Makro testen** button.
- **Supported Macro Actions**:
  - **Warten (Wait)**: Pause execution for a specified duration in milliseconds.
  - **Mausklick (Mouse Click)**: Move the mouse to specific coordinates and perform a left, right, or double click.
  - **Position Picker**: Interactively select click coordinates from the screen using a full-screen overlay.
  - **Tastendruck (KeyPress / Shortcut)**: Simulate a key press or key combination (e.g. `f5`, `ctrl+c`, `enter`, `alt+tab`).
  - **Text eingeben (Type Text)**: Simulate typing a text string character-by-character.
  - **Alarm-Sound abspielen (Play Sound)**: Play a pleasant audio alert through system speakers using native tools.
  - **Ntfy-Push-Benachrichtigung (Remote Push)**: Send a push notification instantly to your smartphone or other devices via `ntfy.sh` (completely free, registration-free open-source service).
- **Profile Manager**: Create, save, load, and delete named configuration profiles (containing coordinates, settings, and macros) to switch between different tasks seamlessly.
- **Pixel Selector**: Focus on a single pixel instead of a large region using the dedicated **Pixel wählen** tool.
- **Multiple Zones Monitoring**: Monitor multiple distinct regions and/or single pixels concurrently. Configure each zone with its own coordinates, target color, mode, tolerance, and match percentage, and execute the automation macro when any zone triggers.
- **Zone Renaming & Reordering**: Custom rename any zone and change the zone order using the **🔼 Nach oben** and **🔽 Nach unten** reordering buttons.
- **Interactive Screen Overlay**: Toggle a red border overlay window that frames the monitored area on your screen in real time. Drag the borders to resize the monitored region, or hold `Shift` and drag the borders to pan (move) the entire region.
- **Dashboard Hotkeys**: Press `Space` to toggle monitoring and `Delete` to remove actions.
- **Pause & Resume Controls**: Pause the monitoring session at any time with the dedicated **Pause** button, freezing active macro execution and trigger evaluations while keeping the live preview running.
- **Clean Menu Bar**: Structured File, Monitoring, Zones, Options, and Help menus to declutter the user interface and access settings.
- **Always on Top Option**: Toggle the window to stay topmost, keeping it visible even when clicking other applications.
- **Window Geometry & Sash Restoring**: Automatically remembers the window position, size, and columns sash separator position inside the profile and startup config.
- **Unsaved Changes Prompt**: Checks if there are unsaved edits to the active profile on window closure and prompts the user to save, discard, or cancel.
- **Activity Log**: Live status updates and match statistics.

---

## 📋 Prerequisites

### 1. System Packages

* **Linux**:
  Since this is a GUI application using Tkinter and simulating input via X11 libraries, make sure the required system libraries are installed:
  ```bash
  sudo apt update
  sudo apt install python3-tk python3-pil.imagetk libxtst6 libx11-6
  ```
* **Windows**:
  Download and install Python 3.12+ from [python.org](https://www.python.org/). During installation, make sure to check the box for **"Add Python to PATH"**.

### 2. Python Dependencies
Install the required packages from `requirements.txt`:
```bash
pip install -r requirements.txt
```

---

## 🚀 Usage

Run the program from this directory:
```bash
python color_monitor.py
```

### Macro Setup:
1. Under **4. Auszuführendes Makro bei Alarm**, click **Hinzufügen** to add a new action.
2. Select **Warten** or **Mausklick**:
   * For **Mausklick**, click **Position vom Bildschirm abgreifen** to interactively click a spot on your desktop and capture its X/Y coordinates automatically.
3. Use **Hoch** (Move Up) / **Runter** (Move Down) to reorder actions.
4. Click **Makro testen** to run the macro immediately for testing.
5. Click **Überwachung STARTEN** to begin monitoring. When a trigger condition is met, your macro will execute in the background.
