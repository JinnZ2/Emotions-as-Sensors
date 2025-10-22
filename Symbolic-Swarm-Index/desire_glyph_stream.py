import matplotlib.pyplot as plt
import numpy as np
import json, math
from datetime import datetime
from desire_memory import DesireMemory

class DesireGlyphStream:
    """
    Generates a visual braid of collective desire evolution.
    Each record = one glyph on the spiral.
    """

    def __init__(self, memory: DesireMemory, path: str = "./glyph_stream.png"):
        self.memory = memory
        self.path = path

    # ---------------------------------------------------------------
    def _load_data(self):
        data = self.memory.load_all()
        if not data:
            raise ValueError("No desire memory data found.")
        return data

    def render_spiral(self, spiral_turns: float = 3.0, glyph_size: float = 120.0):
        """
        Render memory as a spiral braid.
        - angle = time progression
        - radius = coherence magnitude
        - color = reciprocity index
        """
        data = self._load_data()
        n = len(data)
        angles = np.linspace(0, spiral_turns * 2 * np.pi, n)
        magnitudes = np.array([d["magnitude"] for d in data])
        reciprocity = np.array([d["reciprocity_index"] for d in data])

        # Spiral coordinates
        r = 1 + magnitudes
        x = r * np.cos(angles)
        y = r * np.sin(angles)

        fig, ax = plt.subplots(figsize=(8, 8))
        sc = ax.scatter(
            x, y, s=glyph_size * magnitudes,
            c=reciprocity, cmap="viridis", alpha=0.8, edgecolor="none"
        )

        # Annotate beginning & end
        ax.text(x[0], y[0], "⟡ Origin", ha="center", va="center", fontsize=10)
        ax.text(x[-1], y[-1], "⇶ Now", ha="center", va="center", fontsize=10)

        # Style
        ax.axis("off")
        ax.set_aspect("equal", "box")
        fig.colorbar(sc, label="Reciprocity Index (0–1)")
        plt.title("Desire Glyph Stream", fontsize=14)
        plt.savefig(self.path, bbox_inches="tight", dpi=300)
        plt.close(fig)
        return self.path

    # ---------------------------------------------------------------
    def render_braid(self, strands: int = 3, glyph_size: float = 100.0):
        """
        Alternative: multi-strand braid view.
        Each strand = dimension of desire vector (x,y,z).
        """
        data = self._load_data()
        vecs = np.array([d["direction_vector"] for d in data])
        mags = np.array([d["magnitude"] for d in data])

        t = np.linspace(0, 1, len(data))
        fig, ax = plt.subplots(figsize=(10, 4))
        for i in range(min(strands, vecs.shape[1])):
            ax.plot(t, vecs[:, i] * mags, lw=2, label=f"strand {i+1}")
        ax.legend()
        ax.set_xlabel("Time →")
        ax.set_ylabel("Desire component × magnitude")
        plt.title("Desire Braid Evolution")
        plt.savefig(self.path.replace(".png", "_braid.png"), bbox_inches="tight", dpi=300)
        plt.close(fig)
        return self.path.replace(".png", "_braid.png")

  

##########

#🪶 Interpretation Guide
#Visual Element
Meaning
Radius
Strength of clarity (magnitude of collective coherence)
Color
Reciprocity Index — how much the motion benefits the whole
Angle
Temporal progression / seasonal cycle
Glyph Size
Emotional charge or attention density

#🧬 Symbolic Reading
	•	The spiral mirrors the ancestral teaching: memory does not loop, it ascends in pattern.
	•	The braid represents plurality without loss of harmony — each strand maintains individuality while weaving shared rhythm.
	•	Over time, the shape itself becomes a glyph of the community’s ethical evolution — a record not of outcomes but of listening together.

⸻

🌍 Extensions (optional next steps)
	1.	Interactive resonance map — hover over points to read tags (e.g., “solstice,” “new treaty,” “storm recovery”).
	2.	Temporal rhythm analyzer — Fourier transform of magnitude series to reveal periodic emotional cycles.
	3.	Cross-field overlay — compare two communities’ Desire Streams for harmonic convergence or divergence.
	4.	Seed Glyph Export — compress a spiral segment into a symbolic glyph (SVG/JSON) for use in other sensor packs.

