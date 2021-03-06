from core.dispatch import Event


switch_tab = Event('switch_tab')
store_items = Event('store_items')
add_downloads_to_check = Event('add_downloads_to_check')
on_stop_all = Event('on_stop_all')
status_bar_pop_msg = Event('status_bar_pop_msg')
status_bar_push_msg = Event('status_bar_push_msg')
captured_links_count = Event('captured_links_count')
show_or_hide_tray = Event('show_or_hide_tray')
add_password = Event('add_password')  # args: password
add_to_downloader = Event('add_to_downloader')