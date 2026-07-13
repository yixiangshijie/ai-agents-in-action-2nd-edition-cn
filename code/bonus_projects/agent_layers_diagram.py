import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Wedge


def plot_agent_donut(
    highlight_label=None,
    save_prefix="donut_top_left",
    gap_span=90,  # size of the cut-out
):
    # -------- ring definitions --------
    layers = [
        ("PERSONA", "#FF6F61", 13),
        ("TOOLS & ACTIONS", "#23DFBC", 6),
        ("REASONING & PLANNING", "#0A1D3F", 4.5),
        ("KNOWLEDGE & MEMORY", "#FF8A2C", 5),
        ("EVALUATION & FEEDBACK", "#1E5BF6", 4.2),
    ]
    ring_width, gap = 0.4, 0.05
    grey = "#AAAAAA"

    # -------- arc geometry --------
    arc_start = gap_span  # 90 ° (gap begins at +X axis CCW)
    arc_end = 190  # visible all the way round to 0 °
    pad_start, pad_end = 90, 5  # show text from 180 ° … 85 °
    first_angle = arc_start + pad_start  # 180 °
    last_angle = arc_start - pad_end  # 85 °
    visible_span = first_angle - last_angle  # 95 ° → 85 ° slice

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_aspect("equal")
    ax.axis("off")

    # -------- draw each ring --------
    outer_radii = [1.0 + i * (ring_width + gap) for i in range(len(layers))]

    for (label, colour, step_deg), R in zip(layers, outer_radii):
        r0, r1 = R - ring_width, R
        fill = colour if highlight_label in (None, label) else grey

        # 270 ° visible wedge (gap is 0–90°)
        ax.add_patch(
            Wedge(
                (0, 0),
                r1,
                arc_start,
                arc_end,
                width=ring_width,
                facecolor=fill,
                edgecolor=fill,
            )
        )

        # ---- curved label ----
        max_chars = int(visible_span // step_deg) + 1
        chars = list(label)[:max_chars]  # trim if needed
        text_r = r0 + ring_width / 2

        for i, ch in enumerate(chars):
            theta = first_angle - i * step_deg
            if theta < last_angle:  # stop at buffer
                break

            x = text_r * np.cos(np.radians(theta))
            y = text_r * np.sin(np.radians(theta))
            ax.text(
                x,
                y,
                ch,
                ha="center",
                va="center",
                rotation=theta - 90,
                color="white",
                fontsize=10,
                fontweight="bold",
            )

    # -------- tidy up & save --------
    lim = outer_radii[-1] + 0.05

    ax.set_xlim(-lim, 0.05)  # x: left side only
    ax.set_ylim(-0.5, lim)  # y: top half only
    # ax.set_xlim(-lim, lim)
    # ax.set_ylim(-lim, lim)
    fig.patch.set_alpha(0)

    fig.savefig(
        f"{save_prefix}.svg",
        format="svg",
        transparent=True,
        bbox_inches="tight",
        pad_inches=0,
    )
    fig.savefig(
        f"{save_prefix}.png",
        format="png",
        dpi=300,
        transparent=True,
        bbox_inches="tight",
        pad_inches=0,
    )
    return fig


# preview
plot_agent_donut(
    highlight_label="EVALUATION & FEEDBACK", save_prefix="donut_top_left_preview"
)
plt.show()
