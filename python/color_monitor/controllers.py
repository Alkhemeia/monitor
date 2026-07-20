import time
import sys
import ctypes
from ctypes.util import find_library
import tkinter as tk
from tkinter import messagebox
import numpy as np
from PIL import ImageGrab, ImageTk, Image
CLICK_TYPE_MAP = {
    "left": "Linksklick",
    "right": "Rechtsklick",
    "double": "Doppelklick"
}
CLICK_TYPE_REV = {v: k for k, v in CLICK_TYPE_MAP.items()}

KEY_SYM_MAP = {
    "enter": 0xFF0D,
    "return": 0xFF0D,
    "tab": 0xFF09,
    "space": 0x0020,
    "backspace": 0xFF08,
    "escape": 0xFF1B,
    "f1": 0xFFBE,
    "f2": 0xFFBF,
    "f3": 0xFFC0,
    "f4": 0xFFC1,
    "f5": 0xFFC2,
    "f6": 0xFFC3,
    "f7": 0xFFC4,
    "f8": 0xFFC5,
    "f9": 0xFFC6,
    "f10": 0xFFC7,
    "f11": 0xFFC8,
    "f12": 0xFFC9,
    "up": 0xFF52,
    "down": 0xFF54,
    "left": 0xFF51,
    "right": 0xFF53,
    "pageup": 0xFF55,
    "pagedown": 0xFF56,
    "home": 0xFF50,
    "end": 0xFF57,
    "insert": 0xFF63,
    "delete": 0xFFFF,
    "ctrl": 0xFFE3,
    "shift": 0xFFE1,
    "alt": 0xFFE9,
    "meta": 0xFFEB,
    "super": 0xFFEB,
}

class X11MouseController:
    """Simulates mouse movements, clicks, and keyboard events using standard X11 and Xtest libraries via ctypes on Linux."""
    def __init__(self):
        self.display = None
        self.x11 = None
        self.xtst = None
        
        try:
            x11_path = find_library("X11")
            xtst_path = find_library("Xtst")
            if x11_path and xtst_path:
                self.x11 = ctypes.CDLL(x11_path)
                self.xtst = ctypes.CDLL(xtst_path)
                
                # Define signatures
                self.x11.XOpenDisplay.restype = ctypes.c_void_p
                self.x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
                
                self.display = self.x11.XOpenDisplay(None)
                if not self.display:
                    print("Warnung: X-Display konnte nicht geöffnet werden.", file=sys.stderr)
                    
                self.xtst.XTestFakeMotionEvent.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_ulong]
                self.xtst.XTestFakeMotionEvent.restype = ctypes.c_int
                
                self.xtst.XTestFakeButtonEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_bool, ctypes.c_ulong]
                self.xtst.XTestFakeButtonEvent.restype = ctypes.c_int

                # Keyboard signatures
                self.x11.XKeysymToKeycode.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
                self.x11.XKeysymToKeycode.restype = ctypes.c_uint
                
                self.xtst.XTestFakeKeyEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_bool, ctypes.c_ulong]
                self.xtst.XTestFakeKeyEvent.restype = ctypes.c_int
            else:
                print("Warnung: X11- oder Xtst-Bibliotheken wurden auf diesem System nicht gefunden.", file=sys.stderr)
        except Exception as e:
            print(f"X11MouseController Fehler bei der Initialisierung: {e}", file=sys.stderr)

    def move_to(self, x, y):
        if self.display and self.xtst:
            self.xtst.XTestFakeMotionEvent(self.display, -1, int(x), int(y), 0)
            self.x11.XFlush(self.display)

    def click(self, button=1, double=False):
        if self.display and self.xtst:
            if double:
                # First click
                self.xtst.XTestFakeButtonEvent(self.display, button, True, 0)
                self.xtst.XTestFakeButtonEvent(self.display, button, False, 0)
                # Small natural delay
                time.sleep(0.08)
                # Second click
                self.xtst.XTestFakeButtonEvent(self.display, button, True, 0)
                self.xtst.XTestFakeButtonEvent(self.display, button, False, 0)
            else:
                self.xtst.XTestFakeButtonEvent(self.display, button, True, 0)
                self.xtst.XTestFakeButtonEvent(self.display, button, False, 0)
            self.x11.XFlush(self.display)

    def key_combo(self, combo_str):
        if not self.display or not self.xtst or not self.x11:
            return False
        parts = [p.strip().lower() for p in combo_str.split("+")]
        keycodes = []
        for p in parts:
            keysym = KEY_SYM_MAP.get(p)
            if keysym is None and len(p) == 1:
                keysym = ord(p)
            if keysym is not None:
                keycode = self.x11.XKeysymToKeycode(self.display, keysym)
                if keycode != 0:
                    keycodes.append(keycode)
                    
        if not keycodes:
            return False
            
        # Press all keys in sequence
        for kc in keycodes:
            self.xtst.XTestFakeKeyEvent(self.display, kc, True, 0)
        # Release all keys in reverse sequence
        for kc in reversed(keycodes):
            self.xtst.XTestFakeKeyEvent(self.display, kc, False, 0)
            
        self.x11.XFlush(self.display)
        return True

    def type_text(self, text):
        if not self.display or not self.xtst or not self.x11:
            return
        shift_keycode = self.x11.XKeysymToKeycode(self.display, KEY_SYM_MAP["shift"])
        for char in text:
            is_upper = char.isupper()
            keysym = ord(char.lower())
            keycode = self.x11.XKeysymToKeycode(self.display, keysym)
            if keycode == 0:
                continue
                
            if is_upper:
                self.xtst.XTestFakeKeyEvent(self.display, shift_keycode, True, 0)
            
            self.xtst.XTestFakeKeyEvent(self.display, keycode, True, 0)
            self.xtst.XTestFakeKeyEvent(self.display, keycode, False, 0)
            
            if is_upper:
                self.xtst.XTestFakeKeyEvent(self.display, shift_keycode, False, 0)
                
        self.x11.XFlush(self.display)

    def close(self):
        if self.display and self.x11:
            try:
                self.x11.XCloseDisplay(self.display)
            except Exception:
                pass
            self.display = None


class WindowsMouseController:
    """Simulates mouse movements, clicks, and keyboard events using the Windows user32 API via ctypes."""
    def __init__(self):
        pass

    def move_to(self, x, y):
        try:
            ctypes.windll.user32.SetCursorPos(int(x), int(y))
        except Exception as e:
            print(f"Windows SetCursorPos Fehler: {e}", file=sys.stderr)

    def click(self, button=1, double=False):
        try:
            # Map buttons: 1=left, 2=middle, 3=right
            if button == 1:
                down_flag = 0x0002 # MOUSEEVENTF_LEFTDOWN
                up_flag = 0x0004   # MOUSEEVENTF_LEFTUP
            elif button == 3:
                down_flag = 0x0008 # MOUSEEVENTF_RIGHTDOWN
                up_flag = 0x0010   # MOUSEEVENTF_RIGHTUP
            else:
                down_flag = 0x0020 # MOUSEEVENTF_MIDDLEDOWN
                up_flag = 0x0040   # MOUSEEVENTF_MIDDLEUP

            if double:
                ctypes.windll.user32.mouse_event(down_flag, 0, 0, 0, 0)
                ctypes.windll.user32.mouse_event(up_flag, 0, 0, 0, 0)
                time.sleep(0.08)
                ctypes.windll.user32.mouse_event(down_flag, 0, 0, 0, 0)
                ctypes.windll.user32.mouse_event(up_flag, 0, 0, 0, 0)
            else:
                ctypes.windll.user32.mouse_event(down_flag, 0, 0, 0, 0)
                ctypes.windll.user32.mouse_event(up_flag, 0, 0, 0, 0)
        except Exception as e:
            print(f"Windows mouse_event Fehler: {e}", file=sys.stderr)

    def key_combo(self, combo_str):
        parts = [p.strip().lower() for p in combo_str.split("+")]
        vk_codes = []
        vk_map = {
            "enter": 0x0D, "return": 0x0D, "tab": 0x09, "space": 0x20,
            "backspace": 0x08, "escape": 0x1B,
            "f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73, "f5": 0x74,
            "f6": 0x75, "f7": 0x76, "f8": 0x77, "f9": 0x78, "f10": 0x79,
            "f11": 0x7A, "f12": 0x7B,
            "up": 0x26, "down": 0x28, "left": 0x25, "right": 0x27,
            "pageup": 0x21, "pagedown": 0x22, "home": 0x24, "end": 0x23,
            "insert": 0x2D, "delete": 0x2E,
            "ctrl": 0x11, "shift": 0x10, "alt": 0x12
        }
        for p in parts:
            vk = vk_map.get(p)
            if vk is None and len(p) == 1:
                vk = ord(p.upper())
            if vk is not None:
                vk_codes.append(vk)
        if not vk_codes:
            return False
        try:
            for vk in vk_codes:
                ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
            for vk in reversed(vk_codes):
                ctypes.windll.user32.keybd_event(vk, 0, 0x0002, 0) # KEYEVENTF_KEYUP
            return True
        except Exception as e:
            print(f"Windows keybd_event combo Fehler: {e}", file=sys.stderr)
            return False

    def type_text(self, text):
        try:
            for char in text:
                res = ctypes.windll.user32.VkKeyScanW(ord(char))
                if res == -1:
                    continue
                vk = res & 0xFF
                shift_state = (res >> 8) & 0xFF
                use_shift = (shift_state & 1) != 0
                
                if use_shift:
                    ctypes.windll.user32.keybd_event(0x10, 0, 0, 0)
                    
                ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
                ctypes.windll.user32.keybd_event(vk, 0, 0x0002, 0)
                
                if use_shift:
                    ctypes.windll.user32.keybd_event(0x10, 0, 0x0002, 0)
        except Exception as e:
            print(f"Windows type_text Fehler: {e}", file=sys.stderr)

    def close(self):
        pass


class RegionSelector:
    """Full-screen overlay that captures a screenshot and allows clicking and dragging to select a region."""
    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback
        
        # Take full screen screenshot
        try:
            self.screenshot = ImageGrab.grab()
        except Exception as e:
            messagebox.showerror(self.t("error") if hasattr(self, "t") else "Fehler", (self.t("screenshot_error") if hasattr(self, "t") else "Screenshot konnte nicht erstellt werden:\n{}").format(str(e)))
            self.callback(None, None, None, None)
            return
            
        self.screen_w, self.screen_h = self.screenshot.size
        
        # Create full screen overlay window
        self.overlay = tk.Toplevel(parent)
        self.overlay.title("Bereich auswählen")
        self.overlay.attributes("-fullscreen", True)
        self.overlay.attributes("-topmost", True)
        
        # Display the screenshot on canvas
        self.canvas_image = ImageTk.PhotoImage(self.screenshot)
        self.canvas = tk.Canvas(self.overlay, width=self.screen_w, height=self.screen_h, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, anchor="nw", image=self.canvas_image)
        
        self.rect_id = None
        self.start_x = None
        self.start_y = None
        
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.overlay.bind("<Escape>", self.cancel)
        self.overlay.focus_force()
        
        # Instruction label at the top
        self.instruction_frame = tk.Frame(self.overlay, bg="#11111b", bd=2, relief="ridge")
        self.instruction_frame.place(relx=0.5, y=30, anchor="n")
        lbl = tk.Label(self.instruction_frame, text="Ziehen Sie mit der Maus einen Bereich auf. ESC zum Abbrechen.", 
                       font=("Helvetica", 12, "bold"), fg="#cdd6f4", bg="#11111b", padx=15, pady=8)
        lbl.pack()

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        # Draw initial selection rectangle
        self.rect_id = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, 
                                                    outline="#f38ba8", width=2, dash=(4, 4))

    def on_drag(self, event):
        cur_x, cur_y = event.x, event.y
        self.canvas.coords(self.rect_id, self.start_x, self.start_y, cur_x, cur_y)

    def on_release(self, event):
        end_x, end_y = event.x, event.y
        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)
        
        if (x2 - x1) > 2 and (y2 - y1) > 2:
            self.close()
            self.callback(x1, y1, x2, y2)
        else:
            self.cancel()

    def cancel(self, event=None):
        self.close()
        self.callback(None, None, None, None)

    def close(self):
        self.overlay.destroy()
class PixelSelector:
    """Full-screen overlay that captures a screenshot and allows clicking to select a single pixel with coordinates and magnification preview."""
    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback
        
        try:
            self.screenshot = ImageGrab.grab()
        except Exception as e:
            messagebox.showerror(self.t("error") if hasattr(self, "t") else "Fehler", (self.t("screenshot_error") if hasattr(self, "t") else "Screenshot konnte nicht erstellt werden:\n{}").format(str(e)))
            self.callback(None, None)
            return
            
        self.screen_w, self.screen_h = self.screenshot.size
        self.screenshot_np = np.array(self.screenshot)
        
        # Create full screen overlay window
        self.overlay = tk.Toplevel(parent)
        self.overlay.title("Pixel auswählen")
        self.overlay.attributes("-fullscreen", True)
        self.overlay.attributes("-topmost", True)
        
        # Display the screenshot on canvas
        self.canvas_image = ImageTk.PhotoImage(self.screenshot)
        self.canvas = tk.Canvas(self.overlay, width=self.screen_w, height=self.screen_h, highlightthickness=0, cursor="crosshair")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, anchor="nw", image=self.canvas_image)
        
        # Floating coordinates tooltip
        self.tooltip = tk.Toplevel(self.overlay)
        self.tooltip.overrideredirect(True)
        self.tooltip.attributes("-topmost", True)
        
        self.tooltip_frame = tk.Frame(self.tooltip, bg="#11111b", bd=2, relief="solid")
        self.tooltip_frame.pack()
        
        # Magnifier glass canvas
        self.magnifier_canvas = tk.Canvas(self.tooltip_frame, width=80, height=80, bg="black", highlightthickness=0)
        self.magnifier_canvas.pack(padx=5, pady=5)
        
        self.coord_label = tk.Label(self.tooltip_frame, text="X: 0\nY: 0", 
                                    font=("Consolas", 10, "bold"), fg="#cdd6f4", bg="#11111b", padx=10, pady=5)
        self.coord_label.pack()
        
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Button-1>", self.on_click)
        self.overlay.bind("<Escape>", self.cancel)
        self.overlay.focus_force()
        
        # Instruction label at the top
        self.instruction_frame = tk.Frame(self.overlay, bg="#11111b", bd=2, relief="ridge")
        self.instruction_frame.place(relx=0.5, y=30, anchor="n")
        lbl = tk.Label(self.instruction_frame, text="Klicken Sie auf einen Pixel auf dem Bildschirm. ESC zum Abbrechen.", 
                       font=("Helvetica", 12, "bold"), fg="#cdd6f4", bg="#11111b", padx=15, pady=8)
        lbl.pack()

    def on_mouse_move(self, event):
        x, y = event.x, event.y
        if x < 0 or x >= self.screen_w or y < 0 or y >= self.screen_h:
            return
            
        self.coord_label.config(text=f"X: {x}\nY: {y}")
        
        # Draw magnifier
        self.magnifier_canvas.delete("all")
        half_size = 4
        crop_x1 = max(0, x - half_size)
        crop_y1 = max(0, y - half_size)
        crop_x2 = min(self.screen_w, x + half_size + 1)
        crop_y2 = min(self.screen_h, y + half_size + 1)
        
        pixel_size = 8
        for j, cy in enumerate(range(crop_y1, crop_y2)):
            for i, cx in enumerate(range(crop_x1, crop_x2)):
                c_color = self.screenshot_np[cy, cx]
                c_r, c_g, c_b = c_color[0], c_color[1], c_color[2]
                c_hex = f"#{c_r:02x}{c_g:02x}{c_b:02x}"
                
                px1 = i * pixel_size
                py1 = j * pixel_size
                px2 = px1 + pixel_size
                py2 = py1 + pixel_size
                
                # Highlight center pixel
                if cx == x and cy == y:
                    self.magnifier_canvas.create_rectangle(px1, py1, px2, py2, fill=c_hex, outline="#f38ba8", width=1)
                else:
                    self.magnifier_canvas.create_rectangle(px1, py1, px2, py2, fill=c_hex, outline="#313244", width=0)
                    
        # Position tooltip slightly offset from cursor
        tx = x + 20
        ty = y + 20
        if tx + 100 > self.screen_w:
            tx = x - 100 - 20
        if ty + 130 > self.screen_h:
            ty = y - 130 - 20
            
        self.tooltip.geometry(f"+{tx}+{ty}")

    def on_click(self, event):
        self.close()
        self.callback(event.x, event.y)

    def cancel(self, event=None):
        self.close()
        self.callback(None, None)

    def close(self):
        try:
            self.tooltip.destroy()
        except:
            pass
        self.overlay.destroy()


class ColorPickerEyedropper:
    """Full-screen overlay that lets the user hover over the screen to preview and pick a color with a magnifier glass."""
    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback
        
        # Take full screen screenshot
        try:
            self.screenshot = ImageGrab.grab()
        except Exception as e:
            messagebox.showerror(self.t("error") if hasattr(self, "t") else "Fehler", (self.t("screenshot_error") if hasattr(self, "t") else "Screenshot konnte nicht erstellt werden:\n{}").format(str(e)))
            self.callback(None)
            return
            
        self.screen_w, self.screen_h = self.screenshot.size
        self.screenshot_np = np.array(self.screenshot)
        
        # Create full screen overlay
        self.overlay = tk.Toplevel(parent)
        self.overlay.title("Farbe abgreifen")
        self.overlay.attributes("-fullscreen", True)
        self.overlay.attributes("-topmost", True)
        
        self.canvas_image = ImageTk.PhotoImage(self.screenshot)
        self.canvas = tk.Canvas(self.overlay, width=self.screen_w, height=self.screen_h, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, anchor="nw", image=self.canvas_image)
        
        # Floating tooltip/preview window
        self.tooltip = tk.Toplevel(self.overlay)
        self.tooltip.overrideredirect(True)
        self.tooltip.attributes("-topmost", True)
        
        self.tooltip_frame = tk.Frame(self.tooltip, bg="#11111b", bd=2, relief="solid")
        self.tooltip_frame.pack()
        
        self.magnifier_canvas = tk.Canvas(self.tooltip_frame, width=80, height=80, bg="black", highlightthickness=0)
        self.magnifier_canvas.pack(padx=5, pady=5)
        
        self.color_text_label = tk.Label(self.tooltip_frame, text="RGB: (255, 255, 255)\nHEX: #FFFFFF", 
                                         font=("Consolas", 9), fg="#cdd6f4", bg="#11111b")
        self.color_text_label.pack(padx=5, pady=5)
        
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Button-1>", self.on_click)
        self.overlay.bind("<Escape>", self.cancel)
        self.overlay.focus_force()
        
        # Instruction label
        self.instruction_frame = tk.Frame(self.overlay, bg="#11111b", bd=2, relief="ridge")
        self.instruction_frame.place(relx=0.5, y=30, anchor="n")
        lbl = tk.Label(self.instruction_frame, text="Klicken Sie auf den Bildschirm, um eine Farbe abzugreifen. ESC zum Abbrechen.", 
                       font=("Helvetica", 12, "bold"), fg="#cdd6f4", bg="#11111b", padx=15, pady=8)
        lbl.pack()

    def on_mouse_move(self, event):
        x, y = event.x, event.y
        if x < 0 or x >= self.screen_w or y < 0 or y >= self.screen_h:
            return
            
        color = self.screenshot_np[y, x]
        r, g, b = color[0], color[1], color[2]
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        
        self.color_text_label.config(text=f"RGB: ({r}, {g}, {b})\nHEX: {hex_color}")
        
        # Draw magnifier
        self.magnifier_canvas.delete("all")
        half_size = 4
        crop_x1 = max(0, x - half_size)
        crop_y1 = max(0, y - half_size)
        crop_x2 = min(self.screen_w, x + half_size + 1)
        crop_y2 = min(self.screen_h, y + half_size + 1)
        
        pixel_size = 8
        for j, cy in enumerate(range(crop_y1, crop_y2)):
            for i, cx in enumerate(range(crop_x1, crop_x2)):
                c_color = self.screenshot_np[cy, cx]
                c_r, c_g, c_b = c_color[0], c_color[1], c_color[2]
                c_hex = f"#{c_r:02x}{c_g:02x}{c_b:02x}"
                
                px1 = i * pixel_size
                py1 = j * pixel_size
                px2 = px1 + pixel_size
                py2 = py1 + pixel_size
                
                if cx == x and cy == y:
                    self.magnifier_canvas.create_rectangle(px1, py1, px2, py2, fill=c_hex, outline="#f38ba8", width=1)
                else:
                    self.magnifier_canvas.create_rectangle(px1, py1, px2, py2, fill=c_hex, outline="#313244", width=0)
                    
        # Position tooltip
        offset_x = 20
        offset_y = 20
        tx = x + offset_x
        ty = y + offset_y
        if tx + 120 > self.screen_w:
            tx = x - 120 - offset_x
        if ty + 150 > self.screen_h:
            ty = y - 150 - offset_y
            
        self.tooltip.geometry(f"+{tx}+{ty}")

    def on_click(self, event):
        x, y = event.x, event.y
        if 0 <= x < self.screen_w and 0 <= y < self.screen_h:
            color = self.screenshot_np[y, x]
            r, g, b = int(color[0]), int(color[1]), int(color[2])
            self.close()
            self.callback((r, g, b))
        else:
            self.close()

    def cancel(self, event=None):
        self.close()
        self.callback(None)

    def close(self):
        self.tooltip.destroy()
        self.overlay.destroy()


class PositionPicker:
    """Full-screen overlay that captures a screenshot and allows clicking to pick screen coordinates (X, Y)."""
    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback
        
        # Take full screen screenshot
        try:
            self.screenshot = ImageGrab.grab()
        except Exception as e:
            messagebox.showerror(self.t("error") if hasattr(self, "t") else "Fehler", (self.t("screenshot_error") if hasattr(self, "t") else "Screenshot konnte nicht erstellt werden:\n{}").format(str(e)))
            self.parent.deiconify()
            return
            
        self.screen_w, self.screen_h = self.screenshot.size
        
        # Create full screen overlay window
        self.overlay = tk.Toplevel(parent)
        self.overlay.title("Position abgreifen")
        self.overlay.attributes("-fullscreen", True)
        self.overlay.attributes("-topmost", True)
        
        # Display screenshot
        self.canvas_image = ImageTk.PhotoImage(self.screenshot)
        self.canvas = tk.Canvas(self.overlay, width=self.screen_w, height=self.screen_h, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, anchor="nw", image=self.canvas_image)
        
        # Floating coordinates tooltip
        self.tooltip = tk.Toplevel(self.overlay)
        self.tooltip.overrideredirect(True)
        self.tooltip.attributes("-topmost", True)
        
        self.tooltip_frame = tk.Frame(self.tooltip, bg="#11111b", bd=2, relief="solid")
        self.tooltip_frame.pack()
        
        self.coord_label = tk.Label(self.tooltip_frame, text="X: 0\nY: 0", 
                                    font=("Consolas", 10, "bold"), fg="#cdd6f4", bg="#11111b", padx=10, pady=5)
        self.coord_label.pack()
        
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Button-1>", self.on_click)
        self.overlay.bind("<Escape>", self.cancel)
        self.overlay.focus_force()
        
        # Instruction label
        self.instruction_frame = tk.Frame(self.overlay, bg="#11111b", bd=2, relief="ridge")
        self.instruction_frame.place(relx=0.5, y=30, anchor="n")
        lbl = tk.Label(self.instruction_frame, text="Klicken Sie auf den Bildschirm, um die Position abzugreifen. ESC zum Abbrechen.", 
                       font=("Helvetica", 12, "bold"), fg="#cdd6f4", bg="#11111b", padx=15, pady=8)
        lbl.pack()

    def on_mouse_move(self, event):
        x, y = event.x, event.y
        self.coord_label.config(text=f"X: {x}\nY: {y}")
        
        offset = 15
        tx = x + offset
        ty = y + offset
        if tx + 80 > self.screen_w:
            tx = x - 90
        if ty + 50 > self.screen_h:
            ty = y - 60
        self.tooltip.geometry(f"+{tx}+{ty}")

    def on_click(self, event):
        self.close()
        self.callback(event.x, event.y)

    def cancel(self, event=None):
        self.close()
    def close(self):
        self.tooltip.destroy()
        self.overlay.destroy()


