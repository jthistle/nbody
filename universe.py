#!/usr/bin/env python3

from pygame.math import Vector2


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
