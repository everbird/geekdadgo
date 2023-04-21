#!/usr/bin/env python3

import cv2
import pytesseract
import string


ABBR_MONTHS = [
    "JAN",
    "FEB",
    "MAR",
    "APR",
    "MAY",
    "JUN",
    "JUL",
    "AUG",
    "SEP",
    "OCT",
    "NOV",
    "DEC",
]

digits = string.digits
chars = set("".join(ABBR_MONTHS))
whitelist = digits+"".join(sorted(chars))
blacklist = "".join(sorted(set(string.ascii_letters) - chars))
# Set the OCR configuration to recognize only dates in the format "dd/mm/yyyy"
date_config = '--oem 3 --psm 11 -c tessedit_char_whitelist={} -c tessedit_char_blacklist={}'.format(whitelist, blacklist)
time_config = '--oem 3 --psm 11 -c tessedit_char_whitelist=,:APM0123456789 -c tessedit_char_blacklist={}'.format("".join(sorted(set(string.ascii_letters) - set("APM"))))


def get_date_string(frame, i):
    x, y = 20, 10
    w, h = 120, 55
    roi = frame[y:y+h, x:x+w]
    # Debug
    # cv2.imwrite(f"images/ds{i}.png", roi)
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    _text = pytesseract.image_to_string(gray, lang='eng', config=date_config)
    _text = _text.replace(" ", "")
    text = smart_correct(_text)
    if text != _text:
        print("Correct: {} -> {}".format(_text, text))
    return text.strip()


def get_time_string(frame, i):
    y = 125
    x = 640
    w = 160
    h = 50
    roi = frame[y:y+h, x:x+w]
    # Debug
    # cv2.imwrite(f"images/ts{i}.png", roi)
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    _text = pytesseract.image_to_string(gray, lang='eng', config=time_config)
    _text = _text.replace(" ", "")
    return _text.strip()


def smart_correct(text):
    corrections = {
        "O": "0",
        "L": "1",
        "R": "2",
        "E": "3",
        "A": "4",
        "S": "5",
        "G": "6",
        "T": "7",
        "B": "8",
    }
    month = text[:3]
    day = text[3:]
    r = ""
    for ch in day:
        if ch in corrections:
            r += corrections[ch]
        else:
            r += ch
    return "{}{}".format(month, r)


def run():
    print(date_config)
    print(time_config)
    video = cv2.VideoCapture('RPReplay_Final1681627796.MP4')
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    step = 1
    jump = 40
    px = 30
    py = 30

    i = 0
    pre = None
    while i < frame_count:
        ret, frame = video.read()
        # Define the region to crop
        x = 30
        y = 260
        width = 830
        height = 1400

        r,g,b = frame[py+y, px+x, 2], frame[py+y, px+x, 1], frame[py+y, px+x, 0]

        if 253 <= r <= 255 and 250 <= g <= 253 and 224 <= b <= 247:
            # Crop the frame to the specified region
            cropped_frame = frame[y:y+height, x:x+width]
            ds = get_date_string(cropped_frame, i)
            ds = ds.replace(" ", "")
            if len(ds) < 5:
                print(f"Malformed OCR {ds}. Skipping ...")
                i += 1
                continue

            if pre == ds:
                print(f"Still the same date: {ds}")
                i += jump
                continue

            pre = ds

            ts = get_time_string(cropped_frame, i)
            ts = ts.replace(":", "-")
            cv2.imwrite(f'images/img_frame{i:04d}_{ds}_{ts}.png', cropped_frame)
            # video.set(cv2.CAP_PROP_POS_FRAMES, video.get(cv2.CAP_PROP_POS_FRAMES) + step)
            video.set(cv2.CAP_PROP_POS_FRAMES, video.get(cv2.CAP_PROP_POS_FRAMES) + jump)
            i += jump
        else:
            i += 1



if __name__ == '__main__':
    run()
