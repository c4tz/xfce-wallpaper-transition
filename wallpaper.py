#!/usr/bin/python

import argparse, atexit, os, random, signal, subprocess, sys, time
from multiprocessing.dummy import Pool as ThreadPool
import PIL
from PIL import Image
from Xlib.display import Display

class WallpaperTransition:
    def __init__(self, imageFolder, timeout, duration, fps, backupPic):

        self.monitors = self.getMonitorList()
        self.imageFolder = imageFolder
        self.timeout = timeout
        self.duration = duration
        self.fps = fps

        if backupPic:
            self.backupPic = backupPic
            atexit.register(self.backup,)
            signal.signal(signal.SIGTERM, self.signal_handler)

    def getMonitorList(self):
        display = Display()
        root = display.screen().root
        gc = root.create_gc()
        resources = root.xrandr_get_screen_resources()._data

        monitors = {}
        count = 0

        for crtc in resources['crtcs']:
            monitor = display.xrandr_get_crtc_info(crtc, resources['config_timestamp'])._data
            if len(monitor['outputs']) > 0: # is connected
                monitors[count] = (monitor['width'], monitor['height'])
                count += 1

        return monitors

    def getWallpaper(self, monitorNumber):
        return subprocess.check_output('xfconf-query --channel xfce4-desktop '
                                       '--property /backdrop/screen0/monitor'
                                       +str(monitorNumber)+'/workspace0/last-image',
                                       shell=True).decode('utf-8').replace('\n', '')

    def setWallpaper(self, monitorNumber, imagePath):
        subprocess.call('xfconf-query --channel xfce4-desktop --property '
                        '/backdrop/screen0/monitor'+str(monitorNumber)+
                        '/workspace0/last-image --set '+imagePath,
                        shell=True)

    def processImage(self, img, size):
        img.thumbnail(size, PIL.Image.ANTIALIAS)
        img.convert('RGBA')

        offset_x = int(max((size[0] - img.size[0]) / 2, 0))
        offset_y = int(max((size[1] - img.size[1]) / 2, 0))
        offset_tuple = (offset_x, offset_y)

        result = Image.new(mode='RGBA',size=size,color=(0,0,0,0))
        result.paste(img, offset_tuple)
        return result

    def bgTransition(self, monitorID, imageFolder):
        current = self.getWallpaper(monitorID)
        new = imageFolder+'/'+random.choice(os.listdir(imageFolder))

        bg = self.processImage(Image.open(current), self.monitors[monitorID])
        fg = self.processImage(Image.open(new), self.monitors[monitorID])

        count = (self.duration * self.fps) + 1
        sleep = self.duration / self.fps

        for i in range (1, count):
            Image.blend(bg, fg, i/count).save('/tmp/'+str(monitorID)+'_'+str(i)+'.jpg')
        for i in range (1, count):
            time.sleep(sleep)
            self.setWallpaper(monitorID, '/tmp/'+str(monitorID)+'_'+str(i)+'.jpg')
        self.setWallpaper(monitorID, new)
        subprocess.call('rm /tmp/'+str(monitorID)+'_*.jpg', shell=True) # can't use wildcards in pythons os.remove()


    def signal_handler(self, signal, frame):
        self.backup()

    def backup(self):
        for id in self.monitors:
            self.setWallpaper(id, self.backupPic)


    def loop(self):
        while 1:
            array = []
            for id in self.monitors:
                array.append((id, self.imageFolder))

            pool = ThreadPool(len(self.monitors))
            pool.starmap(self.bgTransition, array)
            time.sleep(self.timeout)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='XFCE Wallpaper Transition')
    parser.add_argument(
        '-d',
        '--dir',
        nargs='?',
        default=os.getcwd(),
        metavar=('ImageDir'),
        help='The directory of the backgrounds you want to loop through',
        type=str
    )
    parser.add_argument(
        '-t',
        '--timeout',
        nargs='?',
        default=300,
        metavar=('SECONDS'),
        help='How many seconds to wait before the next transition',
        type=int
    )
    parser.add_argument(
        '-s',
        '--transition',
        nargs=2,
        default=[2, 50],
        metavar=('DURATION FPS'),
        help='Defines how long a transition is and with how much FPS it shall be done',
        type=int
    )
    parser.add_argument(
        '-b',
        '--backup',
        metavar=('BackupPicture'),
        help='If the program crashes, shall there be a backup picture to revert to?',
        type=str
    )

    args = vars(parser.parse_args())

    if 'dir' in args:
        dir = args['dir']
    if 'timeout' in args:
        timeout = args['timeout']
    if 'transition' in args:
        duration = args['transition'][0]
        fps = args['transition'][1]
    if 'backup' in args:
            backupPic = args['backup']

    if dir and timeout and duration and fps:
        wt = WallpaperTransition(dir, timeout, duration, fps, backupPic)
        wt.loop()
    else:
        parser.print_help()