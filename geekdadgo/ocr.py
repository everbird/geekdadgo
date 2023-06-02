#!/usr/bin/env python3

import cv2
import logging
import pytesseract
from dateutil import parser

from datetime import datetime


def get_date_string(frame, i, config):
    ocr = config.data["ocr"]["date"]
    x, y = ocr["x"], ocr["y"]
    w, h = ocr["width"], ocr["height"]
    roi = frame[y:y+h, x:x+w]
    # Debug
    if config.data["app"]["debug"]:
        cv2.imwrite(f"images/ds{i}.png", roi)
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    _text = pytesseract.image_to_string(gray, lang='eng', config=config.ocr_date_config)
    _text = _text.replace(" ", "")
    text = smart_correct(_text)
    if text != _text:
        logging.debug("Correction: {} -> {}".format(_text, text))
    return text.strip()


def get_time_string(frame, i, config):
    ocr = config.data["ocr"]["time"]
    x, y = ocr["x"], ocr["y"]
    w, h = ocr["width"], ocr["height"]
    roi = frame[y:y+h, x:x+w]
    # Debug
    if config.data["app"]["debug"]:
        cv2.imwrite(f"images/ts{i}.png", roi)
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    _text = pytesseract.image_to_string(gray, lang='eng', config=config.ocr_time_config)
    _text = _text.replace(" ", "")
    return _text.strip()


def smart_correct(text):
    day_corrections = {
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
    month_corrections = {v:k for k,v in day_corrections.items()}
    if text.startswith(","):
        text = text[1:]

    month = text[:3]
    rm = ""
    for ch in month:
        if ch in month_corrections:
            rm += month_corrections[ch]
        else:
            rm += ch

    day = text[3:]
    rd = ""
    for ch in day:
        if ch in day_corrections:
            rd += day_corrections[ch]
        else:
            rd += ch
    return "{}{}".format(rm, rd)


def text2datetime(text):
    if "," in text:
        ds, ts = text.split(" ")
        date, year = ds.split(",")
        text = f"{year[:4]} {date} {ts}"
    try:
        dt = parser.parse(text, fuzzy=True)
        if dt.year == 1900:
            current_year = datetime.now().year
            dt = dt.replace(year=current_year)
        return dt
    except ValueError as ex:
        logging.error(f"Failed to parse text to datetime: {text}. Detailed error message {ex}")


def datetime2text(dt):
    datetime_format = "%Y-%m-%dT%H:%M:%S"
    return dt.strftime(datetime_format)
