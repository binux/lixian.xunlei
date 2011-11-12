# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
def format_size(request, size):
    i = 0
    while size > 1024:
        size /= 1024
        i += 1
    return "%d%s" % (size, units[i])

def determin_url_type(url):
    url_lower = url.lower()
    if url_lower.endswith(".torrent"):
        return "bt"
    elif url_lower.startswith("ed2k"):
        return "ed2k"
    elif url_lower.startswith("thunder"):
        return "thunder"
    elif url_lower.startswith("magnet"):
        return "magnet"
    else:
        return "normal"

ui_methods = {
        "format_size": format_size,
}
