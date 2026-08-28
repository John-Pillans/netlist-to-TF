# netlist-to-TF
Python scripts to produce the exact symbolic transfer function from a circuit netlist. Automates the production of equations using Kirchhoff's current law and then solves for the transfer function. The data structures are used to isolate symbolic processing to within this step only for hand off to numeric evaluation, this is faster for repeated evaluation of different component values rather than solving the simultaneous equations each time.

### Parameters
**topology : dict**

A netlist representation of the circuit topology. Component variable names $r_1$ $r_2$ etc are automatically allocated by order of appearance in the component lists. Lists may be empty if there are no components of that type but all four component keys must be present in the dictionary.
```python
{
    'op': [  # List of opamp configurations
        {
            'output': int,   # Output node number
            '+': int,         # Non-inverting input node
            '-': int          # Inverting input node
        },
        ...
    ],
    'r': [   # List of resistor connections
        (node1, node2),
        ...
    ],
    'c': [   # List of capacitor connections
        (node1, node2),
        ...
    ],
    'l': [   # List of inductor connections
        (node1, node2),
        ...
    ]
}
```

Three nodes are defined by default
- '0' 0V
- '1' Input Voltage ($V_{in}$)
- '2' Output Voltage ($V_{out}$)

Additional nodes can be added as required.

**infinite_gain : bool, default: True**

Removes opamp open loop gain from the model.

**infinite_bandwidth : bool, default: True**

Removes opamp gain bandwidth from the model.

### Returns
**denominator,numerator : dict**

Polynomials sparsely represented as a dictionary 
`{exponent: coefficient_string, ... }`

## Examples
### LC high pass filter
Series capacitor between the input and output nodes with a parallel capacitor on the output.
```python
{'r':[], 'l':[[0,2]], 'c':[[1,2]], 'op':[]}
```
Produces the expected 2nd order response:

<img width="84" alt="LC" src="https://github.com/user-attachments/assets/d08a3743-224d-4a8b-a70c-ed9f411fcb41" />

With the sparse polynomial representation:

```python
({0: '1', 2: 'c1*l1'}, {2: 'c1*l1'})
```
### Voltage Follower
As the simplest operational amplifier circuit a voltage follower highlights the optional non ideal opamp models available. One resistor is used as a wire to connect the negative feedback around the amplifier, producing the netlist representation:
```python
{'r':[[2,3]], 'l':[], 'c':[], 'op':[{'+': 1, '-': 3, 'output': 2}]}
```
The value of the resistor is irrelevant and disappears from the resulting transfer functions. The KCL analysis has no current in or out of the opamp input pins and so the voltage across the resistor is always zero. The resistor can be left out as in later examples. Four different outputs are possible depending on the boolean `infinite_gain` and `infinite_bandwidth` parameters.
|      | Infinite Gain | Finite Gain |
| :--- |     :---:     |    :---:    |
| **Infinite Bandwidth**  | 1     | <img width="72" alt="followerIbw" src="https://github.com/user-attachments/assets/1fba0e65-f272-4e43-a15b-598e139ddd23" /> |
| **Finite Bandwidth**    | <img width="73" alt="followerIgain" src="https://github.com/user-attachments/assets/f93768ad-7530-4e88-94d1-08fd53892d20" /> | <img width="112" alt="follower" src="https://github.com/user-attachments/assets/87c76013-0777-4e96-bd79-6dac0335a255" /> |

Both gain bandwidth ($G_{BW}$) and open loop gain ($A_{OL}$) variables are available if required. Tau ($T$) is used in the complete model to simplify the resulting equations, it is related to the gain bandwidth by the following equation:

<img width="132" alt="tau" src="https://github.com/user-attachments/assets/4bf75f28-976e-45a1-875d-6150af041070" />


### 6th order Sallen-Key low pass filter
A worked example of producing the netlist representation from a schematic diagram uses the following circuit:

<img width="886" alt="Circuit" src="https://github.com/user-attachments/assets/1fb2da66-0c19-4350-a278-150927dc20a5" />

- Connections to the default nodes of 0V (node 0) signal input (node 1) and signal output (node 2) are labelled, followed by any other nodes in the circuit.
- Each component is added to the list matching their type (r, l, or c) as a tuple or list of the two nodes the component joins, insensitive to order/direction.
- Operational amplifiers are added to their list as a dict with the 3 pin names as keys.

This produces the following netlist topology representation for input to the function:

```python
{'r':[[1,3], [3,4], [5,6], [6,7]], 'l':[[8,2]], 'c':[[0,4], [3,5], [0,7], [7,8], [0,2]], 'op':[{'+': 4, '-': 5, 'output': 5},{'+': 7, '-': 8, 'output': 8}]}
```

For the default ideal infinite gain and bandwidth opamps this results in a large and complex transfer function equation of 6th order as expected, the output as symbolic factors is:

```python
[{0: '1', 1: 'c1*r1 + c1*r2 + c3*r3 + c3*r4', 2: 'c1*c2*r1*r2 + c1*c3*r1*r3 + c1*c3*r1*r4 + c1*c3*r2*r3 + c1*c3*r2*r4 + c3*c4*r3*r4 + c5*l1', 3: 'c1*c2*c3*r1*r2*r3 + c1*c2*c3*r1*r2*r4 + c1*c3*c4*r1*r3*r4 + c1*c3*c4*r2*r3*r4 + c1*c5*l1*r1 + c1*c5*l1*r2 + c3*c5*l1*r3 + c3*c5*l1*r4', 4: 'c1*c2*c3*c4*r1*r2*r3*r4 + c1*c2*c5*l1*r1*r2 + c1*c3*c5*l1*r1*r3 + c1*c3*c5*l1*r1*r4 + c1*c3*c5*l1*r2*r3 + c1*c3*c5*l1*r2*r4 + c3*c4*c5*l1*r3*r4', 5: 'c1*c3*c5*l1*(c2*r1*r2*r3 + c2*r1*r2*r4 + c4*r1*r3*r4 + c4*r2*r3*r4)', 6: 'c1*c2*c3*c4*c5*l1*r1*r2*r3*r4'}, {0: '1'}]
```
## Environment
Both Sagemath and SymPy versions are provided. Sagemath computes faster and can solve more complex topologies, while SymPy is much easier to install/deploy.
