# graph.py
# Utilities for generating directed graphs (Erdős–Rényi), converting representations and saving

import random
from typing import Tuple, Dict, List, Any
import json
import os

def erdos_renyi_directed(n: int, density: float, weighted: bool = False,
                         weight_range: Tuple[int,int]=(1,10), seed: int | None = None
                        ) -> Tuple[Dict[int, List[Any]], List[List[Any]]]:
    """
    Generates a directed simple graph (no loops, no multi-edges)
    Parameters:
      - n: number of vertices (vertices 0..n-1)
      - density: density as percent or fraction (0..1). If >1 and <=100, it's treated as percent.
      - weighted: whether to add weights (int)
      - weight_range: (min,max) inclusive for weights
      - seed: random seed
    Returns (adj_list, adj_matrix)
      - adj_list: {v: [neigh, ...]} or [(neigh, weight), ...] if weighted
      - adj_matrix: n x n matrix (0 or weight)
    """
    if seed is not None:
        random.seed(seed)

    # Normalize density: if user provided 10 (likely 10%), convert to 0.1
    if density > 1:
        density = density / 100.0

    if not (0 <= density <= 1):
        raise ValueError("density must be in [0,1] (or provided as percent >1).")

    m_max = n * (n - 1)  # for directed graph (no self-loops)
    m = int(round(density * m_max))

    edges = set()
    # Generate unique directed edges (u, v), u != v
    while len(edges) < m:
        u = random.randrange(n)
        v = random.randrange(n)
        if u == v:
            continue
        if (u, v) in edges:
            continue
        edges.add((u, v))

    # Build representations
    adj_list = {i: [] for i in range(n)}
    adj_matrix = [[0]*n for _ in range(n)]

    for (u, v) in edges:
        if weighted:
            w = random.randint(weight_range[0], weight_range[1])
            adj_list[u].append((v, w))
            adj_matrix[u][v] = w
        else:
            adj_list[u].append(v)
            adj_matrix[u][v] = 1

    return adj_list, adj_matrix

def list_to_matrix(adj_list: Dict[int, List[Any]], n: int) -> List[List[Any]]:
    mat = [[0]*n for _ in range(n)]
    for u, neighs in adj_list.items():
        if len(neighs) > 0 and isinstance(neighs[0], tuple):
            # weighted
            for v, w in neighs:
                mat[u][v] = w
        else:
            for v in neighs:
                mat[u][v] = 1
    return mat

def matrix_to_list(mat: List[List[Any]]) -> Dict[int, List[Any]]:
    n = len(mat)
    adj = {i: [] for i in range(n)}
    for u in range(n):
        for v in range(n):
            if mat[u][v] != 0:
                adj[u].append(v)
    return adj

def save_adj_list_json(adj_list: Dict[int, List[Any]], path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(adj_list, f, ensure_ascii=False, indent=2)

def load_adj_list_json(path: str) -> Dict[int, List[Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)
