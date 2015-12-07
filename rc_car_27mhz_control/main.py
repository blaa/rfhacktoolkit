#!/usr/bin/env python

""" 
Made from watberrycannon code to wrap joystick. Creates a COMMAND file with
current command for car.  
"""

from time import sleep
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pigpio

import pygame

from control import Control
from IPython import embed

def init_pygame():
    "Pygame initialization + debug"
    print "- Initialize pygame"
    pygame.init()
    #print "Initialize display"
    #pygame.display.init()
    #pygame.display.set_mode((1,1))
    print "- Initialize joystick"
    pygame.joystick.init()

    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    axes = joystick.get_numaxes()
    hats = joystick.get_numhats()
    buts = joystick.get_numbuttons()
    print "  AXES: %d HATS: %d BUTS: %d" % (axes, hats, buts)

    return joystick


def main():
    try:
        joystick = init_pygame()
    except Exception:
        print "Pygame initialization failed - it MIGHT require (for unknown reasons) root"
        print "You can try with root, but that won't be safer"
        print
        raise


    control = Control(joystick)
    try:
        control.loop()
    except Exception:
        import traceback as tb
        print "GOT EXCEPTION"
        tb.print_exc()
        raise


if __name__ == "__main__":
    main()
