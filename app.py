import streamlit as st
import os, json, urllib.parse, requests
from PIL import Image
from io import BytesIO

st.set_page_config(
    page_title="A Real-Time Packaging Evaluation",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
* { font-family: 'Poppins', sans-serif; }

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0a0a14 0%, #111128 50%, #0d1a2e 100%);
    color: white;
}
[data-testid="stHeader"] { background: transparent; }

/* HERO */
.hero {
    text-align: center;
    padding: 48px 24px 32px;
    background: linear-gradient(135deg, #1a1a4e 0%, #2d1b69 50%, #11224d 100%);
    border-radius: 24px;
    margin-bottom: 32px;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 24px 80px rgba(0,0,0,0.5);
}
.hero h1 { font-size:2.6rem;font-weight:700;color:white;margin:0;line-height:1.2; }
.hero p  { color:rgba(255,255,255,0.7);font-size:1rem;margin-top:12px; }

/* CARDS */
.card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 24px;
    margin: 12px 0;
}
.green-card {
    background: rgba(56,239,125,0.07);
    border: 1px solid rgba(56,239,125,0.25);
    border-radius: 18px;
    padding: 24px;
    margin: 12px 0;
}
.red-card {
    background: rgba(255,65,108,0.07);
    border: 1px solid rgba(255,65,108,0.25);
    border-radius: 18px;
    padding: 24px;
    margin: 12px 0;
}
.blue-card {
    background: rgba(102,126,234,0.08);
    border: 1px solid rgba(102,126,234,0.25);
    border-radius: 18px;
    padding: 24px;
    margin: 12px 0;
}
.elec-hero {
    background: linear-gradient(135deg, #0d2137 0%, #0a3d2e 100%);
    border: 1px solid rgba(56,239,125,0.3);
    border-radius: 20px;
    padding: 32px;
    margin-bottom: 24px;
    text-align: center;
}

/* ISSUE ITEM */
.issue-item {
    background: rgba(255,65,108,0.08);
    border-left: 4px solid #ff416c;
    border-radius: 10px;
    padding: 14px 18px;
    margin: 8px 0;
    color: white;
}
.fix-item {
    background: rgba(56,239,125,0.08);
    border-left: 4px solid #38ef7d;
    border-radius: 10px;
    padding: 14px 18px;
    margin: 8px 0;
    color: white;
}
.neutral-item {
    background: rgba(255,210,0,0.08);
    border-left: 4px solid #ffd200;
    border-radius: 10px;
    padding: 14px 18px;
    margin: 8px 0;
    color: white;
}

/* WINNER BANNER */
.winner-banner {
    text-align:center;
    padding:28px;
    border-radius:18px;
    font-size:1.7rem;
    font-weight:700;
    margin:20px 0;
}

/* PRODUCT CARD */
.product-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 18px;
    padding: 22px;
    margin: 12px 0;
    transition: all 0.3s;
}
.product-card-gold {
    background: linear-gradient(135deg,rgba(255,215,0,0.08),rgba(255,165,0,0.05));
    border: 2px solid rgba(255,215,0,0.4);
    border-radius: 18px;
    padding: 22px;
    margin: 12px 0;
}
.product-card-silver {
    background: linear-gradient(135deg,rgba(192,192,192,0.08),rgba(169,169,169,0.05));
    border: 2px solid rgba(192,192,192,0.35);
    border-radius: 18px;
    padding: 22px;
    margin: 12px 0;
}
.product-card-bronze {
    background: linear-gradient(135deg,rgba(205,127,50,0.08),rgba(184,115,51,0.05));
    border: 2px solid rgba(205,127,50,0.35);
    border-radius: 18px;
    padding: 22px;
    margin: 12px 0;
}
.badge-green {
    display:inline-block;
    background:rgba(56,239,125,0.15);
    color:#38ef7d;
    padding:5px 14px;
    border-radius:20px;
    font-size:0.8rem;
    font-weight:600;
    border:1px solid rgba(56,239,125,0.3);
}
.badge-yellow {
    display:inline-block;
    background:rgba(255,210,0,0.15);
    color:#ffd200;
    padding:5px 14px;
    border-radius:20px;
    font-size:0.8rem;
    font-weight:600;
    border:1px solid rgba(255,210,0,0.3);
}
.badge-red {
    display:inline-block;
    background:rgba(255,65,108,0.15);
    color:#ff416c;
    padding:5px 14px;
    border-radius:20px;
    font-size:0.8rem;
    font-weight:600;
    border:1px solid rgba(255,65,108,0.3);
}
.search-box {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 20px;
}

/* TABS */
div[data-testid="stTabs"] button {
    color:rgba(255,255,255,0.7) !important;
    font-size:0.9rem !important;
    font-weight:600 !important;
    padding: 8px 16px !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color:white !important;
}

/* BUTTONS */
.stButton button {
    background:linear-gradient(135deg,#667eea,#764ba2) !important;
    color:white !important;
    border:none !important;
    border-radius:50px !important;
    padding:12px 36px !important;
    font-weight:600 !important;
    font-size:1rem !important;
    box-shadow:0 4px 20px rgba(102,126,234,0.4) !important;
    transition: all 0.3s !important;
}
[data-testid="stFileUploader"] {
    background:rgba(255,255,255,0.03) !important;
    border:2px dashed rgba(102,126,234,0.4) !important;
    border-radius:16px !important;
}
.stSelectbox label, .stTextInput label, .stTextArea label {
    color:rgba(255,255,255,0.7) !important;
}
</style>
""", unsafe_allow_html=True)

# ── PATHS ────────────────────────────────────────────────────────────────────
MODEL_PATH = os.environ.get("MODEL_PATH", "./packaging_model.pth")

# ── LOAD PACKAGING MODEL ─────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading packaging analysis AI...")
def load_predictor():
    from macros_engine import PackagingPredictor
    return PackagingPredictor(MODEL_PATH)

# ── LOAD ELECTRONICS MODEL ───────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading electronics AI...")
def load_elec_model():
    import torch, torch.nn as nn
    from transformers import BertModel, BertTokenizer
    from torchvision import models as tvm

    class MultimodalModel(nn.Module):
        def __init__(self, num_classes=3, dropout=0.3):
            super().__init__()
            self.bert    = BertModel.from_pretrained("bert-base-uncased")
            self.img_enc = tvm.mobilenet_v2(weights=tvm.MobileNet_V2_Weights.DEFAULT)
            self.img_enc.classifier = nn.Identity()
            self.drop = nn.Dropout(dropout)
            self.fc   = nn.Sequential(
                nn.Linear(768+1280,512), nn.ReLU(), nn.Dropout(dropout),
                nn.Linear(512,128),     nn.ReLU(), nn.Dropout(dropout),
                nn.Linear(128,num_classes)
            )
        def forward(self, input_ids, attention_mask, images):
            txt = self.bert(input_ids=input_ids, attention_mask=attention_mask).pooler_output
            img = self.img_enc(images)
            return self.fc(self.drop(torch.cat([txt,img],dim=1)))

    device    = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    elec_path = "./electronics_model.pth"
    if not os.path.exists(elec_path):
        import gdown
        gdown.download("https://drive.google.com/uc?id=1E01Zg4-07XprlPgwp0nvBQaDeyVXHXZb", elec_path, quiet=False)

    model = MultimodalModel(num_classes=3).to(device)
    ckpt  = torch.load(elec_path, map_location=device)
    model.load_state_dict(ckpt["model_state_dict"], strict=False)
    model.eval()
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    return model, tokenizer, device

# ── CONSTANTS ────────────────────────────────────────────────────────────────
CRITERIA = ["visual_appeal","emotional_resonance","brand_recall","functionality","sustainability"]
CRITERIA_PLAIN = {
    "visual_appeal":       "Eye-Catching Design",
    "emotional_resonance": "Emotional Connection",
    "brand_recall":        "Brand Recognition",
    "functionality":       "Easy to Read",
    "sustainability":      "Eco-Friendly Look",
}
ISSUES_BY_CRITERION = {
    "visual_appeal": [
        "The colours on this packaging are dull and do not stand out on a shelf.",
        "There is no strong visual element to catch a customer's eye quickly.",
        "Competitors with brighter or bolder designs will attract attention first.",
    ],
    "emotional_resonance": [
        "This packaging does not create a warm or inviting feeling for the customer.",
        "There is nothing on the design that makes a shopper feel excited or emotionally connected.",
        "Customers are unlikely to feel a positive emotion when they see this product.",
    ],
    "brand_recall": [
        "The brand name or logo is not prominently placed — customers may forget the brand.",
        "There is nothing unique or memorable about this packaging design.",
        "After seeing this product once, customers are unlikely to recognise it again.",
    ],
    "functionality": [
        "Key information such as ingredients or usage instructions is hard to read.",
        "The text contrast is too low — customers may struggle to read important details.",
        "The packaging does not clearly communicate what the product is at a glance.",
    ],
    "sustainability": [
        "There are no eco-friendly signals on this packaging — green-conscious customers may avoid it.",
        "No recycling symbols or natural design elements are visible.",
        "The packaging does not appeal to the growing segment of environmentally aware shoppers.",
    ],
}
FIXES_BY_CRITERION = {
    "visual_appeal": [
        "Use brighter, warmer colours — reds, oranges, or golds work well for food packaging.",
        "Add a large, clear product image that fills at least 40% of the front face.",
        "Limit the colour palette to 2–3 strong colours so the design feels focused and bold.",
    ],
    "emotional_resonance": [
        "Add warm colour tones like amber or coral — these trigger positive feelings in shoppers.",
        "Include a lifestyle image or a simple human element such as hands enjoying the product.",
        "Add a short, friendly tagline below the product name to create an emotional hook.",
    ],
    "brand_recall": [
        "Move your logo to the top-centre or top-left — this is where eyes look first.",
        "Create a unique shape, pattern, or mascot that customers will associate only with your brand.",
        "Use a single bold font consistently — simplicity makes the brand more memorable.",
    ],
    "functionality": [
        "Increase the contrast between text and background so all information is easy to read.",
        "Use a clean, simple font at a large enough size that it is readable from arm's length.",
        "Place the product name, flavour, and key benefit in clear, separate visual zones.",
    ],
    "sustainability": [
        "Add a clear recycling symbol and a short message like '100% Recyclable Packaging'.",
        "Introduce earthy greens or natural kraft textures into the design to signal eco values.",
        "Replace any glossy or plastic-looking design elements with matte or natural finish visuals.",
    ],
}
GOALS = {
    "Most Eye-Catching on the Shelf":  {"visual_appeal":0.5,"emotional_resonance":0.3,"brand_recall":0.1,"functionality":0.05,"sustainability":0.05},
    "Best Emotional Connection":       {"visual_appeal":0.2,"emotional_resonance":0.6,"brand_recall":0.1,"functionality":0.05,"sustainability":0.05},
    "Strongest Brand Recognition":     {"visual_appeal":0.2,"emotional_resonance":0.2,"brand_recall":0.5,"functionality":0.05,"sustainability":0.05},
    "Most Eco-Friendly Appeal":        {"visual_appeal":0.1,"emotional_resonance":0.1,"brand_recall":0.1,"functionality":0.1,"sustainability":0.6},
    "Best Overall for Customers":      {"visual_appeal":0.25,"emotional_resonance":0.35,"brand_recall":0.2,"functionality":0.1,"sustainability":0.1},
}

# ── HELPERS ──────────────────────────────────────────────────────────────────
def get_level(score):
    if score >= 0.68: return "strong"
    if score >= 0.50: return "average"
    return "weak"

def get_weakest(scores):
    return min(CRITERIA, key=lambda c: scores[c])

def get_issues_and_fixes(scores):
    """Return issues for weak criteria and fixes — no numbers shown"""
    weak = [(c, scores[c]) for c in CRITERIA if scores[c] < 0.60]
    weak.sort(key=lambda x: x[1])
    return weak[:3]  # top 3 weakest

def plain_verdict(scores):
    """Overall plain-language verdict"""
    avg = sum(scores[c] for c in CRITERIA) / len(CRITERIA)
    if avg >= 0.68:
        return ("✅", "Strong Packaging",   "#38ef7d",
                "This packaging is performing well and is likely to attract customers effectively.")
    if avg >= 0.52:
        return ("⚡", "Good with Room to Improve", "#ffd200",
                "This packaging has good elements but a few changes could make it much more effective.")
    return ("⚠️", "Needs Improvement",  "#ff416c",
            "This packaging has several weaknesses that may cause customers to overlook it on the shelf.")

def compare_verdict(sc_a, sc_b):
    avg_a = sum(sc_a[c] for c in CRITERIA) / len(CRITERIA)
    avg_b = sum(sc_b[c] for c in CRITERIA) / len(CRITERIA)
    return "A" if avg_a > avg_b else "B", avg_a, avg_b

def goal_score(scores, goal):
    w = GOALS[goal]
    return sum(w[c] * scores[c] for c in CRITERIA)

def get_elec_score(text, model, tokenizer, device):
    from torchvision import transforms as T
    import torch
    tf  = T.Compose([T.Resize((224,224)),T.ToTensor(),T.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])])
    enc = tokenizer(text, padding="max_length", truncation=True, max_length=128, return_tensors="pt")
    ids, mask = enc["input_ids"].to(device), enc["attention_mask"].to(device)
    img = tf(Image.new("RGB",(224,224),(180,180,180))).unsqueeze(0).to(device)
    with torch.no_grad():
        probs = torch.softmax(model(ids,mask,img), dim=1).cpu().numpy()[0]
    return float(probs[2]), float(probs[1]), float(probs[0])  # pos, neu, neg

@st.cache_data
def load_catalog():
    for path in ["./electronics_catalog.json", "./electronics_catalog.json"]:
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
    return []

# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
  <h1>📦 A Real-Time Packaging Evaluation</h1>
  <p>Upload your packaging · Get honest feedback · Improve what customers see</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Analyse My Packaging",
    "⚖️ Which Design is Better?",
    "🏆 Pick the Best from Many",
    "🛒 Find Best Electronics",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — ANALYSE SINGLE PACKAGING
# ══════════════════════════════════════════════════════════════════════════════
with tab1:

    st.markdown("""
    <div class="blue-card">
      <strong style="font-size:1.1rem">How does this work?</strong><br>
      <span style="color:rgba(255,255,255,0.75)">
        Upload a photo of your packaging. Our AI will tell you exactly what is
        working, what is not, and what changes to make so more customers pick it up.
      </span>
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Upload your packaging image (JPG or PNG)",
        type=["jpg","jpeg","png","bmp","webp"], key="single"
    )

    if uploaded:
        image     = Image.open(uploaded).convert("RGB")
        predictor = load_predictor()

        col_img, col_result = st.columns([1, 2], gap="large")

        with col_img:
            st.image(image, use_container_width=True, caption="Your Packaging")

        with col_result:
            with st.spinner("Analysing your packaging..."):
                from macros_engine import full_report
                scores = predictor.predict(image)
                report = full_report(scores)

            icon, verdict, color, desc = plain_verdict(scores)

            # Overall verdict
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,{color}18,{color}08);
                        border:2px solid {color};border-radius:18px;
                        padding:24px;text-align:center;margin-bottom:16px">
              <div style="font-size:3rem">{icon}</div>
              <div style="font-size:1.6rem;font-weight:700;color:{color};margin-top:4px">
                {verdict}
              </div>
              <div style="color:rgba(255,255,255,0.7);margin-top:8px;font-size:0.95rem">
                {desc}
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Quick status for each area
            st.markdown("#### How each area is performing:")
            for c in CRITERIA:
                level = get_level(scores[c])
                if level == "strong":
                    emoji, tag, col = "✅", "Working Well", "#38ef7d"
                elif level == "average":
                    emoji, tag, col = "⚡", "Could Be Better", "#ffd200"
                else:
                    emoji, tag, col = "❌", "Needs Attention", "#ff416c"
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;
                            background:rgba(255,255,255,0.04);border-radius:10px;
                            padding:10px 16px;margin:6px 0">
                  <span style="color:white;font-weight:500">{emoji} {CRITERIA_PLAIN[c]}</span>
                  <span style="color:{col};font-weight:600;font-size:0.85rem">{tag}</span>
                </div>
                """, unsafe_allow_html=True)

        # ── PROBLEMS SECTION ──────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        weak_areas = get_issues_and_fixes(scores)

        if weak_areas:
            st.markdown("### ❌ What is Not Working")
            st.markdown("""
            <p style="color:rgba(255,255,255,0.6);margin-top:-8px">
            These are the main reasons customers might walk past your product:
            </p>
            """, unsafe_allow_html=True)

            for c, sc in weak_areas:
                issues = ISSUES_BY_CRITERION[c]
                st.markdown(f"""
                <div style="margin-bottom:8px">
                  <div style="color:#ff416c;font-weight:600;font-size:0.95rem;
                              margin-bottom:4px">
                    🔴 {CRITERIA_PLAIN[c]}
                  </div>
                """, unsafe_allow_html=True)
                for issue in issues:
                    st.markdown(f"""
                    <div class="issue-item">⚠️ {issue}</div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

        # ── FIXES SECTION ─────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### ✅ How to Improve It")
        st.markdown("""
        <p style="color:rgba(255,255,255,0.6);margin-top:-8px">
        Make these changes and more customers will notice and pick up your product:
        </p>
        """, unsafe_allow_html=True)

        if weak_areas:
            for c, sc in weak_areas:
                fixes = FIXES_BY_CRITERION[c]
                st.markdown(f"""
                <div style="margin-bottom:8px">
                  <div style="color:#38ef7d;font-weight:600;font-size:0.95rem;
                              margin-bottom:4px">
                    💡 Improve {CRITERIA_PLAIN[c]}
                  </div>
                """, unsafe_allow_html=True)
                for fix in fixes:
                    st.markdown(f"""
                    <div class="fix-item">✅ {fix}</div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="green-card">
              <strong>🎉 Your packaging is performing well!</strong><br>
              <span style="color:rgba(255,255,255,0.7)">
                All key areas are working effectively. Keep the current design
                direction and consider small refinements only.
              </span>
            </div>
            """, unsafe_allow_html=True)

        # ── DOWNLOAD ──────────────────────────────────────────
        plain_report = {
            "overall_verdict":  verdict,
            "problems_found":   {CRITERIA_PLAIN[c]: ISSUES_BY_CRITERION[c] for c,_ in weak_areas},
            "how_to_improve":   {CRITERIA_PLAIN[c]: FIXES_BY_CRITERION[c]  for c,_ in weak_areas},
        }
        st.download_button(
            "⬇️ Download Feedback Report",
            data=json.dumps(plain_report, indent=2),
            file_name="packaging_feedback.json",
            mime="application/json"
        )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — COMPARE TWO DESIGNS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:

    st.markdown("""
    <div class="blue-card">
      <strong style="font-size:1.1rem">Not sure which design to go with?</strong><br>
      <span style="color:rgba(255,255,255,0.75)">
        Upload two versions of your packaging. We will tell you which one
        customers are more likely to respond to — and why.
      </span>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="large")
    up_a   = c1.file_uploader("📦 Upload Design A", type=["jpg","jpeg","png","bmp","webp"], key="A")
    up_b   = c2.file_uploader("📦 Upload Design B", type=["jpg","jpeg","png","bmp","webp"], key="B")

    if up_a and up_b:
        img_a = Image.open(up_a).convert("RGB")
        img_b = Image.open(up_b).convert("RGB")
        c1.image(img_a, use_container_width=True, caption="Design A")
        c2.image(img_b, use_container_width=True, caption="Design B")

        predictor = load_predictor()
        with st.spinner("Comparing both designs..."):
            sc_a = predictor.predict(img_a)
            sc_b = predictor.predict(img_b)

        winner, avg_a, avg_b = compare_verdict(sc_a, sc_b)
        gap = abs(avg_a - avg_b)

        winner_name = f"Design {winner}"
        loser_name  = "Design B" if winner == "A" else "Design A"
        w_scores    = sc_a if winner == "A" else sc_b
        l_scores    = sc_b if winner == "A" else sc_a

        # Winner banner
        if gap < 0.04:
            st.markdown(f"""
            <div class="winner-banner" style="background:linear-gradient(135deg,#4776e6,#8e54e9)">
              🤝 Very Close — Both Designs Are Similar
              <div style="font-size:1rem;font-weight:400;margin-top:8px;opacity:0.9">
                Both designs perform at a similar level. See the details below to choose.
              </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="winner-banner" style="background:linear-gradient(135deg,#11998e,#38ef7d)">
              🏆 {winner_name} is the Better Choice
              <div style="font-size:1rem;font-weight:400;margin-top:8px;opacity:0.9">
                {'By a clear margin' if gap > 0.10 else 'By a small margin'} —
                more customers are likely to respond positively to {winner_name}
              </div>
            </div>
            """, unsafe_allow_html=True)

        # Area by area comparison
        st.markdown("### 📋 Area by Area Breakdown")
        st.markdown("""
        <p style="color:rgba(255,255,255,0.6);margin-top:-8px">
        Here is how each packaging area compares between the two designs:
        </p>
        """, unsafe_allow_html=True)

        for c in CRITERIA:
            va = sc_a[c]; vb = sc_b[c]
            diff = va - vb
            if abs(diff) < 0.05:
                result = "🟡 Similar"
                col_txt = "#ffd200"
            elif diff > 0:
                result = "✅ Design A is better"
                col_txt = "#38ef7d"
            else:
                result = "✅ Design B is better"
                col_txt = "#38ef7d"

            lev_a = get_level(va)
            lev_b = get_level(vb)
            tag_a = "Good ✅" if lev_a=="strong" else "Average ⚡" if lev_a=="average" else "Weak ❌"
            tag_b = "Good ✅" if lev_b=="strong" else "Average ⚡" if lev_b=="average" else "Weak ❌"

            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
                        border-radius:12px;padding:14px 18px;margin:8px 0;
                        display:flex;justify-content:space-between;align-items:center">
              <div style="flex:1">
                <div style="color:white;font-weight:600">{CRITERIA_PLAIN[c]}</div>
              </div>
              <div style="flex:1;text-align:center">
                <span style="color:rgba(255,255,255,0.5);font-size:0.8rem">A: </span>
                <span style="color:white;font-size:0.85rem">{tag_a}</span>
              </div>
              <div style="flex:1;text-align:center">
                <span style="color:rgba(255,255,255,0.5);font-size:0.8rem">B: </span>
                <span style="color:white;font-size:0.85rem">{tag_b}</span>
              </div>
              <div style="flex:1;text-align:right;color:{col_txt};font-weight:600;font-size:0.85rem">
                {result}
              </div>
            </div>
            """, unsafe_allow_html=True)

        # What winner does well / what loser should fix
        st.markdown("<br>", unsafe_allow_html=True)
        col_w, col_l = st.columns(2, gap="large")

        with col_w:
            strong_in_winner = [c for c in CRITERIA if get_level(w_scores[c]) == "strong"]
            st.markdown(f"### ✅ Why {winner_name} Works Better")
            if strong_in_winner:
                for c in strong_in_winner[:3]:
                    st.markdown(f"""
                    <div class="fix-item">
                      <strong>{CRITERIA_PLAIN[c]}</strong> is strong in {winner_name} —
                      customers will respond well to this aspect.
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="fix-item">
                  {winner_name} performs better overall even if no single area is outstanding.
                  Small advantages across all areas add up.
                </div>
                """, unsafe_allow_html=True)

        with col_l:
            weak_in_loser = [(c, l_scores[c]) for c in CRITERIA if get_level(l_scores[c]) != "strong"]
            weak_in_loser.sort(key=lambda x: x[1])
            st.markdown(f"### ⚠️ What {loser_name} Should Fix")
            if weak_in_loser:
                for c, _ in weak_in_loser[:3]:
                    st.markdown(f"""
                    <div class="issue-item">
                      <strong>{CRITERIA_PLAIN[c]}</strong> is a weak area in {loser_name}.
                      {FIXES_BY_CRITERION[c][0]}
                    </div>
                    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — FIND BEST FROM MANY
# ══════════════════════════════════════════════════════════════════════════════
with tab3:

    st.markdown("""
    <div class="blue-card">
      <strong style="font-size:1.1rem">Have multiple designs and not sure which to launch?</strong><br>
      <span style="color:rgba(255,255,255,0.75)">
        Upload up to 5 packaging designs. Tell us your most important goal.
        We will rank them and tell you which one to go with — in plain language.
      </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🎯 Step 1 — What matters most to you?")
    goal = st.selectbox("", list(GOALS.keys()), key="goal_sel", label_visibility="collapsed")

    goal_descs = {
        "Most Eye-Catching on the Shelf":  "Best for products in busy supermarkets where you need to grab attention fast.",
        "Best Emotional Connection":       "Best when you want customers to feel something positive when they see your product.",
        "Strongest Brand Recognition":     "Best when building long-term brand loyalty and repeat purchases.",
        "Most Eco-Friendly Appeal":        "Best for targeting environmentally conscious customers.",
        "Best Overall for Customers":      "Best balanced approach covering all the things that matter to shoppers.",
    }
    st.markdown(f"""
    <div style="background:rgba(102,126,234,0.1);border:1px solid rgba(102,126,234,0.3);
                border-radius:12px;padding:12px 18px;margin:8px 0;color:rgba(255,255,255,0.75);
                font-size:0.9rem">
      💡 {goal_descs[goal]}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📦 Step 2 — Upload your designs (minimum 2)")
    upload_cols  = st.columns(5)
    all_designs  = []
    design_names = ["Design A","Design B","Design C","Design D","Design E"]
    for i, col in enumerate(upload_cols):
        f = col.file_uploader(design_names[i], type=["jpg","jpeg","png","bmp","webp"], key=f"d{i}")
        if f: all_designs.append((design_names[i], f))

    if len(all_designs) >= 2:
        if st.button("🚀 Find the Best Design", key="find_best"):
            predictor = load_predictor()
            results   = []

            with st.spinner("Analysing all your designs..."):
                for name, file in all_designs:
                    img    = Image.open(file).convert("RGB")
                    scores = predictor.predict(img)
                    gs     = goal_score(scores, goal)
                    results.append({"name":name, "image":img,
                                    "scores":scores, "goal_score":gs})

            results.sort(key=lambda x: x["goal_score"], reverse=True)

            # Winner announcement
            winner = results[0]
            margin = results[0]["goal_score"] - results[1]["goal_score"]
            confidence = "clear winner" if margin > 0.08 else "the best option"

            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#0d3d2e,#1a5c3a);
                        border:2px solid #38ef7d;border-radius:20px;
                        padding:32px;text-align:center;margin:20px 0">
              <div style="font-size:2.5rem">🏆</div>
              <div style="font-size:1.8rem;font-weight:700;color:#38ef7d;margin-top:8px">
                {winner["name"]} is your {confidence}
              </div>
              <div style="color:rgba(255,255,255,0.7);margin-top:10px;font-size:0.95rem">
                Based on your goal: <strong style="color:white">{goal}</strong>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # All designs ranked
            st.markdown("### 📊 Full Ranking — Best to Worst")
            rank_styles = [
                ("product-card-gold",   "🥇", "#FFD700"),
                ("product-card-silver", "🥈", "#C0C0C0"),
                ("product-card-bronze", "🥉", "#CD7F32"),
            ]

            for i, r in enumerate(results):
                card_class, medal, medal_color = rank_styles[i] if i < 3 else ("product-card", f"#{i+1}", "#aaaaaa")

                # Verdict for this design
                icon, verdict, vcolor, vdesc = plain_verdict(r["scores"])
                weak_here = [(c, r["scores"][c]) for c in CRITERIA if get_level(r["scores"][c]) != "strong"]
                weak_here.sort(key=lambda x: x[1])
                biggest_issue = ISSUES_BY_CRITERION[weak_here[0][0]][0] if weak_here else "No major issues found."
                top_fix       = FIXES_BY_CRITERION[weak_here[0][0]][0]  if weak_here else "Maintain the current quality."

                img_col, txt_col = st.columns([1, 3], gap="large")
                with img_col:
                    st.image(r["image"], use_container_width=True, caption=f"{medal} {r['name']}")
                with txt_col:
                    st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.04);border:1px solid {medal_color}44;
                                border-left:5px solid {medal_color};border-radius:16px;padding:20px">
                      <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px">
                        <span style="font-size:2rem">{medal}</span>
                        <div>
                          <div style="font-size:1.2rem;font-weight:700;color:white">{r['name']}</div>
                          <span style="color:{vcolor};font-size:0.85rem;font-weight:600">{icon} {verdict}</span>
                        </div>
                      </div>
                      <div style="color:rgba(255,255,255,0.55);font-size:0.82rem;margin-bottom:10px">
                        {vdesc}
                      </div>
                      <div class="issue-item" style="font-size:0.85rem">
                        ❌ Main Issue: {biggest_issue}
                      </div>
                      <div class="fix-item" style="font-size:0.85rem">
                        ✅ Quick Fix: {top_fix}
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

    elif len(all_designs) == 1:
        st.info("⚠️ Please upload at least 2 designs to compare.")
    else:
        st.markdown("""
        <div style="text-align:center;padding:48px;color:rgba(255,255,255,0.3)">
          <div style="font-size:4rem">📦</div>
          <div style="margin-top:12px;font-size:1rem">
            Upload 2 to 5 packaging designs above to get started
          </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — ELECTRONICS RECOMMENDER
# ══════════════════════════════════════════════════════════════════════════════
with tab4:

    st.markdown("""
    <div class="elec-hero">
      <div style="font-size:3rem">🛒</div>
      <h2 style="color:white;margin:12px 0 8px;font-size:1.8rem">
        Find the Best Electronics for You
      </h2>
      <p style="color:rgba(255,255,255,0.7);font-size:1rem;max-width:600px;margin:0 auto">
        Just tell us what you want to buy. Our AI — trained on millions of real Amazon reviews —
        will recommend the products that customers love the most.
      </p>
    </div>
    """, unsafe_allow_html=True)

    catalog = load_catalog()

    if not catalog:
        st.error("Product catalog not found. Please upload electronics_catalog.json to the app folder.")
    else:
        # Search box
        st.markdown('<div class="search-box">', unsafe_allow_html=True)
        scol1, scol2, scol3 = st.columns([4, 1, 1], gap="medium")
        with scol1:
            query = st.text_input(
                "🔍 What do you want to buy?",
                placeholder="e.g. laptop, headphone, smartphone, tablet, camera, speaker, smartwatch...",
                key="elec_q"
            )
        with scol2:
            top_n = st.selectbox("Show top", [3, 5, 10], key="topn")
        with scol3:
            st.markdown("<br>", unsafe_allow_html=True)
            go = st.button("Search 🔍", key="go_btn")
        st.markdown('</div>', unsafe_allow_html=True)

        # Category chips
        st.markdown("""
        <div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:20px">
          <span style="color:rgba(255,255,255,0.5);font-size:0.85rem;padding:6px 0">Quick pick:</span>
        """, unsafe_allow_html=True)
        cats = ["💻 laptop","🎧 headphone","📱 smartphone","⌚ smartwatch","🔊 speaker","📷 camera","📱 tablet"]
        cat_cols = st.columns(len(cats))
        clicked_cat = None
        for i, (col, cat) in enumerate(zip(cat_cols, cats)):
            if col.button(cat, key=f"chip_{i}"):
                clicked_cat = cat.split(" ")[1]
        st.markdown("</div>", unsafe_allow_html=True)

        # Use either typed query or clicked chip
        search_term = clicked_cat if clicked_cat else (query.strip() if go or query.strip() else "")

        if search_term:
            keyword_map = {
                "laptop":"laptop","computer":"laptop","notebook":"laptop",
                "headphone":"headphone","earphone":"headphone","earbuds":"headphone","headset":"headphone",
                "phone":"smartphone","smartphone":"smartphone","mobile":"smartphone","iphone":"smartphone",
                "watch":"smartwatch","smartwatch":"smartwatch",
                "speaker":"speaker","bluetooth":"speaker",
                "tablet":"tablet","ipad":"tablet",
                "camera":"camera","dslr":"camera","mirrorless":"camera","gopro":"camera",
            }
            q         = search_term.lower()
            cat_match = next((v for k,v in keyword_map.items() if k in q), None)
            filtered  = ([p for p in catalog if p["category"]==cat_match]
                         if cat_match else
                         [p for p in catalog if q in p["name"].lower() or q in p["brand"].lower()])

            if not filtered:
                st.markdown(f"""
                <div style="background:rgba(255,65,108,0.08);border:1px solid rgba(255,65,108,0.3);
                            border-radius:14px;padding:20px;text-align:center">
                  <div style="font-size:2rem">🤔</div>
                  <div style="color:white;margin-top:8px">
                    No products found for <strong>"{search_term}"</strong>
                  </div>
                  <div style="color:rgba(255,255,255,0.5);margin-top:4px;font-size:0.9rem">
                    Try: laptop, headphone, smartphone, tablet, camera, speaker or smartwatch
                  </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Score products
                with st.spinner(f"Our AI is analysing {len(filtered)} {search_term}s for you..."):
                    try:
                        e_model, e_tok, e_dev = load_elec_model()
                        scored = []
                        bar    = st.progress(0, text="Reading customer reviews...")
                        for i, p in enumerate(filtered):
                            pos, neu, neg = get_elec_score(p["review"], e_model, e_tok, e_dev)
                            scored.append({**p, "pos":pos*100, "neu":neu*100, "neg":neg*100})
                            bar.progress((i+1)/len(filtered), text=f"Analysed: {p['name']}")
                        bar.empty()
                        scored.sort(key=lambda x: x["pos"], reverse=True)
                        top = scored[:top_n]

                        # Header
                        st.markdown(f"""
                        <div style="background:linear-gradient(135deg,rgba(56,239,125,0.1),rgba(17,153,142,0.05));
                                    border:1px solid rgba(56,239,125,0.25);border-radius:16px;
                                    padding:20px;text-align:center;margin:16px 0">
                          <div style="font-size:1.3rem;font-weight:700;color:#38ef7d">
                            🏆 Top {len(top)} {search_term.title()}s — Ranked by Customer Approval
                          </div>
                          <div style="color:rgba(255,255,255,0.55);font-size:0.85rem;margin-top:4px">
                            Based on real Amazon customer reviews · Higher approval = more customers love it
                          </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Product cards
                        for rank, p in enumerate(top, 1):
                            pos_pct = p["pos"]

                            if pos_pct >= 70:
                                border_col = "#38ef7d"
                                badge_html = '<span class="badge-green">🌟 Highly Recommended</span>'
                                bar_col    = "#38ef7d"
                                verdict_txt = "Customers love this product. A safe and excellent choice."
                            elif pos_pct >= 50:
                                border_col = "#ffd200"
                                badge_html = '<span class="badge-yellow">👍 Good Choice</span>'
                                bar_col    = "#ffd200"
                                verdict_txt = "Most customers are happy with this product."
                            else:
                                border_col = "#ff6b6b"
                                badge_html = '<span class="badge-red">⚠️ Mixed Reviews</span>'
                                bar_col    = "#ff6b6b"
                                verdict_txt = "Some customers have mixed feelings about this product."

                            medals = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
                            medal  = medals[rank-1] if rank <= 10 else f"#{rank}"

                            # Approval bar width
                            bar_w = int(pos_pct)

                            st.markdown(f"""
                            <div style="background:rgba(255,255,255,0.03);
                                        border:1px solid {border_col}55;
                                        border-left:6px solid {border_col};
                                        border-radius:18px;padding:24px;margin:14px 0">

                              <!-- Header row -->
                              <div style="display:flex;justify-content:space-between;
                                          align-items:flex-start;flex-wrap:wrap;gap:10px">
                                <div>
                                  <div style="display:flex;align-items:center;gap:10px">
                                    <span style="font-size:1.8rem">{medal}</span>
                                    <div>
                                      <div style="font-size:1.15rem;font-weight:700;color:white">
                                        {p["name"]}
                                      </div>
                                      <div style="color:rgba(255,255,255,0.45);font-size:0.82rem;margin-top:2px">
                                        by {p["brand"]} &nbsp;·&nbsp; {p["price"]}
                                      </div>
                                    </div>
                                  </div>
                                </div>
                                <div style="text-align:right">
                                  {badge_html}
                                </div>
                              </div>

                              <!-- Approval bar -->
                              <div style="margin:16px 0 8px">
                                <div style="display:flex;justify-content:space-between;
                                            color:rgba(255,255,255,0.6);font-size:0.8rem;margin-bottom:6px">
                                  <span>Customer Approval</span>
                                  <span style="color:{bar_col};font-weight:700">{pos_pct:.0f}% positive</span>
                                </div>
                                <div style="background:rgba(255,255,255,0.08);border-radius:50px;height:12px;overflow:hidden">
                                  <div style="width:{bar_w}%;background:linear-gradient(90deg,{bar_col}cc,{bar_col});
                                              height:12px;border-radius:50px;
                                              box-shadow:0 0 12px {bar_col}66"></div>
                                </div>
                              </div>

                              <!-- Verdict text -->
                              <div style="color:rgba(255,255,255,0.65);font-size:0.88rem;margin-top:8px">
                                {verdict_txt}
                              </div>

                              <!-- Review snippet -->
                              <div style="background:rgba(255,255,255,0.04);border-radius:10px;
                                          padding:12px 14px;margin-top:12px;
                                          color:rgba(255,255,255,0.5);font-size:0.82rem;
                                          font-style:italic;border-left:3px solid {border_col}55">
                                💬 "{p['review'][:160]}..."
                              </div>

                            </div>
                            """, unsafe_allow_html=True)

                        # Download
                        st.markdown("<br>", unsafe_allow_html=True)
                        dl_data = [{"rank":i+1,"name":p["name"],"brand":p["brand"],"price":p["price"],"customer_approval":f"{p['pos']:.0f}%","verdict":"Highly Recommended" if p["pos"]>=70 else "Good Choice" if p["pos"]>=50 else "Mixed Reviews"} for i,p in enumerate(top)]
                        st.download_button(
                            "⬇️ Download Recommendations",
                            data=json.dumps(dl_data, indent=2),
                            file_name=f"best_{search_term}_recommendations.json",
                            mime="application/json"
                        )

                    except Exception as e:
                        st.error(f"Could not load AI model: {e}")
                        st.info("Make sure electronics_model.pth is available and the Google Drive link is public.")
