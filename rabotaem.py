# rabotaem.py
# Experiments for Kahn's algorithm + saving visualizations (matrix and adjacency list)
# Added:
#  - saving adjacency list to .txt in fallback
#  - saving topo order to .txt
#  - option --overwrite-visuals (default False): if False, existing files are not overwritten

import argparse
import csv
import time
import gc
import statistics
import os
from typing import List

from graph import erdos_renyi_directed, ensure_dir
from kan import kahn_list, kahn_matrix
import visualize

import matplotlib.pyplot as plt  # required to save/close figures in the visualizer

def time_function(func, *args, repeats=1):
    times = []
    for _ in range(repeats):
        gc.collect()
        t0 = time.perf_counter()
        res = func(*args)
        t1 = time.perf_counter()
        times.append((t1 - t0, res))
    return times  # list of tuples (time, result)


def save_visual_examples(adj_list, adj_matrix, plot_dir, n, density, trial,
                         topo_result = None, save_suffix="", overwrite: bool = False):
    """
    Save:
      - matrix_{base}.png  (heatmap)  (skipped if already exists and overwrite=False)
      - list_matrix_{base}.png         (from adjacency list)
      - list_graph_{base}.png (if networkx is installed)
      - list_adj_{base}.txt  (adjacency list, in fallback or additionally)
      - topo_{base}.txt      (Kahn's result: order or "CYCLE")
    Returns a dict with paths and flags of what was actually saved.
    """
    vdir = os.path.join(plot_dir, "visualizations")
    os.makedirs(vdir, exist_ok=True)
    density_tag = f"{int(density*100)}"
    base_name = f"n{n}_d{density_tag}_t{trial}{save_suffix}"

    results = {}

    # matrix (from matrix)
    mat_path = os.path.join(vdir, f"matrix_{base_name}.png")
    try:
        ok = visualize.visualize_adjacency_matrix(adj_matrix,
                                            labels=[str(i) for i in range(len(adj_matrix))],
                                            figsize=(6,6),
                                            annotate=True,
                                            save_path=mat_path,
                                            show=False,
                                            overwrite=overwrite)
        results["matrix_path"] = mat_path
        results["matrix_saved"] = bool(ok)
        if results["matrix_saved"]:
            print(f"[Saved] {mat_path}")
    except Exception as e:
        print("Error saving matrix:", e)
        results["matrix_saved"] = False

    # list_matrix and list_graph (and fallback .txt)
    list_matrix_path = os.path.join(vdir, f"list_matrix_{base_name}.png")
    list_graph_path  = os.path.join(vdir, f"list_graph_{base_name}.png")
    list_txt_path    = os.path.join(vdir, f"list_adj_{base_name}.txt")
    try:
        resdict = visualize.visualize_adjacency_list(adj_list,
                                          labels=[str(i) for i in range(len(adj_matrix))],
                                          as_matrix=True,
                                          matrix_figsize=(6,6),
                                          graph_figsize=(6,6),
                                          save_matrix_path=list_matrix_path,
                                          save_graph_path=list_graph_path,
                                          save_adj_txt_path=list_txt_path,
                                          show=False,
                                          overwrite=overwrite)
        # resdict reports which files were actually saved
        results["list_matrix_path"] = list_matrix_path
        results["list_graph_path"]  = list_graph_path
        results["list_txt_path"]    = list_txt_path
        results["list_matrix_saved"] = resdict.get("matrix", False)
        results["list_graph_saved"]  = resdict.get("graph", False)
        results["list_txt_saved"]    = resdict.get("adj_txt", False)

        if results["list_matrix_saved"]:
            print(f"[Saved] {list_matrix_path}")
        if results["list_graph_saved"]:
            print(f"[Saved] {list_graph_path}")
        if results["list_txt_saved"]:
            print(f"[Saved] {list_txt_path}")
    except Exception as e:
        print("Error saving adjacency list visualization:", e)

    # Save topo result to file (if provided), and/or adjacency as txt (additionally)
    topo_path = os.path.join(vdir, f"topo_{base_name}.txt")
    adj_path  = os.path.join(vdir, f"adj_{base_name}.txt")

    try:
        # adjacency list to .txt (in addition to visualize)
        if not (os.path.exists(adj_path) and not overwrite):
            with open(adj_path, "w", encoding="utf-8") as f:
                # build text
                from visualize import _format_adj_text
                f.write(_format_adj_text(adj_list))
            print(f"[Saved] {adj_path}")
        else:
            print(f"[Skip] {adj_path} (exists, overwrite=False)")

        # topo
        if topo_result is None:
            # if not passed — compute safely
            topo = kahn_list_safe(adj_list)
        else:
            topo = topo_result

        if not (os.path.exists(topo_path) and not overwrite):
            with open(topo_path, "w", encoding="utf-8") as f:
                if topo is None:
                    f.write("CYCLE\n")
                else:
                    # write vertices separated by space
                    f.write(" ".join(map(str, topo)) + "\n")
            print(f"[Saved] {topo_path}")
        else:
            print(f"[Skip] {topo_path} (exists, overwrite=False)")

        results["topo_path"] = topo_path
        results["adj_path"]  = adj_path
    except Exception as e:
        print("Error saving adj/topo:", e)

    return results


# helper to get topo without raising
def kahn_list_safe(adj):
    try:
        return kahn_list(adj)
    except Exception:
        return None


def run_experiments(ns: List[int], densities: List[float], repeats: int,
                    out_csv: str, plot_dir: str,
                    save_examples: bool, save_each: bool, example_every_k: int,
                    overwrite_visuals: bool,
                    warmup_runs: int = 2):
    ensure_dir(os.path.dirname(out_csv) or ".")
    ensure_dir(plot_dir)

    header = ["n", "density", "representation", "trial", "time_s"]
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)

        for n in ns:
            for density in densities:
                print(f"Running: n={n}, density={density:.3f}")
                saved_for_pair = False

                for trial in range(1, repeats+1):
                    # Generate graph (generation is outside the measurement)
                    adj_list, adj_matrix = erdos_renyi_directed(n, density, weighted=False)

                    # Warm-up (first few runs)
                    if trial <= warmup_runs:
                        kahn_list(adj_list)
                        kahn_matrix(adj_matrix)

                    # Measurement for lists (get time and result)
                    t_list_res = time_function(kahn_list, adj_list, repeats=1)[0]
                    t_list = t_list_res[0]
                    # topological order result (can be used for saving)
                    topo_list = t_list_res[1]

                    writer.writerow([n, density, "list", trial, f"{t_list:.9f}"])
                    f.flush()

                    # Measurement for matrix (we only need time)
                    t_mat_res = time_function(kahn_matrix, adj_matrix, repeats=1)[0]
                    t_mat = t_mat_res[0]
                    writer.writerow([n, density, "matrix", trial, f"{t_mat:.9f}"])
                    f.flush()

                    # visualization saving logic:
                    if save_examples:
                        do_save = False
                        if save_each:
                            do_save = True
                        elif example_every_k and example_every_k > 0:
                            if (trial % example_every_k) == 0:
                                do_save = True
                        else:
                            if not saved_for_pair:
                                do_save = True
                                saved_for_pair = True

                        if do_save:
                            save_visual_examples(adj_list, adj_matrix, plot_dir, n, density, trial,
                                                 topo_result=topo_list, save_suffix="", overwrite=overwrite_visuals)

    print("Experiments finished, CSV saved:", out_csv)

    # Build summary plots (mean time vs n)
    summarize_and_plot(out_csv, plot_dir, densities)


def summarize_and_plot(csv_path: str, plot_dir: str, densities: List[float]):
    # Read CSV
    data = {}
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            n = int(r["n"])
            density = float(r["density"])
            rep = r["representation"]
            t = float(r["time_s"])
            key = (density, rep, n)
            data.setdefault(key, []).append(t)

    for density in densities:
        ns = sorted({k[2] for k in data.keys() if abs(k[0]-density) < 1e-12})
        mean_list = []
        mean_mat = []
        for n in ns:
            times_list = data.get((density, "list", n), [])
            times_mat  = data.get((density, "matrix", n), [])
            mean_list.append(statistics.mean(times_list) if times_list else 0)
            mean_mat.append(statistics.mean(times_mat) if times_mat else 0)

        plt.figure()
        plt.plot(ns, mean_list, marker="o", label="list (O(V+E))")
        plt.plot(ns, mean_mat, marker="s", label="matrix (O(V^2))")
        plt.title(f"Kahn time vs n — density={density:.3f}")
        plt.xlabel("n")
        plt.ylabel("mean time (s)")
        plt.legend()
        plt.grid(True)
        os.makedirs(plot_dir, exist_ok=True)
        out_path = os.path.join(plot_dir, f"time_vs_n_density_{int(density*100)}.png")
        plt.savefig(out_path)
        plt.close()
        print("Saved plot:", out_path)


def parse_args():
    parser = argparse.ArgumentParser(description="Kahn algorithm experiments with visualizations")
    parser.add_argument("--out", type=str, default="results/raw_results.csv", help="CSV output path")
    parser.add_argument("--plots", type=str, default="plots", help="Folder for plots and visualizations")
    parser.add_argument("--repeats", type=int, default=20, help="Repeats per (n,density)")
    parser.add_argument("--ns", type=str, default="20,40,60,80,100,120,140,160,180,200", help="Comma-separated n values")
    parser.add_argument("--densities", type=str, default="0.01,0.05,0.10,0.20,0.50", help="Comma-separated densities (0..1 or percents)")
    parser.add_argument("--save-examples", dest="save_examples", action="store_true", help="Save visualization examples (matrix + list) per (n,density). Default: False")
    parser.add_argument("--save-each", dest="save_each", action="store_true", help="If set, save visualization for EACH trial (can produce many files). Default: False")
    parser.add_argument("--example-every-k", dest="example_every_k", type=int, default=0, help="If >0 and --save-examples set, save visualization every K-th trial (e.g. K=5). Default: 0 (disabled)")
    parser.add_argument("--overwrite-visuals", dest="overwrite_visuals", action="store_true", help="If set, overwrite existing visualization files (images and txt). Default: False")
    parser.set_defaults(save_examples=False, save_each=False, overwrite_visuals=False)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    ns = [int(x) for x in args.ns.split(",") if x.strip()]
    densities = []
    for d in args.densities.split(","):
        d = d.strip()
        if not d:
            continue
        val = float(d)
        if val > 1:
            val = val / 100.0
        densities.append(val)

    if args.example_every_k and args.example_every_k < 1:
        raise ValueError("--example-every-k must be >= 1")

    run_experiments(ns, densities, repeats=args.repeats, out_csv=args.out, plot_dir=args.plots,
                    save_examples=args.save_examples, save_each=args.save_each, example_every_k=args.example_every_k,
                    overwrite_visuals=args.overwrite_visuals)
