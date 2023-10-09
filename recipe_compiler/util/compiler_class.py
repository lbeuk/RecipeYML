from abc import ABC, abstractmethod
from typing import Optional

class RecipeYAMLCompiler(ABC):
    @abstractmethod
    def __init__(self, recipe_dict: dict, data: dict = None):
        pass

    @abstractmethod
    def compile(self) -> Optional[str]:
        pass