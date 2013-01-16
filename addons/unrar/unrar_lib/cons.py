# -*- coding: utf-8 -*-
__author__ = 'Esteban Castro Borsani'


SUCCESS = 0 #Success

#Errors
ERAR_END_ARCHIVE = 10 #End of archive
ERAR_NO_MEMORY = 11 #Not enough memory to initialize data structures
ERAR_BAD_DATA = 12 #Archive header broken
ERAR_BAD_ARCHIVE = 13 #File is not valid RAR archive
ERAR_UNKNOWN_FORMAT = 14 #Unknown encryption used for archive headers
ERAR_EOPEN = 15 #Archive/Volume open error
ERAR_ECREATE = 16 #File create error
ERAR_ECLOSE = 17 #Archive/File close error
ERAR_EREAD = 18 #Read error
ERAR_EWRITE = 19 #Write error
ERAR_SMALL_BUF = 20 #Buffer too small, comments not completely read
ERAR_UNKNOWN = 21 #Unknown error
ERAR_MISSING_PASSWORD = 22 #Missing password error

#Open Modes
RAR_OM_LIST = 0 #headers only
RAR_OM_EXTRACT = 1 #testing and extracting
RAR_OM_LIST_INCSPLIT = 2 #headers only, include splitted volumes

#Process file operations
RAR_SKIP = 0 #Move to the next file in the archive.
RAR_TEST = 1 #Test the current file and move to the next file in the archive.
RAR_EXTRACT = 2 #Extract the current file and move to the next file in the archive.
RAR_CANCEL_EXTRACT = -1 #return -1 from Callback to cancel

#Process volume change.
RAR_VOL_CHANGE = 0
RAR_VOL_ASK = 0 #Required volume is absent.
RAR_VOL_NOTIFY = 1 #Required volume is successfully opened.

UCM_NEEDPASSWORD = 2

#?
RAR_DLL_VERSION = 5
