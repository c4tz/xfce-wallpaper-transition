# xfce-wallpaper-transition
Use random images from a directory as your wallpaper(s) with a transition in XFCE.

This was made because I couldn't get other programs like [variety](http://peterlevi.com/variety/) to work under Arch Linux + XFCE or they didn't fit my needs.

## Requirements

The following python-packages are required:

* [pillow](https://python-pillow.org/) (or PIL)
* [python-xlib](https://github.com/python-xlib/python-xlib)

You can install them by using this command:

```console
# pip install -U pillow python-xlib
```

## Installation

This is just a simple script, put it anywhere and run it.

## Usage

There are several ways you can use this script.

If you want to use the default options, you'll only need to `cd` to your image-directory and run the script from there, like so:

```console
$ cd ~/pictures
$ python ~/scripts/wallpaper.py
```

If you'd like to give it some arguments instead, you can also do that:

```console
-d ImageDir, --dir ImageDir
                    The directory of the backgrounds you want to loop
                    through
-t SECONDS, --timeout SECONDS
                    How many seconds to wait before the next transition
-s DURATION FPS DURATION FPS, --transition DURATION FPS DURATION FPS
                    Defines how long a transition is and with how much FPS
                    it shall be done
-b BackupPicture, --backup BackupPicture
                    If the program crashes, shall there be a backup
                    picture to revert to?
```

So, a full-blown call would look like this:

```console
$ python wallpaper.py -d ~/pictures -t 300 -s 2 50 -b ~/background.jpg
```

**Warnings:**

* The script will currently crash, if it chooses a non-image-file.
* It will pre-render the image-transition as JPGs to `/tmp/` and then display it. If you're on a slow machine (or just don't have a SSD), I wouldn't recommend a high FPS count.
* In my experience, xfdesktop couldn't handle (DURATION / FPS) <= 0.025. I tested with a GTX 1080.

## Current TODO

* Make it use only picture files, not random ones
* Check if file paths really exist
* General exception handling

## Future Prospects

This script may or may not work with other desktop environments after one changes the command called by it. If someone volunteers or I find myself with a big amount of freetime, the functionality might find its way into the repository. ;)

Hint: I'm talking about [something like this](http://stackoverflow.com/a/21213504) here.