import logging
logger = logging.getLogger(__name__) 

#Libs
import cons
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
    
    def get_all_downloads(self, complete=True):
        all_downloads = {}
        all_downloads.update(self.active_downloads)
        all_downloads.update(self.queue_downloads)
        all_downloads.update(self.stopped_downloads)
        if complete:
            all_downloads.update(self.complete_downloads)
        return all_downloads

    def clear_complete(self):
        self.complete_downloads.clear()

    def save_download_as(self, item_id, save_as):
        all_downloads = self.get_all_checking_downloads()
        download_item = all_downloads[item_id]
        download_item.save_as = save_as
    
    def load_session(self):
        try:
            ordered_list = []
            download_list = self.session_parser.load()
            for item in download_list:
                FILE_NAME, FILE_PATH, LINK, HOST, SIZE, PROGRESS, TIME, CHUNCKS, QUALITY, SAVE_AS = range(10)
                download_item = DownloadItem(item[FILE_NAME], item[HOST], item[SIZE], item[LINK], item[FILE_PATH])
                download_item.status = cons.STATUS_STOPPED
                download_item.progress = item[PROGRESS]
                download_item.size = item[SIZE]
                download_item.time = item[TIME]
                download_item.chunks = item[CHUNCKS]
                download_item.video_quality = item[QUALITY]
                download_item.save_as = item[SAVE_AS]
                self.stopped_downloads[download_item.id] = download_item
                ordered_list.append(download_item)
        except Exception as err:
            logger.exception(err)
            return []
        return ordered_list
    
    def save_session(self, id_item_list):
        download_list = []
        all_downloads = self.get_all_downloads(complete=False)
        for download_item in (all_downloads.get(id_item, None) for id_item in id_item_list): #generator
            if download_item is not None:
                download_list.append([download_item.name, download_item.path, download_item.link, download_item.host,
                                      download_item.size, download_item.progress, download_item.time, download_item.chunks,
                                      download_item.video_quality, download_item.save_as])
        self.session_parser.save(download_list)
        logger.debug("Session has been saved")
        if len(all_downloads) != len(download_list):
            logger.warning("save_session: list len dont match")

    def get_download_items(self, id_item_list):
        """"""
        all_downloads = self.get_all_downloads()
        return [all_downloads[id_item] for id_item in id_item_list]


#singleton like.
api = _Api()