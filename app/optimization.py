# app/optimization.py

import copy
import math
import random
from .models import Floorplan

def calculate_energy(floorplan, connectivity):
    alpha = 1.0  # Weight for area
    beta = 1.0   # Weight for interconnect length
    area = floorplan.calculate_total_area()
    interconnect = floorplan.calculate_interconnect_length(connectivity)
    energy = alpha * area + beta * interconnect
    return energy

def simulated_annealing(floorplan, connectivity, initial_temp=1000, cooling_rate=0.003,
                        min_temp=1, max_iterations=10000):
    current_floorplan = copy.deepcopy(floorplan)
    best_floorplan = copy.deepcopy(current_floorplan)
    current_energy = calculate_energy(current_floorplan, connectivity)
    best_energy = current_energy

    temp = initial_temp
    iteration = 0

    while temp > min_temp and iteration < max_iterations:
        # Create a new candidate floorplan by moving a random block
        candidate_floorplan = copy.deepcopy(current_floorplan)
        # Select a random layer
        layer = random.choice(list(candidate_floorplan.layer_blocks.keys()))
        if not candidate_floorplan.layer_blocks[layer]:
            iteration +=1
            temp *= (1 - cooling_rate)
            continue
        block = random.choice(candidate_floorplan.layer_blocks[layer])
        # Save old position
        old_x, old_y = block.x, block.y
        # Propose a new random position within the layer without overlapping
        attempts = 0
        max_attempts = 100
        placed = False
        while not placed and attempts < max_attempts:
            new_x = random.randint(0, candidate_floorplan.floorplan_size - block.width)
            new_y = random.randint(0, candidate_floorplan.floorplan_size - block.height)
            block.x = new_x
            block.y = new_y
            if not candidate_floorplan.is_overlapping(block, candidate_floorplan.layer_blocks[layer]):
                placed = True
            else:
                block.x, block.y = old_x, old_y  # Revert if overlapping
            attempts +=1
        if not placed:
            # Unable to place without overlapping; skip this move
            block.x, block.y = old_x, old_y
            iteration +=1
            temp *= (1 - cooling_rate)
            continue
        # Calculate new energy
        candidate_energy = calculate_energy(candidate_floorplan, connectivity)
        delta_energy = candidate_energy - current_energy
        # Decide whether to accept the new state
        if delta_energy < 0 or random.uniform(0,1) < math.exp(-delta_energy / temp):
            current_floorplan = candidate_floorplan
            current_energy = candidate_energy
            # Update best floorplan
            if current_energy < best_energy:
                best_floorplan = copy.deepcopy(current_floorplan)
                best_energy = current_energy
        # Cool down
        temp *= (1 - cooling_rate)
        iteration += 1
        if iteration % 1000 == 0:
            print(f"Iteration {iteration}, Temperature {temp:.2f}, Best Energy {best_energy:.2f}")
    print("Optimization completed.")
    return best_floorplan
