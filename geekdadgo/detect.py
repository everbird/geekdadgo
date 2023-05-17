#!/usr/bin/env python3


def check_color(frame, x, y, kind, config):
    r,g,b = frame[y, x, 2], frame[y, x, 1], frame[y, x, 0]
    c = config.data["colors"][kind]
    rr,gg,bb = c['r'], c['g'], c['b']
    return rr[0] <= r <= rr[1] and gg[0] <= g <= gg[1] and bb[0] <= b <= bb[1]


def find_headers(frame, config):
    hh = config.data["header-detect"]["jump"]
    px = config.data["header-detect"]["x"]
    y = config.data["header-detect"]["y"]
    headers = []
    height = frame.shape[0]
    while y < height:
        if (
                check_color(frame, px, y, "header", config)
                or check_color(frame, px, y, "border", config)
        ):
            headers.append(y)
            y += hh

        y += 1
    return headers


def check_loading(i, frame, config):
    x = config.data["loading-detect"]["x"]
    y = config.data["loading-detect"]["y"]
    w = config.data["loading-detect"]["width"]
    h = config.data["loading-detect"]["height"]
    points = [
        (x, y),
        (x+w, y),
        (x, y+h),
        (x+w, y+h)
    ]
    # Debug
    # roi = frame[y:y+h, x:x+w]
    # cv2.imwrite(f"images/frame{i}-loading.png", roi)
    for xx, yy in points:
        if not check_color(frame, xx, yy, "loading", config):
            return False

    return True
