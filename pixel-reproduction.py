import argparse
import numpy
import time
import math
import random
from multiprocessing import Pool
from abc import ABC, abstractmethod
import colorsys

MIN_PIXEL_RANGE = 0
MAX_PIXEL_RANGE = 255
LIFESPAN = 7
DEFAULT_THRESHOLD = 4
MIN_GENERATION_FOR_REPRODUCTION = 2
MAX_GENERATION_FOR_REPRODUCTION = 5


class Pixel(ABC):

    threshold_to_reproduce = DEFAULT_THRESHOLD
    dominance_dict = {}

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

        return (first_values[0] + second_values[0]) // 2, (first_values[1] + second_values[1]) // 2, \
               (first_values[2] + second_values[2]) // 2

    @staticmethod
    def reproduce_couple(couple):
        first_type = type(couple[0]).__name__
        second_type = type(couple[1]).__name__
        global child_type
        if Pixel.dominance_dict[first_type]:
            if Pixel.dominance_dict[second_type]:
                rnd_choice = random.randint(0, 1)
                child_type = first_type if rnd_choice == 0 else second_type
            else:
                child_type = first_type
        else:
            if Pixel.dominance_dict[second_type]:
                child_type = second_type
            else:
                rnd_choice = random.randint(0, 1)
                child_type = first_type if rnd_choice == 0 else second_type
        r, g, b = Pixel.rgb_average(couple[0], couple[1])

        if child_type == 'RGB':
            return RGB((r, g, b))
        elif child_type == 'HSL':
            r, g, b = r / MAX_PIXEL_RANGE, g // MAX_PIXEL_RANGE, b // MAX_PIXEL_RANGE
            return HSL(HSL.from_RGB(r, g, b))
        elif child_type == 'HSV':
            r, g, b = r / MAX_PIXEL_RANGE, g // MAX_PIXEL_RANGE, b // MAX_PIXEL_RANGE
            return HSV(HSV.from_RGB(r, g, b))
        elif child_type == 'CMYK':
            r, g, b = r / MAX_PIXEL_RANGE, g // MAX_PIXEL_RANGE, b // MAX_PIXEL_RANGE
            return CMYK(CMYK.from_RGB(r, g, b))


class RGB(Pixel):

    options = ['RGB', 'HSV', 'CMYK']

    def __init__(self, scheme):
        self.first = scheme[0]
        self.second = scheme[1]
        self.third = scheme[2]
        super().__init__()

    def __repr__(self):
        return '(Red= {0}, Green= {1}, Blue= {2})'.format(self.first, self.second, self.third)

    def asRGB(self):
        return self.get_values()


    def get_options(self):
        return RGB.options

    def get_values(self):
        return self.first, self.second, self.third


class HSL(Pixel):

    options = ['HSL', 'HSV']

    def __init__(self, scheme):
        self.first = scheme[0]
        self.second = scheme[1]
        self.third = scheme[2]
        super().__init__()

    def __repr__(self):
        return '(Hue= {0}°, Saturation= {1}, Lightness= {2})'.format(self.first, self.second, self.third)

    def asRGB(self):
        h, s, l = self.get_values()
        return tuple(round(i * 255) for i in colorsys.hls_to_rgb(h, l, s))

    @staticmethod
    def from_RGB(r, g, b):
        h, l, s = tuple(round(i * 255) for i in colorsys.rgb_to_hls(r, g, b))
        return h, s, l


    def get_options(self):
        return HSL.options

    def get_values(self):
        return self.first, self.second, self.third


class HSV(Pixel):

    options = ['HSV', 'RGB', 'CMYK', 'HSL']

    def __init__(self, scheme):
        self.first = scheme[0]
        self.second = scheme[1]
        self.third = scheme[2]
        super().__init__()


    def __repr__(self):
        return '(Hue= {0}°, Saturation= {1}, Value= {2})'.format(self.first, self.second, self.third)

    def asRGB(self):
        h, s, v = self.get_values()
        return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))

    @staticmethod
    def from_RGB(r, g, b):
        return tuple(round(i * 255) for i in colorsys.rgb_to_hsv(r, g, b))

    def get_options(self):
        return HSV.options

    def get_values(self):
        return self.first, self.second, self.third


class CMYK(Pixel):

    options = ['CMYK',  'HSV', 'RGB']

    def __init__(self, scheme):
        self.first = scheme[0]
        self.second = scheme[1]
        self.third = scheme[2]
        self.forth = scheme[3]
        super().__init__()


    def __repr__(self):
        return '(Cyan= {0}°, Magenta= {1}, Yellow= {2}, Black= {3})'.format(self.first, self.second, self.third,
                                                                           self.forth)

    def get_values(self):
        return self.first, self.second, self.third, self.forth

    def asRGB(self):
        cyan, magenta, yellow, black = self.get_values()
        r = 255 * (1 - cyan) * (1 - black)
        g = 255 * (1 - magenta) * (1 - black)
        b = 255 * (1 - yellow) * (1 - black)

        return r, g, b

    @staticmethod
    def from_RGB(r, g, b):
        r_tag = r // 255
        g_tag = g // 255
        b_tag = b // 255

        k = 1 - max(r_tag, g_tag, b_tag)
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
            if pixel_type == 'RGB':
                self.community[i] = RGB(pixels[i][1:])
            elif pixel_type == 'HSL':
                self.community[i] = HSL(pixels[i][1:])
            elif pixel_type == 'HSV':
                self.community[i] = HSV(pixels[i][1:])
            elif pixel_type == 'CMYK':
                self.community[i] = CMYK(pixels[i][1:])
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
        for index, pixel in self.community.items():
            if pixel.get_generation() >= LIFESPAN:
                self.community.pop(index)

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
        return 'Stage {0}:\n{1}\n'.format(self.get_cur_stage(), self.population)

    def increment_stage(self):
        self.stage += 1

    def get_cur_stage(self):
        return self.stage

    def reproduce_executor(self):
        couples = []
        couples_ids = []
        cur_population = self.population.get_community()
        for id, pixel in cur_population.items():
            if id in couples_ids or pixel.get_generation() < MIN_GENERATION_FOR_REPRODUCTION :
                continue
            possible_mate = pixel.get_mate()
            if possible_mate and possible_mate in cur_population:
                couples.append((pixel, cur_population[possible_mate]))
                couples_ids.extend([id, possible_mate])
            else:
                options_types = pixel.get_options()
                best_option_pixel_id = None
                best_option_pixel_value = 0

                for pair_id, pair_pixel in cur_population.items():
                    if pair_id == id or pair_id in couples_ids or type(pair_pixel).__name__ not in options_types:
                        continue
                    square_distance = Pixel.squares_distance(pixel, pair_pixel)
                    if square_distance > Pixel.threshold_to_reproduce and square_distance > best_option_pixel_value:
                        best_option_pixel_id = pair_id
                if best_option_pixel_id:
                    couples_ids.extend([id, best_option_pixel_id])
                    couples.append((pixel, cur_population[best_option_pixel_id]))
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
            print(self)

            next_call += self.reproduction_interval
            time.sleep(next_call - time.time())



def main():
    dominance_dict = {'RGB': True, 'HSL': False, 'HSV': True, 'CMYK': False}
    pixels = [['RGB', 14, 240, 100],
             ['HSL', 0.2, 0.1, 0.9],
             ['HSV', 0.4, 0.2, 0.7],
             ['CMYK', 120, 56, 200, 12]]
    Pixel.dominance_dict = dominance_dict
    population = Population(pixels)
    Reproduction(population, 1, 5).reproduce()





if __name__ == '__main__':
    # parser = argparse.ArgumentParser(usage="This program simulates the reproduction of pixels. "
    #                                                        "Call it with the 4 mandatory arguments explained below")
    #
    # parser.add_argument("initial_pixels_amount", help="How many pixels would you like to begin "
    #                                                   "with. Must be greater then 2 in order to reproduce", type=int)
    #
    # parser.add_argument("reproduction_interval", help="How much time (seconds) between one reproduction to another",
    #                     type=int)
    #
    #
    # parser.add_argument("number_of_iterations", help="How many reproductions you would like to simulate", type=int)
    #
    #
    # parser.add_argument("reproductions_amount_till_death", help="How many reproductions a pixel can participate before"
    #                                                             "death. Must be greater then 2 in order to reproduce",
    #                     type=int)
    #
    # args = parser.parse_args()
    main()
