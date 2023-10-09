from typing import Optional

class ComponentIDRegister:
    def __init__(self, component_names: [str]):
        self.d = {}
        for i in range(len(component_names)):
            self.d[component_names[i]] = f"recipe-component-{i}"

    def component_id(self, component_name: str) -> Optional[str]:
        return self.d.get(component_name)