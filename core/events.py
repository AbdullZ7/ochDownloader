from dispatch import Event


class _Events:
    captcha_dialog = Event('captcha_dialog') #args: service, get_captcha_img, set_solution
    download_complete = Event('download_complete') #args: download_item
    all_downloads_complete = Event('all_downloads_complete')
    quit = Event('quit')
    limit_exceeded = Event('limit_exceeded')
    add_password = Event('add_password') #args: password

events = _Events()
