from datetime import datetime

from colored import fg, bg, attr


def info(msg):
    print(f'{datetime.utcnow().isoformat()} {fg("light_blue")}{msg}{attr("reset")}')


def warn(msg):
    print(f'{datetime.utcnow().isoformat()} {fg("light_yellow")}{msg}{attr("reset")}')


def error(msg):
    print(f'{datetime.utcnow().isoformat()} {fg("light_red")}{msg}{attr("reset")}')


def debug(msg):
    print(f'{datetime.utcnow().isoformat()} {fg("light_magenta")}{msg}{attr("reset")}')