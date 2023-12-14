import tkinter as tk
from tkinter import ttk
import pyperclip
import pyautogui
import time
from pynput.mouse import Listener
from PIL import ImageGrab
import pytesseract
import easyocr
import re
import os

tesseract_path = 'C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Tesseract-OCR'
os.environ['TESSDATA_PREFIX'] = tesseract_path

   
class ClickRecorder:
    def __init__(self, notebook):
        self.clicks = []
        self.recording = False
        self.mouse_listener = None
        self.text_box = None
        self.input_text_box = None
        self.notebook = notebook

    def create_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='AutoClicks_REC')
        
        button_frame = tk.Frame(tab)
        button_frame.pack()

        self.start_button = tk.Button(button_frame, text='Start Recording', command=self.start_recording, bg='#4CAF50', fg='white', font=('Arial', 14))
        self.start_button.pack(side="left")

        self.stop_button = tk.Button(button_frame, text='Stop Recording', command=self.stop_recording, bg='#F44336', fg='white', font=('Arial', 14))
        self.stop_button.pack(side="left")

        self.replay_button = tk.Button(button_frame, text='Replay Clicks', command=self.replay_clicks, bg='#2196F3', fg='white', font=('Arial', 14))
        self.replay_button.pack(side="left")

        self.clear_button = tk.Button(button_frame, text='Clear Clicks', command=self.clear_recorded_clicks, bg='#FF9800', fg='white', font=('Arial', 14))
        self.clear_button.pack(side="bottom")

        self.input_text_box = tk.Text(tab, height=10, width=50, bg='white', fg='black', font=('Arial', 14))
        self.input_text_box.pack(side="top")

        separator = tk.Frame(tab, height=2, bd=1, relief=tk.SUNKEN)
        separator.pack(fill=tk.X, padx=10, pady=5)

        self.text_box = tk.Text(tab, height=7, width=30, bg='black', fg='white', font=('Arial', 12), state=tk.DISABLED)
        self.text_box.pack(side="bottom", padx=(10, 0), fill=tk.BOTH, expand=True)
        
    def start_recording(self):
        self.recording = True
        self.clicks = []
        self.mouse_listener = Listener(on_click=self.on_mouse_event)
        self.mouse_listener.start()
        self.notebook.winfo_toplevel().iconify()

    def stop_recording(self):
        self.recording = False

        if self.mouse_listener:
            self.mouse_listener.stop()

        self.text_box.config(state=tk.NORMAL)
        self.text_box.delete(1.0, tk.END)

        for click in self.clicks:
            position_str = f"Recorded click at ({click[0]}, {click[1]})\n"
            self.text_box.insert(tk.END, position_str)

        self.display_message("INSERT NUMBERS ABOVE DUDE")  # Display the message
        self.text_box.config(state=tk.DISABLED)
        self.input_text_box.config(state=tk.NORMAL)
        self.input_text_box.delete(1.0, tk.END)

    def replay_clicks(self):
        if not self.recording:
            input_text = self.input_text_box.get("1.0", tk.END).strip().split("\n")
            input_text = [num.strip() for num in input_text if num.strip()]  # Remove empty lines

            # Exclude the last two clicks from replay
            clicks_to_replay = self.clicks[:-1]

            # Clear the status textbox before displaying new status
            self.text_box.config(state=tk.NORMAL)

            for number in input_text:
                paste_flag = False  # Flag to control pasting behavior
                for i, click in enumerate(clicks_to_replay):
                    pyautogui.click(click[0], click[1])
                    time.sleep(0.2)

                    if i == 1:
                        paste_flag = True

                    if paste_flag:
                        pyperclip.copy(number)  # Copy the number to the clipboard
                        pyautogui.hotkey("ctrl", "v")  # Paste the number
                        time.sleep(2)

                        status_message = f"Pasted number {number} at ({click[0]}, {click[1]})\n"
                        self.text_box.insert(tk.END, status_message)
                        self.text_box.yview(tk.END)
                        self.text_box.update()

                        paste_flag = False

            self.text_box.insert(tk.END, "Replay completed.\n")
            self.text_box.yview(tk.END)
            self.text_box.config(state=tk.DISABLED)

    def on_mouse_event(self, x, y, button, pressed):
        if self.recording and pressed:
            if not self.is_inside_window(x, y):
                position = (x, y)
                self.clicks.append(position)

    def display_message(self, message):
        self.text_box.config(state=tk.NORMAL)
        self.text_box.insert(tk.END, message + "\n")
        self.text_box.config(state=tk.DISABLED)

    def is_inside_window(self, x, y):
        window_x = self.notebook.winfo_x()
        window_y = self.notebook.winfo_y()
        window_width = self.notebook.winfo_width()
        window_height = self.notebook.winfo_height()

        if window_x <= x <= window_x + window_width and window_y <= y <= window_y + window_height:
            return True
        else:
            return False

    def clear_recorded_clicks(self):
        self.clicks = []
        self.text_box.config(state=tk.NORMAL)
        self.text_box.delete(1.0, tk.END)
        self.text_box.config(state=tk.DISABLED)

class NumberFetcher:
    def __init__(self, notebook):
        self.text_box = None
        self.selection_window = None
        self.ocr_reader = easyocr.Reader(['en', 'it'], gpu=False)  # 'en' for English, 'it' for Italian
        self.scanning_mode = False  # Flag to enable scanning mode
        self.notebook = notebook

    def create_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='IMG2TXT')

        button_frame = tk.Frame(tab)
        button_frame.pack(side="left")
        
        tote_button = tk.Button(button_frame, text="Tote", command=self.extract_18_digit_numbers, width=10, height=2, bg="green")
        tote_button.pack(side="top")

        scan_button = tk.Button(button_frame, text="Scan", command=self.start_scanning, width=10, height=2, bg="orange")
        scan_button.pack(side="top")

        handwritten_button = tk.Button(button_frame, text="Handwritten", command=self.recognize_handwritten_numbers, width=10, height=2, bg="purple")
        handwritten_button.pack(side="top")
        
        clear_button = tk.Button(button_frame, text="Clear", command=self.clear_text_box, width=10, height=2, bg="blue")
        clear_button.pack(side="top")

        self.text_box = tk.Text(tab, height=20, width=40, bg='white', fg='black', font=('Arial', 14))
        self.text_box.pack()

    def start_scanning(self):
        self.scanning_mode = True

        # Hide the main window
        self.notebook.winfo_toplevel().iconify()

        # Create a transparent selection window
        self.selection_window = tk.Toplevel(self.notebook.winfo_toplevel())
        self.selection_window.attributes("-fullscreen", True)
        self.selection_window.attributes("-alpha", 0.2)  # Set transparency

        # Create a canvas for region selection
        self.canvas = tk.Canvas(self.selection_window, bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)

    def on_mouse_press(self, event):
        self.start_x = self.selection_window.winfo_pointerx() - self.selection_window.winfo_rootx()
        self.start_y = self.selection_window.winfo_pointery() - self.selection_window.winfo_rooty()

    def on_mouse_drag(self, event):
        x = self.selection_window.winfo_pointerx() - self.selection_window.winfo_rootx()
        y = self.selection_window.winfo_pointery() - self.selection_window.winfo_rooty()

        self.canvas.delete("rect")
        self.canvas.create_rectangle(self.start_x, self.start_y, x, y, outline="white", width=3, tags="rect")

    def on_mouse_release(self, event):
        x = self.selection_window.winfo_pointerx() - self.selection_window.winfo_rootx()
        y = self.selection_window.winfo_pointery() - self.selection_window.winfo_rooty()

        self.canvas.delete("rect")

        screenshot = ImageGrab.grab(bbox=(self.start_x, self.start_y, x, y))

        if self.scanning_mode:
            text = pytesseract.image_to_string(screenshot, lang='eng+ita', config='--psm 6')
            self.text_box.delete('1.0', tk.END)
            self.text_box.insert(tk.END, text)

        # Close the selection window
        self.selection_window.destroy()

        # Show the main window
        self.notebook.winfo_toplevel().update()
        self.notebook.winfo_toplevel().deiconify()

    def recognize_handwritten_numbers(self):
        self.start_scanning()  # Enable scanning mode for "Handwritten" as well

    def clear_text_box(self):
        self.text_box.delete('1.0', tk.END)
        
    def extract_18_digit_numbers(self):
        if self.scanning_mode:
        # Capture the entire screen
            screenshot = ImageGrab.grab()

        # Perform OCR on the captured screenshot using Google's Tesseract
            text = pytesseract.image_to_string(screenshot, lang='eng')

        # Extract 18-digit numbers using regular expressions
            extracted_numbers = re.findall(r'\d{18}', text)

        # Display the extracted numbers in the text box
            extracted_text = '\n'.join(extracted_numbers)
            self.text_box.delete('1.0', tk.END)
            self.text_box.insert(tk.END, extracted_text)

            self.scanning_mode = False  # Turn off scanning mode


def main():
    root = tk.Tk()
    root.title("RB-Tool")
    
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)
    
    recorder = ClickRecorder(notebook)
    recorder.create_tab()
    
    fetcher = NumberFetcher(notebook)
    fetcher.create_tab()
    
    root.mainloop()

if __name__ == '__main__':
    main()

