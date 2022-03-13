import ffmpeg
import PIL
import tkinter as tk

import glob
import math
import os


MAX_WIDTH = 960
WORKING_FOLDER = "./tmp"


def show_ui():
    window = tk.Tk()

    lbl_f = tk.Label(text="File: ")
    lbl_f.pack()
    lbl_file = tk.Label(text="-")
    lbl_file.pack(fill=tk.BOTH)

    lbl_u = tk.Label(text="Status: ")
    lbl_u.pack()
    lbl_update = tk.Label(text="-")
    lbl_update.pack(fill=tk.BOTH)

    def pick_file():
        file_dir = tk.filedialog.askopenfilename(
            initialdir="./", title="Select webm", filetypes=(("webm files", "*.webm"), ("all files", "*"))
        )
        lbl_file["text"] = file_dir

    btn_file = tk.Button(text="Select file", command=pick_file)
    btn_file.pack()

    btn_widen = tk.Button(text="Widen webm", command=lambda:
                          widen(window, lbl_update, lbl_file["text"]))
    btn_widen.pack()

    window.geometry("400x150")
    window.mainloop()


def widen(window, lbl_update, file_dir, widen_rate=2):
    # quits if no file specified
    if file_dir == "":
        return

    # find frame count of video
    frames = get_frame_count(file_dir)

    # splits webm into individual frames
    split_video(window, lbl_update, file_dir)

    # manipulates frame sizes into being WIDE incrementally
    widen_frames(window, lbl_update, frames, widen_rate)

    # converts frames into their own individual video
    frame_to_webm(window, lbl_update, frames)

    # concatenates all videos together, keeping the WIDE resolution for each frame
    # TODO find a way to do it natively for ffmpeg-python
    concat_webm(window, lbl_update, frames, file_dir)

    # cleanup crew
    clean_up()
# end_widen


def get_frame_count(file_dir: str) -> int:
    probe = ffmpeg.probe(file_dir)
    duration = float(probe["format"]["duration"])
    true_framerate = probe["streams"][0]["r_frame_rate"].split("/")
    framerate = float(true_framerate[0]) / float(true_framerate[1])
    return math.floor(duration * framerate)


def split_video(window: tk.Tk, lbl_update: tk.Label, file_dir: str):
    lbl_update["text"] = "Splitting video into frames..."
    window.update()

    if not os.path.exists(WORKING_FOLDER):
        os.mkdir(WORKING_FOLDER)

    ffmpeg.input(file_dir)\
        .output(f"{WORKING_FOLDER}/frame%d.jpg", start_number=0)\
        .run(quiet=True)
# end_split_video


def widen_frames(window: tk.Tk, lbl_update: tk.Label, frames: int, widen_rate: int):
    global MAX_WIDTH

    for i in range(frames):
        img = PIL.Image.open(f"{WORKING_FOLDER}/frame{i}.jpg")

        new_width = img.width + i * widen_rate \
            if img.width < MAX_WIDTH else MAX_WIDTH + i * widen_rate

        new_height = img.height if img.width < MAX_WIDTH \
            else math.floor(img.height * MAX_WIDTH / img.width)

        img_resized = img.resize((new_width, new_height))
        img_resized.save(f"{WORKING_FOLDER}/frame{i}.jpg")

        print(f"Resizing frame {i} / {frames-1}")
        lbl_update["text"] = f"Resizing frame {i} / {frames-1}"
        window.update()
# end_widen_frames


def frame_to_webm(window: tk.Tk, lbl_update: tk.Label, frames: int):
    for i in range(frames):
        ffmpeg\
            .input(f"{WORKING_FOLDER}/frame{i}.jpg", framerate=24)\
            .output(f"{WORKING_FOLDER}/frame{i}.webm", video_bitrate=100000, vcodec="libvpx")\
            .run(quiet=True, overwrite_output=True)

        print(f"Converting frame to video {i} / {frames-1}")
        lbl_update["text"] = f"Converting frame to video {i} / {frames-1}"
        window.update()
# end_frame_to_webm


def concat_webm(window: tk.Tk, lbl_update: tk.Label, frames: int, file_dir: str):
    # WORKING_FOLDER not needed here because it uses the cat.txt's reference directory
    webm_list = [
        f"file 'frame{i}.webm'" for i in range(frames)
    ]
    concat = "\n".join(webm_list)

    f = open(f"{WORKING_FOLDER}/cat.txt", "w")
    f.write(concat)
    f.close()

    file_name = file_dir.split("/")[-1]

    lbl_update["text"] = "Concatenating all frames together..."
    window.update()

    os.system(
        f"ffmpeg -y -f concat -safe 0 -i {WORKING_FOLDER}/cat.txt -c copy wide_{file_name}"
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


if __name__ == "__main__":
    show_ui()
