# -*- coding: utf-8 -*-
__author__ = 'Esteban Castro Borsani'

import sys
import os
from ctypes import *
from ctypes.util import find_library

import cons
from exceptions_ import *

if 'win32' in sys.platform.lower():
    lib_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "lib", "unrar.dll")
    unrarlib = WinDLL(lib_path)
    func_type = WINFUNCTYPE
else: #Unix
    lib_path = find_library("libunrar") or os.path.join(os.path.abspath(os.path.dirname(__file__)), "lib", "libunrar.so")
    unrarlib = cdll.LoadLibrary(lib_path)
    func_type = CFUNCTYPE


RARCALLBACK = func_type(c_int, c_uint, c_long, c_long, c_long)


class RAROpenArchiveDataEx(Structure):
    _fields_ = [("ArcName", c_char_p),
                ("ArcNameW", c_wchar_p),
                ("OpenMode", c_uint),
                ("OpenResult", c_uint),
                ("CmtBuf", c_char_p), #may crash on linux when extracting first file
                ("CmtBufSize", c_uint),
                ("CmtSize", c_uint),
                ("CmtState", c_uint),
                ("Flags", c_uint),
                ("Callback", RARCALLBACK),
                ("UserData", c_long), #LPARAM x86
                ("Reserved", c_uint * 28)
                ]

    def __init__(self, filename, mode, password=None):
        #CmtBuf saves rar file comment
        Structure.__init__(self)
        self.ArcName = None
        self.ArcNameW = filename
        self.OpenMode = mode
        self.Callback = RARCALLBACK(self._rar_callback)
        self.password = password
        self.password_flag = False
        self.missing_volume_flag = False

    def _rar_callback(self, msg, user_data, p1, p2):
        if msg == cons.UCM_NEEDPASSWORD:
            self.password_flag = True
            if self.password:
                (c_char*p2).from_address(p1).value = self.password
            else:
                return -1
        elif msg == cons.RAR_VOL_CHANGE and p2 == cons.RAR_VOL_ASK:
            self.missing_volume_flag = True
            return -1
        return 0

    @property
    def open_result(self):
        return self.OpenResult

    @property
    def password_required(self):
        return self.password_flag

    @property
    def missing_volume(self):
        return self.missing_volume_flag


class RARHeaderDataEx(Structure):
    _fields_ = [("ArcName", c_char * 1024),
                ("ArcNameW", c_wchar * 1024),
                ("FileName", c_char * 1024),
                ("FileNameW", c_wchar * 1024),
                ("Flags", c_uint),
                ("PackSize", c_uint),
                ("PackSizeHigh", c_uint),
                ("UnpSize", c_uint),
                ("UnpSizeHigh", c_uint),
                ("HostOS", c_uint),
                ("FileCRC", c_uint),
                ("FileTime", c_uint),
                ("UnpVer", c_uint),
                ("Method", c_uint),
                ("FileAttr", c_uint),
                ("CmtBuf", c_char_p),
                ("CmtBufSize", c_uint),
                ("CmtSize", c_uint),
                ("CmtState", c_uint),
                ("Reserved", c_uint * 1024)
                ]

    @property
    def file_name(self):
        return self.FileNameW


def _c_func(func, restype, argtypes, errcheck=None):
    """
    Wrap c function setting prototype.
    @func: C func
    @restype: return type
    @argtypes: args types
    """
    func.restype = restype
    func.argtypes = argtypes
    if errcheck is not None:
        func.errcheck = errcheck
    return func


def err_check(code):
    if code == cons.ERAR_END_ARCHIVE:
        raise EndOfArchive("End of archive")
    elif code == cons.ERAR_NO_MEMORY:
        raise ArchiveOpenError("Not enough memory to initialize data structures")
    elif code == cons.ERAR_BAD_DATA:
        raise BadHeaderData("Archive header broken")
    elif code == cons.ERAR_BAD_ARCHIVE:
        raise ArchiveOpenError("Archive open error")
    elif code == cons.ERAR_UNKNOWN_FORMAT:
        raise ArchiveOpenError("Unknown encryption used for archive headers")
    elif code == cons.ERAR_EOPEN:
        raise ArchiveOpenError("File open error")
    elif code == cons.ERAR_ECREATE:
        raise UnRARError("File create error")
    elif code == cons.ERAR_ECLOSE:
        raise CloseError("Archive/File close error")
    elif code == cons.ERAR_EREAD:
        raise ReadError("Read error")
    elif code == cons.ERAR_EWRITE:
        raise UnRARError("Write error")
    elif code == cons.ERAR_SMALL_BUF:
        raise ArchiveOpenError("Buffer too small, comments not completely read")
    elif code == cons.ERAR_UNKNOWN:
        raise UnRARError("Unknown error")
    elif code == cons.ERAR_MISSING_PASSWORD:
        raise BadPassword("Missing password error")
    elif not code == cons.SUCCESS:
        raise UnRARError('Unhandled OpenReult: {}'.format(code))


def _check_open_result(res, func, args):
    """
    @res: returned value (by the called C func)
    @func: the C func
    @args: tuple with the args passed to the C func.
    """
    open_result = args[0].open_result #archiveData
    err_check(open_result)
    return res


def _check_result(res, func, args):
    err_check(res)
    return res


#HANDLE = c_void_p #linux and win32
RAROpenArchiveEx = _c_func(unrarlib.RAROpenArchiveEx, c_void_p,
                            [POINTER(RAROpenArchiveDataEx), ],
                            _check_open_result)

#files data
RARReadHeaderEx = _c_func(unrarlib.RARReadHeaderEx, c_int,
                        [c_void_p, POINTER(RARHeaderDataEx)],
                        _check_result)

#Moves the current position in the archive to the next file.
RARProcessFileW = _c_func(unrarlib.RARProcessFileW, c_int,
                        [c_void_p, c_int, c_wchar_p, c_wchar_p],
                        _check_result)

#Close RAR archive and release allocated memory.
RARCloseArchive = _c_func(unrarlib.RARCloseArchive, c_int,
                        [c_void_p, ],
                        _check_result)


if __name__ == "__main__":

    import utils

    passwords = ["algo", "asdasdqwe", "some"]
    utils.extract_file("C:\\Users\\Admin\\Desktop\\evtc.part1.rar", "C:\\Users\\Admin\\Desktop", passwords)