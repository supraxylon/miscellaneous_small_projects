# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains a Python implementation project for generating office space layouts using the Wave Function Collapse (WFC) algorithm, styled after Stardew Valley. The project leverages an existing C# implementation of WFC as a reference (in the `WaveFunctionCollapse/` subdirectory).

**Project Goal**: Create a Python program that generates top-down office space views using WFC with Stardew Valley-style tile graphics, supporting variable grid sizes from 5x5 to 50x50.

## Project Requirements

From `readme.md`:
- Tile types: corners (4 rotations), walls (4 rotations), desk, empty carpet tile (total of 10 tiles initially)
- Edges must be exterior walls of the building
- Output: n×n 2D grid structure (list of lists, DataFrame, etc.) indicating tile positions
- Image assembly module: combines individual tile images into final large composite image
- Grid size: variable between 5×5 and 50×50
- Tile images: to be generated initially, not yet available

## Architecture of Reference Implementation (C#)

The WaveFunctionCollapse C# implementation provides two core models:

### Model Hierarchy
- **`Model.cs`**: Abstract base class implementing the core WFC algorithm
  - Maintains `wave` state (superposition of possible patterns)
  - Implements observation-propagation cycle (lines 73-97)
  - Supports three heuristics: Entropy, MRV (Minimum Remaining Values), Scanline (line 26)
  - Uses AC-4 constraint propagation algorithm (lines 143-180)

- **`OverlappingModel.cs`**: Learns patterns from sample bitmaps
  - Extracts NxN pixel patterns from input images (typically N=2 or N=3)
  - Uses pattern frequency as weights for probabilistic collapse
  - Generates outputs locally similar to input sample

- **`SimpleTiledModel.cs`**: Works with pre-defined tiles and adjacency rules
  - Loads tiles from XML definitions with symmetry specifications
  - Symmetry types: L, T, I, \, F, X (lines 54-89)
  - Adjacency constraints defined in XML `<neighbors>` elements
  - Supports tile rotation and reflection

### Key Algorithm Steps
1. **Pattern extraction**: Read input (bitmap or tileset) and count valid patterns
2. **Wave initialization**: All positions start in superposition of all valid patterns
3. **Observation loop**:
   - Find lowest entropy position (NextUnobservedNode, lines 99-133 in Model.cs)
   - Collapse to single pattern based on weighted probability
4. **Propagation**: Ban conflicting patterns in adjacent cells using constraint propagation
5. **Contradiction handling**: Algorithm may fail if all patterns become forbidden (retry with different seed)

### Configuration
- **`samples.xml`**: Defines generation parameters for all examples
  - Overlapping model params: `name`, `N` (pattern size), `periodic`, `symmetry`, `ground`
  - Tiled model params: `name`, `subset`, `size`/`width`/`height`, `periodic`
- **`tilesets/*.xml`**: Tile definitions with symmetry and adjacency rules
- **`samples/*.png`**: Input images for overlapping model

## Common Development Commands

### C# Reference Implementation
```bash
# Build and run (generates outputs for all samples in samples.xml)
cd WaveFunctionCollapse
dotnet run --configuration Release WaveFunctionCollapse.csproj

# Output saved to: WaveFunctionCollapse/output/
```

### Future Python Implementation
When implementing the Python version:
- Entry point should accept grid size parameter (5-50)
- Separate module for image assembly from tile grid
- Output grid structure representing tile positions
- Use the SimpleTiledModel approach (predefined tiles with adjacency rules) rather than OverlappingModel

## Implementation Notes

### For Office Layout Generation
- Use SimpleTiledModel approach: define office tiles (corners, walls, desks, carpet) with adjacency constraints
- Enforce exterior walls at boundaries (see `ground` parameter usage in Model.cs line 217-225)
- Tile symmetry system (SimpleTiledModel.cs lines 54-89) reduces manual adjacency enumeration
- Consider using Entropy or MRV heuristic for better visual results (avoid Scanline for this use case)

### Tile Design Considerations
- Corner tiles: same image rotated 4 times
- Wall tiles: same image rotated 4 times
- Desk and carpet tiles may have different symmetries
- Each tile needs adjacency rules defining which tiles can be neighbors in each direction

### Avoiding Common Pitfalls
- The algorithm can fail (contradiction) if constraints are too restrictive
- Include retry logic with different random seeds (see Program.cs lines 51-65)
- Periodic boundaries may not be appropriate for bounded office space
- Ensure all tiles have valid neighbors in all directions to avoid errors (see SimpleTiledModel.cs line 195)
