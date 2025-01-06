import tkinter as tk
from tkinter import messagebox, scrolledtext
import subprocess
import sys
import os
import ctypes
import psutil
import pyautogui
import pytesseract
from PIL import Image
import cv2
import time
import keyboard
import threading
import pygetwindow as gw

# Global flag to signal stop
stop_flag = threading.Event()
main_thread = None  # Global reference to the main thread

# Modern colors
BG_COLOR = "#282c34"
FG_COLOR = "#61dafb"
BUTTON_BG_COLOR = "#3e4451"  # Darker color
BUTTON_TEXT_COLOR = "#ffffff"  # White for better readability
TEXT_COLOR = "#abb2bf"

def is_gui_running():
    """Check if the GUI is already running."""
    try:
        window_name = "Mod Detector"
        windows = gw.getWindowsWithTitle(window_name)
        return len(windows) > 0
    except Exception as e:
        print(f"Error checking GUI status: {e}")
        return False

def get_file_paths():
    """Generate dynamic file paths."""
    base_path = os.path.expanduser('~\\Documents\\ModDetector')
    if not os.path.exists(base_path):
        os.makedirs(base_path, exist_ok=True)  # Create folder in Documents
    screenshot_path = os.path.join(base_path, 'current_screenshot.png')
    return screenshot_path

def take_screenshot():
    """Take a screenshot of the entire screen."""
    screenshot = pyautogui.screenshot()
    screenshot_path = get_file_paths()

    if not os.path.exists(os.path.dirname(screenshot_path)):
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)

    screenshot.save(screenshot_path)
    return screenshot_path

def is_admin():
    """Check if the script is running with administrative privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        print(f"Error checking admin status: {e}")
        return False

def run_as_admin():
    """Relaunch the script with administrative privileges."""
    try:
        if not is_admin():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{sys.argv[0]}"', None, 1)
            sys.exit(0)
        else:
            if not is_gui_running():
                start_gui()
            else:
                print("GUI is already running.")
    except Exception as e:
        print(f"Failed to restart as admin: {e}")
        sys.exit(1)

def start_gui():
    """Start the GUI."""
    global root, log_text, mod_warning
    root = tk.Tk()
    root.title("Mod Detector")

    # Modern design
    root.configure(bg=BG_COLOR)
    root.geometry("600x400")
    root.resizable(True, True)

    # Center the window on the screen
    window_width = 600
    window_height = 400
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Header label at the top center
    header_label = tk.Label(root, text="SSplash Auto", font=("Arial", 24, "bold"), bg=BG_COLOR, fg=FG_COLOR)
    header_label.grid(row=0, column=0, columnspan=3, pady=(10, 20), sticky="n")

    # Large mod warning
    mod_warning = tk.Label(root, text="", font=("Arial", 18), bg=BG_COLOR, fg="#ff5555")
    mod_warning.grid(row=1, column=0, columnspan=3, pady=10)

    # Buttons
    start_button = tk.Button(root, text="Start", bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR, command=start_main_loop)
    start_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

    stop_button = tk.Button(root, text="Stop", bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR, command=stop_script)
    stop_button.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

    settings_button = tk.Button(root, text="Settings", bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR, command=open_numpad9_settings)
    settings_button.grid(row=2, column=2, padx=10, pady=10, sticky="ew")

    # Log window
    log_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=10, state=tk.DISABLED, bg=BG_COLOR, fg=FG_COLOR)
    log_text.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

    # Make grid resizable
    root.grid_rowconfigure(3, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    root.grid_columnconfigure(2, weight=1)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

def start_main_loop():
    """Start the main loop in a separate thread."""
    global stop_flag, main_thread
    stop_flag.clear()
    main_thread = threading.Thread(target=main_loop, daemon=True)
    main_thread.start()

def stop_script():
    """Stop the script."""
    global stop_flag, main_thread
    stop_flag.set()
    try:
        if main_thread and main_thread.is_alive():
            main_thread.join(timeout=5)
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'python.exe' and proc.pid != os.getpid():
                proc.terminate()
                messagebox.showinfo("Stopped", "Script successfully stopped.")
                return
        messagebox.showwarning("Warning", "Script is not running.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to stop the script: {e}")

def preprocess_image(image_path):
    """Preprocess the image for better text recognition."""
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    alpha = 1.5
    beta = 0
    adjusted = cv2.convertScaleAbs(gray_image, alpha=alpha, beta=beta)
    blurred_image = cv2.GaussianBlur(adjusted, (5, 5), 0)
    _, binary_image = cv2.threshold(blurred_image, 150, 255, cv2.THRESH_BINARY)
    return Image.fromarray(binary_image)

def scan_text(image_path):
    """Scan and return text from the image."""
    preprocessed_image = preprocess_image(image_path)
    text = pytesseract.image_to_string(preprocessed_image, config='--psm 6')
    update_log(text)
    return text

def close_growtopia():
    """Perform specific actions before forcefully closing Growtopia."""
    try:
        global stop_flag
        stop_flag.set()
        print("numpad9_function stopped.")

        pyautogui.press('space')
        time.sleep(0.1)
        pyautogui.press('space')
        time.sleep(0.1)
        pyautogui.press('enter')
        time.sleep(0.1)
        pyautogui.press('y')
        time.sleep(0.1)
        pyautogui.press('o')
        time.sleep(0.1)
        pyautogui.press('enter')
        time.sleep(0.5)

        result = subprocess.run(["taskkill", "/IM", "Growtopia.exe", "/F"], capture_output=True, text=True)
        if result.returncode == 0:
            print("Growtopia closed successfully.")
        else:
            print(f"Failed to close Growtopia: {result.stderr}")
    except Exception as e:
        print(f"Error closing Growtopia: {e}")

def open_numpad9_settings():
    """Open a window to modify numpad9_function settings."""
    def save_settings():
        """Save new settings."""
        try:
            x1 = int(entry_x1.get())
            y1 = int(entry_y1.get())
            x2 = int(entry_x2.get())
            y2 = int(entry_y2.get())
            sleep_time = float(entry_sleep.get())

            # Assign new values to global variables
            global click_x1, click_y1, click_x2, click_y2, numpad9_sleep
            click_x1, click_y1, click_x2, click_y2, numpad9_sleep = x1, y1, x2, y2, sleep_time

            print(f"New settings saved: x1={x1}, y1={y1}, x2={x2}, y2={y2}, sleep={sleep_time}")
            settings_window.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers!")

    # Create the settings window
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("400x450")
    settings_window.configure(bg=BG_COLOR)

    # Labels and entry fields
    tk.Label(settings_window, text="x1:", bg=BG_COLOR, fg=FG_COLOR).pack(pady=5)
    entry_x1 = tk.Entry(settings_window)
    entry_x1.insert(0, click_x1)  # Display the default value
    entry_x1.pack()

    tk.Label(settings_window, text="y1:", bg=BG_COLOR, fg=FG_COLOR).pack(pady=5)
    entry_y1 = tk.Entry(settings_window)
    entry_y1.insert(0, click_y1)
    entry_y1.pack()

    tk.Label(settings_window, text="x2:", bg=BG_COLOR, fg=FG_COLOR).pack(pady=5)
    entry_x2 = tk.Entry(settings_window)
    entry_x2.insert(0, click_x2)
    entry_x2.pack()

    tk.Label(settings_window, text="y2:", bg=BG_COLOR, fg=FG_COLOR).pack(pady=5)
    entry_y2 = tk.Entry(settings_window)
    entry_y2.insert(0, click_y2)
    entry_y2.pack()

    tk.Label(settings_window, text="Sleep Time:", bg=BG_COLOR, fg=FG_COLOR).pack(pady=5)
    entry_sleep = tk.Entry(settings_window)
    entry_sleep.insert(0, numpad9_sleep)
    entry_sleep.pack()

    # Save button
    save_button = tk.Button(settings_window, text="Save", bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR, command=save_settings)
    save_button.pack(pady=20)


# Default coordinates and sleep time
click_x1, click_y1 = 709, 536
click_x2, click_y2 = 583, 536
numpad9_sleep = 1.6

def set_position_as_x1y1():
    """Set the current mouse position as x1, y1 when 'G' is pressed."""
    global click_x1, click_y1
    mouse_position = pyautogui.position()
    click_x1, click_y1 = mouse_position.x, mouse_position.y
    print(f"New x1, y1 values: {click_x1}, {click_y1}")

def set_position_as_x2y2():
    """Set the current mouse position as x2, y2 when 'H' is pressed."""
    global click_x2, click_y2
    mouse_position = pyautogui.position()
    click_x2, click_y2 = mouse_position.x, mouse_position.y
    print(f"New x2, y2 values: {click_x2}, {click_y2}")

def numpad9_function():
    """Simulate clicking behavior and pressing space."""
    print("Clicking process started.")
    try:
        while not stop_flag.is_set():
            pyautogui.click(click_x1, click_y1)
            time.sleep(0.02)
            pyautogui.click(click_x1, click_y1)
            time.sleep(0.02)
            pyautogui.click(click_x2, click_y2)
            time.sleep(0.02)
            pyautogui.click(click_x2, click_y2)
            time.sleep(0.02)
            pyautogui.keyDown('space')
            time.sleep(numpad9_sleep)
            pyautogui.keyUp('space')
    except Exception as e:
        print(f"Error during clicking: {e}")
    print("Clicking process stopped.")

def mouse_position_window():
    """Open a window displaying the current mouse position."""
    mouse_position = pyautogui.position()  # Get current mouse position
    position_text = f"Mouse X: {mouse_position.x}, Mouse Y: {mouse_position.y}"

    # Create a new window
    position_window = tk.Toplevel()
    position_window.title("Mouse Position")
    position_window.geometry("300x200")
    position_window.configure(bg=BG_COLOR)

    # Display mouse position
    position_label = tk.Label(position_window, text=position_text, font=("Arial", 14), bg=BG_COLOR, fg=FG_COLOR)
    position_label.pack(pady=20)

    # Close button
    close_button = tk.Button(position_window, text="Close", bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                              command=position_window.destroy)
    close_button.pack(pady=10)

def listen_for_hotkeys():
    """Listen for hotkeys for K, L, G, H, and J."""
    print("Hotkey listener started.")
    numpad9_thread = None  # Reference for the thread

    while True:
        try:
            if keyboard.is_pressed('k'):  # Start process on 'K'
                print("Key 'K' pressed. Starting process.")
                if not numpad9_thread or not numpad9_thread.is_alive():
                    global stop_flag
                    stop_flag.clear()
                    numpad9_thread = threading.Thread(target=numpad9_function, daemon=True)
                    numpad9_thread.start()
                time.sleep(0.5)
            elif keyboard.is_pressed('l'):  # Stop process on 'L'
                print("Key 'L' pressed. Stopping process.")
                stop_flag.set()
                if numpad9_thread and numpad9_thread.is_alive():
                    numpad9_thread.join()
                print("Process stopped.")
                time.sleep(0.5)
            elif keyboard.is_pressed('j'):  # Show mouse position window on 'J'
                print("Key 'J' pressed. Opening mouse position window.")
                mouse_position_window()
                time.sleep(0.5)
            elif keyboard.is_pressed('g'):  # Set x1, y1 on 'G'
                print("Key 'G' pressed. Setting x1, y1.")
                set_position_as_x1y1()
                time.sleep(0.5)
            elif keyboard.is_pressed('h'):  # Set x2, y2 on 'H'
                print("Key 'H' pressed. Setting x2, y2.")
                set_position_as_x2y2()
                time.sleep(0.5)
        except Exception as e:
            print(f"Error listening for hotkeys: {e}")
        time.sleep(0.1)

def main_loop():
    """Main loop."""
    print("Mod detector started.")
    threading.Thread(target=listen_for_hotkeys, daemon=True).start()  # Start hotkey listener
    while not stop_flag.is_set():
        try:
            screenshot_path = take_screenshot()
            text = scan_text(screenshot_path)

            if "You were pulled by" in text:
                mod_warning.config(text="You were pulled by a mod!")
                close_growtopia()
                break

            if keyboard.is_pressed('num 6'):
                stop_flag.set()
                break

            time.sleep(1)
        except Exception as e:
            print(f"Error in main loop: {e}")
            break

def update_log(message):
    """Add a message to the log window."""
    log_text.config(state=tk.NORMAL)
    log_text.insert(tk.END, message + "\n")
    log_text.yview(tk.END)
    log_text.config(state=tk.DISABLED)

def on_closing():
    """Handle the window closing event."""
    stop_flag.set()
    if main_thread and main_thread.is_alive():
        main_thread.join(timeout=5)
    root.destroy()

if __name__ == "__main__":
    run_as_admin()

