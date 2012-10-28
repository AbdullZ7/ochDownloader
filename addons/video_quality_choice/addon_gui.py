import logging
logger = logging.getLogger(__name__)

from core.events import events

from qt.addons import AddonCore

from choice_gui import QualityChoiceDialog


class Addon(AddonCore):
    """"""
    def __init__(self, parent, *args, **kwargs):
        """"""
        AddonCore.__init__(self)
        self.parent = parent
        self.connect()

    def set_menu_item(self):
        """"""
        pass

    def connect(self):
        events.quality_choice_dialog.connect(self.trigger) #connect event

    #def disconnect(self):
        #events.quality_choice_dialog.disconnect(self.trigger)

    def trigger(self, f_name, choices_dict, set_solution, *args, **kwargs):
        choice_dlg = QualityChoiceDialog(f_name, choices_dict, self.parent)
        solution = choice_dlg.get_solution()
        set_solution(solution)