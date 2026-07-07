"""
functional_simulation.py — bonus extension (gestures at Unit 7 / signal
propagation, mentioned but not detailed in the brief's syllabus table).
Not one of the five core deliverables — keep or cut depending on time
budget before the Days 12-13 report is due.

WHAT THIS FILE DOES: after the 50-neuron integration loop finishes (using
the *actual* wiring rules from simulation.py — this used to re-implement
its own copy of the Random/Preferential/Local rules, which had drifted
out of sync with simulation.py), seeds a small fraction of DG nodes as
"active" and lets excitatory activation spread through the network for up
to max_steps, checking whether/when the signal reaches CA1. Repeats
n_cascade_trials times per strategy and reports mean spread % and mean
latency to CA1.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import random

from simulation import run_neurogenesis_experiment
from config import SIMULATION


def simulate_signal_cascade(G, regions, seed_percentage=0.1, threshold=0.15, max_steps=20):
    """Simulates a functional signal cascade from DG through CA3 to CA1."""
    dg_nodes = regions['DG']
    n_seeds = max(1, int(len(dg_nodes) * seed_percentage))

    active_nodes = set(random.sample(dg_nodes, k=n_seeds))
    activation_history = [len(active_nodes)]
    ca1_reached_step = None

    for step in range(1, max_steps + 1):
        next_activated = set()
        inactive_nodes = set(G.nodes()) - active_nodes
        for node in inactive_nodes:
            incoming = G.in_edges(node, data=True)
            active_inputs = [data['weight'] for u, v, data in incoming if u in active_nodes]
            excitatory_drive = sum(w for w in active_inputs if w > 0)
            if excitatory_drive >= threshold:
                next_activated.add(node)

        if not next_activated:
            break

        active_nodes.update(next_activated)
        activation_history.append(len(active_nodes))

        ca1_active = [n for n in regions['CA1'] if n in active_nodes]
        if ca1_active and ca1_reached_step is None:
            ca1_reached_step = step

    total_nodes = len(G.nodes())
    reach_percentage = (len(active_nodes) / total_nodes) * 100
    return round(reach_percentage, 2), ca1_reached_step


def run_functional_evaluation():
    """Builds each strategy's post-integration network (via simulation.py,
    not a re-implementation) and tests functional signal propagation."""
    print("Running Functional Signal Cascade Evaluation...")

    for strategy in SIMULATION["strategies"]:
        # Reuse the real wiring rules and get back the finished graph
        _, G, regions = run_neurogenesis_experiment(strategy, return_graph=True)

        reaches, latencies = [], []
        for _ in range(SIMULATION["n_cascade_trials"]):
            reach, latency = simulate_signal_cascade(G, regions)
            reaches.append(reach)
            if latency is not None:
                latencies.append(latency)

        avg_reach = np.mean(reaches)
        avg_latency = np.mean(latencies) if latencies else float('inf')

        print(f"\nResults for [{strategy}] Strategy:")
        print(f" -> Mean Signal Spread: {round(avg_reach, 2)}% of entire network")
        print(f" -> Mean Latency to CA1: {round(avg_latency, 2)} steps")


if __name__ == "__main__":
    run_functional_evaluation()