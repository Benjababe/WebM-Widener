from PIL import Image
import ffmpeg
import tkinter as tk

import glob
import re
import os

from consts import TYPE_WEBM, TYPE_IMG, MAX_HEIGHT, WORKING_FOLDER
from wide_options import WideOptions


# global variables to update ui
main_window: tk.Tk = None
main_var: tk.StringVar = None


def widen(window: tk.Tk, var_status: tk.StringVar, w_options: WideOptions):
    global main_window, main_var

    # quits if no file specified
    if w_options.file_dir == "":
        return

    check_working_dir()

    # keeping reference to ui globally
    main_window = window
    main_var = var_status

    if w_options.file_type == TYPE_WEBM:
        w_options.frame_count = get_frame_count(w_options)
        w_options.frame_rate = get_framerate(w_options)
        split_video(w_options)
        widen_frames(w_options)

    elif w_options.file_type == TYPE_IMG:
        w_options.frame_count = int(w_options.duration * w_options.frame_rate)
        generate_frames(w_options)

    frame_to_webm(w_options)
    concat_webm(w_options)
    clean_up()
# end_widen


def update_lbl_status(update_str: str):
    """ Updates status label on main tkinter window

    Args:
        update_str (str): String to set label to
    """

    global main_window, main_var

    print(update_str)

    main_var.set(update_str)
    main_window.update()
# end_update_status_lbl


def check_working_dir():
    if not os.path.exists(WORKING_FOLDER):
        os.mkdir(WORKING_FOLDER)
# end_check_working_dir


def get_frame_count(w_options: WideOptions) -> int:
    probe = ffmpeg.probe(w_options.file_dir)
    duration = float(probe["format"]["duration"])
    true_framerate = probe["streams"][0]["r_frame_rate"].split("/")
    framerate = float(true_framerate[0]) / float(true_framerate[1])
    return int(duration * framerate)
# end_get_frame_count


def get_framerate(w_options: WideOptions) -> float:
    probe = ffmpeg.probe(w_options.file_dir)
    true_framerate = probe["streams"][0]["r_frame_rate"].split("/")
    return float(true_framerate[0]) / float(true_framerate[1])
# end_get_frame_count


def generate_frames(w_options: WideOptions):
    """ Create incrementally widening frames from initial image.

    Args:
        w_options (WideOptions): WideOptions object, contains initial image directory, widen rate and frame count
    """

    base_img = Image.open(w_options.file_dir)

    if base_img.height > MAX_HEIGHT:
        new_height = MAX_HEIGHT
        new_width = int(base_img.width * MAX_HEIGHT / base_img.height)
        base_img = base_img.resize((new_width, new_height))

    for i in range(w_options.frame_count):
        x_inc = (i * w_options.widen_rate)
        new_img = base_img.resize((base_img.width + x_inc, base_img.height))
        new_img.save(f"{WORKING_FOLDER}/frame{i}.jpg")

        update_lbl_status(f"Resizing frame {i} / {w_options.frame_count-1}")
# end_generate_frames


def split_video(w_options: WideOptions):
    """ Splits the initial video into individual frames

    Args:
        w_options (WideOptions): WideOptions object, contains initial video directory
    """

    update_lbl_status("Splitting video into frames...")

    ffmpeg.input(w_options.file_dir)\
        .output(f"{WORKING_FOLDER}/frame%d.jpg", start_number=0)\
        .run(quiet=True)
# end_split_video


def widen_frames(w_options: WideOptions):
    """ Widens the frames generated from splitting the video

    Args:
        w_options (WideOptions): WideOptions object, contains frame count and widen rate
    """

    global MAX_HEIGHT

    for i in range(w_options.frame_count):
        img = Image.open(f"{WORKING_FOLDER}/frame{i}.jpg")

        new_height = img.height if img.height < MAX_HEIGHT else MAX_HEIGHT

        new_width = img.width + i * w_options.widen_rate \
            if img.height < MAX_HEIGHT else int(img.width * MAX_HEIGHT / img.height) + i * w_options.widen_rate

        img_resized = img.resize((new_width, new_height))
        img_resized.save(f"{WORKING_FOLDER}/frame{i}.jpg")

        update_lbl_status(f"Resizing frame {i} / {w_options.frame_count-1}")
# end_widen_frames


def frame_to_webm(w_options: WideOptions):
    """ Converts each widened frame to a single frame webm video

    Args:
        w_options (WideOptions): WideOptions object, contains frame count, framerate, video bitrate and video encoder
    """

    for i in range(w_options.frame_count):
        ffmpeg\
            .input(f"{WORKING_FOLDER}/frame{i}.jpg", framerate=w_options.frame_rate)\
            .output(f"{WORKING_FOLDER}/frame{i}.webm", video_bitrate=w_options.v_bitrate, vcodec=w_options.encoder)\
            .run(quiet=True, overwrite_output=True)

        update_lbl_status(
            f"Converting frame to video {i} / {w_options.frame_count-1}"
        )
# end_frame_to_webm


def concat_webm(w_options: WideOptions):
    """ Combined all single frame webms into a full length video

    Args:
        w_options (WideOptions): WideOptions object, contains frame count, initial file directory and video encoder
    """

    # WORKING_FOLDER not needed here because it uses the cat.txt's reference directory
    webm_list = [
        f"file 'frame{i}.webm'" for i in range(w_options.frame_count)
    ]
    concat = "\n".join(webm_list)

    f = open(f"{WORKING_FOLDER}/cat.txt", "w")
    f.write(concat)
    f.close()

    filename_pattern = r"([^\/|\\]*)\.[\w\d]+$"
    filename = re.search(filename_pattern, w_options.file_dir).group(1)

    update_lbl_status("Concatenating all frames together...")

    os.system(
        f"ffmpeg -y -f concat -safe 0 -i {WORKING_FOLDER}/cat.txt -c copy wide_{w_options.encoder}_{filename}.webm"
    )

    update_lbl_status("Widening completed!")
# end_concat_webm


def clean_up():
    """ Removes all generated files during the widening process
    """

    for file in glob.glob(f"{WORKING_FOLDER}/frame[0-9]*.jpg"):
        os.remove(file)

    for file in glob.glob(f"{WORKING_FOLDER}/frame[0-9]*.webm"):
        os.remove(file)

    os.remove(f"{WORKING_FOLDER}/cat.txt")
    os.rmdir(WORKING_FOLDER)
# end_clean_up
