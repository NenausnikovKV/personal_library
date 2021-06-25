from source.responce.excerpt_boundaries import ExcerptBoundaries


class FoundComponent:

    def __init__(self, component_name, indices):
        self.component_name = component_name
        self.indices = indices

    @classmethod
    def get_found_components(cls, text, final_components):
        # запаковываем найденные компоненты
        found_components = []
        for component_name, component in final_components.items():
            name = component_name
            component_boundaries = []
            for excerpt in component.text_excerts:
                boundaries = ExcerptBoundaries.get_excerpt_boundaries(text, excerpt)
                component_boundaries.append(boundaries)
            found_components.append(FoundComponent(component_name=name, indices=component_boundaries))
        return found_components





if __name__ == '__main__':

    name = "assign"
    indices = (ExcerptBoundaries(0, 20), ExcerptBoundaries(177, 196))
    found_component = FoundComponent(component_name=name, indices=indices)
