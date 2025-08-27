import math


def remove_nearby_points(target_points, reference_points, threshold):
    """
    Removes points in target_points that are within `threshold` distance
    of any point in reference_points.
    """
    filtered_points = []
    for tx, ty in target_points:
        too_close = False
        for rx, ry in reference_points:
            dist = math.hypot(rx - tx, ry - ty)
            if dist <= threshold:
                too_close = True
                break
        if not too_close:
            filtered_points.append((tx, ty))

    return filtered_points


def distance(p1, p2):
    return math.hypot(p2[0]-p1[0], p2[1]-p1[1])


import math

def distance(p1, p2):
    return math.dist(p1, p2)

def connect_lists(target_points, other_points):
    """
    Finds two distinct points from `other_points` that are:
    - close to `target_points` (min distance criterion)
    - far from each other (max distance criterion)
    """
    if not target_points or not other_points:
        return target_points.copy()
    
    # Step 1: compute each point's distance to the closest target point
    scored = []
    for op in other_points:
        min_d = min(distance(op, tp) for tp in target_points)
        scored.append((min_d, op))
    
    # Step 2: sort by closeness to target
    scored.sort(key=lambda x: x[0])
    
    # Keep the top-k closest candidates (to avoid extremes ruining step 2)
    k = min(5, len(scored))  # adjustable
    candidates = [op for _, op in scored[:k]]
    
    # Step 3: from candidates, pick the pair that are farthest apart
    best_pair = None
    max_sep = -1
    for i in range(len(candidates)):
        for j in range(i+1, len(candidates)):
            sep = distance(candidates[i], candidates[j])
            if sep > max_sep:
                max_sep = sep
                best_pair = (candidates[i], candidates[j])
    
    # Handle edge case: if we only had one candidate
    if best_pair is None:
        best_pair = (candidates[0], candidates[0])
    
    extended = [best_pair[0]] + target_points + [best_pair[1]]
    return extended
