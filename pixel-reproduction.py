import argparse
import time
import math
import random
from multiprocessing import Pool
from abc import ABC, abstractmethod
import colorsys
from enum import Enum

MIN_PIXEL_RANGE = 0
MAX_PIXEL_RANGE = 255
LIFESPAN = 8
DEFAULT_THRESHOLD = 0
MIN_GENERATION_FOR_REPRODUCTION = 3
MAX_GENERATION_FOR_REPRODUCTION = 6
MIN_NUMBER_OF_PIXELS_FOR_REPRODUCTION = 2
EXIT_ERROR = 1
DEFAULT_EMPTY_LIST = 'none'


class ColorSchemes(Enum):
    RGB = 'RGB'
    HSL = 'HSL'
    HSV = 'HSV'
    CMYK = 'CMYK'

class Pixel(ABC):

    threshold_to_reproduce = DEFAULT_THRESHOLD
    global dominance_set

    def __init__(self):
        self.generation = 0
        self.rgb_representation = self.asRGB()
        self.mate = None

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def asRGB(self):
        pass

    @staticmethod
    def set_dominance(dominance):
        Pixel.dominance_set = dominance

    def get_generation(self):
        return self.generation

    def increment_generation_count(self):
        self.generation += 1

    def get_mate(self):
        return self.mate

    @staticmethod
    def squares_distance(first, second):
        asRGB_first = first.asRGB()
        asARGB_second = second.asRGB()
        return math.sqrt(math.pow(asRGB_first[0] - asARGB_second[0], 2) + math.pow(asRGB_first[1] - asARGB_second[1], 2)
                         + math.pow(asRGB_first[2] - asARGB_second[2], 2))

    @staticmethod
    def rgb_average(first, second):
        first_values = first.asRGB()
        second_values = second.asRGB()

        return (first_values[0] + second_values[0]) // 2, (first_values[1] + second_values[1]) // 2,\
               (first_values[2] + second_values[2]) // 2

    @staticmethod
    def reproduce_couple(couple):
        first_type = type(couple[0]).__name__
        second_type = type(couple[1]).__name__
        global child_type
        if first_type in Pixel.dominance_set:
            if second_type in Pixel.dominance_set:
                rnd_choice = random.randint(0, 1)
                child_type = first_type if rnd_choice == 0 else second_type
            else:
                child_type = first_type
        else:
            if second_type in Pixel.dominance_set:
                child_type = second_type
            else:
                rnd_choice = random.randint(0, 1)
                child_type = first_type if rnd_choice == 0 else second_type
        r, g, b = Pixel.rgb_average(couple[0], couple[1])

        if child_type == ColorSchemes.RGB.value:
            return RGB((r, g, b))
        elif child_type == ColorSchemes.HSL.value:
            r, g, b = r / MAX_PIXEL_RANGE, g / MAX_PIXEL_RANGE, b / MAX_PIXEL_RANGE
            return HSL(HSL.from_RGB(r, g, b))
        elif child_type == ColorSchemes.HSV.value:
            r, g, b = r / MAX_PIXEL_RANGE, g / MAX_PIXEL_RANGE, b / MAX_PIXEL_RANGE
            return HSV(HSV.from_RGB(r, g, b))
        elif child_type == ColorSchemes.CMYK.value:
            return CMYK(CMYK.from_RGB(r, g, b))


class RGB(Pixel):
    options = [ColorSchemes.RGB.value, ColorSchemes.HSV.value, ColorSchemes.CMYK.value]

    def __init__(self, scheme):
        self.first = scheme[0]
        self.second = scheme[1]
        self.third = scheme[2]
        super().__init__()

    def __repr__(self):
        return 'RGB(Red= {0}, Green= {1}, Blue= {2}, age={3})'.format(self.first, self.second, self.third,
                                                                      self.generation)

    def asRGB(self):
        return self.get_values()

    def get_options(self):
        return RGB.options

    def get_values(self):
        return self.first, self.second, self.third


class HSL(Pixel):
    options = [ColorSchemes.HSV.value, ColorSchemes.HSL.value]

    def __init__(self, scheme):
        self.first = scheme[0]
        self.second = scheme[1]
        self.third = scheme[2]
        super().__init__()

    def __repr__(self):
        return 'HSL(Hue= {0}°, Saturation= {1}, Lightness= {2}, age={3})'.format(self.first, self.second, self.third,
                                                                                 self.generation)

    def asRGB(self):
        h, s, l = self.get_values()
        return tuple(round(i * 255) for i in colorsys.hls_to_rgb(h, l, s))

    @staticmethod
    def from_RGB(r, g, b):
        r, g, b = r / 255, g / 255, b / 255
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        return round(h, 2), round(s, 2), round(l, 2)


    def get_options(self):
        return HSL.options

    def get_values(self):
        return self.first, self.second, self.third


class HSV(Pixel):
    options = [ColorSchemes.RGB.value, ColorSchemes.HSV.value, ColorSchemes.HSL.value, ColorSchemes.CMYK.value]

    def __init__(self, scheme):
        self.first = scheme[0]
        self.second = scheme[1]
        self.third = scheme[2]
        super().__init__()

    def __repr__(self):
        return 'HSV(Hue= {0}°, Saturation= {1}, Value= {2}, age={3})'.format(self.first, self.second, self.third,
                                                                             self.generation)

    def asRGB(self):
        h, s, v = self.get_values()
        return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))

    @staticmethod
    def from_RGB(r, g, b):
        r, g, b = r / MAX_PIXEL_RANGE, g / MAX_PIXEL_RANGE, b / MAX_PIXEL_RANGE
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        return round(h, 2), round(s, 2), round(v, 2)

    def get_options(self):
        return HSV.options

    def get_values(self):
        return self.first, self.second, self.third


class CMYK(Pixel):

    options = [ColorSchemes.RGB.value, ColorSchemes.HSV.value, ColorSchemes.CMYK.value]

    def __init__(self, scheme):
        self.first = scheme[0]
        self.second = scheme[1]
        self.third = scheme[2]
        self.forth = scheme[3]
        super().__init__()


    def __repr__(self):
        return 'CMYK(Cyan= {0}, Magenta= {1}, Yellow= {2}, Black= {3}, age={4})'.format(self.first, self.second,
                                                                                        self.third, self.forth,
                                                                                        self.generation)

    def get_values(self):
        return self.first, self.second, self.third, self.forth

    def asRGB(self):
        cyan, magenta, yellow, black = self.get_values()

        r = MAX_PIXEL_RANGE * (MAX_PIXEL_RANGE - cyan) // MAX_PIXEL_RANGE * (MAX_PIXEL_RANGE - black) // MAX_PIXEL_RANGE
        g = MAX_PIXEL_RANGE * (MAX_PIXEL_RANGE - magenta) // MAX_PIXEL_RANGE * (MAX_PIXEL_RANGE - black)\
            // MAX_PIXEL_RANGE
        b = MAX_PIXEL_RANGE * (MAX_PIXEL_RANGE - yellow) // MAX_PIXEL_RANGE * (MAX_PIXEL_RANGE - black)\
            // MAX_PIXEL_RANGE

        return r, g, b

    @staticmethod
    def from_RGB(r, g, b):
        r_tag = r // MAX_PIXEL_RANGE
        g_tag = g // MAX_PIXEL_RANGE
        b_tag = b // MAX_PIXEL_RANGE

        k = 1 - max(r_tag, g_tag, b_tag)
        if k == 1:
            c = (1 - r_tag - k)
            m = (1 - g_tag - k)
            y = (1 - b_tag - k)
        else:
            c = (1 - r_tag - k) // (1 - k)
            m = (1 - g_tag - k) // (1 - k)
            y = (1 - b_tag - k) // (1 - k)

        return c, m, y, k

    def get_options(self):
        return CMYK.options


class Population:
    available_id = 0

    def __init__(self, pixels):
        initial_amount = len(pixels)
        self.community = {}
        for i in range(initial_amount):
            pixel_type = pixels[i][0]
            pixels_value = pixels[i][1:]
            try:
                pixels_value = [float(pixels_value[j]) for j in range(len(pixels_value))]
            except ValueError:
                print("Pixel {0} contains bad value".format(pixel_type))
                exit(EXIT_ERROR)
            if pixel_type == ColorSchemes.RGB.value:
                self.community[i] = RGB(pixels_value)
            elif pixel_type == ColorSchemes.HSL.value:
                self.community[i] = HSL(pixels_value)
            elif pixel_type == ColorSchemes.HSV.value:
                self.community[i] = HSV(pixels_value)
            elif pixel_type == ColorSchemes.CMYK.value:
                self.community[i] = CMYK(pixels_value)
            Population.increment_id()

    def __repr__(self):
        return 'Current population holds {0} Pixels\nSee details below:\n{1}\n'.format(self.get_community_size(),
                                                                                       self.community.values())

    def get_community(self):
        return self.community

    def get_community_size(self):
        return len(self.community.keys())

    def increment_generation(self):
        for pixel in self.community.values():
            pixel.increment_generation_count()

    @staticmethod
    def increment_id():
        Population.available_id += 1

    def population_dilution(self):
        new_population = {}
        for index, pixel in self.community.items():
            if pixel.get_generation() <= LIFESPAN:
                new_population[index] = pixel
        self.community = new_population

    def population_expand(self, offsprings):
        for offspring in offsprings:
            self.community[Population.available_id] = offspring
            Population.increment_id()


class Reproduction:
    def __init__(self, population, interval, iterations):
        self.population = population
        self.stage = 0
        self.reproduction_interval = interval
        self.number_of_iterations = iterations
        print(self)

    def __repr__(self):
        return 'After stage {0}:\n{1}\n'.format(self.get_cur_stage(), self.population)

    def increment_stage(self):
        self.stage += 1

    def get_cur_stage(self):
        return self.stage

    def reproduce_executor(self):
        couples = []
        couples_ids = []
        cur_population = self.population.get_community()
        pixels_indexes_capable_of_reproducing = []
        for id, pixel in cur_population.items():
            pixel_gen = pixel.get_generation()
            if MIN_GENERATION_FOR_REPRODUCTION <= pixel_gen <= MAX_GENERATION_FOR_REPRODUCTION:
                pixels_indexes_capable_of_reproducing.append(id)

        for id in pixels_indexes_capable_of_reproducing:
            if id in couples_ids:
                continue
            possible_mate = cur_population[id].get_mate()
            if possible_mate and possible_mate in cur_population:
                couples.append((cur_population[id], cur_population[possible_mate]))
                couples_ids.extend([id, possible_mate])
            else:
                options_types = cur_population[id].get_options()
                best_option_pixel_id = None
                best_option_pixel_value = 0

                for pair_id in pixels_indexes_capable_of_reproducing:
                    if pair_id == id or pair_id in couples_ids or type(cur_population[pair_id]).__name__ not in\
                            options_types:
                        continue
                    square_distance = Pixel.squares_distance(cur_population[id], cur_population[pair_id])
                    if square_distance > Pixel.threshold_to_reproduce and square_distance > best_option_pixel_value:
                        best_option_pixel_id = pair_id
                if best_option_pixel_id:
                    couples_ids.extend([id, best_option_pixel_id])
                    couples.append((cur_population[id], cur_population[best_option_pixel_id]))
        p = Pool()
        offspring_pixels = p.map(Pixel.reproduce_couple, couples)
        self.population.population_expand(offspring_pixels)

    def reproduce(self):
        next_call = time.time()
        for i in range(self.number_of_iterations):
            self.increment_stage()
            self.reproduce_executor()
            self.population.increment_generation()
            self.population.population_dilution()
            population_size = self.population.get_community_size()
            print(self)
            if population_size < MIN_NUMBER_OF_PIXELS_FOR_REPRODUCTION:
                print('Population holds only {0} pixel(s), thus will no longer reproduce, '
                      'stopping the process'.format(population_size))
                break
            next_call += self.reproduction_interval
            time.sleep(next_call - time.time())


def read_from_file(filename):
    pixels = []
    try:
        with open(filename) as input_file:
            for line in input_file:
                line = line.rstrip()
                if not line:
                    break
                pixels.append(line.rstrip().split(','))
        return pixels
    except OSError as err:
        print("OS error: {0}".format(err))
        exit(EXIT_ERROR)


def verify_inputs(pixels, dominance_schemes):
    correct_pixels_type = set(item.value for item in ColorSchemes)
    if dominance_schemes[0] == DEFAULT_EMPTY_LIST:
        dominance_schemes.pop()
    else:
        for scheme in dominance_schemes:
            if scheme not in correct_pixels_type:
                print("Bad value: {0} on dominance schemes list".format(scheme))
                exit(EXIT_ERROR)
    Pixel.set_dominance(dominance_schemes)
    for pixel in pixels:
        if pixel[0] not in correct_pixels_type:
            print("Bad value: {0} on pixels list".format(pixel))
            exit(EXIT_ERROR)


def main(arguments):
    pixels = read_from_file(arguments.population_file)
    dominance_schemes = arguments.dominance_schemes.split(',')
    verify_inputs(pixels, dominance_schemes)
    population = Population(pixels)
    Reproduction(population, arguments.reproduction_interval, arguments.number_of_iterations).reproduce()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage="This program simulates the reproduction of different kinds of pixel. "
                                           "Call it with the two mandatory arguments as explained below")
    parser.add_argument("population_file", help="A name of a file, which includes a population description: Each line"
                                                "of the file includes a comma separated information- "
                                                'Type of Pixel,value1,value2,value3,[value4].'
                                                'Forth value is in the case of CMYK pixel.')

    parser.add_argument("dominance_schemes", help="Which type of pixel is dominance in its reproducing process."
                                                  "Must be a list of pixel types (RGB, HSL, HSV, CYMK), comma"
                                                  "separated. if you wish to specify an empty list if pixels, "
                                                  "please put the word 'none' ")

    parser.add_argument("reproduction_interval", help="How much time (seconds) between one reproduction to another",
                        type=int)

    parser.add_argument("number_of_iterations", help="How many reproductions you would like to simulate", type=int)

    args = parser.parse_args()
    main(args)
