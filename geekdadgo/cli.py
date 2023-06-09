#!/usr/bin/env python3

import logging
from pathlib import Path

import click
import cv2
from exiftool import ExifToolHelper

from geekdadgo.config import Config
from geekdadgo.detect import check_color, check_loading, find_headers
from geekdadgo.img import do_stitch, write_image, split_images
from geekdadgo.log import setup_logger
from geekdadgo.ocr import (
    get_date_string, get_time_string, text2datetime, datetime2text
)


@click.group()
def main():
    pass


@main.command(
    help="Update the DateTimeOriginal of png images in the given directory by parsing the filename in a format like *_2023-02-13T14-40-00.png"
)
@click.option('--images-directory', '-i', help="Directory path of the image files to update.")
def update_dto(images_directory):
    p = Path(images_directory)
    with ExifToolHelper() as et:
        for image_path in p.rglob("*.[jpg jpeg png]*"):
            image_posixpath = image_path.as_posix()
            dt_str = image_path.stem.split("_")[-1]
            dt_str = dt_str.replace("-", ":").replace("T", " ")
            logging.info(f"Updating DateTimeOriginal to {dt_str} for {image_path}.")
            et.set_tags(
                [image_posixpath],
                tags={"DateTimeOriginal": dt_str},
                params=["-P", "-overwrite_original"]
            )


@main.command()
@click.option('--index', '-n', type=int, help="Frame index to get.")
@click.option('--mp4-filepath', '-i', help="Path of MP4 file to process.")
@click.option('--output', '-o', help="Output image file path.")
def getframe(index, mp4_filepath, output):
    video = cv2.VideoCapture(mp4_filepath)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    video.set(cv2.CAP_PROP_POS_FRAMES, video.get(cv2.CAP_PROP_POS_FRAMES) + index)
    ret, frame = video.read()
    cv2.imwrite(output, frame)


@main.command()
@click.option('--mp4-filepath', '-i', help="Path of MP4 file to process.")
@click.option('--output-dir', '-o', default="images", help="Output dir for extracted images.")
@click.option(
    '-v', '--verbose',
    count=True,
    help='''Verbose.\n
-v\tWARN log.\n
-vv\tINFO log.\n
-vvv\tDEBUG log.\n
-vvvv\tAll the log.'''
)
@click.option(
    '-c', '--config-path',
    help=f'''Configuration file path.\n
[1] .{__name__}.conf\n
[2] ~/.{__name__}.conf\n
[3] --config-path
'''
)
@click.option(
    '--log-file',
    help='Path of log file.'
)
def run(mp4_filepath, output_dir, verbose, config_path, log_file):
    logger = setup_logger(__name__, verbose=verbose, log_file=log_file)

    config = Config('geekdadgo')
    config.read(config_path)

    logger.info('verbose: {}'.format(verbose))
    logger.info('input: {}'.format(mp4_filepath))
    logger.info('output: {}'.format(output_dir))
    logger.info("debug mode: {}".format(config.data["app"]["debug"]))

    inputfile = Path(mp4_filepath)
    source = inputfile.stem

    video = cv2.VideoCapture(mp4_filepath)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    logger.info("total frames: {}".format(frame_count))

    output_path = Path(output_dir)

    key_jump = config.data["key-frame-scan"]["jump"]
    stitch_jump = config.data["stitch-scan"]["jump"]

    px = config.data["key-frame-scan"]["x"]
    py = config.data["key-frame-scan"]["y"]

    i = 0
    stitch = False
    to_stitch = []
    pre_dt = None
    last_frame = None
    last_i = 0
    while i < frame_count:
        ret, frame = video.read()

        if frame is None:
            logger.warn("none frame found: {}".format(i))
            break

        last_frame = frame
        last_i = i

        # Define the region to crop
        x = config.data["screen-crop"]["x"]
        y = config.data["screen-crop"]["y"]
        width = config.data["screen-crop"]["width"]
        height = config.data["screen-crop"]["height"]

        if check_color(frame, px+x, py+y, 'header', config):
            # Crop the frame to the specified region
            cropped_frame = frame[y:y+height, x:x+width]

            hs = find_headers(cropped_frame, config)
            logger.info("frame:{}, {}".format(i, hs))

            ds = get_date_string(cropped_frame, i, config)
            ds = ds.replace(" ", "")
            ts = get_time_string(cropped_frame, i, config)

            dt = text2datetime(f"{ds} {ts}")
            if not dt:
                logging.warn(f"Failed to parse datetime for the image since frame {i}")
                i += 1
                continue
            elif dt == pre_dt:
                logging.warn(f"Duplicate frame found at {i} for datetime:{dt}. Skipping ...")
                # video.set(cv2.CAP_PROP_POS_FRAMES, video.get(cv2.CAP_PROP_POS_FRAMES) + key_jump)
                #
                i += key_jump
                video.set(cv2.CAP_PROP_POS_FRAMES, i)
                continue

            pre_dt = dt

            dt_text = datetime2text(dt)
            dt_text = dt_text.replace(":", "-")

            if len(hs) > 1:
                filename_format = config.data["app"]["output_filename_format"]
                outputfile = output_path / filename_format.format(
                    source=source,
                    i=i,
                    tag="n",
                    dt_text=dt_text
                )
                write_image(outputfile.as_posix(), cropped_frame, config)
                # video.set(cv2.CAP_PROP_POS_FRAMES, video.get(cv2.CAP_PROP_POS_FRAMES) + key_jump)
                i += key_jump
                video.set(cv2.CAP_PROP_POS_FRAMES, i)
                continue

            if stitch:
                to_stitch.append((i, cropped_frame))
            else:
                # Start
                stitch = True
                logger.info("start stitch: {}".format(i))
                to_stitch = [(i, cropped_frame)]
            # video.set(cv2.CAP_PROP_POS_FRAMES, video.get(cv2.CAP_PROP_POS_FRAMES) + stitch_jump)
            i += stitch_jump
            video.set(cv2.CAP_PROP_POS_FRAMES, i)

        else:
            if not stitch:
                i += 1
                continue

            cropped_frame = frame[y:y+height, x:x+width]
            if check_loading(i, cropped_frame, config):
                # video.set(cv2.CAP_PROP_POS_FRAMES, video.get(cv2.CAP_PROP_POS_FRAMES) + 5)
                i += 5
                video.set(cv2.CAP_PROP_POS_FRAMES, i)
                continue

            # Stitch on
            hs = find_headers(cropped_frame, config)

            if len(hs) >= 1:
                # End
                logger.info(format("end stitch: {}".format(i)))
                stitch = False
                to_stitch.append((i, cropped_frame))
                do_stitch(to_stitch, output_path, source, config)
                to_stitch = []
            else:
                logger.info("middle: {}".format(i))
                to_stitch.append((i, cropped_frame))

            # video.set(cv2.CAP_PROP_POS_FRAMES, video.get(cv2.CAP_PROP_POS_FRAMES) + stitch_jump)
            i += stitch_jump
            video.set(cv2.CAP_PROP_POS_FRAMES, i)

    if to_stitch:
        # End
        logger.info(format("end stitch out of while loop: {}".format(i)))
        do_stitch(to_stitch, output_path, source, config)
    elif last_frame is not None:
        cropped_frame = last_frame[y:y+height, x:x+width]
        split_images(cropped_frame, last_i, config, output_path, source, pre_dt)


if __name__ == '__main__':
    main()
