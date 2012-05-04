import os
import sys
import subprocess
import tempfile
import logging
logger = logging.getLogger(__name__)

#PIL library.
import ImageFile
import Image
import TiffImagePlugin
import PngImagePlugin
import GifImagePlugin
import JpegImagePlugin

import core.cons as cons
from core.network.connection import URLOpen, URLClose

IMAGE_SUFFIX = ".tif"
TEXT_SUFFIX = ".txt"

def get_path():
    """"""
    if cons.OS_WIN:
        return os.path.join(cons.ADDONS_GUI_PATH, "tesseract","bin", "tesseract.exe")
    #elif cons.OS_OSX:
        #return os.path.join(sys.path[0], "bin", "tesseract")
    else:
        return "tesseract"

def get_solved_captcha(url, cookie, filter=None):
    """
    @params: filter = a function wraping one or more clean_image functions.
    """
    try:
        with URLClose(URLOpen(cookie).open(url)) as s:
            image_data = s.read()
        t = Tesseract(image_data, filter)
        result = t.get_captcha()
    except Exception as err:
        logger.exception(err)
        return None
    else:
        return result


class Tesseract:
    """"""
    def __init__(self, data, filter=None):
        """"""
        try:
            #create temporary image-files
            with tempfile.NamedTemporaryFile(suffix=TEXT_SUFFIX, delete=False) as fh:
                self.text_name = fh.name
            with tempfile.NamedTemporaryFile(suffix=IMAGE_SUFFIX, delete=False) as fh:
                self.image_name = fh.name
            p = ImageFile.Parser()
            p.feed(data)
            image = p.close()
            if filter:
                image = filter(image)
            image.save(self.image_name)
        except EnvironmentError as err:
            logger.exception(err)
            self.text_name = ""
            self.image_name = ""
    
    def get_captcha(self):
        """"""
        captcha = ""
        try:
            text_name = os.path.splitext(self.text_name)[0] #remove prefix for tesseract.
            retcode = subprocess.call([get_path(), self.image_name, text_name])
            if retcode >= 0:
                with open(self.text_name, "rb") as fh:
                    captcha = fh.readline().strip()
        except Exception as err:
            logger.exception(err)
            return ""
        else:
            return captcha


if __name__ == "__main__":
    import clean_image
    def filter(image):
        image_ = clean_image.convert_to_greyscale(image)
        image_ = clean_image.clean_noise(image_, 3)
        return image_
    with open("/home/estecb/Proyecto/addons/tesseract/image_examples/example_netload.png", "rb") as fh:
        t = Tesseract(fh.read(), filter)
    print t.get_captcha()


