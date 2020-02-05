import os
import subprocess

for root, dirs, files in os.walk("./recordings"):
    for file in files:
        if file.endswith(".mp4"):
            filename = os.path.join(root, file)
            output = os.path.join(root, "output.gif")
            print(output)
            # ffmpeg -ss 5 -i input.wmv -t 10 -pix_fmt rgb24 output.gif
            os.system("ffmpeg -y -ss 5 -i {} -t 10 -pix_fmt rgb24 {}".format(filename, output))
