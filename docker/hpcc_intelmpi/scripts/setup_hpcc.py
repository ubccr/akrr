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
    # parsing arguments given in
    parser = argparse.ArgumentParser()
    parser.add_argument("-v","--verbose", action="store_true", help="increase output verbosity")
    parser.add_argument("-D", "--default", action="store_true", help="use default input file")
    parser.add_argument("-n","--nodes", type=int, default=1,
                        help="specify the number of nodes hpcc will be running on (default=1)")
    parser.add_argument("-ppn","--proc_per_node", type=int, default=1,
                        help="specify the number of processes/cores per node (default=1)")
    # another argument to potentially specify what directory to copy it into? - potential future
    args = parser.parse_args()

    # for better verbose readability
    verbose_start = "\33[33mDEBUG START========================== \33[0m "
    verbose_end = "\33[33m============================DEBUG END \33[0m "

    # printing warning to ensure intentional usage
    if args.default:
        print("\33[93mWARNING: Default file chosen, -n and -ppn arguments ignored \33[0m")

    # verbose
    if args.verbose:
        print(verbose_start)
        print("Choosing file with following requirements: ")
        print("Nodes:", args.nodes)
        print("Processes Per Node:", args.proc_per_node)
        print("Default:", args.default)
        print("Now setting up the paths to copy")
        print(verbose_end)

    # setting up paths
    hpcc_inputs_dir = os.environ.get("inputsLoc") + "hpcc/"
    hpcc_input_name = get_input_file_name(args.nodes, args.proc_per_node, args.default)
    input_file_path = hpcc_inputs_dir + hpcc_input_name
    dest_path = os.environ.get("HOME") + "/hpccinf.txt"

    #verbose
    if args.verbose:
        print(verbose_start)
        print("Input file name: " + hpcc_input_name)
        print("Full path: " + input_file_path)
        print("Destination path: " + dest_path)
        print("Attempting to copy input file to destination")
        print(verbose_end)

    # attempting the copy
    try:
        shutil.copy(input_file_path, dest_path)
        print("Successfully copied over proper input file to HOME directory")
    except IOError as e:
        # printing suggestions to possibly fix the issue
        print("\33[91m" + str(e) + "\33[0m")
        print("Possibly you wanted to use the default file? If so, use the -D/--default flag")
        print("Otherwise, add the desired file to " + hpcc_inputs_dir + " or just rename it to hpccinf.txt in the desired directory")
        print("(By default this script copies the file into the HOME directory)")
        print("Use the -v flag for more information")

