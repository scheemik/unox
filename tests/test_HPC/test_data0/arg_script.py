# A script to test taking in arguments from the command line
import sys
import unox.HPC.data0.run_functions as rf

# Argument 0 is always the name of the script
print(f"Script name (sys.argv[0]): {sys.argv[0]}")

# Make a blank list in which to collect command line arguments
cmd_args = []
for arg in sys.argv:
    cmd_args.append(arg)

print(f"Command line arguments: {cmd_args}")

cmd_args = rf.process_cmd_args(cmd_args)