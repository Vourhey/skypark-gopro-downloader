#!/usr/bin/env python3
from goprocam import GoProCamera
from goprocam import constants
from time import sleep
from config import YANDEX_DISK_FOLDER
import os


def main():
    while True:
        try:
            print("Connect to GoPro")
            gpCam = GoProCamera.GoPro(constants.auth)

            print("Downloading all the files...")
            media = gpCam.downloadAll(option="videos")

            print("Deleting all files")
            gpCam.delete(len(media))

            print("Copying files to Yandex.Disk")
            files = os.listdir()
            cwd = os.getcwd()
            videos = list(filter(lambda x: x.endswith('MP4'), files))
            local_videos = list(map(lambda x: os.path.join(cwd, x), videos))
            yandex_videos = list(
                map(lambda x: os.path.join(YANDEX_DISK_FOLDER, x), videos))

            paths = zip(local_videos, yandex_videos)

            for from_path, to_path in paths:
                print("Copying {} to {}".format(from_path, to_path))
                os.rename(from_path, to_path)

        except:
            print("Can't connect to GoPro")
            sleep(5)
            continue


if __name__ == "__main__":
    main()
