import io
import logging
from http import cookiejar

import unittest
from unittest.mock import patch

from core.utils import utils
from core import const

logging.disable(logging.CRITICAL)


class UtilsTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_subprocess_call(self):
        self.assertRaises(OSError, utils.subprocess_call, "unexistent_file")

    def test_subprocess_popen(self):
        self.assertRaises(OSError, utils.subprocess_call, "unexistent_file")

    def test_open_folder_window(self):
        if not const.OS_WIN:
            return

        # Windows
        with patch('os.startfile') as s:
            utils.open_folder_window("path/foo")
            s.assert_called_with('path\\foo', 'explore')

    def test_run_file(self):
        if not const.OS_WIN:
            return

        # Windows
        with patch.object(utils, 'subprocess_popen') as s:
            utils.run_file("path/unexistent_file")
            s.assert_called_with(['path/unexistent_file', ], shell=True)

    def test_links_parser(self):
        text = """https://link_1.com/file.ext
        http://link_2.com/file.ext http://link_3.com/file.ext
        foo bar http://link_4.com/file.ext foo bar
        foohttp://broken.com/broken.ext"""
        self.assertListEqual(utils.links_parser(text), ["https://link_1.com/file.ext",
                                                        "http://link_2.com/file.ext",
                                                        "http://link_3.com/file.ext",
                                                        "http://link_4.com/file.ext"])

    def test_smart_str(self):
        # TODO: remove this function, it's pointless in python3
        unicode_str = "áéíóú foo"
        self.assertEqual(utils.smart_str(unicode_str), unicode_str)

        latin1_str = "áéíóú foo".encode("latin1")
        self.assertRaises(UnicodeDecodeError, utils.smart_str, latin1_str)
        self.assertEqual(utils.smart_str(latin1_str, errors='replace'), "����� foo")
        self.assertEqual(utils.smart_str(latin1_str, encoding='latin1'), unicode_str)

        utf8_str = "áéíóú foo".encode("utf-8")
        self.assertEqual(utils.smart_str(utf8_str), unicode_str)

        bytes_txt = b"foo"
        self.assertEqual(utils.smart_str(bytes_txt), "foo")

        number = 111
        self.assertEqual(utils.smart_str(number), "111")

    def test_time_format(self):
        self.assertEqual(utils.time_format(1), "1s")
        self.assertEqual(utils.time_format(60), "1m 0s")
        self.assertEqual(utils.time_format(3600), "1h 0m 0s")
        self.assertEqual(utils.time_format(86400), "1d 0h 0m")
        self.assertEqual(utils.time_format(59.9), "59s")

    def test_size_format(self):
        self.assertEqual(utils.size_format(1), "1Bytes")
        self.assertEqual(utils.size_format(1024), "1KB")
        self.assertEqual(utils.size_format(1024*1024), "1MB")
        self.assertEqual(utils.size_format(1024*1024*1024), "1.00GB")
        self.assertEqual(utils.size_format(1024*1024*1024 + 1024*1024*100), "1.10GB")

    def test_speed_format(self):
        self.assertEqual(utils.speed_format(1), "1Bytes/s")
        self.assertEqual(utils.speed_format(1024), "1KB/s")
        self.assertEqual(utils.speed_format(1024*1024), "1MB/s")
        self.assertEqual(utils.speed_format(1024*1024*1024), "1.00GB/s")
        self.assertEqual(utils.speed_format(1024*1024*1024 + 1024*1024*100), "1.10GB/s")

    def test_get_filename_from_url(self):
        url = "http//foo.bar/file.ext?js=foobar"
        self.assertEqual(utils.get_filename_from_url(url), "file.ext")

    def test_strip(self):
        self.assertEqual("foobar", utils.strip("fo$o@ba$r", to_strip="@$"))
        self.assertEqual("foobar", utils.strip("foobar"))

    def test_normalize_file_name(self):
        unicode_name = '.file+&amp;/\\:*?"<>|.ext '
        self.assertEqual(utils.normalize_file_name(unicode_name), "file &.ext")

    def test_tail(self):
        text = b"line 1\nline 2\nline 3\nline 4"
        fh = io.BytesIO()
        fh.write(text)
        expected = b"line 3\nline 4"
        self.assertEqual(utils.tail(fh, lines_limit=2), expected)

    def test_html_entities_parser(self):
        entities = "&quot;&apos;&amp;&lt;&gt;&#34;&#39;&#38;&#60;&#62;&#x01ce;"
        expected = "\"'&<>\"'&<>ǎ"
        self.assertEqual(utils.html_entities_parser(entities), expected)

    def test_url_unescape(self):
        url_html = "http://foo.bar/&lt;&gt;&quot;&amp;"
        expected = "http://foo.bar/<>\"&"
        self.assertEqual(utils.url_unescape(url_html), expected)

    def test_load_cookie(self):
        with patch.object(cookiejar.MozillaCookieJar, 'load') as load:
            cookie = utils.load_cookie("path/foo")
            load.assert_called_once_with("path/foo")
            self.assertEqual(type(cookie), type(cookiejar.MozillaCookieJar()))
        self.assertEqual(utils.load_cookie("path/bar"), None)

    def test_remove_file(self):
        path = "path/bar/unexistent_file"
        with patch('os.remove') as remove:
            utils.remove_file(path)
            remove.assert_called_with(path)

        self.assertEqual(utils.remove_file(path), None)