#!/usr/bin/env python3

import cv2
import pytesseract


def get_date_string(frame, i, config):
    ocr = config.data["ocr"]["date"]
    x, y = ocr["x"], ocr["y"]
    w, h = ocr["width"], ocr["height"]
    roi = frame[y:y+h, x:x+w]
    # Debug
    cv2.imwrite(f"images/ds{i}.png", roi)
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    _text = pytesseract.image_to_string(gray, lang='eng', config=config.ocr_date_config)
    _text = _text.replace(" ", "")
    text = smart_correct(_text)
    if text != _text:
        print("Correct: {} -> {}".format(_text, text))
    return text.strip()


def get_time_string(frame, i, config):
    ocr = config.data["ocr"]["time"]
    x, y = ocr["x"], ocr["y"]
    w, h = ocr["width"], ocr["height"]
    roi = frame[y:y+h, x:x+w]
    # Debug
    cv2.imwrite(f"images/ts{i}.png", roi)
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    _text = pytesseract.image_to_string(gray, lang='eng', config=config.ocr_time_config)
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
