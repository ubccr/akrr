#!/usr/bin/env python
import os # to get environment vars
import argparse # to deal with given arguments
import shutil # for copying files over


# function that returns the string of the input file corresponding to the given nodes and ppn
def get_input_file_name(nodes, proc_per_node, default=False):
    if default:
        return "default_hpccinf.txt"
    else:
        return "hpccinf.txt." + str(proc_per_node) + "x" + str(nodes)





if __name__ == "__main__":
    hpcc_inputs_dir = os.environ.get("inputsLoc") + "hpcc/"
    print(hpcc_inputs_dir)

    # parsing arguments given in
    parser = argparse.ArgumentParser()
    parser.add_argument("-v","--verbose", action="store_true", help="increase output verbosity")
    parser.add_argument("-d", "--default", action="store_true", help="use default input file")
    parser.add_argument("-n","--nodes", type=int, default=1,
                        help="specify the number of nodes hpcc will be running on (default=1)")
    parser.add_argument("-ppn","--proc_per_node", type=int, default=1,
                        help="specify the number of processes/cores per node (default=1)")
    args = parser.parse_args()

    if args.verbose:
        print("Choosing file with following requirements: ")
        print("Nodes:", args.nodes)
        print("Processes Per Node:", args.proc_per_node)
        print("Default:", args.default)
        print("Now setting up the paths to copy")

    hpcc_input_name = get_input_file_name(args.nodes, args.proc_per_node, args.default)
    input_file_path = hpcc_inputs_dir + hpcc_input_name
    dest_path = os.environ.get("HOME") + "/hpccinf.txt"

    if args.verbose:
        print("Input file name: " + hpcc_input_name)
        print("Full path: " + input_file_path)
        print("Destination path: " + dest_path)
        print("Attempting to copy input file to destination")

    shutil.copy(input_file_path, dest_path)

