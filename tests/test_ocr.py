#!/usr/bin/env python3

import pytest
import unittest


from geekdadgo.ocr import smart_correct, text2datetime


def test_smart_correct_prefix_comma():
    ds = ",MAR29"
    r = smart_correct(ds)
    assert r == "MAR29", "Failed to correct prefix comma"


def test_smart_correct_number_in_month():
    ds = "MA229"
    r = smart_correct(ds)
    assert r == "MAR29", "Failed to correct number in month"


def test_text2datetime():
    dt = text2datetime("NOV15,2022 14:39")
    assert dt.year == 2022
    assert dt.month == 11
    assert dt.day == 15
    assert dt.hour == 14
    assert dt.minute == 39

    dt = text2datetime("2022 NOV15 14:39")
    assert dt.year == 2022
    assert dt.month == 11
    assert dt.day == 15
    assert dt.hour == 14
    assert dt.minute == 39
