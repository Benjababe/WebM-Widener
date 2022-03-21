import tkinter as tk
import tkinter.filedialog
from consts import BG_PATH, ICON_PATH

from wide import widen_webm
from wide_options import WideOptions


def show_ui():
    window = tk.Tk()
    window.title("WebM Widener")
    window.iconbitmap(ICON_PATH)
    window.geometry("450x350")

    # main frame to contain everything
    bg = tk.PhotoImage(file=BG_PATH)
    frame_main = tk.Label(window, image=bg)
    frame_main.pack()

    frame_file = tk.LabelFrame(frame_main, text='File')
    frame_file.grid(row=1)
    lbl_file = tk.Label(frame_file, text="-")
    lbl_file.pack(padx=6)

    frame_status = tk.LabelFrame(frame_main, text='Status')
    frame_status.grid(row=2)
    lbl_status = tk.Label(frame_status, text="-")
    lbl_status.pack(padx=6)

    # opens file picker
    def pick_file():
        file_dir = tkinter.filedialog.askopenfilename(
            initialdir="./", title="Select File", filetypes=(("WebM files", "*.webm"), ("Image files", "*.png"), ("All files", "*"))
        )
        lbl_file["text"] = file_dir
        window.update()
    # end_pick_file

    # adds file picker button to file frame
    btn_file = tk.Button(frame_file, text="Select File", command=pick_file)
    btn_file.pack(padx=6, pady=6)

    # populate radio buttons for selecting input type
    var_input = tk.IntVar()

    frame_input = tk.LabelFrame(frame_main, text='Input Type')
    frame_input.grid(row=3)

    tk.Radiobutton(frame_input, text='WebM',
                   value=0, variable=var_input).pack()
    tk.Radiobutton(frame_input, text='Image (currently not supported)',
                   value=1, variable=var_input).pack(anchor=tk.W)

    # populate radio buttons for selecting encoder type
    var_encoder = tk.StringVar()

    frame_encoder = tk.LabelFrame(frame_main, text='Video Encoder')
    frame_encoder.grid(row=4)

    tk.Radiobutton(frame_encoder, text='libvpx (VP8, for posting on imageboards)',
                   value="libvpx", variable=var_encoder).pack()
    tk.Radiobutton(frame_encoder, text='libvpx-vp9 (VP9)',
                   value="libvpx-vp9", variable=var_encoder).pack(anchor=tk.W)

    # draws textbox for bitrate entry
    frame_bitrate = tk.LabelFrame(frame_main, text='Video Bitrate (bps)')
    frame_bitrate.grid(row=5)

    txt_bitrate = tk.Entry(frame_bitrate)
    txt_bitrate.insert(0, 50000)
    txt_bitrate.pack(padx=6, pady=6)

    def widen_file():
        wide_options = WideOptions(
            lbl_file["text"], var_encoder.get(), int(txt_bitrate.get())
        )

        if var_input.get() == 0:
            widen_webm(window, lbl_status, wide_options)
        else:
            print("Do image here")
    # end_widen_file

    # draws buttons for widening process
    btn_widen = tk.Button(frame_main, text="Start Widening",
                          command=widen_file)
    btn_widen.grid(row=7, pady=6)

    window.mainloop()


if __name__ == "__main__":
    show_ui()
