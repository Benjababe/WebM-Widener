import tkinter as tk
import tkinter.filedialog
import platform

from consts import BG_PATH, ICON_PATH
from process import resize_video
from options import Options


class WebmWidener(tk.Tk):
    def __init__(self):
        super(WebmWidener, self).__init__()

        self.setup_window()
        self.setup_variables()

        self.draw_main_frame()
        self.draw_file_frame()
        self.draw_status_frame()

        self.draw_input_frame()
        self.draw_encoder_frame()
        self.draw_bitrate_frame()

        self.draw_process_btn()
    # end__init__

    def setup_window(self):
        self.title("WebM Widener")
        self.geometry("450x400")

        # i will find a way someday
        if platform.system() != "Linux":
            self.iconbitmap(ICON_PATH)
    # end_setup_window

    def setup_variables(self):
        self.var_file = tk.StringVar(self, value="-")
        self.var_status = tk.StringVar(self, value="-")
        self.var_input = tk.IntVar(self, value=0)
        self.var_encoder = tk.StringVar(self, value="libvpx")
    # end_setup_variables

    def draw_main_frame(self):
        self.bg = tk.PhotoImage(file=BG_PATH)
        self.frame_main = tk.Label(self, image=self.bg)
        self.frame_main.pack()
    # end_draw_main

    def draw_file_frame(self):
        frame_file = tk.LabelFrame(self.frame_main, text='File')
        frame_file.grid(row=1)

        self.lbl_file = tk.Label(frame_file, textvariable=self.var_file)
        self.lbl_file.pack(padx=6)

        btn_file = tk.Button(
            frame_file, text="Select File", command=self.pick_file
        )
        btn_file.pack(padx=6, pady=6)
    # end_draw_file_frame

    def draw_status_frame(self):
        frame_status = tk.LabelFrame(self.frame_main, text='Status')
        frame_status.grid(row=2)

        self.lbl_status = tk.Label(
            frame_status, textvariable=self.var_status
        )
        self.lbl_status.pack(padx=6)
    # end_draw_status_frame

    def pick_file(self):
        filetypes = (
            ("WebM files", "*.webm"),
            ("Image files", "*.jpg *.png"),
            ("All files", "*")
        )
        file_dir = tkinter.filedialog.askopenfilename(
            initialdir="./", title="Select File", filetypes=filetypes)
        self.var_file.set(file_dir)
        self.update()
    # end_pick_file

    def draw_input_frame(self):
        frame_input = tk.LabelFrame(self.frame_main, text='Input Type')
        frame_input.grid(row=3)

        tk.Radiobutton(frame_input, text='WebM',
                       value=0, variable=self.var_input).pack()
        tk.Radiobutton(frame_input, text='Image (png and jpeg supported)',
                       value=1, variable=self.var_input).pack(anchor=tk.W)
    # end_draw_input_frame

    def draw_encoder_frame(self):
        frame_encoder = tk.LabelFrame(self.frame_main, text='Video Encoder')
        frame_encoder.grid(row=4)

        tk.Radiobutton(frame_encoder, text='libvpx (VP8, for posting on imageboards)',
                       value="libvpx", variable=self.var_encoder).pack()
        tk.Radiobutton(frame_encoder, text='libvpx-vp9 (VP9)',
                       value="libvpx-vp9", variable=self.var_encoder).pack(anchor=tk.W)
    # end_draw_encoder_frame

    def draw_bitrate_frame(self):
        frame_bitrate = tk.LabelFrame(
            self.frame_main, text='Video Bitrate (bps)')
        frame_bitrate.grid(row=5)

        self.txt_bitrate = tk.Entry(frame_bitrate)
        self.txt_bitrate.insert(0, 50000)
        self.txt_bitrate.pack(padx=6, pady=6)
    # end_draw_bitrate_frame

    def start_processing(self):
        options = Options(
            self.var_file.get(), self.var_encoder.get(),
            self.var_input.get(), int(self.txt_bitrate.get()),
            pixel_x_rate=-3, pixel_y_rate=0
        )
        resize_video(self, self.var_status, options)
    # end_start_processing

    def draw_process_btn(self):
        btn_process = tk.Button(self.frame_main, text="Process Video",
                                command=self.start_processing)
        btn_process.grid(row=7, pady=6)
    # end_draw_process_btn


if __name__ == "__main__":
    app = WebmWidener()
    app.mainloop()
