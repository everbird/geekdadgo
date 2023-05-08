#!/usr/bin/env python3

import click
import cv2
import logging

from pathlib import Path

from geekdadgo.config import Config
from geekdadgo.detect import check_color, check_loading, find_headers
from geekdadgo.img import do_stitch, write_image
from geekdadgo.log import setup_logger
from geekdadgo.ocr import get_date_string, get_time_string


@click.group()
def cli():
    pass


@cli.command()
@click.option('--mp4-file', '-i', help="Path of MP4 file to process.")
@click.option('--output-dir', '-o', default="images", help="Output dir for extracted images.")
@click.option(
    '-v', '--verbose',
    count=True,
    help='''Verbose.
-v\tWARN log.
-vv\tINFO log.
-vvv\tDEBUG log.
-vvvv\tAll the log.'''
)
@click.option(
    '-c', '--config-path',
    help=f'''Configuration file path.
[1] .{__name__}.conf
[2] ~/.{__name__}.conf
[3] --config-path
'''
)
def run(mp4_filepath, output_dir, verbose, config_path):
    logger = setup_logger(__name__, verbose=verbose, log_file=log_file)

    config = Config('easy_rate')
    config.read(config_path)

    logger.info('verbose: {}'.format(verbose))
    logger.info('input: {}'.format(mp4_filepath))
    logger.info('output: {}'.format(output_dir))

    logger.info('format: {}'.format(format))
    logger.info('concurrent: {}'.format(concurrent))

    video = cv2.VideoCapture(mp4_filepath)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    output_path = Path(output_dir)

    key_jump = config.data["key-frame-scan"]["jump"]
    stitch_jump = config.data["stitch-scan"]["jump"]

    px = config.data["key-frame-scan"]["x"]
    py = config.data["key-frame-scan"]["y"]

    i = 0
    stitch = False
    to_stitch = []
    while i < frame_count:
        ret, frame = video.read()

        # Define the region to crop
        x = config.data["screen-crop"]["x"]
        y = config.data["screen-crop"]["y"]
        width = config.data["screen-crop"]["width"]
        height = config.data["screen-crop"]["height"]

        if check_color(frame, px+x, py+y, 'header', config):
            # Crop the frame to the specified region
            cropped_frame = frame[y:y+height, x:x+width]

            hs = find_headers(cropped_frame, config)
            print("frame:{}, {}".format(i, hs))

            ds = get_date_string(cropped_frame, i, config)
            ds = ds.replace(" ", "")
            if len(ds) < 4:
                print(f"Malformed OCR {ds}. Skipping ...")
                i += 1
                continue

            ts = get_time_string(cropped_frame, i, config)
            ts = ts.replace(":", "-")

            if len(hs) > 1:
                write_image(output_path / f'img_frame{i:04d}_{ds}_{ts}.png', cropped_frame, config)
                video.set(cv2.CAP_PROP_POS_FRAMES, video.get(cv2.CAP_PROP_POS_FRAMES) + key_jump)
                i += key_jump
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
            if check_loading(i, cropped_frame, config):
                video.set(cv2.CAP_PROP_POS_FRAMES, video.get(cv2.CAP_PROP_POS_FRAMES) + 5)
                i += 5
                continue

            # Stitch on
            hs = find_headers(cropped_frame, config)

            if len(hs) >= 1:
                # End
                print(i, "end stitch")
                stitch = False
                to_stitch.append((i, cropped_frame))
                do_stitch(to_stitch, config)
                to_stitch = []
            else:
                print(i, "middle...")
                to_stitch.append((i, cropped_frame))

            video.set(cv2.CAP_PROP_POS_FRAMES, video.get(cv2.CAP_PROP_POS_FRAMES) + stitch_jump)
            i += stitch_jump


if __name__ == '__main__':
    cli()
