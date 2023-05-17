#!/usr/bin/env python3

import cv2
import imutils
import logging

from geekdadgo.detect import find_headers


def do_stitch(data, config):
    n = len(data)
    frames = [x[1] for x in data]
    i = data[0][0]
    logging.debug("do stitch: {}".format(len(frames)))
    stitcher = cv2.createStitcher(mode=cv2.Stitcher_SCANS) \
        if imutils.is_cv3() \
        else cv2.Stitcher_create(mode=cv2.Stitcher_SCANS)

    stitched = frames[0]
    for j in range(1, n):
        (status, stitched) = stitcher.stitch([stitched, frames[j]])
        if status != cv2.STITCHER_OK:
            logging.error('Error stitching images: status code %d' % status)
            return
    logging.debug("stitched!")
    # Display the stitched image
    write_image(f'images/img_frame{i:04d}_stitched.png', stitched, config)

    # Debug
    for j, f in data:
        cv2.imwrite(f"images/frame{i:04d}-debug{j}.png", f)


def write_image(filename, frame, config, crop=True):
    if crop:
        hs = find_headers(frame, config)
        if len(hs) > 1:
            logging.debug("Found more than 1 headers: {}".format(hs))
            offset = config.data["key-frame-scan"]["crop_offset"]
            frame = frame[0:hs[1]-offset, :]
    cv2.imwrite(filename, frame)
