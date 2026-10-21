
import os
import tempfile

import numpy as np
import imageio.v2 as imageio
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt


def render_lumbar_spine(
    output_path,
    duration_seconds=12,
    fps=12,
    resolution=640,
):
    """Render a simplified rotating 3D lumbar spine prototype."""

    duration_seconds = max(1, int(duration_seconds))
    fps = max(1, int(fps))
    resolution = max(320, int(resolution))

    output_path = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Approximate positions for five lumbar vertebrae.
    vertebrae = [
        (0.0, 0.0, z)
        for z in [0.0, 1.25, 2.50, 3.75, 5.0]
    ]

    def ellipsoid(ax, center, radii, color):
        u = np.linspace(0, 2 * np.pi, 18)
        v = np.linspace(0, np.pi, 12)

        x = radii[0] * np.outer(np.cos(u), np.sin(v))
        y = radii[1] * np.outer(np.sin(u), np.sin(v))
        z = radii[2] * np.outer(np.ones_like(u), np.cos(v))

        ax.plot_surface(
            x + center[0],
            y + center[1],
            z + center[2],
            color=color,
            linewidth=0,
            shade=True,
        )

    total_frames = duration_seconds * fps

    with imageio.get_writer(
        output_path,
        fps=fps,
        codec="libx264",
        macro_block_size=16,
    ) as writer:

        for frame_index in range(total_frames):
            fig = plt.figure(
                figsize=(resolution / 100, resolution / 100),
                dpi=100,
            )

            ax = fig.add_subplot(111, projection="3d")
            ax.set_facecolor("#101827")
            fig.patch.set_facecolor("#101827")

            # Vertebral bodies and simplified posterior elements.
            for x, y, z in vertebrae:
                ellipsoid(
                    ax,
                    (x, y, z),
                    (0.75, 0.52, 0.42),
                    "#D9B38C",
                )

                # Simplified pedicles.
                for side in [-1, 1]:
                    ellipsoid(
                        ax,
                        (x + side * 0.48, y - 0.30, z),
                        (0.20, 0.20, 0.20),
                        "#C99B70",
                    )

                # Posterior spinous process.
                ellipsoid(
                    ax,
                    (x, y - 0.85, z - 0.03),
                    (0.18, 0.48, 0.16),
                    "#E8CBA8",
                )

                # Transverse processes.
                for side in [-1, 1]:
                    ellipsoid(
                        ax,
                        (x + side * 0.95, y - 0.12, z),
                        (0.35, 0.14, 0.14),
                        "#E8CBA8",
                    )

            # Intervertebral discs.
            for z in [0.625, 1.875, 3.125, 4.375]:
                ellipsoid(
                    ax,
                    (0, 0, z),
                    (0.67, 0.46, 0.13),
                    "#64B5C7",
                )

            # Educational labels.
            ax.text(
                1.55, 0, 5.0,
                "L1", color="white", fontsize=9
            )
            ax.text(
                1.55, 0, 3.75,
                "L2", color="white", fontsize=9
            )
            ax.text(
                1.55, 0, 2.50,
                "L3", color="white", fontsize=9
            )
            ax.text(
                1.55, 0, 1.25,
                "L4", color="white", fontsize=9
            )
            ax.text(
                1.55, 0, 0.0,
                "L5", color="white", fontsize=9
            )

            ax.set_title(
                "LUMBAR SPINE | 3D EDUCATIONAL MODEL",
                color="white",
                fontsize=10,
                pad=12,
            )

            ax.view_init(
                elev=15,
                azim=frame_index * 360 / total_frames,
            )

            ax.set_xlim(-2, 2)
            ax.set_ylim(-1.8, 1.5)
            ax.set_zlim(-0.8, 5.8)
            ax.set_box_aspect((4, 3.3, 6.6))
            ax.set_axis_off()

            fig.tight_layout(pad=1)

            fig.canvas.draw()
            frame = np.asarray(
                fig.canvas.buffer_rgba()
            )[:, :, :3].copy()

            writer.append_data(frame)
            plt.close(fig)

    return output_path
