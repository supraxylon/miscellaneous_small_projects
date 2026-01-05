# Randall Simonson jan 2025
"""
Usage is exampled in the __main__ block at the bottom. This module defines a wave function collapse algorithm
to generate a procedural office layout on an n x n grid. The office consists of walls, corners, desks, and carpet tiles,
with adjacency rules defined in neighbor_dict_example. The generate_office(n) method initializes the grid, applies the WFC algorithm,
and returns the final layout.
"""
#from random import random
import random

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
    

if __name__ == "__main__":
    wfc_office = wave_function_collapse_office(None)
    wfc_office.generate_office(10)
    # Example usage: generate a 10×10 layout
    layout = wfc_office.layout
    for row in layout:
        print(row)
