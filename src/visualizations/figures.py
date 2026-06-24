"""Deterministic figure generation for Realizing Emptiness."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import yaml
from matplotlib.colors import ListedColormap, TwoSlopeNorm
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Patch
from matplotlib.text import Text
from matplotlib.transforms import Bbox

from visualizations.captions import (
    write_visual_accessibility_audit,
    write_visual_caption_audit,
)
from visualizations.dashboard import write_artifact_dashboard
from visualizations.integrity import write_figure_integrity_audit
from visualizations.style import (
    MIN_READABLE_FONT_PT,
    render_contract_for,
    semantic_colors,
    write_visual_style_audits,
)


_LAYOUT_TELEMETRY: dict[str, dict[str, bool | int]] = {}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_style(project_root: Path) -> dict[str, Any]:
    with (project_root / "figures.yaml").open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _enforce_readable_text(fig: plt.Figure) -> None:
    for text in fig.findobj(match=Text):
        if not text.get_text():
            continue
        if float(text.get_fontsize()) < MIN_READABLE_FONT_PT:
            text.set_fontsize(MIN_READABLE_FONT_PT)


def _empty_layout_telemetry() -> dict[str, bool | int]:
    return {
        "text_overlap_count": 0,
        "title_overlap_count": 0,
        "cropped_text_count": 0,
        "legend_axis_overlap_count": 0,
        "layout_ok": True,
    }


def _bbox_overlap_area(left: Bbox, right: Bbox) -> float:
    width = max(0.0, min(left.x1, right.x1) - max(left.x0, right.x0))
    height = max(0.0, min(left.y1, right.y1) - max(left.y0, right.y0))
    return width * height


def _bbox_outside(inner: Bbox, outer: Bbox, *, tolerance_px: float = 1.5) -> bool:
    return (
        inner.x0 < outer.x0 - tolerance_px
        or inner.y0 < outer.y0 - tolerance_px
        or inner.x1 > outer.x1 + tolerance_px
        or inner.y1 > outer.y1 + tolerance_px
    )


def _text_layout_categories(fig: plt.Figure) -> dict[int, str]:
    categories: dict[int, str] = {}
    suptitle = getattr(fig, "_suptitle", None)
    if suptitle is not None:
        categories[id(suptitle)] = "title"
    for figure_text in getattr(fig, "texts", []):
        categories.setdefault(id(figure_text), "figure_text")
    for ax in fig.axes:
        for title in (ax.title, ax._left_title, ax._right_title):
            categories[id(title)] = "title"
        categories[id(ax.xaxis.label)] = "axis_label"
        categories[id(ax.yaxis.label)] = "axis_label"
        for tick_label in [*ax.get_xticklabels(), *ax.get_yticklabels()]:
            categories[id(tick_label)] = "tick_label"
        legend = ax.get_legend()
        if legend is not None:
            for legend_text in legend.get_texts():
                categories[id(legend_text)] = "legend_text"
    for legend in fig.legends:
        for legend_text in legend.get_texts():
            categories[id(legend_text)] = "legend_text"
    return categories


def _visible_text_boxes(fig: plt.Figure, renderer: Any) -> list[dict[str, Any]]:
    categories = _text_layout_categories(fig)
    rows: list[dict[str, Any]] = []
    for text in fig.findobj(match=Text):
        label = text.get_text().strip()
        if not text.get_visible() or not label:
            continue
        bbox = text.get_window_extent(renderer=renderer)
        if not np.all(np.isfinite(bbox.extents)):
            continue
        if bbox.width <= 0 or bbox.height <= 0:
            continue
        rows.append(
            {
                "text": label,
                "category": categories.get(id(text), "axes_text"),
                "bbox": bbox,
            }
        )
    return rows


def _legend_boxes(fig: plt.Figure, renderer: Any) -> list[Bbox]:
    boxes: list[Bbox] = []
    for ax in fig.axes:
        legend = ax.get_legend()
        if legend is not None and legend.get_visible():
            boxes.append(legend.get_window_extent(renderer=renderer))
    for legend in fig.legends:
        if legend.get_visible():
            boxes.append(legend.get_window_extent(renderer=renderer))
    return boxes


def _pairwise_overlap_count(boxes: list[Bbox], *, minimum_area_px: float = 9.0) -> int:
    count = 0
    for left_index, left in enumerate(boxes):
        for right in boxes[left_index + 1 :]:
            if _bbox_overlap_area(left, right) >= minimum_area_px:
                count += 1
    return count


def _measure_layout(fig: plt.Figure) -> dict[str, bool | int]:
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    text_boxes = _visible_text_boxes(fig, renderer)
    title_boxes = [row["bbox"] for row in text_boxes if row["category"] == "title"]
    major_text_boxes = [
        row["bbox"]
        for row in text_boxes
        if row["category"] in {"title", "axis_label", "figure_text"}
    ]
    cropped_boxes = [
        row["bbox"]
        for row in text_boxes
        if row["category"] == "figure_text" and _bbox_outside(row["bbox"], fig.bbox)
    ]
    axis_text_boxes = [
        row["bbox"] for row in text_boxes if row["category"] in {"title", "axis_label"}
    ]
    legend_axis_overlap_count = sum(
        1
        for legend_box in _legend_boxes(fig, renderer)
        for axis_box in axis_text_boxes
        if _bbox_overlap_area(legend_box, axis_box) >= 9.0
    )
    telemetry = {
        "text_overlap_count": _pairwise_overlap_count(major_text_boxes),
        "title_overlap_count": _pairwise_overlap_count(title_boxes),
        "cropped_text_count": len(cropped_boxes),
        "legend_axis_overlap_count": legend_axis_overlap_count,
        "layout_ok": False,
    }
    telemetry["layout_ok"] = all(
        int(telemetry[key]) == 0
        for key in (
            "text_overlap_count",
            "title_overlap_count",
            "cropped_text_count",
            "legend_axis_overlap_count",
        )
    )
    return telemetry


def _record_layout_telemetry(fig: plt.Figure, path: Path) -> None:
    _LAYOUT_TELEMETRY[path.stem] = _measure_layout(fig)


def _layout_rect_for(fig: plt.Figure) -> tuple[float, float, float, float] | None:
    explicit = getattr(fig, "_layout_rect", None)
    if explicit is not None:
        return explicit
    low_figure_text = any(
        text.get_visible()
        and text.get_text().strip()
        and text is not getattr(fig, "_suptitle", None)
        and text.get_position()[1] <= 0.06
        for text in getattr(fig, "texts", [])
    )
    top = 0.92 if getattr(fig, "_suptitle", None) is not None else 1.0
    bottom = 0.14 if low_figure_text else 0.0
    if top < 1.0 or bottom > 0.0:
        return (0.0, bottom, 1.0, top)
    return None


def _lift_low_figure_text(fig: plt.Figure) -> None:
    for text in getattr(fig, "texts", []):
        if text is getattr(fig, "_suptitle", None):
            continue
        if not text.get_visible() or not text.get_text().strip():
            continue
        x_pos, y_pos = text.get_position()
        value = text.get_text().strip()
        if y_pos <= 0.06 and "\n" not in value and len(value) > 85:
            text.set_text("\n".join(textwrap.wrap(value, width=95)))
            text.set_linespacing(0.9)
        if y_pos < 0.05:
            text.set_position((x_pos, 0.05))


def _wrap_axis_titles(fig: plt.Figure) -> None:
    for ax in fig.axes:
        for title in (ax.title, ax._left_title, ax._right_title):
            value = title.get_text().strip()
            if "\n" not in value and len(value) > 38:
                title.set_text("\n".join(textwrap.wrap(value, width=34)))


def _save(fig: plt.Figure, path: Path, dpi: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _enforce_readable_text(fig)
    _wrap_axis_titles(fig)
    _lift_low_figure_text(fig)
    layout_rect = _layout_rect_for(fig)
    if layout_rect is not None:
        fig.tight_layout(rect=layout_rect)
    else:
        fig.tight_layout()
    _record_layout_telemetry(fig, path)
    fig.savefig(path, dpi=dpi, bbox_inches="tight", pad_inches=0.14)
    plt.close(fig)


def _fig_path(project_root: Path, style: dict[str, Any], figure_id: str) -> Path:
    return project_root / "output" / "figures" / style["figures"][figure_id]["filename"]


def _sectorisation_map(
    project_root: Path, style: dict[str, Any], profile: dict[str, Any]
) -> Path:
    names = [row["deployment"]["name"] for row in profile["rows"]]
    labels = [row["deployment"]["sector_labels"] for row in profile["rows"]]
    vocab = {
        label: idx
        for idx, label in enumerate(sorted({item for row in labels for item in row}))
    }
    matrix = np.array([[vocab[item] for item in row] for row in labels], dtype=float)
    fig, ax = plt.subplots(figsize=(8, 2.8))
    image = ax.imshow(
        matrix, aspect="auto", cmap="tab20", vmin=-0.5, vmax=max(vocab.values()) + 0.5
    )
    ax.set_yticks(range(len(names)), names)
    ax.set_xticks(range(matrix.shape[1]), [f"b{i}" for i in range(matrix.shape[1])])
    ax.set_title("QRF sector labels by boundary channel")
    ax.set_xlabel("Boundary channel")
    handles = [
        Patch(facecolor=image.cmap(image.norm(index)), label=label)
        for label, index in sorted(vocab.items(), key=lambda row: row[1])
    ]
    ax.legend(
        handles=handles,
        title="Sector color legend",
        bbox_to_anchor=(1.01, 1.0),
        loc="upper left",
        fontsize=9,
    )
    _panel_label(ax, "A")
    return _save_return(
        fig, _fig_path(project_root, style, "qrf_sectorisation_map"), style["dpi"]
    )


def _save_return(fig: plt.Figure, path: Path, dpi: int) -> Path:
    _save(fig, path, dpi)
    return path


def _save_fixed_return(fig: plt.Figure, path: Path, dpi: int) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    _enforce_readable_text(fig)
    _wrap_axis_titles(fig)
    _lift_low_figure_text(fig)
    _record_layout_telemetry(fig, path)
    fig.savefig(path, dpi=dpi, pad_inches=0.02)
    plt.close(fig)
    return path


def _panel_label(ax: plt.Axes, label: str) -> None:
    ax.text(
        0.015,
        0.98,
        label,
        transform=ax.transAxes,
        fontsize=12.3,
        fontweight="bold",
        va="top",
        ha="left",
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.86, "pad": 1.0},
    )


def _zero_centered_norm(values: np.ndarray) -> TwoSlopeNorm | None:
    finite = np.asarray(values, dtype=float)
    finite = finite[np.isfinite(finite)]
    if finite.size == 0:
        return None
    vmin = float(np.min(finite))
    vmax = float(np.max(finite))
    if vmin < 0.0 < vmax:
        return TwoSlopeNorm(vmin=vmin, vcenter=0.0, vmax=vmax)
    return None


def _heatmap_text_color(image: Any, value: float) -> str:
    red, green, blue, _alpha = image.cmap(image.norm(value))
    luminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue
    return "#ffffff" if luminance < 0.46 else "#111827"


def _add_heatmap_cell_grid(ax: plt.Axes, row_count: int, column_count: int) -> None:
    ax.set_xticks(np.arange(-0.5, column_count, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, row_count, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.1)
    ax.tick_params(which="minor", bottom=False, left=False)


def _semantic_colors(style: dict[str, Any]) -> dict[str, str]:
    return semantic_colors()


PROFILE_DISPLAY_LABELS = {
    "separation_constrained": "Sep.",
    "opacified": "Opac.",
    "post_dual": "Post-dual",
}

PROFILE_FULL_LABELS = {
    "separation_constrained": "separation-constrained QRF",
    "opacified": "opacified QRF",
    "post_dual": "post-dual QRF",
}

PROFILE_COLOR_KEYS = {
    "separation_constrained": "primary",
    "opacified": "secondary",
    "post_dual": "accent",
}


def _profile_label(profile_name: str) -> str:
    return PROFILE_DISPLAY_LABELS.get(profile_name, profile_name.replace("_", " "))


def _compact_axis_label(label: str, max_chars: int = 15) -> str:
    if len(label) <= max_chars:
        return label
    return f"{label[: max_chars - 3]}..."


def _profile_color(style: dict[str, Any], profile_name: str) -> str:
    return style["palette"][PROFILE_COLOR_KEYS.get(profile_name, "primary")]


def _graphical_abstract_cover(project_root: Path, style: dict[str, Any]) -> Path:
    colors = _semantic_colors(style)
    fig, ax = plt.subplots(figsize=(12.6, 10.5))
    ax.set_xlim(0, 14.0)
    ax.set_ylim(0, 11.65)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.add_patch(
        FancyBboxPatch(
            (0.34, 0.34),
            13.32,
            10.92,
            boxstyle="round,pad=0.02,rounding_size=0.16",
            facecolor="#f8fafc",
            edgecolor=style["palette"]["grid"],
            linewidth=1.5,
        )
    )

    def box(
        label: str,
        x: float,
        y: float,
        width: float,
        height: float,
        color: str,
        body: str = "",
    ) -> tuple[float, float]:
        patch = FancyBboxPatch(
            (x, y),
            width,
            height,
            boxstyle="round,pad=0.04,rounding_size=0.09",
            facecolor="white",
            edgecolor=color,
            linewidth=3.2,
        )
        ax.add_patch(patch)
        ax.plot(
            [x + 0.22, x + width - 0.22],
            [y + height - 0.18, y + height - 0.18],
            color=color,
            linewidth=4.6,
            solid_capstyle="round",
        )
        ax.text(
            x + width / 2,
            y + height * 0.66,
            label,
            ha="center",
            va="center",
            fontsize=17.0,
            fontweight="bold",
            color=colors["boundary"],
            linespacing=0.82,
        )
        if body:
            ax.text(
                x + width / 2,
                y + height * 0.30,
                body,
                ha="center",
                va="center",
                fontsize=13.0,
                color=colors["boundary"],
                linespacing=0.9,
            )
        return (x + width / 2, y + height / 2)

    box(
        "Source Paper",
        0.88,
        8.24,
        3.82,
        1.42,
        colors["source"],
        "no-self evidence\nformal target",
    )
    box(
        "Finite Layer",
        9.30,
        8.24,
        3.82,
        1.42,
        colors["finite"],
        "equations 1-14\nQRF/BMR/qFEP",
    )
    box(
        "Simulation\nEngines",
        9.30,
        1.22,
        3.82,
        1.42,
        colors["stochastic"],
        "seeded software\nnot empirical",
    )
    box(
        "Claim\nGates",
        0.88,
        1.22,
        3.82,
        1.42,
        colors["blocked"],
        "ceilings + audits\nblock stronger claims",
    )

    center = (7.0, 6.0)
    ax.add_patch(
        Circle(
            center,
            2.28,
            edgecolor=style["palette"]["grid"],
            facecolor="white",
            linewidth=12.0,
            alpha=0.55,
        )
    )
    ax.add_patch(
        Circle(
            center,
            1.86,
            edgecolor=colors["boundary"],
            facecolor="#f8fafc",
            linewidth=3.0,
            linestyle="--",
        )
    )
    ax.add_patch(
        Circle(
            center, 0.76, edgecolor=colors["finite"], facecolor="white", linewidth=3.0
        )
    )
    node_colors = {
        "self": "#111827",
        "env": "#2563eb",
        "action": "#92400e",
        "body": "#7c3aed",
        "world": "#0f766e",
        "other": "#be123c",
    }
    positions = [
        (5.20, 6.35),
        (6.20, 7.55),
        (7.80, 7.55),
        (8.80, 6.35),
        (8.15, 4.62),
        (5.85, 4.62),
    ]
    labels = ["self", "env", "action", "body", "world", "other"]
    label_offsets = {
        "self": (-0.42, 0.0, "right", "center"),
        "env": (-0.14, -0.44, "right", "top"),
        "action": (0.14, -0.44, "left", "top"),
        "body": (0.45, 0.0, "left", "center"),
        "world": (0.45, -0.02, "left", "center"),
        "other": (-0.45, -0.02, "right", "center"),
    }
    for idx, ((x, y), label) in enumerate(zip(positions, labels, strict=True)):
        ax.plot(
            [center[0], x],
            [center[1], y],
            color=style["palette"]["grid"],
            linewidth=1.8,
        )
        ax.add_patch(
            Circle(
                (x, y),
                0.36,
                facecolor=node_colors[label],
                edgecolor="white",
                linewidth=1.5,
            )
        )
        dx, dy, ha, va = label_offsets[label]
        ax.text(
            x + dx,
            y + dy,
            f"b{idx}: {label}",
            ha=ha,
            va=va,
            fontsize=13.4,
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.86, "pad": 0.7},
        )
    ax.text(
        center[0],
        center[1],
        "finite\nboundary\nbitstream",
        ha="center",
        va="center",
        fontsize=15.3,
        fontweight="bold",
        linespacing=0.88,
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.86, "pad": 0.8},
    )

    ribbon_y = [3.92, 3.58, 3.24]
    ribbon_labels = ["separation\nconstrained", "opacified", "post-dual"]
    ribbon_segments = [
        ["self", "env", "action", "body", "world", "other"],
        ["env", "env", "action", "action", "other", "other"],
        ["care", "env", "world", "world", "other", "other"],
    ]
    ribbon_color = {**node_colors, "care": "#16a34a"}
    for row_y, row_label, segments in zip(
        ribbon_y, ribbon_labels, ribbon_segments, strict=True
    ):
        ax.text(
            4.94,
            row_y + 0.04,
            row_label,
            ha="right",
            va="center",
            fontsize=13.0,
            color=colors["boundary"],
            linespacing=0.86,
        )
        for idx, segment in enumerate(segments):
            ax.add_patch(
                plt.Rectangle(
                    (5.14 + idx * 0.59, row_y - 0.085),
                    0.52,
                    0.18,
                    facecolor=ribbon_color[segment],
                    edgecolor="white",
                    linewidth=0.45,
                )
            )
    ax.text(
        7.0,
        2.84,
        "Relabelings license use, not ontology.",
        ha="center",
        va="center",
        fontsize=14.5,
        fontweight="bold",
        bbox={"facecolor": "white", "edgecolor": style["palette"]["grid"], "alpha": 0.96, "pad": 2.1},
    )

    arrow_specs = [
        ((4.62, 8.42), (5.50, 7.16), 0.09),
        ((9.38, 8.42), (8.50, 7.16), -0.09),
        ((8.72, 2.64), (9.42, 2.23), 0.18),
        ((5.28, 2.64), (4.58, 2.23), -0.18),
    ]
    for start, end, curve in arrow_specs:
        ax.add_patch(
            FancyArrowPatch(
                start,
                end,
                arrowstyle="->",
                mutation_scale=23,
                linewidth=2.5,
                color=colors["boundary"],
                connectionstyle=f"arc3,rad={curve}",
            )
        )

    ax.text(
        7.0,
        10.72,
        "Realizing Emptiness",
        ha="center",
        va="center",
        fontsize=31,
        fontweight="bold",
        color=colors["boundary"],
    )
    ax.text(
        7.0,
        10.27,
        "Source-bounded software for QRF relabeling, stochastic validation, and evidence ceilings",
        ha="center",
        va="center",
        fontsize=14.5,
        color=style["palette"]["muted"],
    )
    legend = [
        Patch(facecolor="white", edgecolor=colors["source"], label="source contract"),
        Patch(facecolor="white", edgecolor=colors["finite"], label="finite artifact"),
        Patch(
            facecolor="white", edgecolor=colors["stochastic"], label="seeded simulation"
        ),
        Patch(
            facecolor="white",
            edgecolor=colors["blocked"],
            label="blocked stronger claim",
        ),
        Line2D(
            [0], [0], color=colors["boundary"], linestyle="--", label="boundary screen"
        ),
    ]
    ax.legend(
        handles=legend,
        loc="center",
        bbox_to_anchor=(0.5, 0.025),
        ncol=5,
        frameon=True,
        fontsize=11.0,
        handlelength=1.35,
        borderpad=0.38,
        labelspacing=0.3,
        columnspacing=0.9,
    )
    return _save_fixed_return(
        fig, _fig_path(project_root, style, "graphical_abstract_cover"), style["dpi"]
    )


def _qrf_sector_colors() -> dict[str, str]:
    return {
        "self": "#111827",
        "env": "#2563eb",
        "action": "#92400e",
        "body": "#7c3aed",
        "world": "#0f766e",
        "other": "#be123c",
        "care": "#16a34a",
    }


def _qrf_boundary_screen_geometry(
    project_root: Path,
    style: dict[str, Any],
    profile: dict[str, Any],
    audit: dict[str, Any],
    ledger: dict[str, Any],
) -> Path:
    colors = _semantic_colors(style)
    sector_colors = _qrf_sector_colors()
    fig, ax = plt.subplots(figsize=(10.8, 6.2))
    ax.set_xlim(-2.0, 7.1)
    ax.set_ylim(-1.15, 5.1)
    ax.axis("off")

    center = (2.75, 2.2)
    ax.add_patch(
        Circle(
            center,
            1.62,
            edgecolor=colors["boundary"],
            facecolor="#f8fafc",
            linewidth=2.0,
            linestyle="--",
        )
    )
    ax.add_patch(
        Circle(
            center, 0.62, edgecolor=colors["finite"], facecolor="white", linewidth=1.8
        )
    )
    positions = [
        (1.45, 3.25),
        (2.2, 4.05),
        (3.45, 3.92),
        (4.34, 2.55),
        (3.55, 0.65),
        (1.35, 0.78),
    ]
    for channel, (x_pos, y_pos) in zip(ledger["rows"], positions, strict=True):
        sector = channel["sector_labels_by_profile"]["post_dual"]
        ax.plot(
            [center[0], x_pos],
            [center[1], y_pos],
            color=style["palette"]["grid"],
            linewidth=1.0,
        )
        ax.add_patch(
            Circle(
                (x_pos, y_pos),
                0.25,
                facecolor="white",
                edgecolor=sector_colors[sector],
                linewidth=2.0,
            )
        )
        ax.text(
            x_pos,
            y_pos,
            channel["channel_id"],
            ha="center",
            va="center",
            fontsize=11.8,
            fontweight="bold",
        )
        role = channel["finite_surrogate_role"].replace(" cue", "")
        offset_x = -0.52 if x_pos < center[0] else 0.52
        offset_y = 0.24 if y_pos >= center[1] else -0.24
        ax.text(
            x_pos + offset_x,
            y_pos + offset_y,
            "\n".join(textwrap.wrap(role, width=16)),
            ha="right" if offset_x < 0 else "left",
            va="center",
            fontsize=9,
            color=style["palette"]["muted"],
            linespacing=0.95,
        )
    ax.text(
        center[0],
        center[1],
        "finite\nboundary\nscreen",
        ha="center",
        va="center",
        fontsize=12.9,
        fontweight="bold",
    )
    ax.add_patch(
        FancyArrowPatch(
            (-1.35, 2.2),
            (1.02, 2.2),
            arrowstyle="->",
            mutation_scale=18,
            color=style["palette"]["warning"],
            linewidth=2.2,
        )
    )
    ax.add_patch(
        FancyArrowPatch(
            (4.58, 2.2),
            (6.45, 2.2),
            arrowstyle="->",
            mutation_scale=18,
            color=style["palette"]["secondary"],
            linewidth=2.2,
        )
    )
    ax.text(
        -1.38,
        2.55,
        "action selects transition",
        fontsize=11.2,
        color=style["palette"]["warning"],
        fontweight="bold",
    )
    ax.text(
        4.98,
        2.55,
        "observation emits bitstream",
        fontsize=11.2,
        color=style["palette"]["secondary"],
        fontweight="bold",
    )
    ax.text(
        2.75,
        -0.62,
        f"{len(ledger['rows'])} software channels; {len(profile['rows'])} admissible QRF deployments; "
        f"negative control fails = {audit['negative_control_fails']}",
        ha="center",
        va="center",
        fontsize=10.4,
        color=colors["boundary"],
        bbox={"facecolor": "white", "edgecolor": style["palette"]["grid"], "pad": 2.0},
    )
    handles = [
        Line2D(
            [0],
            [0],
            color=colors["boundary"],
            linestyle="--",
            linewidth=2.0,
            label="finite boundary screen",
        ),
        Line2D(
            [0],
            [0],
            color=style["palette"]["warning"],
            linewidth=2.2,
            label="action edge",
        ),
        Line2D(
            [0],
            [0],
            color=style["palette"]["secondary"],
            linewidth=2.2,
            label="observation edge",
        ),
        Patch(
            facecolor="white", edgecolor=colors["finite"], label="boundary channel b_i"
        ),
    ]
    ax.legend(handles=handles, loc="upper right", frameon=True, fontsize=10.1)
    ax.set_title(
        "Finite boundary screen: action and observation without ontological proof",
        fontsize=15.1,
        fontweight="bold",
    )
    return _save_return(
        fig,
        _fig_path(project_root, style, "qrf_boundary_screen_geometry"),
        style["dpi"],
    )


def _qrf_channel_relabeling_ledger(
    project_root: Path, style: dict[str, Any], ledger: dict[str, Any]
) -> Path:
    colors = _semantic_colors(style)
    sector_colors = _qrf_sector_colors()
    fig, ax = plt.subplots(figsize=(13.2, 5.6))
    ax.set_xlim(-1.55, 7.95)
    ax.set_ylim(-0.75, 5.05)
    ax.axis("off")
    row_labels = [
        "channel\nrole",
        "evidenced\nbitstream",
        "separation\nconstrained",
        "opacified",
        "post-dual",
    ]
    channel_rows = ledger["rows"]
    profile_names = ledger["profiles"]
    cell_width = 1.08
    cell_height = 0.70
    x0 = 0.18
    y_top = 3.82
    for column, row in enumerate(channel_rows):
        x_pos = x0 + column * cell_width
        ax.text(
            x_pos + cell_width / 2,
            4.62,
            row["channel_id"],
            ha="center",
            va="bottom",
            fontsize=13,
            fontweight="bold",
        )
        role = "\n".join(
            textwrap.wrap(row["finite_surrogate_role"].replace(" cue", ""), width=12)
        )
        ax.add_patch(
            plt.Rectangle(
                (x_pos, y_top),
                cell_width,
                cell_height,
                facecolor="#f8fafc",
                edgecolor=style["palette"]["grid"],
                linewidth=0.75,
            )
        )
        ax.text(
            x_pos + cell_width / 2,
            y_top + cell_height / 2,
            role,
            ha="center",
            va="center",
            fontsize=9,
            color=style["palette"]["muted"],
            linespacing=0.9,
        )
        evidence_y = y_top - cell_height
        ax.add_patch(
            plt.Rectangle(
                (x_pos, evidence_y),
                cell_width,
                cell_height,
                facecolor="white",
                edgecolor=style["palette"]["primary"],
                linewidth=0.75,
            )
        )
        ax.text(
            x_pos + cell_width / 2,
            evidence_y + cell_height / 2,
            f"{row['channel_id']}\nsame bit",
            ha="center",
            va="center",
            fontsize=10.1,
            fontweight="bold",
        )
        ax.text(
            x_pos + cell_width - 0.08,
            evidence_y + cell_height - 0.12,
            "=",
            ha="center",
            va="center",
            fontsize=12.3,
            color=colors["pass"],
            fontweight="bold",
        )
        for profile_index, profile_name in enumerate(profile_names, start=1):
            y_pos = y_top - (profile_index + 1) * cell_height
            sector = row["sector_labels_by_profile"][profile_name]
            ax.add_patch(
                plt.Rectangle(
                    (x_pos, y_pos),
                    cell_width,
                    cell_height,
                    facecolor=sector_colors[sector],
                    edgecolor="white",
                    linewidth=0.9,
                )
            )
            text_color = (
                "white"
                if sector in {"self", "env", "action", "body", "world", "other"}
                else style["palette"]["primary"]
            )
            ax.text(
                x_pos + cell_width / 2,
                y_pos + cell_height / 2,
                sector,
                ha="center",
                va="center",
                fontsize=9,
                color=text_color,
                fontweight="bold",
            )
    for index, label in enumerate(row_labels):
        y_pos = y_top - index * cell_height + cell_height / 2
        ax.text(
            -0.1,
            y_pos,
            label,
            ha="right",
            va="center",
            fontsize=9,
            fontweight="bold" if index == 0 else "normal",
        )
    ax.text(
        3.42,
        -0.12,
        "Equations 7-10: Q relabels b_i; P(o|Q_i)=P(o|Q_j); sigma restricts admissible Q_sigma.",
        ha="center",
        va="center",
        fontsize=10.1,
        color=style["palette"]["primary"],
        bbox={"facecolor": "white", "edgecolor": style["palette"]["grid"], "pad": 1.5},
    )
    ax.set_title(
        "b0-b5 channel ledger: same bits, different QRF labels",
        fontsize=15.1,
        fontweight="bold",
    )
    handles = [
        Patch(
            facecolor="white",
            edgecolor=style["palette"]["primary"],
            label="same evidenced bit b_i",
        ),
        *[
            Patch(facecolor=color, label=label)
            for label, color in sector_colors.items()
        ],
    ]
    ax.legend(
        handles=handles,
        title="Sector legend",
        bbox_to_anchor=(1.01, 1.0),
        loc="upper left",
        fontsize=9,
    )
    return _save_return(
        fig,
        _fig_path(project_root, style, "qrf_channel_relabeling_ledger"),
        style["dpi"],
    )


def _qrf_invariance_policy_flow(
    project_root: Path,
    style: dict[str, Any],
    profile: dict[str, Any],
    audit: dict[str, Any],
) -> Path:
    colors = _semantic_colors(style)
    fig, axes = plt.subplots(
        1, 2, figsize=(14.2, 5.3), gridspec_kw={"width_ratios": [1.0, 1.15]}
    )

    ax = axes[0]
    values = [row["marginal_probability_sum"] for row in audit["rows"]]
    names = [row["deployment"]["name"] for row in audit["rows"]]
    x = np.arange(len(names))
    ax.bar(x, values, color=colors["pass"], label="admissible QRF mass")
    ax.axhline(
        1.0,
        color=colors["boundary"],
        linestyle="--",
        linewidth=1.2,
        label="normalized target",
    )
    ax.scatter(
        [len(names) + 0.18],
        [1.0],
        marker="x",
        color=colors["fail"],
        s=160,
        linewidths=2.4,
        label="perturbed control fails",
    )
    ax.text(
        len(names) + 0.18,
        0.83,
        "negative\ncontrol\nfails",
        ha="center",
        va="top",
        fontsize=9,
        color=colors["fail"],
        fontweight="bold",
    )
    ax.set_ylim(0, 1.15)
    ax.set_xlim(-0.6, len(names) + 0.7)
    ax.set_ylabel("Probability mass")
    ax.set_xticks(x, [_profile_label(name) for name in names], rotation=0)
    ax.set_title(
        "Admissible relabelings preserve the bitstream distribution",
        fontsize=13.2,
        fontweight="bold",
    )
    ax.legend(fontsize=9, loc="lower left")
    for index, value in enumerate(values):
        ax.text(
            index, value + 0.035, f"{value:.2f}", ha="center", va="bottom", fontsize=9
        )
    _panel_label(ax, "A")

    ax = axes[1]
    action_labels = list(profile["action_labels"])
    left = np.zeros(len(profile["rows"]))
    action_palette = [
        style["palette"]["warning"],
        style["palette"]["secondary"],
        style["palette"]["accent"],
    ]
    y = np.arange(len(profile["rows"]))
    for action_index, action in enumerate(action_labels):
        values = [row["action_counts"].get(action, 0) for row in profile["rows"]]
        ax.barh(y, values, left=left, color=action_palette[action_index], label=action)
        left += np.asarray(values)
    ax.set_yticks(
        y, [_profile_label(row["deployment"]["name"]) for row in profile["rows"]]
    )
    ax.set_xlabel("Selected actions across deterministic pymdp trace")
    ax.set_title(
        "Policy selection changes while the audited screen stays fixed",
        fontsize=13.2,
        fontweight="bold",
    )
    ax.invert_yaxis()
    ax.legend(
        title="Action legend", bbox_to_anchor=(1.02, 1.0), loc="upper left", fontsize=9
    )
    for row_index, total in enumerate(left):
        ax.text(
            total - 0.25,
            row_index,
            f"{int(total)} steps",
            va="center",
            ha="right",
            fontsize=9,
            color="white",
            fontweight="bold",
        )
    _panel_label(ax, "B")

    fig.suptitle(
        "QRF invariance and policy flow: same screen, different policies",
        fontsize=15.1,
        fontweight="bold",
    )
    return _save_return(
        fig, _fig_path(project_root, style, "qrf_invariance_policy_flow"), style["dpi"]
    )


def _finite_quantum_scope_summary(
    project_root: Path, style: dict[str, Any], readiness: dict[str, Any]
) -> Path:
    colors = _semantic_colors(style)
    groups = [
        (
            "entropy\nseparability",
            "two-qubit\nentropy",
            "product/Bell\ncontrols",
            "physical\nboundary",
        ),
        (
            "contextuality\ncovers",
            "CHSH + LP\nfinite covers",
            "local/no-signaling\ncontrols",
            "all QRF\ncontexts",
        ),
        (
            "open-system\ntrajectories",
            "Lindblad + MCWF\nsurrogates",
            "trace/PSD/\nconvergence",
            "physical\nqFEP",
        ),
        (
            "many-body\ncosts",
            "cut sweeps +\nCPTP costs",
            "separable/non-CPTP\ncontrols",
            "observer\nproof",
        ),
        (
            "roadmap\nadapters",
            "readiness +\nprovenance gates",
            "blocked-row\ncontrols",
            "human/practice\nevidence",
        ),
    ]
    columns = [
        "finite\nengine",
        "negative\ncontrols",
        "allowed\nclaim",
        "blocked\nclaim",
    ]
    matrix = np.tile(np.array([1.0, 1.0, 1.0, 0.0]), (len(groups), 1))
    fig, ax = plt.subplots(figsize=(10.4, 5.4))
    cmap = ListedColormap(["#fef3c7", "#d1fae5"])
    ax.imshow(matrix, aspect="auto", cmap=cmap, vmin=0, vmax=1)
    ax.set_xticks(range(len(columns)), columns)
    ax.set_yticks(range(len(groups)), [group[0] for group in groups])
    ax.tick_params(axis="both", labelsize=9)
    for y_idx, (_, validates, controls, blocked) in enumerate(groups):
        values = [validates, controls, "finite\nsurrogate", blocked]
        for x_idx, value in enumerate(values):
            ax.text(
                x_idx,
                y_idx,
                value,
                ha="center",
                va="center",
                fontsize=9,
                color=colors["blocked"] if x_idx == 3 else style["palette"]["primary"],
                bbox={
                    "facecolor": "#fef3c7",
                    "edgecolor": "none",
                    "alpha": 0.92,
                    "pad": 0.3,
                }
                if x_idx == 3
                else None,
            )
        ax.add_patch(
            plt.Rectangle(
                (2.5, y_idx - 0.5),
                1.0,
                1.0,
                fill=False,
                edgecolor=colors["blocked"],
                hatch="..",
                linewidth=0.0,
            )
        )
    fig.suptitle(
        "Finite quantum scope summary: what is validated, what remains blocked",
        fontsize=14.6,
    )
    ax.set_title(
        f"{readiness.get('implemented_count', 0)} finite engines; "
        f"{readiness.get('future_count', 0)} external-evidence classes blocked",
        fontsize=9,
        color=style["palette"]["muted"],
        pad=8,
    )
    handles = [
        Patch(
            facecolor="#d1fae5",
            edgecolor=style["palette"]["grid"],
            label="finite artifact or gate present",
        ),
        Patch(
            facecolor="#fef3c7",
            edgecolor=colors["blocked"],
            hatch="..",
            label="stronger empirical/physical claim blocked",
        ),
    ]
    ax.legend(
        handles=handles,
        title="Scope legend",
        bbox_to_anchor=(0.5, -0.16),
        loc="upper center",
        ncol=2,
        fontsize=9,
    )
    _panel_label(ax, "Q")
    return _save_return(
        fig,
        _fig_path(project_root, style, "finite_quantum_scope_summary"),
        style["dpi"],
    )


def _binary_colorbar(fig: plt.Figure, image, ax: plt.Axes, label: str) -> None:
    colorbar = fig.colorbar(image, ax=ax, fraction=0.035, pad=0.02)
    colorbar.set_ticks([0, 1])
    colorbar.set_ticklabels(["absent", "present"])
    colorbar.set_label(label)


def _binary_colorbar_unlabeled(fig: plt.Figure, image, ax: plt.Axes) -> None:
    colorbar = fig.colorbar(image, ax=ax, fraction=0.035, pad=0.02)
    colorbar.set_ticks([0, 1])
    colorbar.set_ticklabels(["absent", "present"])


def _boundary_audit(
    project_root: Path, style: dict[str, Any], audit: dict[str, Any]
) -> Path:
    fig, ax = plt.subplots(figsize=(8.4, 3.8))
    values = [row["marginal_probability_sum"] for row in audit["rows"]]
    names = [row["deployment"]["name"] for row in audit["rows"]]
    x = np.arange(len(names))
    ax.bar(
        x,
        values,
        color=style["palette"]["secondary"],
        edgecolor=style["palette"]["primary"],
        linewidth=0.5,
    )
    ax.axhline(1.0, color=style["palette"]["accent"], linestyle="--", linewidth=1.2)
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("Probability mass")
    ax.set_title("Admissible QRF labels preserve boundary distribution")
    ax.set_xticks(x, [_profile_label(name) for name in names])
    ax.grid(axis="y", color=style["palette"]["grid"], linewidth=0.5, alpha=0.55)
    for index, value in enumerate(values):
        ax.text(
            index, value + 0.035, f"{value:.2f}", ha="center", va="bottom", fontsize=9
        )
    ax.legend(
        handles=[
            Patch(
                color=style["palette"]["secondary"], label="profile probability mass"
            ),
            Line2D(
                [0],
                [0],
                color=style["palette"]["accent"],
                linestyle="--",
                label="normalized target",
            ),
        ],
        fontsize=9,
        loc="lower right",
    )
    _panel_label(ax, "B")
    return _save_return(
        fig,
        _fig_path(project_root, style, "boundary_indistinguishability"),
        style["dpi"],
    )


def _qrf_reference_frame_geometry(
    project_root: Path,
    style: dict[str, Any],
    profile: dict[str, Any],
    audit: dict[str, Any],
) -> Path:
    deployments = [row["deployment"] for row in profile["rows"]]
    sector_colors = {
        "self": "#111827",
        "env": "#2563eb",
        "action": "#92400e",
        "body": "#7c3aed",
        "world": "#0f766e",
        "other": "#be123c",
        "care": "#16a34a",
    }
    fig, ax = plt.subplots(figsize=(11.2, 6.2))
    ax.set_xlim(-1.25, 10.45)
    ax.set_ylim(-1.72, 5.35)
    ax.axis("off")
    center = (4.5, 2.4)
    channel_positions = [
        (2.1, 4.1),
        (3.2, 4.6),
        (5.7, 4.55),
        (6.9, 4.05),
        (7.15, 1.15),
        (2.0, 1.05),
    ]
    boundary = Circle(
        center,
        2.35,
        edgecolor=style["palette"]["muted"],
        facecolor="none",
        linewidth=1.8,
        linestyle="--",
    )
    ax.add_patch(boundary)
    ax.text(
        center[0],
        center[1],
        "finite boundary\nscreen",
        ha="center",
        va="center",
        fontsize=11.8,
        fontweight="bold",
    )
    ax.text(
        0.1,
        2.4,
        "action\nselection",
        ha="center",
        va="center",
        fontsize=10.5,
        color=style["palette"]["warning"],
        fontweight="bold",
    )
    ax.text(
        9.2,
        2.4,
        "observation\ncue",
        ha="center",
        va="center",
        fontsize=10.5,
        color=style["palette"]["secondary"],
        fontweight="bold",
    )
    ax.add_patch(
        FancyArrowPatch(
            (0.7, 2.4),
            (2.0, 2.4),
            arrowstyle="->",
            mutation_scale=12,
            color=style["palette"]["warning"],
            linewidth=1.5,
        )
    )
    ax.add_patch(
        FancyArrowPatch(
            (7.0, 2.4),
            (8.5, 2.4),
            arrowstyle="->",
            mutation_scale=12,
            color=style["palette"]["secondary"],
            linewidth=1.5,
        )
    )
    for idx, (x_pos, y_pos) in enumerate(channel_positions):
        ax.add_patch(
            Circle(
                (x_pos, y_pos),
                0.22,
                facecolor="white",
                edgecolor=style["palette"]["primary"],
                linewidth=1.2,
            )
        )
        ax.text(x_pos, y_pos, f"b{idx}", ha="center", va="center", fontsize=9)
        ax.plot(
            [center[0], x_pos],
            [center[1], y_pos],
            color=style["palette"]["grid"],
            linewidth=0.8,
        )
    y_rows = [-0.35, -0.72, -1.09]
    for row_idx, deployment in enumerate(deployments):
        ax.text(
            -0.95,
            y_rows[row_idx],
            _profile_label(deployment["name"]),
            ha="left",
            va="center",
            fontsize=9,
            fontweight="bold",
        )
        for col_idx, label in enumerate(deployment["sector_labels"]):
            x_pos = 2.0 + col_idx * 0.78
            color = sector_colors.get(label, "#64748b")
            ax.add_patch(
                Circle(
                    (x_pos, y_rows[row_idx]),
                    0.13,
                    facecolor=color,
                    edgecolor="white",
                    linewidth=0.5,
                )
            )
            ax.text(
                x_pos,
                y_rows[row_idx] - 0.26,
                label[:4],
                ha="center",
                va="top",
                fontsize=9,
            )
    ax.text(
        4.5,
        0.25,
        "same b0-b5 screen; QRF rows relabel sectors only",
        fontsize=10.3,
        ha="center",
        fontweight="bold",
    )
    ax.text(
        4.5,
        -0.08,
        f"audited distribution preserved; negative control fails: {audit['negative_control_fails']}",
        fontsize=9,
        ha="center",
        color=style["palette"]["accent"],
    )
    legend_labels = sorted(
        {label for deployment in deployments for label in deployment["sector_labels"]}
    )
    handles = [
        Patch(facecolor=sector_colors.get(label, "#64748b"), label=label)
        for label in legend_labels
    ]
    handles.extend(
        [
            Line2D(
                [0],
                [0],
                color=style["palette"]["muted"],
                linestyle="--",
                label="boundary screen",
            ),
            Line2D(
                [0],
                [0],
                color=style["palette"]["warning"],
                marker=">",
                label="action edge",
            ),
            Line2D(
                [0],
                [0],
                color=style["palette"]["secondary"],
                marker=">",
                label="observation edge",
            ),
        ]
    )
    ax.legend(
        handles=handles, title="Sector and edge legend", loc="lower right", fontsize=9
    )
    _panel_label(ax, "C")
    ax.set_title("QRF reference-frame geometry over a finite boundary screen")
    return _save_return(
        fig,
        _fig_path(project_root, style, "qrf_reference_frame_geometry"),
        style["dpi"],
    )


def _bmr_decomposition(
    project_root: Path, style: dict[str, Any], bmr: dict[str, Any]
) -> Path:
    rows = [row for row in bmr["rows"] if row["prior_precision"] == 4.0]
    x = [row["metacognitive_access"] for row in rows]
    delta_f = [row["delta_free_energy"] for row in rows]
    delta_c = [row["delta_complexity"] for row in rows]
    delta_a = [row["delta_accuracy"] for row in rows]
    fig, ax = plt.subplots(figsize=(9.4, 5.2))
    series = [
        (delta_f, "Delta F", style["palette"]["primary"], "o"),
        (delta_c, "Delta complexity", style["palette"]["secondary"], "s"),
        (delta_a, "Delta accuracy", style["palette"]["accent"], "^"),
    ]
    for values, label, color, marker in series:
        ax.plot(
            x,
            values,
            marker=marker,
            label=label,
            color=color,
            linewidth=2.2,
            markersize=6.5,
        )
    ax.axhline(
        0,
        color=style["palette"]["muted"],
        linewidth=1.3,
        linestyle="--",
        label="keep/prune boundary",
    )
    ax.text(
        max(x),
        0.08,
        "Delta F < 0 favors prune",
        ha="right",
        va="bottom",
        fontsize=9,
        color=style["palette"]["muted"],
        bbox={
            "facecolor": "white",
            "edgecolor": style["palette"]["grid"],
            "alpha": 0.92,
            "pad": 2.0,
        },
    )
    ax.set_xlabel("Metacognitive access")
    ax.set_ylabel("Reduced-minus-full value")
    ax.set_xlim(min(x) - 0.03, max(x) + 0.03)
    ax.grid(axis="y", color=style["palette"]["grid"], linewidth=0.5, alpha=0.6)
    ax.set_title("BMR free-energy components at prior precision 4.0")
    ax.legend(title="Line and threshold legend", fontsize=9, loc="center right")
    _panel_label(ax, "D")
    return _save_return(
        fig,
        _fig_path(project_root, style, "bmr_free_energy_decomposition"),
        style["dpi"],
    )


def _bmr_phase_diagram(
    project_root: Path, style: dict[str, Any], bmr: dict[str, Any]
) -> Path:
    colors = _semantic_colors(style)
    rows = bmr["rows"]
    accesses = sorted({row["metacognitive_access"] for row in rows})
    precisions = sorted({row["prior_precision"] for row in rows})
    matrix = np.zeros((len(precisions), len(accesses)))
    prune = np.zeros_like(matrix, dtype=bool)
    lookup = {
        (row["prior_precision"], row["metacognitive_access"]): row for row in rows
    }
    for p_idx, precision in enumerate(precisions):
        for a_idx, access in enumerate(accesses):
            row = lookup[(precision, access)]
            matrix[p_idx, a_idx] = row["delta_free_energy"]
            prune[p_idx, a_idx] = row["prunes_prior"]
    fig, ax = plt.subplots(figsize=(10.8, 5.9))
    image = ax.imshow(
        matrix, aspect="auto", cmap="RdBu_r", norm=_zero_centered_norm(matrix)
    )
    for p_idx in range(len(precisions)):
        for a_idx in range(len(accesses)):
            value = matrix[p_idx, a_idx]
            decision = "PRUNE prior" if prune[p_idx, a_idx] else "KEEP prior"
            ax.text(
                a_idx,
                p_idx,
                f"{decision}\nDF {value:+.2f}",
                ha="center",
                va="center",
                fontsize=9,
                color=_heatmap_text_color(image, value),
                fontweight="bold",
            )
    ax.set_xticks(range(len(accesses)), [f"{value:.2g}" for value in accesses])
    ax.set_yticks(range(len(precisions)), [f"{value:.2g}" for value in precisions])
    _add_heatmap_cell_grid(ax, len(precisions), len(accesses))
    ax.set_xlabel("Metacognitive access")
    ax.set_ylabel("Separation-prior precision")
    ax.set_title("BMR decision grid: keep or prune the separation prior")
    cbar = fig.colorbar(
        image, ax=ax, label="Delta F = F_reduced - F_full; negative favors PRUNE prior"
    )
    cbar.ax.axhline(0.0, color="white", linewidth=1.4)
    ax.legend(
        handles=[
            Patch(
                facecolor=colors["keep"],
                label="KEEP prior: full model still earns its complexity",
            ),
            Patch(
                facecolor=colors["prune"],
                label="PRUNE prior: reduced model lowers free energy",
            ),
        ],
        title="Decision rule",
        fontsize=9,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.17),
        ncol=1,
    )
    _panel_label(ax, "E")
    return _save_return(
        fig, _fig_path(project_root, style, "bmr_pruning_phase_diagram"), style["dpi"]
    )


def _simulation_sensitivity_heatmap(
    project_root: Path, style: dict[str, Any], sensitivity: dict[str, Any]
) -> Path:
    rows = sensitivity["rows"]
    accesses = sorted({row["metacognitive_access"] for row in rows})
    precisions = sorted({row["prior_precision"] for row in rows})
    matrix = np.zeros((len(precisions), len(accesses)))
    prune_rate = np.zeros_like(matrix)
    prune_count = np.zeros_like(matrix, dtype=int)
    noise_count = np.zeros_like(matrix, dtype=int)
    for p_idx, precision in enumerate(precisions):
        for a_idx, access in enumerate(accesses):
            subset = [
                row
                for row in rows
                if row["prior_precision"] == precision
                and row["metacognitive_access"] == access
            ]
            matrix[p_idx, a_idx] = float(
                np.mean([row["delta_free_energy"] for row in subset])
            )
            pruned_rows = sum(1 for row in subset if row["prunes_prior"])
            noise_count[p_idx, a_idx] = len(subset)
            prune_count[p_idx, a_idx] = pruned_rows
            prune_rate[p_idx, a_idx] = float(pruned_rows / len(subset))
    fig, ax = plt.subplots(figsize=(10.2, 5.4))
    image = ax.imshow(
        matrix, aspect="auto", cmap="RdBu_r", norm=_zero_centered_norm(matrix)
    )
    for p_idx in range(len(precisions)):
        for a_idx in range(len(accesses)):
            value = matrix[p_idx, a_idx]
            ax.text(
                a_idx,
                p_idx,
                f"{prune_count[p_idx, a_idx]}/{noise_count[p_idx, a_idx]} noise rows\nfavor PRUNE",
                ha="center",
                va="center",
                fontsize=8.5,
                color=_heatmap_text_color(image, value),
                fontweight="bold",
            )
    ax.set_xticks(range(len(accesses)), [f"{value:.2g}" for value in accesses])
    ax.set_yticks(range(len(precisions)), [f"{value:.2g}" for value in precisions])
    _add_heatmap_cell_grid(ax, len(precisions), len(accesses))
    ax.set_xlabel("Metacognitive access")
    ax.set_ylabel("Separation-prior precision")
    ax.set_title("Sensitivity grid: mean Delta F and noise-row pruning count")
    cbar = fig.colorbar(image, ax=ax, label="Mean Delta F; negative favors PRUNE prior")
    cbar.ax.axhline(0.0, color="white", linewidth=1.4)
    ax.text(
        0.01,
        -0.22,
        "Counts aggregate observation-noise rows in the software grid; they are not empirical samples.",
        transform=ax.transAxes,
        fontsize=9,
        color=style["palette"]["muted"],
    )
    _panel_label(ax, "F")
    return _save_return(
        fig,
        _fig_path(project_root, style, "simulation_sensitivity_heatmap"),
        style["dpi"],
    )


def _quantum_boundary_entropy_landscape(
    project_root: Path, style: dict[str, Any], quantum: dict[str, Any]
) -> Path:
    rows = quantum["rows"]
    theta = np.array([row["theta"] for row in rows])
    entropy = np.array([row["reduced_entropy_bits"] for row in rows])
    chsh = np.array([row["chsh_s_max"] for row in rows])
    contextual = np.array([row["contextual_fraction"] for row in rows])
    landauer = np.array([row["landauer_lower_bound_kbt"] for row in rows])
    fig, axes = plt.subplots(2, 2, figsize=(10.2, 6.6))
    axes = axes.ravel()
    axes[0].plot(
        theta,
        entropy,
        marker="o",
        color=style["palette"]["primary"],
        label="reduced entropy",
    )
    axes[0].plot(
        theta,
        2.0 * entropy,
        marker="s",
        color=style["palette"]["secondary"],
        label="mutual information",
    )
    axes[0].set_title("Boundary entropy across entanglement sweep")
    axes[0].set_ylabel("Bits")
    axes[0].legend(title="Entropy legend", fontsize=9)
    axes[1].plot(
        theta, chsh, marker="o", color=style["palette"]["accent"], label="CHSH S_max"
    )
    axes[1].axhline(
        quantum["local_chsh_bound"],
        color=style["palette"]["muted"],
        linestyle="--",
        label="local bound",
    )
    axes[1].axhline(
        quantum["tsirelson_bound"],
        color=style["palette"]["warning"],
        linestyle=":",
        label="Tsirelson bound",
    )
    axes[1].set_title("Bell-witness strength")
    axes[1].set_ylabel("CHSH value")
    axes[1].legend(title="Bound legend", fontsize=9)
    axes[2].plot(
        theta,
        contextual,
        marker="^",
        color=style["palette"]["secondary"],
        label="contextual fraction",
    )
    axes[2].set_title("Contextuality witness proxy")
    axes[2].set_xlabel("Schmidt-family theta")
    axes[2].set_ylabel("Unit-scaled witness")
    axes[2].legend(fontsize=9)
    axes[3].plot(
        theta,
        landauer,
        marker="d",
        color=style["palette"]["warning"],
        label="Landauer lower bound",
    )
    axes[3].set_title("Computational boundary erasure lower bound")
    axes[3].set_xlabel("Schmidt-family theta")
    axes[3].set_ylabel("kBT units")
    axes[3].legend(fontsize=9)
    for label, ax in zip(("G", "H", "I", "J"), axes, strict=True):
        ax.grid(color=style["palette"]["grid"], linewidth=0.6, alpha=0.8)
        _panel_label(ax, label)
    fig.suptitle("Finite two-qubit entropy and contextuality controls", y=1.02)
    return _save_return(
        fig,
        _fig_path(project_root, style, "quantum_boundary_entropy_landscape"),
        style["dpi"],
    )


def _quantum_contextuality_witness(
    project_root: Path, style: dict[str, Any], quantum: dict[str, Any]
) -> Path:
    rows = quantum["rows"]
    entropy = np.array([row["reduced_entropy_bits"] for row in rows])
    chsh = np.array([row["chsh_s_max"] for row in rows])
    contextual = np.array([row["contextual_fraction"] for row in rows])
    basis_rows = quantum["basis_invariance_rows"]
    theta_grid = quantum["theta_grid"]
    rotation_grid = quantum["rotation_grid"]
    heat = np.zeros((len(rotation_grid), len(theta_grid)))
    drift = np.zeros_like(heat)
    lookup = {(row["theta"], row["rotation_angle"]): row for row in basis_rows}
    for x_idx, theta in enumerate(theta_grid):
        for y_idx, angle in enumerate(rotation_grid):
            row = lookup[(theta, angle)]
            heat[y_idx, x_idx] = row["rotated_measurement_entropy_bits"]
            drift[y_idx, x_idx] = row["entropy_drift_bits"]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    scatter = axes[0].scatter(
        entropy,
        chsh,
        c=contextual,
        cmap="viridis",
        s=55,
        edgecolor="white",
        linewidth=0.5,
    )
    axes[0].plot(
        entropy,
        chsh,
        color=style["palette"]["grid"],
        linewidth=1,
        zorder=0,
        label="Schmidt sweep",
    )
    axes[0].axhline(
        quantum["local_chsh_bound"],
        color=style["palette"]["muted"],
        linestyle="--",
        label="local bound",
    )
    axes[0].axhline(
        quantum["tsirelson_bound"],
        color=style["palette"]["warning"],
        linestyle=":",
        label="Tsirelson bound",
    )
    axes[0].set_xlabel("Reduced entropy (bits)")
    axes[0].set_ylabel("CHSH S_max")
    axes[0].set_title("CHSH witness as boundary entropy rises")
    axes[0].legend(title="Line legend", fontsize=9)
    colorbar = fig.colorbar(scatter, ax=axes[0], fraction=0.046, pad=0.04)
    colorbar.set_label("Contextual fraction")
    image = axes[1].imshow(
        heat,
        origin="lower",
        aspect="auto",
        cmap="magma",
        extent=[
            min(theta_grid),
            max(theta_grid),
            min(rotation_grid),
            max(rotation_grid),
        ],
    )
    axes[1].contour(
        theta_grid,
        rotation_grid,
        drift,
        levels=[1e-12],
        colors=[style["palette"]["accent"]],
        linewidths=0.8,
    )
    axes[1].set_xlabel("Schmidt-family theta")
    axes[1].set_ylabel("Local rotation angle")
    axes[1].set_title(
        "Basis sweep: measurement entropy changes, reduced entropy invariant"
    )
    cbar = fig.colorbar(image, ax=axes[1], fraction=0.046, pad=0.04)
    cbar.set_label("Rotated measurement entropy (bits)")
    axes[1].legend(
        handles=[
            Line2D(
                [0],
                [0],
                color=style["palette"]["accent"],
                label="zero reduced-entropy drift contour",
            )
        ],
        fontsize=9,
        loc="upper left",
    )
    _panel_label(axes[0], "K")
    _panel_label(axes[1], "L")
    return _save_return(
        fig,
        _fig_path(project_root, style, "quantum_contextuality_witness"),
        style["dpi"],
    )


def _quantum_measurement_contextuality_table(
    project_root: Path, style: dict[str, Any], contextuality: dict[str, Any]
) -> Path:
    contexts = contextuality["measurement_cover"]["contexts"]
    outcomes = contextuality["measurement_cover"]["outcomes"]
    rows = [
        row
        for row in contextuality["probability_rows"]
        if row["model"] == "bell_measurement_cover"
    ]
    lookup = {(row["context"], row["outcome"]): row["probability"] for row in rows}
    matrix = np.array(
        [[lookup[(context, outcome)] for outcome in outcomes] for context in contexts],
        dtype=float,
    )
    fig, axes = plt.subplots(
        1, 2, figsize=(11, 4.3), gridspec_kw={"width_ratios": [1.45, 1.0]}
    )
    image = axes[0].imshow(matrix, aspect="auto", cmap="YlGnBu", vmin=0, vmax=0.5)
    for y_idx, context in enumerate(contexts):
        for x_idx, outcome in enumerate(outcomes):
            value = matrix[y_idx, x_idx]
            axes[0].text(
                x_idx, y_idx, f"{value:.3f}", ha="center", va="center", fontsize=9
            )
    axes[0].set_xticks(range(len(outcomes)), outcomes)
    axes[0].set_yticks(range(len(contexts)), contexts)
    axes[0].set_xlabel("Joint outcome")
    axes[0].set_ylabel("Measurement context")
    axes[0].set_title("Bell empirical-model probabilities")
    colorbar = fig.colorbar(image, ax=axes[0], fraction=0.046, pad=0.04)
    colorbar.set_label("Joint probability")
    labels = ["product control", "Bell cover"]
    values = [contextuality["product_control_chsh"], contextuality["bell_chsh"]]
    bars = axes[1].bar(
        labels,
        values,
        color=[style["palette"]["muted"], style["palette"]["accent"]],
        edgecolor=style["palette"]["primary"],
        linewidth=0.8,
    )
    bars[0].set_hatch("//")
    bars[1].set_hatch("..")
    axes[1].axhline(
        contextuality["local_chsh_bound"],
        color=style["palette"]["primary"],
        linestyle="--",
        linewidth=1.2,
    )
    axes[1].axhline(
        contextuality["tsirelson_bound"],
        color=style["palette"]["warning"],
        linestyle=":",
        linewidth=1.4,
    )
    for index, value in enumerate(values):
        axes[1].text(index, value + 0.05, f"S={value:.3f}", ha="center", fontsize=9)
    axes[1].set_ylim(0, 3.05)
    axes[1].set_ylabel("CHSH S")
    axes[1].set_title("Negative control and Tsirelson check")
    axes[1].tick_params(axis="x", rotation=12)
    axes[1].legend(
        handles=[
            Patch(
                facecolor=style["palette"]["muted"],
                edgecolor=style["palette"]["primary"],
                hatch="//",
                label="product control",
            ),
            Patch(
                facecolor=style["palette"]["accent"],
                edgecolor=style["palette"]["primary"],
                hatch="..",
                label="Bell cover",
            ),
            Line2D(
                [0],
                [0],
                color=style["palette"]["primary"],
                linestyle="--",
                label="local bound",
            ),
            Line2D(
                [0],
                [0],
                color=style["palette"]["warning"],
                linestyle=":",
                label="Tsirelson bound",
            ),
        ],
        title="Encoding legend",
        fontsize=9,
        loc="upper left",
    )
    _panel_label(axes[0], "A")
    _panel_label(axes[1], "B")
    return _save_return(
        fig,
        _fig_path(project_root, style, "quantum_measurement_contextuality_table"),
        style["dpi"],
    )


def _quantum_local_polytope_audit(
    project_root: Path, style: dict[str, Any], contextuality: dict[str, Any]
) -> Path:
    fits = {row["model"]: row for row in contextuality["local_polytope"]["fits"]}
    labels = ["product control", "Bell cover"]
    residuals = [
        fits["product_control"]["min_l1_residual"],
        fits["bell_measurement_cover"]["min_l1_residual"],
    ]
    feasibility = [
        fits["product_control"]["feasible"],
        fits["bell_measurement_cover"]["feasible"],
    ]
    fig, axes = plt.subplots(
        1, 2, figsize=(11, 4.2), gridspec_kw={"width_ratios": [1.0, 1.35]}
    )
    bars = axes[0].bar(
        labels,
        residuals,
        color=[style["palette"]["muted"], style["palette"]["accent"]],
        edgecolor=style["palette"]["primary"],
        linewidth=0.8,
    )
    bars[0].set_hatch("//")
    bars[1].set_hatch("..")
    axes[0].axhline(
        0.0,
        color=style["palette"]["primary"],
        linestyle="--",
        linewidth=1,
        label="exact feasibility target",
    )
    for index, (value, feasible) in enumerate(zip(residuals, feasibility, strict=True)):
        axes[0].text(
            index,
            value + 0.025,
            "feasible" if feasible else "infeasible",
            ha="center",
            fontsize=9,
        )
    axes[0].set_ylim(0, max(residuals) * 1.25)
    axes[0].set_ylabel("Minimum L1 residual")
    axes[0].set_title("Local-polytope feasibility")
    axes[0].tick_params(axis="x", rotation=12)
    axes[0].legend(
        handles=[
            Patch(
                facecolor=style["palette"]["muted"],
                edgecolor=style["palette"]["primary"],
                hatch="//",
                label="product control",
            ),
            Patch(
                facecolor=style["palette"]["accent"],
                edgecolor=style["palette"]["primary"],
                hatch="..",
                label="Bell cover",
            ),
            Line2D(
                [0],
                [0],
                color=style["palette"]["primary"],
                linestyle="--",
                label="zero residual target",
            ),
        ],
        title="Encoding legend",
        fontsize=9,
        loc="upper left",
    )
    weights = fits["product_control"]["assignment_rows"]
    signatures = [
        f"A0{row['A0']:+d} A1{row['A1']:+d} B0{row['B0']:+d} B1{row['B1']:+d}"
        for row in weights
    ]
    values = [row["weight"] for row in weights]
    y_pos = np.arange(len(weights))
    axes[1].barh(
        y_pos,
        values,
        color=style["palette"]["muted"],
        edgecolor=style["palette"]["primary"],
        hatch="//",
        label="local assignment weight",
    )
    axes[1].set_yticks(y_pos, signatures)
    axes[1].invert_yaxis()
    axes[1].set_xlabel("Mixture weight")
    axes[1].set_title("Product-control deterministic assignment mixture")
    axes[1].legend(fontsize=9, loc="lower right")
    for y_index, value in enumerate(values):
        axes[1].text(value + 0.005, y_index, f"{value:.3f}", va="center", fontsize=9)
    axes[1].set_xlim(0.0, max(values) * 1.25)
    _panel_label(axes[0], "C")
    _panel_label(axes[1], "D")
    return _save_return(
        fig,
        _fig_path(project_root, style, "quantum_local_polytope_audit"),
        style["dpi"],
    )


def _quantum_open_system_dynamics(
    project_root: Path, style: dict[str, Any], dynamics: dict[str, Any]
) -> Path:
    rows = [row for row in dynamics["rows"] if row["state_label"] == "bell_dephased"]
    rates = dynamics["decoherence_rate_grid"]
    colors = plt.cm.viridis(np.linspace(0.1, 0.9, len(rates)))
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.8))
    for color, rate in zip(colors, rates, strict=True):
        subset = [row for row in rows if abs(row["decoherence_rate"] - rate) < 1e-8]
        times = [row["time"] for row in subset]
        axes[0].plot(
            times,
            [row["chsh_s_max"] for row in subset],
            marker="o",
            color=color,
            label=f"gamma={rate:g}",
        )
        axes[1].plot(
            times,
            [row["global_entropy_bits"] for row in subset],
            marker="s",
            color=color,
            label=f"gamma={rate:g}",
        )
        axes[2].plot(
            times,
            [row["mutual_information_bits"] for row in subset],
            marker="^",
            color=color,
            label=f"gamma={rate:g}",
        )
    axes[0].axhline(
        2.0, color=style["palette"]["muted"], linestyle="--", label="local CHSH bound"
    )
    axes[0].set_title("CHSH witness decays")
    axes[0].set_ylabel("CHSH S_max")
    axes[1].set_title("Global entropy increases")
    axes[1].set_ylabel("Bits")
    axes[2].set_title("Mutual information contracts")
    axes[2].set_ylabel("Bits")
    for ax in axes:
        ax.set_xlabel("Time")
        ax.grid(color=style["palette"]["grid"], linewidth=0.6, alpha=0.8)
    axes[0].legend(title="Rate legend", fontsize=9, loc="upper right")
    axes[1].legend(title="Rate legend", fontsize=9, loc="lower right")
    axes[2].legend(title="Rate legend", fontsize=9, loc="upper right")
    _panel_label(axes[0], "M")
    _panel_label(axes[1], "N")
    _panel_label(axes[2], "O")
    return _save_return(
        fig,
        _fig_path(project_root, style, "quantum_open_system_dynamics"),
        style["dpi"],
    )


def _qfep_boundary_hamiltonian_dynamics(
    project_root: Path, style: dict[str, Any], dynamics: dict[str, Any]
) -> Path:
    rows = dynamics["rows"]
    rates = dynamics["decoherence_rate_grid"]
    colors = plt.cm.cividis(np.linspace(0.12, 0.92, len(rates)))
    fig, axes = plt.subplots(1, 3, figsize=(14.0, 4.4))
    for color, rate in zip(colors, rates, strict=True):
        subset = [row for row in rows if abs(row["decoherence_rate"] - rate) < 1e-8]
        times = [row["time"] for row in subset]
        axes[0].plot(
            times,
            [row["global_entropy_bits"] for row in subset],
            marker="o",
            color=color,
            label=f"rate={rate:g}",
        )
        axes[1].plot(
            times,
            [row["mutual_information_bits"] for row in subset],
            marker="s",
            color=color,
            label=f"rate={rate:g}",
        )
        axes[2].plot(
            times,
            [max(0.0, -row["min_eigenvalue"]) for row in subset],
            marker="^",
            color=color,
            label=f"rate={rate:g}",
        )
    axes[0].set_title("Boundary entropy\nproduction")
    axes[0].set_ylabel("Global entropy (bits)")
    axes[1].set_title("Mutual information\ncontracts")
    axes[1].set_ylabel("Mutual information (bits)")
    axes[2].set_title("Positivity residual\nstays at zero")
    axes[2].set_ylabel("Negative-eigenvalue residual")
    for ax in axes:
        ax.set_xlabel("Time")
        ax.grid(color=style["palette"]["grid"], linewidth=0.6, alpha=0.8)
        ax.legend(title="Lindblad rate legend", fontsize=9)
    fig.suptitle(
        "Finite boundary-Hamiltonian qFEP extension engine",
        y=0.98,
        fontsize=15.1,
        fontweight="bold",
    )
    setattr(fig, "_layout_rect", (0.0, 0.0, 1.0, 0.86))
    _panel_label(axes[0], "AB")
    _panel_label(axes[1], "AC")
    _panel_label(axes[2], "AD")
    return _save_return(
        fig,
        _fig_path(project_root, style, "qfep_boundary_hamiltonian_dynamics"),
        style["dpi"],
    )


def _many_body_boundary_screen_sweep(
    project_root: Path, style: dict[str, Any], sweep: dict[str, Any]
) -> Path:
    states = sorted({row["state_label"] for row in sweep["rows"]})
    cuts = [cut["id"] for cut in sweep["cuts"]]
    lookup = {(row["state_label"], row["cut_id"]): row for row in sweep["rows"]}
    matrix = np.array(
        [
            [lookup[(state, cut)]["reduced_entropy_bits"] for cut in cuts]
            for state in states
        ]
    )
    fig, ax = plt.subplots(figsize=(9.6, 3.8))
    image = ax.imshow(
        matrix,
        aspect="auto",
        cmap="PuBuGn",
        vmin=0.0,
        vmax=max(1.0, float(np.max(matrix))),
    )
    for y_idx, state in enumerate(states):
        for x_idx, cut in enumerate(cuts):
            row = lookup[(state, cut)]
            label = f"{row['reduced_entropy_bits']:.1f}"
            if row["observer_boundary_candidate"]:
                label += "\nobserver"
            elif row["cut_class"] == "negative_control_random_cut":
                label += "\ncontrol"
            ax.text(x_idx, y_idx, label, ha="center", va="center", fontsize=9)
    ax.set_xticks(range(len(cuts)), [cut.replace("_", "\n") for cut in cuts])
    ax.set_yticks(range(len(states)), [state.replace("_", "\n") for state in states])
    ax.set_xlabel("Subsystem cut")
    ax.set_ylabel("Finite many-body state")
    ax.set_title("Many-body boundary-screen cut sensitivity")
    colorbar = fig.colorbar(image, ax=ax, fraction=0.035, pad=0.02)
    colorbar.set_label("Reduced entropy (bits)")
    ax.legend(
        handles=[
            Patch(facecolor=plt.cm.PuBuGn(0.75), label="entangled cut entropy"),
            Patch(
                facecolor=plt.cm.PuBuGn(0.15), label="separable or low-entropy control"
            ),
            Line2D(
                [0],
                [0],
                marker="s",
                color="w",
                markerfacecolor="white",
                markeredgecolor=style["palette"]["primary"],
                label="cell text labels observer/control status",
            ),
        ],
        title="Encoding legend",
        fontsize=9,
        loc="upper right",
    )
    _panel_label(ax, "AE")
    return _save_return(
        fig,
        _fig_path(project_root, style, "many_body_boundary_screen_sweep"),
        style["dpi"],
    )


def _sheaf_contextuality_obstruction_audit(
    project_root: Path, style: dict[str, Any], audit: dict[str, Any]
) -> Path:
    rows = audit["rows"]
    labels = [row["id"].replace("_", "\n") for row in rows]
    residuals = [row["min_l1_residual"] for row in rows]
    feasible = [row["global_section_feasible"] for row in rows]
    fig, axes = plt.subplots(
        1, 2, figsize=(11.2, 4.1), gridspec_kw={"width_ratios": [1.15, 1.0]}
    )
    bars = axes[0].bar(
        labels,
        residuals,
        color=[
            style["palette"]["muted"] if flag else style["palette"]["accent"]
            for flag in feasible
        ],
    )
    bars[0].set_hatch("//")
    bars[1].set_hatch("..")
    axes[0].axhline(
        0.0,
        color=style["palette"]["primary"],
        linestyle="--",
        label="global-section target",
    )
    for index, row in enumerate(rows):
        axes[0].text(
            index,
            row["min_l1_residual"] + 0.04,
            "feasible" if row["global_section_feasible"] else "obstructed",
            ha="center",
            fontsize=9,
        )
    axes[0].set_ylabel("Minimum L1 residual")
    axes[0].set_title("Global-section feasibility")
    axes[0].legend(
        handles=[
            Patch(
                facecolor=style["palette"]["muted"],
                hatch="//",
                label="noncontextual control",
            ),
            Patch(
                facecolor=style["palette"]["accent"],
                hatch="..",
                label="parity obstruction",
            ),
            Line2D(
                [0],
                [0],
                color=style["palette"]["primary"],
                linestyle="--",
                label="zero residual target",
            ),
        ],
        title="Encoding legend",
        fontsize=9,
        loc="upper left",
    )
    matrix = np.array(
        [
            [
                1.0 if row["global_section_feasible"] else 0.0,
                1.0 if row["no_disturbance_max_error"] < 1e-10 else 0.0,
            ]
            for row in rows
        ]
    )
    image = axes[1].imshow(matrix, aspect="auto", cmap="YlGnBu", vmin=0, vmax=1)
    axes[1].set_xticks([0, 1], ["global\nsection", "no-disturbance\nmarginals"])
    axes[1].set_yticks(range(len(labels)), labels)
    for y_idx in range(matrix.shape[0]):
        for x_idx in range(matrix.shape[1]):
            axes[1].text(
                x_idx,
                y_idx,
                "Y" if matrix[y_idx, x_idx] else "N",
                ha="center",
                va="center",
                fontsize=10.1,
            )
    axes[1].set_title("Sheaf audit controls")
    _binary_colorbar(fig, image, axes[1], "criterion satisfied")
    _panel_label(axes[0], "AF")
    _panel_label(axes[1], "AG")
    return _save_return(
        fig,
        _fig_path(project_root, style, "sheaf_contextuality_obstruction_audit"),
        style["dpi"],
    )


def _qrf_transformation_covariance_audit(
    project_root: Path, style: dict[str, Any], audit: dict[str, Any]
) -> Path:
    rows = audit["rows"]
    columns = ["column_stochastic", "nonnegative", "accepted"]
    matrix = np.array(
        [[1.0 if row[column] else 0.0 for column in columns] for row in rows]
    )
    labels = [row["id"].replace("_", "\n") for row in rows]
    fig, axes = plt.subplots(
        1, 2, figsize=(12.2, 4.8), gridspec_kw={"width_ratios": [1.2, 1.0]}
    )
    image = axes[0].imshow(matrix, aspect="auto", cmap="YlGnBu", vmin=0, vmax=1)
    axes[0].set_xticks(
        range(len(columns)), [column.replace("_", "\n") for column in columns]
    )
    axes[0].set_yticks(range(len(labels)), labels)
    axes[0].set_xticks(np.arange(-0.5, len(columns), 1), minor=True)
    axes[0].set_yticks(np.arange(-0.5, len(labels), 1), minor=True)
    axes[0].grid(which="minor", color="white", linewidth=1.2)
    for y_idx in range(matrix.shape[0]):
        for x_idx in range(matrix.shape[1]):
            axes[0].text(
                x_idx,
                y_idx,
                "Y" if matrix[y_idx, x_idx] else "N",
                ha="center",
                va="center",
                fontsize=9,
                fontweight="bold",
            )
    axes[0].set_title("Admissible QRF map checks")
    _binary_colorbar(fig, image, axes[0], "criterion satisfied")
    admissible = [row for row in rows if row["admissible"]]
    x = np.arange(len(admissible))
    axes[1].bar(
        x - 0.18,
        [row["mass_error"] for row in admissible],
        width=0.36,
        color=style["palette"]["secondary"],
        label="mass error",
    )
    axes[1].bar(
        x + 0.18,
        [row["expectation_covariance_error"] or 0.0 for row in admissible],
        width=0.36,
        color=style["palette"]["accent"],
        hatch="//",
        label="covariance error",
    )
    axes[1].set_xticks(x, [row["id"].replace("_", "\n") for row in admissible])
    axes[1].set_ylabel("Absolute error")
    axes[1].set_title("Probability and expectation covariance")
    axes[1].grid(axis="y", color=style["palette"]["grid"], linewidth=0.5, alpha=0.55)
    axes[1].legend(title="Error legend", fontsize=9)
    _panel_label(axes[0], "AH")
    _panel_label(axes[1], "AI")
    return _save_return(
        fig,
        _fig_path(project_root, style, "qrf_transformation_covariance_audit"),
        style["dpi"],
    )


def _empirical_adapter_provenance_audit(
    project_root: Path, style: dict[str, Any], audit: dict[str, Any]
) -> Path:
    rows = audit["rows"]
    criteria = [
        ("has_source_identity", "source\nidentity"),
        ("has_ethics_basis", "ethics\nbasis"),
        ("has_preprocessing_hash", "preprocess\nhash"),
        ("has_null_model", "null\nmodel"),
        ("allowed_for_empirical_claim", "empirical\nclaim"),
    ]
    matrix = np.array(
        [[1.0 if row[key] else 0.0 for key, _ in criteria] for row in rows]
    )
    fig, ax = plt.subplots(figsize=(10.8, 4.3))
    image = ax.imshow(matrix, aspect="auto", cmap="YlOrBr", vmin=0, vmax=1)
    ax.set_xticks(range(len(criteria)), [label for _, label in criteria])
    ax.set_yticks(range(len(rows)), [row["id"].replace("_", "\n") for row in rows])
    for y_idx, row in enumerate(rows):
        for x_idx, (key, _) in enumerate(criteria):
            ax.text(
                x_idx,
                y_idx,
                "Y" if row[key] else "N",
                ha="center",
                va="center",
                fontsize=9,
            )
        ax.text(len(criteria) + 0.18, y_idx, row["decision"], va="center", fontsize=9)
    ax.set_xlim(-0.5, len(criteria) + 1.4)
    ax.set_title("Empirical adapter provenance remains fail-closed")
    ax.set_xlabel("Provenance and claim-permission criterion")
    ax.set_ylabel("Adapter record")
    colorbar = fig.colorbar(image, ax=ax, fraction=0.035, pad=0.02)
    colorbar.set_ticks([0, 1])
    colorbar.set_ticklabels(["no", "yes"])
    colorbar.set_label("criterion present")
    ax.legend(
        handles=[
            Patch(facecolor=plt.cm.YlOrBr(0.8), label="criterion present"),
            Patch(facecolor=plt.cm.YlOrBr(0.15), label="criterion absent"),
            Line2D(
                [0],
                [0],
                color="none",
                marker="s",
                markerfacecolor="white",
                markeredgecolor=style["palette"]["primary"],
                label="cell text gives Y/N and decision",
            ),
        ],
        title="Encoding legend",
        fontsize=9,
        loc="upper right",
    )
    _panel_label(ax, "AJ")
    return _save_return(
        fig,
        _fig_path(project_root, style, "empirical_adapter_provenance_audit"),
        style["dpi"],
    )


def _arbitrary_two_qubit_entanglement_audit(
    project_root: Path, style: dict[str, Any], audit: dict[str, Any]
) -> Path:
    rows = audit["rows"]
    werner = sorted(
        [row for row in rows if row["family"] == "werner"],
        key=lambda row: row["parameter"],
    )
    invalid = audit["invalid_density_controls"]
    fig, axes = plt.subplots(
        1, 2, figsize=(11.2, 4.2), gridspec_kw={"width_ratios": [1.25, 1.0]}
    )
    p_values = [row["parameter"] for row in werner]
    negativity = [row["negativity"] for row in werner]
    ppt_min = [row["ppt_min_eigenvalue"] for row in werner]
    entangled = [row["entangled_by_ppt"] for row in werner]
    axes[0].plot(
        p_values,
        negativity,
        marker="o",
        color=style["palette"]["secondary"],
        label="negativity",
    )
    axes[0].plot(
        p_values,
        ppt_min,
        marker="s",
        linestyle="--",
        color=style["palette"]["accent"],
        label="PPT min eigenvalue",
    )
    for x_value, flag in zip(p_values, entangled, strict=True):
        axes[0].axvline(
            x_value, color=style["palette"]["grid"], linewidth=0.4, alpha=0.5
        )
        axes[0].text(
            x_value,
            max(negativity) + 0.025,
            "E" if flag else "S",
            ha="center",
            fontsize=9,
        )
    axes[0].axvline(
        1.0 / 3.0,
        color=style["palette"]["warning"],
        linestyle=":",
        linewidth=1.4,
        label="Werner PPT threshold",
    )
    axes[0].axhline(0.0, color=style["palette"]["primary"], linewidth=0.8)
    axes[0].set_xlabel("Werner mixing parameter p")
    axes[0].set_ylabel("Witness value")
    axes[0].set_title("PPT and negativity controls")
    axes[0].legend(title="Line and marker legend", fontsize=9)
    case_labels = [
        row["id"].replace("_", "\n") for row in rows if row["family"] != "werner"
    ]
    case_values = [row["negativity"] for row in rows if row["family"] != "werner"]
    axes[1].bar(
        case_labels,
        case_values,
        color=[
            style["palette"]["muted"],
            style["palette"]["muted"],
            style["palette"]["accent"],
        ],
    )
    for index, value in enumerate(case_values):
        axes[1].text(index, value + 0.02, f"{value:.2f}", ha="center", fontsize=9)
    axes[1].set_ylabel("Negativity")
    axes[1].set_title("Separable and Bell controls")
    axes[1].legend(
        handles=[
            Patch(facecolor=style["palette"]["muted"], label="separable controls"),
            Patch(facecolor=style["palette"]["accent"], label="Bell entangled control"),
            Line2D(
                [0],
                [0],
                color="none",
                marker="s",
                markerfacecolor="white",
                markeredgecolor=style["palette"]["primary"],
                label=f"{len(invalid)} invalid matrices rejected",
            ),
        ],
        title="Control legend",
        fontsize=9,
        loc="upper left",
    )
    _panel_label(axes[0], "AK")
    _panel_label(axes[1], "AL")
    return _save_return(
        fig,
        _fig_path(project_root, style, "arbitrary_two_qubit_entanglement_audit"),
        style["dpi"],
    )


def _general_measurement_cover_polytope_audit(
    project_root: Path, style: dict[str, Any], audit: dict[str, Any]
) -> Path:
    rows = audit["rows"]
    labels = [row["id"].replace("_", "\n") for row in rows]
    residuals = [row["min_l1_residual"] for row in rows]
    feasible = [row["global_section_feasible"] for row in rows]
    fig, axes = plt.subplots(
        1, 2, figsize=(11.5, 4.2), gridspec_kw={"width_ratios": [1.25, 1.0]}
    )
    colors = [
        style["palette"]["muted"] if flag else style["palette"]["accent"]
        for flag in feasible
    ]
    bars = axes[0].bar(
        labels,
        residuals,
        color=colors,
        edgecolor=style["palette"]["primary"],
        linewidth=0.7,
    )
    for bar, flag in zip(bars, feasible, strict=True):
        bar.set_hatch("//" if flag else "..")
    axes[0].axhline(0.0, color=style["palette"]["primary"], linestyle="--", linewidth=1)
    for index, row in enumerate(rows):
        axes[0].text(
            index,
            row["min_l1_residual"] + 0.035,
            "feasible" if row["global_section_feasible"] else "obstructed",
            ha="center",
            fontsize=9,
        )
    axes[0].set_ylabel("Minimum L1 residual")
    axes[0].set_title("Parsed cover polytope residuals")
    axes[0].legend(
        handles=[
            Patch(
                facecolor=style["palette"]["muted"],
                hatch="//",
                label="feasible control",
            ),
            Patch(
                facecolor=style["palette"]["accent"],
                hatch="..",
                label="infeasible obstruction",
            ),
            Line2D(
                [0],
                [0],
                color=style["palette"]["primary"],
                linestyle="--",
                label="zero residual target",
            ),
        ],
        title="Encoding legend",
        fontsize=9,
    )
    columns = ["global_section_feasible", "expected_feasible", "no_disturbance"]
    matrix = np.array(
        [
            [
                1.0 if row["global_section_feasible"] else 0.0,
                1.0 if row["expected_feasible"] else 0.0,
                1.0 if row["no_disturbance_max_error"] < 1e-10 else 0.0,
            ]
            for row in rows
        ]
    )
    image = axes[1].imshow(matrix, aspect="auto", cmap="YlGnBu", vmin=0, vmax=1)
    axes[1].set_xticks(
        range(len(columns)), [column.replace("_", "\n") for column in columns]
    )
    axes[1].set_yticks(range(len(labels)), labels)
    for y_idx in range(matrix.shape[0]):
        for x_idx in range(matrix.shape[1]):
            axes[1].text(
                x_idx,
                y_idx,
                "Y" if matrix[y_idx, x_idx] else "N",
                ha="center",
                va="center",
                fontsize=9,
            )
    axes[1].set_title("Parser and feasibility checks")
    _binary_colorbar(fig, image, axes[1], "criterion satisfied")
    _panel_label(axes[0], "AM")
    _panel_label(axes[1], "AN")
    return _save_return(
        fig,
        _fig_path(project_root, style, "general_measurement_cover_polytope_audit"),
        style["dpi"],
    )


def _thermodynamic_channel_cost_audit(
    project_root: Path, style: dict[str, Any], audit: dict[str, Any]
) -> Path:
    rows = audit["rows"]
    channels = sorted({row["channel_id"] for row in rows})
    states = sorted({row["state_id"] for row in rows})
    lookup = {(row["state_id"], row["channel_id"]): row for row in rows}
    matrix = np.array(
        [
            [
                lookup[(state, channel)]["landauer_lower_bound_kbt"]
                for channel in channels
            ]
            for state in states
        ]
    )
    fig, axes = plt.subplots(
        1, 2, figsize=(11.4, 4.2), gridspec_kw={"width_ratios": [1.2, 0.9]}
    )
    image = axes[0].imshow(
        matrix,
        aspect="auto",
        cmap="YlOrBr",
        vmin=0.0,
        vmax=max(0.1, float(np.max(matrix))),
    )
    axes[0].set_xticks(
        range(len(channels)), [channel.replace("_", "\n") for channel in channels]
    )
    axes[0].set_yticks(
        range(len(states)), [state.replace("_", "\n") for state in states]
    )
    for y_idx in range(matrix.shape[0]):
        for x_idx in range(matrix.shape[1]):
            axes[0].text(
                x_idx,
                y_idx,
                f"{matrix[y_idx, x_idx]:.2f}",
                ha="center",
                va="center",
                fontsize=9,
            )
    axes[0].set_title("Landauer lower-bound matrix")
    axes[0].set_xlabel("Finite channel")
    axes[0].set_ylabel("Input state")
    colorbar = fig.colorbar(image, ax=axes[0], fraction=0.04, pad=0.02)
    colorbar.set_label("Lower bound (kBT units)")
    invalid = audit["invalid_channel_controls"]
    axes[1].bar(
        [row["id"].replace("_", "\n") for row in invalid],
        [row["cptp_error"] for row in invalid],
        color=style["palette"]["accent"],
        edgecolor=style["palette"]["primary"],
        hatch="//",
        label="CPTP error",
    )
    axes[1].axhline(
        1e-6,
        color=style["palette"]["primary"],
        linestyle="--",
        linewidth=1,
        label="rejection threshold",
    )
    axes[1].set_yscale("log")
    axes[1].set_title("Non-CPTP controls rejected")
    axes[1].set_ylabel("Max CPTP residual")
    axes[1].legend(title="Control legend", fontsize=9)
    _panel_label(axes[0], "AO")
    _panel_label(axes[1], "AP")
    return _save_return(
        fig,
        _fig_path(project_root, style, "thermodynamic_channel_cost_audit"),
        style["dpi"],
    )


def _sparse_boundary_screen_scaling_audit(
    project_root: Path, style: dict[str, Any], audit: dict[str, Any]
) -> Path:
    rows = [
        row
        for row in audit["rows"]
        if row["state_label"] == "sparse_cross_boundary_bell_pairs"
    ]
    qubits = audit["qubit_counts"]
    cuts = sorted({row["cut_id"] for row in rows})
    lookup = {(row["qubit_count"], row["cut_id"]): row for row in rows}
    matrix = np.array(
        [
            [lookup[(qubit, cut)]["reduced_entropy_bits"] for cut in cuts]
            for qubit in qubits
        ]
    )
    fig, axes = plt.subplots(
        1, 2, figsize=(11.8, 4.2), gridspec_kw={"width_ratios": [1.2, 1.0]}
    )
    image = axes[0].imshow(
        matrix,
        aspect="auto",
        cmap="PuBuGn",
        vmin=0.0,
        vmax=max(1.0, float(np.max(matrix))),
    )
    axes[0].set_xticks(range(len(cuts)), [cut.replace("_", "\n") for cut in cuts])
    axes[0].set_yticks(range(len(qubits)), [str(qubit) for qubit in qubits])
    for y_idx, qubit in enumerate(qubits):
        for x_idx, cut in enumerate(cuts):
            row = lookup[(qubit, cut)]
            tag = "obs" if row["observer_boundary_candidate"] else "ctrl"
            axes[0].text(
                x_idx,
                y_idx,
                f"{row['reduced_entropy_bits']:.1f}\n{tag}",
                ha="center",
                va="center",
                fontsize=9,
            )
    axes[0].set_xlabel("Subsystem cut")
    axes[0].set_ylabel("Qubit count")
    axes[0].set_title("Sparse exact boundary-screen entropy")
    colorbar = fig.colorbar(image, ax=axes[0], fraction=0.04, pad=0.02)
    colorbar.set_label("Reduced entropy (bits)")
    observer = [lookup[(qubit, "observer_half_cut")] for qubit in qubits]
    axes[1].plot(
        qubits,
        [row["reduced_entropy_bits"] for row in observer],
        marker="o",
        color=style["palette"]["secondary"],
        label="observer cut entropy",
    )
    axes[1].set_xlabel("Qubit count")
    axes[1].set_ylabel("Observer entropy (bits)")
    ax2 = axes[1].twinx()
    ax2.plot(
        qubits,
        [row["amplitude_density"] for row in observer],
        marker="s",
        color=style["palette"]["warning"],
        linestyle="--",
        label="amplitude density",
    )
    ax2.set_ylabel("Nonzero amplitude density")
    axes[1].set_title("Scaling and sparsity diagnostics")
    handles1, labels1 = axes[1].get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    axes[1].legend(
        handles1 + handles2,
        labels1 + labels2,
        title="Line legend",
        fontsize=9,
        loc="center right",
    )
    _panel_label(axes[0], "AQ")
    _panel_label(axes[1], "AR")
    return _save_return(
        fig,
        _fig_path(project_root, style, "sparse_boundary_screen_scaling_audit"),
        style["dpi"],
    )


def _qrf_frame_covariance_toy_audit(
    project_root: Path, style: dict[str, Any], audit: dict[str, Any]
) -> Path:
    rows = audit["rows"]
    columns = [
        "accepted",
        "spectrum_drift",
        "reduced_entropy_multiset_drift_bits",
        "probability_spectrum_drift",
    ]
    matrix = np.array(
        [
            [1.0 if row["accepted"] else 0.0 for _ in columns[:1]]
            + [0.0 if row[column] < 1e-10 else 1.0 for column in columns[1:]]
            for row in rows
        ]
    )
    labels = [row["id"].replace("_", "\n") for row in rows]
    fig, axes = plt.subplots(
        1, 2, figsize=(11.6, 4.2), gridspec_kw={"width_ratios": [1.0, 1.0]}
    )
    image = axes[0].imshow(matrix, aspect="auto", cmap="YlGnBu", vmin=0, vmax=1)
    axes[0].set_xticks(
        range(len(columns)),
        ["accepted", "spectrum\nfail", "entropy\nfail", "probability\nfail"],
    )
    axes[0].set_yticks(range(len(labels)), labels)
    for y_idx in range(matrix.shape[0]):
        for x_idx in range(matrix.shape[1]):
            axes[0].text(
                x_idx,
                y_idx,
                "Y" if matrix[y_idx, x_idx] else "N",
                ha="center",
                va="center",
                fontsize=9,
            )
    axes[0].set_title("Frame transform acceptance and drift flags")
    _binary_colorbar(fig, image, axes[0], "criterion or failure present")
    admissible = [row for row in rows if row["admissible"]]
    x = np.arange(len(admissible))
    residual_floor = 1e-14
    spectrum_values = [max(row["spectrum_drift"], residual_floor) for row in admissible]
    entropy_values = [
        max(row["reduced_entropy_multiset_drift_bits"], residual_floor)
        for row in admissible
    ]
    probability_values = [
        max(row["probability_spectrum_drift"], residual_floor) for row in admissible
    ]
    axes[1].bar(
        x - 0.22,
        spectrum_values,
        width=0.22,
        color=style["palette"]["secondary"],
        label="spectrum drift",
    )
    axes[1].bar(
        x,
        entropy_values,
        width=0.22,
        color=style["palette"]["accent"],
        hatch="//",
        label="reduced-entropy drift",
    )
    axes[1].bar(
        x + 0.22,
        probability_values,
        width=0.22,
        color=style["palette"]["warning"],
        hatch="..",
        label="probability drift",
    )
    axes[1].axhline(
        residual_floor,
        color=style["palette"]["primary"],
        linestyle=":",
        linewidth=1,
        label="display floor for zero residuals",
    )
    axes[1].set_yscale("log")
    axes[1].set_ylim(residual_floor / 3.0, 1e-9)
    for x_index in x:
        axes[1].text(
            x_index,
            residual_floor * 1.8,
            "<1e-12",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    axes[1].set_xticks(x, [row["id"].replace("_", "\n") for row in admissible])
    axes[1].set_title("Admissible covariance residuals")
    axes[1].set_ylabel("Absolute drift (floored for display)")
    axes[1].legend(title="Residual legend", fontsize=9)
    _panel_label(axes[0], "AS")
    _panel_label(axes[1], "AT")
    return _save_return(
        fig,
        _fig_path(project_root, style, "qrf_frame_covariance_toy_audit"),
        style["dpi"],
    )


def _profile_comparison(
    project_root: Path, style: dict[str, Any], profile: dict[str, Any]
) -> Path:
    names = [row["deployment"]["name"] for row in profile["rows"]]
    short_names = [_profile_label(name) for name in names]
    free_energy = [row["free_energy"] for row in profile["rows"]]
    posterior = [row["posterior_mass"] for row in profile["rows"]]
    action_labels = profile["action_labels"]
    profile_colors = [_profile_color(style, name) for name in names]
    action_colors = [
        style["palette"]["warning"],
        style["palette"]["secondary"],
        style["palette"]["accent"],
    ]
    action_counts = np.array(
        [
            [row["action_counts"][action] for action in action_labels]
            for row in profile["rows"]
        ],
        dtype=float,
    )
    fig, axes = plt.subplots(1, 3, figsize=(12.8, 4.2))
    axes[0].bar(
        short_names,
        free_energy,
        color=profile_colors,
        edgecolor=style["palette"]["primary"],
        linewidth=0.6,
    )
    axes[0].set_title("Profile free energy")
    axes[0].set_ylabel("Free energy\n(lower ranks higher)")
    best_index = int(np.argmin(free_energy))
    axes[0].annotate(
        "lower F -> higher posterior",
        xy=(best_index, free_energy[best_index]),
        xytext=(best_index, max(free_energy) + 0.12),
        arrowprops={
            "arrowstyle": "->",
            "color": style["palette"]["primary"],
            "linewidth": 0.9,
        },
        ha="center",
        fontsize=9,
    )
    axes[1].bar(
        short_names,
        posterior,
        color=profile_colors,
        edgecolor=style["palette"]["primary"],
        linewidth=0.6,
    )
    axes[1].set_title("Profile posterior mass")
    axes[1].set_ylabel("Posterior mass")
    axes[1].set_ylim(0, max(0.05, max(posterior) * 1.18))
    bottom = np.zeros(len(names))
    for idx, action in enumerate(action_labels):
        axes[2].bar(
            short_names,
            action_counts[:, idx],
            bottom=bottom,
            color=action_colors[idx],
            label=action,
        )
        bottom += action_counts[:, idx]
    axes[2].set_title("Selected actions")
    axes[2].set_ylabel("Count over trace")
    profile_handles = [
        Patch(
            facecolor=_profile_color(style, name),
            edgecolor=style["palette"]["primary"],
            label=f"{_profile_label(name)} = {PROFILE_FULL_LABELS.get(name, name)}",
        )
        for name in names
    ]
    action_handles = [
        Patch(
            facecolor=action_colors[idx],
            edgecolor="white",
            label=action.replace("_", " "),
        )
        for idx, action in enumerate(action_labels)
    ]
    fig.legend(
        handles=profile_handles,
        title="Profile legend",
        loc="upper center",
        bbox_to_anchor=(0.42, -0.02),
        ncol=3,
        fontsize=9,
    )
    fig.legend(
        handles=action_handles,
        title="Action legend",
        loc="upper center",
        bbox_to_anchor=(0.86, -0.02),
        ncol=1,
        fontsize=9,
    )
    for ax in axes:
        ax.tick_params(axis="x", rotation=0)
        ax.grid(axis="y", color=style["palette"]["grid"], linewidth=0.5, alpha=0.55)
    _panel_label(axes[0], "P")
    _panel_label(axes[1], "Q")
    _panel_label(axes[2], "R")
    return _save_return(
        fig, _fig_path(project_root, style, "pymdp_profile_comparison"), style["dpi"]
    )


def _posterior_trajectory(
    project_root: Path, style: dict[str, Any], profile: dict[str, Any]
) -> Path:
    steps = np.arange(profile["steps"])
    traces = {
        row["deployment"]["name"]: np.array(
            [
                entry["state_posterior"][2]
                for entry in profile["policy_trace_rows"]
                if entry["profile"] == row["deployment"]["name"]
            ],
            dtype=float,
        )
        for row in profile["rows"]
    }
    fig, ax = plt.subplots(figsize=(11.2, 4.8))
    y_max = 0.0
    for index, row in enumerate(profile["rows"]):
        profile_name = row["deployment"]["name"]
        trajectory = traces[profile_name]
        y_max = max(y_max, float(trajectory.max()))
        color = _profile_color(style, profile_name)
        ax.plot(
            steps,
            trajectory,
            label=f"{_profile_label(profile_name)} = {PROFILE_FULL_LABELS.get(profile_name, profile_name)}",
            color=color,
            marker="o",
        )
        ax.text(
            steps[-1] + 0.25,
            trajectory[-1],
            _profile_label(profile_name),
            va="center",
            fontsize=9,
            color=color,
            fontweight="bold",
        )
        perturbation_steps = [
            entry["step"]
            for entry in profile["policy_trace_rows"]
            if entry["profile"] == profile_name
            and entry.get("perturbed_observation") is True
        ]
        if perturbation_steps:
            ax.scatter(
                perturbation_steps,
                trajectory[perturbation_steps],
                s=78,
                facecolors="none",
                edgecolors=style["palette"]["warning"],
                linewidths=1.4,
                marker="s",
                label="perturbation step" if index == 0 else None,
                zorder=4,
            )
    ax.set_xlabel("Step")
    ax.set_ylabel("P(contextual_post_dual state)")
    ax.set_xlim(steps[0] - 0.2, steps[-1] + 1.9)
    ax.set_ylim(0, min(1.0, y_max + 0.12))
    ax.set_title("pymdp posterior trajectory with perturbation markers")
    ax.grid(axis="y", color=style["palette"]["grid"], linewidth=0.5, alpha=0.55)
    ax.legend(
        title="Line and marker legend",
        fontsize=9,
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
    )
    _panel_label(ax, "S")
    return _save_return(
        fig, _fig_path(project_root, style, "posterior_trajectory"), style["dpi"]
    )


def _pymdp_runtime_validation_dashboard(
    project_root: Path,
    style: dict[str, Any],
    runtime_log: dict[str, Any],
    model_audit: dict[str, Any],
    stochastic_effects: dict[str, Any],
) -> Path:
    colors = _semantic_colors(style)
    model_rows = model_audit["rows"]
    a_residual = max(
        abs(float(value) - 1.0) for row in model_rows for value in row["A_column_sums"]
    )
    b_residual = max(
        abs(float(value) - 1.0)
        for row in model_rows
        for action_sums in row["B_column_sums_by_action"]
        for value in action_sums
    )
    d_residual = max(abs(float(row["D_sum"]) - 1.0) for row in model_rows)
    summary = runtime_log["summary"]
    controls = runtime_log["controls"]
    control_items = [
        ("runtime\ncheck", controls["canary_ok"]),
        ("model\nhashes", controls["all_model_hashes_present"]),
        ("replay", controls["deterministic_replay_equal"]),
        ("labels", controls["all_trace_labels_resolve"]),
        ("perturb.", controls["perturbation_flags_present"]),
    ]
    effect_rows = sorted(
        [
            row
            for row in stochastic_effects["rows"]
            if row["metric"]
            in {"switch_rate", "mean_surprise", "mean_weighted_expected_free_energy"}
        ],
        key=lambda row: abs(float(row["cliffs_delta"])),
        reverse=True,
    )[:5]
    fig, axes = plt.subplots(2, 2, figsize=(12.8, 7.6))

    ax = axes[0, 0]
    residuals = [a_residual, b_residual, d_residual]
    residual_plot = np.maximum(residuals, 1e-16)
    ax.bar(
        ["A likelihood", "B transition", "D prior"],
        residual_plot,
        color=colors["pass"],
        label="normalization residual",
    )
    ax.axhline(
        1e-8, color=colors["blocked"], linestyle=":", linewidth=1.1, label="tolerance"
    )
    for idx, value in enumerate(residuals):
        ax.text(
            idx,
            min(residual_plot[idx] * 2.6, 3.2e-9),
            f"{value:.1e}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    ax.set_yscale("log")
    ax.set_ylim(1e-17, 2e-7)
    ax.set_ylabel("Absolute residual (log scale)")
    ax.set_title("Generative-model normalization")
    ax.legend(fontsize=9)
    _panel_label(ax, "PD")

    ax = axes[0, 1]
    runtime_residuals = [
        summary["max_state_posterior_norm_residual"],
        summary["max_policy_posterior_norm_residual"],
        summary["max_weighted_expected_free_energy_residual"],
        summary["max_efe_term_residual"],
    ]
    runtime_labels = [
        "state\nposterior",
        "policy\nposterior",
        "weighted\nEFE",
        "EFE\nterms",
    ]
    runtime_plot = np.maximum(runtime_residuals, 1e-12)
    ax.bar(
        runtime_labels, runtime_plot, color=colors["finite"], label="runtime residual"
    )
    ax.axhline(
        1e-7,
        color=colors["blocked"],
        linestyle=":",
        linewidth=1.1,
        label="strict tolerance",
    )
    for idx, value in enumerate(runtime_residuals):
        ax.text(
            idx,
            min(runtime_plot[idx] * 2.2, 3.6e-8),
            f"{value:.1e}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    ax.set_yscale("log")
    ax.set_ylim(1e-12, 2e-7)
    ax.set_ylabel("Maximum residual (log scale)")
    ax.set_title("Trace-level recomputation checks")
    ax.legend(fontsize=9)
    _panel_label(ax, "PE")

    ax = axes[1, 0]
    values = [1.0 if passed else 0.0 for _, passed in control_items]
    bar_colors = [
        colors["pass"] if passed else colors["fail"] for _, passed in control_items
    ]
    ax.bar(
        [label for label, _ in control_items],
        values,
        color=bar_colors,
        edgecolor=colors["boundary"],
        label="pass/fail control",
    )
    ax.set_ylim(0, 1.18)
    ax.set_ylabel("Control status")
    ax.set_title("Runtime event-log controls")
    for idx, (_, passed) in enumerate(control_items):
        ax.text(
            idx,
            0.55,
            "PASS" if passed else "FAIL",
            ha="center",
            va="center",
            fontsize=9,
            fontweight="bold",
            color="white" if passed else colors["boundary"],
        )
    ax.legend(
        handles=[
            Patch(facecolor=colors["pass"], edgecolor=colors["boundary"], label="pass"),
            Patch(facecolor=colors["fail"], edgecolor=colors["boundary"], label="fail"),
        ],
        fontsize=9,
    )
    _panel_label(ax, "PF")

    ax = axes[1, 1]
    y = np.arange(len(effect_rows))
    labels = [
        f"{_profile_label(row['profile'])} | {row['metric'].replace('mean_', '').replace('_', ' ')}"
        for row in effect_rows
    ]
    effects = np.array([row["cliffs_delta"] for row in effect_rows], dtype=float)
    effect_colors = [
        colors["stochastic"] if value >= 0 else colors["null"] for value in effects
    ]
    ax.barh(
        y, effects, color=effect_colors, edgecolor=colors["boundary"], linewidth=0.6
    )
    ax.axvline(
        0.0,
        color=colors["boundary"],
        linestyle="--",
        linewidth=1.0,
        label="profile-null zero",
    )
    lower = min(-0.95, float(effects.min()) - 0.08)
    ax.set_xlim(lower, 0.16)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlabel("Cliff's delta")
    ax.set_title("Largest seeded profile-null contrasts")
    ax.legend(
        handles=[
            Patch(
                facecolor=colors["stochastic"],
                edgecolor=colors["boundary"],
                label="profile higher",
            ),
            Patch(
                facecolor=colors["null"],
                edgecolor=colors["boundary"],
                label="null higher",
            ),
            Line2D([0], [0], color=colors["boundary"], linestyle="--", label="zero"),
        ],
        fontsize=9,
        loc="lower right",
    )
    _panel_label(ax, "PG")

    fig.suptitle(
        "Supplemental pymdp runtime validation dashboard",
        fontsize=15.1,
        fontweight="bold",
    )
    setattr(fig, "_layout_rect", (0.0, 0.03, 1.0, 0.95))
    return _save_return(
        fig,
        _fig_path(project_root, style, "pymdp_runtime_validation_dashboard"),
        style["dpi"],
    )


def _criticality(
    project_root: Path, style: dict[str, Any], report: dict[str, Any]
) -> Path:
    labels = ["entropy", "switch", "variance", "near-critical"]
    values = [
        report["entropy_nats"],
        report["switch_rate"],
        report["variance"],
        report["near_critical_score"],
    ]
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.bar(labels, values, color=style["palette"]["secondary"])
    ax.set_title("Single-trace criticality diagnostic")
    ax.set_ylabel("Simulated diagnostic value")
    ax.legend(
        handles=[
            Patch(color=style["palette"]["secondary"], label="single simulated trace")
        ],
        fontsize=9,
    )
    _panel_label(ax, "T")
    return _save_return(
        fig, _fig_path(project_root, style, "criticality_proxy_panels"), style["dpi"]
    )


def _criticality_stochastic_ensemble(
    project_root: Path, style: dict[str, Any], criticality: dict[str, Any]
) -> Path:
    colors = _semantic_colors(style)
    real_rows = [
        row for row in criticality["summary_rows"] if row["null_control"] is False
    ]
    null_rows = [
        row for row in criticality["summary_rows"] if row["null_control"] is True
    ]
    profiles = [row["profile"] for row in real_rows]
    profile_labels = [_profile_label(profile_name) for profile_name in profiles]
    x = np.arange(len(profiles))
    width = 0.34
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 4.6))
    for ax, metric, title, ylabel in (
        (
            axes[0],
            "near_critical_score",
            "Near-critical score is simulated with null controls",
            "Score",
        ),
        (
            axes[1],
            "switch_rate",
            "Switch-rate intervals expose trajectory variability",
            "Switch rate",
        ),
    ):
        real_mean = np.array(
            [row["metrics"][metric]["mean"] for row in real_rows], dtype=float
        )
        real_low = np.array(
            [row["metrics"][metric]["ci95_low"] for row in real_rows], dtype=float
        )
        real_high = np.array(
            [row["metrics"][metric]["ci95_high"] for row in real_rows], dtype=float
        )
        null_mean = np.array(
            [row["metrics"][metric]["mean"] for row in null_rows], dtype=float
        )
        null_low = np.array(
            [row["metrics"][metric]["ci95_low"] for row in null_rows], dtype=float
        )
        null_high = np.array(
            [row["metrics"][metric]["ci95_high"] for row in null_rows], dtype=float
        )
        ax.bar(
            x - width / 2,
            real_mean,
            width,
            color=colors["stochastic"],
            label="profile ensemble",
            yerr=np.vstack([real_mean - real_low, real_high - real_mean]),
            capsize=3,
        )
        ax.bar(
            x + width / 2,
            null_mean,
            width,
            color=colors["null"],
            label="null control",
            hatch="//",
            yerr=np.vstack([null_mean - null_low, null_high - null_mean]),
            capsize=3,
        )
        for tick_index, (real_value, null_value) in enumerate(
            zip(real_mean, null_mean, strict=True)
        ):
            direction = (
                "profile > null" if real_value > null_value else "profile <= null"
            )
            ax.text(
                tick_index,
                max(real_value, null_value) + 0.03,
                direction,
                ha="center",
                va="bottom",
                fontsize=9,
                color=style["palette"]["muted"],
            )
        ax.set_xticks(x, profile_labels)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(axis="y", color=style["palette"]["grid"], linewidth=0.5, alpha=0.55)
    _panel_label(axes[0], "SA")
    _panel_label(axes[1], "SB")
    fig.legend(
        handles=[
            Patch(
                facecolor=colors["stochastic"],
                label="profile ensemble mean with 95% interval",
            ),
            Patch(
                facecolor=colors["null"],
                hatch="//",
                label="null-control mean with 95% interval",
            ),
        ],
        title="Shared stochastic legend",
        loc="upper center",
        bbox_to_anchor=(0.5, -0.02),
        ncol=2,
        fontsize=9,
    )
    fig.suptitle(
        "Seeded stochastic criticality indicators remain simulation-only",
        fontsize=15.1,
        fontweight="bold",
    )
    return _save_return(
        fig,
        _fig_path(project_root, style, "criticality_stochastic_ensemble"),
        style["dpi"],
    )


def _criticality_signatures(
    project_root: Path,
    style: dict[str, Any],
    criticality_ensemble: dict[str, Any],
    report: dict[str, Any],
) -> Path:
    """Measured criticality signatures: branching ratio per profile and avalanche sizes."""
    colors = _semantic_colors(style)
    real_rows = [
        row
        for row in criticality_ensemble["summary_rows"]
        if row["null_control"] is False
    ]
    null_rows = [
        row
        for row in criticality_ensemble["summary_rows"]
        if row["null_control"] is True
    ]
    profiles = [row["profile"] for row in real_rows]
    profile_labels = [_profile_label(profile_name) for profile_name in profiles]
    real_branching = np.array(
        [row["metrics"]["branching_ratio"]["mean"] for row in real_rows], dtype=float
    )
    null_branching = np.array(
        [row["metrics"]["branching_ratio"]["mean"] for row in null_rows], dtype=float
    )
    x = np.arange(len(profiles))
    width = 0.34
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 4.6))

    axes[0].bar(
        x - width / 2,
        real_branching,
        width,
        color=colors["stochastic"],
        label="profile ensemble",
    )
    axes[0].bar(
        x + width / 2,
        null_branching,
        width,
        color=colors["null"],
        hatch="//",
        edgecolor=colors["boundary"],
        label="null control",
    )
    axes[0].axhline(
        1.0,
        color=colors["boundary"],
        linestyle="--",
        linewidth=1.0,
        label="sigma = 1 (balanced)",
    )
    axes[0].set_xticks(x, profile_labels, fontsize=9)
    axes[0].set_ylabel("Measured branching ratio", fontsize=10.1)
    axes[0].set_title("Branching ratio separates profiles from null", fontsize=11.2)
    axes[0].legend(fontsize=9, loc="upper right")
    _panel_label(axes[0], "A")

    sizes = report.get("avalanche_size_distribution", {}).get("sizes", [])
    if sizes:
        axes[1].hist(
            sizes,
            bins=max(3, min(12, len(set(sizes)))),
            color=colors["finite"],
            edgecolor=colors["boundary"],
        )
    else:
        axes[1].text(
            0.5,
            0.5,
            "no supra-threshold avalanches",
            ha="center",
            va="center",
            fontsize=10.1,
        )
    axes[1].set_xlabel("Avalanche size (summed channel flips)", fontsize=10.1)
    axes[1].set_ylabel("Count", fontsize=10.1)
    axes[1].set_title("Single-trace avalanche-size distribution", fontsize=11.2)
    axes[1].legend(
        handles=[
            Patch(
                facecolor=colors["finite"],
                edgecolor=colors["boundary"],
                label="avalanche sizes",
            )
        ],
        fontsize=9,
        loc="upper right",
    )
    _panel_label(axes[1], "B")

    fig.text(
        0.5,
        0.005,
        "Seeded software trajectory diagnostics; not evidence of neural avalanches, branching, or empirical criticality.",
        ha="center",
        fontsize=9,
        style="italic",
    )
    fig.suptitle(
        "Measured criticality signatures with null controls",
        fontsize=14,
        fontweight="bold",
    )
    fig.tight_layout(rect=(0, 0.03, 1, 0.96))
    return _save_return(
        fig, _fig_path(project_root, style, "criticality_signatures"), style["dpi"]
    )


def _compassion_scope_widening(
    project_root: Path, style: dict[str, Any], audit: dict[str, Any]
) -> Path:
    """Scope-of-concern widening (precision driver) plus the active per-channel action-influence."""
    colors = _semantic_colors(style)
    rows = audit["rows"]
    profiles = [_profile_label(row["deployment"]) for row in rows]
    real = np.array(audit["real_scope_asymmetries"], dtype=float)
    ablated = np.array(audit["ablated_scope_asymmetries"], dtype=float)
    influence = np.array(audit["channel_influence"], dtype=float)
    shuffled_mean = float(audit["mean_action_shuffled_influence"])
    channels = [f"b{index}" for index in range(len(influence))]
    x = np.arange(len(profiles))
    width = 0.34
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12.8, 5.1))
    ax.bar(
        x - width / 2,
        real,
        width,
        color=colors["finite"],
        label="separation prior active",
    )
    ax.bar(
        x + width / 2,
        ablated,
        width,
        color=colors["null"],
        hatch="//",
        edgecolor=colors["boundary"],
        label="precision-ablation control",
    )
    ax.axhline(
        0.0,
        color=colors["boundary"],
        linestyle="--",
        linewidth=1.0,
        label="self/non-self balance",
    )
    ax.set_xticks(x, profiles, fontsize=9)
    ax.set_ylabel("Scope asymmetry (non-self minus self concern)", fontsize=10.1)
    ax.set_title("Scope asymmetry shifts\nwith active prior", fontsize=10.8)
    ax.legend(fontsize=9, loc="upper left")
    _panel_label(ax, "C")
    channel_x = np.arange(len(channels))
    ax2.bar(
        channel_x,
        influence,
        0.6,
        color=colors["finite"],
        label="realised action-influence",
    )
    ax2.axhline(
        shuffled_mean,
        color=colors["null"],
        linestyle="--",
        linewidth=1.3,
        label="action-shuffled (pairing broken)",
    )
    ax2.set_xticks(channel_x, channels, fontsize=9)
    ax2.set_ylim(0.0, 1.05)
    ax2.set_ylabel(
        "Per-channel action-influence (fraction of baseline error)", fontsize=10.1
    )
    ax2.set_title("Action influence collapses\nunder shuffled pairing", fontsize=10.8)
    ax2.legend(fontsize=9, loc="upper right")
    _panel_label(ax2, "D")
    fig.text(
        0.5,
        0.02,
        "Finite policy-scope surrogate; not a measure of compassion, well-being, practice efficacy, or any affective outcome.",
        ha="center",
        fontsize=9,
        style="italic",
    )
    fig.tight_layout(rect=(0, 0.18, 1, 1))
    setattr(fig, "_layout_rect", (0.0, 0.18, 1.0, 1.0))
    return _save_return(
        fig, _fig_path(project_root, style, "compassion_scope_widening"), style["dpi"]
    )


def _practice_policy_scope_map(
    project_root: Path, style: dict[str, Any], practice_map: dict[str, Any]
) -> Path:
    """Render practice protocols as model-intervention deltas with on-figure safety boundaries."""
    colors = _semantic_colors(style)
    protocols = practice_map["protocols"]
    labels: list[str] = []
    values: list[float] = []
    bar_colors: list[str] = []
    for protocol in protocols:
        for name, delta in protocol["model_intervention"].items():
            labels.append(f"{protocol['id']}: {name}")
            values.append(float(delta))
            bar_colors.append(colors["finite"] if delta >= 0 else colors["blocked"])
    y = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(11.0, 0.6 * len(labels) + 2.2))
    ax.barh(y, values, color=bar_colors, edgecolor=colors["boundary"], linewidth=0.6)
    ax.axvline(
        0.0,
        color=colors["boundary"],
        linestyle="--",
        linewidth=1.0,
        label="no intervention",
    )
    ax.set_yticks(y, labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Model-intervention delta (software interface only)", fontsize=10.1)
    ax.set_title(
        "Practice protocols are bounded model interventions, not efficacy claims",
        fontsize=11.2,
    )
    ax.legend(
        handles=[
            Patch(
                facecolor=colors["finite"],
                edgecolor=colors["boundary"],
                label="increase",
            ),
            Patch(
                facecolor=colors["blocked"],
                edgecolor=colors["boundary"],
                label="decrease",
            ),
            Line2D([0], [0], color=colors["boundary"], linestyle="--", label="zero"),
        ],
        fontsize=9,
        loc="lower right",
    )
    _panel_label(ax, "P")
    boundary = " | ".join(
        f"{protocol['id']}: {protocol['safety_boundary']}" for protocol in protocols
    )
    fig.text(0.5, 0.005, boundary, ha="center", fontsize=9, style="italic", wrap=True)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    return _save_return(
        fig, _fig_path(project_root, style, "practice_policy_scope_map"), style["dpi"]
    )


def _separation_prior_emergence(
    project_root: Path, style: dict[str, Any], audit: dict[str, Any]
) -> Path:
    """Factored vs unfactored predictor error across the empowerment grid (section 4.1)."""
    colors = _semantic_colors(style)
    rows = sorted(audit["rows"], key=lambda row: row["empowerment"])
    empowerment = [row["empowerment"] for row in rows]
    factored = [row["factored_error"] for row in rows]
    unfactored = [row["unfactored_error"] for row in rows]
    advantage = [row["factored_advantage"] for row in rows]
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    ax.plot(
        empowerment,
        unfactored,
        marker="s",
        color=colors["blocked"],
        label="unfactored model error",
    )
    ax.plot(
        empowerment,
        factored,
        marker="o",
        color=colors["finite"],
        label="factored (self/env) model error",
    )
    ax.plot(
        empowerment,
        advantage,
        marker="^",
        color=colors["keep"],
        linestyle="--",
        label="factored advantage",
    )
    ax.axhline(0.0, color=colors["boundary"], linewidth=0.8)
    ax.set_xlabel("Empowerment (fraction of action-contingent channels)", fontsize=10.1)
    ax.set_ylabel("Mean bit error / advantage", fontsize=10.1)
    ax.set_title(
        "A factored model buys accuracy only when agency is present", fontsize=11.2
    )
    ax.legend(fontsize=9, loc="center left")
    _panel_label(ax, "E")
    fig.text(
        0.5,
        0.005,
        "Finite deterministic predictor comparison; not a developmental, neural, or empirical empowerment claim.",
        ha="center",
        fontsize=9,
        style="italic",
    )
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    return _save_return(
        fig, _fig_path(project_root, style, "separation_prior_emergence"), style["dpi"]
    )


def _internal_cut_unmeasurability(
    project_root: Path, style: dict[str, Any], audit: dict[str, Any]
) -> Path:
    """Internal-cut entropy (god's-eye) versus A's invariant accessible marginal (section 3.3)."""
    colors = _semantic_colors(style)
    rows = audit["rows"]
    labels = [
        f"{''.join(map(str, row['b1']))}|{''.join(map(str, row['b2']))}" for row in rows
    ]
    separable = [row["separable_cut_entropy_bits"] for row in rows]
    entangled = [row["entangled_cut_entropy_bits"] for row in rows]
    drift = [row["accessible_marginal_drift"] for row in rows]
    x = np.arange(len(rows))
    width = 0.34
    fig, ax = plt.subplots(figsize=(10.2, 4.6))
    ax.bar(
        x - width / 2,
        separable,
        width,
        color=colors["finite"],
        label="separable internal cut (god's-eye S)",
    )
    ax.bar(
        x + width / 2,
        entangled,
        width,
        color=colors["quantum"],
        label="entangled internal cut (god's-eye S)",
    )
    ax.plot(
        x,
        drift,
        marker="o",
        color=colors["boundary"],
        linestyle="none",
        label="A's accessible marginal drift (~0)",
    )
    ax.set_xticks(x, labels, fontsize=9, rotation=30, ha="right")
    ax.set_xlabel("Environment internal bipartition B1 | B2", fontsize=10.1)
    ax.set_ylabel("Entanglement entropy (bits)", fontsize=10.1)
    ax.set_title(
        "A cannot adjudicate the internal cut its marginal is invariant; only a god's-eye view differs",
        fontsize=10.6,
    )
    ax.legend(fontsize=9, loc="center right")
    _panel_label(ax, "G")
    fig.text(
        0.5,
        0.005,
        "Finite pure-state linear-algebra audit over environment bipartitions; not a physical or observer-boundary measurement.",
        ha="center",
        fontsize=9,
        style="italic",
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    return _save_return(
        fig,
        _fig_path(project_root, style, "internal_cut_unmeasurability"),
        style["dpi"],
    )


def _quantum_trajectory_unraveling(
    project_root: Path, style: dict[str, Any], trajectory: dict[str, Any]
) -> Path:
    colors = _semantic_colors(style)
    rows = trajectory["rows"]
    rates = trajectory["decoherence_rate_grid"]
    max_rate = max(rates)
    strong_rows = [
        row for row in rows if abs(row["decoherence_rate"] - max_rate) < 1e-9
    ]
    fig, axes = plt.subplots(1, 3, figsize=(14.0, 4.8))
    axes[0].plot(
        [row["time"] for row in strong_rows],
        [row["ensemble_global_entropy_bits"] for row in strong_rows],
        marker="o",
        color=colors["stochastic"],
        label="trajectory ensemble",
    )
    axes[0].plot(
        [row["time"] for row in strong_rows],
        [row["exact_global_entropy_bits"] for row in strong_rows],
        linestyle="--",
        color=colors["quantum"],
        label="exact Lindblad density",
    )
    axes[0].set_title("Entropy reconstruction\nat strongest rate")
    axes[0].set_xlabel("Time")
    axes[0].set_ylabel("Global entropy (bits)")
    axes[0].legend(fontsize=9)
    for rate in rates:
        subset = [row for row in rows if abs(row["decoherence_rate"] - rate) < 1e-9]
        axes[1].plot(
            [row["time"] for row in subset],
            [row["trace_distance_to_exact"] for row in subset],
            marker="o",
            linewidth=1.4,
            label=f"gamma={rate:g}",
        )
    axes[1].axhline(
        0.16,
        color=colors["blocked"],
        linestyle=":",
        linewidth=1,
        label="validation tolerance",
    )
    axes[1].set_title("Ensemble density stays\nnear exact solution")
    axes[1].set_xlabel("Time")
    axes[1].set_ylabel("Trace distance")
    axes[1].legend(fontsize=9)
    jump_rows = trajectory["jump_count_rows"]
    means = []
    lows = []
    highs = []
    for rate in rates:
        counts = np.array(
            [
                row["jump_count"]
                for row in jump_rows
                if abs(row["decoherence_rate"] - rate) < 1e-9
            ],
            dtype=float,
        )
        mean = float(counts.mean())
        sd = float(counts.std(ddof=1)) if len(counts) > 1 else 0.0
        half = 1.96 * sd / np.sqrt(max(1, len(counts)))
        means.append(mean)
        lows.append(mean - half)
        highs.append(mean + half)
    means_array = np.array(means)
    axes[2].bar(
        [f"{rate:g}" for rate in rates],
        means_array,
        color=colors["quantum"],
        yerr=np.vstack([means_array - np.array(lows), np.array(highs) - means_array]),
        capsize=3,
        label="jump-count mean with 95% CI",
    )
    axes[2].set_title("Jump counts vanish\nfor gamma=0 control")
    axes[2].set_xlabel("Dephasing rate gamma")
    axes[2].set_ylabel("Jumps per trajectory")
    axes[2].legend(fontsize=9)
    for label, ax in zip(("QA", "QB", "QC"), axes, strict=True):
        _panel_label(ax, label)
    fig.suptitle(
        "Seeded quantum trajectories unravel the finite Lindblad surrogate",
        fontsize=15.1,
        fontweight="bold",
    )
    setattr(fig, "_layout_rect", (0.0, 0.0, 1.0, 0.86))
    return _save_return(
        fig,
        _fig_path(project_root, style, "quantum_trajectory_unraveling"),
        style["dpi"],
    )


def _stochastic_effect_size_forest(
    project_root: Path, style: dict[str, Any], audit: dict[str, Any]
) -> Path:
    colors = _semantic_colors(style)
    rows = [
        row
        for row in audit["rows"]
        if row["metric"]
        in {"switch_rate", "mean_surprise", "mean_weighted_expected_free_energy"}
    ]
    metric_labels = {
        "switch_rate": "switch rate",
        "mean_surprise": "surprise",
        "mean_weighted_expected_free_energy": "weighted EFE",
    }
    rows = sorted(rows, key=lambda row: (row["profile"], row["metric"]))
    labels = [
        f"{_profile_label(row['profile'])} | {metric_labels[row['metric']]}"
        for row in rows
    ]
    y = np.arange(len(rows))
    effects = np.array([row["cliffs_delta"] for row in rows], dtype=float)
    p_values = np.array([row["holm_p"] for row in rows], dtype=float)
    fig, ax = plt.subplots(figsize=(10.8, 6.6))
    bar_colors = [
        colors["stochastic"] if value >= 0 else colors["null"] for value in effects
    ]
    bars = ax.barh(
        y, effects, color=bar_colors, edgecolor=colors["boundary"], linewidth=0.6
    )
    for bar, p_value in zip(bars, p_values, strict=True):
        if p_value >= 0.05:
            bar.set_hatch("//")
    previous_profile = None
    for index, row in enumerate(rows):
        if previous_profile is not None and row["profile"] != previous_profile:
            ax.axhline(index - 0.5, color=style["palette"]["grid"], linewidth=1.1)
        previous_profile = row["profile"]
    ax.axvline(
        0.0,
        color=colors["boundary"],
        linestyle="--",
        linewidth=1.0,
        label="no profile-null effect",
    )
    ax.set_yticks(y, labels)
    ax.tick_params(axis="y", labelsize=9)
    ax.invert_yaxis()
    lower = min(-1.02, float(effects.min()) - 0.15)
    upper = max(0.18, float(effects.max()) + 0.25)
    ax.set_xlim(lower, upper)
    ax.set_xlabel("Cliff's delta (profile ensemble minus null control)")
    ax.set_title("Seeded stochastic profile-null effect sizes with robustness labels")
    ax.legend(
        handles=[
            Patch(
                facecolor=colors["stochastic"],
                edgecolor=colors["boundary"],
                label="profile higher",
            ),
            Patch(
                facecolor=colors["null"],
                edgecolor=colors["boundary"],
                label="null higher",
            ),
            Patch(
                facecolor="white",
                edgecolor=colors["boundary"],
                hatch="//",
                label="Holm p >= 0.05",
            ),
            Line2D(
                [0], [0], color=colors["boundary"], linestyle="--", label="zero effect"
            ),
        ],
        title="Effect legend",
        fontsize=9,
        loc="upper left",
        bbox_to_anchor=(1.02, 1.0),
        ncol=1,
    )
    for index, row in enumerate(rows):
        effect_label = "profile higher" if effects[index] >= 0 else "null higher"
        interval = [
            row.get(
                "pooled_bootstrap_ci95_low", row.get("delta_profile_minus_null", 0.0)
            ),
            row.get(
                "pooled_bootstrap_ci95_high", row.get("delta_profile_minus_null", 0.0)
            ),
        ]
        ax.text(
            upper - 0.02,
            index,
            f"{effect_label}; Holm p={row['holm_p']:.3f}; CI[{interval[0]:.2f},{interval[1]:.2f}]",
            va="center",
            ha="right",
            fontsize=9,
            color=style["palette"]["muted"],
        )
    ax.grid(axis="x", color=style["palette"]["grid"], linewidth=0.5, alpha=0.55)
    _panel_label(ax, "SR")
    setattr(fig, "_layout_rect", (0.0, 0.10, 0.80, 1.0))
    return _save_return(
        fig,
        _fig_path(project_root, style, "stochastic_effect_size_forest"),
        style["dpi"],
    )


def _bmr_robustness_resampling(
    project_root: Path, style: dict[str, Any], audit: dict[str, Any]
) -> Path:
    colors = _semantic_colors(style)
    rows = audit["rows"]
    accesses = sorted({row["metacognitive_access"] for row in rows})
    precisions = sorted({row["prior_precision"] for row in rows})
    lookup = {
        (row["prior_precision"], row["metacognitive_access"]): row for row in rows
    }
    prune_matrix = np.array(
        [
            [lookup[(precision, access)]["pruning_rate"] for access in accesses]
            for precision in precisions
        ]
    )
    stable_matrix = np.array(
        [
            [
                1.0 if lookup[(precision, access)]["sign_stable"] else 0.0
                for access in accesses
            ]
            for precision in precisions
        ]
    )
    fig, axes = plt.subplots(
        1, 2, figsize=(13.2, 6.1), gridspec_kw={"width_ratios": [1.0, 1.12]}
    )
    image = axes[0].imshow(
        prune_matrix, aspect="auto", cmap="YlGnBu", vmin=0.0, vmax=1.0
    )
    for y_idx, precision in enumerate(precisions):
        for x_idx, access in enumerate(accesses):
            row = lookup[(precision, access)]
            axes[0].text(
                x_idx,
                y_idx,
                f"{row['pruning_rate']:.0%}\n{'stable' if row['sign_stable'] else 'mixed'}",
                ha="center",
                va="center",
                fontsize=9,
                color=_heatmap_text_color(image, prune_matrix[y_idx, x_idx]),
                fontweight="bold",
            )
    axes[0].set_xticks(range(len(accesses)), [f"{value:g}" for value in accesses])
    axes[0].set_yticks(range(len(precisions)), [f"{value:g}" for value in precisions])
    _add_heatmap_cell_grid(axes[0], len(precisions), len(accesses))
    axes[0].set_xlabel("Metacognitive access")
    axes[0].set_ylabel("Separation-prior precision")
    axes[0].set_title("Pruning-rate robustness")
    cbar = fig.colorbar(image, ax=axes[0], fraction=0.04, pad=0.02)
    cbar.set_label("Bootstrap pruning rate over noise rows")
    stable_cmap = ListedColormap(
        [style["palette"]["warning"], style["palette"]["secondary"]]
    )
    stable = axes[1].imshow(
        stable_matrix, aspect="auto", cmap=stable_cmap, vmin=0.0, vmax=1.0
    )
    axes[1].set_xticks(range(len(accesses)), [f"{value:g}" for value in accesses])
    axes[1].set_yticks(range(len(precisions)), [f"{value:g}" for value in precisions])
    _add_heatmap_cell_grid(axes[1], len(precisions), len(accesses))
    axes[1].set_xlabel("Metacognitive access")
    axes[1].set_title("Delta-F sign stability (CI low/high)")
    for y_idx, precision in enumerate(precisions):
        for x_idx, access in enumerate(accesses):
            row = lookup[(precision, access)]
            label = "prune" if row["mean_delta_free_energy"] < 0 else "keep"
            axes[1].text(
                x_idx,
                y_idx,
                f"{label}\n{row['delta_ci95_low']:+.1f}\n{row['delta_ci95_high']:+.1f}",
                ha="center",
                va="center",
                fontsize=9,
                color=_heatmap_text_color(stable, stable_matrix[y_idx, x_idx]),
                fontweight="bold",
            )
    stable_cbar = fig.colorbar(stable, ax=axes[1], fraction=0.04, pad=0.02)
    stable_cbar.set_label("Delta-F sign")
    stable_cbar.set_ticks([0.25, 0.75])
    stable_cbar.set_ticklabels(["mixed", "stable"])
    fig.legend(
        handles=[
            Patch(facecolor=colors["prune"], label="prune: mean Delta F < 0"),
            Patch(facecolor=colors["keep"], label="keep: mean Delta F >= 0"),
        ],
        title="Decision legend",
        fontsize=9,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.08),
        ncol=2,
    )
    _panel_label(axes[0], "BR")
    _panel_label(axes[1], "BS")
    return _save_return(
        fig, _fig_path(project_root, style, "bmr_robustness_resampling"), style["dpi"]
    )


def _quantum_trajectory_convergence(
    project_root: Path, style: dict[str, Any], audit: dict[str, Any]
) -> Path:
    colors = _semantic_colors(style)
    rows = audit["rows"]
    counts = np.array([row["trajectory_count"] for row in rows], dtype=float)
    residuals = np.array(
        [row["max_trace_distance_to_exact"] for row in rows], dtype=float
    )
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.1))
    axes[0].plot(
        counts,
        residuals,
        marker="o",
        color=colors["quantum"],
        label="max trace distance",
    )
    axes[0].axhline(
        0.16,
        color=colors["blocked"],
        linestyle=":",
        linewidth=1.3,
        label="trajectory tolerance",
    )
    axes[0].set_xscale("log", base=2)
    axes[0].set_xlabel("Trajectory count")
    axes[0].set_ylabel("Max trace distance to exact Lindblad density")
    axes[0].set_title("Trajectory ensemble residual convergence")
    axes[0].legend(title="Line legend", fontsize=9)
    control = audit["too_few_trajectory_control"]
    bars = axes[1].bar(
        ["too few\ncontrol", "largest\nensemble"],
        [control["max_trace_distance_to_exact"], residuals[-1]],
        color=[colors["blocked"], colors["stochastic"]],
        edgecolor=colors["boundary"],
        linewidth=0.7,
    )
    bars[0].set_hatch("..")
    axes[1].axhline(
        0.16, color=colors["boundary"], linestyle="--", label="pass/fail threshold"
    )
    axes[1].set_ylabel("Max trace distance")
    axes[1].set_title("Negative control fails before interpretation")
    axes[1].legend(fontsize=9)
    axes[1].text(
        0,
        control["max_trace_distance_to_exact"] + 0.01,
        "fails",
        ha="center",
        fontsize=9,
    )
    axes[1].text(1, residuals[-1] + 0.01, "passes", ha="center", fontsize=9)
    _panel_label(axes[0], "QC")
    _panel_label(axes[1], "QD")
    return _save_return(
        fig,
        _fig_path(project_root, style, "quantum_trajectory_convergence"),
        style["dpi"],
    )


def _visual_semantic_palette_ledger(project_root: Path, style: dict[str, Any]) -> Path:
    colors = _semantic_colors(style)
    roles = [
        "pass",
        "fail",
        "keep",
        "prune",
        "finite",
        "blocked",
        "stochastic",
        "null",
        "quantum",
        "boundary",
    ]
    fig, ax = plt.subplots(figsize=(10.4, 5.0))
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, len(roles))
    ax.axis("off")
    ax.text(
        1.45,
        len(roles) - 0.25,
        "role",
        fontsize=9,
        fontweight="bold",
        color=style["palette"]["muted"],
    )
    ax.text(
        3.2,
        len(roles) - 0.25,
        "color",
        fontsize=9,
        fontweight="bold",
        color=style["palette"]["muted"],
    )
    ax.text(
        5.1,
        len(roles) - 0.25,
        "non-color cue",
        fontsize=9,
        fontweight="bold",
        color=style["palette"]["muted"],
    )
    ax.text(
        7.45,
        len(roles) - 0.25,
        "governance use",
        fontsize=9,
        fontweight="bold",
        color=style["palette"]["muted"],
    )
    for index, role in enumerate(roles):
        y = len(roles) - index - 0.7
        hatch = ".." if role == "blocked" else "//" if role == "null" else ""
        cue = (
            "hatched blocked"
            if role == "blocked"
            else "hatched null/control"
            if role == "null"
            else "solid color"
        )
        ax.add_patch(
            plt.Rectangle(
                (0.4, y - 0.25),
                0.85,
                0.5,
                facecolor=colors[role],
                edgecolor=colors["boundary"],
                hatch=hatch,
            )
        )
        ax.text(1.45, y, role, va="center", fontsize=11.2, fontweight="bold")
        ax.text(3.2, y, colors[role], va="center", fontsize=10.1)
        ax.text(
            5.1, y, cue, va="center", fontsize=10.1, color=style["palette"]["muted"]
        )
        ax.text(
            7.45,
            y,
            "semantic role reused across figures",
            va="center",
            fontsize=10.1,
            color=style["palette"]["muted"],
        )
    ax.legend(
        handles=[
            Patch(facecolor=colors["pass"], label="pass / validated finite check"),
            Patch(
                facecolor=colors["blocked"], hatch="..", label="blocked stronger claim"
            ),
            Patch(
                facecolor=colors["null"], hatch="//", label="null or negative control"
            ),
        ],
        title="Palette legend",
        fontsize=9,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.03),
        ncol=3,
    )
    ax.set_title("Shared semantic palette and non-color encodings")
    _panel_label(ax, "VS")
    return _save_return(
        fig,
        _fig_path(project_root, style, "visual_semantic_palette_ledger"),
        style["dpi"],
    )


def _method_assumption_failure_map(
    project_root: Path,
    style: dict[str, Any],
    ledger: dict[str, Any],
    controls: dict[str, Any],
) -> Path:
    colors = _semantic_colors(style)
    methods = ledger["rows"]
    control_counts = {}
    for row in controls["rows"]:
        control_counts[row["method_id"]] = control_counts.get(row["method_id"], 0) + 1
    columns = [
        "hard\nconstraints",
        "modeling\nchoices",
        "assumptions",
        "evidence\nceiling",
        "negative\ncontrols",
    ]
    label_map = {
        "finite_qrf_boundary_screen": "finite QRF screen",
        "bmr_separation_prior_sweep": "BMR prior sweep",
        "pymdp_active_inference_profiles": "pymdp profiles",
        "seeded_stochastic_policy_ensemble": "stochastic ensemble",
        "quantum_trajectory_unraveling": "quantum trajectory",
        "contextuality_and_measurement_cover_engines": "contextuality cover",
        "practice_protocol_adapter": "practice adapter",
        "visual_and_claim_governance": "visual/claim governance",
    }
    matrix = np.array(
        [
            [
                1.0 if method["hard_constraints"] else 0.0,
                1.0 if method["modeling_choices"] else 0.0,
                1.0 if method["assumptions"] else 0.0,
                1.0 if method["evidence_ceiling"] else 0.0,
                1.0 if control_counts.get(method["method_id"], 0) else 0.0,
            ]
            for method in methods
        ]
    )
    fig, ax = plt.subplots(figsize=(12.2, 7.0))
    image = ax.imshow(matrix, aspect="auto", cmap="YlGnBu", vmin=0, vmax=1)
    ax.set_xticks(range(len(columns)), columns)
    ax.set_yticks(
        range(len(methods)),
        [
            label_map.get(method["method_id"], method["method_id"].replace("_", " "))
            for method in methods
        ],
    )
    ax.tick_params(axis="y", labelsize=12, pad=8)
    for y_idx, method in enumerate(methods):
        for x_idx in range(len(columns)):
            value = int(matrix[y_idx, x_idx])
            label = "Y" if value else "N"
            if x_idx == len(columns) - 1:
                label = str(control_counts.get(method["method_id"], 0))
            text_color = "white" if value else colors["boundary"]
            ax.text(
                x_idx,
                y_idx,
                label,
                ha="center",
                va="center",
                fontsize=10.1,
                fontweight="bold",
                color=text_color,
            )
    ax.set_title("Method assumptions and falsification coverage")
    _binary_colorbar(fig, image, ax, "contract present")
    ax.legend(
        handles=[
            Patch(
                facecolor=style["palette"]["secondary"], label="method contract present"
            ),
            Patch(
                facecolor="white",
                edgecolor=style["palette"]["primary"],
                label="cell text gives Y/N or control count",
            ),
        ],
        title="Contract legend",
        fontsize=9,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.1),
        ncol=2,
    )
    _panel_label(ax, "MF")
    return _save_return(
        fig,
        _fig_path(project_root, style, "method_assumption_failure_map"),
        style["dpi"],
    )


def _claim_graph(
    project_root: Path, style: dict[str, Any], crosswalk: dict[str, Any]
) -> Path:
    rows = crosswalk["claims"]
    fig, ax = plt.subplots(figsize=(10.8, max(5.2, len(rows) * 0.36)))
    y = np.arange(len(rows))
    ax.scatter([0] * len(rows), y, color=style["palette"]["primary"])
    ax.scatter([1] * len(rows), y, color=style["palette"]["secondary"])
    ax.scatter([2] * len(rows), y, color=style["palette"]["accent"])
    for idx, row in enumerate(rows):
        ax.plot([0, 1, 2], [idx, idx, idx], color=style["palette"]["grid"], linewidth=1)
        ax.text(-0.08, idx, row["id"], va="center", ha="right", fontsize=9)
        ax.text(
            2.12,
            idx,
            row.get("gate", row["id"]),
            va="center",
            fontsize=9,
            color=style["palette"]["muted"],
        )
    ax.set_xlim(-1.45, 3.85)
    ax.set_ylim(-0.5, len(rows) - 0.5)
    ax.set_yticks([])
    ax.set_xticks([0, 1, 2], ["claim", "source", "gate"])
    ax.grid(axis="y", color=style["palette"]["grid"], linewidth=0.35, alpha=0.35)
    ax.set_title("Claim-source-validation bindings")
    ax.legend(
        handles=[
            Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor=style["palette"]["primary"],
                label="claim node",
            ),
            Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor=style["palette"]["secondary"],
                label="source node",
            ),
            Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor=style["palette"]["accent"],
                label="gate node",
            ),
            Line2D([0], [0], color=style["palette"]["grid"], label="validated binding"),
        ],
        fontsize=9,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.06),
        ncol=4,
    )
    return _save_return(
        fig,
        _fig_path(project_root, style, "claim_source_validation_graph"),
        style["dpi"],
    )


def _scholarship_coverage(
    project_root: Path, style: dict[str, Any], matrix_payload: dict[str, Any]
) -> Path:
    tracks = matrix_payload["tracks"]
    rows = matrix_payload["rows"]
    matrix = np.array(
        [[1.0 if row["tracks"].get(track) else 0.0 for track in tracks] for row in rows]
    )
    labels = [row["citation_key"] for row in rows]
    fig, ax = plt.subplots(figsize=(10.8, max(6.2, len(labels) * 0.27)))
    image = ax.imshow(matrix, aspect="auto", cmap="Greens", vmin=0, vmax=1)
    ax.set_xticks(range(len(tracks)), tracks, rotation=35, ha="right")
    ax.set_yticks(range(len(labels)), labels)
    ax.set_xticks(np.arange(-0.5, len(tracks), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(labels), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=0.7)
    for y_idx in range(matrix.shape[0]):
        for x_idx in range(matrix.shape[1]):
            if matrix[y_idx, x_idx]:
                ax.text(
                    x_idx,
                    y_idx,
                    "Y",
                    ha="center",
                    va="center",
                    fontsize=9,
                    color=style["palette"]["primary"],
                    fontweight="bold",
                )
    ax.tick_params(axis="y", labelsize=9)
    ax.set_title("Scholarship coverage by track")
    ax.set_xlabel("Model track")
    ax.set_ylabel("Citation key")
    _binary_colorbar(fig, image, ax, "track support")
    _panel_label(ax, "V")
    return _save_return(
        fig, _fig_path(project_root, style, "scholarship_coverage_matrix"), style["dpi"]
    )


def _claim_support_matrix(
    project_root: Path, style: dict[str, Any], audit: dict[str, Any]
) -> Path:
    class_order = {
        "operational_surrogate": 0,
        "implemented_model": 1,
        "finite_sweep": 2,
        "finite_quantum_simulation": 3,
        "runtime_canary": 4,
        "proxy_boundary": 5,
        "safety_boundary": 6,
        "background_boundary": 7,
        "implementation_boundary": 8,
    }
    claim_kind = {
        row["claim_id"]: row["claim_kind"]
        for row in audit["support_rows"]
        if row["public_crosswalk_claim"]
    }
    public_claims = sorted(
        {
            row["claim_id"]
            for row in audit["support_rows"]
            if row["public_crosswalk_claim"]
        },
        key=lambda claim: (class_order.get(claim_kind.get(claim, ""), 99), claim),
    )
    citation_keys = sorted(
        {
            row["citation_key"]
            for row in audit["support_rows"]
            if row["public_crosswalk_claim"]
        }
    )
    lookup = {
        (row["claim_id"], row["citation_key"])
        for row in audit["support_rows"]
        if row["public_crosswalk_claim"]
    }
    matrix = np.array(
        [
            [1.0 if (claim, citation) in lookup else 0.0 for citation in citation_keys]
            for claim in public_claims
        ]
    )
    fig, ax = plt.subplots(figsize=(18.6, 8.8))
    image = ax.imshow(matrix, aspect="auto", cmap="Blues", vmin=0, vmax=1)
    ax.set_xticks(
        range(len(citation_keys)),
        [_compact_axis_label(key, 15) for key in citation_keys],
        rotation=58,
        ha="right",
        rotation_mode="anchor",
    )
    ax.set_yticks(range(len(public_claims)), public_claims)
    ax.tick_params(axis="both", labelsize=9)
    ax.set_xticks(np.arange(-0.5, len(citation_keys), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(public_claims), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=0.65)
    for y_idx in range(matrix.shape[0]):
        for x_idx in range(matrix.shape[1]):
            if matrix[y_idx, x_idx]:
                ax.text(
                    x_idx,
                    y_idx,
                    "o",
                    ha="center",
                    va="center",
                    fontsize=9,
                    color=style["palette"]["primary"],
                    fontweight="bold",
                )
    group_midpoints: list[float] = []
    group_labels: list[str] = []
    previous_kind = None
    group_start = 0
    for y_idx, claim in enumerate(public_claims):
        kind = claim_kind.get(claim, "")
        if previous_kind is not None and kind != previous_kind:
            ax.axhline(y_idx - 0.5, color="white", linewidth=1.6)
            group_midpoints.append((group_start + y_idx - 1) / 2)
            group_labels.append(previous_kind.replace("_", " "))
            group_start = y_idx
        previous_kind = kind
    if public_claims:
        group_midpoints.append((group_start + len(public_claims) - 1) / 2)
        group_labels.append(claim_kind.get(public_claims[-1], "").replace("_", " "))
    ax.set_xlim(-0.5, len(citation_keys) + 4.5)
    for midpoint, label in zip(group_midpoints, group_labels, strict=True):
        ax.text(
            len(citation_keys) + 0.15,
            midpoint,
            label,
            ha="left",
            va="center",
            fontsize=9,
            color=style["palette"]["muted"],
            clip_on=False,
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.82, "pad": 1.0},
        )
    ax.text(
        len(citation_keys) + 0.15,
        -0.95,
        "claim class",
        ha="left",
        va="bottom",
        fontsize=9,
        fontweight="bold",
        clip_on=False,
    )
    ax.set_title("Scoped public-claim support by citation key")
    ax.set_xlabel("Citation key (abbreviated; full keys in source audit)")
    ax.set_ylabel("Claim ID")
    colorbar = fig.colorbar(
        image, ax=ax, orientation="vertical", fraction=0.018, pad=0.065
    )
    colorbar.set_ticks([0, 1])
    colorbar.set_ticklabels(["absent", "present"])
    colorbar.set_label("scoped citation support")
    _panel_label(ax, "W")
    return _save_return(
        fig, _fig_path(project_root, style, "claim_support_matrix"), style["dpi"]
    )


def _manuscript_claim_audit(
    project_root: Path, style: dict[str, Any], audit: dict[str, Any]
) -> Path:
    labels = ["citations resolved", "claim IDs present", "positive claims absent"]
    values = [
        1.0 if not audit["missing_bibliography_keys"] else 0.0,
        1.0 if not audit["missing_claim_mentions"] else 0.0,
        1.0 if not audit["forbidden_positive_claims"] else 0.0,
    ]
    colors = [
        style["palette"]["accent"] if value else style["palette"]["warning"]
        for value in values
    ]
    fig, ax = plt.subplots(figsize=(7.5, 3.2))
    ax.bar(labels, values, color=colors)
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("Gate passed")
    ax.set_title("Manuscript claim audit")
    ax.tick_params(axis="x", rotation=12)
    for index, value in enumerate(values):
        ax.text(
            index, value + 0.04, "pass" if value else "fail", ha="center", fontsize=9
        )
    ax.legend(
        handles=[
            Patch(color=style["palette"]["accent"], label="gate passed"),
            Patch(color=style["palette"]["warning"], label="gate failed"),
        ],
        fontsize=9,
        loc="lower right",
    )
    _panel_label(ax, "X")
    return _save_return(
        fig, _fig_path(project_root, style, "manuscript_claim_audit"), style["dpi"]
    )


def _evidence_ceiling_stress_matrix(
    project_root: Path, style: dict[str, Any], audit: dict[str, Any]
) -> Path:
    stressors = [row["id"] for row in audit["stressors"]]
    class_order = {
        "operational_surrogate": 0,
        "implemented_model": 1,
        "finite_sweep": 2,
        "finite_quantum_simulation": 3,
        "runtime_canary": 4,
        "proxy_boundary": 5,
        "safety_boundary": 6,
        "background_boundary": 7,
        "implementation_boundary": 8,
    }
    rows = sorted(
        audit["rows"],
        key=lambda row: (
            class_order.get(row.get("claim_status", ""), 99),
            row["claim_id"],
        ),
    )
    matrix = np.array(
        [
            [1.0 if row["stressors"].get(stressor) else 0.0 for stressor in stressors]
            for row in rows
        ]
    )
    labels = [row["claim_id"] for row in rows]
    fig, ax = plt.subplots(figsize=(11.2, 6.4))
    image = ax.imshow(matrix, aspect="auto", cmap="Oranges", vmin=0, vmax=1)
    ax.set_xticks(range(len(stressors)), stressors, rotation=35, ha="right")
    ax.set_yticks(range(len(labels)), labels)
    ax.tick_params(axis="both", labelsize=9)
    group_midpoints = []
    group_labels = []
    previous_status = None
    group_start = 0
    for y_idx, row in enumerate(rows):
        status = row.get("claim_status", "")
        if previous_status is not None and status != previous_status:
            ax.axhline(y_idx - 0.5, color="white", linewidth=1.6)
            group_midpoints.append((group_start + y_idx - 1) / 2)
            group_labels.append(previous_status.replace("_", " "))
            group_start = y_idx
        previous_status = status
    if rows:
        group_midpoints.append((group_start + len(rows) - 1) / 2)
        group_labels.append(rows[-1].get("claim_status", "").replace("_", " "))
    ax2 = ax.twinx()
    ax2.set_ylim(ax.get_ylim())
    ax2.set_yticks(group_midpoints)
    ax2.set_yticklabels(group_labels)
    ax2.spines["right"].set_position(("axes", 1.03))
    ax2.tick_params(axis="y", labelsize=9, length=0, pad=5)
    ax2.set_ylabel("Claim class", labelpad=14)
    ax.set_title("Evidence ceilings by claim class")
    ax.set_xlabel("Boundary stressor")
    ax.set_ylabel("Public claim ID")
    colorbar = fig.colorbar(
        image,
        ax=ax,
        orientation="horizontal",
        location="top",
        fraction=0.035,
        pad=0.075,
        shrink=0.32,
        aspect=12,
    )
    colorbar.set_ticks([0, 1])
    colorbar.set_ticklabels(["absent", "present"])
    colorbar.ax.xaxis.set_ticks_position("bottom")
    colorbar.ax.tick_params(labelsize=8, pad=1, labeltop=False, labelbottom=True)
    _panel_label(ax, "Y")
    return _save_return(
        fig,
        _fig_path(project_root, style, "evidence_ceiling_stress_matrix"),
        style["dpi"],
    )


def _claim_context_evidence_ladder(
    project_root: Path, style: dict[str, Any], ledger: dict[str, Any]
) -> Path:
    colors = _semantic_colors(style)
    class_order = {
        "operational_surrogate": 0,
        "implemented_model": 1,
        "finite_sweep": 2,
        "finite_quantum_simulation": 3,
        "runtime_canary": 4,
        "proxy_boundary": 5,
        "safety_boundary": 6,
        "background_boundary": 7,
        "implementation_boundary": 8,
    }
    rows = sorted(
        ledger["rows"],
        key=lambda row: (
            class_order.get(row.get("evidence_class", ""), 99),
            row["claim_id"],
        ),
    )
    y_positions = np.arange(len(rows))
    support_counts = np.array([row["source_role_count"] for row in rows], dtype=float)
    max_support = max(float(np.max(support_counts)), 1.0)
    class_palette = {
        "operational_surrogate": "#93c5fd",
        "implemented_model": "#60a5fa",
        "finite_sweep": "#34d399",
        "finite_quantum_simulation": "#818cf8",
        "runtime_canary": "#fbbf24",
        "proxy_boundary": "#f59e0b",
        "safety_boundary": "#fb7185",
        "background_boundary": "#a78bfa",
        "implementation_boundary": "#38bdf8",
    }
    bar_colors = [
        class_palette.get(row.get("evidence_class", ""), colors["finite"])
        for row in rows
    ]

    gate_x = max_support + 0.55
    blocked_x = max_support + 1.25
    fig, ax = plt.subplots(figsize=(12.4, 7.1))
    ax.barh(
        y_positions,
        support_counts,
        color=bar_colors,
        edgecolor=colors["boundary"],
        linewidth=0.55,
        label="scoped source-role count",
    )
    ax.scatter(
        np.full_like(y_positions, gate_x, dtype=float),
        y_positions,
        marker="o",
        s=42,
        color=colors["pass"],
        edgecolor="white",
        linewidth=0.8,
        zorder=4,
    )
    for y_idx, row in enumerate(rows):
        ax.barh(
            y_idx,
            0.18,
            left=blocked_x - 0.09,
            height=0.54,
            color=colors["blocked"],
            edgecolor=colors["boundary"],
            hatch="..",
            linewidth=0.6,
            zorder=3,
        )

    class_groups: list[tuple[str, float]] = []
    previous_class = rows[0].get("evidence_class", "") if rows else None
    group_start = 0
    for y_idx, row in enumerate(rows):
        evidence_class = row.get("evidence_class", "")
        if previous_class is not None and evidence_class != previous_class:
            ax.axhline(y_idx - 0.5, color=style["palette"]["grid"], linewidth=1.2)
            class_groups.append((previous_class, (group_start + y_idx - 1) / 2.0))
            group_start = y_idx
        previous_class = evidence_class
    if rows:
        class_groups.append((str(previous_class), (group_start + len(rows) - 1) / 2.0))
    ax.set_yticks(y_positions, [row["claim_id"] for row in rows])
    ax.tick_params(axis="y", labelsize=9)
    ax.set_xlabel("Scoped source-role count (context breadth, not evidence strength)")
    ax.set_title(
        "Public claims: context breadth and blocked stronger readings",
        fontsize=17,
        pad=18,
    )
    ax.set_xlim(0, max_support + 1.75)
    ax.set_ylim(len(rows) - 0.4, -1.08)
    ax.text(
        gate_x,
        -0.58,
        "gate",
        ha="center",
        va="center",
        rotation=90,
        fontsize=8.4,
        fontweight="bold",
        color=colors["pass"],
    )
    ax.text(
        blocked_x,
        -0.58,
        "blocked",
        ha="center",
        va="center",
        rotation=90,
        fontsize=8.4,
        fontweight="bold",
        color=colors["blocked"],
    )
    if class_groups:
        class_axis = ax.twinx()
        class_axis.set_ylim(ax.get_ylim())
        class_axis.set_yticks(
            [y_center for _, y_center in class_groups],
            [evidence_class.replace("_", " ") for evidence_class, _ in class_groups],
        )
        class_axis.tick_params(
            axis="y", labelsize=8.2, length=0, pad=9, colors=colors["boundary"]
        )
        class_axis.set_ylabel(
            "Evidence class",
            fontsize=8.8,
            fontweight="bold",
            color=colors["boundary"],
            labelpad=18,
        )
        class_axis.grid(False)
        for spine in class_axis.spines.values():
            spine.set_visible(False)
    ax.grid(axis="x", color=style["palette"]["grid"], linewidth=0.6, alpha=0.6)
    legend_handles = [
        Patch(
            facecolor=class_palette["operational_surrogate"],
            edgecolor=colors["boundary"],
            label="bar length = scoped source roles",
        ),
        Patch(
            facecolor=class_palette["finite_sweep"],
            edgecolor=colors["boundary"],
            label="bar color/right axis = evidence class",
        ),
    ]
    ax.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.17),
        ncol=2,
        fontsize=9,
        frameon=True,
    )
    setattr(fig, "_layout_rect", (0.0, 0.18, 0.9, 1.0))
    return _save_return(
        fig,
        _fig_path(project_root, style, "claim_context_evidence_ladder"),
        style["dpi"],
    )


def _formalism_operation_map(
    project_root: Path, style: dict[str, Any], audit: dict[str, Any]
) -> Path:
    rows = audit["rows"]
    columns = ["source mapped", "finite calc", "surrogate boundary", "value bound"]
    matrix = []
    for row in rows:
        note = row.get("surrogate_note", "").lower()
        matrix.append(
            [
                1.0,
                1.0 if row.get("computable") else 0.0,
                1.0 if "surrogate" in note or not row.get("computable") else 0.0,
                1.0 if row.get("value_key") else 0.0,
            ]
        )
    fig, ax = plt.subplots(figsize=(8, 6.2))
    image = ax.imshow(np.array(matrix), aspect="auto", cmap="YlGnBu", vmin=0, vmax=1)
    ax.set_xticks(range(len(columns)), columns, rotation=25, ha="right")
    ax.set_yticks(range(len(rows)), [f"Eq {row['number']}" for row in rows])
    ax.tick_params(axis="both", labelsize=9)
    for y_idx, row in enumerate(rows):
        ax.text(len(columns) + 0.08, y_idx, row["label"], va="center", fontsize=9)
    ax.set_xlim(-0.5, len(columns) + 3.2)
    ax.set_title("Equation operational status")
    _binary_colorbar(fig, image, ax, "status present")
    _panel_label(ax, "Z")
    return _save_return(
        fig, _fig_path(project_root, style, "formalism_operation_map"), style["dpi"]
    )


def _quantum_roadmap_readiness_matrix(
    project_root: Path, style: dict[str, Any], readiness: dict[str, Any]
) -> Path:
    rows = readiness["rows"]
    columns = readiness["columns"]
    matrix = np.array(
        [[1.0 if row[column] else 0.0 for column in columns] for row in rows]
    )
    label_lookup = {
        "two_qubit_separability_entropy": "separability\nentropy",
        "arbitrary_two_qubit_entanglement_audit": "mixed-state\nentanglement",
        "chsh_contextuality_witness": "CHSH\nwitness",
        "chsh_measurement_cover_table": "CHSH cover\n+ LP",
        "general_measurement_cover_polytope_audit": "general cover\n+ LP",
        "qrf_basis_invariance_toy": "basis\ninvariance",
        "boundary_landauer_entropy": "Landauer\nbound",
        "thermodynamic_channel_cost_audit": "channel\ncost",
        "two_qubit_dephasing_channel": "dephasing\nchannel",
        "full_open_system_qfep_dynamics": "qFEP\ndynamics",
        "many_body_boundary_screens": "many-body\nscreens",
        "sparse_boundary_screen_scaling_audit": "sparse screen\nscaling",
        "general_sheaf_contextuality_engine": "sheaf\nengine",
        "qrf_transformation_library": "QRF\ntransforms",
        "qrf_frame_covariance_toy_audit": "QRF frame\ncovariance",
        "empirical_adapter": "empirical\nadapter",
    }
    fig, ax = plt.subplots(figsize=(12.0, 9.6))
    image = ax.imshow(matrix, aspect="auto", cmap="YlGnBu", vmin=0, vmax=1)
    ax.set_xticks(
        range(len(columns)), [column.replace("_", "\n") for column in columns]
    )
    ax.set_yticks(
        range(len(rows)),
        [label_lookup.get(row["id"], row["id"].replace("_", "\n")) for row in rows],
    )
    ax.tick_params(axis="both", labelsize=9)
    for y_idx, row in enumerate(rows):
        for x_idx, column in enumerate(columns):
            color = "white" if row[column] else style["palette"]["primary"]
            ax.text(
                x_idx,
                y_idx,
                "Y" if row[column] else "N",
                ha="center",
                va="center",
                fontsize=9,
                color=color,
            )
        state = (
            "finite validated"
            if row["roadmap_class"] == "implemented"
            else "blocked roadmap"
        )
        ax.text(len(columns) + 0.15, y_idx, state, va="center", fontsize=9)
    ax.set_xlim(-0.5, len(columns) + 1.7)
    ax.set_title("Quantum roadmap readiness and claim boundary")
    _binary_colorbar(fig, image, ax, "criterion satisfied")
    handles = [
        Patch(
            facecolor="#7fcdbb",
            edgecolor=style["palette"]["primary"],
            label="Y: criterion satisfied",
        ),
        Patch(
            facecolor="#f7fcf0",
            edgecolor=style["palette"]["primary"],
            label="N: criterion absent or blocked",
        ),
    ]
    ax.legend(
        handles=handles,
        title="Readiness legend",
        bbox_to_anchor=(0.5, -0.13),
        loc="upper center",
        ncol=2,
        fontsize=9,
    )
    _panel_label(ax, "AA")
    return _save_return(
        fig,
        _fig_path(project_root, style, "quantum_roadmap_readiness_matrix"),
        style["dpi"],
    )


def boundary_use_ontology_verdicts(audit: dict[str, Any]) -> dict[str, Any]:
    """Derive the use/ontology lane verdicts from the indistinguishability audit flags.

    The figure headline (not just its footnote) reads these, so a flipped audit flag
    cannot leave a green verdict standing. Pure function so the binding is regression-tested.
    """
    admissible_equal = bool(audit.get("all_admissible_distributions_equal"))
    control_fails = bool(audit.get("negative_control_fails"))
    return {
        "use": {
            "ok": admissible_equal,
            "head": "USE is licensed"
            if admissible_equal
            else "USE not confirmed: frames differ",
            "mark": "OK" if admissible_equal else "??",
        },
        "ontology": {
            "ok": control_fails,
            "head": "ONTOLOGY is not licensed"
            if control_fails
            else "audit incomplete: control did not fail",
            "mark": "NO" if control_fails else "??",
        },
    }


def separation_prior_lifecycle(bmr: dict[str, Any]) -> dict[str, Any]:
    """Derive the separation-prior net-value lifecycle from the BMR sweep.

    Returns the per-precision Delta F series, which precision(s) actually cross keep -> prune,
    the bolded arc precision (weakest crosser), the interpolated crossing access, and whether
    the non-arc precisions are pruned throughout. Derived from data, never assumed, so the
    figure's lifecycle claim is regression-tested rather than green-by-construction.
    """
    rows = bmr["rows"]
    accesses = sorted({row["metacognitive_access"] for row in rows})
    precisions = sorted({row["prior_precision"] for row in rows})
    lookup = {
        (row["prior_precision"], row["metacognitive_access"]): row for row in rows
    }
    missing = [(p, a) for p in precisions for a in accesses if (p, a) not in lookup]
    if missing:
        raise ValueError(
            f"bmr_sweep grid is ragged; missing {len(missing)} cells e.g. {missing[:3]}"
        )
    series = {
        p: [float(lookup[(p, a)]["delta_free_energy"]) for a in accesses]
        for p in precisions
    }

    def _crosses(net: list[float]) -> bool:
        return any(net[idx - 1] > 0 >= net[idx] for idx in range(1, len(net)))

    crossing_precisions = [p for p in precisions if _crosses(series[p])]
    arc_precision = min(crossing_precisions) if crossing_precisions else min(precisions)
    crossing = None
    net = series[arc_precision]
    for idx in range(1, len(accesses)):
        if net[idx - 1] > 0 >= net[idx]:
            # The trigger guarantees y0 > 0 >= y1, so y0 - y1 > 0; linear interpolation is safe.
            x0, x1, y0, y1 = accesses[idx - 1], accesses[idx], net[idx - 1], net[idx]
            crossing = x0 + (x1 - x0) * (y0 / (y0 - y1))
            break
    others_pruned = all(max(series[p]) <= 0 for p in precisions if p != arc_precision)
    return {
        "accesses": accesses,
        "precisions": precisions,
        "series": series,
        "crossing_precisions": crossing_precisions,
        "arc_precision": arc_precision,
        "crossing": crossing,
        "others_pruned": others_pruned,
    }


def _qrf_sector_situation(
    project_root: Path, style: dict[str, Any], ledger: dict[str, Any]
) -> Path:
    """Early-section sector situation: one shared screen read through three QRF lenses.

    Distinct from the results-section relabeling ledger: this figure leads with a single
    boundary screen carrying explicit observation symbols, ties every lens reading to the
    same bit with a vertical connector, and counts the sectors each lens imposes, so a
    first-time reader sees that the *partitioning* changes while the evidenced bit does not.
    """
    colors = _semantic_colors(style)
    sector_colors = _qrf_sector_colors()
    channels = ledger["rows"]
    profiles = ledger["profiles"]
    profile_titles = {
        "separation_constrained": "separation-constrained lens",
        "opacified": "opacified lens",
        "post_dual": "post-dual lens",
    }
    n = len(channels)
    fig, ax = plt.subplots(figsize=(12.6, 6.6))
    ax.set_xlim(-2.6, n + 0.4)
    ax.set_ylim(-1.35, len(profiles) + 1.65)
    ax.axis("off")

    screen_y = len(profiles) + 0.55
    # Shared boundary screen: one cell per channel carrying its observation symbol.
    ax.text(
        -2.5,
        screen_y + 0.33,
        "shared boundary\nscreen (same\nevidenced bits)",
        ha="left",
        va="center",
        fontsize=9,
        fontweight="bold",
        color=colors["boundary"],
        linespacing=0.95,
    )
    for column, channel in enumerate(channels):
        ax.add_patch(
            plt.Rectangle(
                (column, screen_y),
                0.92,
                0.66,
                facecolor="white",
                edgecolor=colors["boundary"],
                linewidth=1.4,
            )
        )
        ax.text(
            column + 0.46,
            screen_y + 0.46,
            channel["channel_id"],
            ha="center",
            va="center",
            fontsize=12.3,
            fontweight="bold",
            color=colors["boundary"],
        )
        ax.text(
            column + 0.46,
            screen_y + 0.16,
            channel.get("observation_symbol", "o in {0,1}"),
            ha="center",
            va="center",
            fontsize=9,
            color=style["palette"]["muted"],
        )
        # Vertical tie: the same column (same bit) is read by every lens below.
        ax.plot(
            [column + 0.46, column + 0.46],
            [-0.55, screen_y],
            color=style["palette"]["grid"],
            linewidth=0.7,
            linestyle=":",
            zorder=0,
        )

    sector_counts = {}
    for row_index, profile in enumerate(profiles):
        lens_y = len(profiles) - 1 - row_index
        labels = ledger["sector_labels_by_profile"][profile]
        sector_counts[profile] = len(set(labels))
        ax.text(
            -2.5,
            lens_y + 0.33,
            profile_titles.get(profile, profile),
            ha="left",
            va="center",
            fontsize=9,
            fontweight="bold",
        )
        for column, sector in enumerate(labels):
            ax.add_patch(
                plt.Rectangle(
                    (column, lens_y),
                    0.92,
                    0.62,
                    facecolor=sector_colors[sector],
                    edgecolor="white",
                    linewidth=1.1,
                )
            )
            text_color = (
                "white"
                if sector in {"self", "env", "action", "body", "world", "other"}
                else colors["boundary"]
            )
            ax.text(
                column + 0.46,
                lens_y + 0.31,
                sector,
                ha="center",
                va="center",
                fontsize=9,
                color=text_color,
                fontweight="bold",
            )
        ax.text(
            n + 0.18,
            lens_y + 0.31,
            f"{sector_counts[profile]} sectors",
            ha="left",
            va="center",
            fontsize=9,
            color=style["palette"]["muted"],
        )

    ax.text(
        (n) / 2.0,
        -1.12,
        "Same bits, three admissible carvings; the bitstream cannot decide which sectorisation is ontologically real (Eq. 9).",
        ha="center",
        va="center",
        fontsize=10.1,
        color=colors["pass"],
        bbox={"facecolor": "white", "edgecolor": colors["pass"], "pad": 2.2},
    )
    ax.set_title(
        "The QRF sector situation: one boundary screen, three lenses",
        fontsize=15.1,
        fontweight="bold",
    )
    handles = [
        Line2D(
            [0],
            [0],
            color=style["palette"]["grid"],
            linestyle=":",
            label="vertical tie: same evidenced bit b_i",
        ),
        *[
            Patch(facecolor=color, label=label)
            for label, color in sector_colors.items()
        ],
    ]
    ax.legend(
        handles=handles,
        title="Sector legend",
        bbox_to_anchor=(1.005, 1.0),
        loc="upper left",
        fontsize=9,
    )
    fig.tight_layout()
    return _save_return(
        fig, _fig_path(project_root, style, "qrf_sector_situation"), style["dpi"]
    )


def _boundary_use_vs_ontology(
    project_root: Path, style: dict[str, Any], audit: dict[str, Any]
) -> Path:
    """Conceptual permission diagram: boundary use is licensed, boundary ontology is not.

    Not a bar chart (that is qrf_invariance_policy_flow): this is the no-self-evidence rule
    rendered as a stepwise permission diagram. Both verdicts stay bound to the
    indistinguishability audit's own control flags rather than asserted.
    """
    colors = _semantic_colors(style)
    deployments = [row["deployment"]["name"] for row in audit["rows"]]
    verdicts = boundary_use_ontology_verdicts(audit)
    admissible_equal = verdicts["use"]["ok"]
    control_fails = verdicts["ontology"]["ok"]
    fig, ax = plt.subplots(figsize=(13.8, 7.2))
    ax.set_xlim(0, 14.0)
    ax.set_ylim(0, 7.55)
    ax.axis("off")

    ax.set_title(
        "Boundary use is licensed; boundary ontology is not",
        fontsize=17.2,
        fontweight="bold",
        pad=8,
    )

    def badge(x: float, y: float, text: str, edge: str) -> None:
        ax.add_patch(
            Circle((x, y), 0.22, facecolor=edge, edgecolor=edge, linewidth=1.0)
        )
        ax.text(
            x,
            y,
            text,
            ha="center",
            va="center",
            fontsize=11.0,
            fontweight="bold",
            color="white",
        )

    def wrapped(text: str, width: int) -> str:
        return "\n".join(textwrap.wrap(text, width=width))

    screen_x, screen_y, screen_w, screen_h = 4.45, 5.92, 5.10, 1.17
    ax.add_patch(
        FancyBboxPatch(
            (screen_x, screen_y),
            screen_w,
            screen_h,
            boxstyle="round,pad=0.10",
            facecolor="#f8fafc",
            edgecolor=colors["boundary"],
            linewidth=2.1,
        )
    )
    badge(screen_x - 0.28, screen_y + screen_h / 2, "1", colors["boundary"])
    ax.text(
        screen_x + screen_w / 2,
        screen_y + 0.88,
        "shared finite boundary bitstream",
        ha="center",
        va="center",
        fontsize=12.4,
        fontweight="bold",
        color=colors["boundary"],
    )
    ax.text(
        screen_x + screen_w / 2,
        screen_y + 0.66,
        "single evidenced object",
        ha="center",
        va="center",
        fontsize=9.8,
        color=style["palette"]["muted"],
    )
    bit_labels = ["b0", "b1", "b2", "b3", "b4", "b5"]
    for index, bit in enumerate(bit_labels):
        x = screen_x + 0.62 + index * 0.78
        ax.add_patch(
            plt.Rectangle(
                (x, screen_y + 0.22),
                0.48,
                0.26,
                facecolor="white",
                edgecolor=colors["boundary"],
                linewidth=0.9,
            )
        )
        ax.text(
            x + 0.24,
            screen_y + 0.35,
            bit,
            ha="center",
            va="center",
            fontsize=10.8,
            fontweight="bold",
            color=colors["boundary"],
        )

    def lane(
        x0: float,
        edge: str,
        number: str,
        head: str,
        mark: str,
        body: str,
        audit_text: str,
    ) -> None:
        box_w, box_h = 5.85, 3.55
        y0 = 2.15
        ax.add_patch(
            FancyBboxPatch(
                (x0, y0),
                box_w,
                box_h,
                boxstyle="round,pad=0.16",
                facecolor="white",
                edgecolor=edge,
                linewidth=2.5,
            )
        )
        badge(x0 + 0.38, y0 + box_h - 0.42, number, edge)
        ax.text(
            x0 + box_w / 2,
            y0 + box_h - 0.50,
            f"{mark} {head}",
            ha="center",
            va="center",
            fontsize=14.6,
            fontweight="bold",
            color=edge,
        )
        ax.text(
            x0 + box_w / 2,
            y0 + 2.10,
            wrapped(body, 42),
            ha="center",
            va="center",
            fontsize=11.3,
            color=colors["boundary"],
            linespacing=1.08,
        )
        ax.add_patch(
            FancyBboxPatch(
                (x0 + 0.38, y0 + 0.38),
                box_w - 0.76,
                0.62,
                boxstyle="round,pad=0.08",
                facecolor="#f8fafc",
                edgecolor=edge,
                linewidth=1.0,
                alpha=0.98,
            )
        )
        ax.text(
            x0 + box_w / 2,
            y0 + 0.69,
            wrapped(audit_text, 54),
            ha="center",
            va="center",
            fontsize=10.4,
            style="italic",
            color=style["palette"]["muted"],
            linespacing=1.0,
        )
        ax.add_patch(
            FancyArrowPatch(
                (screen_x + screen_w / 2, screen_y),
                (x0 + box_w / 2, y0 + box_h + 0.08),
                arrowstyle="-|>",
                mutation_scale=16,
                color=edge,
                linewidth=1.8,
            )
        )

    # Headline verdict (head + mark + edge), not just the footnote, is bound to the audit flags
    # (see boundary_use_ontology_verdicts): a flipped flag turns the lane neutral grey.
    use_edge = colors["pass"] if verdicts["use"]["ok"] else colors["null"]
    use_head, use_mark = verdicts["use"]["head"], verdicts["use"]["mark"]
    ont_edge = colors["blocked"] if verdicts["ontology"]["ok"] else colors["null"]
    ont_head, ont_mark = verdicts["ontology"]["head"], verdicts["ontology"]["mark"]
    lane(
        0.55,
        use_edge,
        "2",
        use_head,
        use_mark,
        "Use the same b0-b5 bits through any admissible QRF sector frame for prediction, policy selection, and model comparison. Relabeling self, env, action, body, world, other, or care does not change the audited observation distribution.",
        f"{len(deployments)} admissible frames give one distribution"
        + (
            " (audit: all_admissible_distributions_equal)"
            if admissible_equal
            else " (NOT confirmed)"
        ),
    )
    lane(
        7.60,
        ont_edge,
        "3",
        ont_head,
        ont_mark,
        "Do not treat a chosen sector frame as proof of a real self/world boundary. The audit rejects a distribution-changing perturbation, so ontology is not inferred from the same finite bitstream.",
        (
            "perturbation correctly fails (audit: negative_control_fails)"
            if control_fails
            else "control NOT failing"
        ),
    )
    ax.text(
        7.0,
        1.25,
        "Boundary use and boundary ontology are different evidential objects; this finite-software audit is not empirical, neural, clinical, practice-efficacy, or physical qFEP evidence.",
        ha="center",
        va="center",
        fontsize=11.1,
        color=colors["boundary"],
    )
    handles = [
        Patch(
            facecolor="white",
            edgecolor=colors["pass"],
            label="licensed: prediction under any admissible frame",
        ),
        Patch(
            facecolor="white",
            edgecolor=colors["blocked"],
            label="blocked: ontological reading of the frame",
        ),
    ]
    ax.legend(
        handles=handles,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.03),
        ncol=2,
        fontsize=10.6,
        frameon=True,
    )
    fig.tight_layout()
    return _save_return(
        fig, _fig_path(project_root, style, "boundary_use_vs_ontology"), style["dpi"]
    )


def _separation_prior_net_value(
    project_root: Path,
    style: dict[str, Any],
    bmr: dict[str, Any],
    emergence: dict[str, Any],
) -> Path:
    """Lifecycle synthesis: the separation prior's net value vs. metacognitive access, per precision.

    Net value = Delta F = F_reduced - F_full. A positive value means keeping the prior still pays
    (useful); a negative value means reduction wins (dispensable). The useful -> dispensable arc is
    a property of the *weakest* admissible prior precision, whose curve starts positive at low access
    and crosses zero into the prune region; stronger priors are over-rigid and are pruned throughout.
    The honest finding (the arc lives only at low precision) is read off the curves, not averaged away.
    """
    colors = _semantic_colors(style)
    life = separation_prior_lifecycle(bmr)
    accesses = np.array(life["accesses"], dtype=float)
    precisions = life["precisions"]
    series = {p: np.array(life["series"][p], dtype=float) for p in precisions}
    crossing_precisions = life["crossing_precisions"]
    arc_precision = life["arc_precision"]

    fig, ax = plt.subplots(figsize=(10.2, 5.8))
    y_hi = max(0.05, max(float(s.max()) for s in series.values())) * 1.15
    y_lo = min(-0.05, min(float(s.min()) for s in series.values())) * 1.08
    ax.axhspan(0, y_hi, facecolor=colors["keep"], alpha=0.10)
    ax.axhspan(y_lo, 0, facecolor=colors["prune"], alpha=0.10)
    ax.axhline(0.0, color=colors["boundary"], linewidth=1.0)

    for precision in precisions:
        net = series[precision]
        is_arc = precision == arc_precision
        ax.plot(
            accesses,
            net,
            marker="o" if is_arc else "",
            linewidth=2.4 if is_arc else 1.0,
            color=colors["finite"] if is_arc else colors["null"],
            label=(
                f"prior precision {precision:g} (lifecycle arc)"
                if is_arc
                else f"prior precision {precision:g}"
            ),
            zorder=3 if is_arc else 2,
        )
        ax.text(
            accesses[-1] + 0.015,
            net[-1],
            f"{precision:g}",
            va="center",
            fontsize=9,
            color=colors["finite"] if is_arc else colors["null"],
            fontweight="bold" if is_arc else "normal",
        )

    crossing = life["crossing"]
    if crossing is not None:
        ax.axvline(crossing, color=colors["prune"], linestyle="--", linewidth=1.3)
        ax.text(
            crossing + 0.01,
            y_hi * 0.55,
            f"useful -> dispensable\nat access ~ {crossing:.2f}",
            ha="left",
            va="center",
            fontsize=9,
            color=colors["prune"],
        )
    others_pruned = life["others_pruned"]
    prune_note = (
        "prune: reduction wins\n(strong priors throughout)"
        if others_pruned
        else "prune: reduction wins"
    )
    ax.text(
        accesses.min() + 0.01,
        y_hi * 0.55,
        "keep:\nprior pays",
        fontsize=9,
        color=colors["keep"],
        va="center",
    )
    ax.text(
        accesses.max(),
        y_lo * 0.55,
        prune_note,
        fontsize=9,
        color=colors["prune"],
        ha="right",
        va="center",
    )

    full_adv = float(emergence.get("full_empowerment_advantage", 0.0))
    ax.set_xlabel("Metacognitive access", fontsize=10.1)
    ax.set_ylabel("Net value of prior  (Delta F = F_reduced - F_full)", fontsize=10.1)
    ax.set_xlim(accesses.min() - 0.03, accesses.max() + 0.16)
    ax.set_ylim(y_lo, y_hi)
    if crossing_precisions == [min(precisions)]:
        title = "The weakest separation prior is useful before it is dispensable"
    elif crossing_precisions:
        title = "The separation prior is useful before it is dispensable"
    else:
        title = "Separation-prior net value across metacognitive access"
    ax.set_title(title, fontsize=12.3)
    ax.legend(fontsize=9, loc="lower left", title="Bayesian model-reduction sweep")
    _panel_label(ax, "S")
    fig.text(
        0.5,
        0.005,
        f"Prior first earns value via agency (factored advantage rises 0 -> {full_adv:.2f} with empowerment); "
        "finite software sweep, not a developmental, neural, contemplative, or clinical claim.",
        ha="center",
        fontsize=9,
        style="italic",
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    return _save_return(
        fig, _fig_path(project_root, style, "separation_prior_net_value"), style["dpi"]
    )


def _multipartite_witness_negativity(
    project_root: Path, style: dict[str, Any], audit: dict[str, Any]
) -> Path:
    """Minimum bipartition negativity per fixture; separable false-positive controls sit at zero."""
    colors = _semantic_colors(style)
    # The asymmetric fixture is a wrong-axis-regression control whose value is its per-cut
    # pattern (one separable cut), so its minimum negativity is zero; excluding it keeps this
    # entangled-vs-separable contrast figure from rendering it as a teal bar at height zero.
    rows = [row for row in audit["rows"] if row["family"] != "asymmetric"]
    labels = [row["id"].replace("_", "\n") for row in rows]
    values = [row["min_bipartition_negativity"] for row in rows]
    bar_colors = [
        colors["fail"] if row["family"] == "separable_control" else colors["pass"]
        for row in rows
    ]
    fig, ax = plt.subplots(figsize=(12.4, 5.2))
    positions = np.arange(len(rows))
    ax.bar(
        positions, values, color=bar_colors, edgecolor=colors["boundary"], linewidth=0.6
    )
    ax.axhline(0.0, color=colors["boundary"], linewidth=0.8)
    ax.set_xticks(positions, labels, fontsize=9)
    ax.set_ylabel("Minimum bipartition negativity", fontsize=10.1)
    ax.set_title(
        "Multipartite witness: entangled fixtures detected, separable controls at zero",
        fontsize=12.3,
    )
    ax.legend(
        handles=[
            Patch(
                facecolor=colors["pass"],
                edgecolor=colors["boundary"],
                label="entangled fixture (detected, negativity > 0)",
            ),
            Patch(
                facecolor=colors["fail"],
                edgecolor=colors["boundary"],
                label="separable false-positive control (negativity = 0)",
            ),
        ],
        fontsize=9,
        loc="upper right",
    )
    _panel_label(ax, "W")
    fig.text(
        0.5,
        0.005,
        "Finite PPT/negativity witness over fixed states; not a genuine-multipartite-entanglement certificate and not empirical evidence.",
        ha="center",
        fontsize=9,
        style="italic",
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    return _save_return(
        fig,
        _fig_path(project_root, style, "multipartite_witness_negativity"),
        style["dpi"],
    )


def _tensor_network_scaling(
    project_root: Path, style: dict[str, Any], audit: dict[str, Any]
) -> Path:
    """Two panels: MPS bond-dimension scaling and the bond-one truncation control."""
    colors = _semantic_colors(style)
    rows = audit["rows"]
    labels = [row["id"].replace("_qubit", "").replace("_", " ") for row in rows]
    positions = np.arange(len(rows))
    bonds = [row["max_bond_dimension"] for row in rows]
    trunc = [row["truncated_chi1_error"] for row in rows]
    entangled_mask = [row["family"] in {"ghz", "w"} for row in rows]
    fig, axes = plt.subplots(1, 2, figsize=(12.6, 5.0))
    axes[0].bar(
        positions,
        bonds,
        color=[colors["finite"] if e else colors["keep"] for e in entangled_mask],
        edgecolor=colors["boundary"],
        linewidth=0.6,
    )
    axes[0].set_xticks(positions, labels, fontsize=9, rotation=20, ha="right")
    axes[0].set_ylabel("Max bond dimension", fontsize=10.1)
    axes[0].set_title(
        "Exact MPS bond scaling (entangled stay 2, product 1)", fontsize=11.2
    )
    axes[0].legend(
        handles=[
            Patch(facecolor=colors["finite"], label="entangled (GHZ/W)"),
            Patch(facecolor=colors["keep"], label="product"),
        ],
        fontsize=9,
    )
    _panel_label(axes[0], "A")
    axes[1].bar(
        positions,
        trunc,
        color=[colors["fail"] if e else colors["pass"] for e in entangled_mask],
        edgecolor=colors["boundary"],
        linewidth=0.6,
    )
    axes[1].set_xticks(positions, labels, fontsize=9, rotation=20, ha="right")
    axes[1].set_ylabel("Bond-one truncation error", fontsize=10.1)
    axes[1].set_title(
        "Truncation control: lossy on entangled, lossless on product", fontsize=11.2
    )
    axes[1].legend(
        handles=[
            Patch(facecolor=colors["fail"], label="entangled (error > 0)"),
            Patch(facecolor=colors["pass"], label="product (error = 0)"),
        ],
        fontsize=9,
    )
    _panel_label(axes[1], "B")
    fig.text(
        0.5,
        0.005,
        "Finite exact matrix-product-state benchmark over toy states; not a large-scale many-body simulation and not empirical evidence.",
        ha="center",
        fontsize=9,
        style="italic",
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    return _save_return(
        fig, _fig_path(project_root, style, "tensor_network_scaling"), style["dpi"]
    )


def _collision_model_relaxation(
    project_root: Path, style: dict[str, Any], audit: dict[str, Any]
) -> Path:
    """Initial vs final trace distance to the ancilla per coupling; zero-coupling control unchanged."""
    colors = _semantic_colors(style)
    rows = audit["rows"]
    labels = [
        f"{row['id'].replace('_', ' ')}\n(theta={row['theta']:g})" for row in rows
    ]
    positions = np.arange(len(rows))
    width = 0.38
    initial = [row["initial_distance"] for row in rows]
    final = [row["final_distance"] for row in rows]
    fig, ax = plt.subplots(figsize=(10.4, 5.2))
    ax.bar(
        positions - width / 2,
        initial,
        width,
        color=colors["keep"],
        edgecolor=colors["boundary"],
        linewidth=0.6,
        label="initial trace distance to ancilla",
    )
    ax.bar(
        positions + width / 2,
        final,
        width,
        color=colors["prune"],
        edgecolor=colors["boundary"],
        linewidth=0.6,
        label=f"final trace distance after {audit['step_count']} collisions",
    )
    ax.set_xticks(positions, labels, fontsize=9)
    ax.set_ylabel("Trace distance to ancilla", fontsize=10.1)
    ax.set_title(
        "Collision-model relaxation: coupled collapses to the ancilla, zero-coupling does not",
        fontsize=11.8,
    )
    ax.legend(fontsize=9, loc="upper center")
    _panel_label(ax, "C")
    fig.text(
        0.5,
        0.005,
        "Finite deterministic partial-SWAP collision surrogate; not a physical heat bath or thermodynamic measurement and not empirical evidence.",
        ha="center",
        fontsize=9,
        style="italic",
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    return _save_return(
        fig, _fig_path(project_root, style, "collision_model_relaxation"), style["dpi"]
    )


def _data_processing_monotonicity(
    project_root: Path, style: dict[str, Any], audit: dict[str, Any]
) -> Path:
    """Three panels: the data-processing inequality and its two firing discriminating controls."""
    colors = _semantic_colors(style)
    channel_rows = audit["channel_rows"]
    cp_rows = audit["complete_positivity_rows"]
    selective_rows = audit["selective_postselection_rows"]
    fig, axes = plt.subplots(1, 3, figsize=(15.8, 5.4))

    # Panel A: every CPTP channel maps distinguishability onto or below the y = x line (monotone).
    channel_names = sorted({row["channel"] for row in channel_rows})
    palette = {
        name: colors[key]
        for name, key in zip(channel_names, ("finite", "stochastic", "null"))
    }
    for name in channel_names:
        pre = [
            row["trace_distance_before"]
            for row in channel_rows
            if row["channel"] == name
        ]
        post = [
            row["trace_distance_after"]
            for row in channel_rows
            if row["channel"] == name
        ]
        axes[0].scatter(
            pre,
            post,
            s=34,
            color=palette[name],
            edgecolor=colors["boundary"],
            linewidth=0.4,
            label=name.replace("_", " "),
        )
    limit = max(row["trace_distance_before"] for row in channel_rows) * 1.05
    axes[0].plot(
        [0, limit],
        [0, limit],
        color=colors["boundary"],
        linestyle="--",
        linewidth=0.8,
        label="y = x (no change)",
    )
    axes[0].set_xlim(0, limit)
    axes[0].set_ylim(0, limit)
    axes[0].set_xlabel("trace distance before channel", fontsize=10.1)
    axes[0].set_ylabel("trace distance after channel", fontsize=10.1)
    axes[0].set_title(
        "CPTP channels do not increase\ndistinguishability", fontsize=10.8
    )
    axes[0].legend(fontsize=9, loc="upper left")
    _panel_label(axes[0], "A")

    # Panel B: complete-positivity control. Channels have Choi min-eigenvalue >= 0; transpose is -1.
    cp_labels = [
        row["map"].replace("_control", " (control)").replace("_", " ")
        for row in cp_rows
    ]
    cp_values = [row["choi_min_eigenvalue"] for row in cp_rows]
    cp_colors = [
        colors["pass"] if row["completely_positive"] else colors["fail"]
        for row in cp_rows
    ]
    positions = np.arange(len(cp_rows))
    axes[1].bar(
        positions,
        cp_values,
        color=cp_colors,
        edgecolor=colors["boundary"],
        linewidth=0.6,
    )
    axes[1].axhline(0.0, color=colors["boundary"], linewidth=0.8)
    axes[1].set_xticks(positions, cp_labels, fontsize=9, rotation=20, ha="right")
    axes[1].set_ylabel("Choi matrix minimum eigenvalue", fontsize=10.1)
    axes[1].set_title(
        "Control: transpose is positive,\nnot completely positive", fontsize=10.8
    )
    axes[1].legend(
        handles=[
            Patch(facecolor=colors["pass"], label="completely positive (channel)"),
            Patch(facecolor=colors["fail"], label="not CP (transpose control)"),
        ],
        fontsize=9,
    )
    _panel_label(axes[1], "B")

    # Panel C: selective post-selection control. A filter can raise distinguishability toward 1.
    sel_positions = np.arange(len(selective_rows))
    width = 0.38
    before = [row["trace_distance_before"] for row in selective_rows]
    after = [row["trace_distance_after_postselection"] for row in selective_rows]
    sel_labels = [f"angle={row['angle']:.2f}" for row in selective_rows]
    axes[2].bar(
        sel_positions - width / 2,
        before,
        width,
        color=colors["keep"],
        edgecolor=colors["boundary"],
        linewidth=0.6,
        label="before post-selection",
    )
    axes[2].bar(
        sel_positions + width / 2,
        after,
        width,
        color=colors["prune"],
        edgecolor=colors["boundary"],
        linewidth=0.6,
        label="after selective filter",
    )
    axes[2].set_xticks(sel_positions, sel_labels, fontsize=9)
    axes[2].set_ylabel("trace distance between the two states", fontsize=10.1)
    axes[2].set_title(
        "Selective post-selection can\nincrease distinguishability", fontsize=10.8
    )
    axes[2].legend(fontsize=9, loc="lower right")
    _panel_label(axes[2], "C")

    fig.text(
        0.5,
        0.02,
        "Finite qubit-channel data-processing surrogate for opacification as forgetting; not empirical, physical qFEP, neural, clinical, or contemplative evidence.",
        ha="center",
        fontsize=9,
        style="italic",
    )
    fig.tight_layout(rect=(0, 0.10, 1, 1))
    setattr(fig, "_layout_rect", (0.0, 0.10, 1.0, 1.0))
    return _save_return(
        fig,
        _fig_path(project_root, style, "data_processing_monotonicity"),
        style["dpi"],
    )


def _markov_blanket_discovery(
    project_root: Path, style: dict[str, Any], audit: dict[str, Any]
) -> Path:
    """Three panels: sparse precision support, dense marginal covariance, and the F1 recovery contrast."""
    colors = _semantic_colors(style)
    precision = np.abs(np.asarray(audit["precision_matrix"], dtype=float))
    correlation = np.abs(np.asarray(audit["marginal_correlation_matrix"], dtype=float))
    size = precision.shape[0]
    internal, blanket = set(audit["internal_nodes"]), set(audit["blanket_nodes"])
    labels = [
        f"{'I' if n in internal else 'B' if n in blanket else 'E'}{n}"
        for n in range(size)
    ]
    fig, axes = plt.subplots(1, 3, figsize=(15.2, 5.0))

    # Panel A: precision (conditional-independence) support -- sparse; internal-external is zero.
    off_precision = precision.copy()
    np.fill_diagonal(off_precision, np.nan)
    image_a = axes[0].imshow(
        off_precision, cmap="Blues", vmin=0.0, vmax=float(np.nanmax(off_precision))
    )
    axes[0].set_title(
        "Precision support: boundary is visible\n(internal-external entries are zero)",
        fontsize=10.6,
    )
    fig.colorbar(image_a, ax=axes[0], fraction=0.046, pad=0.04).set_label(
        "|precision| (partial coupling)", fontsize=9
    )
    _markov_axis_ticks(axes[0], labels)
    _panel_label(axes[0], "A")

    # Panel B: marginal correlation -- dense; the boundary's structural zeros are filled in.
    off_correlation = correlation.copy()
    np.fill_diagonal(off_correlation, np.nan)
    image_b = axes[1].imshow(
        off_correlation,
        cmap="Oranges",
        vmin=0.0,
        vmax=float(np.nanmax(off_correlation)),
    )
    axes[1].set_title(
        "Marginal correlation: boundary is hidden\n(every block is filled in)",
        fontsize=10.6,
    )
    fig.colorbar(image_b, ax=axes[1], fraction=0.046, pad=0.04).set_label(
        "|marginal correlation|", fontsize=9
    )
    _markov_axis_ticks(axes[1], labels)
    _panel_label(axes[1], "B")

    # Panel C: blanket-recovery F1 for the three readings.
    methods = [
        "precision\nsupport",
        "partial-correlation\nthreshold",
        "marginal-correlation\nthreshold",
    ]
    scores = [
        audit["precision_support_f1"],
        audit["partial_correlation_best_f1"],
        audit["marginal_correlation_best_f1"],
    ]
    bar_colors = [
        colors["pass"] if value >= 1.0 - 1e-9 else colors["fail"] for value in scores
    ]
    positions = np.arange(len(methods))
    axes[2].bar(
        positions, scores, color=bar_colors, edgecolor=colors["boundary"], linewidth=0.6
    )
    axes[2].axhline(
        1.0,
        color=colors["boundary"],
        linestyle="--",
        linewidth=0.8,
        label="exact recovery (F1 = 1)",
    )
    axes[2].set_xticks(positions, methods, fontsize=9)
    axes[2].set_ylim(0, 1.08)
    axes[2].set_ylabel("blanket-recovery F1", fontsize=10.1)
    axes[2].set_title(
        "Conditional independence recovers the blanket;\nthe marginal cannot",
        fontsize=10.6,
    )
    axes[2].legend(fontsize=9, loc="upper center", bbox_to_anchor=(0.5, -0.24))
    _panel_label(axes[2], "C")

    fig.text(
        0.5,
        0.02,
        "Finite deterministic Gaussian-graphical-model surrogate; not empirical, neural, developmental, clinical, or physical qFEP evidence.",
        ha="center",
        fontsize=9,
        style="italic",
    )
    fig.tight_layout(rect=(0, 0.12, 1, 1))
    setattr(fig, "_layout_rect", (0.0, 0.12, 1.0, 1.0))
    return _save_return(
        fig, _fig_path(project_root, style, "markov_blanket_discovery"), style["dpi"]
    )


def _markov_axis_ticks(axis: Any, labels: list[str]) -> None:
    positions = np.arange(len(labels))
    axis.set_xticks(positions, labels, fontsize=9)
    axis.set_yticks(positions, labels, fontsize=9)


def _n_cycle_contextuality_panel(
    project_root: Path, style: dict[str, Any], audit: dict[str, Any]
) -> Path:
    """Feasibility matrix over n-cycle behaviors; odd cycles are contextual, cross-checked vs 2-colorability."""
    colors = _semantic_colors(style)
    rows = sorted(audit["rows"], key=lambda row: row["n"])
    behaviors = [
        "perfect_anticorrelation_feasible",
        "quantum_correlation_feasible",
        "uncorrelated_feasible",
    ]
    behavior_labels = [
        "perfect\nanti-corr\n(E=-1)",
        "quantum\nE=-cos(pi/n)",
        "uncorrelated\n(E=0)",
    ]
    matrix = np.array([[1.0 if row[b] else 0.0 for b in behaviors] for row in rows])
    cmap = ListedColormap([colors["fail"], colors["pass"]])
    fig, ax = plt.subplots(figsize=(9.0, 5.6))
    ax.imshow(matrix, aspect="auto", cmap=cmap, vmin=0, vmax=1)
    ax.set_xticks(range(len(behaviors)), behavior_labels, fontsize=9)
    ax.set_yticks(
        range(len(rows)),
        [
            f"n={row['n']} ({'odd' if row['is_odd_cycle'] else 'even'}, {'2-colorable' if row['two_colorable'] else 'frustrated'})"
            for row in rows
        ],
        fontsize=9,
    )
    for y_idx, row in enumerate(rows):
        for x_idx, b in enumerate(behaviors):
            feasible = row[b]
            ax.text(
                x_idx,
                y_idx,
                "feasible\n(noncontextual)" if feasible else "infeasible\n(contextual)",
                ha="center",
                va="center",
                fontsize=9,
                color="white",
                fontweight="bold",
            )
    ax.set_title(
        "n-cycle contextuality: odd cycles are contextual (LP infeasible), even are not",
        fontsize=11.8,
    )
    ax.legend(
        handles=[
            Patch(
                facecolor=colors["pass"], label="feasible: noncontextual model exists"
            ),
            Patch(
                facecolor=colors["fail"],
                label="infeasible: contextual (no noncontextual model)",
            ),
        ],
        fontsize=9,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.22),
        ncol=2,
    )
    _panel_label(ax, "N")
    fig.text(
        0.5,
        0.05,
        "Measured noncontextual-polytope LP feasibility cross-checked against graph two-colorability; not an asserted optimal violation and not empirical evidence.",
        ha="center",
        fontsize=9,
        style="italic",
    )
    fig.tight_layout(rect=(0, 0.20, 1, 1))
    setattr(fig, "_layout_rect", (0.0, 0.20, 1.0, 1.0))
    return _save_return(
        fig, _fig_path(project_root, style, "n_cycle_contextuality_panel"), style["dpi"]
    )


def generate_all_figures(project_root: Path) -> dict[str, Any]:
    """Generate all registered figures and write the source map."""
    style = _load_style(project_root)
    font_scale = max(float(style.get("font_scale", 1.0)), 1.0)
    # Reset to library defaults first so figure bytes are identical whether this
    # runs in a clean subprocess (the chain) or in-process after other tests have
    # mutated matplotlib's global rcParams. Without this, leaked rcParams change
    # the rendered PNG bytes and break the pinned figure hashes in the release
    # manifest. The explicit update below then sets the project's deterministic
    # typography on top of a known baseline.
    plt.rcdefaults()
    plt.rcParams.update(
        {
            "font.size": 13.0 * font_scale,
            "axes.titlesize": 16.0 * font_scale,
            "axes.labelsize": 13.5 * font_scale,
            "xtick.labelsize": 12.0 * font_scale,
            "ytick.labelsize": 12.0 * font_scale,
            "legend.fontsize": 12.0 * font_scale,
            "figure.titlesize": 18.0 * font_scale,
        }
    )
    (project_root / "output" / "figures" / "qrf_boundary_graphical_model.png").unlink(
        missing_ok=True
    )
    data = project_root / "output" / "data"
    profile = _load_json(data / "pymdp_profile_comparison.json")
    policy_trace = _load_json(data / "pymdp_policy_trace.json")
    model_audit = _load_json(data / "pymdp_generative_model_audit.json")
    pymdp_runtime = _load_json(data / "pymdp_runtime_diagnostics_log.json")
    profile["policy_trace_rows"] = policy_trace["rows"]
    equation = _load_json(data / "equation_audit.json")
    audit = _load_json(data / "qrf_boundary_indistinguishability.json")
    qrf_ledger = _load_json(data / "qrf_boundary_channel_ledger.json")
    bmr = _load_json(data / "bmr_sweep.json")
    sensitivity = _load_json(data / "simulation_sensitivity_grid.json")
    quantum = _load_json(data / "quantum_boundary_entropy.json")
    quantum_dynamics = _load_json(data / "quantum_open_system_dynamics.json")
    quantum_contextuality = _load_json(data / "quantum_measurement_contextuality.json")
    qfep_dynamics = _load_json(data / "qfep_boundary_hamiltonian_dynamics.json")
    quantum_trajectory = _load_json(data / "quantum_trajectory_unraveling.json")
    many_body = _load_json(data / "many_body_boundary_screen_sweep.json")
    sheaf = _load_json(data / "sheaf_contextuality_obstruction_audit.json")
    qrf_transform = _load_json(data / "qrf_transformation_covariance_audit.json")
    empirical_adapter = _load_json(data / "empirical_adapter_provenance_audit.json")
    entanglement = _load_json(data / "arbitrary_two_qubit_entanglement_audit.json")
    cover_polytope = _load_json(data / "general_measurement_cover_polytope_audit.json")
    channel_cost = _load_json(data / "thermodynamic_channel_cost_audit.json")
    sparse_screen = _load_json(data / "sparse_boundary_screen_scaling_audit.json")
    qrf_frame = _load_json(data / "qrf_frame_covariance_toy_audit.json")
    quantum_readiness = _load_json(data / "quantum_roadmap_readiness_matrix.json")
    criticality = _load_json(
        project_root / "output" / "reports" / "criticality_proxy_report.json"
    )
    criticality_stochastic = _load_json(data / "criticality_stochastic_ensemble.json")
    compassion_scope = _load_json(data / "compassion_scope_audit.json")
    emergence = _load_json(data / "separation_prior_emergence_audit.json")
    internal_cut = _load_json(data / "internal_cut_unmeasurability_audit.json")
    practice_map = _load_json(data / "practice_protocol_map.json")
    stochastic_effects = _load_json(data / "stochastic_effect_size_audit.json")
    bmr_robustness = _load_json(data / "bmr_robustness_resampling_audit.json")
    trajectory_convergence = _load_json(
        data / "quantum_trajectory_convergence_audit.json"
    )
    method_ledger = _load_json(data / "method_assumption_ledger.json")
    method_controls = _load_json(data / "method_negative_control_inventory.json")
    crosswalk = _load_json(data / "source_claim_crosswalk.json")
    scholarship = _load_json(data / "scholarship_source_matrix.json")
    claim_support = _load_json(data / "claim_support_audit.json")
    manuscript_claim = _load_json(data / "manuscript_claim_audit.json")
    evidence_ceiling = _load_json(data / "evidence_ceiling_audit.json")
    claim_context = _load_json(data / "claim_context_ledger.json")
    multipartite_witness = _load_json(data / "multipartite_witness_suite_audit.json")
    tensor_network = _load_json(data / "tensor_network_benchmark_audit.json")
    collision_model = _load_json(data / "collision_model_thermalization_audit.json")
    n_cycle = _load_json(data / "n_cycle_contextuality_library_audit.json")
    data_processing = _load_json(data / "data_processing_monotonicity_audit.json")
    markov_blanket = _load_json(data / "markov_blanket_discovery_audit.json")
    produced = {
        "graphical_abstract_cover": _graphical_abstract_cover(project_root, style),
        "qrf_boundary_screen_geometry": _qrf_boundary_screen_geometry(
            project_root, style, profile, audit, qrf_ledger
        ),
        "qrf_channel_relabeling_ledger": _qrf_channel_relabeling_ledger(
            project_root, style, qrf_ledger
        ),
        "qrf_invariance_policy_flow": _qrf_invariance_policy_flow(
            project_root, style, profile, audit
        ),
        "qrf_sectorisation_map": _sectorisation_map(project_root, style, profile),
        "boundary_indistinguishability": _boundary_audit(project_root, style, audit),
        "qrf_reference_frame_geometry": _qrf_reference_frame_geometry(
            project_root, style, profile, audit
        ),
        "bmr_free_energy_decomposition": _bmr_decomposition(project_root, style, bmr),
        "bmr_pruning_phase_diagram": _bmr_phase_diagram(project_root, style, bmr),
        "simulation_sensitivity_heatmap": _simulation_sensitivity_heatmap(
            project_root, style, sensitivity
        ),
        "finite_quantum_scope_summary": _finite_quantum_scope_summary(
            project_root, style, quantum_readiness
        ),
        "quantum_boundary_entropy_landscape": _quantum_boundary_entropy_landscape(
            project_root, style, quantum
        ),
        "quantum_contextuality_witness": _quantum_contextuality_witness(
            project_root, style, quantum
        ),
        "quantum_measurement_contextuality_table": _quantum_measurement_contextuality_table(
            project_root, style, quantum_contextuality
        ),
        "quantum_local_polytope_audit": _quantum_local_polytope_audit(
            project_root, style, quantum_contextuality
        ),
        "quantum_open_system_dynamics": _quantum_open_system_dynamics(
            project_root, style, quantum_dynamics
        ),
        "qfep_boundary_hamiltonian_dynamics": _qfep_boundary_hamiltonian_dynamics(
            project_root, style, qfep_dynamics
        ),
        "quantum_trajectory_unraveling": _quantum_trajectory_unraveling(
            project_root, style, quantum_trajectory
        ),
        "many_body_boundary_screen_sweep": _many_body_boundary_screen_sweep(
            project_root, style, many_body
        ),
        "sheaf_contextuality_obstruction_audit": _sheaf_contextuality_obstruction_audit(
            project_root, style, sheaf
        ),
        "qrf_transformation_covariance_audit": _qrf_transformation_covariance_audit(
            project_root, style, qrf_transform
        ),
        "empirical_adapter_provenance_audit": _empirical_adapter_provenance_audit(
            project_root, style, empirical_adapter
        ),
        "arbitrary_two_qubit_entanglement_audit": _arbitrary_two_qubit_entanglement_audit(
            project_root, style, entanglement
        ),
        "general_measurement_cover_polytope_audit": _general_measurement_cover_polytope_audit(
            project_root, style, cover_polytope
        ),
        "thermodynamic_channel_cost_audit": _thermodynamic_channel_cost_audit(
            project_root, style, channel_cost
        ),
        "sparse_boundary_screen_scaling_audit": _sparse_boundary_screen_scaling_audit(
            project_root, style, sparse_screen
        ),
        "qrf_frame_covariance_toy_audit": _qrf_frame_covariance_toy_audit(
            project_root, style, qrf_frame
        ),
        "quantum_roadmap_readiness_matrix": _quantum_roadmap_readiness_matrix(
            project_root, style, quantum_readiness
        ),
        "pymdp_profile_comparison": _profile_comparison(project_root, style, profile),
        "posterior_trajectory": _posterior_trajectory(project_root, style, profile),
        "pymdp_runtime_validation_dashboard": _pymdp_runtime_validation_dashboard(
            project_root, style, pymdp_runtime, model_audit, stochastic_effects
        ),
        "criticality_proxy_panels": _criticality(project_root, style, criticality),
        "criticality_stochastic_ensemble": _criticality_stochastic_ensemble(
            project_root, style, criticality_stochastic
        ),
        "criticality_signatures": _criticality_signatures(
            project_root, style, criticality_stochastic, criticality
        ),
        "compassion_scope_widening": _compassion_scope_widening(
            project_root, style, compassion_scope
        ),
        "separation_prior_emergence": _separation_prior_emergence(
            project_root, style, emergence
        ),
        "internal_cut_unmeasurability": _internal_cut_unmeasurability(
            project_root, style, internal_cut
        ),
        "practice_policy_scope_map": _practice_policy_scope_map(
            project_root, style, practice_map
        ),
        "stochastic_effect_size_forest": _stochastic_effect_size_forest(
            project_root, style, stochastic_effects
        ),
        "bmr_robustness_resampling": _bmr_robustness_resampling(
            project_root, style, bmr_robustness
        ),
        "quantum_trajectory_convergence": _quantum_trajectory_convergence(
            project_root, style, trajectory_convergence
        ),
        "visual_semantic_palette_ledger": _visual_semantic_palette_ledger(
            project_root, style
        ),
        "method_assumption_failure_map": _method_assumption_failure_map(
            project_root, style, method_ledger, method_controls
        ),
        "claim_source_validation_graph": _claim_graph(project_root, style, crosswalk),
        "scholarship_coverage_matrix": _scholarship_coverage(
            project_root, style, scholarship
        ),
        "claim_support_matrix": _claim_support_matrix(
            project_root, style, claim_support
        ),
        "manuscript_claim_audit": _manuscript_claim_audit(
            project_root, style, manuscript_claim
        ),
        "evidence_ceiling_stress_matrix": _evidence_ceiling_stress_matrix(
            project_root, style, evidence_ceiling
        ),
        "claim_context_evidence_ladder": _claim_context_evidence_ladder(
            project_root, style, claim_context
        ),
        "formalism_operation_map": _formalism_operation_map(
            project_root, style, equation
        ),
        "qrf_sector_situation": _qrf_sector_situation(project_root, style, qrf_ledger),
        "boundary_use_vs_ontology": _boundary_use_vs_ontology(
            project_root, style, audit
        ),
        "separation_prior_net_value": _separation_prior_net_value(
            project_root, style, bmr, emergence
        ),
        "multipartite_witness_negativity": _multipartite_witness_negativity(
            project_root, style, multipartite_witness
        ),
        "tensor_network_scaling": _tensor_network_scaling(
            project_root, style, tensor_network
        ),
        "collision_model_relaxation": _collision_model_relaxation(
            project_root, style, collision_model
        ),
        "n_cycle_contextuality_panel": _n_cycle_contextuality_panel(
            project_root, style, n_cycle
        ),
        "data_processing_monotonicity": _data_processing_monotonicity(
            project_root, style, data_processing
        ),
        "markov_blanket_discovery": _markov_blanket_discovery(
            project_root, style, markov_blanket
        ),
    }
    figure_rows = []
    for figure_id, path in produced.items():
        row = {
            "id": figure_id,
            "path": str(path.relative_to(project_root)),
            "source_artifacts": _source_artifacts_for(figure_id),
            "caption": style["figures"][figure_id]["caption"],
            "visual_encoding": style["figures"][figure_id]["visual_encoding"],
            "alt_text": style["figures"][figure_id]["alt_text"],
            "render_contract": render_contract_for(figure_id),
            **_LAYOUT_TELEMETRY.get(figure_id, _empty_layout_telemetry()),
        }
        if figure_id == "qrf_channel_relabeling_ledger":
            row["channel_labels"] = [
                channel["channel_id"] for channel in qrf_ledger["rows"]
            ]
        figure_rows.append(row)
    source_map = {
        "schema": "realizing_emptiness.figure_source_map.v1",
        "figure_count": len(produced),
        "figures": figure_rows,
    }
    output_path = data / "figure_source_map.json"
    output_path.write_text(
        json.dumps(source_map, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_visual_caption_audit(project_root, source_map)
    write_visual_accessibility_audit(project_root, source_map)
    write_visual_style_audits(project_root, source_map)
    write_figure_integrity_audit(project_root, source_map)
    write_artifact_dashboard(project_root, source_map)
    return source_map


def _source_artifacts_for(figure_id: str) -> list[str]:
    mapping = {
        "graphical_abstract_cover": [
            "output/data/source_claim_crosswalk.json",
            "output/data/equation_audit.json",
            "output/data/qrf_boundary_indistinguishability.json",
            "output/data/stochastic_policy_ensemble.json",
            "output/data/quantum_trajectory_unraveling.json",
        ],
        "qrf_boundary_screen_geometry": [
            "output/data/pymdp_profile_comparison.json",
            "output/data/qrf_boundary_indistinguishability.json",
            "output/data/qrf_boundary_channel_ledger.json",
        ],
        "qrf_channel_relabeling_ledger": [
            "output/data/qrf_boundary_channel_ledger.json",
            "output/data/qrf_boundary_indistinguishability.json",
        ],
        "qrf_invariance_policy_flow": [
            "output/data/pymdp_profile_comparison.json",
            "output/data/qrf_boundary_indistinguishability.json",
        ],
        "qrf_sectorisation_map": ["output/data/pymdp_profile_comparison.json"],
        "boundary_indistinguishability": [
            "output/data/qrf_boundary_indistinguishability.json"
        ],
        "qrf_reference_frame_geometry": [
            "output/data/pymdp_profile_comparison.json",
            "output/data/qrf_boundary_indistinguishability.json",
        ],
        "bmr_free_energy_decomposition": ["output/data/bmr_sweep.json"],
        "bmr_pruning_phase_diagram": ["output/data/bmr_sweep.json"],
        "simulation_sensitivity_heatmap": [
            "output/data/simulation_sensitivity_grid.json"
        ],
        "finite_quantum_scope_summary": [
            "output/data/quantum_roadmap_readiness_matrix.json"
        ],
        "quantum_boundary_entropy_landscape": [
            "output/data/quantum_boundary_entropy.json"
        ],
        "quantum_contextuality_witness": ["output/data/quantum_boundary_entropy.json"],
        "quantum_measurement_contextuality_table": [
            "output/data/quantum_measurement_contextuality.json"
        ],
        "quantum_local_polytope_audit": [
            "output/data/quantum_measurement_contextuality.json"
        ],
        "quantum_open_system_dynamics": [
            "output/data/quantum_open_system_dynamics.json"
        ],
        "qfep_boundary_hamiltonian_dynamics": [
            "output/data/qfep_boundary_hamiltonian_dynamics.json"
        ],
        "quantum_trajectory_unraveling": [
            "output/data/quantum_trajectory_unraveling.json"
        ],
        "many_body_boundary_screen_sweep": [
            "output/data/many_body_boundary_screen_sweep.json"
        ],
        "sheaf_contextuality_obstruction_audit": [
            "output/data/sheaf_contextuality_obstruction_audit.json"
        ],
        "qrf_transformation_covariance_audit": [
            "output/data/qrf_transformation_covariance_audit.json"
        ],
        "empirical_adapter_provenance_audit": [
            "output/data/empirical_adapter_provenance_audit.json"
        ],
        "arbitrary_two_qubit_entanglement_audit": [
            "output/data/arbitrary_two_qubit_entanglement_audit.json"
        ],
        "general_measurement_cover_polytope_audit": [
            "output/data/general_measurement_cover_polytope_audit.json"
        ],
        "thermodynamic_channel_cost_audit": [
            "output/data/thermodynamic_channel_cost_audit.json"
        ],
        "sparse_boundary_screen_scaling_audit": [
            "output/data/sparse_boundary_screen_scaling_audit.json"
        ],
        "qrf_frame_covariance_toy_audit": [
            "output/data/qrf_frame_covariance_toy_audit.json"
        ],
        "quantum_roadmap_readiness_matrix": [
            "output/data/quantum_roadmap_readiness_matrix.json"
        ],
        "pymdp_profile_comparison": [
            "output/data/pymdp_profile_comparison.json",
            "output/data/pymdp_policy_trace.json",
            "output/data/pymdp_runtime_diagnostics_log.json",
        ],
        "posterior_trajectory": [
            "output/data/pymdp_profile_comparison.json",
            "output/data/pymdp_policy_trace.json",
            "output/data/pymdp_runtime_diagnostics_log.json",
        ],
        "pymdp_runtime_validation_dashboard": [
            "output/data/pymdp_runtime_diagnostics_log.json",
            "output/data/pymdp_generative_model_audit.json",
            "output/data/pymdp_policy_trace.json",
            "output/data/stochastic_effect_size_audit.json",
        ],
        "criticality_proxy_panels": ["output/reports/criticality_proxy_report.json"],
        "criticality_stochastic_ensemble": [
            "output/data/criticality_stochastic_ensemble.json"
        ],
        "criticality_signatures": [
            "output/data/criticality_stochastic_ensemble.json",
            "output/reports/criticality_proxy_report.json",
        ],
        "compassion_scope_widening": ["output/data/compassion_scope_audit.json"],
        "separation_prior_emergence": [
            "output/data/separation_prior_emergence_audit.json"
        ],
        "internal_cut_unmeasurability": [
            "output/data/internal_cut_unmeasurability_audit.json"
        ],
        "practice_policy_scope_map": ["output/data/practice_protocol_map.json"],
        "stochastic_effect_size_forest": [
            "output/data/stochastic_effect_size_audit.json"
        ],
        "bmr_robustness_resampling": [
            "output/data/bmr_robustness_resampling_audit.json"
        ],
        "quantum_trajectory_convergence": [
            "output/data/quantum_trajectory_convergence_audit.json"
        ],
        "visual_semantic_palette_ledger": ["figures.yaml"],
        "method_assumption_failure_map": [
            "output/data/method_assumption_ledger.json",
            "output/data/method_negative_control_inventory.json",
        ],
        "claim_source_validation_graph": ["output/data/source_claim_crosswalk.json"],
        "scholarship_coverage_matrix": ["output/data/scholarship_source_matrix.json"],
        "claim_support_matrix": ["output/data/claim_support_audit.json"],
        "manuscript_claim_audit": ["output/data/manuscript_claim_audit.json"],
        "evidence_ceiling_stress_matrix": ["output/data/evidence_ceiling_audit.json"],
        "claim_context_evidence_ladder": [
            "output/data/claim_context_ledger.json",
            "output/data/claim_support_audit.json",
            "output/data/evidence_ceiling_audit.json",
        ],
        "formalism_operation_map": ["output/data/equation_audit.json"],
        "qrf_sector_situation": [
            "output/data/qrf_boundary_channel_ledger.json",
            "output/data/qrf_boundary_indistinguishability.json",
        ],
        "boundary_use_vs_ontology": [
            "output/data/qrf_boundary_indistinguishability.json"
        ],
        "separation_prior_net_value": [
            "output/data/bmr_sweep.json",
            "output/data/separation_prior_emergence_audit.json",
        ],
        "multipartite_witness_negativity": [
            "output/data/multipartite_witness_suite_audit.json"
        ],
        "tensor_network_scaling": ["output/data/tensor_network_benchmark_audit.json"],
        "collision_model_relaxation": [
            "output/data/collision_model_thermalization_audit.json"
        ],
        "n_cycle_contextuality_panel": [
            "output/data/n_cycle_contextuality_library_audit.json"
        ],
        "data_processing_monotonicity": [
            "output/data/data_processing_monotonicity_audit.json"
        ],
        "markov_blanket_discovery": ["output/data/markov_blanket_discovery_audit.json"],
    }
    return mapping[figure_id]
