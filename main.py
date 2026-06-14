"""
main.py — COMP 323 Neurogenesis & Graph Theory Project
=======================================================
Single entry point. Runs the full pipeline or individual phases.

Usage:
    python main.py                        # full pipeline
    python main.py --phase baseline       # Days 3-4 only
    python main.py --phase connectivity   # Days 5-6 only
    python main.py --phase simulate       # Days 8-9 only (coming Week 2)
    python main.py --phase analyze        # Days 10-11 only (coming Week 2)
"""

import sys
import os
import argparse
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║   COMP 323 — Graph Theory   |   Kathmandu University        ║
║   Neurogenesis & Graph Theory:                               ║
║   Simulating New Neuron Integration in Hippocampal Networks  ║
║   Group B  ·  2-Week Project                                 ║
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
    """Days 8-9: Neurogenesis simulation (Week 2)."""
    print("\n── PHASE: NEUROGENESIS SIMULATION (Days 8-9) ─────────────────")
    sim_path = os.path.join(os.path.dirname(__file__), "src", "simulation.py")
    if not os.path.exists(sim_path):
        print("  ⏳ simulation.py not yet implemented — coming Days 8-9.")
        print("  When ready, run:  python main.py --phase simulate")
    else:
        from simulation import run_simulation
        run_simulation()
        print("  ✓ Simulation complete.")


def phase_analyze():
    """Days 10-11: Metric plots and analysis (Week 2)."""
    print("\n── PHASE: ANALYSIS & PLOTS (Days 10-11) ──────────────────────")
    met_path = os.path.join(os.path.dirname(__file__), "src", "metrics.py")
    if not os.path.exists(met_path):
        print("  ⏳ metrics.py not yet implemented — coming Days 10-11.")
    else:
        from metrics import run_analysis
        run_analysis()
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
    print(f"  Data    → data/raw/  &  data/processed/")
    print(f"{'═'*62}\n")


if __name__ == "__main__":
    main()