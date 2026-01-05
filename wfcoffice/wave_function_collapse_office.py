# Randall Simonson jan 2025
"""
Usage is exampled in the __main__ block at the bottom. This module defines a wave function collapse algorithm
to generate a procedural office layout on an n x n grid. The office consists of walls, corners, desks, and carpet tiles,
with adjacency rules defined in neighbor_dict_example. The generate_office(n) method initializes the grid, applies the WFC algorithm,
and returns the final layout.

V2 additions: generate_combined_image() method to stitch tile images into a final composite image.
"""
#from random import random
import random
from PIL import Image
import os

class wave_function_collapse_office:
    def __init__(self, neighbor_dict):
        # Define adjacency rules (tile -> allowed neighbors on N,E,S,W)
        self.neighbor_dict_example = {
            "CornerTL": {"N":[],   "E":["WallTop"],    "S":["WallLeft"],   "W":[]},
            "CornerTR": {"N":[],   "E":[],           "S":["WallRight"],  "W":["WallTop"]},
            "CornerBL": {"N":["WallLeft"], "E":["WallBottom"], "S":[], "W":[]},
            "CornerBR": {"N":["WallRight"],"E":[],           "S":[],           "W":["WallBottom"]},
            "WallTop":  {"N":[],   "E":["WallTop","CornerTR"], "S":["Desk","Carpet"], "W":["WallTop","CornerTL"]},
            "WallBottom":{"N":["Desk","Carpet"], "E":["WallBottom","CornerBR"], "S":[],   "W":["WallBottom","CornerBL"]},
            "WallLeft": {"N":["WallLeft","CornerTL"],  "E":["Desk","Carpet"], "S":["WallLeft","CornerBL"], "W":[]},
            "WallRight":{"N":["WallRight","CornerTR"], "E":[],           "S":["WallRight","CornerBR"], "W":["Desk","Carpet"]},
            "Desk":     {"N":["Desk","Carpet","WallTop"], "E":["Desk","Carpet","WallRight"],
                        "S":["Desk","Carpet","WallBottom"], "W":["Desk","Carpet","WallLeft"]},
            "Carpet":   {"N":["Desk","Carpet","WallTop"], "E":["Desk","Carpet","WallRight"],
                        "S":["Desk","Carpet","WallBottom"], "W":["Desk","Carpet","WallLeft"]}
        }
        # default to my example if none provided
        self.neighbor_dict = neighbor_dict if neighbor_dict else self.neighbor_dict_example
        self.layout = None

    def generate_office(self,n):
        # Initialize domains
        domains = [[None]*n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                # Corners
                if   (i,j)==(0,0): domains[i][j] = ["CornerTL"]
                elif (i,j)==(0,n-1): domains[i][j] = ["CornerTR"]
                elif (i,j)==(n-1,0): domains[i][j] = ["CornerBL"]
                elif (i,j)==(n-1,n-1): domains[i][j] = ["CornerBR"]
                # Edges (non-corner)
                elif i==0:      domains[i][j] = ["WallTop"]
                elif i==n-1:    domains[i][j] = ["WallBottom"]
                elif j==0:      domains[i][j] = ["WallLeft"]
                elif j==n-1:    domains[i][j] = ["WallRight"]
                # Interior
                else:           domains[i][j] = ["Desk","Carpet"]
        # Helper to propagate after collapsing a cell
        def propagate(i,j):
            stack = [(i,j)]
            while stack:
                ci, cj = stack.pop()
                tile = domains[ci][cj][0]  # single collapsed tile
                # For each neighbor, filter its domain
                for di,dj,side in [(-1,0,'N'), (0,1,'E'), (1,0,'S'), (0,-1,'W')]:
                    ni,nj = ci+di, cj+dj
                    if 0 <= ni < n and 0 <= nj < n:
                        opp = {'N':'S','S':'N','E':'W','W':'E'}[side]
                        allowed = self.neighbor_dict[tile][side]
                        new_dom = [t for t in domains[ni][nj] if t in self.neighbor_dict and tile in self.neighbor_dict[t][opp]]
                        # (Above ensures consistency of adjacency.)
                        if not new_dom:
                            raise Exception(f"No valid tile for neighbor at {(ni,nj)}")
                        if set(new_dom) != set(domains[ni][nj]):
                            domains[ni][nj] = new_dom
                            if len(new_dom)==1:
                                stack.append((ni,nj))
        # WFC collapse loop
        while True:
            # Find cell with smallest domain >1
            min_size = float('inf'); cell = None
            for i in range(n):
                for j in range(n):
                    if 1 < len(domains[i][j]) < min_size:
                        min_size = len(domains[i][j]); cell = (i,j)
            if not cell:
                break  # all cells collapsed
            i,j = cell
            choice = random.choice(domains[i][j])       # collapse to one
            domains[i][j] = [choice]
            propagate(i,j)
        self.layout = domains
        return self.layout

    def generate_combined_image(self, tile_to_image_dict, image_folder_path, output_path=None):
        """
        Stitches together individual tile images into a complete office layout image.

        Parameters:
        -----------
        tile_to_image_dict : dict
            Dictionary mapping tile names (e.g., "CornerTL", "Desk") to image filenames (e.g., "corner_tl.png")
        image_folder_path : str
            Path to the folder containing the tile images
        output_path : str, optional
            Path to save the combined image. If None, returns the image object without saving.

        Returns:
        --------
        PIL.Image
            The combined image with all tiles stitched together

        Raises:
        -------
        ValueError
            If layout has not been generated yet (call generate_office first)
        FileNotFoundError
            If a required tile image file is not found
        """
        if self.layout is None:
            raise ValueError("No layout generated yet. Call generate_office(n) first.")

        n = len(self.layout)  # Grid size

        # Load a sample tile to get dimensions
        first_tile_name = self.layout[0][0][0]
        if first_tile_name not in tile_to_image_dict:
            raise ValueError(f"Tile '{first_tile_name}' not found in tile_to_image_dict")

        sample_tile_path = os.path.join(image_folder_path, tile_to_image_dict[first_tile_name])
        if not os.path.exists(sample_tile_path):
            raise FileNotFoundError(f"Tile image not found: {sample_tile_path}")

        sample_tile = Image.open(sample_tile_path)
        tile_width, tile_height = sample_tile.size
        sample_tile.close()

        # Create the combined image
        combined_width = n * tile_width
        combined_height = n * tile_height
        combined_image = Image.new('RGBA', (combined_width, combined_height))

        # Stitch tiles together
        for i in range(n):
            for j in range(n):
                # Get the tile name (it's stored as a single-element list)
                tile_name = self.layout[i][j][0]

                # Get the corresponding image filename
                if tile_name not in tile_to_image_dict:
                    raise ValueError(f"Tile '{tile_name}' not found in tile_to_image_dict")

                image_filename = tile_to_image_dict[tile_name]
                tile_image_path = os.path.join(image_folder_path, image_filename)

                # Check if file exists
                if not os.path.exists(tile_image_path):
                    raise FileNotFoundError(f"Tile image not found: {tile_image_path}")

                # Load the tile image
                tile_image = Image.open(tile_image_path)

                # Ensure tile is the expected size
                if tile_image.size != (tile_width, tile_height):
                    tile_image = tile_image.resize((tile_width, tile_height), Image.LANCZOS)

                # Calculate position in the combined image
                x = j * tile_width
                y = i * tile_height

                # Paste the tile
                combined_image.paste(tile_image, (x, y))
                tile_image.close()

        # Save if output path provided
        if output_path:
            # if the file already exists, add a number to the filename:
            if os.path.exists(output_path):
                base, ext = os.path.splitext(output_path)
                count = 1
                while os.path.exists(f"{base}_{count}{ext}"):
                    count += 1
                output_path = f"{base}_{count}{ext}"
            combined_image.save(output_path)
            print(f"Combined image saved to: {output_path}")

        return combined_image


if __name__ == "__main__":
    # Example usage
    wfc_office = wave_function_collapse_office(None)
    wfc_office.generate_office(10)

    # Print the layout
    layout = wfc_office.layout
    print("Generated Layout:")
    for row in layout:
        print(row)

    # Example tile-to-image mapping
    # (You would replace these with your actual image filenames)
    tile_images = {
        "CornerTL": "corner_tl.png",
        "CornerTR": "corner_tr.png",
        "CornerBL": "corner_bl.png",
        "CornerBR": "corner_br.png",
        "WallTop": "wall_top.png",
        "WallBottom": "wall_bottom.png",
        "WallLeft": "wall_left.png",
        "WallRight": "wall_right.png",
        "Desk": "desk.png",
        "Carpet": "carpet.png"
    }

    #Generate combined image examnpole
    combined_img = wfc_office.generate_combined_image(
        tile_to_image_dict=tile_images,
        image_folder_path="./exampe_imgs/office",
        output_path="outputs/office_layout.png"
    )
