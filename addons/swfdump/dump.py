import os
import tempfile
import subprocess
import logging
logger = logging.getLogger(__name__)

from core import cons
from core import utils

def get_path():
    if cons.OS_WIN:
        return os.path.join(cons.ADDONS_GUI_PATH, "swfdump", "bin", "swfdump.exe")
    else:
        return "swfdump"

def get_swf_dump(content):
    #swf file
    try:
        with tempfile.NamedTemporaryFile(suffix=".swf", delete=False) as fh:
            fh.write(content)
        p = utils.subprocess_popen([get_path(), '-a', fh.name], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out_put, err = p.communicate()
        if err:
            raise Exception(err)
        else:
            return out_put
    except Exception as err:
        logger.exception(err)
        return None