import pkgutil
import importlib
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import core.cons as cons


class AddonCore:
    """"""
    def __init__(self):
        self.name = None
    
    def get_menu_item(self):
        raise NotImplementedError()
    
    def get_tab(self):
        pass
    
    def get_preferences(self):
        pass
    
    def save(self):
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
        #addons =  []
        for module_loader, name, ispkg in pkgutil.iter_modules(path=[cons.ADDONS_GUI_PATH, ]):
            try:
                module = importlib.import_module("addons.{module}.addon_gui".format(module=name))
                self.addons_list.append(module.Addon(*args, **kwargs))
            except Exception as err:
                logger.warning("{0}: {1}".format(name, err))
        #return addons


if __name__ == "__main__":
    for module_loader, name, ispkg in pkgutil.walk_packages(path=["/home/estecb/Proyecto/addons", ]):
        print name
    #print AddonMount().get_menu_item()
    #print [name for module_loader, name, ispkg in pkgutil.iter_modules(path=[cons.APP_PATH])]
    
