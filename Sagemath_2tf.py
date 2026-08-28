from sage.all import *

def to_transfer_function(topology, infinite_gain=True, infinite_bandwidth=True):
    """
    Calculates the Transfer Function of arbitrary circuit topology.

    Returns a dictionary containing coefficients of the numerator and denominator polynomials.
    Format: {exponent: "coefficient_str", ...}
    """
    h,s = var(['h','s'])
    Aol = var('Aol', latex_name='A_{OL}')

    node_set = {0,1,2}
    comp_symbols = {}
    for designator in ['r','l','c']:
        if topology[designator]:
            comp_symbols[designator] = var([designator+str(i+1) for i,_ in enumerate(topology[designator])])
            for component in topology[designator]:
                node_set.update(component)
    node_symbols = {node:var("n"+str(node)) for node in node_set}
    node_symbols[0] = 0
    node_symbols[1] = var('Vin')
    node_symbols[2] = var('Vout')

    equations = [h==node_symbols[2]/node_symbols[1]]
    targets = [h]
    low_impedance_nodes = {0,1}
    if infinite_gain and not infinite_bandwidth:
        Gbw = var('Gbw')
        opamp_gain = Gbw / s
    else:
        if infinite_bandwidth:
            opamp_gain = Aol
        else:
            Tau = var('Tau', latex_name=r'\tau')
            opamp_gain = Aol / (1 + Tau * s)
    
    for opamp in topology['op']:
        out_idx = opamp["output"]
        low_impedance_nodes.add(out_idx)
        equations.append(node_symbols[out_idx] == (node_symbols[opamp["+"]] - node_symbols[opamp["-"]])
                          * opamp_gain)
        targets.append(node_symbols[out_idx])

    for node in node_set - low_impedance_nodes:
        node_var = node_symbols[node]
        node_eq = 0
        for designator in ['r','l','c']:
            for i,component in enumerate(topology[designator]):
                if node in component:
                    other_node = component[0] if node == component[1] else component[1]
                    term = node_var - node_symbols[other_node]
                    part = comp_symbols[designator][i]
                    if designator == 'c':
                        node_eq += s * part * term
                    elif designator == 'r':
                        node_eq += term / part
                    elif designator == 'l':
                        node_eq += term / (s * part)
        equations.append(0==node_eq)
        targets.append(node_var)

    solution = solve(equations,targets)[0][0].rhs()
    if infinite_gain:
        solution = limit(solution, Aol=oo)

    pretty_print(solution)
    h_Y = solution.numerator().collect(s).coefficients(s)
    h_X = solution.denominator().collect(s).coefficients(s)
    return {i[1]:str(i[0].simplify()) for i in h_X},{i[1]:str(i[0].simplify()) for i in h_Y}
