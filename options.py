class Options():
    file_dir: str
    encoder: str
    file_type: int
    v_bitrate: int
    pixel_x_rate: int
    pixel_y_rate: int
    frame_count: int = 1
    frame_rate: float = 24.0
    duration: float = 10

    def __init__(self, file_dir: str, encoder: str, file_type: int,
                 v_bitrate: int, pixel_x_rate: int = 0, pixel_y_rate: int = 0):
        super().__init__()
        self.file_dir = file_dir
        self.encoder = encoder
        self.file_type = file_type
        self.v_bitrate = v_bitrate
        self.pixel_x_rate = pixel_x_rate
        self.pixel_y_rate = pixel_y_rate
