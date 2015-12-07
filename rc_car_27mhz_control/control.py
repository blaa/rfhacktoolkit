import pygame
from time import time

AXIS_X = 0
AXIS_Y = 1

class Control(object):
    """
    Control loop for steering a car
    """

    def command(self, cmd):
        print "CMD", cmd
        with open('COMMAND', 'w') as f:
            f.write(cmd)

    def __init__(self, joystick):
        "Set up state"
        self.joystick = joystick


    def _do_move_robot(self):
        "Update servos angles"
        x = self.joystick.get_axis(AXIS_X)
        y = self.joystick.get_axis(AXIS_Y)
        th = 0.6

        if y < -th:
            forward = 1
        elif y > th:
            forward = -1
        else:
            forward = 0

        if x < -th:
            side = -1
        elif x > th:
            side = 1
        else:
            side = 0
        

        cmd_map = {
            # forward/backward, left/right
            ( 1, -1): 'q',
            ( 1,  0): 'w',
            ( 1,  1): 'e',

            ( 0, -1): 'a',
            ( 0,  0): 's',
            ( 0,  1): 'd',

            (-1, -1): 'z',
            (-1,  0): 'x',
            (-1,  1): 'c',
        }
        print x, y
        self.command(cmd_map[(forward, side)])
        
    def loop(self):
        "Joystick -> (Pump, Robot) control"

        print "- Entering control loop (HIDE!)"
        while True:

            try:
                # Don't block in auto mode
                s = time()
                event = pygame.event.poll()

            except KeyboardInterrupt:
                break

            if event.type == pygame.JOYAXISMOTION:
                self._do_move_robot()
            elif event.type == pygame.QUIT:
                break

        print "Finishing on user request"
