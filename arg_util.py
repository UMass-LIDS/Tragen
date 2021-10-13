from constants import *
from collections import defaultdict
import argparse
import json
import sys


def define_arguments():
    parser = argparse.ArgumentParser(description='TRAGEN')

    parser.add_argument('-a', '--available_fds',   action='store_true',  help="show available footprint descriptors")

    parser.add_argument('-x', '--example',   action='store_true',  help="an example")

    parser.add_argument('-c', '--config_file',   action='store',  help="enter the full path to a json config file, example can be found in OUTPUT/config.json")

    parser.add_argument('-d', '--output_dir',   action='store',  help="enter path to output directory")
    
    return parser


def show_available_fds():
    print("available fds are: ")
    availableTcs = defaultdict()
    f = open("FOOTPRINT_DESCRIPTORS/available_fds.txt", "r")
    for l in f:
        l = l.strip().split(",")
        tc = l[1]
        print(tc)
    return availableTcs

    

def show_example():
    print("Here's an example command : python3 tragen_cli.py -c <config_file> -d <output_directory>")

    
## Fill the arguments as entered by the user.
class Arguments():
    def __init__(self):
        self.traffic_classes = ""
        self.traffic_ratio   = ""
        self.length          = 100000000
        self.hitrate_type    = "rhr"


def convertTo(traffic_class, traffic_volume, type="reqs"):
    f = open("FOOTPRINT_DESCRIPTORS/" + traffic_class + "/footprint_desc_all.txt", "r")
    l = f.readline()
    l = l.strip().split(" ")

    duration  = int(l[3]) - int(l[2])
    reqs      = int(l[0])
    req_rate  = float(reqs)/duration
    byte_rate = float(l[1])/duration
    gb_rate   = float(byte_rate)/GB

    if type == "reqs":
        return (traffic_volume*req_rate)/gb_rate
    else:
        return (traffic_volume*gb_rate)/req_rate
         

def read_config_file(config_file):
    with open(config_file) as config:
        config = json.load(config)

    args = Arguments()

    ## Trace length
    args.length = config["Trace_length"]
    if args.length.isnumeric() == False or int(args.length) <= 0:
        print("Enter valid trace length (in number of requests")

    ## Hitrate type
    args.hitrate_type = config["Hitrate_type"]    
    if args.hitrate_type != "rhr" and args.hitrate_type != "bhr":
        print("Input Hitrate_type as either 'rhr' or 'bhr'")
        sys.exit()

    ## Input unit
    if config["Input_unit"] != "gbps" and config["Input_unit"] != "reqs/s":
        print("Input Input_unit as either 'reqs/s' or 'gbps'")
        sys.exit()
    input_unit = config["Input_unit"]
    
    ## Read traffic classes and their traffic volume
    traffic_classes = []
    traffic_ratio   = []

    for tc in config["Traffic_classes"]:

        traffic_classes.append(tc["traffic_class"])

        if args.hitrate_type == "rhr" and input_unit == "gbps":
            traffic_volume = convertTo(tc["traffic_class"], float(tc["traffic_volume"]), "reqs")
        elif args.hitrate_type == "bhr" and input_unit == "reqs/s":
            traffic_volume = convertTo(tc["traffic_class"], float(tc["traffic_volume"]), "gbps")
        else:
            traffic_volume = tc["traffic_volume"]
        traffic_ratio.append(traffic_volume)

    args.traffic_classes = ":".join([str(x).lower() for x in traffic_classes])
    args.traffic_ratio   = ":".join([str(x) for x in traffic_ratio])

    return args

    
        
        
