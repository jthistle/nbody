#!/usr/bin/env python3

from pygame.math import Vector2
import const as CONST


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


def readableDistance(d):
    """Returns a human-readable distance given a distance in meters"""
    if d >= CONST.LY:
        return "{:.2f}ly".format(d/CONST.LY)
    elif d >= CONST.AU:
        return "{:.2f}au".format(d/CONST.AU)
    elif d >= 10 ** 3:
        return "{:.2e}km".format(d/(10 ** 3))
    elif d >= 1:
        return "{:.2f}m".format(d)
    else:
        return "{:.2e}m".format(d)
