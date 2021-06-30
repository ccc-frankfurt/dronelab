# Simulation Workpackage

&#8594; current Strategy/ToDos:

## Validation

** &#8594; Extract proportion of "rail" pixels in every image in the railsem data**  

- railsem19_data folder contains 3 out of 8500 uint8 images with class segmentations (*all uint8 images, RGB images and json files available on request*)
- idea:  
Import uint8 image with `cv2.imread(inp_path_uint8,cv2.IMREAD_GRAYSCALE)`;  
Pixel value equals class index in rs19-config.json?
- (see "example-vis.py" line 39-45 and line 79-83 for example usage of uint8 image)

**Goal: compare share of pixels of "rail" class in real images with proportion of rails in (simulated?!) drone images**

## Generate Limited World Model with Julia

** &#8594; Generate limited 3d world model with [Julia Gen](https://www.gen.dev/)**  
[(Gen example)](https://www.youtube.com/watch?v=B7mc1wXPZR8)  

Variables in genererative model: 

1. Rail Pairs  
Two (straight) parallel lines with fixed z (height) coordinate  
Distance between two lines is constant

2. Object Position  
Objects position could be marked by single pixel position (x,y), z coordinate fixed  
For now only look at position of object on the ground

3. Camera Position  
pitch, roll, yaw?  

4. Camera Noise 

------------------------------
Thoughts:  
- limit coordinate range to drone image size?

## Monte Carlo





