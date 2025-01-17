# Growtopia auto mod detector

Mod Detector

Mod Detector is an automation tool designed to assist with specific tasks in the game Growtopia. It automates user actions like mouse clicks and keyboard inputs while also monitoring the game screen for specific text messages to trigger automated responses.

This application allows players to AFK farm efficiently in Growtopia while reducing the risk of being banned. It continuously checks for the presence of moderators by scanning for specific in-game messages. If a moderator is detected, the tool tries to mimic non-AFK behavior by sending messages in the chat to make it appear as though the user is active. Afterward, it automatically closes the game, ensuring the user's account remains safe.

# Main Features
### 1.Automated Mouse Clicking and Keyboard Input:

The **numpad9_function()** automates mouse clicks at specific coordinates followed by pressing the **space** key.

This allows the program to perform repetitive tasks in the game automatically.

### 2.Dynamic Coordinate Adjustment:

Pressing the **G** key sets the current mouse position as the **x1, y1** coordinates.

Pressing the **H** key sets the current mouse position as the **x2, y2** coordinates.

This makes it easy to adjust the automation to new positions dynamically.

### 3.Screen Capture and Text Recognition:

The program takes periodic screenshots of the game screen and uses **Tesseract OCR** to recognize text.

If specific text (e.g., "You were pulled by") is detected, the program alerts the user and safely closes the game.

### 4.Hotkey Listener:

**K** Key: Starts the automated clicking process.

**L** Key: Stops the automated clicking process.

**J** Key: Displays the current mouse position.

**G** and **H** Keys: Set new coordinates for the automation.

### 5.Safe Game Closure:

The **growtopia_kapat()** function safely terminates the game by simulating specific keypresses before forcibly closing the application.

### 6.Modern and User-Friendly Interface:

Built with Tkinter, the GUI provides a clean and intuitive interface for managing the program.

Users can easily start, stop, and customize settings through the interface.

# How to Use
Ensure Required Libraries Are Installed:

Use the command pip install **-r requirements.txt** to install all necessary dependencies.

Run the Program:

Launch the program and use the GUI to control automation or hotkeys (G, H, K, L, and J) for quick adjustments.
Customize Settings:

Adjust mouse click coordinates and automation timing through the GUI's **Settings** button.

**Main Screen**

![Ekran görüntüsü 2025-01-06 214149](https://github.com/user-attachments/assets/2b1ec01f-f8ae-4644-9b80-721b628c0035)

**Settings**

![Ekran görüntüsü 2025-01-06 214157](https://github.com/user-attachments/assets/905e39e2-5746-491e-b91a-efea083ce26c)

**After Detecting a Mod**

![Ekran görüntüsü 2025-01-06 214657](https://github.com/user-attachments/assets/2bd9ce94-5794-4920-af0f-5b7bc725610f)

# Technical Details
Python Version: 3.12.5

Libraries Used:

Tkinter: For the graphical user interface.

PyAutoGUI: For mouse and keyboard automation.

Tesseract OCR: For text recognition from screenshots.

Pygetwindow: For managing and monitoring GUI windows.

OpenCV: For advanced image processing tasks.
