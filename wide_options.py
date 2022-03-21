class WideOptions():
    file_dir: str
    encoder: str
    bitrate: int
    widen_rate: int
    frames: int

    def __init__(self, file_dir: str, encoder: str, bitrate: int, widen_rate: int = 2, frames: int = 1):
        super().__init__()
        self.file_dir = file_dir
        self.encoder = encoder
        self.bitrate = bitrate
        self.widen_rate = widen_rate
        self.frames = frames
