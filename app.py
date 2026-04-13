
import streamlit as st
import os, json, datetime
from PIL import Image

st.set_page_config(
    page_title="PackageAI",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── BEAUTIFUL CSS ──
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

.hero h1 {
    font-size: 3rem;
    font-weight: 700;
    color: white;
    margin: 0;
    text-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

.hero p {
    color: rgba(255,255,255,0.85);
    font-size: 1.1rem;
    margin-top: 10px;
}

.card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 24px;
    margin: 12px 0;
    backdrop-filter: blur(10px);
}

.strategy-badge {
    display: inline-block;
    padding: 12px 28px;
    border-radius: 50px;
    font-size: 1.4rem;
    font-weight: 700;
    margin: 10px 0;
    box-shadow: 0 8px 30px rgba(0,0,0,0.3);
}

.score-label {
    color: rgba(255,255,255,0.7);
    font-size: 0.85rem;
    margin-bottom: 4px;
}

.cs-number {
    font-size: 3.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
}

.winner-banner {
    text-align: center;
    padding: 24px;
    border-radius: 16px;
    font-size: 1.8rem;
    font-weight: 700;
    margin: 20px 0;
}

.tip-card {
    background: rgba(102,126,234,0.15);
    border-left: 4px solid #667eea;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 8px 0;
    color: white;
}

.metric-box {
    background: rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.1);
}

.tab-content { padding: 20px 0; }

div[data-testid="stTabs"] button {
    color: white !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
}

.stButton button {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 12px 32px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    transition: all 0.3s !important;
    box-shadow: 0 4px 15px rgba(102,126,234,0.4) !important;
}

.stButton button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(102,126,234,0.6) !important;
}

[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.03) !important;
    border: 2px dashed rgba(102,126,234,0.5) !important;
    border-radius: 16px !important;
    padding: 20px !important;
}

.stSlider label { color: rgba(255,255,255,0.8) !important; }

section[data-testid="stSidebar"] {
    background: #1a1a2e !important;
}

.dataframe {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)

MODEL_PATH = os.environ.get("MODEL_PATH", "./packaging_model.pth")

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
    "Bold & Vibrant": ("linear-gradient(135deg,#ff416c,#ff4b2b)",
                       "#ff416c"),
    "Eco-Friendly":   ("linear-gradient(135deg,#11998e,#38ef7d)",
                       "#11998e"),
    "Minimalist":     ("linear-gradient(135deg,#4776e6,#8e54e9)",
                       "#4776e6"),
    "Interactive":    ("linear-gradient(135deg,#f7971e,#ffd200)",
                       "#f7971e"),
}

WEIGHTS = dict(zip(CRITERIA,[0.3,0.4,0.1,0.1,0.1]))

def score_bar(name, value):
    pct = int(value * 100)
    if value >= 0.70:   color = "#38ef7d"
    elif value >= 0.55: color = "#ffd200"
    else:               color = "#ff416c"

    st.markdown(f"""
    <div style="margin:8px 0">
      <div style="display:flex;justify-content:space-between;
                  color:rgba(255,255,255,0.7);font-size:0.85rem;
                  margin-bottom:4px">
        <span>{LABELS[name]}</span>
        <span style="color:{color};font-weight:700">{value:.2f}</span>
      </div>
      <div style="background:rgba(255,255,255,0.1);border-radius:50px;
                  height:10px;overflow:hidden">
        <div style="width:{pct}%;background:{color};height:10px;
                    border-radius:50px;
                    box-shadow:0 0 10px {color}88;
                    transition:width 0.5s ease"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── HERO HEADER ──
st.markdown("""
<div class="hero">
  <h1>📦 PackageAI</h1>
  <p>Real-Time Packaging Attention Predictor · Deep Learning + MACROS Ranking</p>
</div>
""", unsafe_allow_html=True)

# ── TABS ──
tab1, tab2, tab3 = st.tabs([
    "🔍  Analyze Design",
    "⚖️  Compare Designs",
    "📊  About"
])

# ════════════════════════════════════════
# TAB 1 — SINGLE ANALYSIS
# ════════════════════════════════════════
with tab1:
    st.markdown("<div class='tab-content'>", unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Drop your packaging image here",
        type=["jpg","jpeg","png","bmp","webp"],
        key="single"
    )

    if uploaded:
        image = Image.open(uploaded).convert("RGB")
        predictor = load_predictor()

        col_img, col_res = st.columns([1,2], gap="large")

        with col_img:
            st.image(image, use_container_width=True,
                     caption="Your Design")

        with col_res:
            with st.spinner("🤖 Analyzing your design..."):
                from macros_engine import full_report
                scores = predictor.predict(image)
                report = full_report(scores)

            cs       = report["consensus_score"]
            strategy = report["strategy"]
            sname    = strategy["name"]
            grad, color = STRATEGY_COLORS.get(
                sname, ("linear-gradient(135deg,#667eea,#764ba2)","#667eea"))

            # Strategy Badge
            st.markdown(f"""
            <div style="text-align:center;margin:10px 0 20px">
              <div class="strategy-badge"
                   style="background:{grad};color:white">
                {strategy["code"]} — {sname}
              </div>
              <p style="color:rgba(255,255,255,0.6);
                        font-size:0.9rem;margin-top:8px">
                {strategy["description"]}
              </p>
            </div>
            """, unsafe_allow_html=True)

            # CS Score
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

        # Score Bars
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 📊 Criterion Scores")
        for c in CRITERIA:
            score_bar(c, scores[c])
        st.markdown("</div>", unsafe_allow_html=True)

        # Tips
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"### 💡 How to Improve "
                    f"{LABELS[report['weakest_criterion']]}")
        for i,tip in enumerate(report["improvement_tips"],1):
            st.markdown(f"""
            <div class="tip-card">
              <strong>#{i}</strong> {tip}
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # What-If
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 🔮 What-If Simulator")
        st.caption("Drag sliders to simulate improvements")

        adj = {}
        cols = st.columns(5)
        for i,c in enumerate(CRITERIA):
            adj[c] = cols[i].slider(
                LABELS[c], 0.0, 1.0,
                float(scores[c]), 0.01, key=f"s_{c}"
            )

        from macros_engine import compute_cs, map_strategy
        new_cs  = compute_cs(adj)
        new_st  = map_strategy(new_cs)
        delta   = new_cs - cs
        dcolor  = "#38ef7d" if delta >= 0 else "#ff416c"
        dsign   = "+" if delta >= 0 else ""

        st.markdown(f"""
        <div style="background:rgba(102,126,234,0.15);
                    border-radius:12px;padding:16px;
                    margin-top:12px;text-align:center">
          <span style="font-size:1.1rem">
            New CS: <strong style="color:#667eea;
                             font-size:1.4rem">{new_cs:.3f}</strong>
            &nbsp;|&nbsp;
            Change: <strong style="color:{dcolor}">
              {dsign}{delta:.3f}</strong>
            &nbsp;|&nbsp;
            Strategy: <strong style="color:{dcolor}">
              {new_st["name"]}</strong>
          </span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Download
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            "⬇️ Download Full Report",
            data=json.dumps(report, indent=2),
            file_name=f"report_{uploaded.name}.json",
            mime="application/json"
        )

    st.markdown("</div>", unsafe_allow_html=True)

# ════════════════════════════════════════
# TAB 2 — COMPARE TWO DESIGNS
# ════════════════════════════════════════
with tab2:
    st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
    st.markdown("### Upload Two Designs to Compare")

    c1, c2 = st.columns(2, gap="large")
    up_a = c1.file_uploader("📦 Design A",
                             type=["jpg","jpeg","png","bmp","webp"],
                             key="A")
    up_b = c2.file_uploader("📦 Design B",
                             type=["jpg","jpeg","png","bmp","webp"],
                             key="B")

    if up_a and up_b:
        img_a = Image.open(up_a).convert("RGB")
        img_b = Image.open(up_b).convert("RGB")
        c1.image(img_a, use_container_width=True, caption="Design A")
        c2.image(img_b, use_container_width=True, caption="Design B")

        predictor = load_predictor()
        with st.spinner("🤖 Comparing designs..."):
            from macros_engine import compare_designs, full_report
            sc_a  = predictor.predict(img_a)
            sc_b  = predictor.predict(img_b)
            comp  = compare_designs(sc_a, sc_b)

        winner = comp["overall_winner"]
        w_grad, w_color = STRATEGY_COLORS.get(
            comp[f"strategy_{winner.lower()}"]["name"],
            ("linear-gradient(135deg,#667eea,#764ba2)","#667eea"))

        # Winner Banner
        st.markdown(f"""
        <div class="winner-banner" style="background:{w_grad}">
          🏆 Design {winner} Wins!
          <div style="font-size:1rem;font-weight:400;margin-top:6px;
                      opacity:0.9">
            CS<sub>A</sub> = {comp["design_a_cs"]}
            &nbsp;vs&nbsp;
            CS<sub>B</sub> = {comp["design_b_cs"]}
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Side by side CS
        ca, cb = st.columns(2, gap="large")
        ga,cola = STRATEGY_COLORS.get(
            comp["strategy_a"]["name"],
            ("linear-gradient(135deg,#667eea,#764ba2)","#667eea"))
        gb,colb = STRATEGY_COLORS.get(
            comp["strategy_b"]["name"],
            ("linear-gradient(135deg,#667eea,#764ba2)","#667eea"))

        ca.markdown(f"""
        <div class="card" style="text-align:center">
          <div style="font-size:1.1rem;color:rgba(255,255,255,0.6)">
            Design A</div>
          <div style="font-size:2.5rem;font-weight:700;
                      color:{cola}">{comp["design_a_cs"]}</div>
          <div style="color:{cola};font-weight:600">
            {comp["strategy_a"]["name"]}</div>
        </div>""", unsafe_allow_html=True)

        cb.markdown(f"""
        <div class="card" style="text-align:center">
          <div style="font-size:1.1rem;color:rgba(255,255,255,0.6)">
            Design B</div>
          <div style="font-size:2.5rem;font-weight:700;
                      color:{colb}">{comp["design_b_cs"]}</div>
          <div style="color:{colb};font-weight:600">
            {comp["strategy_b"]["name"]}</div>
        </div>""", unsafe_allow_html=True)

        # Criterion breakdown
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 📊 Criterion Breakdown")

        for c in CRITERIA:
            d    = comp["per_criterion"][c]
            better = d["better"]
            va   = d["design_a"]
            vb   = d["design_b"]
            col1,col2,col3,col4,col5 = st.columns([2,2,2,2,1])
            col1.markdown(f"<span style='color:rgba(255,255,255,0.7)'>"
                          f"{LABELS[c]}</span>",
                          unsafe_allow_html=True)
            bar_a = "🟢" if better=="A" else "🔴" if better=="B" else "🟡"
            bar_b = "🟢" if better=="B" else "🔴" if better=="A" else "🟡"
            col2.markdown(f"{bar_a} **{va:.3f}**")
            col3.markdown(f"{bar_b} **{vb:.3f}**")
            col4.markdown(f"Diff: **{d['diff_b_minus_a']:+.3f}**")
            col5.markdown(
                f"<span style='color:#38ef7d;font-weight:700'>"
                f"{'A' if better=='A' else 'B' if better=='B' else '='}"
                f"</span>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ════════════════════════════════════════
# TAB 3 — ABOUT
# ════════════════════════════════════════
with tab3:
    st.markdown("""
    <div class="card">
      <h3>🎯 About This System</h3>
      <p style="color:rgba(255,255,255,0.7)">
        Real-Time Packaging Attention Prediction System using
        Deep Learning and MACROS Ranking. Based on IEEE Access 2025.
      </p>
    </div>
    """, unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    c1.markdown("""
    <div class="metric-box">
      <div style="font-size:2rem">🧠</div>
      <div style="font-weight:700;margin:8px 0">MobileNetV2</div>
      <div style="color:rgba(255,255,255,0.6);font-size:0.85rem">
        Deep Learning Model</div>
    </div>""", unsafe_allow_html=True)
    c2.markdown("""
    <div class="metric-box">
      <div style="font-size:2rem">📊</div>
      <div style="font-weight:700;margin:8px 0">MACROS</div>
      <div style="color:rgba(255,255,255,0.6);font-size:0.85rem">
        Multi-Criteria Ranking</div>
    </div>""", unsafe_allow_html=True)
    c3.markdown("""
    <div class="metric-box">
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
    </div>
    """, unsafe_allow_html=True)
