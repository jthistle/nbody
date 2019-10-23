#!/usr/bin/env python3

import pygame
import math
import os
import random
from pygame.math import Vector2

from colours import *
from utils import *
import const as CONST
from body import Body
from camera import Camera
from universe import Universe


def main():
    pygame.init()
    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 700
    SCREEN_CENTRE = Vector2(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)

    # Scale in pixels per metre
    # 100 pix = 1 AU
    UNIVERSE = Universe(CONST.AU / 100, 2 ** 23)

    CAMERA = Camera(SCREEN_CENTRE)

    DISPLAY = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    CLOCK = pygame.time.Clock()
    FPS = 120

    moveData = {
        "mouseHeld": False,
        "tempRelMass": 1,
        "tempBody": None,
        "lastPos": (0, 0),
        "currentPos": (0, 0),
        "lastTime": -1,
        "currentTime": 0
    }

    bodies = []

    font = pygame.font.SysFont("monospace", 15)

    while True:
        DISPLAY.fill(BLACK)
        realDeltaT = (CLOCK.get_time()/1000)
        UNIVERSE.update(realDeltaT)
        deltaT = UNIVERSE.deltaT(realDeltaT)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()

            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_PERIOD:
                    UNIVERSE.accelTime(2)
                elif e.key == pygame.K_COMMA:
                    UNIVERSE.accelTime(1/2)

            elif e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    moveData["mouseHeld"] = True
                    moveData["tempRelMass"] = 1
                    moveData["currentPos"] = e.pos
                    moveData["lastPos"] = e.pos
                    moveData["lastTime"] = -1
                    moveData["currentTime"] = UNIVERSE.totalTime

                    # The body's position will be set later before drawing
                    moveData["tempBody"] = Body(Vector2(), moveData["tempRelMass"] * CONST.ME)

                elif e.button == 4:
                    if moveData["mouseHeld"]:
                        if pygame.KMOD_SHIFT & pygame.key.get_mods():
                            moveData["tempRelMass"] *= 2 ** (2/3)
                        else:
                            moveData["tempRelMass"] *= 2 ** (1/3)
                        moveData["tempBody"].setMass(moveData["tempRelMass"] * CONST.ME)
                    else:
                        CAMERA.resize(2)

                elif e.button == 5:
                    if moveData["mouseHeld"]:
                        if pygame.KMOD_SHIFT & pygame.key.get_mods():
                            moveData["tempRelMass"] /= 2 ** (2/3)
                        else:
                            moveData["tempRelMass"] /= 2 ** (1/3)
                        moveData["tempBody"].setMass(moveData["tempRelMass"] * CONST.ME)
                    else:
                        CAMERA.resize(1/2)

            elif e.type == pygame.MOUSEBUTTONUP:
                if e.button == 1:
                    moveData["mouseHeld"] = False
                    tempBody = moveData["tempBody"]

                    beginPos = Vector2(moveData["lastPos"])
                    endPos = Vector2(moveData["currentPos"])

                    # Calculate last velocity of mouse
                    if not (pygame.KMOD_CTRL & pygame.key.get_mods()):
                        if moveData["currentTime"] - moveData["lastTime"] == 0:
                            print("Oops... zero-division avoided!")
                        else:
                            dampener = 2
                            distance = UNIVERSE.screenToWorld((endPos - beginPos)) / (CAMERA.scale * dampener)
                            velocity = distance / (moveData["currentTime"] - moveData["lastTime"])
                            tempBody.velocity = velocity

                    bodies.append(tempBody)
                    moveData["tempBody"] = None

                    print("Created body with mass {:.4e}kg".format(tempBody.mass))

            elif e.type == pygame.MOUSEMOTION:
                if moveData["mouseHeld"]:
                    moveData["lastPos"] = moveData["currentPos"]
                    moveData["lastTime"] = moveData["currentTime"]
                    moveData["currentPos"] = e.pos
                    moveData["currentTime"] = UNIVERSE.totalTime

        CAMERA.handleInput(realDeltaT)

        # Update pos always, and now so that we can take into account any camera moves
        if moveData["mouseHeld"]:
            bodyPos = UNIVERSE.screenToWorld(CAMERA.reverseDrawPos(moveData["currentPos"]))
            moveData["tempBody"].setPos(bodyPos)

        if moveData["tempBody"]:
            moveData["tempBody"].draw(DISPLAY, CAMERA, UNIVERSE)

        for body in bodies:
            body.update(deltaT, bodies)

        for body in bodies:
            body.draw(DISPLAY, CAMERA, UNIVERSE)

        lineY = SCREEN_HEIGHT - 10
        pygame.draw.line(DISPLAY, WHITE, (10, lineY), (110, lineY), 2)

        drawText(DISPLAY, readableDistance(UNIVERSE.scale * 100 / CAMERA.scale), font, (120, lineY - 10), WHITE)

        # Draw UI
        drawText(DISPLAY, "Time scale: {}x".format(UNIVERSE.timeScale), font, (10, 10), WHITE)
        drawText(DISPLAY, "Time elapsed: {}".format(secondsToTimeString(UNIVERSE.totalTime)), font, (10, 30), WHITE)
        # drawText(DISPLAY, "Camera scale: {:.2e}x".format(CAMERA.scale), font, (SCREEN_WIDTH - 10, 10), WHITE, False)

        pygame.display.update()
        CLOCK.tick(FPS)


if __name__ == "__main__":
    main()
