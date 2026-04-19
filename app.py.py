
import streamlit as st
import os, json, datetime
from PIL import Image

st.set_page_config(
    page_title="PackageAI",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
* { font-family: 'Poppins', sans-serif; }
.main { background: #0f0f1a; }
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
    color: white;
}
[data-testid="stHeader"] { background: transparent; }
.hero {
    text-align: center;
    padding: 40px 20px 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20px;
    margin-bottom: 30px;
    box-shadow: 0 20px 60px rgba(102,126,234,0.3);
}
.hero h1 { font-size:3rem;font-weight:700;color:white;margin:0; }
.hero p { color:rgba(255,255,255,0.85);font-size:1.1rem;margin-top:10px; }
.card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 24px;
    margin: 12px 0;
    backdrop-filter: blur(10px);
}
.strategy-badge {
    display:inline-block;padding:12px 28px;border-radius:50px;
    font-size:1.4rem;font-weight:700;margin:10px 0;
    box-shadow:0 8px 30px rgba(0,0,0,0.3);
}
.score-label { color:rgba(255,255,255,0.7);font-size:0.85rem;margin-bottom:4px; }
.cs-number {
    font-size:3.5rem;font-weight:700;
    background:linear-gradient(135deg,#667eea,#764ba2);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1;
}
.winner-banner {
    text-align:center;padding:24px;border-radius:16px;
    font-size:1.8rem;font-weight:700;margin:20px 0;
}
.tip-card {
    background:rgba(102,126,234,0.15);border-left:4px solid #667eea;
    border-radius:8px;padding:14px 18px;margin:8px 0;color:white;
}
.metric-box {
    background:rgba(255,255,255,0.05);border-radius:12px;padding:16px;
    text-align:center;border:1px solid rgba(255,255,255,0.1);
}
.recommend-card {
    background: linear-gradient(135deg,rgba(102,126,234,0.2),rgba(118,75,162,0.2));
    border: 2px solid #667eea;border-radius:16px;padding:24px;margin:12px 0;
}
.goal-selected {
    background:linear-gradient(135deg,#667eea,#764ba2) !important;
    color:white !important;border:none !important;
}
div[data-testid="stTabs"] button {
    color:white !important;font-size:1rem !important;font-weight:600 !important;
}
.stButton button {
    background:linear-gradient(135deg,#667eea,#764ba2) !important;
    color:white !important;border:none !important;border-radius:50px !important;
    padding:12px 32px !important;font-weight:600 !important;font-size:1rem !important;
    box-shadow:0 4px 15px rgba(102,126,234,0.4) !important;
}
[data-testid="stFileUploader"] {
    background:rgba(255,255,255,0.03) !important;
    border:2px dashed rgba(102,126,234,0.5) !important;
    border-radius:16px !important;padding:20px !important;
}
.stSlider label { color:rgba(255,255,255,0.8) !important; }
.rank-1 { color:#ffd700;font-size:1.5rem; }
.rank-2 { color:#c0c0c0;font-size:1.3rem; }
.rank-3 { color:#cd7f32;font-size:1.2rem; }
</style>
""", unsafe_allow_html=True)

MODEL_PATH = os.environ.get("MODEL_PATH","./packaging_model.pth")

@st.cache_resource(show_spinner="🧠 Loading AI Model...")
def load_predictor():
    from macros_engine import PackagingPredictor
    return PackagingPredictor(MODEL_PATH)

CRITERIA = ["visual_appeal","emotional_resonance",
            "brand_recall","functionality","sustainability"]
LABELS = {
    "visual_appeal":       "🎨 Visual Appeal",
    "emotional_resonance": "❤️ Emotional Resonance",
    "brand_recall":        "🧠 Brand Recall",
    "functionality":       "⚙️ Functionality",
    "sustainability":      "🌿 Sustainability",
}
STRATEGY_COLORS = {
    "Bold & Vibrant": ("linear-gradient(135deg,#ff416c,#ff4b2b)","#ff416c"),
    "Eco-Friendly":   ("linear-gradient(135deg,#11998e,#38ef7d)","#11998e"),
    "Minimalist":     ("linear-gradient(135deg,#4776e6,#8e54e9)","#4776e6"),
    "Interactive":    ("linear-gradient(135deg,#f7971e,#ffd200)","#f7971e"),
}
WEIGHTS = dict(zip(CRITERIA,[0.3,0.4,0.1,0.1,0.1]))

# Goal definitions — each goal has custom weights
GOALS = {
    "🎯 Maximum Customer Attraction":
        {"visual_appeal":0.4,"emotional_resonance":0.4,
         "brand_recall":0.1,"functionality":0.05,"sustainability":0.05},
    "🌿 Most Eco-Friendly":
        {"visual_appeal":0.1,"emotional_resonance":0.1,
         "brand_recall":0.1,"functionality":0.1,"sustainability":0.6},
    "🧠 Strongest Brand Memory":
        {"visual_appeal":0.2,"emotional_resonance":0.2,
         "brand_recall":0.5,"functionality":0.05,"sustainability":0.05},
    "⚖️ Best Overall Balance":
        {"visual_appeal":0.2,"emotional_resonance":0.2,
         "brand_recall":0.2,"functionality":0.2,"sustainability":0.2},
    "🏪 Best Shelf Visibility":
        {"visual_appeal":0.5,"emotional_resonance":0.3,
         "brand_recall":0.1,"functionality":0.05,"sustainability":0.05},
}

GOAL_DESCRIPTIONS = {
    "🎯 Maximum Customer Attraction":
        "Prioritises designs that immediately grab attention and create emotional connection.",
    "🌿 Most Eco-Friendly":
        "Best for brands targeting environmentally conscious consumers.",
    "🧠 Strongest Brand Memory":
        "Ideal when brand recognition and repeat purchase is the main goal.",
    "⚖️ Best Overall Balance":
        "Equal weight across all criteria — best all-rounder design.",
    "🏪 Best Shelf Visibility":
        "Maximises visual impact — best for standing out in crowded retail shelves.",
}

BEST_FOR = {
    "visual_appeal":       "Most Eye-Catching",
    "emotional_resonance": "Strongest Emotional Connect",
    "brand_recall":        "Best Brand Memory",
    "functionality":       "Most Functional",
    "sustainability":      "Most Eco-Friendly",
}

def score_bar(name, value):
    pct = int(value*100)
    color = "#38ef7d" if value>=0.70 else "#ffd200" if value>=0.55 else "#ff416c"
    st.markdown(f"""
    <div style="margin:8px 0">
      <div style="display:flex;justify-content:space-between;
                  color:rgba(255,255,255,0.7);font-size:0.85rem;margin-bottom:4px">
        <span>{LABELS[name]}</span>
        <span style="color:{color};font-weight:700">{value:.2f}</span>
      </div>
      <div style="background:rgba(255,255,255,0.1);border-radius:50px;
                  height:10px;overflow:hidden">
        <div style="width:{pct}%;background:{color};height:10px;border-radius:50px;
                    box-shadow:0 0 10px {color}88"></div>
      </div>
    </div>""", unsafe_allow_html=True)

def compute_goal_score(scores, goal):
    w = GOALS[goal]
    return round(sum(w[c]*scores[c] for c in CRITERIA), 4)

# ── HERO ──
st.markdown("""
<div class="hero">
  <h1>📦 PackageAI</h1>
  <p>Real-Time Packaging Attention Predictor · Deep Learning + MACROS Ranking</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Analyze Design",
    "⚖️ Compare Designs",
    "🏆 Find Best Design",
    "📊 About"
])

# ══════════════════════════════════════════
# TAB 1 — SINGLE ANALYSIS
# ══════════════════════════════════════════
with tab1:
    uploaded = st.file_uploader(
        "Drop your packaging image here",
        type=["jpg","jpeg","png","bmp","webp"], key="single"
    )
    if uploaded:
        image = Image.open(uploaded).convert("RGB")
        predictor = load_predictor()
        col_img, col_res = st.columns([1,2], gap="large")

        with col_img:
            st.image(image, use_container_width=True, caption="Your Design")

        with col_res:
            with st.spinner("🤖 Analyzing your design..."):
                from macros_engine import full_report
                scores = predictor.predict(image)
                report = full_report(scores)

            cs = report["consensus_score"]
            strategy = report["strategy"]
            sname = strategy["name"]
            grad, color = STRATEGY_COLORS.get(
                sname,("linear-gradient(135deg,#667eea,#764ba2)","#667eea"))

            st.markdown(f"""
            <div style="text-align:center;margin:10px 0 20px">
              <div class="strategy-badge" style="background:{grad};color:white">
                {strategy["code"]} — {sname}
              </div>
              <p style="color:rgba(255,255,255,0.6);font-size:0.9rem;margin-top:8px">
                {strategy["description"]}
              </p>
            </div>""", unsafe_allow_html=True)

            c1,c2,c3 = st.columns(3)
            c1.markdown(f"""
            <div class="metric-box">
              <div class="score-label">Consensus Score</div>
              <div class="cs-number">{cs:.3f}</div>
            </div>""", unsafe_allow_html=True)
            c2.markdown(f"""
            <div class="metric-box">
              <div class="score-label">Strategy</div>
              <div style="font-size:1.3rem;font-weight:700;
                          color:{color};margin-top:4px">{sname}</div>
            </div>""", unsafe_allow_html=True)
            c3.markdown(f"""
            <div class="metric-box">
              <div class="score-label">Weakest Area</div>
              <div style="font-size:0.95rem;font-weight:600;
                          color:#ff416c;margin-top:4px">
                {LABELS[report["weakest_criterion"]]}
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 📊 Criterion Scores")
        for c in CRITERIA:
            score_bar(c, scores[c])
        st.markdown("</div>", unsafe_allow_html=True)

        # ── IMPROVEMENT SUGGESTIONS ──
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"### 💡 How to Improve "
                    f"{LABELS[report['weakest_criterion']]}")

        weakest = report["weakest_criterion"]
        wscore  = scores[weakest]

        # Specific suggestions based on actual score value
        specific_tips = {
            "visual_appeal": [
                f"Your Visual Appeal is {wscore:.2f} — colours lack energy. "
                f"Switch to a warm bold palette (reds, oranges, yellows).",
                "Add a large hero product image occupying at least 40% of the front face.",
                "Use maximum 3 colours — too many colours reduce visual focus.",
                f"Expected improvement: Visual Appeal {wscore:.2f} → "
                f"{min(wscore+0.25,0.95):.2f} after redesign.",
            ],
            "emotional_resonance": [
                f"Your Emotional Resonance is {wscore:.2f} — packaging feels cold. "
                f"Add warm tones like amber (#e8892b) or coral (#ff6b6b).",
                "Include a human element — a face, hands, or lifestyle moment "
                "increases emotional connection by up to 30%.",
                "Add a short emotional tagline below the product name "
                "(e.g. 'Made with love' or 'For your best moments').",
                f"Expected improvement: Emotional Resonance {wscore:.2f} → "
                f"{min(wscore+0.28,0.95):.2f} after changes.",
            ],
            "brand_recall": [
                f"Your Brand Recall is {wscore:.2f} — logo and brand name "
                f"are not memorable enough.",
                "Position logo top-centre or top-left — eye-tracking studies "
                "show this zone gets first fixation.",
                "Use a unique shape or mascot that consumers can associate "
                "with your brand instantly.",
                f"Expected improvement: Brand Recall {wscore:.2f} → "
                f"{min(wscore+0.22,0.95):.2f} after repositioning.",
            ],
            "functionality": [
                f"Your Functionality score is {wscore:.2f} — text is hard to "
                f"read. Increase contrast ratio to at least 4.5:1.",
                "Use a clean sans-serif font at minimum 12pt for all key info.",
                "Add clear icons for: serving size, storage instructions, "
                "and best-before date.",
                f"Expected improvement: Functionality {wscore:.2f} → "
                f"{min(wscore+0.20,0.95):.2f} after typography fix.",
            ],
            "sustainability": [
                f"Your Sustainability score is {wscore:.2f} — no eco signals "
                f"visible. Add earthy greens or kraft-paper textures.",
                "Add a prominent recycling symbol with '100% Recyclable' text.",
                "Replace glossy finish design cues with matte/natural texture visuals.",
                f"Expected improvement: Sustainability {wscore:.2f} → "
                f"{min(wscore+0.30,0.95):.2f} after eco redesign.",
            ],
        }

        tips = specific_tips.get(weakest, report["improvement_tips"])
        for i, tip in enumerate(tips, 1):
            icon = "⚠️" if i==1 else "✅" if i==4 else "💡"
            st.markdown(f"""
            <div class="tip-card">
              <strong>{icon} #{i}</strong> {tip}
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── WHAT-IF ──
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 🔮 What-If Simulator")
        st.caption("Drag sliders to simulate improvements")
        adj = {}
        cols = st.columns(5)
        for i,c in enumerate(CRITERIA):
            adj[c] = cols[i].slider(
                LABELS[c],0.0,1.0,float(scores[c]),0.01,key=f"s_{c}")

        from macros_engine import compute_cs, map_strategy
        new_cs = compute_cs(adj)
        new_st = map_strategy(new_cs)
        delta  = new_cs - cs
        dcol   = "#38ef7d" if delta>=0 else "#ff416c"
        dsign  = "+" if delta>=0 else ""

        st.markdown(f"""
        <div style="background:rgba(102,126,234,0.15);border-radius:12px;
                    padding:16px;margin-top:12px;text-align:center">
          New CS: <strong style="color:#667eea;font-size:1.4rem">{new_cs:.3f}</strong>
          &nbsp;|&nbsp;
          Change: <strong style="color:{dcol}">{dsign}{delta:.3f}</strong>
          &nbsp;|&nbsp;
          Strategy: <strong style="color:{dcol}">{new_st["name"]}</strong>
        </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.download_button(
            "⬇️ Download Full Report",
            data=json.dumps(report, indent=2),
            file_name=f"report_{uploaded.name}.json",
            mime="application/json"
        )

# ══════════════════════════════════════════
# TAB 2 — COMPARE TWO DESIGNS
# ══════════════════════════════════════════
with tab2:
    st.markdown("### Upload Two Designs to Compare")
    c1, c2 = st.columns(2, gap="large")
    up_a = c1.file_uploader("📦 Design A",
                             type=["jpg","jpeg","png","bmp","webp"],key="A")
    up_b = c2.file_uploader("📦 Design B",
                             type=["jpg","jpeg","png","bmp","webp"],key="B")

    if up_a and up_b:
        img_a = Image.open(up_a).convert("RGB")
        img_b = Image.open(up_b).convert("RGB")
        c1.image(img_a, use_container_width=True, caption="Design A")
        c2.image(img_b, use_container_width=True, caption="Design B")

        predictor = load_predictor()
        with st.spinner("🤖 Comparing designs..."):
            from macros_engine import compare_designs
            sc_a = predictor.predict(img_a)
            sc_b = predictor.predict(img_b)
            comp = compare_designs(sc_a, sc_b)

        winner = comp["overall_winner"]
        w_grad, w_color = STRATEGY_COLORS.get(
            comp[f"strategy_{winner.lower()}"]["name"],
            ("linear-gradient(135deg,#667eea,#764ba2)","#667eea"))

        st.markdown(f"""
        <div class="winner-banner" style="background:{w_grad}">
          🏆 Design {winner} Wins!
          <div style="font-size:1rem;font-weight:400;margin-top:6px;opacity:0.9">
            CS<sub>A</sub> = {comp["design_a_cs"]}
            &nbsp;vs&nbsp;
            CS<sub>B</sub> = {comp["design_b_cs"]}
          </div>
        </div>""", unsafe_allow_html=True)

        ca, cb = st.columns(2, gap="large")
        ga,cola = STRATEGY_COLORS.get(comp["strategy_a"]["name"],
            ("linear-gradient(135deg,#667eea,#764ba2)","#667eea"))
        gb,colb = STRATEGY_COLORS.get(comp["strategy_b"]["name"],
            ("linear-gradient(135deg,#667eea,#764ba2)","#667eea"))

        ca.markdown(f"""
        <div class="card" style="text-align:center">
          <div style="font-size:1.1rem;color:rgba(255,255,255,0.6)">Design A</div>
          <div style="font-size:2.5rem;font-weight:700;color:{cola}">
            {comp["design_a_cs"]}</div>
          <div style="color:{cola};font-weight:600">
            {comp["strategy_a"]["name"]}</div>
        </div>""", unsafe_allow_html=True)

        cb.markdown(f"""
        <div class="card" style="text-align:center">
          <div style="font-size:1.1rem;color:rgba(255,255,255,0.6)">Design B</div>
          <div style="font-size:2.5rem;font-weight:700;color:{colb}">
            {comp["design_b_cs"]}</div>
          <div style="color:{colb};font-weight:600">
            {comp["strategy_b"]["name"]}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 📊 Criterion Breakdown")
        for c in CRITERIA:
            d = comp["per_criterion"][c]
            better = d["better"]
            col1,col2,col3,col4,col5 = st.columns([2,2,2,2,1])
            col1.markdown(
                f"<span style='color:rgba(255,255,255,0.7)'>{LABELS[c]}</span>",
                unsafe_allow_html=True)
            ba = "🟢" if better=="A" else "🔴" if better=="B" else "🟡"
            bb = "🟢" if better=="B" else "🔴" if better=="A" else "🟡"
            col2.markdown(f"{ba} **{d['design_a']:.3f}**")
            col3.markdown(f"{bb} **{d['design_b']:.3f}**")
            col4.markdown(f"Diff: **{d['diff_b_minus_a']:+.3f}**")
            col5.markdown(
                f"<span style='color:#38ef7d;font-weight:700'>"
                f"{'A' if better=='A' else 'B' if better=='B' else '='}"
                f"</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════
# TAB 3 — FIND BEST DESIGN (NEW FEATURE)
# ══════════════════════════════════════════
with tab3:
    st.markdown("""
    <div class="card">
      <h3>🏆 Packaging Recommender Engine</h3>
      <p style="color:rgba(255,255,255,0.7)">
        Upload up to 5 packaging designs. Tell us your goal.
        Our AI will recommend the BEST design for you —
        just like how a car recommender picks the best car
        based on what matters most to you.
      </p>
    </div>""", unsafe_allow_html=True)

    # ── GOAL SELECTION ──
    st.markdown("### 🎯 Step 1 — What is Your Goal?")
    goal = st.selectbox(
        "Choose what matters most to you:",
        list(GOALS.keys()),
        key="goal_select"
    )

    goal_grad, goal_color = {
        "🎯 Maximum Customer Attraction":
            ("linear-gradient(135deg,#ff416c,#ff4b2b)","#ff416c"),
        "🌿 Most Eco-Friendly":
            ("linear-gradient(135deg,#11998e,#38ef7d)","#11998e"),
        "🧠 Strongest Brand Memory":
            ("linear-gradient(135deg,#4776e6,#8e54e9)","#4776e6"),
        "⚖️ Best Overall Balance":
            ("linear-gradient(135deg,#667eea,#764ba2)","#667eea"),
        "🏪 Best Shelf Visibility":
            ("linear-gradient(135deg,#f7971e,#ffd200)","#f7971e"),
    }.get(goal, ("linear-gradient(135deg,#667eea,#764ba2)","#667eea"))

    st.markdown(f"""
    <div style="background:{goal_grad};border-radius:12px;
                padding:14px 20px;margin:8px 0">
      <strong style="color:white">{goal}</strong><br>
      <span style="color:rgba(255,255,255,0.85);font-size:0.9rem">
        {GOAL_DESCRIPTIONS[goal]}
      </span>
    </div>""", unsafe_allow_html=True)

    # ── UPLOAD DESIGNS ──
    st.markdown("### 📦 Step 2 — Upload Your Designs (2 to 5 images)")

    cols_up = st.columns(5)
    uploaded_designs = []
    design_labels = ["Design A","Design B","Design C","Design D","Design E"]

    for i, col in enumerate(cols_up):
        f = col.file_uploader(
            design_labels[i],
            type=["jpg","jpeg","png","bmp","webp"],
            key=f"rec_{i}"
        )
        if f:
            uploaded_designs.append((design_labels[i], f))

    if len(uploaded_designs) >= 2:
        st.markdown("### 🤖 Step 3 — Get Recommendation")

        if st.button("🚀 Find Best Design for My Goal"):
            predictor = load_predictor()
            results = []

            with st.spinner("Analyzing all designs..."):
                for name, file in uploaded_designs:
                    img    = Image.open(file).convert("RGB")
                    scores = predictor.predict(img)
                    gs     = compute_goal_score(scores, goal)
                    from macros_engine import compute_cs, map_strategy
                    cs     = compute_cs(scores)
                    strat  = map_strategy(cs)
                    results.append({
                        "name":    name,
                        "image":   img,
                        "scores":  scores,
                        "goal_score": gs,
                        "cs":      cs,
                        "strategy": strat,
                    })

            # Sort by goal score
            results.sort(key=lambda x: x["goal_score"], reverse=True)
            winner = results[0]
            wg, wc = STRATEGY_COLORS.get(
                winner["strategy"]["name"],
                ("linear-gradient(135deg,#667eea,#764ba2)","#667eea"))

            # ── WINNER BANNER ──
            st.markdown(f"""
            <div class="winner-banner" style="background:{wg}">
              🏆 RECOMMENDED: {winner["name"]}
              <div style="font-size:1rem;font-weight:400;
                          margin-top:8px;opacity:0.9">
                Best for: {goal} &nbsp;|&nbsp;
                Goal Score: {winner["goal_score"]:.3f} &nbsp;|&nbsp;
                Strategy: {winner["strategy"]["name"]}
              </div>
            </div>""", unsafe_allow_html=True)

            # ── SHOW ALL DESIGNS WITH SCORES ──
            st.markdown("### 📊 Full Comparison")
            rank_icons = ["🥇","🥈","🥉","4️⃣","5️⃣"]

            img_cols = st.columns(len(results))
            for i, (col, r) in enumerate(zip(img_cols, results)):
                col.image(r["image"], use_container_width=True,
                          caption=f"{rank_icons[i]} {r['name']}")
                rg, rc = STRATEGY_COLORS.get(
                    r["strategy"]["name"],
                    ("linear-gradient(135deg,#667eea,#764ba2)","#667eea"))
                col.markdown(f"""
                <div style="text-align:center;margin-top:4px">
                  <div style="font-size:1.5rem;font-weight:700;color:{rc}">
                    {r["goal_score"]:.3f}
                  </div>
                  <div style="color:rgba(255,255,255,0.6);font-size:0.8rem">
                    Goal Score
                  </div>
                  <div style="color:{rc};font-size:0.85rem;font-weight:600">
                    {r["strategy"]["name"]}
                  </div>
                </div>""", unsafe_allow_html=True)

            # ── DETAILED SCORE TABLE ──
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("#### 📋 Detailed Scores")

            header = "| Design | " + " | ".join(
                [LABELS[c] for c in CRITERIA]) + " | CS | Goal Score | Rank |"
            sep = "|--------|" + "|---------|"*5 + "|----|-----------|------|"
            st.markdown(header)
            st.markdown(sep)

            for i, r in enumerate(results):
                row = f"| {rank_icons[i]} {r['name']} |"
                for c in CRITERIA:
                    v = r["scores"][c]
                    emoji = "🟢" if v>=0.70 else "🟡" if v>=0.55 else "🔴"
                    row += f" {emoji} {v:.2f} |"
                row += f" {r['cs']:.3f} | **{r['goal_score']:.3f}** |"
                row += f" #{i+1} |"
                st.markdown(row)

            st.markdown("</div>", unsafe_allow_html=True)

            # ── WHY WINNER ──
            st.markdown("<div class='recommend-card'>", unsafe_allow_html=True)
            st.markdown(f"### 💡 Why {winner['name']} is Recommended")

            ws = winner["scores"]
            best_criterion = max(CRITERIA, key=lambda c: ws[c])
            weak_criterion = min(CRITERIA, key=lambda c: ws[c])

            st.markdown(f"""
            <div class="tip-card">
              ✅ <strong>Strongest at:</strong>
              {LABELS[best_criterion]} ({ws[best_criterion]:.2f})
              — this directly drives {goal}
            </div>
            <div class="tip-card">
              ✅ <strong>Strategy:</strong>
              {winner["strategy"]["name"]} —
              {winner["strategy"]["description"]}
            </div>
            <div class="tip-card">
              ⚠️ <strong>One thing to improve:</strong>
              {LABELS[weak_criterion]} is {ws[weak_criterion]:.2f} —
              fixing this could push Goal Score to
              {min(winner["goal_score"]+0.08,1.0):.3f}
            </div>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # ── BEST DESIGN PER CATEGORY ──
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("#### 🎯 Best Design for Each Goal")
            for c in CRITERIA:
                best = max(results, key=lambda r: r["scores"][c])
                st.markdown(
                    f"**{BEST_FOR[c]}** → "
                    f"🏅 {best['name']} ({best['scores'][c]:.2f})")
            st.markdown("</div>", unsafe_allow_html=True)

            # ── DOWNLOAD REPORT ──
            report_data = {
                "goal":        goal,
                "recommended": winner["name"],
                "goal_score":  winner["goal_score"],
                "strategy":    winner["strategy"]["name"],
                "rankings": [
                    {"rank": i+1, "name": r["name"],
                     "goal_score": r["goal_score"],
                     "cs": r["cs"], "scores": r["scores"]}
                    for i,r in enumerate(results)
                ]
            }
            st.download_button(
                "⬇️ Download Recommendation Report",
                data=json.dumps(report_data, indent=2),
                file_name="recommendation_report.json",
                mime="application/json"
            )

    elif len(uploaded_designs) == 1:
        st.info("⚠️ Please upload at least 2 designs to compare")
    else:
        st.markdown("""
        <div style="text-align:center;padding:40px;
                    color:rgba(255,255,255,0.4)">
          <div style="font-size:3rem">📦</div>
          <div style="margin-top:12px">
            Upload 2–5 designs above to get started
          </div>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# TAB 4 — ABOUT
# ══════════════════════════════════════════
with tab4:
    st.markdown("""
    <div class="card">
      <h3>🎯 About PackageAI</h3>
      <p style="color:rgba(255,255,255,0.7)">
        Real-Time Packaging Attention Prediction System using Deep Learning
        and MACROS Ranking. Final Year Major Project.
      </p>
    </div>""", unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    c1.markdown("""<div class="metric-box">
      <div style="font-size:2rem">🧠</div>
      <div style="font-weight:700;margin:8px 0">MobileNetV2</div>
      <div style="color:rgba(255,255,255,0.6);font-size:0.85rem">
        Deep Learning Model</div>
    </div>""", unsafe_allow_html=True)
    c2.markdown("""<div class="metric-box">
      <div style="font-size:2rem">📊</div>
      <div style="font-weight:700;margin:8px 0">MACROS</div>
      <div style="color:rgba(255,255,255,0.6);font-size:0.85rem">
        Multi-Criteria Ranking</div>
    </div>""", unsafe_allow_html=True)
    c3.markdown("""<div class="metric-box">
      <div style="font-size:2rem">📦</div>
      <div style="font-weight:700;margin:8px 0">5058 Images</div>
      <div style="color:rgba(255,255,255,0.6);font-size:0.85rem">
        Biscuit Wrappers Dataset</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
      <h4>⚖️ MACROS Weights</h4>
      <table style="width:100%;color:rgba(255,255,255,0.8)">
        <tr><td>🎨 Visual Appeal</td><td><b>30%</b></td></tr>
        <tr><td>❤️ Emotional Resonance</td><td><b>40%</b></td></tr>
        <tr><td>🧠 Brand Recall</td><td><b>10%</b></td></tr>
        <tr><td>⚙️ Functionality</td><td><b>10%</b></td></tr>
        <tr><td>🌿 Sustainability</td><td><b>10%</b></td></tr>
      </table>
    </div>""", unsafe_allow_html=True)
