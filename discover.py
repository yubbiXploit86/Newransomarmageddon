import os
import fnmatch
import win32api
import win32con
import win32file
import ctypes
from pathlib import Path

def discoverFiles(startpath):
    """
    Recursively discover all files in the given path and subdirectories.
    This function now finds ALL files without exception.
    """
    file_list = []
    
    # Convert to absolute path
    startpath = os.path.abspath(startpath)
    
    # Check if path exists
    if not os.path.exists(startpath):
        return file_list
    
    # Walk through all directories
    for root, dirs, files in os.walk(startpath, topdown=True, followlinks=True):
        # Don't skip any directories - include everything
        # Remove any access restrictions
        try:
            # Process all files
            for file in files:
                try:
                    full_path = os.path.join(root, file)
                    
                    # Skip if it's a junction point or symlink? No - include everything
                    if os.path.exists(full_path):
                        file_list.append(full_path)
                except:
                    # If can't access individual file, try next
                    continue
        except:
            # If can't access directory, try next
            continue
    
    return file_list

def discoverFiles_brutal(startpath):
    """
    Ultra brutal file discovery - finds EVERYTHING including system files
    """
    file_list = []
    
    # Get all drives on Windows
    if os.name == 'nt':
        drives = [d for d in win32api.GetLogicalDriveStrings().split('\x00') if d]
        for drive in drives:
            try:
                file_list.extend(discoverFiles(drive))
            except:
                continue
    else:
        # Linux - include all mount points
        try:
            with open('/proc/mounts', 'r') as f:
                mounts = f.readlines()
                for mount in mounts:
                    parts = mount.split()
                    if len(parts) > 1:
                        try:
                            file_list.extend(discoverFiles(parts[1]))
                        except:
                            continue
        except:
            file_list.extend(discoverFiles('/'))
            file_list.extend(discoverFiles('/home'))
            file_list.extend(discoverFiles('/root'))
            file_list.extend(discoverFiles('/etc'))
            file_list.extend(discoverFiles('/var'))
            file_list.extend(discoverFiles('/usr'))
            file_list.extend(discoverFiles('/boot'))
    
    return file_list

def get_all_drives():
    """Get all available drives including network drives"""
    drives = []
    
    if os.name == 'nt':
        # Get all logical drives
        drive_bitmask = win32api.GetLogicalDrives()
        for letter in range(26):
            if drive_bitmask & (1 << letter):
                drive = chr(65 + letter) + ':\\'
                drives.append(drive)
        
        # Get network drives
        try:
            import subprocess
            result = subprocess.run('net use', shell=True, capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for line in lines:
                if '\\\\' in line:
                    parts = line.split()
                    for part in parts:
                        if '\\\\' in part:
                            drives.append(part)
                            break
        except:
            pass
    else:
        # Linux drives
        drives = ['/', '/home', '/root', '/etc', '/var', '/usr', '/boot', '/mnt', '/media']
        # Add mounted drives
        try:
            with open('/proc/mounts', 'r') as f:
                for line in f:
                    parts = line.split()
                    if len(parts) > 1 and parts[1] not in drives:
                        drives.append(parts[1])
        except:
            pass
    
    return drives

def discover_all_files():
    """Discover ALL files on the system without exception"""
    all_files = []
    drives = get_all_drives()
    
    for drive in drives:
        try:
            files = discoverFiles(drive)
            all_files.extend(files)
        except:
            continue
    
    return all_files

# Override the original function to be more aggressive
discoverFiles = discover_all_files
