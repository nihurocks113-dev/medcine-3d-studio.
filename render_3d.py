
import os
import numpy as np
import imageio.v2 as imageio
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


def render_lumbar_spine(
    output_path,
    duration_seconds=8,
    fps=6,
    resolution=320,
    topic="Lumbar spine anatomy",
):
    """
    Topic-aware educational 3D prototype renderer.
    Existing render_lumbar_spine calls remain compatible.
    """

    duration_seconds = max(2, int(duration_seconds))
    fps = max(2, int(fps))
    resolution = max(320, int(resolution))

    output_path = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    topic_lower = topic.lower()

    if any(word in topic_lower for word in ["heart", "cardiac"]):
        model = "heart"
        title = "HEART ANATOMY"
    elif any(word in topic_lower for word in ["brain", "cerebr"]):
        model = "brain"
        title = "BRAIN ANATOMY"
    elif any(word in topic_lower for word in ["lung", "respiratory"]):
        model = "lungs"
        title = "LUNG ANATOMY"
    else:
        model = "spine"
        title = "LUMBAR SPINE ANATOMY"

    def ellipsoid(ax, center, radii, color):
        u = np.linspace(0, 2 * np.pi, 14)
        v = np.linspace(0, np.pi, 10)

        x = radii[0] * np.outer(np.cos(u), np.sin(v))
        y = radii[1] * np.outer(np.sin(u), np.sin(v))
        z = radii[2] * np.outer(
            np.ones_like(u), np.cos(v)
        )

        ax.plot_surface(
            x + center[0],
            y + center[1],
            z + center[2],
            color=color,
            linewidth=0,
            antialiased=False,
            shade=True,
        )

    fig = plt.figure(
        figsize=(resolution / 100, resolution / 100),
        dpi=100,
    )
    fig.patch.set_facecolor("#101827")
    ax = fig.add_subplot(111, projection="3d")
    ax.set_facecolor("#101827")

    if model == "spine":
        levels = [0, 1.25, 2.5, 3.75, 5.0]

        for i, z in enumerate(levels):
            ellipsoid(
                ax, (0, 0, z),
                (0.72, 0.50, 0.40), "#D9B38C"
            )

            for side in [-1, 1]:
                ellipsoid(
                    ax, (side * 0.48, -0.28, z),
                    (0.18, 0.18, 0.18), "#C99B70"
                )
                ellipsoid(
                    ax, (side * 0.95, -0.10, z),
                    (0.30, 0.13, 0.13), "#E8CBA8"
                )

            ellipsoid(
                ax, (0, -0.82, z),
                (0.16, 0.42, 0.14), "#E8CBA8"
            )

            ax.text(
                1.30, 0, z,
                f"L{i + 1}",
                color="white", fontsize=8,
            )

        for z in [0.625, 1.875, 3.125, 4.375]:
            ellipsoid(
                ax, (0, 0, z),
                (0.65, 0.44, 0.12), "#64B5C7"
            )

        ax.set_xlim(-1.8, 1.8)
        ax.set_ylim(-1.5, 1.3)
        ax.set_zlim(-0.7, 5.7)
        ax.set_box_aspect((3.6, 2.8, 6.4))

    elif model == "heart":
        ellipsoid(ax, (-0.38, 0, 0.1),
                  (0.55, 0.48, 0.75), "#C83E4D")
        ellipsoid(ax, (0.38, 0, 0.1),
                  (0.55, 0.48, 0.75), "#E45757")
        ellipsoid(ax, (0, 0, -0.48),
                  (0.60, 0.48, 0.58), "#B52D40")
        ax.text(0, -0.7, 0.9, "Heart model",
                color="white", ha="center")
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.3, 1.3)
        ax.set_zlim(-1.4, 1.5)
        ax.set_box_aspect((1, 1, 1.5))

    elif model == "brain":
        ellipsoid(ax, (-0.4, 0, 0),
                  (0.65, 0.65, 0.75), "#D9A7A0")
        ellipsoid(ax, (0.4, 0, 0),
                  (0.65, 0.65, 0.75), "#E6B5AC")
        ellipsoid(ax, (0, -0.05, -0.72),
                  (0.30, 0.32, 0.48), "#C98E8E")
        ax.text(0, -0.8, 1.0, "Brain model",
                color="white", ha="center")
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.5, 1.5)
        ax.set_zlim(-1.5, 1.5)
        ax.set_box_aspect((1, 1, 1))

    else:
        for side in [-1, 1]:
            ellipsoid(
                ax, (side * 0.55, 0, 0),
                (0.48, 0.42, 0.95), "#C96F77"
            )

        ellipsoid(
            ax, (0, 0, 0.75),
            (0.18, 0.18, 0.75), "#D9B38C"
        )
        ax.text(0, -0.7, 1.25, "Lung model",
                color="white", ha="center")
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.3, 1.3)
        ax.set_zlim(-1.5, 1.6)
        ax.set_box_aspect((1, 1, 1.5))

    ax.set_title(title, color="white", fontsize=10, pad=10)
    ax.set_axis_off()

    total_frames = duration_seconds * fps

    try:
        with imageio.get_writer(
            output_path,
            fps=fps,
            codec="libx264",
            macro_block_size=16,
        ) as writer:
            for frame_index in range(total_frames):
                ax.view_init(
                    elev=15,
                    azim=frame_index * 360 / total_frames,
                )
                fig.canvas.draw()

                frame = np.asarray(
                    fig.canvas.buffer_rgba()
                )[:, :, :3].copy()

                writer.append_data(frame)
    finally:
        plt.close(fig)

    return output_path
