import sympy as sp
class Support:
    def __init__(self):
        self.type = ""
        self.location = 0
        self.possible_supports = ["fixed","simple","bearing","none"]
        self.reaction_forces=[0,0,0]
        self.boundary_condition = [0,0]
    def type_determination(self):
        wrong_input = True
        self.type = input("Type the type of support (fixed/simple/bearing). If there are no more supports type none: ").lower()
        if self.type not in self.possible_supports:
            while wrong_input:
                self.type = input("Please check your spelling"
                                     ".Type the type of support (fixed/simple/bearing). If there are no more supports type none: ").lower()
                if self.type in self.possible_supports:
                    wrong_input = False
        return self.type
    def location_determination(self,l):
        invalid_location = True
        self.location = float(input("Type the location of support in m: "))
        if self.location > l or self.location < 0:
            while invalid_location:
                self.location = float(input("location of support must be within 0 and L: "))
                if 0 <= self.location <= l:
                    invalid_location = False
    def reaction_forces_determination(self,index):
        Rx, Ry, M = sp.symbols(f"Rx{index} Ry{index} M{index}")
        if self.type == "fixed":
            self.reaction_forces = [Rx,Ry,M]
        if self.type == "simple":
            self.reaction_forces = [Rx,Ry,0]
        if self.type == "bearing":
            self.reaction_forces = [0,Ry,0]
    def boundary_conditions_determination(self,index):
        y,theta = sp.symbols(f"y{index} theta{index}")
        if self.type == "fixed":
            self.boundary_condition = [0,0]
        if self.type == "simple":
            self.boundary_condition = [0,theta]
        if self.type == "bearing":
            self.boundary_condition = [0,theta]