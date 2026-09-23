import sympy as sp
from forces import Force
from moments import Moment
from supports import Support
import numpy as np
import matplotlib.pyplot as plt
x = sp.Symbol("x")
##__________________________ PROBLEM DESCRIPTION ____________________________
print("Coordinate system: x along the beam, y is the vertical direction, and z is into the page")
print("Problem is from left to right where the at most left is L=0")
print("Problem must be statically determinable")
# Material
E = float(input("Enter Modulus of elasticity in GPa: "))*1e9
G = float(input("Enter modulus of rigidity in GPa: "))*1e9
# Moment of inertia
I = float(input("Enter moment of inertia in m^4: "))
A = float(input("Enter the area in m^2: "))
# Beam length
L = float(input("Enter beam Length in m: "))
K = float(input("Enter K: "))
LOCATIONS=[0,L]

# Supports
supports = []
more_supports = True
while more_supports:
    support = Support()
    support.type_determination()
    if support.type == "none":
        more_supports = False
    else:
        support.location_determination(L)
        support_number = len(supports) + 1
        support.reaction_forces_determination(support_number)
        support.boundary_conditions_determination(support_number)
        supports.append(support)
        LOCATIONS.append(support.location)



#Forces

forces = []
more_forces = True
while more_forces:
    force = Force()
    force.type_determination()
    if force.type == "none":
        more_forces = False
    else:
        force.magnitude_determination()
        force.location_determination(L)
        if force.type == "point":
            LOCATIONS.append(force.location)
        else:
            LOCATIONS.append(force.location[0])
            LOCATIONS.append(force.location[1])
        forces.append(force)

#moments

moments = []
more_moments = True
while more_moments:
    moment = Moment()
    moment.type_determination()
    if moment.type == "none":
        more_moments = False
    else:
        moment.magnitude_determination()
        moment.location_determination(L)
        if moment.type == "point":
            LOCATIONS.append(moment.location)
        else:
            LOCATIONS.append(moment.location[0])
            LOCATIONS.append(moment.location[1])
        moments.append(moment)
#


#------------------------------------SOLVING THE PROBLEM STATICALLY TO GET THE REACTION FORCES-----------------------------------------
# forces equations
equations = []
for i in range(0,2):
    sumF = 0
    for support in supports:
        sumF += support.reaction_forces[i]
    for force in forces:
        if force.type == "point":
            sumF += force.magnitude[i]
        else:
            equivalent_force = sp.integrate(force.magnitude[i], (x, force.location[0], force.location[1]))
            sumF += equivalent_force
    equations.append(sp.Eq(sumF,0))
#moment equations
sumM = supports[0].reaction_forces[2]
for support in supports[1:]:
    sumM += support.reaction_forces[1]*(support.location - supports[0].location)
for force in forces:
    if force.type == "point":
         sumM += force.magnitude[1]*(force.location - supports[0].location)
    else:
        equivalent_force_moment = sp.integrate((x-supports[0].location)*force.magnitude[1],
                                               (x, force.location[0], force.location[1]))
        sumM += equivalent_force_moment
for moment in moments:
    if moment.type == "point":
        sumM += moment.magnitude[0]
    else:
        equivalent_moment = sp.integrate(moment.magnitude[0], (x, moment.location[0], moment.location[1]))
        sumM = sumM + equivalent_moment
equations.append(sp.Eq(sumM,0))

unknowns = [
    force for support in supports
    for force in support.reaction_forces
    if isinstance(force, sp.Symbol)
]

# 2. Solve the equations system for all collected unknowns
sol = sp.solve(equations, unknowns)

# 3. Save solved values straight into each Support object (1-liner per support)
for support in supports:
    support.reaction_forces = [sol.get(f, f) for f in support.reaction_forces]


#------------------------ CALCULATING SHEAR FORCE AND MOMENT ----------------------
# sorting the LOCATIONS ARRAY from least to most
LOCATIONS = sorted(set(LOCATIONS))
V = 0
M = 0
Mend = 0
Vend = 0
section_shear_forces = []
section_moments = []

for i in range(0,len(LOCATIONS)-1):
    M = Mend
    V = Vend
    for support in supports:
        if support.location == LOCATIONS[i]:
            V += support.reaction_forces[1]
            M -= support.reaction_forces[2]
    for force in forces:
        if force.type == "point":
            if force.location == LOCATIONS[i]:
                V += force.magnitude[1]
        else:
            if force.location[0] <= LOCATIONS[i] < force.location[1]:
                if x in force.magnitude[1].free_symbols:
                    local_force = force.magnitude[1].subs(x,x+LOCATIONS[i])
                    V += sp.integrate(local_force, x)
                else:
                    V += sp.integrate(force.magnitude[1], x)
    for moment in moments:
        if moment.type == "point":
            if moment.location == LOCATIONS[i]:
                M-= moment.magnitude[0]
        else:
            if moment.location[0] <= LOCATIONS[i] < moment.location[1]:
                if x in moment.magnitude[0].free_symbols:
                    local_moment = moment.magnitude[0].subs(x,x+LOCATIONS[i])
                    M -= sp.integrate(local_moment, x)
                else:
                    M -= sp.integrate(moment.magnitude[0], x)
    M += sp.integrate(V, x)
    Mend = M.subs(x, LOCATIONS[i+1]-LOCATIONS[i])
    if x in V.free_symbols:
        Vend = V.subs(x, LOCATIONS[i+1]-LOCATIONS[i])
    else:
        Vend = V
    section_shear_forces.append(V)
    section_moments.append(M)
#---------------------------------FINDING THE DEFLECTION AND ITS SLOPE -------------------------------

constants = []
theta_syms = []
y_syms = []
theta_equations = []
deflection_equations = []
theta_functions = []
deflection_functions = []
Equations = []
# getting the theta, deflection,and the constant expressions
for i in range(0,len(section_moments)):
    y,theta,c,d = sp.symbols(f"y{i+1} theta{i+1} c{i+1} d{i+1}")
    constants.extend([c,d])
    theta_syms.append(theta)
    y_syms.append(y)
    theta_eq = sp.Eq(theta,sp.integrate((1/(E*I))*section_moments[i],x) + c)
    theta_equations.append(theta_eq)
    y_eq = sp.Eq(y,sp.integrate(theta_equations[i].rhs-(section_shear_forces[i]/(K*G*A)),x) + d)
    deflection_equations.append(y_eq)
#boundary conditions

#support boundary condition

for support in supports:
    for i in range(0, len(section_moments)):
        if support.location == LOCATIONS[i] or support.location == LOCATIONS[i+1]:
            if support.boundary_condition[1] == 0:
                theta_BR = theta_equations[i].subs({x: support.location-LOCATIONS[i], theta_syms[i]: support.boundary_condition[1]})
                Equations.append(theta_BR)
            y_BR = deflection_equations[i].subs({x:support.location -LOCATIONS[i] ,y_syms[i]:support.boundary_condition[0]})
            Equations.append(y_BR)
if len(section_moments)>1:
    #equal slope boundary condition
    for i in range(0, len(section_moments) - 1):
        slope_eq = sp.Eq(theta_equations[i].rhs.subs({x:LOCATIONS[i+1]-LOCATIONS[i]}),theta_equations[i+1].rhs.subs({x:0}))
        Equations.append(slope_eq)
        deflect_eq = sp.Eq(deflection_equations[i].rhs.subs({x: LOCATIONS[i + 1] - LOCATIONS[i]}),deflection_equations[i + 1].rhs.subs({x: 0}),)
        Equations.append(deflect_eq)

solution = sp.solve(Equations, constants)
solution_dict = {str(sym): float(val) for sym, val in solution.items()}
print("Solution:", solution)

for i in range(0,len(section_moments)):
    c = sp.Symbol(f"c{i + 1}")
    d = sp.Symbol(f"d{i + 1}")
    c_val = solution_dict[f"c{i + 1}"]
    d_val = solution_dict[f"d{i + 1}"]
    theta_expr =theta_equations[i].rhs.subs({c: c_val})
    theta_functions.append(theta_expr)
    print(f"theta{i + 1}(x) = {theta_expr}")
    y_expr = deflection_equations[i].rhs.subs({c: c_val, d: d_val})
    deflection_functions.append(y_expr)
    print(f"y{i + 1}(x) = {y_expr}")

# ------------------------ GRAPHING THE FUNCTIONS TO GET THE DIAGRAMS ----------------------
X_vals = []
V_vals = []
M_vals = []
Theta_vals = []
Y_vals = []

for i in range(len(section_moments)):
    start = LOCATIONS[i]
    end = LOCATIONS[i + 1]

    x_local = np.linspace(0, end - start, 100)

    V_func = sp.lambdify(x, section_shear_forces[i], "numpy")
    M_func = sp.lambdify(x, section_moments[i], "numpy")
    Theta_func = sp.lambdify(x, theta_functions[i], "numpy")
    Y_func = sp.lambdify(x, deflection_functions[i], "numpy")

    # Evaluate functions
    V_eval = V_func(x_local)
    M_eval = M_func(x_local)
    Theta_eval = Theta_func(x_local)
    Y_eval = Y_func(x_local)

    # If the function is a constant (like the 15000 shear), expand it into an array
    if np.isscalar(V_eval): V_eval = np.full_like(x_local, V_eval, dtype=float)
    if np.isscalar(M_eval): M_eval = np.full_like(x_local, M_eval, dtype=float)
    if np.isscalar(Theta_eval): Theta_eval = np.full_like(x_local, Theta_eval, dtype=float)
    if np.isscalar(Y_eval): Y_eval = np.full_like(x_local, Y_eval, dtype=float)

    # Append values
    X_vals.extend(x_local + start)
    V_vals.extend(V_eval)
    M_vals.extend(M_eval)
    Theta_vals.extend(Theta_eval)
    Y_vals.extend(Y_eval)

# Force the shear diagram to close to zero at the free end
X_V = X_vals + [L]
V_V = V_vals + [0]

# Turn on interactive mode to open all 4 windows simultaneously
plt.ion()

fig1 = plt.figure("Shear Force Diagram")
plt.plot(X_V, V_V, 'r', linewidth=2)
plt.axhline(0, color='black', linewidth=1.5)
plt.axvline(0, color='black', linewidth=1.5)
plt.ylabel('Shear (N)')
plt.xlabel('Beam Length (m)')
plt.grid(True, linestyle='--', alpha=0.6)
fig1.show()

fig2 = plt.figure("Bending Moment Diagram")
plt.plot(X_vals, M_vals, 'b', linewidth=2)
plt.axhline(0, color='black', linewidth=1.5)
plt.axvline(0, color='black', linewidth=1.5)
plt.ylabel('Moment (N·m)')
plt.xlabel('Beam Length (m)')
plt.grid(True, linestyle='--', alpha=0.6)
fig2.show()

fig3 = plt.figure("theat Diagram")
plt.plot(X_vals, Theta_vals, 'g', linewidth=2)
plt.axhline(0, color='black', linewidth=1.5)
plt.axvline(0, color='black', linewidth=1.5)
plt.ylabel('theta (rad)')
plt.xlabel('Beam Length (m)')
plt.grid(True, linestyle='--', alpha=0.6)
fig3.show()

fig4 = plt.figure("Deflection Diagram")
plt.plot(X_vals, Y_vals, 'm', linewidth=2)
plt.axhline(0, color='black', linewidth=1.5)
plt.axvline(0, color='black', linewidth=1.5)
plt.ylabel('Deflection (m)')
plt.xlabel('Beam Length (m)')
plt.grid(True, linestyle='--', alpha=0.6)
fig4.show()

# Turn off interactive mode and hold windows open until closed by user
plt.ioff()
plt.show(block=True)

# ------------------------ FINDING DEFLECTION AND THETA AT ANY POINT ----------------------
more_input = True
while more_input:
    wrong_input = True
    while wrong_input:
        user_input = float(input(f"Please enter the point you want to find the angle and the deflection at(must be within 0 and {L}): "))
        if 0 <= user_input <= L:
            wrong_input = False
    for i in range(len(section_moments)):
        if LOCATIONS[i] <= user_input <= LOCATIONS[i + 1]:
            angle_at_point = theta_functions[i].subs({x: user_input - LOCATIONS[i]})
            deflection_at_point = deflection_functions[i].subs({x: user_input - LOCATIONS[i]})
            print(f"\n--- At x = {user_input} (Section {i + 1}) ---")
            print(f"Slope (theta): {angle_at_point}")
            print(f"Deflection (y): {deflection_at_point}")
            break
    more = input("Would you like to calculate more points? (y/n): ").lower()
    if more == "n":
        more_input = False

print("Program ended")
