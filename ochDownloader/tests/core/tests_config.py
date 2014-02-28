import json
import logging

import unittest
from unittest.mock import patch, Mock

from core import const
from core.config import conf
from core.config.conf import _Config, rlock, RawConfigParser
from core.config.const import SECTION_ADDONS
from core.config import const as c_const

logging.disable(logging.CRITICAL)


class TestException(Exception):
    """"""


class ConfTest(unittest.TestCase):

    def setUp(self):
        self.conf = _Config()

    def tearDown(self):
        pass

    def test_rlock(self):
        @rlock
        def func(arg, kwarg=None):
            self.assertEqual(arg, "foo")
            self.assertEqual(kwarg, "bar")
            return True

        self.assertTrue(func("foo", kwarg="bar"))

    def test_conf(self):
        with patch.object(_Config, 'load') as l:
            with patch.object(_Config, 'create') as c:
                conf = _Config()
                l.assert_called_once_with()
                c.assert_called_once_with()

    def test_create(self):
        default = {"section": {"option": "value", }, }

        with patch.dict('core.config.const.DEFAULT', default) as d:
            conf = _Config()
            conf.create()
            self.assertTrue(conf.has_section("section"))
            self.assertTrue(conf.has_option("section", "option"))

    def test_load(self):
        with patch.object(_Config, 'read') as r:
            conf = _Config()
            conf.load()
            r.assert_called_with(const.CONFIG_FILE, encoding='utf-8')

        with patch.object(_Config, 'read', side_effect=OSError()):
            conf = _Config()
            conf.load()

        with patch.object(_Config, 'read', side_effect=TestException()):
            self.assertRaises(TestException, _Config)

    def test_save(self):
        with patch.object(self.conf, 'write') as w:
            with patch('builtins.open') as o:
                self.conf.save()
                o.assert_called_once_with(const.CONFIG_FILE, mode='w', encoding='utf-8')
                self.assertTrue(w.called)

        with patch.object(self.conf, 'write', side_effect=OSError()):
            with patch('builtins.open', side_effect=OSError()):
                self.conf.save()

        with patch.object(self.conf, 'write', side_effect=TestException()):
            with patch('builtins.open'):
                self.assertRaises(TestException, self.conf.save)

        with patch.object(self.conf, 'write'):
            with patch('builtins.open', side_effect=TestException()):
                self.assertRaises(TestException, self.conf.save)

    def test_get(self):
        with patch.object(RawConfigParser, 'get') as g:
            self.conf.get("foo")
            g.assert_called_once_with("foo")

    def test_getboolean(self):
        with patch.object(RawConfigParser, 'getboolean') as g:
            self.conf.getboolean("foo")
            g.assert_called_once_with("foo")

    def test_getint(self):
        with patch.object(RawConfigParser, 'getint') as g:
            self.conf.getint("foo")
            g.assert_called_once_with("foo")

    def test_set(self):
        with patch.object(RawConfigParser, 'set') as s:
            self.conf.set("section", "option", value="foo")
            s.assert_called_once_with("section", "option", "foo")

    def test_setboolean(self):
        with patch.object(self.conf, 'set') as s:
            self.conf.setboolean("section", "option", True)
            s.assert_called_once_with("section", "option", "True")
            self.conf.setboolean("section", "option", False)
            s.assert_called_with("section", "option", "False")

    def test_setint(self):
        with patch.object(self.conf, 'set') as s:
            self.conf.setint("section", "option", 1)
            s.assert_called_once_with("section", "option", "1")

    def test_set_addon_option(self):
        with patch.object(self.conf, 'set') as s:
            self.conf.set_addon_option("option", "foo")
            s.assert_called_once_with(SECTION_ADDONS, "option", "foo")

    def test_setboolean_addon_option(self):
        with patch.object(self.conf, 'setboolean') as s:
            self.conf.setboolean_addon_option("option", True)
            s.assert_called_once_with(SECTION_ADDONS, "option", True)

    def test_setint_addon_option(self):
        with patch.object(self.conf, 'setint') as s:
            self.conf.setint_addon_option("option", 1)
            s.assert_called_once_with(SECTION_ADDONS, "option", 1)

    def test_get_addon_option(self):
        with patch.object(self.conf, 'get') as g:
            self.conf.get_addon_option("option", default="foo")
            g.assert_called_once_with(SECTION_ADDONS, "option", fallback="foo")

    def test_getboolean_addon_option(self):
        with patch.object(self.conf, 'getboolean') as g:
            self.conf.getboolean_addon_option("option", default=True)
            g.assert_called_once_with(SECTION_ADDONS, "option", fallback=True)

    def test_getint_addon_option(self):
        with patch.object(self.conf, 'getint') as g:
            self.conf.getint_addon_option("option", default=1)
            g.assert_called_once_with(SECTION_ADDONS, "option", fallback=1)

    def test_set_proxy_active(self):
        with patch.object(self.conf, 'setboolean') as s:
            self.conf.set_proxy_active(is_active=True)
            s.assert_called_once_with(c_const.SECTION_NETWORK, c_const.OPTION_PROXY_ACTIVE, True)

    def test_get_proxy_active(self):
        with patch.object(self.conf, 'getboolean') as g:
            self.conf.get_proxy_active()
            g.assert_called_once_with(c_const.SECTION_NETWORK, c_const.OPTION_PROXY_ACTIVE)

    def test_set_proxy(self):
        with patch.object(self.conf, 'set') as s:
            with patch.object(self.conf, 'setint') as sint:
                self.conf.set_proxy("ptype", "ip", 8000)
                #s.assert_called_with(c_const.SECTION_NETWORK, c_const.OPTION_PROXY_TYPE, "ptype")
                s.assert_called_with(c_const.SECTION_NETWORK, c_const.OPTION_PROXY_IP, "ip")
                sint.assert_called_with(c_const.SECTION_NETWORK, c_const.OPTION_PROXY_PORT, 8000)

    def test_get_proxy(self):
        with patch.object(self.conf, 'get') as g:
            with patch.object(self.conf, 'getint') as gint:
                self.conf.get_proxy()
                g.assert_called_with(c_const.SECTION_NETWORK, c_const.OPTION_PROXY_IP)
                gint.assert_called_once_with(c_const.SECTION_NETWORK, c_const.OPTION_PROXY_PORT)

    def test_set_retries_limit(self):
        with patch.object(self.conf, 'setint') as s:
            self.conf.set_retries_limit(1)
            s.assert_called_once_with(c_const.SECTION_NETWORK, c_const.OPTION_RETRIES_LIMIT, 1)

    def test_get_retries_limit(self):
        with patch.object(self.conf, 'getint') as g:
            self.conf.get_retries_limit()
            g.assert_called_once_with(c_const.SECTION_NETWORK, c_const.OPTION_RETRIES_LIMIT)

    def test_set_html_dl(self):
        with patch.object(self.conf, 'setboolean') as s:
            self.conf.set_html_dl(is_active=True)
            s.assert_called_once_with(c_const.SECTION_NETWORK, c_const.OPTION_HTML_DL, True)

    def test_get_html_dl(self):
        with patch.object(self.conf, 'getboolean') as g:
            self.conf.get_html_dl()
            g.assert_called_once_with(c_const.SECTION_NETWORK, c_const.OPTION_HTML_DL)

    def test_set_max_conn(self):
        with patch.object(self.conf, 'setint') as s:
            self.conf.set_max_conn(1)
            s.assert_called_once_with(c_const.SECTION_NETWORK, c_const.OPTION_MAX_CONN, 1)

    def test_get_max_conn(self):
        with patch.object(self.conf, 'getint') as g:
            self.conf.get_max_conn()
            g.assert_called_once_with(c_const.SECTION_NETWORK, c_const.OPTION_MAX_CONN)

    def test_set_window_settings(self):
        with patch.object(self.conf, 'set') as s:
            self.conf.set_window_settings(1, 1, 1, 1)
            s.assert_called_once_with(c_const.SECTION_GUI, c_const.OPTION_WINDOW_SETTINGS,
                                      json.dumps([1, 1, 1, 1]))

    def test_get_window_settings(self):
        ret = c_const.DEFAULT[c_const.SECTION_GUI][c_const.OPTION_WINDOW_SETTINGS]

        with patch.object(self.conf, 'get', return_value=ret) as g:
            x, y, w, h = self.conf.get_window_settings()
            g.assert_called_once_with(c_const.SECTION_GUI, c_const.OPTION_WINDOW_SETTINGS)

    def test_set_save_dl_paths(self):
        with patch.object(self.conf, 'set') as s:
            self.conf.set_save_dl_paths(['foo', ])
            s.assert_called_once_with(c_const.SECTION_GUI, c_const.OPTION_SAVE_DL_PATHS,
                                      json.dumps(['foo', ]))

    def test_get_save_dl_paths(self):
        ret = c_const.DEFAULT[c_const.SECTION_GUI][c_const.OPTION_SAVE_DL_PATHS]

        with patch.object(self.conf, 'get', return_value=ret) as g:
            paths = self.conf.get_save_dl_paths()
            g.assert_called_once_with(c_const.SECTION_GUI, c_const.OPTION_SAVE_DL_PATHS)
            self.assertEqual(paths, json.loads(ret))

    def test_set_tray_available(self):
        with patch.object(self.conf, 'setboolean') as s:
            self.conf.set_tray_available(is_active=True)
            s.assert_called_once_with(c_const.SECTION_GUI, c_const.OPTION_TRAY_ICON, True)

    def test_get_tray_available(self):
        with patch.object(self.conf, 'getboolean') as g:
            self.conf.get_tray_available()
            g.assert_called_once_with(c_const.SECTION_GUI, c_const.OPTION_TRAY_ICON)

    def test_set_auto_switch_tab(self):
        with patch.object(self.conf, 'setboolean') as s:
            self.conf.set_auto_switch_tab(is_active=True)
            s.assert_called_once_with(c_const.SECTION_GUI, c_const.OPTION_SWITCH_TAB, True)

    def test_get_auto_switch_tab(self):
        with patch.object(self.conf, 'getboolean') as g:
            self.conf.get_auto_switch_tab()
            g.assert_called_once_with(c_const.SECTION_GUI, c_const.OPTION_SWITCH_TAB)