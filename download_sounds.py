import urllib.request
import os

assets_dir = "/Users/prameshluitel/Documents/Marketing Deparment Automation/video-renderer/public/assets"

sounds = {
    "whoosh.mp3": "https://s3.amazonaws.com/freecodecamp/drums/Heater-4_1.mp3",
    "impact.mp3": "https://s3.amazonaws.com/freecodecamp/drums/Kick_n_Hat.mp3",
    "riser.mp3": "https://s3.amazonaws.com/freecodecamp/drums/Cev_H2.mp3",
    "pop.mp3": "https://s3.amazonaws.com/freecodecamp/drums/Heater-1.mp3",
    "glitch.mp3": "https://s3.amazonaws.com/freecodecamp/drums/RP4_KICK_1.mp3",
    "fireworks.mp3": "https://s3.amazonaws.com/freecodecamp/drums/Dsc_Oh.mp3",
    "electronic.mp3": "https://raw.githubusercontent.com/muhammederdem/mini-player/master/mp3/1.mp3",
    "cinematic.mp3": "https://raw.githubusercontent.com/muhammederdem/mini-player/master/mp3/2.mp3",
    "lofi.mp3": "https://raw.githubusercontent.com/muhammederdem/mini-player/master/mp3/3.mp3",
    "upbeat.mp3": "https://raw.githubusercontent.com/muhammederdem/mini-player/master/mp3/4.mp3"
}

for filename, url in sounds.items():
    filepath = os.path.join(assets_dir, filename)
    print(f"Downloading {filename}...")
    try:
        urllib.request.urlretrieve(url, filepath)
    except Exception as e:
        print(f"Failed to download {filename}: {e}")

print("Done!")
