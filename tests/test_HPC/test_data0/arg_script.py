# A script to test taking in arguments from the command line
import sys
import unox.HPC.data0.run_functions as rf

# Argument 0 is always the name of the script
print(f"Script name (sys.argv[0]): {sys.argv[0]}")

# Print the given command line arguments
print(f"Command line arguments: {sys.argv}")

# Process the command line arguments
cmd_args = rf.process_cmd_args(sys.argv)