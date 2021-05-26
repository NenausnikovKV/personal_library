class Component:
    def __init__(self, name, vivo, necessity=True):
        self.name = name
        self.vivo = vivo
        self.necessity = necessity
    
    def __repr__(self):
        return "{0} \n {1}".format(self.name, self.vivo)


