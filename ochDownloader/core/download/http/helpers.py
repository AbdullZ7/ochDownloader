

def is_valid_range(source, start_range, size):
    # check if it's the same file
    if size != source.get_content_size():
        return False

    s_range = source.get_start_range()

    if s_range is None or s_range != start_range:
        return False

    return True