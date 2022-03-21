from ast import Str
from PIL import Image
import ffmpeg
import tkinter as tk

import glob
import math
import os

from consts import MAX_HEIGHT, WORKING_FOLDER
from wide_options import WideOptions


# global variables to update ui
main_window: tk.Tk = None
lbl: tk.Label = None


def widen_webm(window: tk.Tk, lbl_status: tk.Label, w_options: WideOptions):
    global main_window, lbl

    # quits if no file specified
    if w_options.file_dir == "":
        return

    # keeping reference to ui globally
    main_window = window
    lbl = lbl_status

    # find frame count and framerate of video
    w_options.frames = get_frame_count(w_options)
    w_options.framerate = get_framerate(w_options)

    # splits webm into individual frames
    split_video(w_options)

    # manipulates frame sizes into being WIDE incrementally
    widen_frames(w_options)

    # converts frames into their own individual video
    frame_to_webm(w_options)

    # concatenates all videos together, keeping the WIDE resolution for each frame
    # TODO find a way to do it natively for ffmpeg-python
    concat_webm(w_options)

    # cleanup crew
    clean_up()
# end_widen


def update_status_lbl(update_str: str, col: str = "#fff"):
    lbl["text"] = update_str
    lbl.config(fg=col)
    main_window.update()


def get_frame_count(w_options: WideOptions) -> int:
    probe = ffmpeg.probe(w_options.file_dir)
    duration = float(probe["format"]["duration"])
    true_framerate = probe["streams"][0]["r_frame_rate"].split("/")
    framerate = float(true_framerate[0]) / float(true_framerate[1])
    return math.floor(duration * framerate)
# end_get_frame_count


def get_framerate(w_options: WideOptions) -> float:
    probe = ffmpeg.probe(w_options.file_dir)
    true_framerate = probe["streams"][0]["r_frame_rate"].split("/")
    return float(true_framerate[0]) / float(true_framerate[1])
# end_get_frame_count


def split_video(w_options: WideOptions):
    update_status_lbl("Splitting video into frames...")

    if not os.path.exists(WORKING_FOLDER):
        os.mkdir(WORKING_FOLDER)

    ffmpeg.input(w_options.file_dir)\
        .output(f"{WORKING_FOLDER}/frame%d.jpg", start_number=0)\
        .run(quiet=True)
# end_split_video


def widen_frames(w_options: WideOptions):
    global MAX_HEIGHT

    for i in range(w_options.frames):
        img = Image.open(f"{WORKING_FOLDER}/frame{i}.jpg")

        new_height = img.height if img.height < MAX_HEIGHT else MAX_HEIGHT

        new_width = img.width + i * w_options.widen_rate \
            if img.height < MAX_HEIGHT else math.floor(img.width * MAX_HEIGHT / img.height) + i * w_options.widen_rate

        img_resized = img.resize((new_width, new_height))
        img_resized.save(f"{WORKING_FOLDER}/frame{i}.jpg")

        print(f"Resizing frame {i} / {w_options.frames-1}")
        update_status_lbl(f"Resizing frame {i} / {w_options.frames-1}")
# end_widen_frames


def frame_to_webm(w_options: WideOptions):
    for i in range(w_options.frames):
        ffmpeg\
            .input(f"{WORKING_FOLDER}/frame{i}.jpg", framerate=w_options.framerate)\
            .output(f"{WORKING_FOLDER}/frame{i}.webm", video_bitrate=w_options.v_bitrate, vcodec=w_options.encoder)\
            .run(quiet=True, overwrite_output=True)

        print(f"Converting frame to video {i} / {w_options.frames-1}")
        update_status_lbl(
            f"Converting frame to video {i} / {w_options.frames-1}")
# end_frame_to_webm


def concat_webm(w_options: WideOptions):
    # WORKING_FOLDER not needed here because it uses the cat.txt's reference directory
    webm_list = [
        f"file 'frame{i}.webm'" for i in range(w_options.frames)
    ]
    concat = "\n".join(webm_list)

    f = open(f"{WORKING_FOLDER}/cat.txt", "w")
    f.write(concat)
    f.close()

    file_name = w_options.file_dir.split("/")[-1]

    update_status_lbl("Concatenating all frames together...")

    os.system(
        f"ffmpeg -y -f concat -safe 0 -i {WORKING_FOLDER}/cat.txt -c copy wide_{w_options.encoder}_{file_name}"
    )

    update_status_lbl("Widening completed!", "#0f0")
# end_concat_webm


def clean_up():
    for file in glob.glob(f"{WORKING_FOLDER}/frame[0-9]*.jpg"):
        os.remove(file)

    for file in glob.glob(f"{WORKING_FOLDER}/frame[0-9]*.webm"):
        os.remove(file)

    os.remove(f"{WORKING_FOLDER}/cat.txt")
    os.rmdir(WORKING_FOLDER)
# end_clean_up
