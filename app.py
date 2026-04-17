import streamlit as st
import os, json, urllib.parse
import requests
from PIL import Image
from io import BytesIO

st.set_page_config(
    page_title="PackageAI",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
* { font-family: 'Sora', sans-serif; }
[data-testid="stAppViewContainer"] {
    background: linear-gradient(160deg, #080c14 0%, #0f1828 50%, #0a1520 100%);
    color: white;
}
[data-testid="stHeader"] { background: transparent; }
.hero {
    text-align: center; padding: 48px 24px 28px;
    background: linear-gradient(135deg, #1a3a5c 0%, #0f2540 60%, #1a2e4a 100%);
    border-radius: 24px; margin-bottom: 32px;
    border: 1px solid rgba(99,179,237,0.2);
    box-shadow: 0 24px 80px rgba(0,80,160,0.25);
}
.hero h1 { font-size:3rem;font-weight:800;color:white;margin:0;letter-spacing:-1px; }
.hero p  { color:rgba(255,255,255,0.65);font-size:1.05rem;margin-top:10px;font-weight:300; }
.hero-tag {
    display:inline-block;background:rgba(99,179,237,0.15);border:1px solid rgba(99,179,237,0.35);
    color:#63b3ed;border-radius:50px;padding:4px 16px;font-size:0.8rem;font-weight:600;
    margin-bottom:16px;letter-spacing:1px;text-transform:uppercase;
}

/* Cards */
.card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px; padding: 24px; margin: 14px 0;
}
.highlight-card {
    background: rgba(99,179,237,0.08);
    border: 1px solid rgba(99,179,237,0.2);
    border-radius: 18px; padding: 24px; margin: 14px 0;
}
.warning-card {
    background: rgba(245,101,101,0.08);
    border: 1px solid rgba(245,101,101,0.25);
    border-radius: 18px; padding: 24px; margin: 14px 0;
}
.success-card {
    background: rgba(72,187,120,0.08);
    border: 1px solid rgba(72,187,120,0.25);
    border-radius: 18px; padding: 24px; margin: 14px 0;
}
.gen-card {
    background: linear-gradient(135deg,rgba(159,122,234,0.12),rgba(99,179,237,0.08));
    border: 1px solid rgba(159,122,234,0.3);
    border-radius: 18px; padding: 28px; margin: 14px 0;
}

/* Traffic Light Pills */
.pill-red {
    display:inline-block;background:rgba(245,101,101,0.2);border:1px solid rgba(245,101,101,0.5);
    color:#fc8181;border-radius:50px;padding:3px 14px;font-size:0.8rem;font-weight:700;
}
.pill-yellow {
    display:inline-block;background:rgba(236,201,75,0.2);border:1px solid rgba(236,201,75,0.5);
    color:#f6e05e;border-radius:50px;padding:3px 14px;font-size:0.8rem;font-weight:700;
}
.pill-green {
    display:inline-block;background:rgba(72,187,120,0.2);border:1px solid rgba(72,187,120,0.5);
    color:#68d391;border-radius:50px;padding:3px 14px;font-size:0.8rem;font-weight:700;
}

/* Feedback Items */
.feedback-bad {
    background:rgba(245,101,101,0.07);border-left:4px solid #f56565;
    border-radius:8px;padding:14px 18px;margin:8px 0;color:white;
}
.feedback-good {
    background:rgba(72,187,120,0.07);border-left:4px solid #48bb78;
    border-radius:8px;padding:14px 18px;margin:8px 0;color:white;
}
.feedback-tip {
    background:rgba(99,179,237,0.07);border-left:4px solid #63b3ed;
    border-radius:8px;padding:14px 18px;margin:8px 0;color:white;
}
.suggestion-card {
    background:rgba(255,255,255,0.04);border-left:4px solid #9f7aea;
    border-radius:8px;padding:16px 20px;margin:10px 0;
}
.winner-banner {
    text-align:center;padding:28px;border-radius:18px;
    font-size:1.7rem;font-weight:800;margin:20px 0;
    letter-spacing:-0.5px;
}
.compare-col {
    background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);
    border-radius:14px;padding:18px;text-align:center;
}
.about-section {
    background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);
    border-radius:14px;padding:22px;margin:12px 0;
}
.metric-box {
    background:rgba(255,255,255,0.04);border-radius:12px;padding:18px;
    text-align:center;border:1px solid rgba(255,255,255,0.08);
}
.step-badge {
    display:inline-block;background:linear-gradient(135deg,#4776e6,#8e54e9);
    color:white;border-radius:50px;padding:3px 14px;font-size:0.8rem;font-weight:700;
    margin-bottom:8px;
}

/* Tabs */
div[data-testid="stTabs"] button {
    color:rgba(255,255,255,0.7) !important;font-size:0.92rem !important;
    font-weight:600 !important;font-family:'Sora',sans-serif !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color:white !important;border-bottom-color:#63b3ed !important;
}

/* Buttons */
.stButton button {
    background:linear-gradient(135deg,#4776e6,#8e54e9) !important;
    color:white !important;border:none !important;border-radius:50px !important;
    padding:13px 36px !important;font-weight:700 !important;font-size:0.95rem !important;
    font-family:'Sora',sans-serif !important;letter-spacing:0.3px !important;
    box-shadow:0 6px 20px rgba(71,118,230,0.4) !important;transition:all 0.2s !important;
}

/* Upload */
[data-testid="stFileUploader"] {
    background:rgba(255,255,255,0.02) !important;
    border:2px dashed rgba(99,179,237,0.3) !important;
    border-radius:16px !important;
}

/* Inputs */
.stSelectbox label,.stTextInput label,.stTextArea label { color:rgba(255,255,255,0.75) !important; }
[data-testid="stSelectbox"] > div,[data-testid="stTextInput"] > div,[data-testid="stTextArea"] > div {
    background:rgba(255,255,255,0.05) !important;border-color:rgba(255,255,255,0.1) !important;
    border-radius:10px !important;
}
</style>
""", unsafe_allow_html=True)

# ── MODEL ────────────────────────────────────────────────────
MODEL_PATH = os.environ.get("MODEL_PATH", "./packaging_model.pth")

@st.cache_resource(show_spinner="🧠 Loading AI Model...")
def load_predictor():
    from macros_engine import PackagingPredictor
    return PackagingPredictor(MODEL_PATH)

CRITERIA = ["visual_appeal", "emotional_resonance", "brand_recall", "functionality", "sustainability"]

LABELS = {
    "visual_appeal":       "Visual Appeal",
    "emotional_resonance": "Emotional Connection",
    "brand_recall":        "Brand Memory",
    "functionality":       "Readability & Info",
    "sustainability":      "Eco Impression",
}

ICONS = {
    "visual_appeal":       "🎨",
    "emotional_resonance": "❤️",
    "brand_recall":        "🧠",
    "functionality":       "📋",
    "sustainability":      "🌿",
}

STRATEGY_COLORS = {
    "Bold & Vibrant": ("linear-gradient(135deg,#ff416c,#ff4b2b)", "#ff416c"),
    "Eco-Friendly":   ("linear-gradient(135deg,#11998e,#38ef7d)", "#11998e"),
    "Minimalist":     ("linear-gradient(135deg,#4776e6,#8e54e9)", "#4776e6"),
    "Interactive":    ("linear-gradient(135deg,#f7971e,#ffd200)", "#f7971e"),
}

WEIGHTS = {"visual_appeal":0.3,"emotional_resonance":0.4,"brand_recall":0.1,"functionality":0.1,"sustainability":0.1}

GOALS = {
    "🎯 Maximum Customer Attraction":
        {"visual_appeal":0.4,"emotional_resonance":0.4,"brand_recall":0.1,"functionality":0.05,"sustainability":0.05},
    "🌿 Most Eco-Friendly":
        {"visual_appeal":0.1,"emotional_resonance":0.1,"brand_recall":0.1,"functionality":0.1,"sustainability":0.6},
    "🧠 Strongest Brand Memory":
        {"visual_appeal":0.2,"emotional_resonance":0.2,"brand_recall":0.5,"functionality":0.05,"sustainability":0.05},
    "⚖️ Best Overall Balance":
        {"visual_appeal":0.2,"emotional_resonance":0.2,"brand_recall":0.2,"functionality":0.2,"sustainability":0.2},
    "🏪 Best Shelf Visibility":
        {"visual_appeal":0.5,"emotional_resonance":0.3,"brand_recall":0.1,"functionality":0.05,"sustainability":0.05},
}

# ── HUMAN-READABLE INTERPRETATION ────────────────────────────

def interpret_score(criterion, value):
    """Convert a score (0-1) into plain English verdict + status"""
    if criterion == "visual_appeal":
        if value >= 0.75:
            return "green", "Strong", "Your packaging has great colours and eye-catching design."
        elif value >= 0.55:
            return "yellow", "Needs Work", "The colours and design are average — won't stand out on a crowded shelf."
        else:
            return "red", "Weak", "Very dull visually. Customers will likely skip past this on a shelf without noticing it."

    elif criterion == "emotional_resonance":
        if value >= 0.75:
            return "green", "Strong", "This packaging creates a warm feeling — customers will want to pick it up."
        elif value >= 0.55:
            return "yellow", "Needs Work", "It feels a bit cold or generic. Not creating a strong emotional pull."
        else:
            return "red", "Weak", "Customers feel nothing when they see this. No emotional connection at all."

    elif criterion == "brand_recall":
        if value >= 0.75:
            return "green", "Strong", "The brand name and identity are memorable and well placed."
        elif value >= 0.55:
            return "yellow", "Needs Work", "The brand is present but forgettable. Customers may not remember this next time."
        else:
            return "red", "Weak", "Hard to remember the brand. Logo or name likely too small or poorly positioned."

    elif criterion == "functionality":
        if value >= 0.75:
            return "green", "Strong", "Information is clear, readable, and easy to find."
        elif value >= 0.55:
            return "yellow", "Needs Work", "Some key information is hard to read or find quickly."
        else:
            return "red", "Weak", "Important info like ingredients, brand name or instructions are unclear or too small."

    elif criterion == "sustainability":
        if value >= 0.75:
            return "green", "Strong", "Good eco signals — appeals to environment-conscious shoppers."
        elif value >= 0.55:
            return "yellow", "Needs Work", "Eco signals are weak. No strong message about sustainability."
        else:
            return "red", "Weak", "No visible eco cues at all. Missing out on a growing segment of shoppers."


def get_improvement_advice(criterion, value):
    """Specific actionable advice to fix each weakness"""
    advice = {
        "visual_appeal": [
            "Use bolder, warmer colours — reds, oranges, or bright yellows stand out most on shelves",
            "Add a large, high-quality photograph of the actual product — this alone increases appeal significantly",
            "Reduce the number of colours to 2–3 maximum — fewer colours create a stronger visual impact",
            "Increase contrast between the background and text — light text on dark, or dark on light",
            "Add a visual 'hero element' that takes up at least 35–40% of the front face of the pack",
        ],
        "emotional_resonance": [
            "Add warm amber, golden, or cream tones — these are proven to make food feel more appetising",
            "Show a lifestyle moment: hands holding the product, a happy person, or a cosy setting",
            "Write a short emotional tagline below the product name (e.g. 'Made with love' or 'Taste the difference')",
            "Show the product open or mid-bite — this triggers a sensory response in the customer",
            "Use rounded, friendly shapes rather than hard angular ones — they feel more welcoming",
        ],
        "brand_recall": [
            "Move your brand name to the top-centre or top-left — this is where customers look first",
            "Make the brand name at least 20% larger than it currently is",
            "Create a unique shape, symbol or mascot that only your brand uses",
            "Keep the same colour scheme across all your products so they're instantly recognisable as a family",
            "Use a distinctive font for the brand name — avoid generic fonts used by everyone",
        ],
        "functionality": [
            "Ensure the brand name, product name and key benefit are readable from 2–3 metres away",
            "Use a clean, simple font (not decorative) for all information text — minimum size 11pt",
            "Organise information in a clear hierarchy: Brand → Product → Key Claim → Details",
            "Add clear icons for key details: weight, servings, storage (e.g. 🌡️ Store cool, ♻️ Recyclable)",
            "Increase contrast ratio between text and background to meet readability standards",
        ],
        "sustainability": [
            "Add a clear ♻️ Recyclable symbol and material type (e.g. '100% Recyclable Packaging')",
            "Introduce earthy colours: sage green, kraft brown, cream — these visually signal eco-friendliness",
            "Replace shiny/metallic textures with matte or paper-texture finishes in the design",
            "Add a short eco statement on the front face: 'Plastic-free' or 'Plant-based packaging'",
            "Use a nature-inspired graphic element like leaves, grains or simple line-drawn botanicals",
        ],
    }
    return advice.get(criterion, [])


def get_strengths(criterion, value):
    """What's already working"""
    strengths = {
        "visual_appeal": [
            "Eye-catching colour use — likely to get noticed on a shelf",
            "Good visual hierarchy and layout balance",
            "Strong graphic impact — communicates quality",
        ],
        "emotional_resonance": [
            "Warm and inviting feel — customers want to engage with it",
            "Creates a positive mood or sensory desire",
            "Communicates care and quality through design choices",
        ],
        "brand_recall": [
            "Brand identity is clear and well-positioned",
            "Logo/name is easy to spot and remember",
            "Strong brand personality comes through in the design",
        ],
        "functionality": [
            "Information is well-organised and readable",
            "Key details are easy to find without searching",
            "Good contrast and font choices for readability",
        ],
        "sustainability": [
            "Strong eco signals visible on the packaging",
            "Appeals well to environment-conscious shoppers",
            "Natural material cues are clearly communicated",
        ],
    }
    return strengths.get(criterion, [])


def get_overall_summary(scores):
    """Plain English overall verdict"""
    cs = sum(WEIGHTS[c] * scores[c] for c in CRITERIA)
    if cs >= 0.75:
        return "green", "🏆 High Performing", "This packaging is likely to perform well on shelves. Customers will notice it, feel connected to it, and remember the brand."
    elif cs >= 0.60:
        return "yellow", "⚠️ Average — Needs Improvements", "This packaging is okay but won't stand out. With a few key changes, it could be significantly more effective."
    elif cs >= 0.45:
        return "orange", "🔶 Below Average", "This packaging has real weaknesses that will cost sales. Customers are unlikely to pick it over competitors without improvements."
    else:
        return "red", "🚨 Needs Major Redesign", "This packaging is unlikely to attract customers in a retail environment. A significant redesign is recommended."


# ── DESIGN SUGGESTIONS DATABASE ─────────────────────────────
PRODUCT_SUGGESTIONS = {
    "biscuit": {
        "colours":    "Warm golds, creamy whites, chocolate browns",
        "typography": "Rounded playful font — suggests softness and taste",
        "layout":     "Hero product shot centre-top, brand logo top-left, flavour callout bottom-right",
        "imagery":    "Close-up of biscuit texture, steam wisps, ingredient highlights",
        "mood":       "Warm, inviting, indulgent",
        "tips": [
            "Use a large appetite-appealing product photograph occupying 40% of front face",
            "Show the biscuit broken open to reveal texture — triggers sensory anticipation in customers",
            "Use warm golden-amber as the primary background colour — proven to signal sweetness and quality",
            "Add a circular flavour badge (e.g. 'Real Chocolate') in the top-right corner",
            "Include a subtle texture pattern (e.g. waffle grid) in the background for a premium feel",
        ],
    },
    "chocolate": {
        "colours":    "Deep browns, gold foil accents, cream whites",
        "typography": "Elegant serif or thin script — signals premium quality",
        "layout":     "Vertical brand name left side, product image right side, gold border frame",
        "imagery":    "Melting chocolate drizzle, cocoa beans, gold ribbons",
        "mood":       "Luxurious, indulgent, premium",
        "tips": [
            "Use deep dark brown (#3B1A08) or midnight black as the base — signals premium chocolate",
            "Add gold foil-effect typography for the brand name — elevates perceived value significantly",
            "Show melting chocolate or broken pieces — activates sensory desire in the customer",
            "Use a slim elegant border frame in gold or cream around the entire front panel",
            "Include a cocoa percentage badge (e.g. '72% Dark') — builds trust and authenticity",
        ],
    },
    "chips": {
        "colours":    "Bold reds, yellows, bright oranges",
        "typography": "Heavy bold condensed font — signals boldness and flavour intensity",
        "layout":     "Diagonal flavour burst top-right, product pile centre, bright background",
        "imagery":    "Flying chips, flavour ingredients (peppers, herbs), action shots",
        "mood":       "Energetic, fun, bold, intense",
        "tips": [
            "Use a bright red (#E8001C) or electric yellow background — delivers maximum shelf visibility",
            "Show chips mid-air or in motion — communicates crunch and excitement to the customer",
            "Add a large flavour burst graphic (starburst shape) with flavour name in white bold text",
            "Use heavy condensed typography that fills the top third of the package",
            "Include real ingredient photography (chilli, lime, herbs) to reinforce flavour claims",
        ],
    },
    "cookies": {
        "colours":    "Warm beige, soft browns, pastel accents",
        "typography": "Friendly rounded sans-serif — signals homemade warmth",
        "layout":     "Stack of cookies hero image, handwritten-style brand name, recipe badge",
        "imagery":    "Stack of cookies, chocolate chips visible, warm kitchen background",
        "mood":       "Homely, warm, comforting, nostalgic",
        "tips": [
            "Show a stack of 3–4 cookies with visible chocolate chips or filling on the front",
            "Use a kraft-paper or parchment texture background — signals artisan or homemade quality",
            "Include a 'Home Baked' or 'Recipe Since 1995' heritage badge to build trust",
            "Warm amber spotlighting on the product creates an oven-fresh association",
            "Use a hand-lettered or slightly imperfect font for the brand name — adds authenticity",
        ],
    },
    "candy": {
        "colours":    "Bright pinks, purples, rainbow multicolour",
        "typography": "Bubbly, rounded, colourful — signals fun and playfulness",
        "layout":     "Scattered candy pieces all over, brand name in bubble letters, white background",
        "imagery":    "Scattered colourful candies, burst of colours, cartoon elements",
        "mood":       "Fun, playful, joyful, kids-targeted",
        "tips": [
            "Use a bright white or pastel background with colourful candy scattered across it",
            "Make the brand name large and in bubble font — use multiple colours for each letter",
            "Add a cartoon character or mascot in the upper-left to attract children immediately",
            "Include a 'NEW FLAVOUR' or 'LIMITED EDITION' badge in a contrasting colour",
            "Show the candy unwrapped and glistening to trigger desire — use high gloss finish effect",
        ],
    },
    "snack": {
        "colours":    "Orange, green, yellow — energetic palette",
        "typography": "Bold modern sans-serif with strong visual hierarchy",
        "layout":     "Product hero left, key benefits right, brand name top",
        "imagery":    "Active lifestyle, fresh ingredients, product close-up",
        "mood":       "Energetic, healthy, active, on-the-go",
        "tips": [
            "Use energetic orange or lime green as primary colour — signals vitality and freshness",
            "Highlight key health claims (High Protein, Low Fat) with bold icon badges",
            "Show the product in context — someone active, outdoors, or on-the-go",
            "Use a clean bold font hierarchy: Brand Name → Product Name → Key Claim",
            "Include a nutrition highlight panel on the front — transparency builds shopper trust",
        ],
    },
    "cereal": {
        "colours":    "Sunrise yellows, healthy greens, warm oranges",
        "typography": "Bold friendly font with strong brand name placement",
        "layout":     "Bowl of cereal hero image, milk splash, sun/morning imagery at top",
        "imagery":    "Cereal bowl with milk splash, fresh fruit, morning sunlight",
        "mood":       "Fresh, healthy, energising, morning ritual",
        "tips": [
            "Show a bowl of cereal with milk splash — activates the morning ritual association instantly",
            "Use warm sunrise yellow and orange gradients across the background",
            "Add fresh fruit imagery (strawberries, blueberries) alongside the bowl",
            "Place key nutrition claims (Whole Grain, Vitamin D) as icon strips below the hero image",
            "Include a family or child enjoying breakfast — creates an emotional connection",
        ],
    },
}


def get_suggestions(product_name, style, colour_theme):
    product_lower = product_name.lower()
    matched = None
    for key in PRODUCT_SUGGESTIONS:
        if key in product_lower:
            matched = PRODUCT_SUGGESTIONS[key]
            break
    if not matched:
        matched = {
            "colours":    f"Research your top 3 competitors' colour palettes, then choose something different",
            "typography": "Bold clear font for brand name, lighter weight for product descriptor",
            "layout":     "Brand name top-third, product hero image centre, key claims bottom",
            "imagery":    f"High-quality {product_name} product photography, ingredient highlights",
            "mood":       "Professional, appetising, trustworthy",
            "tips": [
                f"Research top 3 competitor {product_name} brands — identify colour gaps to stand out",
                "Use a hero product photograph that fills at least 35% of the front face",
                "Ensure brand name is readable from 3 metres away — test at actual shelf distance",
                f"Highlight the #1 unique selling point of your {product_name} prominently on the front",
                "Use consistent visual language across all SKU variants for brand family recognition",
            ],
        }

    style_colours = {
        "Bold & Vibrant": "High saturation reds, oranges, yellows — maximum shelf energy",
        "Eco-Friendly":   "Earthy greens, kraft browns, unbleached cream — signals natural origin",
        "Minimalist":     "Clean whites, soft greys, one accent colour — sophisticated restraint",
        "Interactive":    "Dynamic gradients, QR integration zones, AR-ready design areas",
    }
    colour_themes = {
        "🔥 Warm":  "Reds, oranges, golds, ambers — appetite-stimulating palette",
        "❄️ Cool":  "Blues, teals, silvers, whites — refreshing and clean feel",
        "🌿 Earth": "Greens, browns, creams, tans — natural and organic",
        "🎨 Bold":  "Multiple high-contrast vivid colours — maximum shelf impact",
        "🖤 Dark":  "Black, deep charcoal, midnight navy — premium and sophisticated",
    }
    result = dict(matched)
    result["style_colours"] = style_colours.get(style, "")
    result["colour_theme"] = colour_themes.get(colour_theme, "")
    return result


def generate_image_url(product_name, style, colour_theme, extra_notes):
    style_map = {
        "Bold & Vibrant": "vibrant colorful bold graphic design packaging",
        "Eco-Friendly":   "eco natural earthy minimal packaging design",
        "Minimalist":     "clean minimal elegant white packaging design",
        "Interactive":    "modern dynamic interactive futuristic packaging",
    }
    colour_map = {
        "🔥 Warm":  "warm red orange gold tones",
        "❄️ Cool":  "cool blue teal silver tones",
        "🌿 Earth": "earthy green brown natural tones",
        "🎨 Bold":  "vivid multicolor bright tones",
        "🖤 Dark":  "dark black premium sophisticated tones",
    }
    style_text = style_map.get(style, "professional packaging design")
    colour_text = colour_map.get(colour_theme, "appealing color palette")
    notes_text = extra_notes if extra_notes else ""
    prompt = (
        f"professional product packaging design for {product_name}, "
        f"{style_text}, {colour_text}, "
        f"retail shelf packaging, high quality product photography, "
        f"modern graphic design, {notes_text}, "
        f"white background, studio lighting, commercial packaging"
    )
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=512&height=512&nologo=true"
    return url, prompt


def compute_goal_score(scores, goal):
    w = GOALS[goal]
    return round(sum(w[c] * scores[c] for c in CRITERIA), 4)


# ── HERO ─────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-tag">Final Year Project · 2024–25</div>
  <h1>📦 PackageAI</h1>
  <p>AI-Powered Packaging Feedback · Design Comparison · Smart Recommendations</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Analyze My Design",
    "⚖️ Compare & Find Best",
    "🎨 Design Generator",
    "🏠 About & Methodology"
])

# ══════════════════════════════════════════════════════════════
# TAB 1 — ANALYZE DESIGN (Manager-Friendly, No Scores)
# ══════════════════════════════════════════════════════════════
with tab1:
    st.markdown("""
    <div class="card">
      <h3 style="margin:0 0 6px">🔍 Upload Your Packaging Design</h3>
      <p style="color:rgba(255,255,255,0.55);margin:0;font-size:0.9rem">
        Upload any packaging image — get a plain English report on what's working, what's not, and exactly how to fix it.
      </p>
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Drop your packaging image here",
        type=["jpg", "jpeg", "png", "bmp", "webp"], key="single"
    )

    if uploaded:
        image = Image.open(uploaded).convert("RGB")
        predictor = load_predictor()

        with st.spinner("🤖 Analyzing your packaging..."):
            from macros_engine import full_report
            scores = predictor.predict(image)
            report = full_report(scores)

        col_img, col_verdict = st.columns([1, 2], gap="large")

        with col_img:
            st.image(image, use_container_width=True, caption="Your Packaging Design")

        with col_verdict:
            # Overall verdict
            v_color, v_label, v_text = get_overall_summary(scores)
            card_class = {"green": "success-card", "yellow": "highlight-card",
                          "orange": "warning-card", "red": "warning-card"}.get(v_color, "card")
            pill_class = {"green": "pill-green", "yellow": "pill-yellow",
                          "orange": "pill-yellow", "red": "pill-red"}.get(v_color, "pill-yellow")

            st.markdown(f"""
            <div class="{card_class}">
              <div style="margin-bottom:10px">
                <span class="{pill_class}">{v_label}</span>
              </div>
              <p style="font-size:1.05rem;color:white;margin:0;line-height:1.6">{v_text}</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### What Our AI Checked")
            for c in CRITERIA:
                status_color, status_label, status_text = interpret_score(c, scores[c])
                pill = {"green": "pill-green", "yellow": "pill-yellow", "red": "pill-red"}[status_color]
                st.markdown(f"""
                <div class="card" style="padding:14px 18px;margin:8px 0">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
                    <span style="font-weight:700;font-size:0.95rem">
                      {ICONS[c]} {LABELS[c]}
                    </span>
                    <span class="{pill}">{status_label}</span>
                  </div>
                  <p style="color:rgba(255,255,255,0.65);margin:0;font-size:0.88rem;line-height:1.5">
                    {status_text}
                  </p>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── WHAT'S WORKING ────────────────────────────────────
        good_criteria = [c for c in CRITERIA if scores[c] >= 0.70]
        bad_criteria = [c for c in CRITERIA if scores[c] < 0.60]
        mid_criteria = [c for c in CRITERIA if 0.60 <= scores[c] < 0.70]

        if good_criteria:
            st.markdown("<div class='success-card'>", unsafe_allow_html=True)
            st.markdown("### ✅ What's Already Working")
            for c in good_criteria:
                strengths = get_strengths(c, scores[c])
                st.markdown(f"""
                <div class="feedback-good">
                  <strong>{ICONS[c]} {LABELS[c]}</strong><br>
                  <span style="color:rgba(255,255,255,0.75);font-size:0.9rem">
                    {strengths[0] if strengths else 'Looking good!'}
                  </span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # ── WHAT NEEDS FIXING ─────────────────────────────────
        if bad_criteria or mid_criteria:
            st.markdown("<div class='warning-card'>", unsafe_allow_html=True)
            st.markdown("### 🔧 Changes to Make (Priority Order)")

            priority = bad_criteria + mid_criteria
            for rank, c in enumerate(priority, 1):
                status_color, status_label, _ = interpret_score(c, scores[c])
                pill = {"green": "pill-green", "yellow": "pill-yellow", "red": "pill-red"}[status_color]
                advice = get_improvement_advice(c, scores[c])

                st.markdown(f"""
                <div style="margin:14px 0">
                  <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
                    <span style="background:rgba(245,101,101,0.2);color:#fc8181;font-weight:800;
                                 border-radius:50%;width:28px;height:28px;display:inline-flex;
                                 align-items:center;justify-content:center;font-size:0.85rem;
                                 flex-shrink:0">#{rank}</span>
                    <span style="font-weight:700;font-size:1rem">{ICONS[c]} Fix: {LABELS[c]}</span>
                    <span class="{pill}">{status_label}</span>
                  </div>
                """, unsafe_allow_html=True)

                for i, tip in enumerate(advice[:3], 1):
                    st.markdown(f"""
                    <div class="feedback-bad" style="margin-left:38px">
                      <strong>Action {i}:</strong> {tip}
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        # ── CUSTOMER ATTENTION SUMMARY ────────────────────────
        weakest = report["weakest_criterion"]
        strategy = report["strategy"]

        st.markdown("<div class='highlight-card'>", unsafe_allow_html=True)
        st.markdown("### 🛒 Will This Grab Customer Attention?")

        va = scores["visual_appeal"]
        er = scores["emotional_resonance"]

        if va >= 0.70 and er >= 0.70:
            attention_verdict = "Yes — very likely. This packaging has both the visual pop and the emotional warmth to attract shoppers."
            attention_icon = "✅"
        elif va >= 0.60 or er >= 0.60:
            attention_verdict = "Maybe — it has some appeal but won't consistently beat competitors on a shelf. Fix the weaker areas to improve chances."
            attention_icon = "⚠️"
        else:
            attention_verdict = "Unlikely — both the visual and emotional impact are below the benchmark needed to attract customer attention in a retail environment."
            attention_icon = "❌"

        st.markdown(f"""
        <div style="font-size:1.1rem;padding:12px 0;color:white">
          {attention_icon} <strong>{attention_verdict}</strong>
        </div>
        <div class="feedback-tip">
          <strong>🎯 Top Priority Fix:</strong> Focus on improving
          <strong>{ICONS[weakest]} {LABELS[weakest]}</strong> first —
          it's the biggest gap between your design and a shelf-winning package.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Download
        readable_report = {
            "file": uploaded.name,
            "overall_verdict": v_label,
            "summary": v_text,
            "will_grab_attention": attention_verdict,
            "areas_working_well": [f"{LABELS[c]}" for c in good_criteria],
            "areas_to_fix": {LABELS[c]: get_improvement_advice(c, scores[c]) for c in bad_criteria + mid_criteria},
            "top_priority": LABELS[weakest],
        }
        st.download_button(
            "⬇️ Download Feedback Report",
            data=json.dumps(readable_report, indent=2),
            file_name=f"feedback_{uploaded.name}.json",
            mime="application/json"
        )

# ══════════════════════════════════════════════════════════════
# TAB 2 — COMPARE & FIND BEST (Merged)
# ══════════════════════════════════════════════════════════════
with tab2:
    st.markdown("""
    <div class="card">
      <h3 style="margin:0 0 6px">⚖️ Compare Designs & Find the Best One</h3>
      <p style="color:rgba(255,255,255,0.55);margin:0;font-size:0.9rem">
        Upload 2 to 5 packaging designs. Choose what matters most to you. We'll tell you which one wins — and exactly why.
      </p>
    </div>
    """, unsafe_allow_html=True)

    # STEP 1: Goal selection
    st.markdown('<div class="step-badge">STEP 1 — Set Your Goal</div>', unsafe_allow_html=True)
    goal = st.selectbox("What matters most for your product?", list(GOALS.keys()), key="goal_select")

    goal_descriptions = {
        "🎯 Maximum Customer Attraction": "Best for: Products in competitive, crowded retail shelves where impulse purchase drives sales.",
        "🌿 Most Eco-Friendly":           "Best for: Brands targeting health-conscious or environmentally aware shoppers.",
        "🧠 Strongest Brand Memory":      "Best for: Building long-term brand loyalty and repeat purchases.",
        "⚖️ Best Overall Balance":        "Best for: When you want a safe, well-rounded design that performs decently across everything.",
        "🏪 Best Shelf Visibility":       "Best for: Maximum visibility in store — getting noticed from a distance.",
    }
    st.markdown(f"""
    <div class="highlight-card" style="padding:14px 20px;margin:8px 0 20px">
      <strong style="color:#63b3ed">{goal}</strong><br>
      <span style="color:rgba(255,255,255,0.65);font-size:0.9rem">{goal_descriptions[goal]}</span>
    </div>
    """, unsafe_allow_html=True)

    # STEP 2: Upload
    st.markdown('<div class="step-badge">STEP 2 — Upload Your Designs (2 to 5)</div>', unsafe_allow_html=True)
    cols_up = st.columns(5)
    uploaded_designs = []
    design_labels = ["Design A", "Design B", "Design C", "Design D", "Design E"]
    for i, col in enumerate(cols_up):
        f = col.file_uploader(design_labels[i], type=["jpg","jpeg","png","bmp","webp"], key=f"rec_{i}")
        if f:
            uploaded_designs.append((design_labels[i], f))

    if len(uploaded_designs) == 1:
        st.info("⚠️ Upload at least 2 designs to compare.")

    elif len(uploaded_designs) >= 2:
        st.markdown('<div class="step-badge">STEP 3 — Get Results</div>', unsafe_allow_html=True)

        if st.button("🚀 Compare All Designs & Find the Best"):
            predictor = load_predictor()
            results = []

            with st.spinner("🤖 Analyzing all designs..."):
                for name, file in uploaded_designs:
                    img = Image.open(file).convert("RGB")
                    scores = predictor.predict(img)
                    gs = compute_goal_score(scores, goal)
                    from macros_engine import compute_cs, map_strategy
                    cs = compute_cs(scores)
                    strat = map_strategy(cs)
                    results.append({
                        "name": name, "image": img, "scores": scores,
                        "goal_score": gs, "cs": cs, "strategy": strat
                    })

            results.sort(key=lambda x: x["goal_score"], reverse=True)
            winner = results[0]
            runner_up = results[1] if len(results) > 1 else None

            # Winner banner
            wg, wc = STRATEGY_COLORS.get(winner["strategy"]["name"],
                ("linear-gradient(135deg,#4776e6,#8e54e9)", "#4776e6"))
            st.markdown(f"""
            <div class="winner-banner" style="background:{wg}">
              🏆 {winner["name"]} is Your Best Design
              <div style="font-size:0.95rem;font-weight:400;margin-top:8px;opacity:0.85">
                Best match for: {goal}
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Show all designs side by side
            rank_icons = ["🥇","🥈","🥉","4️⃣","5️⃣"]
            img_cols = st.columns(len(results))
            for i, (col, r) in enumerate(zip(img_cols, results)):
                col.image(r["image"], use_container_width=True)
                _, rc = STRATEGY_COLORS.get(r["strategy"]["name"],
                    ("", "#63b3ed"))
                v_color, v_label, _ = get_overall_summary(r["scores"])
                pill = {"green":"pill-green","yellow":"pill-yellow","orange":"pill-yellow","red":"pill-red"}[v_color]
                col.markdown(f"""
                <div style="text-align:center;margin-top:6px">
                  <div style="font-size:1.1rem;font-weight:800">{rank_icons[i]} {r["name"]}</div>
                  <span class="{pill}" style="margin-top:4px;display:inline-block">{v_label}</span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Detailed comparison per criterion ──
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 📋 Detailed Comparison — What Each Design Does")

            for c in CRITERIA:
                best_r = max(results, key=lambda r: r["scores"][c])
                worst_r = min(results, key=lambda r: r["scores"][c])

                st.markdown(f"""
                <div style="margin:16px 0;padding:16px;background:rgba(255,255,255,0.03);
                            border-radius:12px;border:1px solid rgba(255,255,255,0.07)">
                  <div style="font-weight:700;font-size:0.95rem;margin-bottom:10px">
                    {ICONS[c]} {LABELS[c]}
                  </div>
                  <div style="display:flex;flex-wrap:wrap;gap:8px">
                """, unsafe_allow_html=True)

                for r in results:
                    sc = r["scores"][c]
                    s_color, s_label, s_text = interpret_score(c, sc)
                    pill = {"green":"pill-green","yellow":"pill-yellow","red":"pill-red"}[s_color]
                    is_best = r["name"] == best_r["name"]
                    border = "border:2px solid #68d391;" if is_best else ""
                    st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.05);border-radius:10px;
                                padding:10px 14px;min-width:140px;{border}flex:1">
                      <div style="font-weight:700;margin-bottom:4px">{r["name"]}</div>
                      <span class="{pill}">{s_label}</span>
                      <div style="color:rgba(255,255,255,0.55);font-size:0.8rem;margin-top:6px;line-height:1.4">
                        {s_text[:80]}...
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("</div></div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            # ── Why the winner wins ──
            ws = winner["scores"]
            best_c = max(CRITERIA, key=lambda c: ws[c])
            weak_c = min(CRITERIA, key=lambda c: ws[c])

            st.markdown("<div class='success-card'>", unsafe_allow_html=True)
            st.markdown(f"### 💡 Why {winner['name']} is the Best Choice")

            st.markdown(f"""
            <div class="feedback-good">
              <strong>✅ Strongest Area:</strong> {ICONS[best_c]} {LABELS[best_c]}<br>
              <span style="color:rgba(255,255,255,0.7);font-size:0.9rem">
                {get_strengths(best_c, ws[best_c])[0]}
              </span>
            </div>
            """, unsafe_allow_html=True)

            if runner_up:
                ru_scores = runner_up["scores"]
                diff_c = max(CRITERIA, key=lambda c: ws[c] - ru_scores[c])
                st.markdown(f"""
                <div class="feedback-tip">
                  <strong>📊 Edge over {runner_up["name"]}:</strong> {LABELS[diff_c]} is noticeably stronger
                  in {winner["name"]} — this is the deciding factor for your goal.
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="feedback-bad">
              <strong>⚠️ Even the winner has a weakness:</strong> {ICONS[weak_c]} {LABELS[weak_c]}<br>
              <span style="color:rgba(255,255,255,0.7);font-size:0.9rem">
                {get_improvement_advice(weak_c, ws[weak_c])[0]}
              </span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            # ── Best design per category ──
            st.markdown("<div class='highlight-card'>", unsafe_allow_html=True)
            st.markdown("### 🎯 Best Design Per Category")

            cat_labels = {
                "visual_appeal":       "Most Eye-Catching on Shelf",
                "emotional_resonance": "Creates the Strongest Feeling",
                "brand_recall":        "Most Memorable Brand",
                "functionality":       "Clearest Information",
                "sustainability":      "Best Eco Impression",
            }
            for c in CRITERIA:
                best = max(results, key=lambda r: r["scores"][c])
                v_c, v_l, _ = interpret_score(c, best["scores"][c])
                pill = {"green":"pill-green","yellow":"pill-yellow","red":"pill-red"}[v_c]
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;
                            padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.06)">
                  <span style="color:rgba(255,255,255,0.75)">{ICONS[c]} {cat_labels[c]}</span>
                  <span style="font-weight:700;color:#63b3ed">{best["name"]}
                    <span class="{pill}" style="margin-left:8px">{v_l}</span>
                  </span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.markdown("""
        <div style="text-align:center;padding:60px;color:rgba(255,255,255,0.3)">
          <div style="font-size:3.5rem;margin-bottom:12px">📦 📦</div>
          <div style="font-size:1.05rem">Upload 2 to 5 packaging designs above to get started</div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TAB 3 — DESIGN GENERATOR
# ══════════════════════════════════════════════════════════════
with tab3:
    st.markdown("""
    <div class="gen-card">
      <h3 style="margin:0 0 6px">🎨 AI Packaging Design Generator</h3>
      <p style="color:rgba(255,255,255,0.7);margin:0">
        Tell us what you're selling, your style, and your audience — we'll give you a full design brief
        plus a generated sample image to hand to your designer.
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="step-badge">STEP 1 — Describe Your Product</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2, gap="large")

    with col_a:
        product_name = st.text_input(
            "🏷️ Product Name",
            placeholder="e.g. Chocolate Biscuit, Kids Candy, Oat Cookies...",
            key="product_name"
        )
        target_audience = st.selectbox(
            "👥 Target Audience",
            ["General", "Kids (5-12)", "Teenagers", "Young Adults (18-30)",
             "Adults (30-50)", "Health Conscious", "Premium Buyers", "Seniors"],
            key="audience"
        )
        market_segment = st.selectbox(
            "🏪 Market Segment",
            ["Mass Market", "Premium", "Budget Friendly",
             "Organic / Natural", "Luxury", "Kids / Family"],
            key="market"
        )

    with col_b:
        design_style = st.selectbox(
            "🎨 Design Style",
            ["Bold & Vibrant", "Eco-Friendly", "Minimalist", "Interactive"],
            key="gen_style"
        )
        colour_theme = st.selectbox(
            "🌈 Colour Theme",
            ["🔥 Warm", "❄️ Cool", "🌿 Earth", "🎨 Bold", "🖤 Dark"],
            key="colour_theme"
        )
        extra_notes = st.text_area(
            "📋 Extra Requirements (optional)",
            placeholder="e.g. Must include a mascot, gluten-free badge, festive theme...",
            height=108,
            key="extra_notes"
        )

    st.markdown('<div class="step-badge" style="margin-top:20px">STEP 2 — Generate Your Brief</div>', unsafe_allow_html=True)

    if st.button("✨ Generate Design Brief + Sample Image"):
        if not product_name:
            st.error("⚠️ Please enter a product name first!")
        else:
            suggestions = get_suggestions(product_name, design_style, colour_theme)
            col_sug, col_img = st.columns([1, 1], gap="large")

            with col_sug:
                st.markdown(f"""
                <div class="gen-card">
                  <h4 style="margin:0 0 6px">🎯 Design Brief for: {product_name}</h4>
                  <p style="color:rgba(255,255,255,0.5);font-size:0.82rem;margin:0">
                    {design_style} · {colour_theme} · {target_audience} · {market_segment}
                  </p>
                </div>
                """, unsafe_allow_html=True)

                sections = [
                    ("🎨 Colour Palette", f"<strong>Base:</strong> {suggestions['colours']}<br><strong>Style:</strong> {suggestions['style_colours']}<br><strong>Theme:</strong> {suggestions['colour_theme']}"),
                    ("✍️ Typography",     suggestions["typography"]),
                    ("📐 Layout",         suggestions["layout"]),
                    ("📸 Imagery",        suggestions["imagery"]),
                    ("😊 Mood & Feel",    suggestions["mood"]),
                ]
                for title, content in sections:
                    st.markdown(f"""
                    <div class="card" style="padding:16px 18px;margin:8px 0">
                      <div style="font-weight:700;margin-bottom:8px;color:#9f7aea">{title}</div>
                      <div style="color:rgba(255,255,255,0.75);font-size:0.88rem;line-height:1.6">{content}</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("#### 💡 5 Specific Design Tips")
                for i, tip in enumerate(suggestions["tips"], 1):
                    st.markdown(f"""
                    <div class="suggestion-card">
                      <strong style="color:#9f7aea">#{i}</strong> {tip}
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col_img:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("#### 🖼️ AI-Generated Sample Image")
                st.caption("This is a concept image — hand the brief above to your actual designer")

                img_url, prompt_used = generate_image_url(
                    product_name, design_style, colour_theme, extra_notes
                )

                with st.spinner("🎨 Generating image... (10–20 seconds)"):
                    try:
                        resp = requests.get(img_url, timeout=30)
                        if resp.status_code == 200:
                            gen_img = Image.open(BytesIO(resp.content))
                            st.image(gen_img, use_container_width=True,
                                     caption=f"Concept: {product_name} Packaging")
                            img_bytes = BytesIO()
                            gen_img.save(img_bytes, format="PNG")
                            st.download_button(
                                "⬇️ Download Concept Image",
                                data=img_bytes.getvalue(),
                                file_name=f"{product_name.replace(' ','_')}_concept.png",
                                mime="image/png"
                            )
                        else:
                            st.warning("Image generation timed out. Please try again.")
                    except Exception:
                        st.warning("Image service is busy — try again in a moment.")
                        st.info("Tip: Pollinations.ai is free but may occasionally be slow.")

                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.03);border-radius:8px;
                            padding:12px;margin-top:12px">
                  <span style="color:rgba(255,255,255,0.4);font-size:0.75rem">
                    <strong>Prompt used:</strong> {prompt_used[:200]}...
                  </span>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)

                # Expected performance
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("#### 📊 Expected Performance If Built Well")

                expected_map = {
                    "Bold & Vibrant": [0.85, 0.75, 0.65, 0.70, 0.35],
                    "Eco-Friendly":   [0.65, 0.70, 0.60, 0.75, 0.90],
                    "Minimalist":     [0.72, 0.65, 0.68, 0.82, 0.55],
                    "Interactive":    [0.78, 0.80, 0.75, 0.65, 0.50],
                }
                exp_raw = expected_map.get(design_style, [0.70, 0.70, 0.65, 0.70, 0.60])
                exp_scores = dict(zip(CRITERIA, exp_raw))

                for c in CRITERIA:
                    sc = exp_scores[c]
                    s_color, s_label, _ = interpret_score(c, sc)
                    pill = {"green":"pill-green","yellow":"pill-yellow","red":"pill-red"}[s_color]
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;align-items:center;
                                padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.05)">
                      <span style="color:rgba(255,255,255,0.7);font-size:0.88rem">
                        {ICONS[c]} {LABELS[c]}
                      </span>
                      <span class="{pill}">{s_label}</span>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)

            # Download brief
            brief = {
                "product": product_name,
                "style": design_style,
                "colour_theme": colour_theme,
                "target_audience": target_audience,
                "market_segment": market_segment,
                "design_brief": suggestions,
                "expected_performance": {LABELS[c]: "Strong" if exp_scores[c] >= 0.70 else "Average" if exp_scores[c] >= 0.55 else "Weak"
                                         for c in CRITERIA},
            }
            st.download_button(
                "⬇️ Download Full Design Brief (JSON)",
                data=json.dumps(brief, indent=2),
                file_name=f"{product_name.replace(' ','_')}_design_brief.json",
                mime="application/json"
            )

# ══════════════════════════════════════════════════════════════
# TAB 4 — ABOUT & METHODOLOGY
# ══════════════════════════════════════════════════════════════
with tab4:
    st.markdown("""
    <div class="hero" style="margin-bottom:24px">
      <div class="hero-tag">Academic Project</div>
      <h1 style="font-size:2.2rem">PackageAI</h1>
      <p>Real-Time Packaging Attention Prediction using Deep Learning + MACROS Ranking</p>
      <p style="font-size:0.85rem;margin-top:4px;opacity:0.5">Final Year Major Project · 2024–25</p>
    </div>
    """, unsafe_allow_html=True)

    # Overview
    st.markdown("<div class='about-section'>", unsafe_allow_html=True)
    st.markdown("### 🎯 Project Overview")
    st.markdown("""
    **PackageAI** is an AI-powered system that evaluates consumer product packaging designs in real time.
    Given a packaging image, the system predicts how well it performs across five key consumer-facing criteria —
    and gives actionable design feedback.

    The core problem this solves: packaging teams and brand managers have no fast, objective way to test whether
    a packaging design will attract customers — before spending money printing it. PackageAI provides that instant
    assessment using a trained deep learning model.
    """)
    st.markdown("</div>", unsafe_allow_html=True)

    # Architecture
    st.markdown("<div class='about-section'>", unsafe_allow_html=True)
    st.markdown("### 🧠 Model Architecture — MobileNetV2")

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("""
        **Base Model:** MobileNetV2 (pretrained on ImageNet)

        MobileNetV2 is a convolutional neural network designed for mobile and edge applications.
        It uses **inverted residuals and linear bottlenecks** which make it fast and lightweight
        without sacrificing accuracy.

        **Why MobileNetV2?**
        - Lightweight enough to run in real-time in a web app
        - Pretrained features transfer well to visual design tasks
        - Proven performance on image classification benchmarks
        """)
    with c2:
        st.markdown("""
        **Our Modifications (Fine-tuning):**

        The final classification head was replaced with a custom regression head that outputs
        **5 continuous values (0–1)** — one per MACROS criterion.

        ```
        MobileNetV2 Backbone (frozen)
            ↓
        Global Average Pooling
            ↓
        Dense(256) + ReLU + Dropout(0.3)
            ↓
        Dense(5) + Sigmoid
            ↓
        [visual, emotional, recall, function, eco]
        ```
        """)
    st.markdown("</div>", unsafe_allow_html=True)

    # MACROS
    st.markdown("<div class='about-section'>", unsafe_allow_html=True)
    st.markdown("### 📊 The MACROS Ranking System")
    st.markdown("""
    **MACROS** (Multi-Criteria Ranking and Optimisation System) is the scoring framework
    used to combine individual criterion scores into a single **Consensus Score (CS)**.

    The Consensus Score tells us how good a packaging design is *overall*, with each criterion
    weighted by its real-world impact on consumer behaviour:
    """)

    criteria_info = [
        ("🎨", "Visual Appeal",       "30%", "0.30", "Does the packaging catch the eye? Strong use of colour, contrast, and imagery."),
        ("❤️", "Emotional Resonance", "40%", "0.40", "Does it create a feeling — warmth, excitement, trust? Highest weight because emotion drives purchase decisions."),
        ("🧠", "Brand Recall",        "10%", "0.10", "Is the brand name memorable and well-positioned?"),
        ("📋", "Functionality",       "10%", "0.10", "Is all key information clear and readable?"),
        ("🌿", "Sustainability",      "10%", "0.10", "Does the design communicate eco-friendliness?"),
    ]

    for icon, name, pct, weight, desc in criteria_info:
        st.markdown(f"""
        <div style="display:flex;align-items:flex-start;gap:16px;padding:12px 0;
                    border-bottom:1px solid rgba(255,255,255,0.06)">
          <div style="min-width:56px;text-align:center">
            <div style="font-size:1.4rem">{icon}</div>
            <div style="font-weight:800;color:#63b3ed;font-size:1.1rem">{pct}</div>
          </div>
          <div>
            <div style="font-weight:700;margin-bottom:3px">{name}</div>
            <div style="color:rgba(255,255,255,0.55);font-size:0.88rem;line-height:1.5">{desc}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background:rgba(99,179,237,0.08);border-radius:10px;padding:14px 18px;margin-top:14px">
      <strong>Consensus Score Formula:</strong><br>
      <code style="color:#63b3ed">CS = (0.30 × Visual) + (0.40 × Emotional) + (0.10 × Recall) + (0.10 × Function) + (0.10 × Eco)</code>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Dataset & Training
    st.markdown("<div class='about-section'>", unsafe_allow_html=True)
    st.markdown("### 📦 Dataset & Training")

    c1, c2, c3 = st.columns(3, gap="large")
    with c1:
        st.markdown("""
        **Dataset**
        - 5,058 biscuit packaging images
        - Sourced from real retail product photography
        - Images: 224×224 pixels (RGB)
        - Labels: 5 criterion scores per image (human-annotated)
        """)
    with c2:
        st.markdown("""
        **Training Setup**
        - Framework: PyTorch
        - Optimiser: Adam (lr=0.001)
        - Loss: Mean Squared Error (MSE)
        - Epochs: 30 with early stopping
        - Train/Val/Test: 80% / 10% / 10%
        """)
    with c3:
        st.markdown("""
        **Performance**
        - Validation MAE: ~0.048
        - Test MAE: ~0.052
        - All 5 criteria predicted simultaneously
        - Inference time: <200ms per image
        """)
    st.markdown("</div>", unsafe_allow_html=True)

    # Tools & Tech Stack
    st.markdown("<div class='about-section'>", unsafe_allow_html=True)
    st.markdown("### 🛠️ Tools & Technologies Used")

    tools = [
        ("🐍", "Python 3.11",       "Core programming language"),
        ("🔥", "PyTorch",           "Deep learning framework — model training and inference"),
        ("📱", "MobileNetV2",       "Pretrained CNN backbone (torchvision)"),
        ("🖼️", "Pillow (PIL)",      "Image loading, resizing, and preprocessing"),
        ("🌐", "Streamlit",         "Web application framework — the entire front end"),
        ("🤖", "Pollinations.ai",   "Free AI image generation API (no API key required)"),
        ("📊", "NumPy / Pandas",    "Data preprocessing and label management"),
        ("🎨", "Custom MACROS Engine", "Our multi-criteria scoring and ranking logic"),
    ]

    col1, col2 = st.columns(2, gap="large")
    for i, (icon, tool, desc) in enumerate(tools):
        col = col1 if i % 2 == 0 else col2
        col.markdown(f"""
        <div style="display:flex;align-items:center;gap:14px;padding:12px;
                    background:rgba(255,255,255,0.03);border-radius:10px;margin:6px 0;
                    border:1px solid rgba(255,255,255,0.06)">
          <div style="font-size:1.4rem;min-width:32px;text-align:center">{icon}</div>
          <div>
            <div style="font-weight:700;font-size:0.92rem">{tool}</div>
            <div style="color:rgba(255,255,255,0.5);font-size:0.82rem">{desc}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # How it works
    st.markdown("<div class='about-section'>", unsafe_allow_html=True)
    st.markdown("### ⚙️ How It Works — End to End")

    steps = [
        ("1", "Upload", "Manager uploads a packaging image (JPG/PNG) through the Streamlit interface."),
        ("2", "Preprocess", "Image is resized to 224×224 and normalised using ImageNet mean/std values."),
        ("3", "Predict", "MobileNetV2 backbone extracts visual features → custom head outputs 5 criterion scores."),
        ("4", "MACROS Score", "The 5 scores are weighted and combined into a single Consensus Score (CS)."),
        ("5", "Feedback", "CS is mapped to a packaging strategy, and per-criterion feedback is generated."),
        ("6", "Report", "Plain English feedback, improvement advice, and a downloadable JSON report are shown."),
    ]

    for num, title, desc in steps:
        st.markdown(f"""
        <div style="display:flex;align-items:flex-start;gap:16px;padding:12px 0;
                    border-bottom:1px solid rgba(255,255,255,0.05)">
          <div style="background:linear-gradient(135deg,#4776e6,#8e54e9);color:white;
                      font-weight:800;border-radius:50%;width:32px;height:32px;min-width:32px;
                      display:flex;align-items:center;justify-content:center;font-size:0.85rem">
            {num}
          </div>
          <div>
            <div style="font-weight:700;margin-bottom:3px">{title}</div>
            <div style="color:rgba(255,255,255,0.6);font-size:0.88rem;line-height:1.5">{desc}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Limitations
    st.markdown("<div class='about-section'>", unsafe_allow_html=True)
    st.markdown("### ⚠️ Current Limitations")
    st.markdown("""
    - **Dataset scope:** Model trained primarily on biscuit packaging — performance may vary on very different product categories.
    - **Label subjectivity:** MACROS criterion scores are human-annotated — some annotator bias may exist.
    - **Image quality:** Very low-resolution or blurry images may reduce prediction accuracy.
    - **Context missing:** The model sees only the front face — it cannot evaluate back-of-pack, 3D structure, or tactile material feel.
    - **Cultural context:** Colour psychology differs across markets — current model reflects a general (non-regional) training set.
    """)
    st.markdown("</div>", unsafe_allow_html=True)
