import logging
logger = logging.getLogger(__name__) 

#Libs
import cons
from config import config_parser #initialize config.
from events import events #initialize events.
from plugins_parser import plugins_parser #initialize plugins_parser
from host_accounts import host_accounts #initialize accounts.
#
from download_manager import DownloadManager
from add_downloads_manager import AddDownloadsManager
from update_manager import UpdateManager
from session_parser import SessionParser
from download_core import DownloadItem


class _Api(DownloadManager, AddDownloadsManager):
    """
    AddDownloadsManager:
    .Contiene la lista de archivos pendientes, y metodos para el chequeo de links.
    .Atributos heredados:
    self.pending_downloads - privados.
    .Metodos heredados:
    N/A
    
    DownloadManager:
    N/A
    """
    def __init__(self):
        """"""
        DownloadManager.__init__(self)
        AddDownloadsManager.__init__(self)
        self.session_parser = SessionParser()
    
    def start_update_manager(self):
        update_manager = UpdateManager() #new thread.
        update_manager.start()
        return update_manager
    
    def get_active_downloads(self):
        return self.active_downloads.copy()
    
    def get_queue_downloads(self):
        return self.queue_downloads.copy()
    
    def get_complete_downloads(self):
        return self.complete_downloads.copy()
    
    def get_stopped_downloads(self):
        return self.stopped_downloads.copy()
    
    def get_all_downloads(self):
        all_downloads = {}
        all_downloads.update(self.active_downloads)
        all_downloads.update(self.queue_downloads)
        all_downloads.update(self.stopped_downloads)
        all_downloads.update(self.complete_downloads)
        return all_downloads
    
    def load_session(self):
        try:
            download_list = self.session_parser.load()
            if download_list:
                for item in download_list:
                    FILE_NAME, FILE_PATH, LINK, HOST, SIZE, STATUS_MSG, PROGRESS, TIME, TIME_REMAIN, CHUNCKS = range(10) #cool stuff
                    download_item = DownloadItem(item[FILE_NAME], item[HOST], item[SIZE], item[LINK], item[FILE_PATH])
                    download_item.status = cons.STATUS_STOPPED
                    download_item.progress = item[PROGRESS]
                    download_item.size = item[SIZE]
                    download_item.time = item[TIME]
                    download_item.chunks = item[CHUNCKS]
                    self.stopped_downloads[download_item.id] = download_item
        except Exception as err:
            logger.exception(err)
    
    def save_session(self, id_order_list):
        download_list = []
        all_downloads = self.active_downloads.values() + self.queue_downloads.values() + self.stopped_downloads.values()
        self.reorder_list(all_downloads, id_order_list) #reorder in-place.
        for download_item in all_downloads:
            download_list.append([download_item.name, download_item.path, download_item.link, download_item.host, download_item.size, download_item.status_msg, download_item.progress, download_item.time, download_item.time_remain, download_item.chunks]) #lista dentro de lista
        #download_list = self.get_downloads_list(id_order_list)
        self.session_parser.save(download_list)
        logger.debug("Session has been saved")
    
    def get_download_items(self, id_items_list):
        """"""
        all_downloads = self.get_all_downloads()
        return [all_downloads[id_item] for id_item in id_items_list]
    
    def get_status(self):
        """"""
        result_list = self.get_items_update() #return only updated items
        return result_list
    
    

#singleton like.
api = _Api()
