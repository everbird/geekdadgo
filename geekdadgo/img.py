#!/usr/bin/env python3

import cv2
import imutils
import logging

from geekdadgo.detect import find_headers
from geekdadgo.ocr import (
    get_date_string, get_time_string, text2datetime, datetime2text
)


def do_stitch(data, output_path, source, config):
    n = len(data)
    frames = [x[1] for x in data]
    i = data[0][0]
    logging.debug("do stitch: {}".format(len(frames)))
    stitcher = cv2.createStitcher(mode=cv2.Stitcher_SCANS) \
        if imutils.is_cv3() \
        else cv2.Stitcher_create(mode=cv2.Stitcher_SCANS)

    # Get ts and ds from the first image
    stitched = frames[0]
    ds = get_date_string(stitched, i, config)
    ds = ds.replace(" ", "")
    ts = get_time_string(stitched, i, config)
    dt = text2datetime(f"{ds} {ts}")
    if not dt:
        logging.error(f"Failed to parse datetime for this stitched image since frame {i}")
        return
    dt_text = datetime2text(dt)
    dt_text = dt_text.replace(":", "-")

    for j in range(1, n):
        (status, stitched) = stitcher.stitch([stitched, frames[j]])
        if status != cv2.STITCHER_OK:
            logging.error('Error stitching images: status code %d' % status)
            return
    logging.debug("stitched!")
    # Display the stitched image
    filename_format = config.data["app"]["output_filename_format"]
    outputfile = output_path / filename_format.format(
        source=source,
        i=i,
        tag="s",
        dt_text=dt_text
    )
    write_image(outputfile.as_posix(), stitched, config)

    # Debug
    if config.data["app"]["debug"]:
        for j, f in data:
            cv2.imwrite(f"images/frame{i:04d}-debug{j}.png", f)


def split_images(frame, index, config, output_path, source, pre_dt):
    hs = find_headers(frame, config)
    logging.debug("frame to split:{}, {}".format(index, hs))
    write_image("images/last.png", frame, config, crop=False)
    filename_format = config.data["app"]["output_filename_format"]
    offset = config.data["key-frame-scan"]["crop_offset"]
    py = config.data["key-frame-scan"]["y"]
    header_count = len(hs)
    for i, header in enumerate(hs):
        logging.debug(f"header: {header}")
        start = header-py if header > py else 0
        if i == header_count-1:
            cropped_frame = frame[start:, :]
        else:
            cropped_frame = frame[start:hs[i+1]-offset, :]

        ds = get_date_string(cropped_frame, i, config)
        ds = ds.replace(" ", "")
        ts = get_time_string(cropped_frame, i, config)

        dt = text2datetime(f"{ds} {ts}")
        if pre_dt == dt:
            logging.debug(f"Skip {i} {header} since detected dt {dt} is the same as pre_dt {pre_dt}")
            continue

        dt_text = datetime2text(dt)
        dt_text = dt_text.replace(":", "-")

        outputfile = output_path / filename_format.format(
            source=source,
            i=index,
            tag=f"m{i}",
            dt_text=dt_text
        )
        write_image(outputfile.as_posix(), cropped_frame, config, crop=False)


def write_image(filename, frame, config, crop=True):
    if crop:
        hs = find_headers(frame, config)
        if len(hs) > 1:
            logging.debug("Found more than 1 headers: {}".format(hs))
            offset = config.data["key-frame-scan"]["crop_offset"]
            frame = frame[0:hs[1]-offset, :]
    cv2.imwrite(filename, frame)
