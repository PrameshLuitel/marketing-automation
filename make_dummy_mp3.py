import base64
import os

# Base64 of a very short blank MP3
silent_mp3_b64 = "SUQzBAAAAAAAI1RTU0UAAAAPAAADTGF2ZjU4Ljc2LjEwMAAAAAAAAAAAAAAA//tQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAASW5mbwAAAA8AAAAEAAABIwBMTEzPz8/Pz8/Pz8/Pz8/v7+/v7+/v7+/v7+///wAAOExhdmMzLjEwMAAAAAAAAAAAAAAAQQqEAAAAAAAAAAAAAAABIw=="

mp3_data = base64.b64decode(silent_mp3_b64)
tracks = ["electronic.mp3", "cinematic.mp3", "pop.mp3", "lofi.mp3"]

for t in tracks:
    path = f"video-renderer/public/assets/{t}"
    if not os.path.exists(path):
        with open(path, "wb") as f:
            f.write(mp3_data)
        print(f"Created {path}")
