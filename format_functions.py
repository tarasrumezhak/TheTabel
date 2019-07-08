def name_from_secure_name(secure_name):
    ind_last_digit = 0
    for ind, c in enumerate(secure_name):
        if c.isdigit():
            ind_last_digit = ind
    try:
        return secure_name[ind_last_digit+1:]
    except IndexError:
        return secure_name
