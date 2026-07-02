# =============================================================================
# config.py
# COMP 323 — Neurogenesis & Graph Theory Project
#
# WHAT THIS FILE DOES: single source of truth for every tunable number in the
# project. Every value here is actually imported and used somewhere — if you
# change GRAPH["n_DG"] or SIMULATION["local_ca3_age"], the simulation behaves
# differently.
# =============================================================================

import os

# ── Paths ─────────────────────────────────────────────────────────────────
BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
RESULTS_FIG_DIR = os.path.join(BASE_DIR, "results", "figures")
RESULTS_MET_DIR = os.path.join(BASE_DIR, "results", "metrics")

# ── Baseline graph parameters (Days 3-4) — used by graph_model.py ──────────
GRAPH = {
    "n_DG":  40,
    "n_CA3": 30,
    "n_CA1": 30,
    "n_immature": 0,          # mature baseline for Week 1 connectivity analysis
    "seed": 42,

    # Edge fan-out per node type (mirrors graph_model.py's wiring rules)
    "dg_ca3_out":     8,
    "ca3_recurrent":  10,
    "ca3_ca1_out":    8,
    "inhibitory_out": 10,

    # Synaptic strength range (excitatory magnitude before sign is applied)
    "synaptic_strength_min": 0.5,
    "synaptic_strength_max": 0.9,
}

# ── Neurogenesis simulation parameters (Days 8-9) — used by simulation.py ──
SIMULATION = {
    "n_newborns": 50,
    "new_neuron_init_age": 0.1,

    "strategies": ["Random", "Preferential", "Local"],

    # Local-attachment maturation thresholds (brief §6.2 / Assumption B2):
    # age < local_dg_only_age        -> connect within DG only
    # local_dg_only_age <= age < local_ca3_age -> expand to CA3
    # age >= local_ca3_age           -> full connectivity (adds CA1 too)
    "local_dg_only_age": 0.3,
    "local_ca3_age":     0.7,
    "age_increment":     0.05,   # age gained per simulation timestep

    # Checkpoints at which the expensive metrics (fundamental circuits,
    # planarity) are computed, per brief §7 Propositions 1-3 (t=0,25,50)
    "checkpoints": [0, 25, 50],

    "n_cascade_trials": 100,     # Monte-Carlo trials for the signal cascade
}

# ── Visualization settings — used by connectivity.py's visualize_connectivity() ──
VIZ = {
    "node_colors": {
        "DG":  "#4A69BD",
        "CA3": "#10AC84",
        "CA1": "#5f27cd",
    },
}

# ── Report strings ──────────────────────────────────────────────────────────
PROJECT = {
    "title":      "Neurogenesis & Graph Theory",
    "subtitle":   "Simulating New Neuron Integration in Hippocampal Networks",
    "course":     "COMP 323 — Graph Theory",
    "university": "Kathmandu University",
    "team":       "Group B",
    "reference":  "Narsingh Deo, Graph Theory (Dover, 2016)",
}