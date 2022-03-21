import tkinter as tk
import tkinter.filedialog

from wide import widen_webm


def show_ui():
    window = tk.Tk()
    window.title("WebM Widener")
    window.geometry("450x350")

    # main frame to contain everything
    frame_main = tk.Label(window)
    frame_main.pack()

    # draws info labels for visual progress
    frame_info = tk.Label(frame_main)
    frame_info.grid(row=2)

    lbl_f = tk.Label(frame_info, text="File: ")
    lbl_f.pack()
    lbl_file = tk.Label(frame_info, text="-")
    lbl_file.pack(fill=tk.BOTH)

    lbl_u = tk.Label(frame_info, text="Status: ")
    lbl_u.pack()
    lbl_update = tk.Label(frame_info, text="-")
    lbl_update.pack(fill=tk.BOTH)

    # opens file picker
    def pick_file():
        file_dir = tkinter.filedialog.askopenfilename(
            initialdir="./", title="Select File", filetypes=(("WebM files", "*.webm"), ("Image files", "*.png"), ("All files", "*"))
        )
        lbl_file["text"] = file_dir
        window.update()
    # end_pick_file

    # populate radio buttons for selecting input type
    var_input = tk.IntVar()

    frame_input = tk.LabelFrame(frame_main, text='Input Type')
    frame_input.grid(row=3)

    tk.Radiobutton(frame_input, text='WebM',
                   value=0, variable=var_input).pack()
    tk.Radiobutton(frame_input, text='Image (only png supported)',
                   value=1, variable=var_input).pack(anchor=tk.W)

    # populate radio buttons for selecting encoder type
    var_encoder = tk.StringVar()

    frame_encoder = tk.LabelFrame(frame_main, text='Video Encoder')
    frame_encoder.grid(row=4)

    tk.Radiobutton(frame_encoder, text='libvpx (VP8, for posting on imageboards)',
                   value="libvpx", variable=var_encoder).pack()
    tk.Radiobutton(frame_encoder, text='libvpx-vp9 (VP9)',
                   value="libvpx-vp9", variable=var_encoder).pack(anchor=tk.W)

    # draws buttons for selecting file and starting widening
    btn_file = tk.Button(text="Select File", command=pick_file)
    btn_file.pack()

    def widen_file():
        if var_input.get() == 0:
            widen_webm(window, lbl_update, lbl_file["text"], var_encoder.get())
        else:
            print("Do image here")

    btn_widen = tk.Button(text="Start Widening",
                          command=widen_file)
    btn_widen.pack(pady=2)

    window.mainloop()


if __name__ == "__main__":
    show_ui()
