from PIL import Image
import ffmpeg
import tkinter as tk

import glob
import math
import os

from consts import MAX_HEIGHT, WORKING_FOLDER
from wide_options import WideOptions


def widen_webm(window: tk.Tk, lbl_update: tk.Label, wide_options: WideOptions):
    # quits if no file specified
    if wide_options.file_dir == "":
        return

    # find frame count of video
    wide_options.frames = get_frame_count(wide_options)

    # splits webm into individual frames
    split_video(window, lbl_update, wide_options)

    # manipulates frame sizes into being WIDE incrementally
    widen_frames(window, lbl_update, wide_options)

    # converts frames into their own individual video
    frame_to_webm(window, lbl_update, wide_options)

    # concatenates all videos together, keeping the WIDE resolution for each frame
    # TODO find a way to do it natively for ffmpeg-python
    concat_webm(window, lbl_update, wide_options)

    # cleanup crew
    clean_up()
# end_widen


def get_frame_count(wide_options: WideOptions) -> int:
    probe = ffmpeg.probe(wide_options.file_dir)
    duration = float(probe["format"]["duration"])
    true_framerate = probe["streams"][0]["r_frame_rate"].split("/")
    framerate = float(true_framerate[0]) / float(true_framerate[1])
    return math.floor(duration * framerate)
# end_get_frame_count


def split_video(window: tk.Tk, lbl_update: tk.Label, wide_options: WideOptions):
    lbl_update["text"] = "Splitting video into frames..."
    window.update()

    if not os.path.exists(WORKING_FOLDER):
        os.mkdir(WORKING_FOLDER)

    ffmpeg.input(wide_options.file_dir)\
        .output(f"{WORKING_FOLDER}/frame%d.jpg", start_number=0)\
        .run(quiet=True)
# end_split_video


def widen_frames(window: tk.Tk, lbl_update: tk.Label, wide_options: WideOptions):
    global MAX_HEIGHT

    for i in range(wide_options.frames):
        img = Image.open(f"{WORKING_FOLDER}/frame{i}.jpg")

        new_height = img.height if img.height < MAX_HEIGHT else MAX_HEIGHT

        new_width = img.width + i * wide_options.widen_rate \
            if img.height < MAX_HEIGHT else math.floor(img.width * MAX_HEIGHT / img.height) + i * wide_options.widen_rate

        img_resized = img.resize((new_width, new_height))
        img_resized.save(f"{WORKING_FOLDER}/frame{i}.jpg")

        print(f"Resizing frame {i} / {wide_options.frames-1}")
        lbl_update["text"] = f"Resizing frame {i} / {wide_options.frames-1}"
        window.update()
# end_widen_frames


def frame_to_webm(window: tk.Tk, lbl_update: tk.Label, wide_options: WideOptions):
    for i in range(wide_options.frames):
        ffmpeg\
            .input(f"{WORKING_FOLDER}/frame{i}.jpg", framerate=24)\
            .output(f"{WORKING_FOLDER}/frame{i}.webm", video_bitrate=wide_options.bitrate, vcodec=wide_options.encoder)\
            .run(quiet=True, overwrite_output=True)

        print(f"Converting frame to video {i} / {wide_options.frames-1}")
        lbl_update["text"] = f"Converting frame to video {i} / {wide_options.frames-1}"
        window.update()
# end_frame_to_webm


def concat_webm(window: tk.Tk, lbl_update: tk.Label, wide_options: WideOptions):
    # WORKING_FOLDER not needed here because it uses the cat.txt's reference directory
    webm_list = [
        f"file 'frame{i}.webm'" for i in range(wide_options.frames)
    ]
    concat = "\n".join(webm_list)

    f = open(f"{WORKING_FOLDER}/cat.txt", "w")
    f.write(concat)
    f.close()

    file_name = wide_options.file_dir.split("/")[-1]

    lbl_update["text"] = "Concatenating all frames together..."
    window.update()

    os.system(
        f"ffmpeg -y -f concat -safe 0 -i {WORKING_FOLDER}/cat.txt -c copy wide_{wide_options.encoder}_{file_name}"
    )

    lbl_update["text"] = "Widening completed!"
    window.update()
# end_concat_webm


def clean_up():
    for file in glob.glob(f"{WORKING_FOLDER}/frame[0-9]*.jpg"):
        os.remove(file)

    for file in glob.glob(f"{WORKING_FOLDER}/frame[0-9]*.webm"):
        os.remove(file)

    os.remove(f"{WORKING_FOLDER}/cat.txt")
    os.rmdir(WORKING_FOLDER)
# end_clean_up
