# **Pixel Reproduction**

### This program simulates a reproduction of pixel population.
A pixel is an entity which carries one of the possible color schemes: RGB, HSL, HSV, CYMK.
A population of pixels is a collection of pixels.
Pixels can reproduce in couples. 
Pixels of different type will only reproduce with the desired type as explained in the assignment description,
and only if their distance function big enough 
(bigger then a default threshold and biggest among other possible mates). The distance function can be easily changed.
I have added a feature of pixel's dominance. Like human's genes, a pixel's type can be either dominant or recessive.
When 2 pixels decide to reproduce, their offspring's type will be decided according to their parents dominance. If they
are both dominant or recessive, the type will be decided randomly. Then, its values will be the average of its parents
type as RGB representation.
This information needs to be included in the arguments of the program.


#### Getting Started
In order to run the program run the following command (replace each argument with the proper integer) inside the project folder:

> python3 ./pixel_reproduction.py population_file, dominance_schemes, initial_pixels_amount, reproduction_interval, number_of_iterations

All arguments are mandatory. 
Their values are explained below or via --help command.

#### Prerequisites
argparse, colorsys, enum, abc, time, random, multiprocessing 

#### Installing
Run the following command:

> pip install colorsys enum abc time random multiprocessing 

#### ARGUMENTS
population_file: A name of a file, which includes a population description: Each line
                                                of the file includes a comma separated information- 
                                                Type of Pixel,value1,value2,value3,value4.
                                                Forth value is in the case of CMYK pixel.

dominance_schemes :Which type of pixel is dominance in its reproducing process."
                                                  "Must be a list of pixel types (RGB, HSL, HSV, CYMK), comma"
                                                  "separated. if you wish to specify an empty list if pixels, "
                                                  "please put the word 'none' 

reproduction_interval: How much time (seconds) between one reproduction to another

number_of_iterations: How many reproductions you would like to simulate


#### About the code
The reproduction is achieved by using multiprocessing. Each process takes a couple of pixels to reproduce in order to
get an efficient and fast program.
There is an abstract class- Pixel. Every other type of pixel extends it.
I've used a library - 'colorsys' to move from one representation of pixel type to another.

#### Authors
Shimon Berkovich
