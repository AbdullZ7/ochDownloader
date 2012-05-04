import ctypes
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

#stuff taken from msdn api and examples.

FLASHW_STOP = 0
FLASHW_CAPTION = 1 #flash window
FLASHW_TRAY = 2 #flash icon
FLASHW_ALL = (FLASHW_CAPTION | FLASHW_TRAY)
FLASHW_TIMER = 4
FLASHW_TIMERNOFG = 12 #flash until come to foregound.

FORMAT_MESSAGE_FROM_SYSTEM = 4096

windll = ctypes.windll
#_gdi32 = windll.gdi32
#_kernel32 = windll.kernel32
_user32 = windll.user32

# error checking
_GetLastError = windll.kernel32.GetLastError
_SetLastError = windll.kernel32.SetLastError
_FormatMessageA = windll.kernel32.FormatMessageA

#err = _GetLastError()
def format_error(err):
    msg = ctypes.create_string_buffer(256)
    _FormatMessageA(FORMAT_MESSAGE_FROM_SYSTEM,
                      ctypes.c_void_p(),
                      err,
                      0,
                      msg,
                      len(msg),
                      ctypes.c_void_p())
    return msg.value

#typedef struct {
#  UINT  cbSize;
#  HWND  hwnd;
#  DWORD dwFlags;
#  UINT  uCount;
#  DWORD dwTimeout;
#}FLASHWINFO, *PFLASHWINFO;

class FLASHWINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), 
                ("hwnd", ctypes.c_void_p),
                ("dwFlags", ctypes.c_uint),
                ("uCount", ctypes.c_uint),
                ("dwTimeout", ctypes.c_uint)
                ]

def flash_taskbar_icon(window_handle, flag=FLASHW_TIMERNOFG, times=2, rate=0):
    """
    @param window_handler: GTKWindow.window.handle
    @param flag: 0 = stop flashing, 1 = flash the window, 2 = flash the taskbar button, 
        3= flash both, 4 = flash until flag is 0, 12 = flash until window comes to foreground.
    @param times: flash x times
    @param rate: flash time rate in mseg, 0 = mouse rate.
    """
    try:
        # start flashing the window
        finfo = FLASHWINFO(0, window_handle, flag, times, rate)
        finfo.cbSize = ctypes.sizeof(finfo)
        #BOOL WINAPI FlashWindowEx(  __in  PFLASHWINFO pfwi );
        _user32.FlashWindowEx(ctypes.byref(finfo)) #byref = pointer/reference in memory.
        #print format_error(_GetLastError())
    except Exception as err:
        logger.exception(err)



