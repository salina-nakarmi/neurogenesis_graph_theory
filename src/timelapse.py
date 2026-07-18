"""
timelapse.py — side-by-side animated comparison of the three neurogenesis
wiring strategies (Random / Preferential / Local).
 
WHAT THIS FILE DOES: replays each strategy's exact wiring rules from
simulation.py, one newborn at a time, and records what changed at every
step (which node was born, which edges appeared, and — for Local — which
maturation stage each newborn is in). It then renders all three strategies
side by side as a single animated GIF/MP4 so the structural differences
between strategies are visible frame-by-frame, not just in a final static
graph.
 
Colors match graph_model.py's plot_and_save_graph() exactly:
  DG excitatory        #4A69BD (blue)
  CA3 excitatory       #10AC84 (teal)
  CA1 excitatory       #5f27cd (purple)
  Inhibitory (any reg) #C83737 (red)
  Newborn / immature   #E6AD12 (gold/yellow)
 
Newborn neuron color progression:
  - Every newborn starts YELLOW (#E6AD12) the moment it's born.
  - Random / Preferential: wiring is instantaneous (no age-based staging
    exists in the model for these strategies), so their newborns stay
    yellow for the whole run — there's no "matured" state to render.
  - Local: this is the only strategy with real age-gated maturation
    (config.SIMULATION local_dg_only_age / local_ca3_age), so its
    newborns visibly progress:
        age <  local_dg_only_age               -> YELLOW  (young, DG-only)
        local_dg_only_age <= age < local_ca3_age -> ORANGE (aging, gained CA3)
        age >= local_ca3_age                    -> DG BLUE (matured — visually
                                                    folds back into the normal
                                                    DG population, same color
                                                    as every other mature DG
                                                    excitatory neuron)
 
Run:  python timelapse.py
Output: results/figures/neurogenesis_timelapse.{gif,mp4}
"""
 
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
 
import random
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as mpatches
 
from graph_model import create_hippocampal_graph
from simulation import (
    _wire_random, _wire_preferential, _wire_local_birth,
    _wire_local_expand_ca3, _wire_local_expand_ca1,
)
from config import GRAPH, SIMULATION, RESULTS_FIG_DIR
 
os.makedirs(RESULTS_FIG_DIR, exist_ok=True)
 
# ── Colors — identical to graph_model.py's plot_and_save_graph() palette ───
REGION_COLOR = {
    "DG":  "#4A69BD",   # mature DG excitatory (blue)
    "CA3": "#10AC84",   # mature CA3 excitatory (teal)
    "CA1": "#5f27cd",   # mature CA1 excitatory (purple)
}
INHIB_COLOR     = "#C83737"   # inhibitory interneuron, any region (red)
YOUNG_COLOR     = "#E6AD12"   # newborn, just born / DG-only (gold/yellow)
AGING_COLOR     = "#FF8C00"   # Local newborn that has gained CA3 links (orange)
MATURE_COLOR    = REGION_COLOR["DG"]   # Local newborn once fully matured -> same as DG
FEEDER_COLOR    = "#9AA0A6"   # gray — inhibitory feeder edges into newborns
CA3_EDGE_COLOR  = REGION_COLOR["CA3"]  # teal — newborn -> CA3 edges
CA1_EDGE_COLOR  = REGION_COLOR["CA1"]  # purple — newborn -> CA1 edges
FLASH_COLOR     = "#FF3B30"   # bright red — node/edges added THIS step
 
N_NEWBORNS = SIMULATION["n_newborns"]
 
 
def newborn_fill_color(strategy, stage_val):
    """Color of a newborn node given its current maturation stage.
    stage_val: 0 = DG-only/young, 1 = CA3 reached, 2 = CA1 reached (matured).
    Only 'Local' actually progresses through stages in this model."""
    if strategy == "Local":
        if stage_val >= 2:
            return MATURE_COLOR
        elif stage_val == 1:
            return AGING_COLOR
        else:
            return YOUNG_COLOR
    return YOUNG_COLOR   # Random / Preferential: no aging mechanic, stays yellow
 
 
# ─────────────────────────────────────────────────────────────────────────
# 1. Replay each strategy step-by-step, recording a compact history
# ─────────────────────────────────────────────────────────────────────────
 
def build_history(strategy_name, n_newborns=N_NEWBORNS):
    random.seed(GRAPH["seed"])
    np.random.seed(GRAPH["seed"])
 
    G, regions, _ = create_hippocampal_graph(n_immature=0)
    baseline_edges = list(G.edges())
    baseline_ntype = {n: G.nodes[n]["ntype"] for n in G.nodes()}
 
    immature_tracker = []
    newborn_order = []          # birth order list of newborn node ids
    stage = {}                  # node -> 0 (DG-only) / 1 (CA3 reached) / 2 (CA1 reached)
 
    ca3_edges_cum = set()       # accumulated newborn -> CA3 edges
    ca1_edges_cum = set()       # accumulated newborn -> CA1 edges
    feeder_edges_cum = set()    # accumulated inhibitory-feeder -> newborn edges
 
    history = [{
        "step": 0, "new_node": None,
        "newborns_so_far": [],
        "feeder_edges": set(), "ca3_edges": set(), "ca1_edges": set(),
        "new_feeder": set(), "new_ca3": set(), "new_ca1": set(),
        "stage": {},
    }]
 
    for i in range(1, n_newborns + 1):
        new_node = max(G.nodes()) + 1
        G.add_node(new_node, region="DG", ntype="excitatory",
                   age=SIMULATION["new_neuron_init_age"])
        regions["DG"].append(new_node)
        newborn_order.append(new_node)
        stage[new_node] = 0
 
        edges_before = set(G.edges())
 
        if strategy_name == "Random":
            _wire_random(G, regions, new_node)
            stage[new_node] = 1        # CA3 wired immediately
        elif strategy_name == "Preferential":
            _wire_preferential(G, regions, new_node)
            stage[new_node] = 1        # CA3 wired immediately
        elif strategy_name == "Local":
            _wire_local_birth(G, regions, new_node)
            immature_tracker.append(new_node)
        else:
            raise ValueError(f"Unknown strategy: {strategy_name}")
 
        if strategy_name == "Local":
            for node in immature_tracker:
                old_age = G.nodes[node]["age"]
                new_age = min(1.0, old_age + SIMULATION["age_increment"])
                G.nodes[node]["age"] = new_age
                if old_age < SIMULATION["local_dg_only_age"] <= new_age:
                    _wire_local_expand_ca3(G, regions, node)
                    stage[node] = max(stage.get(node, 0), 1)
                if old_age < SIMULATION["local_ca3_age"] <= new_age:
                    _wire_local_expand_ca1(G, regions, node)
                    stage[node] = max(stage.get(node, 0), 2)
 
        edges_after = set(G.edges())
        new_edges = edges_after - edges_before
 
        newborn_set = set(newborn_order)
        new_feeder = {(u, v) for (u, v) in new_edges if v in newborn_set and u not in newborn_set}
        new_ca3    = {(u, v) for (u, v) in new_edges if u in newborn_set and v in regions["CA3"]}
        new_ca1    = {(u, v) for (u, v) in new_edges if u in newborn_set and v in regions["CA1"]}
 
        feeder_edges_cum |= new_feeder
        ca3_edges_cum    |= new_ca3
        ca1_edges_cum    |= new_ca1
 
        history.append({
            "step": i, "new_node": new_node,
            "newborns_so_far": list(newborn_order),
            "feeder_edges": set(feeder_edges_cum),
            "ca3_edges": set(ca3_edges_cum),
            "ca1_edges": set(ca1_edges_cum),
            "new_feeder": new_feeder, "new_ca3": new_ca3, "new_ca1": new_ca1,
            "stage": dict(stage),
        })
 
    return {
        "regions": regions,            # final regions (baseline lists unchanged + all newborns in DG)
        "baseline_edges": baseline_edges,
        "baseline_ntype": baseline_ntype,
        "history": history,
    }
 
 
# ─────────────────────────────────────────────────────────────────────────
# 2. Fixed layout — identical baseline positions across all 3 panels,
#    newborns line up in a dedicated column so growth is easy to track
# ─────────────────────────────────────────────────────────────────────────
 
def build_layout(regions_baseline, n_newborns):
    pos = {}
    n_dg, n_ca3, n_ca1 = GRAPH["n_DG"], GRAPH["n_CA3"], GRAPH["n_CA1"]
 
    for i, n in enumerate(regions_baseline["DG"][:n_dg]):
        pos[n] = (0.0, i / max(n_dg - 1, 1))
    for i, n in enumerate(regions_baseline["CA3"][:n_ca3]):
        pos[n] = (1.15, i / max(n_ca3 - 1, 1))
    for i, n in enumerate(regions_baseline["CA1"][:n_ca1]):
        pos[n] = (2.3, i / max(n_ca1 - 1, 1))
 
    # newborn column, sits to the left, fills top -> bottom as they're born
    newborn_x = -0.55
    return pos, newborn_x
 
 
def newborn_pos(idx, n_newborns, newborn_x):
    return (newborn_x, idx / max(n_newborns - 1, 1))
 
 
# ─────────────────────────────────────────────────────────────────────────
# 3. Build all 3 histories + a shared layout
# ─────────────────────────────────────────────────────────────────────────
 
print("Replaying wiring rules for each strategy...")
strategies = SIMULATION["strategies"]
data = {s: build_history(s) for s in strategies}
print("Done. Building layout...")
 
pos_baseline, newborn_x = build_layout(data[strategies[0]]["regions"], N_NEWBORNS)
 
pos_full = dict(pos_baseline)
for s in strategies:
    for idx, entry in enumerate(data[s]["history"][1:]):
        pos_full[entry["new_node"]] = newborn_pos(idx, N_NEWBORNS, newborn_x)
 
 
# ─────────────────────────────────────────────────────────────────────────
# 4. Render
# ─────────────────────────────────────────────────────────────────────────
 
fig, axes = plt.subplots(1, 3, figsize=(19, 7.5))
fig.suptitle("", fontsize=15, fontweight="bold")
 
BASELINE_NODE_SIZE = 10
 
 
def draw_baseline(ax, regions, baseline_edges, baseline_ntype):
    for region_key in ("DG", "CA3", "CA1"):
        nodes = regions[region_key][:GRAPH[f"n_{region_key}"]] if region_key != "DG" \
                else regions[region_key][:GRAPH["n_DG"]]
        exc_x, exc_y, inh_x, inh_y = [], [], [], []
        for n in nodes:
            x, y = pos_baseline[n]
            if baseline_ntype[n] == "inhibitory":
                inh_x.append(x); inh_y.append(y)
            else:
                exc_x.append(x); exc_y.append(y)
        ax.scatter(exc_x, exc_y, s=BASELINE_NODE_SIZE, c=REGION_COLOR[region_key],
                   alpha=0.6, zorder=2, linewidths=0)
        ax.scatter(inh_x, inh_y, s=BASELINE_NODE_SIZE, c=INHIB_COLOR,
                   alpha=0.75, zorder=2, linewidths=0)
 
    # static faint backdrop of the existing (baseline) synaptic network
    for u, v in baseline_edges:
        x1, y1 = pos_baseline[u]
        x2, y2 = pos_baseline[v]
        ax.plot([x1, x2], [y1, y2], color="#CCCCCC", linewidth=0.25,
                alpha=0.18, zorder=1)
 
 
def draw_frame(ax, strategy, frame_idx):
    ax.clear()
    ax.set_xlim(-0.75, 2.6)
    ax.set_ylim(-0.06, 1.06)
    ax.axis("off")
 
    d = data[strategy]
    regions = d["regions"]
    draw_baseline(ax, regions, d["baseline_edges"], d["baseline_ntype"])
 
    entry = d["history"][frame_idx]
    newborns_so_far = entry["newborns_so_far"]
    stage = entry["stage"]
 
    # persistent (already-added) edges, categorized
    for (u, v) in entry["feeder_edges"] - entry["new_feeder"]:
        x1, y1 = pos_full[u]; x2, y2 = pos_full[v]
        ax.plot([x1, x2], [y1, y2], color=FEEDER_COLOR, linewidth=0.5, alpha=0.5, zorder=2)
    for (u, v) in entry["ca3_edges"] - entry["new_ca3"]:
        x1, y1 = pos_full[u]; x2, y2 = pos_full[v]
        ax.plot([x1, x2], [y1, y2], color=CA3_EDGE_COLOR, linewidth=0.6, alpha=0.55, zorder=2)
    for (u, v) in entry["ca1_edges"] - entry["new_ca1"]:
        x1, y1 = pos_full[u]; x2, y2 = pos_full[v]
        ax.plot([x1, x2], [y1, y2], color=CA1_EDGE_COLOR, linewidth=0.6, alpha=0.55, zorder=2)
 
    # this-step edges: flash color, thicker
    for (u, v) in entry["new_feeder"] | entry["new_ca3"] | entry["new_ca1"]:
        x1, y1 = pos_full[u]; x2, y2 = pos_full[v]
        ax.plot([x1, x2], [y1, y2], color=FLASH_COLOR, linewidth=1.8, alpha=0.9, zorder=4)
 
    # newborn nodes: fill color follows maturation stage (see newborn_fill_color)
    if newborns_so_far:
        xs, ys, colors, sizes, edgecolors, linewidths = [], [], [], [], [], []
        for n in newborns_so_far:
            x, y = pos_full[n]
            xs.append(x); ys.append(y)
            colors.append(newborn_fill_color(strategy, stage.get(n, 0)))
            just_born = (n == entry["new_node"])
            sizes.append(150 if just_born else 34)
            edgecolors.append(FLASH_COLOR if just_born else "white")
            linewidths.append(2.2 if just_born else 0.6)
        ax.scatter(xs, ys, s=sizes, c=colors, edgecolors=edgecolors,
                   linewidths=linewidths, zorder=5)
 
    n_ca3_links = len(entry["ca3_edges"])
    n_ca1_links = len(entry["ca1_edges"])
    ax.set_title(
        f"{strategy}\n"
        f"Newborns: {len(newborns_so_far):>2}   "
        f"Direct→CA3: {n_ca3_links:>3}   "
        f"Direct→CA1: {n_ca1_links:>2}",
        fontsize=12, fontweight="bold", loc="left"
    )
 
 
legend_handles = [
    mpatches.Patch(color=REGION_COLOR["DG"],  label="Mature DG excitatory"),
    mpatches.Patch(color=REGION_COLOR["CA3"], label="Mature CA3 excitatory"),
    mpatches.Patch(color=REGION_COLOR["CA1"], label="Mature CA1 excitatory"),
    mpatches.Patch(color=INHIB_COLOR,         label="Inhibitory interneuron"),
    mpatches.Patch(color=YOUNG_COLOR,         label="Newborn (young)"),
    mpatches.Patch(color=AGING_COLOR,         label="Local: aging"),
    mpatches.Patch(color=MATURE_COLOR,        label="Local: matured (= DG)"),
    mpatches.Patch(color=FLASH_COLOR,         label="Added this step"),
]
 
 
def animate(frame_idx):
    for ax, strategy in zip(axes, strategies):
        draw_frame(ax, strategy, frame_idx)
    fig.suptitle(
        f"Neurogenesis Integration Timelapse — Step {frame_idx}/{N_NEWBORNS}",
        fontsize=15, fontweight="bold", y=0.99
    )
    return []
 
 
# build once for legend sizing, then animate
animate(0)
fig.legend(handles=legend_handles, loc="lower center", ncol=4, fontsize=8.5,
           frameon=False, bbox_to_anchor=(0.5, -0.06))
plt.tight_layout(rect=[0, 0.09, 1, 0.95])
 
print("Rendering animation (this can take a minute)...")
anim = animation.FuncAnimation(fig, animate, frames=N_NEWBORNS + 1, interval=180)
 
mp4_path = os.path.join(RESULTS_FIG_DIR, "neurogenesis_timelapse.mp4")
gif_path = os.path.join(RESULTS_FIG_DIR, "neurogenesis_timelapse.gif")
 
try:
    anim.save(mp4_path, writer=animation.FFMpegWriter(fps=6, bitrate=1800), dpi=110)
    print(f"Saved timelapse (mp4, small) -> {mp4_path}")
except Exception as e:
    print(f"ffmpeg unavailable ({e}); skipping mp4")
 
anim.save(gif_path, writer=animation.PillowWriter(fps=6), dpi=85)
plt.close(fig)
print(f"Saved timelapse (gif) -> {gif_path}")
 
