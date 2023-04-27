# -*- coding: utf-8 -*-
# @Time    : 2023/4/26 16:56
# @Author  : XXX
# @Site    : 
# @File    : sound.py
# @Software: PyCharm 
# @Comment :

import platform
import os
import threading
from enum import IntEnum


class SoundType(IntEnum):
    PORT_NEW = 0,
    PORT_ACCIDENT_DISCONNECT = 1,
    PORT_OPEN = 2


sound_path_Darwin = [
    '/System/Library/Sounds/Bottle.aiff',
    '/System/Library/Sounds/Sosumi.aiff',
    '/System/Library/Sounds/Ping.aiff'
]

sound_path_Linux = [
    '/usr/share/sounds/freedesktop/stereo/complete.oga',
]


def play_sound(sound_type: SoundType):
    t = threading.Thread(target=_play_sound, args=[sound_type])
    t.start()


def _play_sound(sound_type: SoundType):

    system = platform.system()
    try:
        if system == 'Windows':
            import winsound
            sound_path_win = [
                ('SystemAsterisk', winsound.SND_ALIAS)
            ]
            winsound.PlaySound(*sound_path_win[sound_type.value])
        elif system == 'Darwin':
            os.system(f'afplay {sound_path_Darwin[sound_type.value]}')
        elif system == 'Linux':
            os.system(f'aplay {sound_path_Linux[sound_type.value]}')
        else:
            print('Sound Unsupported platform')
    except:
        return