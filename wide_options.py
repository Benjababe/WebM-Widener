class WideOptions():
    file_dir: str
    encoder: str
    v_bitrate: int
    widen_rate: int
    frame_count: int = 1
    framerate: float = 24.0
    duration: float = 10

    def __init__(self, file_dir: str, encoder: str, v_bitrate: int, widen_rate: int = 2):
        super().__init__()
        self.file_dir = file_dir
        self.encoder = encoder
        self.v_bitrate = v_bitrate
        self.widen_rate = widen_rate
