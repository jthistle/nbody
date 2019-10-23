#!/usr/bin/env python3

import pygame
from pygame.math import Vector2


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
