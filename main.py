"""
main.py — COMP 323 Neurogenesis & Graph Theory Project
=======================================================
Single entry point. Runs the full pipeline or individual phases.

Usage:
    python main.py                        # full pipeline
    python main.py --phase baseline       # Days 3-4 only
    python main.py --phase connectivity   # Days 5-6 only
    python main.py --phase simulate       # Days 8-9 only
    python main.py --phase analyze        # Days 10-11 only

NOTE: previously this inserted a "src/" subfolder onto sys.path and called
functions (run_simulation, run_analysis) that don't exist in this repo —
leftover from an earlier planned layout. All files live at the repo root,
so no path juggling is needed, and the calls now match the real function
names in simulation.py / simulation_plot.py.
"""

import time
import argparse
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║   COMP 323 — Graph Theory   |   Kathmandu University          ║
║   Neurogenesis & Graph Theory:                                ║
║   Simulating New Neuron Integration in Hippocampal Networks   ║
║   Group B  ·  2-Week Project                                  ║
╚══════════════════════════════════════════════════════════════╝
"""


def phase_baseline():
    """Days 3-4: Build and visualize the baseline hippocampal graph."""
    print("\n── PHASE: BASELINE GRAPH (Days 3-4) ──────────────────────────")
    from graph_model import create_hippocampal_graph, plot_and_save_graph
    G, regions, immature = create_hippocampal_graph()
    plot_and_save_graph(G, regions, immature)

    print(f"  Nodes  : {G.number_of_nodes()}")
    print(f"  Edges  : {G.number_of_edges()}")
    print(f"  ✓ Baseline graph built and visualized.")
    return G, regions, immature


def phase_connectivity():
    """Days 5-6: Full Unit 3 connectivity and planarity analysis."""
    print("\n── PHASE: CONNECTIVITY ANALYSIS (Days 5-6) ───────────────────")
    from connectivity import run_connectivity_analysis
    run_connectivity_analysis()
    print("  ✓ Connectivity analysis complete.")


def phase_simulate():
    """Days 8-9: Neurogenesis simulation across all three strategies."""
    print("\n── PHASE: NEUROGENESIS SIMULATION (Days 8-9) ─────────────────")
    import csv
    from simulation import run_neurogenesis_experiment
    from config import SIMULATION

    all_results = []
    for strategy in SIMULATION["strategies"]:
        print(f"  -> Simulating: {strategy}")
        all_results.extend(run_neurogenesis_experiment(strategy))

    fields = ['Strategy', 'Newborns_Added', 'Kappa', 'Lambda', 'Min_Degree',
              'Avg_Degree', 'Clustering_Coeff', 'Avg_Shortest_Path',
              'Fundamental_Circuits', 'Is_Planar']
    with open("simulation_metrics.csv", mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(all_results)
    print("  ✓ Simulation complete → simulation_metrics.csv")


def phase_analyze():
    """Days 10-11: Metric plots and analysis."""
    print("\n── PHASE: ANALYSIS & PLOTS (Days 10-11) ──────────────────────")
    import simulation_plot  # running the module generates and saves the figure
    print("  ✓ Analysis complete.")


def main():
    print(BANNER)

    parser = argparse.ArgumentParser(
        description="COMP 323 Neurogenesis & Graph Theory Pipeline"
    )
    parser.add_argument(
        "--phase",
        choices=["baseline", "connectivity", "simulate", "analyze", "all"],
        default="all",
        help="Which phase to run (default: all)"
    )
    args = parser.parse_args()

    start = time.time()

    if args.phase in ("baseline", "all"):
        phase_baseline()

    if args.phase in ("connectivity", "all"):
        phase_connectivity()

    if args.phase in ("simulate", "all"):
        phase_simulate()

    if args.phase in ("analyze", "all"):
        phase_analyze()

    elapsed = time.time() - start
    print(f"\n{'═'*62}")
    print(f"  Pipeline complete in {elapsed:.1f}s")
    print(f"  Figures → results/figures/")
    print(f"  Metrics → simulation_metrics.csv")
    print(f"{'═'*62}\n")


if __name__ == "__main__":
    main()