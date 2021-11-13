import epub2sphinx
import sys

def unit_test(function_name):
    if "create_directory_structure" == function_name:
        print(function_name)
        epub2sphinx.create_directory_structure("testing",["source","build"])

unit_test(sys.argv[1])
