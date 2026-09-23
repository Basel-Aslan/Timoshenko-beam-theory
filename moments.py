
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
)
class Moment:
    def __init__(self):
        self.type = ""
        self.magnitude = 0
        self.location = 0
        self.possible_moments = ["point", "function", "none"]

    def type_determination(self):
        wrong_input = True
        self.type = input("Type the type of moment (point or function). If there are no more moments type none: ").lower()
        if self.type not in self.possible_moments:
            while wrong_input:
                self.type = input("Please check your spelling"
                                   ".Type the type of moment (point or function). If there are no more moments type none: ").lower()
                if self.type in self.possible_moments:
                    wrong_input = False
        return self.type
    def magnitude_determination(self):
        if self.type == "point":
            z_expr = float(input("Type the z magnitude of moment in N.m (CCW + and CW -): "))
            y_expr = float(input("Type the y magnitude of force in N.m (CCW + and CW -): "))
            self.magnitude = [z_expr, y_expr]
        if self.type == "function":
            transformations = standard_transformations + (implicit_multiplication_application,)
            z_expr = parse_expr(input("Type the z magnitude of moment in N/m (CCW + and CW -): "),
                                transformations=transformations)
            y_expr = parse_expr(input("Type the y magnitude of moment in N/m (CCW + and CW -): "),
                                transformations=transformations)
            self.magnitude = [z_expr, y_expr]
        return self.magnitude
    def location_determination(self,l):
        invalid_location = True
        if self.type == "point":
            self.location = float(input("Type the location of moment in m: "))
            if self.location > l or self.location < 0:
                while invalid_location:
                    self.location = float(input("location of moment must be within 0 and L: "))
                    if 0 <= self.location <= l:
                        invalid_location = False
        if self.type == "function":
            self.location = [float(input("Type the lower boundary of the location of the moment in m: ")),
                                 float(input("Type the upper boundary of the location of the moment in m: "))]
            self.invalid_lower_bound(l)
            self.invalid_upper_bound(l)
            if self.location[1] < self.location[0]:
                invalid_location = True
                while invalid_location:
                    print("lower boundary of moment must be smaller than upper boundary of moment")
                    self.location[0] = float(input("lower boundary of moment must be within 0 and L: "))
                    self.invalid_lower_bound(l)
                    self.location[1] = float(input("upper boundary of moment must be within 0 and L: "))
                    self.invalid_upper_bound(l)
                    if self.location[1] > self.location[0]:
                        invalid_location = False
        return self.location
    def invalid_lower_bound(self,l):
        if self.location[0] < 0 or self.location[0] > l:
            invalid_location = True
            while invalid_location:
                self.location[0] = float(input("lower boundary of moment must be within 0 and L: "))
                if 0 <= self.location[0] <= l:
                    invalid_location = False
    def invalid_upper_bound(self,l):
        if self.location[1] < 0 or self.location[1] > l:
            invalid_location = True
            while invalid_location:
                self.location[1] = float(input("upper boundary of moment must be within 0 and L: "))
                if 0 <= self.location[1] <= l:
                    invalid_location = False
