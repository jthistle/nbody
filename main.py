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

    def draw(self, surface, camera, universe):
        tempPos = camera.drawPos(universe.worldToScreen(self.pos))
        pygame.draw.circle(surface, self.colour, tempPos, self.radius * camera.scale, 0)


def drawText(surface, text, font, position, colour, leftAlign = True):
    rendered = font.render(text, 1, colour)

    if not leftAlign:
        position -= Vector2(rendered.get_width(), 0)

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


class Camera:
    def __init__(self, centre):
        self.centre = centre
        self.pos = Vector2()
        self.scale = 1

        # WASD camera movement map
        speed = 300
        self.TRANSLATION_MAP = {
            pygame.K_a: Vector2(-speed, 0),
            pygame.K_d: Vector2(speed, 0),
            pygame.K_s: Vector2(0, speed),
            pygame.K_w: Vector2(0, -speed)
        }

    def move(self, vector):
        self.pos += vector

    def resize(self, sf):
        self.scale *= sf  #TODO

    def drawPos(self, screenPos):
        """Given a point on the screen, transform it to its new position based on the
        current state of the camera"""
        pos = Vector2(screenPos)

        pos -= self.pos
        pos[0] = self.centre[0] + self.scale * (pos[0] - self.centre[0])
        pos[1] = self.centre[1] + self.scale * (pos[1] - self.centre[1])

        return pos

    def reverseDrawPos(self, drawPos):
        """The inverse of drawPos"""
        pos = Vector2(drawPos)

        pos[0] = ((pos[0] - self.centre[0]) / self.scale) + self.centre[0]
        pos[1] = ((pos[1] - self.centre[1]) / self.scale) + self.centre[1]
        pos += self.pos

        return pos

    def handleInput(self, deltaT):
        held = pygame.key.get_pressed()
        translation = Vector2()
        for key in self.TRANSLATION_MAP:
            if held[key]:
                translation += self.TRANSLATION_MAP[key]

        self.pos += translation * deltaT / self.scale


class Universe:
    def __init__(self, scale, timeScale):
        self.scale = scale
        self.timeScale = timeScale
        self.totalTime = 0

    def accelTime(self, factor):
        self.timeScale *= factor

    def deltaT(self, realDeltaT):
        return realDeltaT * self.timeScale

    def update(self, realDeltaT):
        self.totalTime += self.deltaT(realDeltaT)

    def screenToWorld(self, screenPos):
        return Vector2(screenPos) * self.scale

    def worldToScreen(self, worldPos):
        return Vector2(worldPos) / self.scale


def main():
    pygame.init()
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    SCREEN_CENTRE = Vector2(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)

    # Scale in pixels per metre
    # 100 pix = 1 AU
    UNIVERSE = Universe(int(150e7), 2 ** 23)

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
                    moveData["tempBody"] = Body(Vector2(), moveData["tempRelMass"] * EARTH_MASS)

                elif e.button == 4:
                    if moveData["mouseHeld"]:
                        moveData["tempRelMass"] *= 2 ** (1/3)
                        moveData["tempBody"].setMass(moveData["tempRelMass"] * EARTH_MASS)
                    else:
                        CAMERA.resize(2)

                elif e.button == 5:
                    if moveData["mouseHeld"]:
                        moveData["tempRelMass"] /= 2 ** (1/3)
                        moveData["tempBody"].setMass(moveData["tempRelMass"] * EARTH_MASS)
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
                            distance = UNIVERSE.screenToWorld((endPos - beginPos) / CAMERA.scale)
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

        # pygame.draw.line(DISPLAY, WHITE, (10, 10), (110, 10), 2)

        # Draw UI
        drawText(DISPLAY, "Time scale: {}x".format(UNIVERSE.timeScale), font, (10, 10), WHITE)
        drawText(DISPLAY, "Time elapsed: {}".format(secondsToTimeString(UNIVERSE.totalTime)), font, (10, 30), WHITE)
        drawText(DISPLAY, "Camera scale: {}x".format(CAMERA.scale), font, (SCREEN_WIDTH - 10, 10), WHITE, False)

        pygame.display.update()
        CLOCK.tick(FPS)


if __name__ == "__main__":
    main()
