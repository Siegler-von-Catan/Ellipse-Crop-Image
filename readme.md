# Ellipse Crop Image for Blender Pipeline Step
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


## Usage
```
usage: blenderPreparation.py [-h] -i INPUT [-tl TOPLEFT] [-dr DOWNRIGHT] -o OUTPUT

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        the file path to the image to process
  -tl TOPLEFT, --topleft TOPLEFT
                        coordinate of a pixel in the image interpreted as the top left corner (x@y)
  -dr DOWNRIGHT, --downright DOWNRIGHT
                        coordinate of a pixel in the image interpreted as the down right corner (x@y)
  -o OUTPUT, --output OUTPUT
                        the file path to save the result to
```
                        
## Example
python3 blenderPreparation.py -i some_cute_cat.jpg -o cat_result.jpg
![alt text](https://github.com/Siegler-von-Catan/optimizeImageForBlender/blob/main/some_cute_cat.jpg)
![alt text](https://github.com/Siegler-von-Catan/optimizeImageForBlender/blob/main/cat_result.jpg)
