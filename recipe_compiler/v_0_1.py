from pybars import Compiler
import types
from .util.compiler_class import RecipeYAMLCompiler
from .util.component_id_register import ComponentIDRegister
from .util.time_accumulator import TimeAccumulator
from typing import Optional
import sys

# Key namespaces prefixed with YM correspond to the keys in the YAML files.
# Key namespaces prefixed with HB correspond to the keys in the dictionary
# sent to the handlebars compiler.

YM_INGREDIENT_KEYS = types.SimpleNamespace()
YM_INGREDIENT_KEYS.AMOUNT = "Amount"
YM_INGREDIENT_KEYS.NOTE = "Note"
YM_INGREDIENT_KEYS.CREF = "CREF"

HB_INGREDIENT_KEYS = types.SimpleNamespace()
HB_INGREDIENT_KEYS.NAME = "name"
HB_INGREDIENT_KEYS.AMOUNT = "amount"
HB_INGREDIENT_KEYS.NOTE = "note"
HB_INGREDIENT_KEYS.CREF = "cref"

YM_COMPONENT_KEYS = types.SimpleNamespace()
YM_COMPONENT_KEYS.INGREDIENTS = "Ingredients"
YM_COMPONENT_KEYS.INSTRUCTIONS = "Instructions"
YM_COMPONENT_KEYS.TIME = "Time"
YM_COMPONENT_KEYS.MAIN = "Main"

HB_COMPONENT_KEYS = types.SimpleNamespace()
HB_COMPONENT_KEYS.NAME = "name"
HB_COMPONENT_KEYS.ID = "id"
HB_COMPONENT_KEYS.INGREDIENTS = "ingredients"
HB_COMPONENT_KEYS.INSTRUCTIONS = "instructions"
HB_COMPONENT_KEYS.TIME = "time"

YM_RECIPE_KEYS = types.SimpleNamespace()
YM_RECIPE_KEYS.METADATA = "Metadata"
YM_RECIPE_KEYS.COMPONENTS = "Components"

HB_RECIPE_KEYS = types.SimpleNamespace()
HB_RECIPE_KEYS.SUBCOMPONENTS = "subcomponents"
HB_RECIPE_KEYS.MAINCOMPONENT = "maincomponent"
HB_RECIPE_KEYS.TOTAL_TIME = "totaltime"
HB_RECIPE_KEYS.TIME = "time"

HB_TIME_KEYS = types.SimpleNamespace()
HB_TIME_KEYS.NAME = "name"
HB_TIME_KEYS.LENGTH = "length"

class CompilerV_0_1(RecipeYAMLCompiler):
    def __init__(self, recipe_dict: dict, data: dict = None):
        self.recipe_dict = recipe_dict
        self.meta = recipe_dict[YM_RECIPE_KEYS.METADATA]
        self.components = recipe_dict[YM_RECIPE_KEYS.COMPONENTS]
        self.component_id_register = ComponentIDRegister(list(self.components.keys()))
        self.times = {}
        self.main_component = None

    def compile_ingredient(
        self, ingredient_name: str, ingredient_data: dict
    ) -> Optional[str]:
        hb_data = {HB_INGREDIENT_KEYS.NAME: ingredient_name}

        for key, value in ingredient_data.items():
            match key:
                case YM_INGREDIENT_KEYS.AMOUNT:
                    hb_data[HB_INGREDIENT_KEYS.AMOUNT] = value
                case YM_INGREDIENT_KEYS.NOTE:
                    hb_data[HB_INGREDIENT_KEYS.NOTE] = value
                case YM_INGREDIENT_KEYS.CREF:
                    cref = self.component_id_register.component_id(value)
                    if cref is None:
                        print(
                            'Error: Ingredient CREF "{value}" does not exist in components.',
                            file=sys.stderr,
                        )
                        return None
                    hb_data[HB_INGREDIENT_KEYS.CREF] = cref

        template_text = open("templates/default/ingredient.handlebars", "r").read()

        compiler = Compiler()
        template = compiler.compile(template_text)

        output = template(hb_data)
        return output

    def compile_component(
        self, component_name: str, component_data: dict
    ) -> Optional[str]:
        hb_data = {
            HB_COMPONENT_KEYS.NAME: component_name,
            HB_COMPONENT_KEYS.ID: self.component_id_register.component_id(
                component_name
            ),
        }

        is_main = False

        for key, value in component_data.items():
            match key:
                case YM_COMPONENT_KEYS.INGREDIENTS:
                    ingredients = [
                        self.compile_ingredient(ingredient_name, ingredient_data)
                        for ingredient_name, ingredient_data in value.items()
                    ]
                    if None in ingredients:
                        return None
                    hb_data[HB_COMPONENT_KEYS.INGREDIENTS] = ingredients
                case YM_COMPONENT_KEYS.INSTRUCTIONS:
                    hb_data[HB_COMPONENT_KEYS.INSTRUCTIONS] = value
                case YM_COMPONENT_KEYS.TIME:
                    times = []
                    for name, time in value.items():
                        ta = TimeAccumulator(time)
                        if name in self.times.keys():
                            self.times[name] = self.times[name] + ta
                        else:
                            self.times[name] = ta
                        times.append(
                            {
                                HB_TIME_KEYS.NAME: name,
                                HB_TIME_KEYS.LENGTH: str(ta),
                            }
                        )
                    hb_data[HB_COMPONENT_KEYS.TIME] = times
                case YM_COMPONENT_KEYS.MAIN:
                    is_main = True
                    if self.main_component is not None:
                        print(
                            "Error: There is more than one main component defined.",
                            file=sys.stderr,
                        )
                        return None
        
        if is_main:
            self.main_component = hb_data
            return ""

        template_text = open("templates/default/subcomponent.handlebars", "r").read()

        compiler = Compiler()
        template = compiler.compile(template_text)

        output = template(hb_data)
        return output

    def render_maincomponent(self) -> Optional[str]:
        hb_data = self.main_component

        template_text = open("templates/default/maincomponent.handlebars", "r").read()

        compiler = Compiler()
        template = compiler.compile(template_text)

        output = template(hb_data)
        return output


    def compile(self) -> Optional[str]:
        hb_data = {}
        
        subcomponents = []

        for component_name, component_data in self.recipe_dict[
            YM_RECIPE_KEYS.COMPONENTS
        ].items():
            if (
                rendered_component := self.compile_component(
                    component_name, component_data
                )
            ) is not None:
                if rendered_component != "":
                    subcomponents.append(rendered_component)
            else:
                return None


        maincomponent = self.render_maincomponent()
        if maincomponent is None:
            return None

        total_time = None
        for time in self.times:
            if total_time is None:
                total_time = time
            else:
                total_time += time


        hb_data[HB_RECIPE_KEYS.SUBCOMPONENTS] = subcomponents
        hb_data[HB_RECIPE_KEYS.MAINCOMPONENT] = maincomponent
        hb_data[HB_RECIPE_KEYS.TIME] = [[k, v] for k, v in self.times.items()]
        hb_data[HB_RECIPE_KEYS.TOTAL_TIME] = total_time

        template_text = open("templates/default/recipe.handlebars", "r").read()

        compiler = Compiler()
        template = compiler.compile(template_text)

        output = template(hb_data)
        return output