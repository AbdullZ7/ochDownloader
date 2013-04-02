import os
import logging
logger = logging.getLogger(__name__)

try:
    import _winreg
except ImportError:
    _winreg = None

from core import cons


APP_EXE = os.path.join(cons.APP_PATH, cons.APP_NAME + ".exe")


def register_app_path():
    try:
        if cons.OS_WIN and _winreg is not None:
            sub_key = os.path.join('Software', cons.APP_NAME)
            with _winreg.CreateKeyEx(_winreg.HKEY_CURRENT_USER, sub_key, 0, _winreg.KEY_WRITE) as key:
                _winreg.SetValueEx(key, 'path', 0, _winreg.REG_SZ, cons.APP_PATH)
    except Exception as err:
        logger.warning(err)


def register_och_uri_scheme():
    try:
        if cons.OS_WIN and _winreg is not None:
            reg_list = [
                ('och', '', 'och URI'),
                ('och', 'Content Type', 'application/x-och'),
                ('och', 'URL Protocol', ''),
                (os.path.join('och', 'DefaultIcon'), '', "\"{path}\",0".format(path=APP_EXE)),
                (os.path.join('och', 'shell'), '', 'open'),
                (os.path.join('och', 'shell', 'open', 'command'), '', "\"{path}\" --ipc=true --links \"%1\"".format(path=APP_EXE))
            ]
            for sub_key, value_name, value in reg_list:
                with _winreg.CreateKeyEx(_winreg.HKEY_CLASSES_ROOT, sub_key, 0, _winreg.KEY_WRITE) as key:
                    _winreg.SetValueEx(key, value_name, 0, _winreg.REG_SZ, value)
    except Exception as err:
        logger.warning(err)