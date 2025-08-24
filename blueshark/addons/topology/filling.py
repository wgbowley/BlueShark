"""
Filename: filling.py
Author: William Bowley
Version: 0.1
Date: 2025-08-16

Description:
    This addon aims to add topology optimization
    to the framework for all solvers

    This module fills geometry using scanline fill
"""

def flood_fill(
    voxel_map: list[list[int]],
    centroid: tuple[int, int],
    material: int,
) -> None:
    y, x = centroid  # swap to row = y, col = x
    if voxel_map[y][x] == material:
        return

    orig_color = voxel_map[y][x]
    m, n = len(voxel_map), len(voxel_map[0])
    stack = [(y, x)]
    # voxel_map[y][x] = 4  # fill the seed immediately

    while stack:
        cy, cx = stack.pop()
        if voxel_map[cy][cx] == orig_color:
            voxel_map[cy][cx] = material

            # neighbors (up, down, left, right)
            if cy + 1 < m:
                stack.append((cy + 1, cx))
            if cy - 1 >= 0:
                stack.append((cy - 1, cx))
            if cx + 1 < n:
                stack.append((cy, cx + 1))
            if cx - 1 >= 0:
                stack.append((cy, cx - 1))
