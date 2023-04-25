#!/usr/bin/env python3

import cv2
import pytesseract
import string
import imutils


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
whitelist = ","+digits+"".join(sorted(chars))
blacklist = "".join(sorted(set(string.ascii_letters) - chars))
# Set the OCR configuration to recognize only dates in the format "dd/mm/yyyy"
# REF: https://muthu.co/all-tesseract-ocr-options/
#
date_config = '--oem 3 --psm 7 -c tessedit_char_whitelist={} -c tessedit_char_blacklist={}'.format(whitelist, blacklist)
time_config = '--oem 3 --psm 7 -c tessedit_char_whitelist=,:APM0123456789 -c tessedit_char_blacklist={}'.format("".join(sorted(set(string.ascii_letters) - set("APM"))))


def get_date_string(frame, i):
    x, y = 20, 0
    w, h = 120+85, 55
    roi = frame[y:y+h, x:x+w]
    # Debug
    cv2.imwrite(f"images/ds{i}.png", roi)
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    _text = pytesseract.image_to_string(gray, lang='eng', config=date_config)
    _text = _text.replace(" ", "")
    text = smart_correct(_text)
    if text != _text:
        print("Correct: {} -> {}".format(_text, text))
    return text.strip()


def get_time_string(frame, i):
    y = 110
    x = 640
    w = 160
    h = 55
    roi = frame[y:y+h, x:x+w]
    # Debug
    cv2.imwrite(f"images/ts{i}.png", roi)
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


def is_header(frame, x, y):
    r,g,b = frame[y, x, 2], frame[y, x, 1], frame[y, x, 0]
    return 253 <= r <= 255 and 250 <= g <= 253 and 224 <= b <= 247


def is_header_border(frame, x, y):
    r,g,b = frame[y, x, 2], frame[y, x, 1], frame[y, x, 0]
    return 185 <= r <= 235 and 180 <= g <= 220 and 60 <= b <= 180


def is_loading(frame, x, y):
    r,g,b = frame[y, x, 2], frame[y, x, 1], frame[y, x, 0]
    return 200 <= r <= 252 and 200 <= g <= 252 and 200 <= b <= 252


def find_headers(frame):
    hh = 42+5
    px = 30
    headers = []
    y = 20  # keep it the same as py
    # height = 1400
    height = frame.shape[0]
    while y < height:
        if is_header(frame, px, y) or is_header_border(frame, px, y):
            headers.append(y)
            y += hh

        y += 1
    return headers


def do_stitch_v2(data):
    n = len(data)
    frames = [x[1] for x in data]
    i = data[0][0]
    print("do stitch", len(frames))
    stitcher = cv2.createStitcher(mode=cv2.Stitcher_SCANS) if imutils.is_cv3() else cv2.Stitcher_create(mode=cv2.Stitcher_SCANS)

    stitched = frames[0]
    for j in range(1, n):
        (status, stitched) = stitcher.stitch([stitched, frames[j]])
        if status != cv2.STITCHER_OK:
            print('Error stitching images: status code %d' % status)
            return
    print("stitched!")
    # Display the stitched image
    write_image(f'images/img_frame{i:04d}_stitched.png', stitched)

    # Debug
    for j, f in data:
        cv2.imwrite(f"images/frame{i:04d}-debug{j}.png", f)


def check_loading(i, frame):
    x = 350-30
    y = 885-260
    w = 180
    h = 180
    points = [
        (x, y),
        (x+w, y),
        (x, y+h),
        (x+w, y+h)
    ]
    # Debug
    # roi = frame[y:y+h, x:x+w]
    # cv2.imwrite(f"images/frame{i}-loading.png", roi)
    print(f"check loading:{i}")
    for xx, yy in points:
        if not is_loading(frame, xx, yy):
            return False

    print("frame {} is loading".format(i))
    return True


def write_image(filename, frame):
    hs = find_headers(frame)
    if len(hs) > 1:
        print("hs > 1", hs)
        offset = 10
        frame = frame[0:hs[1]-offset, :]
    cv2.imwrite(filename, frame)



def run():
    print(date_config)
    print(time_config)
    video = cv2.VideoCapture('RPReplay_Final1682408133.MP4')
    # video = cv2.VideoCapture('RPReplay_Final1682069721.MP4')
    # video = cv2.VideoCapture('RPReplay_Final1682069172.MP4')
    # video = cv2.VideoCapture('RPReplay_Final1681627796.MP4')
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    step = 1
    jump = 15
    px = 30
    py = 20

    i = 0
    pre = None
    stitch = False
    to_stitch = []
    stitch_jump = 30
    while i < frame_count:
        ret, frame = video.read()
        # Define the region to crop
        x = 30
        y = 260
        width = 830
        height = 1400

        r,g,b = frame[py+y, px+x, 2], frame[py+y, px+x, 1], frame[py+y, px+x, 0]

        if 253 <= r <= 255 and 245 <= g <= 253 and 224 <= b <= 247:
            # Crop the frame to the specified region
            cropped_frame = frame[y:y+height, x:x+width]

            hs = find_headers(cropped_frame)
            print("frame:{}, {}".format(i, hs))

            ds = get_date_string(cropped_frame, i)
            ds = ds.replace(" ", "")
            if len(ds) < 4:
                print(f"Malformed OCR {ds}. Skipping ...")
                i += 1
                continue

            ts = get_time_string(cropped_frame, i)
            ts = ts.replace(":", "-")

            if len(hs) > 1:
                write_image(f'images/img_frame{i:04d}_{ds}_{ts}.png', cropped_frame)
                # video.set(cv2.CAP_PROP_POS_FRAMES, video.get(cv2.CAP_PROP_POS_FRAMES) + step)
                video.set(cv2.CAP_PROP_POS_FRAMES, video.get(cv2.CAP_PROP_POS_FRAMES) + jump)
                i += jump
                continue

            if stitch:
                to_stitch.append((i, cropped_frame))
            else:
                # Start
                stitch = True
                print(i, "start stitch")
                to_stitch = [(i, cropped_frame)]
            video.set(cv2.CAP_PROP_POS_FRAMES, video.get(cv2.CAP_PROP_POS_FRAMES) + stitch_jump)
            i += stitch_jump

        else:
            if not stitch:
                i += 1
                continue

            cropped_frame = frame[y:y+height, x:x+width]
            if check_loading(i, cropped_frame):
                video.set(cv2.CAP_PROP_POS_FRAMES, video.get(cv2.CAP_PROP_POS_FRAMES) + 5)
                i += 5
                continue

            # Stitch on
            hs = find_headers(cropped_frame)

            if len(hs) >= 1:
                # End
                print(i, "end stitch")
                stitch = False
                to_stitch.append((i, cropped_frame))
                do_stitch_v2(to_stitch)
                to_stitch = []
            else:
                print(i, "middle...")
                to_stitch.append((i, cropped_frame))

            video.set(cv2.CAP_PROP_POS_FRAMES, video.get(cv2.CAP_PROP_POS_FRAMES) + stitch_jump)
            i += stitch_jump


if __name__ == '__main__':
    run()
