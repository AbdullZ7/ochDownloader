from core import utils

from .exceptions import RequestError


class Response:

    def __init__(self, res):
        self.res = res
        self.headers = dict(res.info())

    def readlines(self):
        try:
            for line in self.res.readlines():
                yield line
        except Exception as err:
            raise RequestError(err)

    def read(self, size=None):
        try:
            return self.res.read(size)
        except Exception as err:
            raise RequestError(err)

    def close(self):
        self.res.close()

    def can_resume(self):
        if self.headers.get('Content-Range', None):
            return True

        if self.headers.get('Accept-Ranges', "").lower() == "bytes":
            return True

        return False

    def get_content_size(self):
        try:
            return int(self.headers['Content-Range'].split("/")[-1])  # Content-Range: bytes 0-92244842/92244843
        except (KeyError, ValueError):
            pass

        try:
            return int(self.headers['Content-Length'])  # Content-Length: 92244843
        except (KeyError, ValueError):
            pass

        return 0

    def get_start_range(self):
        try:
            # Content-Range: bytes 61505536-92244842/92244843
            return int(self.headers['Content-Range'].split("/")[0].strip().split(" ")[-1].split("-")[0])
        except (KeyError, ValueError):
            pass

    def _get_filename(self):
        # TODO: fixme, HTTP headers are latin1 encoded, but python return unicode
        # must do encode-decode?
        # http://lucumr.pocoo.org/2013/7/2/the-updated-guide-to-unicode/
        # Content-Disposition: Attachment; filename=name.ext
        disposition = self.headers.get('Content-Disposition', "")

        if 'filename="' in disposition:
            return disposition.split('filename=')[-1].split('"')[1]

        if "filename='" in disposition:
            return disposition.split('filename=')[-1].split("'")[1]

        if 'filename=' in disposition:
            return disposition.split('filename=')[-1]

        if 'filename*=' in disposition:
            return disposition.split("'")[-1]

    def get_filename(self):
        file_name = self._get_filename()

        # TODO: fixme may raise an exception
        if file_name and file_name.startswith('=?UTF-8?B?'):  # base64
            file_name = file_name[10:].decode('base64')

        if not file_name:
            file_name = utils.get_filename_from_url(self.res.url)

        file_name = utils.normalize_file_name(file_name)

        return file_name

    def is_html(self):
        # Content-Type: text/html; charset=ISO-8859-4
        if "text/html" in self.headers.get('Content-Type', ""):
            return True
        else:
            return False