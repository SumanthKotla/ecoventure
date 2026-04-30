from ortools.constraint_solver import routing_enums_pb2, pywrapcp
 
 
def meters_to_miles(m: float) -> float:
    return m / 1609.34
 
 
def seconds_to_hours(s: float) -> float:
    return s / 3600
 
 
def optimize_route(distance_matrix: list[list[float]]) -> tuple[list[int], float]:
    """
    Solves TSP to find the optimal visit order.
    distance_matrix: 2D list of distances in meters.
    Returns (ordered_indices, total_distance_meters).
    """
    n = len(distance_matrix)
    BIG = 999_999_999
    int_matrix = [
        [int(d) if (d is not None and d >= 0) else BIG for d in row]
        for row in distance_matrix
    ]
 
    manager = pywrapcp.RoutingIndexManager(n, 1, 0)
    routing = pywrapcp.RoutingModel(manager)
 
    def distance_callback(from_idx, to_idx):
        return int_matrix[manager.IndexToNode(from_idx)][manager.IndexToNode(to_idx)]
 
    transit_idx = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_idx)
 
    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    params.time_limit.seconds = 10
 
    solution = routing.SolveWithParameters(params)
 
    if not solution:
        # BUG WAS HERE: was summing int_matrix[i][i] (diagonal = 0)
        # Fixed: fall back to greedy instead
        return greedy_route(distance_matrix)
 
    order = []
    idx = routing.Start(0)
    while not routing.IsEnd(idx):
        order.append(manager.IndexToNode(idx))
        idx = solution.Value(routing.NextVar(idx))
 
    total = solution.ObjectiveValue()
    return order, total
 
 
def greedy_route(distance_matrix: list[list[float]]) -> tuple[list[int], float]:
    """Fallback greedy nearest-neighbor if OR-Tools fails."""
    n = len(distance_matrix)
 
    # Sanitize: replace None / negative values with a large finite number
    BIG = 9_999_999_999.0
    clean = [
        [d if (d is not None and d >= 0) else BIG for d in row]
        for row in distance_matrix
    ]
 
    visited = [0]
    remaining = list(range(1, n))
    total = 0.0
 
    while remaining:
        last = visited[-1]
        nearest = min(remaining, key=lambda x: clean[last][x])
        total += clean[last][nearest]
        visited.append(nearest)
        remaining.remove(nearest)
 
    return visited, total
 
 
def build_leg_summary(
    stops: list[str],
    order: list[int],
    dist_matrix: list[list[float]],
    dur_matrix: list[list[float]],
) -> list[dict]:
    """Returns per-leg breakdown of the optimized route."""
    legs = []
    for i in range(len(order) - 1):
        frm = order[i]
        to = order[i + 1]
        legs.append({
            "from": stops[frm],
            "to": stops[to],
            "distance_miles": round(meters_to_miles(dist_matrix[frm][to]), 1),
            "drive_hours": round(seconds_to_hours(dur_matrix[frm][to]), 1),
        })
    return legs
 