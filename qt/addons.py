import pkgutil
import importlib
import weakref
import logging
logger = logging.getLogger(__name__)

from core import cons


class AddonCore:
    """"""
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


class AddonsManager:
    """"""
    def __init__(self, *args, **kwargs):
        """"""
        self.addons_list = []
        self.init_addons(*args, **kwargs)

    def init_addons(self, *args, **kwargs):
        """
        find all files in the addons directory and import them
        """
        for module_loader, name, ispkg in pkgutil.iter_modules(path=[cons.ADDONS_GUI_PATH, ]):
            try:
                module = importlib.import_module("addons.{module}.addon_gui".format(module=name))
                self.addons_list.append(module.Addon(*args, **kwargs))
            except Exception as err:
                logger.exception("{0}: {1}".format(name, err))


if __name__ == "__main__":
    pass
    
