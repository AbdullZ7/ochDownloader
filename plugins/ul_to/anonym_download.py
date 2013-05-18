from plugins.uploaded.anonym_download import PluginDownload as plugin_download


class PluginDownload(plugin_download):
    def __init__(self, *args, **kwargs):
        plugin_download.__init__(self, *args, **kwargs)
