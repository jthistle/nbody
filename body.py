#!/usr/bin/env python3

import math
import pygame
from pygame.math import Vector2
import const as CONST


class Body():
    def __init__(self, pos, mass):
        self.setPos(pos)
        self.setMass(mass)
        self.velocity = Vector2()

    def setPos(self, pos):
        self.pos = pos

    def setMass(self, mass):
        self.mass = mass
        self.getRadius()
        self.setColour()

    def getRadius(self):
        adjustment = 3
        k = 5.565194508027365e-05 * adjustment
        radius = k * (self.mass ** (1/3))
        self.radius = radius

    def setColour(self):
        minL = 30
        maxL = 105 - minL
        maxH = 90
        logVal = math.log(self.mass) - minL

        h = max(0, min((maxH, maxH - (logVal / maxL) * maxH)))
        self.colour = pygame.Color(0, 0, 0)
        self.colour.hsla = (h, 100, 50, 1)

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
            mag = ((CONST.G * body.mass) / (distance ** 2))
            direction = distanceVector.normalize()

            accelVector = mag * direction
            accel += accelVector

        self.velocity += accel * dt

    def update(self, dt, bodies):
        self.applyForces(dt, bodies)
        self.pos = self.pos + (self.velocity * dt)

    def draw(self, surface, camera, universe):
        tempPos = camera.drawPos(universe.worldToScreen(self.pos))
        radius = camera.scale * (self.radius / universe.scale)
        width = 0

        if radius < 2:
            radius = 2
            width = 1

        pygame.draw.circle(surface, self.colour, tempPos, radius, width)
