
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
):
    """Render a simplified rotating lumbar spine MP4."""

    duration_seconds = max(2, int(duration_seconds))
    fps = max(2, int(fps))
    resolution = max(320, int(resolution))

    output_path = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    def ellipsoid(ax, center, radii, color):
        u = np.linspace(0, 2 * np.pi, 12)
        v = np.linspace(0, np.pi, 9)

        x = radii[0] * np.outer(
            np.cos(u), np.sin(v)
        )
        y = radii[1] * np.outer(
            np.sin(u), np.sin(v)
        )
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

    # Draw the model only once.
    levels = [0, 1.25, 2.5, 3.75, 5.0]

    for z in levels:
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

    # Intervertebral discs
    for z in [0.625, 1.875, 3.125, 4.375]:
        ellipsoid(
            ax, (0, 0, z),
            (0.65, 0.44, 0.12), "#64B5C7"
        )

    # Labels
    for label, z in zip(
        ["L5", "L4", "L3", "L2", "L1"], levels
    ):
        ax.text(
            1.30, 0, z, label,
            color="white", fontsize=8
        )

    ax.set_title(
        "LUMBAR SPINE - 3D EDUCATIONAL MODEL",
        color="white", fontsize=9, pad=8
    )

    ax.set_xlim(-1.8, 1.8)
    ax.set_ylim(-1.5, 1.3)
    ax.set_zlim(-0.7, 5.7)
    ax.set_box_aspect((3.6, 2.8, 6.4))
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
                angle = frame_index * 360 / total_frames

                # Rotate the camera, not the 3D model.
                ax.view_init(elev=15, azim=angle)
                fig.canvas.draw()

                frame = np.asarray(
                    fig.canvas.buffer_rgba()
                )[:, :, :3].copy()

                writer.append_data(frame)

    finally:
        plt.close(fig)

    return output_path
