import datetime, time

now = int(time.time())
delta = 500 * 365.242 * 86400 # 500 years of seconds
start_epoch = int(now - delta)
