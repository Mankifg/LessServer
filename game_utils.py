import functions
import requests
from datetime import datetime as dt
import uuid

FILES = "abcdef"
BASE_URL = "https://less.palcka.si"


def from_coord_notation(coord_not):
    if len(coord_not) != 4:
        return False, "Len != 4"

    x1, y1, x2, y2 = coord_not

    if not (x1 in FILES and x2 in FILES):
        return False, "Out of bounds"

    x1 = FILES.index(x1)
    x2 = FILES.index(x2)

    y1, y2 = int(y1), int(y2)

    y1 = 6 - y1
    y2 = 6 - y2

    if not (functions.is_valid_cords(x1, y1) and functions.is_valid_cords(x2, y2)):
        print(x1, y1, "->", x2, y2)
        return False, "Coords not good"

    return True, [x1, y1, x2, y2]


def from_arry_notation(arry):
    if len(arry) != 4:
        return False, "Len != 4"

    x1, y1, x2, y2 = arry

    x1 = FILES[x1]
    x2 = FILES[x2]
    y1 = 6 - y1
    y2 = 6 - y2

    return True, f"{x1}{y1}{x2}{y2}"


UP_LEFT = "w"
BOTTOM_RIGHT = "b"
START_POS = "bb4/bb4/6/6/4ww/4ww"


def is_win(lbp):
    if lbp[0:2] + lbp[4:6] == UP_LEFT * 4:
        return True, 1
    if lbp[-2:] + lbp[-6:-4] == BOTTOM_RIGHT * 4:
        return True, -1
    return False, 0


def new_b10_board():
    return requests.get(url=f"{BASE_URL}/new").json()["data"]


def new_game_id():
    return str(int(dt.now().timestamp() * 10))


def new_uuid():
    return uuid.uuid4()


def swap_players(p):
    if p == "w":
        return "b"
    if p == "b":
        return "w"
