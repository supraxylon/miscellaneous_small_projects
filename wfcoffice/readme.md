Goal:
Create a Python program which uses the wave function collapse algorithm to generate a top-down view of an office space in the style of started valley.

Questions:
What kind of tiles or visual elements should the office space include (e.g., desks, chairs, walls, plants, etc.)?

Do you already have tile images or should the program generate a grid using placeholder graphics/colors?

Should the output be a visual image, a grid of symbols, or something else?

What size or dimensions should the office layout be (e.g., 10x10, 20x20)?

Answers:
1. As many as you can make. The edges should all be the four exterior walls of the building 2. I don't have the tile images yet; but let's start by using your image generator to make them. The first few should be the corners of the building which will be the same tile just rotated four times and the walls which will get that same treatment for a total of 8 tiles and then let's have a desk aswell and an empty carpet tile. 3. The output should be a n by n 2D grid which contains which tile is in which position. This could be a list of lists or a dataframe or anything else that makes sense, we should also have a module which assembles the images into that grid and returns that final large image. 4. It should be variable however; we can say the range will be between 5x5 to 50x50

Pseudocode:
# Example WFC loop (pseudo-code)
# Assume domains[i][j] = list of possible tile-types for cell (i,j).
while there exists a cell with domain size > 1:
    # Pick cell with minimal options (lowest entropy)
    (i,j) = cell_with_min_domain(domains)
    # Randomly collapse it to one allowed tile
    chosen = random.choice(domains[i][j])
    domains[i][j] = [chosen]
    # Propagate constraints to neighbors
    propagate_constraints(domains, (i,j))
