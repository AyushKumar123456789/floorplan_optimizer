# app/utilities.py

import random
import csv
import os

from .models import Block, Floorplan

def generate_sample_blocks(num_blocks, layers):
    blocks = []
    for i in range(num_blocks):
        width = random.randint(5, 15)
        height = random.randint(5, 15)
        block = Block(id=i, width=width, height=height)
        blocks.append(block)
    return blocks

def generate_sample_connectivity(num_blocks, connections_per_block=3):
    connectivity = []
    for i in range(num_blocks):
        connected = set()
        while len(connected) < connections_per_block:
            j = random.randint(0, num_blocks-1)
            if i != j and j not in connected:
                connectivity.append((i, j))
                connected.add(j)
    return connectivity

def log_metrics(benchmark_type, benchmark_file, initial_floorplan, optimized_floorplan,
                initial_energy, optimized_energy, initial_temp, optimized_temp,
                execution_time, connectivity):
    # Define the CSV file and headers
    csv_file = 'experimental_results.csv'
    headers = ['Benchmark Type', 'Benchmark File', 'Initial Area', 'Optimized Area',
               'Area Reduction (%)', 'Initial Interconnect Length', 'Optimized Interconnect Length',
               'Interconnect Reduction (%)', 'Initial Power Consumption', 'Optimized Power Consumption',
               'Power Reduction (%)', 'Initial Max Temperature', 'Optimized Max Temperature',
               'Temp Reduction (°C)', 'Execution Time (s)', 'Initial Block Placements']

    # Calculate areas and interconnect lengths
    initial_area = initial_floorplan.calculate_total_area()
    optimized_area = optimized_floorplan.calculate_total_area()
    initial_interconnect = initial_floorplan.calculate_interconnect_length(connectivity)
    optimized_interconnect = optimized_floorplan.calculate_interconnect_length(connectivity)
    initial_power = initial_interconnect * 1.0  # alpha = 1.0
    optimized_power = optimized_interconnect * 1.0  # alpha = 1.0

    # Calculate reductions
    area_reduction = ((initial_area - optimized_area) / initial_area) * 100 if initial_area !=0 else 0
    interconnect_reduction = ((initial_interconnect - optimized_interconnect) / initial_interconnect) * 100 if initial_interconnect !=0 else 0
    power_reduction = ((initial_power - optimized_power) / initial_power) * 100 if initial_power !=0 else 0
    temp_reduction = initial_temp - optimized_temp

    # Get initial block placements
    initial_placements = "; ".join([f"Block {b.id}: (x={b.x}, y={b.y}, layer={b.layer})" for b in initial_floorplan.blocks])

    # Prepare data row
    data_row = [
        benchmark_type,
        benchmark_file,
        initial_area,
        optimized_area,
        round(area_reduction, 2),
        initial_interconnect,
        optimized_interconnect,
        round(interconnect_reduction, 2),
        initial_power,
        optimized_power,
        round(power_reduction, 2),
        initial_temp,
        optimized_temp,
        temp_reduction,
        round(execution_time, 2),
        initial_placements
    ]

    # Write to CSV
    file_exists = os.path.isfile(csv_file)
    try:
        with open(csv_file, 'a', newline='') as file:
            writer = csv.writer(file)
            # Write header if file does not exist
            if not file_exists:
                writer.writerow(headers)
            writer.writerow(data_row)
        print(f"Metrics logged to {csv_file}")
    except Exception as e:
        print(f"Error logging metrics: {e}")
