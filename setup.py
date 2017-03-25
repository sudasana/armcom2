from distutils.core import setup
import py2exe, sys, os
import glob, shutil
import pygame
sys.argv.append('py2exe')

# constant defs
VERSION = 'Proof of Concept 2'
AUTHOR_NAME = 'Gregory Adam Scott'
AUTHOR_EMAIL = 'armouredcommander@gmail.com'
AUTHOR_URL = 'http://www.armouredcommander.com'
PRODUCT_NAME = 'Armoured Commander II'
SCRIPT_MAIN = 'armcom2.py'
VERSIONSTRING = PRODUCT_NAME + VERSION
#ICONFILE = 'icon.ico'

REMOVE_BUILD_ON_EXIT = False				# remove build tree on exit

PYGAMEDIR = os.path.split(pygame.base.__file__)[0]

DLLS = ['libtcod-mingw.dll', 'python27.dll', 'SDL.dll']

if os.path.exists('dist/'): shutil.rmtree('dist/')	# remove last dist dir

extra_files = [ ("",['readme.txt', 'gpl.txt']),
	("data",glob.glob(os.path.join('data','c64_12x12.png'))),
	("data",glob.glob(os.path.join('data','c64_16x16.png'))),
	("data",glob.glob(os.path.join('data','*.xml'))),
	("data",glob.glob(os.path.join('data','*.xp'))),
]

# list of modules to exclude from dist
MODULE_EXCLUDES = [
	'email', 'AppKit', 'Foundation', 'bdb', 'difflib', 'tcl', 'Tkinter', 'Tkconstants',
	'curses', 'distutils', 'setuptools', 'urllib',
	'BaseHTTPServer', '_LWPCookieJar', '_MozillaCookieJar', 'ftplib', 'gopherlib',
	'_ssl', 'htmllib', 'mimetypes', 'tty', 'webbrowser', 'compiler', 'pydoc'
]

INCLUDE_STUFF = ['encodings',"encodings.latin_1"]

#hack which fixes the pygame mixer and pygame font
origIsSystemDLL = py2exe.build_exe.isSystemDLL	# save the orginal before we edit it
def isSystemDLL(pathname):
    # checks if the freetype and ogg dll files are being included
    if os.path.basename(pathname).lower() in ("libogg-0.dll"):
            return 0
    return origIsSystemDLL(pathname)		# return the orginal function
py2exe.build_exe.isSystemDLL = isSystemDLL	# override the default function with this one

setup(windows = [
	{'script': SCRIPT_MAIN,
	'other_resources': [(u"VERSIONTAG",1,VERSIONSTRING)]
#	'icon_resources': [(1,ICONFILE)]
	}],
	options = {"py2exe": {
		"optimize": 2,
		"includes": INCLUDE_STUFF,
		"compressed": 1,
		"ascii": 1,
		"bundle_files": 2,
		"ignores": ['tcl','AppKit','Numeric','Foundation'],
		"excludes": MODULE_EXCLUDES} },
	name = PRODUCT_NAME,
	version = VERSION,
	data_files = extra_files,
	zipfile = None,
	author = AUTHOR_NAME,
	author_email = AUTHOR_EMAIL,
	url = AUTHOR_URL)

# clean up
if os.path.exists('dist/tcl'): shutil.rmtree('dist/tcl')
if REMOVE_BUILD_ON_EXIT: shutil.rmtree('build/')
if os.path.exists('dist/tcl84.dll'): os.unlink('dist/tcl84.dll')
if os.path.exists('dist/tk84.dll'): os.unlink('dist/tk84.dll')

# copy over required DLLs
for f in DLLS:
	fname = os.path.basename(f)
	try:
		shutil.copyfile(f,os.path.join('dist',fname))
	except: pass

# copy over source files
#os.mkdir('dist/src')
#SOURCEFILES = ['armcom2.py', 'setup.py', 'xp_loader.py', 'LICENSE_xp_loader.txt', 'gpl.txt', 'icon.ico']
#for filename in SOURCEFILES:
#	shutil.copyfile(filename, 'dist/src/'+filename)

