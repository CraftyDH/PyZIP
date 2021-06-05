import time
def mktime(ctime: time.struct_time):
    # Time (5 Hour) (6 Minute) (5 Second ( divided by zero ))
    modtime = ctime.tm_hour << 11 | ctime.tm_min << 5 | ctime.tm_sec // 2
    # Date (7 Year) (4 Month) (5 Day)
    moddate = (ctime.tm_year - 1980) << 9 | ctime.tm_mon << 5 | ctime.tm_mday
    return (modtime, moddate)

