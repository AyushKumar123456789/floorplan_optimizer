# app/models.py

import random
import matplotlib.pyplot as plt

class Block:
    def __init__(self, id, width, height, layer=0):
        self.id = id
        self.width = width
        self.height = height
        self.layer = layer
        self.x = 0
        self.y = 0

    def __repr__(self):
        return f"Block(id={self.id}, layer={self.layer}, x={self.x}, y={self.y})"

class Floorplan:
    def __init__(self, blocks, layers, floorplan_size=100):
        self.blocks = blocks  # List of Block objects
        self.layers = layers  # Number of layers
        self.floorplan_size = floorplan_size  # Size of the floorplan (e.g., 100x100)
        self.layer_blocks = {layer: [] for layer in range(layers)}
        self.assign_blocks_to_layers()

    def is_overlapping(self, block, layer_blocks):
        for other in layer_blocks:
            if other.id == block.id:
                continue
            if (block.x < other.x + other.width and
                block.x + block.width > other.x and
                block.y < other.y + other.height and
                block.y + block.height > other.y):
                return True
        return False

    def assign_blocks_to_layers(self):
        # Simple heuristic: distribute blocks evenly across layers
        for i, block in enumerate(self.blocks):
            layer = i % self.layers
            block.layer = layer
            placed = False
            attempts = 0
            max_attempts = 1000
            while not placed and attempts < max_attempts:
                block.x = random.randint(0, self.floorplan_size - block.width)
                block.y = random.randint(0, self.floorplan_size - block.height)
                if not self.is_overlapping(block, self.layer_blocks[layer]):
                    self.layer_blocks[layer].append(block)
                    placed = True
                attempts += 1
            if not placed:
                raise Exception(f"Unable to place Block {block.id} without overlapping after {max_attempts} attempts.")

    def calculate_total_area(self):
        total_area = 0
        for layer in self.layer_blocks:
            if not self.layer_blocks[layer]:
                continue
            max_x = max(block.x + block.width for block in self.layer_blocks[layer])
            max_y = max(block.y + block.height for block in self.layer_blocks[layer])
            layer_area = max_x * max_y
            total_area += layer_area
        return total_area

    def calculate_interconnect_length(self, connectivity):
        total_length = 0
        for (b1, b2) in connectivity:
            block1 = next((b for b in self.blocks if b.id == b1), None)
            block2 = next((b for b in self.blocks if b.id == b2), None)
            if block1 and block2:
                # Calculate Manhattan distance, considering layer difference
                dx = abs(block1.x - block2.x)
                dy = abs(block1.y - block2.y)
                dz = abs(block1.layer - block2.layer) * 10  # Assume vertical distance as 10 units per layer
                total_length += dx + dy + dz
        return total_length

    def visualize_floorplan(self, save_path=None, title_suffix=""):
        colors = ['red', 'green', 'blue', 'yellow', 'cyan', 'magenta', 'orange', 'purple']
        for layer in self.layer_blocks:
            plt.figure(figsize=(6,6))
            plt.title(f"Layer {layer} {title_suffix}")
            for block in self.layer_blocks[layer]:
                rect = plt.Rectangle((block.x, block.y), block.width, block.height,
                                     edgecolor='black', facecolor=random.choice(colors), alpha=0.5)
                plt.gca().add_patch(rect)
                plt.text(block.x + block.width/2, block.y + block.height/2,
                         str(block.id), ha='center', va='center')
            plt.xlim(0, self.floorplan_size)
            plt.ylim(0, self.floorplan_size)
            plt.xlabel('X')
            plt.ylabel('Y')
            plt.grid(True)
            if save_path:
                plt.savefig(save_path)
                plt.close()
            else:
                plt.show()
