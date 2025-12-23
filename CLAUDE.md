# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CROMD (Cobertura de Sensores com Drones) is a solver for the **Drone-based Sensor Coverage Routing Problem with Makespan Optimization**. The problem involves routing multiple drones from a depot to cover sensors while minimizing the maximum tour length (makespan).

## Key Components

### Instance Reader (`notebooks/instance_reader.py`)

Reads problem instances and supports three distance metrics:
- **Euclidean** (default): For planar coordinates
- **Haversine**: For GPS coordinates (lat/lon), returns distances in **meters**
- **Manhattan**: Grid-based distance

**Critical**: The reader returns:
- `V`: List `[0, 1, 2, ..., n-1]` where 0 is the depot/base
- `d`: Flat dictionary `{(i,j): distance}` (NOT nested `d[i][j]`)
- `Viz`: List where `Viz[i]` contains neighbors within sensor i's coverage radius
- Coverage uses **strict inequality** `d(i,j) < radius`, not `<=`

### CPLEX Solver (`notebooks/solve_run.ipynb`)

Implements Integer Linear Programming formulation with branch-and-cut:

**Mathematical Notation Mapping**:
- Text formulation uses: `V` = sensors (without depot), `V' = V ∪ {0}` (all nodes)
- Instance reader returns: `V = [0, 1, ..., n-1]` (already includes depot)
- Code must map: `V_math = V_input \ {0}`, `V'_math = V_input`

**Model Structure**:
1. **Base model** (`build_CROMD_cplex`): Contains ONLY the 6 core constraints from the mathematical formulation:
   - Coverage constraints
   - Flow coherence (in/out degree = visit variable)
   - Autonomy limits
   - Makespan bounds
   - Symmetry breaking

2. **Cut-set separation** (`CROMDCallback`): Dynamically adds connectivity constraints via branch-and-cut
   - Constructs auxiliary graph with capacities from current solution
   - Computes minimum cuts between depot and active nodes
   - Adds violated cut-set inequalities: `∑_{i∈S} ∑_{j∉S} x̄_{ij} ≥ 2`

**IMPORTANT**: Do NOT add connectivity constraints directly to the base model. Subtour elimination is handled exclusively through dynamic separation in the callback.

### Distance Data Structure

Instance files use GPS coordinates:
- Format: `longitude latitude radius` (note: longitude first, NOT lat/lon)
- Haversine distance configured to return **meters** via `Unit.METERS`
- Coverage radius values in instance files are in meters (e.g., 200m)

## Running Tests and Notebooks

```bash
# Test distance calculations
python3 test_distances.py

# Run notebooks
jupyter notebook notebooks/solve_run.ipynb
```

## Instance File Format

```
n                    # Total number of sensors (including depot)
lon0 lat0 radius0    # Depot (sensor 0)
lon1 lat1 radius1    # Sensor 1
...
```

Instances are in `data/instances/` with naming pattern:
- `instancia{N}{Region}[_factor].csv`
- Example: `instancia1Tijuca_0.7.csv`

## Dependencies

- Python 3.9+
- `cplex`: IBM CPLEX Optimization Studio
- `networkx`: For minimum cut computation in callback
- `haversine`: For GPS distance calculations
- `matplotlib`: For route visualization
