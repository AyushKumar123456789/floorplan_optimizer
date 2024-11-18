# app/routes.py

from flask import Blueprint, request, jsonify, render_template, send_file
from .models import Floorplan
from .optimization import simulated_annealing, calculate_energy
from .utilities import generate_sample_blocks, generate_sample_connectivity, log_metrics
import time
import os
import csv  # Ensure csv is imported

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/optimize', methods=['POST'])
def optimize_floorplan():
    data = request.json
    num_blocks = data.get('num_blocks', 20)
    layers = data.get('layers', 3)
    connections_per_block = data.get('connections_per_block', 3)
    floorplan_size = data.get('floorplan_size', 100)

    # Generate blocks and connectivity
    blocks = generate_sample_blocks(num_blocks, layers)
    connectivity = generate_sample_connectivity(num_blocks, connections_per_block)

    # Initialize floorplan
    try:
        floorplan = Floorplan(blocks, layers, floorplan_size)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

    # Calculate initial energy
    initial_energy = calculate_energy(floorplan, connectivity)

    # Start timing
    start_time = time.time()

    # Optimize floorplan
    optimized_floorplan = simulated_annealing(floorplan, connectivity)

    # Calculate optimized energy
    optimized_energy = calculate_energy(optimized_floorplan, connectivity)

    # End timing
    end_time = time.time()
    execution_time = end_time - start_time

    # Evaluate thermal profiles (simplified)
    initial_temp = max(len(floorplan.layer_blocks[layer]) for layer in floorplan.layer_blocks) * 10
    optimized_temp = max(len(optimized_floorplan.layer_blocks[layer]) for layer in optimized_floorplan.layer_blocks) * 10

    # Log metrics
    log_metrics(
        benchmark_type='Sample',
        benchmark_file='N/A',
        initial_floorplan=floorplan,
        optimized_floorplan=optimized_floorplan,
        initial_energy=initial_energy,
        optimized_energy=optimized_energy,
        initial_temp=initial_temp,
        optimized_temp=optimized_temp,
        execution_time=execution_time,
        connectivity=connectivity
    )

    # Visualize and save floorplans
    images_dir = os.path.join(main.root_path, 'static', 'images')
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
    initial_image_paths = []
    optimized_image_paths = []
    for layer in floorplan.layer_blocks:
        initial_filename = f'initial_layer_{layer}.png'
        optimized_filename = f'optimized_layer_{layer}.png'
        initial_path = os.path.join(images_dir, initial_filename)
        optimized_path = os.path.join(images_dir, optimized_filename)
        floorplan.visualize_floorplan(save_path=initial_path, title_suffix="(Initial)")
        optimized_floorplan.visualize_floorplan(save_path=optimized_path, title_suffix="(Optimized)")
        initial_image_paths.append(os.path.join('static', 'images', initial_filename))
        optimized_image_paths.append(os.path.join('static', 'images', optimized_filename))

    # Read existing CSV and return its content
    csv_file = 'experimental_results.csv'
    csv_data = []
    if os.path.isfile(csv_file):
        with open(csv_file, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                csv_data.append(row)

    response = {
        'status': 'success',
        'initial_energy': initial_energy,
        'optimized_energy': optimized_energy,
        'area_reduction': round(((floorplan.calculate_total_area() - optimized_floorplan.calculate_total_area()) / floorplan.calculate_total_area()) * 100, 2),
        'interconnect_reduction': round(((floorplan.calculate_interconnect_length(connectivity) - optimized_floorplan.calculate_interconnect_length(connectivity)) / floorplan.calculate_interconnect_length(connectivity)) * 100, 2),
        'power_reduction': round(((floorplan.calculate_interconnect_length(connectivity) - optimized_floorplan.calculate_interconnect_length(connectivity)) / floorplan.calculate_interconnect_length(connectivity)) * 100, 2),
        'initial_temp': initial_temp,
        'optimized_temp': optimized_temp,
        'execution_time': round(execution_time, 2),
        'initial_images': [path.replace('\\', '/') for path in initial_image_paths],
        'optimized_images': [path.replace('\\', '/') for path in optimized_image_paths],
        'download_csv': '/download_csv',
        'csv_data': csv_data
    }

    return jsonify(response)

@main.route('/download_csv')
def download_csv():
    csv_path = os.path.join(main.root_path, '..', 'experimental_results.csv')
    if os.path.exists(csv_path):
        return send_file(csv_path, as_attachment=True)
    else:
        return "CSV file not found.", 404
