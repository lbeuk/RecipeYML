HELP_MSG = """\
RecipeYML - Recipe to static web page compiler

Options:
    compile-recipe {source file} [dst=destination file]:
        Compiles the recipes in the source directory into the destination directory.
"""

import sys
from recipe_compiler import compile_recipe

ARGV = sys.argv
ARGC = len(ARGV)

def cli_compile_recipe():
    if ARGC < 3:
        print("Error: Incorrect number of arguments for compile-recipe", file=sys.stderr)
        exit(1)

    src_file_contents = None
    dst_file = sys.stdout
    try:
        src_file_contents = open(ARGV[2], "r").read()
    except:
        print("Error: Could not open the source file.", file=sts.stderr)
        exit(1)

    for arg in ARGV[3:]:
        split = arg.split('=')
        flag = split[0]
        value = split[1]
        match flag:
            case "dst":
                try:
                    dst_file = open(value, "w+")
                except:
                    print("Error: Could not open the destination file.", file=sys.stderr)
                    exit(1)

    
    compiled_recipe = compile_recipe(src_file_contents)

    if compiled_recipe == None:
        exit(1)

    print(compiled_recipe, file=dst_file)

if __name__ == "__main__":
    match ARGV[1]:
        case "compile-recipe":
            cli_compile_recipe()
        case _:
            print(HELP_MSG)
