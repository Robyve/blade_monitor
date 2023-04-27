# -*- coding: utf-8 -*-
# @Time    : 2023/4/26 16:56
# @Author  : XXX
# @Site    : 
# @File    : sound.py
# @Software: PyCharm 
# @Comment :

import platform
import os


def play_sound():
    system = platform.system()
    if system == 'Windows':
        import winsound
        winsound.PlaySound('SystemAsterisk', winsound.SND_ALIAS)
    elif system == 'Darwin':
        os.system('afplay /System/Library/Sounds/Bottle.aiff')
    elif system == 'Linux':
        os.system('aplay /usr/share/sounds/freedesktop/stereo/complete.oga')
    else:
        print('Unsupported platform')