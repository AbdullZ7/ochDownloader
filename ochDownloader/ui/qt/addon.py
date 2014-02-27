import pkgutil
import importlib
import weakref
import logging

from core import const

logger = logging.getLogger(__name__)
_registry = []


def register(addon_cls):
    if not issubclass(addon_cls, AddonBase):
        raise Exception("%s is not a subclass of %s" % (addon_cls.__name__, AddonBase.__name__))

    if addon_cls not in _registry:
        _registry.append(addon_cls)


def autodiscover():
    for module_loader, name, ispkg in pkgutil.iter_modules(path=[const.ADDONS_GUI_PATH, ]):
        try:
            importlib.import_module("addons.{module}.addon".format(module=name))
        except Exception as err:
            logger.exception(err)


class AddonBase:
    """"""
    # TODO: create add_action menu method.
    def __init__(self, parent):
        self.weak_parent = weakref.ref(parent)
        self.name = None

    @property
    def parent(self):
        return self.weak_parent()
    
    def set_menu_item(self):
        raise NotImplementedError()
    
    def get_tab(self):
        pass
    
    def get_preferences(self):
        pass