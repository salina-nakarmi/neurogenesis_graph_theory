"""
simulation_plot.py — Days 10-11 deliverable.

WHAT THIS FILE DOES: reads simulation_metrics.csv (produced by
simulation.py / main.py --phase simulate) and plots how four
graph-theoretic properties evolve over the 50-neuron integration, one
line per strategy. These four panels are the direct visual evidence for
Proposition 1 (preferential attachment preserves small-world structure:
clustering, path length, κ ≥ 3 — better than random attachment).

(Previously this file also defined an unused inline `data` string that
was dead code left over from early testing — removed. It also only had
3 panels; Avg_Shortest_Path is one of the five metrics named in the
brief §6.1 and is required to actually evaluate Proposition 1, so it's
added as a 4th panel here.)
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("simulation_metrics.csv")

sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(1, 4, figsize=(24, 5))
fig.suptitle("Evolution of Hippocampal Graph Topology During Neurogenesis",
             fontsize=16, fontweight='bold', y=1.05)

palette = {"Random": "#3498db", "Preferential": "#e74c3c", "Local": "#2ecc71"}

# Panel 1: Structural Integrity (Kappa Connectivity)
sns.lineplot(ax=axes[0], data=df, x="Newborns_Added", y="Kappa", hue="Strategy", palette=palette, linewidth=2.5)
axes[0].set_title("Network Structural Robustness (κ)", fontsize=12, fontweight='bold')
axes[0].set_xlabel("Newborn Neurons Added", fontsize=10)
axes[0].set_ylabel("Vertex Connectivity (κ)", fontsize=10)
axes[0].set_ylim(0, 7)

# Panel 2: Average Network Degree
sns.lineplot(ax=axes[1], data=df, x="Newborns_Added", y="Avg_Degree", hue="Strategy", palette=palette, linewidth=2.5)
axes[1].set_title("Average Structural Node Degree", fontsize=12, fontweight='bold')
axes[1].set_xlabel("Newborn Neurons Added", fontsize=10)
axes[1].set_ylabel("Average Degree (⟨k⟩)", fontsize=10)

# Panel 3: Clustering Coefficient (Local Information Processing)
sns.lineplot(ax=axes[2], data=df, x="Newborns_Added", y="Clustering_Coeff", hue="Strategy", palette=palette, linewidth=2.5)
axes[2].set_title("Network Local Clustering Coefficient", fontsize=12, fontweight='bold')
axes[2].set_xlabel("Newborn Neurons Added", fontsize=10)
axes[2].set_ylabel("Clustering Coefficient (C)", fontsize=10)

# Panel 4: Average Shortest Path Length (needed for Proposition 1)
sns.lineplot(ax=axes[3], data=df, x="Newborns_Added", y="Avg_Shortest_Path", hue="Strategy", palette=palette, linewidth=2.5)
axes[3].set_title("Average Shortest Path Length", fontsize=12, fontweight='bold')
axes[3].set_xlabel("Newborn Neurons Added", fontsize=10)
axes[3].set_ylabel("Avg. Shortest Path Length", fontsize=10)

plt.tight_layout()

output_image = "neurogenesis_results_panel.png"
plt.savefig(output_image, dpi=300, bbox_inches='tight')
plt.close()

print(f"Experimental analytical panels successfully generated and saved to: '{output_image}'")