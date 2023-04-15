import argparse
import csv
import json
import logging
import random
import os.path
from configparser import ConfigParser

from chase.Sheep import Sheep
from chase.Wolf import Wolf


def random_coordinates(init_pos_limit):
    number = round(random.uniform(-init_pos_limit, init_pos_limit), 3)
    logging.debug(f"Called random_coordinates({init_pos_limit}), returned {number}")
    return number


def creating_flock_of_sheep(size, init_pos_limit):
    flock = []
    for i in range(size):
        sheep = Sheep()
        sheep.number = i + 1
        sheep.x = random_coordinates(init_pos_limit)
        sheep.y = random_coordinates(init_pos_limit)
        flock.append(sheep)
    logging.debug(f"Called creating_flock_of_sheep({size},{init_pos_limit}), returned {flock}")
    return flock


def calculate_eaten_sheep(flock):
    alive_counter = 0
    for i in range(len(flock)):
        if flock[i].status == 'alive':
            alive_counter += 1
    if alive_counter == 0:
        logging.info("There is no sheep alive in flock")
    return alive_counter


def moving_flock(flock, sheep_move_dist):
    for sheep in flock:
        if sheep.status == 'alive':
            sheep.move(sheep_move_dist)
    logging.debug(f"Called moving_flock({flock}, {sheep_move_dist})")


def simulation(rounds, size, init_pos_limit, sheep_move_dist, wolf_move_dist, directory, wait):
    list_of_dictionary = []
    path = get_path(directory)
    rounds_counter = 1
    wolf = Wolf()
    flock = creating_flock_of_sheep(size, init_pos_limit)
    while rounds_counter <= rounds and calculate_eaten_sheep(flock) != 0:
        print(f"This is round number {rounds_counter}")
        wolf.move(wolf_move_dist, flock)
        moving_flock(flock, sheep_move_dist)
        print(f"The wolf position is: {round(wolf.x, 3)}, {round(wolf.y, 3)}")
        print(f"Number of alive sheep is: {calculate_eaten_sheep(flock)}")
        logging.info(f"This is round number {rounds_counter}, the wolf position is:"
                     f" {round(wolf.x, 3)}, {round(wolf.y, 3)}, "
                     f"number of alive sheep is: {calculate_eaten_sheep(flock)} ")
        csv_write(rounds_counter, calculate_eaten_sheep(flock), create_path_of_file(path, 'alive.csv'))
        list_of_dictionary.append(making_dictionary(flock, wolf, rounds_counter))
        rounds_counter += 1
        if wait:
            waiting()
        print()
    list_of_dictionary_to_json(list_of_dictionary, create_path_of_file(path, 'pos.json'), directory)


def csv_write(rounds, alive, filename):
    fieldnames = ['round', 'number_of_alive_sheep']
    if rounds == 1:
        csv_file = open(filename, "w+", newline='')
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
    else:
        csv_file = open(filename, "a", newline='')
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writerow({'round': rounds, 'number_of_alive_sheep': alive})
    logging.debug(f"Called csv_write({rounds},{alive},{filename})")
    csv_file.close()


def making_dictionary(flock, wolf, round_number):
    dictionary = {
        "round_no": round_number,
        "wolf_pos": wolf.get_position(),
        "sheep_pos": []
    }
    for sheep in flock:
        if sheep.status == 'alive':
            dictionary["sheep_pos"].append(sheep.get_position())
        else:
            dictionary["sheep_pos"].append(None)
    logging.debug(f"Called making_dictionary({flock},{wolf},{round_number}), returned {dictionary}")
    return dictionary


def list_of_dictionary_to_json(dictionary_list, filename, directory):
    path = get_path(directory)
    is_exist = os.path.exists(path)
    if is_exist:
        f = open(filename, "w+")
        f.write(json.dumps(dictionary_list, indent=4))
        f.close()
    else:
        f = open(filename, "a")
        f.write(json.dumps(dictionary_list, indent=4))
        f.close()
    logging.debug(f"Called list_of_dictionary_to_json({dictionary_list},{filename},{directory})")


def create_path_of_file(path, filename):
    return os.path.join(path, filename)


def get_path(directory):
    path = os.getcwd()
    if not (directory is None):
        path = os.path.join(path, directory)
        if not os.path.exists(path):
            os.mkdir(path)
    logging.debug(f"Called get_path({directory}), returned {path} ")
    return path


def waiting():
    logging.debug("Called waiting")
    input("Press a key to continue...")


def parse_config(filename):
    config = ConfigParser()
    config.read(filename)
    init = config.get('Terrain', 'InitPosLimit')
    sheep = config.get('Movement', 'SheepMoveDist')
    wolf = config.get('Movement', 'WolfMoveDist')
    if float(init) < 0 or float(sheep) < 0 or float(wolf) < 0:
        logging.error("Not positive number passed as argument")
        raise ValueError("Not positive number")
    logging.debug(f"Called parse_config({filename}),returned {float(init), float(sheep), float(wolf)}")
    return float(init), float(sheep), float(wolf)


def check_positive(value):
    amount = int(value)
    if amount <= 0:
        raise argparse.ArgumentTypeError("%s value must be positive" % value)
    logging.debug(f"Called check_positive({value}), returned {amount}")
    return amount


def main():
    rounds = 50
    sheep_number = 15
    init_pos_limit = 10.0
    sheep_move_dist = 0.5
    wolf_move_dist = 1.0
    directory = None
    wait = False
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help="set config file", action='store', dest='conf_file', metavar='FILE')
    parser.add_argument('-d', '--dir', action='store', help="choose where to save files", dest='directory',
                        metavar='DIR')
    parser.add_argument('-l', '--log', action='store', help="create log file with log LEVEL", dest='log_lvl',
                        metavar='LEVEL')
    parser.add_argument('-r', '--rounds', action='store',
                        help="choose amount of rounds", dest='amount_of_rounds',
                        type=check_positive, metavar='NUM')
    parser.add_argument('-s', '--sheep', action='store',
                        help="choose amount of sheep", dest='amount_of_sheep', type=check_positive,
                        metavar='NUM')
    parser.add_argument('-w', '--wait', action='store_true', help="wait for input after each round")
    args = parser.parse_args()
    if args.conf_file:
        init_pos_limit, sheep_move_dist, wolf_move_dist = parse_config(args.conf_file)
    if args.directory:
        directory = args.directory
    if args.log_lvl:
        if args.log_lvl.lower() == "DEBUG".lower():
            lvl = logging.DEBUG
        elif args.log_lvl.lower() == "INFO".lower():
            lvl = logging.INFO
        elif args.log_lvl.lower() == "WARNING".lower():
            lvl = logging.WARNING
        elif args.log_lvl.lower() == "ERROR".lower():
            lvl = logging.ERROR
        elif args.log_lvl.lower() == "CRITICAL".lower():
            lvl = logging.CRITICAL
        else:
            raise ValueError("Invalid log level!")
        filename = create_path_of_file(get_path(directory), "chase.log")
        logging.basicConfig(level=lvl, filename=filename, force=True)
    if args.amount_of_rounds:
        rounds = args.amount_of_rounds
    if args.amount_of_sheep:
        sheep_number = args.amount_of_sheep
    if args.wait:
        wait = args.wait
    simulation(rounds, sheep_number, init_pos_limit, sheep_move_dist, wolf_move_dist, directory, wait)
