import sys
import yaml
from typing import Dict, Type, Optional
from .util.compiler_class import RecipeYAMLCompiler
import traceback


# Compiler imports
from .v_0_1 import CompilerV_0_1

METADATA_KEY = "Metadata" # Key for metadata in YAML file
VERSION_KEY = "RecipeYML" # Key for version in metadata

# Maps compiler string to appropriate function
COMPILERS: Dict[str, Type[RecipeYAMLCompiler]] = {
    "0.1": CompilerV_0_1
}

def compile_recipe(recipe_text: str) -> Optional[str]:    
    # Read metadata block
    recipe_dict = None
    compiler_version = None

    try:
        recipe_dict = yaml.load(recipe_text, Loader=yaml.Loader)
        recipe_metadata = recipe_dict[METADATA_KEY]
        # recipe_title = recipe_metadata["Title"]
        # recipe_author = recipe_metadata["Author"]
        # recipe_version = recipe_metadata["Version"].split(".")
        compiler_version = str(recipe_metadata[VERSION_KEY])
    except:
        print(f"File \"{path}\" does not have a valid RecipeYML Metadata block.")

    # Get compiler
    RecipeCompiler: Type[RecipeYAMLCompiler]

    try:
        RecipeCompiler = COMPILERS[compiler_version]
    except:
        print(f"Info: Recipe file \"{path}\" requires an unsupported RecipeYML spec version ({compiler_version}), and is being ignored.")
        return None

    # Compile
    try:
        compiler = RecipeCompiler(recipe_dict)
        return compiler.compile()

    except Exception as e:
        print("File failed compilation.", file=sys.stderr)
        print(e)
        traceback.print_exc()
    
    return None
        

    