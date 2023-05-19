#!/usr/bin/env python3

import pytest
import unittest


from geekdadgo.ocr import smart_correct


def test_smart_correct_prefix_comma():
    ds = ",MAR29"
    r = smart_correct(ds)
    assert r == "MAR29", "Failed to correct prefix comma"


def test_smart_correct_number_in_month():
    ds = "MA229"
    r = smart_correct(ds)
    assert r == "MAR29", "Failed to correct number in month"
