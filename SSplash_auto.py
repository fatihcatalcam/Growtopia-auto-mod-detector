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

# Modern renkler
BG_COLOR = "#282c34"
FG_COLOR = "#61dafb"
BUTTON_BG_COLOR = "#3e4451"  # Daha koyu bir renk
BUTTON_TEXT_COLOR = "#ffffff"  # Beyaz renk, okunabilirliği artırmak için
TEXT_COLOR = "#abb2bf"

def is_gui_running():
    """Check if the GUI is already running."""
    try:
        window_name = "Mod Dedektörü"
        windows = gw.getWindowsWithTitle(window_name)
        return len(windows) > 0
    except Exception as e:
        print(f"Error checking GUI status: {e}")
        return False

def get_file_paths():
    """Dinamik dosya yolu oluşturur."""
    base_path = os.path.expanduser('~\\Documents\\ModDedektoru')
    if not os.path.exists(base_path):
        os.makedirs(base_path, exist_ok=True)  # Belgeler dizininde klasör oluşturur
    screenshot_path = os.path.join(base_path, 'current_screenshot.png')
    return screenshot_path


def ekran_goruntusu_al():
    """Bütün ekranın ekran görüntüsünü alır."""
    ekran_goruntusu = pyautogui.screenshot()
    screenshot_path = get_file_paths()

    if not os.path.exists(os.path.dirname(screenshot_path)):
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)

    ekran_goruntusu.save(screenshot_path)
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
                print("GUI zaten açık.")
    except Exception as e:
        print(f"Failed to restart as admin: {e}")
        sys.exit(1)

def start_gui():
    """GUI'yi başlatır."""
    global root, log_text, mod_warning
    root = tk.Tk()
    root.title("Mod Dedektörü")

    # Modern tasarım
    root.configure(bg=BG_COLOR)
    root.geometry("600x400")
    root.resizable(True, True)

    # Pencereyi ortalamak için ekran boyutları
    window_width = 600
    window_height = 400
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Üst orta tarafa başlık
    header_label = tk.Label(root, text="SSplash Auto", font=("Arial", 24, "bold"), bg=BG_COLOR, fg=FG_COLOR)
    header_label.grid(row=0, column=0, columnspan=3, pady=(10, 20), sticky="n")

    # Büyük mod uyarısı
    mod_warning = tk.Label(root, text="", font=("Arial", 18), bg=BG_COLOR, fg="#ff5555")
    mod_warning.grid(row=1, column=0, columnspan=3, pady=10)

    # Butonlar
    start_button = tk.Button(root, text="Başlat", bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR, command=start_main_loop)
    start_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

    stop_button = tk.Button(root, text="Durdur", bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR, command=stop_script)
    stop_button.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

    settings_button = tk.Button(root, text="Ayarlar", bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR, command=open_numpad9_settings)
    settings_button.grid(row=2, column=2, padx=10, pady=10, sticky="ew")

    # Log penceresi
    log_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=10, state=tk.DISABLED, bg=BG_COLOR, fg=FG_COLOR)
    log_text.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

    # Grid yapısının ölçeklenebilir olması için ayar
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
                messagebox.showinfo("Durduruldu", "Script başarıyla durduruldu.")
                return
        messagebox.showwarning("Uyarı", "Script çalışmıyor.")
    except Exception as e:
        messagebox.showerror("Hata", f"Script durdurulamadı: {e}")

def preprocess_image(image_path):
    """Görüntüyü daha etkili şekilde ön işleme tabi tutar."""
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    alpha = 1.5
    beta = 0
    adjusted = cv2.convertScaleAbs(gray_image, alpha=alpha, beta=beta)
    blurred_image = cv2.GaussianBlur(adjusted, (5, 5), 0)
    _, binary_image = cv2.threshold(blurred_image, 150, 255, cv2.THRESH_BINARY)
    return Image.fromarray(binary_image)

def metin_tara(image_path):
    """Görüntüdeki metni tarar ve döndürür."""
    preprocessed_image = preprocess_image(image_path)
    metin = pytesseract.image_to_string(preprocessed_image, config='--psm 6')
    update_log(metin)
    return metin



def growtopia_kapat():
    """Growtopia uygulamasını kapatmadan önce belirli işlemleri yapar ve uygulamayı zorla kapatır."""
    try:
        # İlk olarak numpad9_function'u durdur
        global stop_flag
        stop_flag.set()
        print("numpad9_function durduruldu.")

        # Growtopia'nın kontrolünü sağlamak için tuş basımlarını gönder
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

        # Growtopia uygulamasını zorla kapat
        result = subprocess.run(["taskkill", "/IM", "Growtopia.exe", "/F"], capture_output=True, text=True)
        if result.returncode == 0:
            print("Growtopia başarıyla kapatıldı.")
        else:
            print(f"Growtopia kapatılamadı: {result.stderr}")
    except Exception as e:
        print(f"Growtopia kapatılırken bir hata oluştu: {e}")

def open_numpad9_settings():
    """numpad9_function ayarlarını değiştirmek için bir pencere açar."""
    def save_settings():
        """Yeni ayarları kaydeder."""
        try:
            x1 = int(entry_x1.get())
            y1 = int(entry_y1.get())
            x2 = int(entry_x2.get())
            y2 = int(entry_y2.get())
            sleep_time = float(entry_sleep.get())

            # Yeni değerleri global değişkenlere atar
            global click_x1, click_y1, click_x2, click_y2, numpad9_sleep
            click_x1, click_y1, click_x2, click_y2, numpad9_sleep = x1, y1, x2, y2, sleep_time

            print(f"Yeni ayarlar kaydedildi: x1={x1}, y1={y1}, x2={x2}, y2={y2}, sleep={sleep_time}")
            settings_window.destroy()
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli sayılar girin!")

    # Pencere oluştur
    settings_window = tk.Toplevel(root)
    settings_window.title("Ayarlar")
    settings_window.geometry("400x450")
    settings_window.configure(bg=BG_COLOR)

    # Etiket ve giriş alanları
    tk.Label(settings_window, text="x1:", bg=BG_COLOR, fg=FG_COLOR).pack(pady=5)
    entry_x1 = tk.Entry(settings_window)
    entry_x1.insert(0, click_x1)  # Varsayılan değeri göster
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

    # Kaydet butonu
    save_button = tk.Button(settings_window, text="Kaydet", bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR, command=save_settings)
    save_button.pack(pady=20)


# Varsayılan koordinatlar ve süre
click_x1, click_y1 = 709, 536
click_x2, click_y2 = 583, 536
numpad9_sleep = 1.6

def set_position_as_x1y1():
    """G tuşuna basıldığında fare konumunu x1, y1 olarak ayarlar."""
    global click_x1, click_y1
    mouse_position = pyautogui.position()
    click_x1, click_y1 = mouse_position.x, mouse_position.y
    print(f"x1, y1 yeni değerleri: {click_x1}, {click_y1}")

def set_position_as_x2y2():
    """H tuşuna basıldığında fare konumunu x2, y2 olarak ayarlar."""
    global click_x2, click_y2
    mouse_position = pyautogui.position()
    click_x2, click_y2 = mouse_position.x, mouse_position.y
    print(f"x2, y2 yeni değerleri: {click_x2}, {click_y2}")


def numpad9_function():
    """Simulate clicking behavior and pressing space."""
    print("Tıklama işlemi başladı.")
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
        print(f"Tıklama sırasında hata oluştu: {e}")
    print("Tıklama işlemi durduruldu.")


def mouse_position_window():
    """Mouse imlecinin konumunu gösteren bir pencere açar."""
    mouse_position = pyautogui.position()  # Mevcut mouse pozisyonunu al
    position_text = f"Mouse X: {mouse_position.x}, Mouse Y: {mouse_position.y}"

    # Yeni bir pencere oluştur
    position_window = tk.Toplevel()
    position_window.title("Mouse Konumu")
    position_window.geometry("300x200")
    position_window.configure(bg=BG_COLOR)

    # Konum bilgisini gösteren etiket
    position_label = tk.Label(position_window, text=position_text, font=("Arial", 14), bg=BG_COLOR, fg=FG_COLOR)
    position_label.pack(pady=20)

    # Pencereyi kapatmak için bir düğme
    close_button = tk.Button(position_window, text="Kapat", bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR,
                              command=position_window.destroy)
    close_button.pack(pady=10)
        

def listen_for_hotkeys():
    """Listen for hotkeys for K, L, and J."""
    print("Hotkey dinleyici başlatıldı.")
    numpad9_thread = None  # Referans için bir iş parçacığı

    while True:
        try:
            if keyboard.is_pressed('k'):  # K tuşu işlemi başlatır
                print("K tuşuna basıldı. İşlem başlatılıyor.")
                if not numpad9_thread or not numpad9_thread.is_alive():
                    global stop_flag
                    stop_flag.clear()
                    numpad9_thread = threading.Thread(target=numpad9_function, daemon=True)
                    numpad9_thread.start()
                time.sleep(0.5)
            elif keyboard.is_pressed('l'):  # L tuşu işlemi durdurur
                print("L tuşuna basıldı. İşlem durduruluyor.")
                stop_flag.set()
                if numpad9_thread and numpad9_thread.is_alive():
                    numpad9_thread.join()
                print("İşlem durduruldu.")
                time.sleep(0.5)
            elif keyboard.is_pressed('j'):  # J tuşu mouse pozisyonunu gösterir
                print("J tuşuna basıldı. Mouse konumu penceresi açılıyor.")
                mouse_position_window()
                time.sleep(0.5)  # Tetikleme süresini azalt
            elif keyboard.is_pressed('g'):  # G tuşu x1, y1 ayarlar
                print("G tuşuna basıldı. x1, y1 ayarlanıyor.")
                set_position_as_x1y1()
                time.sleep(0.5)
            elif keyboard.is_pressed('h'):  # H tuşu x2, y2 ayarlar
                print("H tuşuna basıldı. x2, y2 ayarlanıyor.")
                set_position_as_x2y2()
                time.sleep(0.5)
        except Exception as e:
            print(f"Hotkey dinlenirken bir hata oluştu: {e}")
        time.sleep(0.1)




def main_loop():
    """Ana döngü."""
    print("Mod dedektörü başlatıldı.")
    threading.Thread(target=listen_for_hotkeys, daemon=True).start()  # Hotkey dinleyici iş parçacığı
    while not stop_flag.is_set():
        try:
            ekran_goruntusu_yolu = ekran_goruntusu_al()
            metin = metin_tara(ekran_goruntusu_yolu)

            if "You were pulled by" in metin:
                mod_warning.config(text="Mod tarafından çekildiniz!")
                growtopia_kapat()
                break

            if keyboard.is_pressed('num 6'):
                stop_flag.set()
                break

            time.sleep(1)
        except Exception as e:
            print(f"Bir hata oluştu: {e}")
            break

def update_log(message):
    """Log penceresine mesaj ekler."""
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
