#!/usr/bin/env python

#     SealExtraction - Extracting the motive out of stamps with Image Processing.
#     Copyright (C) 2021
#     Joana Bergsiek, Leonard Geier, Lisa Ihde, Tobias Markus, Dominik Meier, Paul Methfessel
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

'''
Given an
- input Image INPUT,
- (optional) a 2 dimensional coordinate (x@y) TOPLEFT in image range, defaults to 2@2
- (optional) a 2 dimensional coordinate (x@y) DOWNRIGHT in image range, DOWNRIGHT > TOPLEFT,
    defaults to INPUT WIDTH-2@INPUT HEIGHT-2
- and an output path OUTPUT,
this program will convert INPUT to gray scale and create an ellipse mask within the rectangle defined
by TOPLEFT and DOWNRIGHT.
This mask is then used to fill everything outside the ellipse white. The result is saved as the user specified image
format in OUTPUT.

Doing this will guarantee a displacement map which border's are aligned at the "highest position" (white = 0 = top),
ideal for boolean merging with a 3D model in Blender as the needed 3D position of the displacement map stays consistent
(like done in our other project https://github.com/Siegler-von-Catan/displacementMapToStl).
'''

import argparse

import cv2 as cv
import numpy as np

borderPixels = 2

def coords(s):
    try:
        x, y = map(int, s.split('@'))
        return [x, y]
    except:
        raise argparse.ArgumentTypeError("Coordinates must be x@y")

def initializArgumentParser():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i",
                    "--input",
                    metavar="INPUT",
                    help="the file path to the image to process",
                    type=str,
                    required=True)

    ap.add_argument("-tl",
                    "--topleft",
                    metavar="TOPLEFT",
                    help="coordinate of a pixel in the image interpreted as the top left corner (x@y)",
                    type=coords,
                    required=False)

    ap.add_argument("-dr",
                    "--downright",
                    metavar="DOWNRIGHT",
                    help="coordinate of a pixel in the image interpreted as the down right corner (x@y)",
                    type=coords,
                    required=False)

    ap.add_argument("-o",
                    "--output",
                    metavar="OUTPUT",
                    help="the file path to save the result to",
                    type=str,
                    required=True)
    return ap

def process(image, topleft, downright):
    # fit ellipse through topleft-downright defined rectangle
    mask, boundingRect = get_mask_on(image, topleft, downright)
    # get first masked value (foreground)
    fg = cv.bitwise_or(image, image, mask=mask)
    # get second masked value (background) mask must be inverted
    mask = cv.bitwise_not(mask)
    background = np.full(image.shape, 255, dtype=np.uint8)
    bk = cv.bitwise_or(background, background, mask=mask)
    # combine foreground+background
    final = cv.bitwise_or(fg, bk)
    # crop image to bounding rect
    final = crop_image_to_contour_AABB(final, boundingRect)

    return final

def get_mask_on(image, topleft, downright):
    mask = np.zeros(image.shape[:2], np.uint8)
    center = (round((topleft[0] + downright[0]) / 2), round((topleft[1] + downright[1]) / 2))
    points = np.float32([
        center,
        (center[0], topleft[1]),
        (downright[0], center[1]),
        (center[0], downright[1]),
        (topleft[0], center[1]),
    ])
    ellipse = cv.fitEllipse(points)
    cv.ellipse(mask, ellipse, 255, -1)

    return mask, cv.boundingRect(points)

def crop_image_to_contour_AABB(image, boundingRect):
    x = max(0, boundingRect[0] - borderPixels)
    y = max(0, boundingRect[1] - borderPixels)
    w = min(image.shape[1], boundingRect[2] + 2 * borderPixels)
    h = min(image.shape[0], boundingRect[3] + 2 * borderPixels)

    return image[y:y+h, x:x+w]

def main():
    ap = initializArgumentParser()
    args = vars(ap.parse_args())

    image = cv.imread(args["input"], cv.IMREAD_GRAYSCALE)
    image_height, image_width = image.shape

    maxWidth = image_width-1-borderPixels
    maxHeight = image_height-1-borderPixels

    topleft = args["topleft"] if args["topleft"] else [borderPixels, borderPixels]
    downright = args["downright"] if args["downright"] else [maxWidth, maxHeight]

    # ensure valid range
    topleft[0] = max(borderPixels, min(topleft[0], maxWidth))
    topleft[1] = max(borderPixels, min(topleft[1], maxHeight))
    downright[0] = max(borderPixels, min(downright[0], maxWidth))
    downright[1] = max(borderPixels, min(downright[1], maxHeight))

    result = process(image, topleft, downright)
    cv.imwrite(args["output"], result)

if __name__ == '__main__':
    main()

