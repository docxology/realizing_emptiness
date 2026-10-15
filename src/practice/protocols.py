"""Embodied-practice protocol specs mapped to model interventions."""

from __future__ import annotations

from typing import Any
from modeling.registry import model_parameters


def practice_protocol_map() -> dict[str, Any]:
    """Return bounded practice protocol mappings for software interfaces."""
    interventions = model_parameters("practice_mapping")["interventions"]
    protocols = [
        {
            "id": "attentional_opacification",
            "label": "Attend to QRF variation",
            "model_intervention": interventions["attentional_opacification"],
            "paper_role": "progressive opacification of sigma",
            "safety_boundary": "Not therapeutic advice and not a claim of realization.",
        },
        {
            "id": "dependent_origination_inquiry",
            "label": "Track condition-dependence of sector labels",
            "model_intervention": interventions["dependent_origination_inquiry"],
            "paper_role": "reveals boundary designation as contingent",
            "safety_boundary": "For reflective modeling only; stop if distressing.",
        },
        {
            "id": "compassion_alignment",
            "label": "Expand policy scope without self-sector privilege",
            "model_intervention": interventions["compassion_alignment"],
            "paper_role": "unbounded free-energy minimization proxy",
            "safety_boundary": "Not a moral prescription or clinical protocol.",
        },
    ]
    return {
        "schema": "realizing_emptiness.practice_protocol_map.v1",
        "allow_user_facing_claims": False,
        "protocol_count": len(protocols),
        "protocols": protocols,
        "all_have_safety_boundaries": all(bool(row["safety_boundary"]) for row in protocols),
    }

