from dispatch import Event


download_complete = Event('download_complete')  # args: download_item
all_downloads_complete = Event('all_downloads_complete')
quit = Event('quit')
limit_exceeded = Event('limit_exceeded')
add_raw_downloads = Event('add_raw_downloads')  # args: links, path, cookie