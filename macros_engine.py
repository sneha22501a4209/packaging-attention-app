"""
=============================================================
PART 3 + PART 4 — MACROS RANKING & REAL-TIME FEEDBACK ENGINE
=============================================================
This module is shared by both the Streamlit app and the
FastAPI service.  Import it; don't run it directly.

MACROS formula (paper Section V-B, Step 5):
  CS = 0.3·VA + 0.4·ER + 0.1·BR + 0.1·FN + 0.1·SU

Strategy mapping (paper Section V, Step 6):
  CS ≥ 0.70 → Bold & Vibrant (ψ2)
  CS ≥ 0.65 → Eco-Friendly  (ψ3)
  CS ≥ 0.60 → Minimalist    (ψ1)
  CS <  0.60 → Interactive   (ψ4)

INNOVATION (Part 4):
  • Identifies the weakest criterion
  • Returns 3 specific, actionable design suggestions
  • "What-if" simulation: CS change if a criterion rises by Δ
=============================================================
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Optional

import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from torchvision import models, transforms

# ──────────────────────────────────────────────────────────
# CRITERION METADATA
# ──────────────────────────────────────────────────────────

CRITERIA = [
    "visual_appeal",
    "emotional_resonance",
    "brand_recall",
    "functionality",
    "sustainability",
]

# Weights from paper (Section V-B, Step 1)
WEIGHTS = {
    "visual_appeal":       0.3,
    "emotional_resonance": 0.4,
    "brand_recall":        0.1,
    "functionality":       0.1,
    "sustainability":      0.1,
}

STRATEGY_MAP = [
    # (threshold, code, name, description)
    (0.70, "ψ2", "Bold & Vibrant",
     "Energetic, shelf-dominant design with vibrant colours and strong typography."),
    (0.65, "ψ3", "Eco-Friendly",
     "Natural materials palette with sustainability messaging front-and-centre."),
    (0.60, "ψ1", "Minimalist",
     "Clean layout with strategic negative space and emotional anchor elements."),
    (0.00, "ψ4", "Interactive",
     "QR / AR-driven engagement; needs stronger visual and emotional hooks."),
]

# Actionable suggestions per criterion
SUGGESTIONS = {
    "visual_appeal": [
        "Increase colour saturation — use a bold primary accent against a neutral background.",
        "Add a focal graphic element (illustration or product hero shot) occupying ≥ 30 % of front face.",
        "Apply a consistent brand colour palette — limit to 3–4 complementary hues.",
    ],
    "emotional_resonance": [
        "Shift colour temperature toward warm tones (amber, terracotta, coral) to trigger positive affect.",
        "Include a lifestyle image or micro-story that connects the product to a consumer moment.",
        "Use rounded, friendly typography instead of sharp geometric fonts to reduce perceived coldness.",
    ],
    "brand_recall": [
        "Simplify the logo placement — position it in the top-left or centre and maintain a clear exclusion zone.",
        "Add a distinctive silhouette or shape language unique to this SKU (die-cut, unique structural form).",
        "Reduce visual clutter — limit the number of text blocks to ≤ 4 distinct zones.",
    ],
    "functionality": [
        "Increase contrast ratio between text and background to ≥ 4.5:1 (WCAG AA standard).",
        "Use a readable sans-serif typeface at ≥ 10 pt equivalent; avoid decorative scripts for key info.",
        "Add clear icons for usage instructions — consumers should parse key info in under 3 seconds.",
    ],
    "sustainability": [
        "Introduce earthy greens, browns, or unbleached kraft textures to signal eco-credentials.",
        "Add a prominent recycling symbol + material callout (e.g., '100 % recyclable board').",
        "Replace glossy lamination cues with matte or textured finish design elements.",
    ],
}


# ──────────────────────────────────────────────────────────
# MACROS CONSENSUS SCORE  (paper §V-B)
# ──────────────────────────────────────────────────────────

def compute_cs(scores: dict[str, float]) -> float:
    """
    Weighted consensus score CS ∈ [0, 1].
    scores must contain all 5 CRITERIA keys.
    """
    return sum(WEIGHTS[c] * float(scores[c]) for c in CRITERIA)


def map_strategy(cs: float) -> dict:
    """Return strategy metadata for a given CS."""
    for threshold, code, name, desc in STRATEGY_MAP:
        if cs >= threshold:
            return {"code": code, "name": name, "description": desc,
                    "cs": round(cs, 4)}
    # Fallback (should not reach here)
    return {"code": "ψ4", "name": "Interactive",
            "description": STRATEGY_MAP[-1][3], "cs": round(cs, 4)}


# ──────────────────────────────────────────────────────────
# FEEDBACK ENGINE  (Part 4 — Student Innovation)
# ──────────────────────────────────────────────────────────

def identify_weakest(scores: dict[str, float]) -> str:
    """Returns the name of the criterion with the lowest score."""
    return min(CRITERIA, key=lambda c: scores[c])


def get_suggestions(criterion: str) -> list[str]:
    """Returns 3 actionable improvement tips for a criterion."""
    return SUGGESTIONS.get(criterion, ["No suggestions available."])


def whatif_simulation(
    scores: dict[str, float],
    delta: float = 0.10,
) -> list[dict]:
    """
    'What-if' analysis: for each criterion independently,
    compute how the CS changes if that criterion improves by delta.

    Returns a list of dicts sorted by impact (largest gain first).
    """
    base_cs = compute_cs(scores)
    results = []
    for c in CRITERIA:
        improved = dict(scores)
        improved[c] = min(1.0, improved[c] + delta)
        new_cs  = compute_cs(improved)
        impact  = new_cs - base_cs
        results.append({
            "criterion":     c,
            "original":      round(scores[c], 4),
            "improved":      round(improved[c], 4),
            "delta":         delta,
            "original_cs":   round(base_cs, 4),
            "new_cs":        round(new_cs, 4),
            "cs_gain":       round(impact, 4),
            "new_strategy":  map_strategy(new_cs)["name"],
        })
    results.sort(key=lambda x: x["cs_gain"], reverse=True)
    return results


# ──────────────────────────────────────────────────────────
# FULL FEEDBACK REPORT
# ──────────────────────────────────────────────────────────

def full_report(scores: dict[str, float]) -> dict:
    """
    Combines MACROS ranking + feedback + what-if into one dict.
    Used by both Streamlit and FastAPI.
    """
    cs       = compute_cs(scores)
    strategy = map_strategy(cs)
    weakest  = identify_weakest(scores)
    tips     = get_suggestions(weakest)
    whatif   = whatif_simulation(scores, delta=0.10)

    return {
        "scores":            scores,
        "consensus_score":   round(cs, 4),
        "strategy":          strategy,
        "weakest_criterion": weakest,
        "improvement_tips":  tips,
        "whatif":            whatif,
    }


# ──────────────────────────────────────────────────────────
# MODEL INFERENCE
# ──────────────────────────────────────────────────────────

IMAGE_SIZE = 224

INFER_TF = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])


def _build_model_arch() -> nn.Module:
    """Rebuild architecture (must match training)."""
    model = models.mobilenet_v2(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3),
        nn.Linear(in_features, 256),
        nn.ReLU(inplace=True),
        nn.Dropout(p=0.2),
        nn.Linear(256, 5),
        nn.Sigmoid(),
    )
    return model


class PackagingPredictor:
    """
    Loads the trained model once and exposes a predict() method.
    Thread-safe for FastAPI / Streamlit reruns because weights
    are loaded into a fixed model object.
    """

    def __init__(self, model_path: str):
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        self.model = _build_model_arch().to(self.device)

        checkpoint = torch.load(model_path, map_location=self.device)
        # Support both raw state_dict and our wrapped checkpoint
        if "state_dict" in checkpoint:
            self.model.load_state_dict(checkpoint["state_dict"])
        else:
            self.model.load_state_dict(checkpoint)

        self.model.eval()
        print(f"✅ Model loaded from {model_path}  [{self.device}]")

    @torch.no_grad()
    def predict(self, image: Image.Image) -> dict[str, float]:
        """
        image: PIL.Image (RGB)
        Returns dict of 5 criterion scores, each in [0, 1].
        """
        tensor = INFER_TF(image.convert("RGB")).unsqueeze(0).to(self.device)
        output = self.model(tensor).squeeze(0).cpu().numpy()
        return {c: round(float(v), 4) for c, v in zip(CRITERIA, output)}

    def predict_bytes(self, raw_bytes: bytes) -> dict[str, float]:
        """Convenience wrapper: accepts raw image bytes."""
        img = Image.open(io.BytesIO(raw_bytes))
        return self.predict(img)

    def analyze(self, image: Image.Image) -> dict:
        """Predict + full MACROS report in one call."""
        scores = self.predict(image)
        return full_report(scores)


# ──────────────────────────────────────────────────────────
# COMPARE TWO DESIGNS
# ──────────────────────────────────────────────────────────

def compare_designs(scores_a: dict, scores_b: dict) -> dict:
    """
    Compares two packaging design score dicts.
    Returns which is better per criterion and overall.
    """
    cs_a = compute_cs(scores_a)
    cs_b = compute_cs(scores_b)

    per_criterion = {}
    for c in CRITERIA:
        diff = scores_b[c] - scores_a[c]
        per_criterion[c] = {
            "design_a": round(scores_a[c], 4),
            "design_b": round(scores_b[c], 4),
            "diff_b_minus_a": round(diff, 4),
            "better": "B" if diff > 0.005 else ("A" if diff < -0.005 else "tie"),
        }

    return {
        "design_a_cs":  round(cs_a, 4),
        "design_b_cs":  round(cs_b, 4),
        "overall_winner": "B" if cs_b > cs_a else ("A" if cs_a > cs_b else "tie"),
        "strategy_a":   map_strategy(cs_a),
        "strategy_b":   map_strategy(cs_b),
        "per_criterion": per_criterion,
    }
