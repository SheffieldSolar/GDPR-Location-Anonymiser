"""
Code to determine the appropriate fishnet grid parameters necessary to anonymise a set of locations.

Jamie Taylor
2019-11-08
"""

import sys
import os
import argparse
import time as TIME
import numpy as np
import pandas as pd

def load_locations_from_file(filename):
    with open(filename) as fid:
        locations = pd.read_csv(fid)
    return locations

def parse_options():
    parser = argparse.ArgumentParser(description="Determine optimal grid required to anonymise "
                                                 "locations.")
    parser.add_argument("-f", "--infile", metavar="<path-to-file>", dest="infile", action="store",
                        required=True, type=str, help="Specify a CSV file containing id,lon,lat "
                                                      "co-ordinates (one pair of co-ordinates per "
                                                      "line) with headerline "
                                                      "'id,longitude,latitude'.")
    parser.add_argument("-n", "--number", metavar="<n_systems>", dest="min_systems", action="store",
                        type=int, required=False, default=3, help="Specify the minimum number of "
                                                                  "systems per grid square to "
                                                                  "achieve anonymisation (defaults "
                                                                  "to 3).")
    parser.add_argument("-t", "--tolerance", metavar="<n_systems>", dest="tolerance",
                        action="store", type=int, required=False, default=10,
                        help="Specify the number of systems that can be discarded in order to "
                             "achieve smaller grid size.")
    options = parser.parse_args()
    if not os.path.isfile(options.infile):
        raise Exception(f"The input file '{options.infile}' does not exist.")
    return options

def find_optimal_grid(locations, min_systems, converge=0.001, extent=(-7., 49., 2.2, 61.), tolerance=10, isotropic=False):
    xdelta = 0.1
    ydelta = 0.1
    iterator = xdelta * 2. / 3.
    finished = False
    last = False
    prev = None
    while not finished:
        success = False
        print(f"xdelta: {xdelta}, ydelta: {ydelta}")
        for yoffset in np.arange(0., ydelta, ydelta / 2.):
            for xoffset in np.arange(0., xdelta, xdelta / 2.):
                if success:
                    continue
                print(f"    xoffset: {xoffset}, yoffset: {yoffset}")
                i = 0
                blacklisted_cells = []
                systems_to_exclude = pd.DataFrame(columns=locations.columns, data=None)
                lons = np.arange(extent[0] + xoffset, extent[2] + xdelta, xdelta)
                lats = np.arange(extent[1] + yoffset, extent[3] + ydelta, ydelta)
                total = len(lats) * len(lons)
                np.random.shuffle(lons)
                np.random.shuffle(lats)
                for lon_ in lons:
                    for lat_ in lats:
                        lon_condition = (locations["longitude"] >= lon_) & \
                                        (locations["longitude"] < lon_ + xdelta)
                        lat_condition = (locations["latitude"] >= lat_) & \
                                        (locations["latitude"] < lat_ + ydelta)
                        local = locations[lon_condition & lat_condition]
                        n_systems = len(local)
                        i += 1
                        if not i % 10:
                            print_progress(i, total, prefix="        ", suffix=f"({i} of {total})",
                                           decimals=2, bar_length=100)
                        if 0 < n_systems < min_systems:
                            if len(systems_to_exclude) > tolerance:
                                break
                            else:
                                systems_to_exclude = pd.concat([systems_to_exclude, local])
                                blacklisted_cells.append((lon_, lat_))
                    if 0 < n_systems < min_systems and len(systems_to_exclude) > tolerance:
                        break
                print_progress(total, total, prefix="        ", suffix=f"({i} of {total})", decimals=2,
                               bar_length=100)
                if n_systems == 0 or n_systems > min_systems:
                    break
                print(f"        -> Failed (excluded={len(systems_to_exclude)}), incrementing x offset...")
            if n_systems == 0 or n_systems > min_systems:
                success = True
                break
            print("        -> Failed, incrementing y offset...")
        if success:
            if iterator > converge:
                if prev == "increase":
                    iterator *= 0.5
                else:
                    while xdelta - iterator < 0:
                        iterator *= 2. / 3.
                print(f"        -> Succeeded, decreasing grid size by {iterator}...")
                xdelta -= iterator
                ydelta -= iterator
                prev = "decrease"
            else:
                print("        -> Converged, exiting...")
                finished = True
        else:
            if prev == "decrease":
                iterator *= 0.5
            print(f"        -> Failed (excluded={len(systems_to_exclude)}), increasing grid size "
                  f"by {iterator}...")
            xdelta += iterator
            ydelta += iterator
            prev = "increase"
        xdelta = max(xdelta, converge)
        ydelta = max(ydelta, converge)
    return (xoffset, yoffset), (xdelta, ydelta), blacklisted_cells, systems_to_exclude

def print_progress(iteration, total, prefix="", suffix="", decimals=2, bar_length=100):
    """
    Call in a loop to create terminal progress bar.

    Parameters
    ----------
    `iteration` : int
        current iteration (required)
    `total` : int
        total iterations (required)
    `prefix` : string
        prefix string (optional)
    `suffix` : string
        suffix string (optional)
    `decimals` : int
        number of decimals in percent complete (optional)
    `bar_length` : int
        character length of bar (optional)
    Notes
    -----
    Taken from `Stack Overflow <http://stackoverflow.com/a/34325723>`_.
    """
    filled_length = int(round(bar_length * iteration / float(total)))
    percents = round(100.00 * (iteration / float(total)), decimals)
    progress_bar = "#" * filled_length + "-" * (bar_length - filled_length)
    sys.stdout.write("\r%s |%s| %s%s %s" % (prefix, progress_bar, percents, "%", suffix))
    sys.stdout.flush()
    if iteration == total:
        sys.stdout.write("\n")
        sys.stdout.flush()

def main():
    options = parse_options()
    timerstart = TIME.time()
    locations = load_locations_from_file(options.infile)
    print("Determining the optimal grid to use for location anonymisation of:")
    print(f"    {len(locations)} locations")
    print(f"    with max {options.min_systems} per grid square")
    print(f"    and up to {options.tolerance} locations discarded")
    print("---- BEGIN OPTIMISATION ----")
    offset, grid_size, blacklist, excluded_systems = find_optimal_grid(locations,
                                                                       options.min_systems,
                                                                       tolerance=options.tolerance)
    time_taken = TIME.time() - timerstart
    time_taken_mins = time_taken / 60
    print(f"Finished, took {time_taken:.2f} seconds ({time_taken_mins:.2f} minutes)")
    import pdb; pdb.set_trace()

if __name__ == "__main__":
    main()