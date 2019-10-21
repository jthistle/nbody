#!/usr/bin/env python3

import pygame
import math
import os
import random
from pygame.math import Vector2
from colours import *


GRAV_CONST = 6.67430e-11
EARTH_MASS = int(5.97e24)


class Body():
    def __init__(self, pos, mass):
        self.setPos(pos)
        self.setMass(mass)
        self.velocity = Vector2()

        COLOURS = [
            WHITE,
            RED,
            GREEN,
            BLUE,
            PURPLE
        ]
        self.colour = random.choice(COLOURS)

    def setPos(self, pos):
        self.pos = pos

    def setMass(self, mass):
        self.mass = mass
        relSize = self.mass / EARTH_MASS
        self.radius = int(relSize ** (1/3) * 2)

    def applyForces(self, dt, bodies):
        """Apply gravitational forces using Newton's law.

        F = (GMm)/(r^2)
        """
        accel = Vector2()
        for body in bodies:
            if body == self:
                continue
            distanceVector = body.pos - self.pos
            distance = distanceVector.magnitude()
            mag = ((GRAV_CONST * body.mass) / (distance ** 2))
            direction = distanceVector.normalize()

            accelVector = mag * direction
            accel += accelVector

        self.velocity += accel * dt

    def update(self, dt, bodies):
        self.applyForces(dt, bodies)
        self.pos = self.pos + (self.velocity * dt)

    def draw(self, surface, scale, translate):
        tempPos = self.pos // scale + translate
        pygame.draw.circle(surface, self.colour, tempPos, self.radius, 0)


def drawText(surface, text, font, position, colour):
    rendered = font.render(text, 1, colour)
    surface.blit(rendered, position)


def secondsToTimeString(secs):
    secs = int(secs)
    minutes = secs // 60
    secs %= 60

    hours = minutes // 60
    minutes %= 60

    days = hours // 24
    hours %= 24

    years = days // 365
    days %= 365

    return "{} yrs, {} days, {:02d}:{:02d}:{:02d}".format(years, days, hours, minutes, secs)


def main():
    pygame.init()
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600

    # Scale in pixels per metre
    SCALE = int(150e7)   # 100 pix = 1 AU
    WIDTH = SCREEN_WIDTH/SCALE
    HEIGHT = SCREEN_HEIGHT/SCALE

    SCREEN_CENTRE = Vector2(WIDTH/2, HEIGHT/2)
    CENTRE = SCREEN_CENTRE/SCALE

    CAMERA_POS = Vector2()

    speed = 300
    TRANSLATION_MAP = {
        pygame.K_a: Vector2(-speed, 0),
        pygame.K_d: Vector2(speed, 0),
        pygame.K_s: Vector2(0, speed),
        pygame.K_w: Vector2(0, -speed)
    }

    DISPLAY = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    CLOCK = pygame.time.Clock()
    FPS = 120
    totalTime = 0
    TIME_SCALE = 2 ** 23

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
        deltaT = realDeltaT * TIME_SCALE
        totalTime += deltaT

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()

            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_PERIOD:
                    TIME_SCALE *= 2
                elif e.key == pygame.K_COMMA:
                    TIME_SCALE /= 2

            elif e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    moveData["mouseHeld"] = True
                    moveData["tempRelMass"] = 1
                    moveData["tempBody"] = Body((Vector2(e.pos) + CAMERA_POS) * SCALE, moveData["tempRelMass"] * EARTH_MASS)
                    moveData["currentPos"] = e.pos
                    moveData["lastPos"] = e.pos
                    moveData["lastTime"] = -1
                    moveData["currentTime"] = totalTime

                elif e.button == 4:
                    if moveData["mouseHeld"]:
                        moveData["tempRelMass"] *= math.e
                        moveData["tempBody"].setMass(moveData["tempRelMass"] * EARTH_MASS)

                elif e.button == 5:
                    if moveData["mouseHeld"]:
                        moveData["tempRelMass"] /= math.e
                        moveData["tempBody"].setMass(moveData["tempRelMass"] * EARTH_MASS)

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
                            distance = (endPos - beginPos) * SCALE
                            velocity = distance / (moveData["currentTime"] - moveData["lastTime"])
                            tempBody.velocity = velocity

                    bodies.append(tempBody)
                    moveData["tempBody"] = None

            elif e.type == pygame.MOUSEMOTION:
                if moveData["mouseHeld"]:
                    moveData["lastPos"] = moveData["currentPos"]
                    moveData["lastTime"] = moveData["currentTime"]
                    moveData["currentPos"] = e.pos
                    moveData["currentTime"] = totalTime

        # Alternate event handling: check for keydown
        held = pygame.key.get_pressed()
        translation = Vector2()
        for key in TRANSLATION_MAP:
            if held[key]:
                translation += TRANSLATION_MAP[key]

        CAMERA_POS += translation * realDeltaT

        # Update pos always, and now so that we can take into account any camera moves
        if moveData["mouseHeld"]:
            moveData["tempBody"].setPos((Vector2(moveData["currentPos"]) + CAMERA_POS) * SCALE)

        if moveData["tempBody"]:
            moveData["tempBody"].draw(DISPLAY, SCALE, -CAMERA_POS)

        for body in bodies:
            body.update(deltaT, bodies)

        for body in bodies:
            body.draw(DISPLAY, SCALE, -CAMERA_POS)

        # pygame.draw.line(DISPLAY, WHITE, (10, 10), (110, 10), 2)

        # Draw UI
        drawText(DISPLAY, "Time scale: {}x".format(TIME_SCALE), font, (10, 10), WHITE)

        drawText(DISPLAY, "Time elapsed: {}".format(secondsToTimeString(totalTime)), font, (10, 30), WHITE)

        pygame.display.update()
        CLOCK.tick(FPS)


if __name__ == "__main__":
    main()
