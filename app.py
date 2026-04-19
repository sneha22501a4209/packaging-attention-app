import streamlit as st
import os, json, datetime, urllib.parse, time
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
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
* { font-family: 'Poppins', sans-serif; }
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
    color: white;
}
[data-testid="stHeader"] { background: transparent; }
.hero {
    text-align: center; padding: 40px 20px 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20px; margin-bottom: 30px;
    box-shadow: 0 20px 60px rgba(102,126,234,0.3);
}
.hero h1 { font-size:3rem;font-weight:700;color:white;margin:0; }
.hero p  { color:rgba(255,255,255,0.85);font-size:1.1rem;margin-top:10px; }
.card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px; padding: 24px; margin: 12px 0;
}
.strategy-badge {
    display:inline-block;padding:12px 28px;border-radius:50px;
    font-size:1.4rem;font-weight:700;margin:10px 0;
    box-shadow:0 8px 30px rgba(0,0,0,0.3);
}
.cs-number {
    font-size:3.5rem;font-weight:700;
    background:linear-gradient(135deg,#667eea,#764ba2);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1;
}
.score-label { color:rgba(255,255,255,0.7);font-size:0.85rem;margin-bottom:4px; }
.metric-box {
    background:rgba(255,255,255,0.05);border-radius:12px;padding:16px;
    text-align:center;border:1px solid rgba(255,255,255,0.1);
}
.winner-banner {
    text-align:center;padding:24px;border-radius:16px;
    font-size:1.8rem;font-weight:700;margin:20px 0;
}
.tip-card {
    background:rgba(102,126,234,0.15);border-left:4px solid #667eea;
    border-radius:8px;padding:14px 18px;margin:8px 0;color:white;
}
.recommend-card {
    background:linear-gradient(135deg,rgba(102,126,234,0.2),rgba(118,75,162,0.2));
    border:2px solid #667eea;border-radius:16px;padding:24px;margin:12px 0;
}
.gen-card {
    background:linear-gradient(135deg,rgba(255,65,108,0.15),rgba(255,75,43,0.15));
    border:2px solid #ff416c;border-radius:16px;padding:24px;margin:12px 0;
}
.elec-card {
    background:linear-gradient(135deg,rgba(56,239,125,0.15),rgba(17,153,142,0.15));
    border:2px solid #38ef7d;border-radius:16px;padding:24px;margin:12px 0;
}
.suggestion-card {
    background:rgba(255,255,255,0.05);border-left:4px solid #ff416c;
    border-radius:8px;padding:16px 20px;margin:10px 0;
}
div[data-testid="stTabs"] button {
    color:white !important;font-size:0.9rem !important;font-weight:600 !important;
}
.stButton button {
    background:linear-gradient(135deg,#667eea,#764ba2) !important;
    color:white !important;border:none !important;border-radius:50px !important;
    padding:12px 32px !important;font-weight:600 !important;
    box-shadow:0 4px 15px rgba(102,126,234,0.4) !important;
}
[data-testid="stFileUploader"] {
    background:rgba(255,255,255,0.03) !important;
    border:2px dashed rgba(102,126,234,0.5) !important;
    border-radius:16px !important;padding:20px !important;
}
.stSlider label { color:rgba(255,255,255,0.8) !important; }
.stSelectbox label { color:rgba(255,255,255,0.8) !important; }
.stTextInput label { color:rgba(255,255,255,0.8) !important; }
.stTextArea label  { color:rgba(255,255,255,0.8) !important; }
</style>
""", unsafe_allow_html=True)

MODEL_PATH = os.environ.get("MODEL_PATH", "./packaging_model.pth")

# ── LOAD PACKAGING MODEL ─────────────────────────────────────────────────────
@st.cache_resource(show_spinner="🧠 Loading Packaging AI Model...")
def load_predictor():
    from macros_engine import PackagingPredictor
    return PackagingPredictor(MODEL_PATH)

# ── LOAD ELECTRONICS MODEL ───────────────────────────────────────────────────
@st.cache_resource(show_spinner="🔬 Loading Electronics AI Model...")
def load_electronics_model():
    import torch
    import torch.nn as nn
    from transformers import BertModel
    from torchvision import models as tvm

    class MultimodalModel(nn.Module):
        def __init__(self, num_classes=3, dropout=0.3):
            super().__init__()
            self.bert = BertModel.from_pretrained("bert-base-uncased")
            self.img_enc = tvm.mobilenet_v2(weights=tvm.MobileNet_V2_Weights.DEFAULT)
            self.img_enc.classifier = nn.Identity()
            self.drop = nn.Dropout(dropout)
            self.fc = nn.Sequential(
                nn.Linear(768 + 1280, 512), nn.ReLU(), nn.Dropout(dropout),
                nn.Linear(512, 128), nn.ReLU(), nn.Dropout(dropout),
                nn.Linear(128, num_classes)
            )
        def forward(self, input_ids, attention_mask, images):
            txt = self.bert(input_ids=input_ids, attention_mask=attention_mask).pooler_output
            img = self.img_enc(images)
            return self.fc(self.drop(torch.cat([txt, img], dim=1)))

    device     = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    elec_path  = "./electronics_model.pth"

    if not os.path.exists(elec_path):
        try:
            import gdown
            gdown.download(
                "https://drive.google.com/uc?id=1E01Zg4-07XprlPgwp0nvBQaDeyVXHXZb",
                elec_path, quiet=False
            )
        except Exception as e:
            return None, device, str(e)

    try:
        model = MultimodalModel(num_classes=3).to(device)
        ckpt  = torch.load(elec_path, map_location=device)
        model.load_state_dict(ckpt["model_state_dict"], strict=False)
        model.eval()
        return model, device, "ok"
    except Exception as e:
        return None, device, str(e)

@st.cache_resource(show_spinner="📝 Loading BERT tokenizer...")
def load_elec_tokenizer():
    from transformers import BertTokenizer
    return BertTokenizer.from_pretrained("bert-base-uncased")

# ── CONSTANTS ────────────────────────────────────────────────────────────────
CRITERIA = ["visual_appeal","emotional_resonance","brand_recall","functionality","sustainability"]
LABELS = {
    "visual_appeal":"🎨 Visual Appeal","emotional_resonance":"❤️ Emotional Resonance",
    "brand_recall":"🧠 Brand Recall","functionality":"⚙️ Functionality","sustainability":"🌿 Sustainability",
}
STRATEGY_COLORS = {
    "Bold & Vibrant":("linear-gradient(135deg,#ff416c,#ff4b2b)","#ff416c"),
    "Eco-Friendly":  ("linear-gradient(135deg,#11998e,#38ef7d)","#11998e"),
    "Minimalist":    ("linear-gradient(135deg,#4776e6,#8e54e9)","#4776e6"),
    "Interactive":   ("linear-gradient(135deg,#f7971e,#ffd200)","#f7971e"),
}
GOALS = {
    "🎯 Maximum Customer Attraction":{"visual_appeal":0.4,"emotional_resonance":0.4,"brand_recall":0.1,"functionality":0.05,"sustainability":0.05},
    "🌿 Most Eco-Friendly":           {"visual_appeal":0.1,"emotional_resonance":0.1,"brand_recall":0.1,"functionality":0.1,"sustainability":0.6},
    "🧠 Strongest Brand Memory":      {"visual_appeal":0.2,"emotional_resonance":0.2,"brand_recall":0.5,"functionality":0.05,"sustainability":0.05},
    "⚖️ Best Overall Balance":        {"visual_appeal":0.2,"emotional_resonance":0.2,"brand_recall":0.2,"functionality":0.2,"sustainability":0.2},
    "🏪 Best Shelf Visibility":       {"visual_appeal":0.5,"emotional_resonance":0.3,"brand_recall":0.1,"functionality":0.05,"sustainability":0.05},
}
GOAL_DESC = {
    "🎯 Maximum Customer Attraction":"Prioritises designs that immediately grab attention and emotional connection.",
    "🌿 Most Eco-Friendly":"Best for brands targeting environmentally conscious consumers.",
    "🧠 Strongest Brand Memory":"Ideal when brand recognition and repeat purchase is the main goal.",
    "⚖️ Best Overall Balance":"Equal weight across all criteria — best all-rounder design.",
    "🏪 Best Shelf Visibility":"Maximises visual impact — best for standing out in crowded retail shelves.",
}
PRODUCT_SUGGESTIONS = {
    "biscuit":{"colours":"Warm golds, creamy whites, chocolate browns","typography":"Rounded playful font","layout":"Hero product shot centre-top, brand logo top-left","imagery":"Close-up biscuit texture, steam wisps","mood":"Warm, inviting, indulgent","tips":["Use a large appetite-appealing product photograph (40% front face)","Show the biscuit broken open to reveal texture","Use warm golden-amber as primary background","Add a circular flavour badge in top-right corner","Add subtle texture pattern in background for premium feel"]},
    "chocolate":{"colours":"Deep browns, gold foil accents, cream whites","typography":"Elegant serif — signals premium","layout":"Brand name left, product image right, gold border","imagery":"Melting chocolate drizzle, cocoa beans","mood":"Luxurious, premium","tips":["Use deep dark brown base — signals premium chocolate","Add gold foil-effect typography","Show melting chocolate or broken pieces","Use slim elegant border frame","Include cocoa percentage badge"]},
    "chips":{"colours":"Bold reds, yellows, bright oranges","typography":"Heavy bold condensed font","layout":"Flavour burst top-right, product pile centre","imagery":"Flying chips, flavour ingredients, action shots","mood":"Energetic, fun, bold","tips":["Use bright red or yellow — maximum shelf visibility","Show chips mid-air — communicates crunch","Add flavour burst graphic with white text","Heavy condensed typography fills top third","Include real ingredient photography"]},
    "cookies":{"colours":"Warm beige, soft browns, pastel accents","typography":"Friendly rounded sans-serif","layout":"Stack of cookies hero, handwritten brand name","imagery":"Stack with visible chips, warm background","mood":"Homely, warm, nostalgic","tips":["Show stack of 3-4 cookies with visible chips","Use kraft-paper texture background","Include heritage badge","Warm amber spotlight creates oven-fresh feel","Hand-lettered font adds authenticity"]},
    "snack":{"colours":"Orange, green, yellow","typography":"Bold modern sans-serif","layout":"Product hero left, nutrition highlights right","imagery":"Active lifestyle, fresh ingredients","mood":"Energetic, healthy, on-the-go","tips":["Use energetic orange or lime green","Highlight health claims with icon badges","Show product in active context","Clean bold font hierarchy","Include nutrition highlight panel on front"]},
}
ELEC_LABELS = {
    2:("🌟 Positive Attention","#38ef7d","Consumers respond very positively. Strong brand attention signal."),
    1:("😐 Neutral Attention", "#ffd200","Mixed consumer response. Product has potential but needs improvement."),
    0:("⚠️ Negative Attention","#ff416c","Consumers respond negatively. Significant improvement recommended."),
}
ELEC_ADVICE = {
    2:["Maintain current product quality — consumer response is strong.","Highlight top positive review quotes on your product listing page.","Consider expanding this product line — brand trust is established."],
    1:["Improve product description clarity — consumers feel uncertain.","Enhance packaging visuals — neutral response signals low excitement.","Address the most common neutral complaints in product Q&A section."],
    0:["Urgently review product quality — negative reviews reduce repeat purchases.","Read 1-star reviews and address the top 3 recurring complaints.","Consider a product redesign or rebranding before relaunch."],
}
CAT_TIPS = {
    "Headphones & Earbuds":"Sound quality and comfort dominate reviews. Noise cancellation is the top positive driver.",
    "Smartphones & Tablets":"Battery life and camera quality are top predictors of positive attention.",
    "Laptops & Computers":"Performance and build quality drive brand recall. Value for money matters most.",
    "Cameras & Photography":"Image quality and ease of use are top criteria. Accessories boost score.",
    "Smart Home Devices":"App integration and setup ease dominate consumer feedback.",
    "Gaming":"Performance and compatibility are critical. Community feedback matters.",
    "Cables & Accessories":"Durability is the top driver. Packaging quality builds trust.",
    "Wearables":"Comfort, battery, and health accuracy drive positive attention.",
    "Speakers":"Sound clarity and bass response dominate. Portability is valued.",
    "Other Electronics":"Reliability and value for money are the key decision drivers.",
}

# ── HELPERS ──────────────────────────────────────────────────────────────────
def score_bar(name, value):
    pct   = int(value*100)
    color = "#38ef7d" if value>=0.70 else "#ffd200" if value>=0.55 else "#ff416c"
    st.markdown(f"""
    <div style="margin:8px 0">
      <div style="display:flex;justify-content:space-between;color:rgba(255,255,255,0.7);font-size:0.85rem;margin-bottom:4px">
        <span>{LABELS[name]}</span><span style="color:{color};font-weight:700">{value:.2f}</span>
      </div>
      <div style="background:rgba(255,255,255,0.1);border-radius:50px;height:10px;overflow:hidden">
        <div style="width:{pct}%;background:{color};height:10px;border-radius:50px;box-shadow:0 0 10px {color}88"></div>
      </div>
    </div>""", unsafe_allow_html=True)

def compute_goal_score(scores, goal):
    return round(sum(GOALS[goal][c]*scores[c] for c in CRITERIA), 4)

def get_suggestions(product_name, style, colour_theme):
    matched = next((v for k,v in PRODUCT_SUGGESTIONS.items() if k in product_name.lower()), None)
    if not matched:
        matched = {"colours":f"Research competitor palettes for {product_name}","typography":"Bold clear font for brand name","layout":"Brand name top, product hero centre, key claims bottom","imagery":f"High-quality {product_name} photography","mood":"Professional, trustworthy","tips":[f"Research top 3 competitor {product_name} brands","Hero product photograph fills at least 35% of front face","Brand name readable from 3 metres away","Highlight #1 unique selling point prominently","Consistent visual language across all variants"]}
    result = dict(matched)
    result["style_colours"] = {"Bold & Vibrant":"High saturation reds, oranges, yellows","Eco-Friendly":"Earthy greens, kraft browns","Minimalist":"Clean whites, soft greys","Interactive":"Dynamic gradients, AR zones"}.get(style,"")
    result["colour_theme"]  = {"🔥 Warm":"Reds, oranges, golds","❄️ Cool":"Blues, teals, silvers","🌿 Earth":"Greens, browns, creams","🎨 Bold":"Vivid multicolour","🖤 Dark":"Black, charcoal, navy"}.get(colour_theme,"")
    return result

def gen_image_url(product_name, style, colour_theme, extra_notes):
    style_map = {
        "Bold & Vibrant": "vibrant colorful bold graphic design packaging",
        "Eco-Friendly":   "eco natural earthy minimal packaging design",
        "Minimalist":     "clean minimal elegant white packaging design",
        "Interactive":    "modern dynamic interactive futuristic packaging",
    }
    colour_map = {
        "🔥 Warm": "warm red orange gold tones",
        "❄️ Cool":  "cool blue teal silver tones",
        "🌿 Earth": "earthy green brown natural tones",
        "🎨 Bold":  "vivid multicolor bright tones",
        "🖤 Dark":  "dark black premium sophisticated tones",
    }
    style_text  = style_map.get(style, "professional packaging design")
    colour_text = colour_map.get(colour_theme, "appealing color palette")
    prompt = (
        f"professional product packaging design for {product_name}, "
        f"{style_text}, {colour_text}, "
        f"retail shelf packaging, high quality, modern graphic design, "
        f"{extra_notes or ''}, white background, studio lighting"
    )
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=512&height=512&nologo=true"
    return url, prompt

def predict_electronics(text, image, model, device, tokenizer):
    from torchvision import transforms as T
    import torch, numpy as np
    IMG_TF = T.Compose([T.Resize((224,224)),T.ToTensor(),T.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])])
    enc  = tokenizer(text, padding="max_length", truncation=True, max_length=128, return_tensors="pt")
    ids, mask = enc["input_ids"].to(device), enc["attention_mask"].to(device)
    if image is None: image = Image.new("RGB",(224,224),(200,200,200))
    img = IMG_TF(image.convert("RGB")).unsqueeze(0).to(device)
    with torch.no_grad():
        logits = model(ids, mask, img)
        probs  = torch.softmax(logits,dim=1).cpu().numpy()[0]
    return int(probs.argmax()), probs

# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
  <h1>📦 PackageAI</h1>
  <p>Packaging Attention Predictor · Deep Learning + MACROS · Electronics Brand AI</p>
</div>
""", unsafe_allow_html=True)

tab1,tab2,tab3,tab4,tab5,tab6 = st.tabs([
    "🔍 Analyze Design","⚖️ Compare Designs","🏆 Find Best Design",
    "🎨 Design Generator","🔬 Electronics AI","📊 About"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — ANALYZE DESIGN
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    uploaded = st.file_uploader("Drop your packaging image here",type=["jpg","jpeg","png","bmp","webp"],key="single")
    if uploaded:
        image = Image.open(uploaded).convert("RGB")
        predictor = load_predictor()
        col_img,col_res = st.columns([1,2],gap="large")
        with col_img:
            st.image(image,use_container_width=True,caption="Your Design")
        with col_res:
            with st.spinner("🤖 Analyzing..."):
                from macros_engine import full_report
                scores = predictor.predict(image)
                report = full_report(scores)
            cs = report["consensus_score"]
            sname = report["strategy"]["name"]
            grad,color = STRATEGY_COLORS.get(sname,("linear-gradient(135deg,#667eea,#764ba2)","#667eea"))
            st.markdown(f'<div style="text-align:center;margin:10px 0 20px"><div class="strategy-badge" style="background:{grad};color:white">{report["strategy"]["code"]} — {sname}</div><p style="color:rgba(255,255,255,0.6);font-size:0.9rem;margin-top:8px">{report["strategy"]["description"]}</p></div>',unsafe_allow_html=True)
            c1,c2,c3 = st.columns(3)
            c1.markdown(f'<div class="metric-box"><div class="score-label">Consensus Score</div><div class="cs-number">{cs:.3f}</div></div>',unsafe_allow_html=True)
            c2.markdown(f'<div class="metric-box"><div class="score-label">Strategy</div><div style="font-size:1.3rem;font-weight:700;color:{color};margin-top:4px">{sname}</div></div>',unsafe_allow_html=True)
            c3.markdown(f'<div class="metric-box"><div class="score-label">Weakest Area</div><div style="font-size:0.95rem;font-weight:600;color:#ff416c;margin-top:4px">{LABELS[report["weakest_criterion"]]}</div></div>',unsafe_allow_html=True)

        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown("<div class='card'>",unsafe_allow_html=True)
        st.markdown("### 📊 Criterion Scores")
        for c in CRITERIA: score_bar(c,scores[c])
        st.markdown("</div>",unsafe_allow_html=True)

        weakest = report["weakest_criterion"]
        wscore  = scores[weakest]
        tips_db = {
            "visual_appeal":[f"Visual Appeal is {wscore:.2f} — colours lack energy. Switch to warm bold palette.","Add a large hero product image (40% front face).","Use maximum 3 colours — too many reduces focus.",f"Expected: {wscore:.2f} → {min(wscore+0.25,0.95):.2f} after redesign."],
            "emotional_resonance":[f"Emotional Resonance is {wscore:.2f} — packaging feels cold.","Include a human element or lifestyle moment.","Add a short emotional tagline below product name.",f"Expected: {wscore:.2f} → {min(wscore+0.28,0.95):.2f} after changes."],
            "brand_recall":[f"Brand Recall is {wscore:.2f} — logo not memorable enough.","Position logo top-centre or top-left.","Use a unique shape consumers can instantly associate.",f"Expected: {wscore:.2f} → {min(wscore+0.22,0.95):.2f} after repositioning."],
            "functionality":[f"Functionality is {wscore:.2f} — text hard to read. Increase contrast.","Use clean sans-serif font at minimum 12pt.","Add clear icons for serving size, storage, best-before.",f"Expected: {wscore:.2f} → {min(wscore+0.20,0.95):.2f} after fix."],
            "sustainability":[f"Sustainability is {wscore:.2f} — no eco signals visible.","Add recycling symbol with '100% Recyclable' text.","Replace glossy cues with matte/natural texture.",f"Expected: {wscore:.2f} → {min(wscore+0.30,0.95):.2f} after eco redesign."],
        }
        st.markdown("<div class='card'>",unsafe_allow_html=True)
        st.markdown(f"### 💡 How to Improve {LABELS[weakest]}")
        for i,tip in enumerate(tips_db.get(weakest,report["improvement_tips"]),1):
            icon = "⚠️" if i==1 else "📈" if i==4 else "💡"
            st.markdown(f'<div class="tip-card"><strong>{icon} #{i}</strong> {tip}</div>',unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)

        st.markdown("<div class='card'>",unsafe_allow_html=True)
        st.markdown("### 🔮 What-If Simulator")
        adj  = {}
        cols = st.columns(5)
        for i,c in enumerate(CRITERIA):
            adj[c] = cols[i].slider(LABELS[c],0.0,1.0,float(scores[c]),0.01,key=f"s_{c}")
        from macros_engine import compute_cs, map_strategy
        new_cs = compute_cs(adj); new_st = map_strategy(new_cs); delta = new_cs-cs
        dcol = "#38ef7d" if delta>=0 else "#ff416c"; dsign = "+" if delta>=0 else ""
        st.markdown(f'<div style="background:rgba(102,126,234,0.15);border-radius:12px;padding:16px;margin-top:12px;text-align:center">New CS: <strong style="color:#667eea;font-size:1.4rem">{new_cs:.3f}</strong> &nbsp;|&nbsp; Change: <strong style="color:{dcol}">{dsign}{delta:.3f}</strong> &nbsp;|&nbsp; Strategy: <strong style="color:{dcol}">{new_st["name"]}</strong></div>',unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)
        st.download_button("⬇️ Download Full Report",data=json.dumps(report,indent=2),file_name=f"report_{uploaded.name}.json",mime="application/json")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — COMPARE TWO DESIGNS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### Upload Two Designs to Compare")
    c1,c2 = st.columns(2,gap="large")
    up_a  = c1.file_uploader("📦 Design A",type=["jpg","jpeg","png","bmp","webp"],key="A")
    up_b  = c2.file_uploader("📦 Design B",type=["jpg","jpeg","png","bmp","webp"],key="B")
    if up_a and up_b:
        img_a = Image.open(up_a).convert("RGB"); img_b = Image.open(up_b).convert("RGB")
        c1.image(img_a,use_container_width=True,caption="Design A"); c2.image(img_b,use_container_width=True,caption="Design B")
        predictor = load_predictor()
        with st.spinner("🤖 Comparing..."):
            from macros_engine import compare_designs
            sc_a = predictor.predict(img_a); sc_b = predictor.predict(img_b)
            comp = compare_designs(sc_a,sc_b)
        winner = comp["overall_winner"]
        wg,wc  = STRATEGY_COLORS.get(comp[f"strategy_{winner.lower()}"]["name"],("linear-gradient(135deg,#667eea,#764ba2)","#667eea"))
        st.markdown(f'<div class="winner-banner" style="background:{wg}">🏆 Design {winner} Wins!<div style="font-size:1rem;font-weight:400;margin-top:6px;opacity:0.9">CS_A = {comp["design_a_cs"]} &nbsp;vs&nbsp; CS_B = {comp["design_b_cs"]}</div></div>',unsafe_allow_html=True)
        ca,cb = st.columns(2,gap="large")
        ga,cola = STRATEGY_COLORS.get(comp["strategy_a"]["name"],("linear-gradient(135deg,#667eea,#764ba2)","#667eea"))
        gb,colb = STRATEGY_COLORS.get(comp["strategy_b"]["name"],("linear-gradient(135deg,#667eea,#764ba2)","#667eea"))
        ca.markdown(f'<div class="card" style="text-align:center"><div style="color:rgba(255,255,255,0.6)">Design A</div><div style="font-size:2.5rem;font-weight:700;color:{cola}">{comp["design_a_cs"]}</div><div style="color:{cola};font-weight:600">{comp["strategy_a"]["name"]}</div></div>',unsafe_allow_html=True)
        cb.markdown(f'<div class="card" style="text-align:center"><div style="color:rgba(255,255,255,0.6)">Design B</div><div style="font-size:2.5rem;font-weight:700;color:{colb}">{comp["design_b_cs"]}</div><div style="color:{colb};font-weight:600">{comp["strategy_b"]["name"]}</div></div>',unsafe_allow_html=True)
        st.markdown("<div class='card'>",unsafe_allow_html=True); st.markdown("### 📊 Criterion Breakdown")
        for c in CRITERIA:
            d = comp["per_criterion"][c]; better = d["better"]
            col1,col2,col3,col4,col5 = st.columns([2,2,2,2,1])
            col1.markdown(f"<span style='color:rgba(255,255,255,0.7)'>{LABELS[c]}</span>",unsafe_allow_html=True)
            ba = "🟢" if better=="A" else "🔴" if better=="B" else "🟡"
            bb = "🟢" if better=="B" else "🔴" if better=="A" else "🟡"
            col2.markdown(f"{ba} **{d['design_a']:.3f}**"); col3.markdown(f"{bb} **{d['design_b']:.3f}**")
            col4.markdown(f"Diff: **{d['diff_b_minus_a']:+.3f}**")
            col5.markdown(f"<span style='color:#38ef7d;font-weight:700'>{'A' if better=='A' else 'B' if better=='B' else '='}</span>",unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — FIND BEST DESIGN
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="card"><h3>🏆 Packaging Recommender Engine</h3><p style="color:rgba(255,255,255,0.7)">Upload up to 5 designs. Choose your goal. AI picks the best one.</p></div>',unsafe_allow_html=True)
    st.markdown("### 🎯 Step 1 — What is Your Goal?")
    goal = st.selectbox("Choose what matters most:",list(GOALS.keys()),key="goal_select")
    gg,gc = {"🎯 Maximum Customer Attraction":("linear-gradient(135deg,#ff416c,#ff4b2b)","#ff416c"),"🌿 Most Eco-Friendly":("linear-gradient(135deg,#11998e,#38ef7d)","#11998e"),"🧠 Strongest Brand Memory":("linear-gradient(135deg,#4776e6,#8e54e9)","#4776e6"),"⚖️ Best Overall Balance":("linear-gradient(135deg,#667eea,#764ba2)","#667eea"),"🏪 Best Shelf Visibility":("linear-gradient(135deg,#f7971e,#ffd200)","#f7971e")}.get(goal,("linear-gradient(135deg,#667eea,#764ba2)","#667eea"))
    st.markdown(f'<div style="background:{gg};border-radius:12px;padding:14px 20px;margin:8px 0"><strong style="color:white">{goal}</strong><br><span style="color:rgba(255,255,255,0.85);font-size:0.9rem">{GOAL_DESC[goal]}</span></div>',unsafe_allow_html=True)
    st.markdown("### 📦 Step 2 — Upload Your Designs (2 to 5)")
    cols_up = st.columns(5); up_designs = []
    for i,col in enumerate(cols_up):
        f = col.file_uploader(["Design A","Design B","Design C","Design D","Design E"][i],type=["jpg","jpeg","png","bmp","webp"],key=f"rec_{i}")
        if f: up_designs.append((["Design A","Design B","Design C","Design D","Design E"][i],f))
    if len(up_designs)>=2:
        if st.button("🚀 Find Best Design for My Goal"):
            predictor = load_predictor(); results = []
            with st.spinner("Analyzing all designs..."):
                for name,file in up_designs:
                    img = Image.open(file).convert("RGB"); scores = predictor.predict(img)
                    from macros_engine import compute_cs, map_strategy
                    cs = compute_cs(scores); strat = map_strategy(cs)
                    results.append({"name":name,"image":img,"scores":scores,"goal_score":compute_goal_score(scores,goal),"cs":cs,"strategy":strat})
            results.sort(key=lambda x:x["goal_score"],reverse=True); winner = results[0]
            wg,wc = STRATEGY_COLORS.get(winner["strategy"]["name"],("linear-gradient(135deg,#667eea,#764ba2)","#667eea"))
            st.markdown(f'<div class="winner-banner" style="background:{wg}">🏆 RECOMMENDED: {winner["name"]}<div style="font-size:1rem;font-weight:400;margin-top:8px;opacity:0.9">Best for: {goal} &nbsp;|&nbsp; Score: {winner["goal_score"]:.3f} &nbsp;|&nbsp; {winner["strategy"]["name"]}</div></div>',unsafe_allow_html=True)
            ri = ["🥇","🥈","🥉","4️⃣","5️⃣"]; ic = st.columns(len(results))
            for i,(col,r) in enumerate(zip(ic,results)):
                col.image(r["image"],use_container_width=True,caption=f"{ri[i]} {r['name']}")
                rg,rc = STRATEGY_COLORS.get(r["strategy"]["name"],("linear-gradient(135deg,#667eea,#764ba2)","#667eea"))
                col.markdown(f'<div style="text-align:center;margin-top:4px"><div style="font-size:1.5rem;font-weight:700;color:{rc}">{r["goal_score"]:.3f}</div><div style="color:rgba(255,255,255,0.6);font-size:0.8rem">Goal Score</div><div style="color:{rc};font-size:0.85rem;font-weight:600">{r["strategy"]["name"]}</div></div>',unsafe_allow_html=True)
            ws = winner["scores"]; bc = max(CRITERIA,key=lambda c:ws[c]); wkc = min(CRITERIA,key=lambda c:ws[c])
            st.markdown(f'<div class="recommend-card"><h4>💡 Why {winner["name"]} is Recommended</h4><div class="tip-card">✅ <strong>Strongest:</strong> {LABELS[bc]} ({ws[bc]:.2f})</div><div class="tip-card">✅ <strong>Strategy:</strong> {winner["strategy"]["name"]} — {winner["strategy"]["description"]}</div><div class="tip-card">⚠️ <strong>Improve:</strong> {LABELS[wkc]} ({ws[wkc]:.2f})</div></div>',unsafe_allow_html=True)
    elif len(up_designs)==1: st.info("⚠️ Upload at least 2 designs to compare")
    else: st.markdown('<div style="text-align:center;padding:40px;color:rgba(255,255,255,0.4)"><div style="font-size:3rem">📦</div><div>Upload 2–5 designs above to get started</div></div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — AI DESIGN GENERATOR
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="gen-card"><h3>🎨 AI Packaging Design Generator</h3><p style="color:rgba(255,255,255,0.8)">Tell us your product. Get specific design suggestions + AI generated sample image instantly.</p></div>',unsafe_allow_html=True)
    st.markdown("### 📝 Step 1 — Describe Your Product")
    ca,cb = st.columns(2,gap="large")
    with ca:
        pname = st.text_input("🏷️ Product Name",placeholder="e.g. Chocolate Biscuit, Kids Candy...",key="pname")
        taud  = st.selectbox("👥 Target Audience",["General","Kids (5-12)","Teenagers","Young Adults (18-30)","Adults (30-50)","Health Conscious","Premium Buyers"],key="taud")
        mseg  = st.selectbox("🏪 Market Segment",["Mass Market","Premium","Budget Friendly","Organic / Natural","Luxury","Kids / Family"],key="mseg")
    with cb:
        dstyle = st.selectbox("🎨 Design Style",["Bold & Vibrant","Eco-Friendly","Minimalist","Interactive"],key="dstyle")
        ctheme = st.selectbox("🎨 Colour Theme",["🔥 Warm","❄️ Cool","🌿 Earth","🎨 Bold","🖤 Dark"],key="ctheme")
        enotes = st.text_area("📋 Extra Requirements (optional)",placeholder="e.g. mascot, gluten-free badge...",height=100,key="enotes")
    if st.button("✨ Generate Design Suggestions + Sample Image"):
        if not pname: st.error("⚠️ Please enter a product name first!")
        else:
            sug = get_suggestions(pname,dstyle,ctheme)
            cs1,cs2 = st.columns([1,1],gap="large")
            with cs1:
                st.markdown(f'<div class="gen-card"><h4>🎯 Design Brief: {pname}</h4><p style="color:rgba(255,255,255,0.6);font-size:0.85rem">{dstyle} · {ctheme} · {taud} · {mseg}</p></div>',unsafe_allow_html=True)
                for title,key in [("🎨 Recommended Colours","colours"),("✍️ Typography","typography"),("📐 Layout Guide","layout")]:
                    st.markdown(f"<div class='card'><strong>{title}</strong><div class='suggestion-card'>{sug[key]}</div></div>",unsafe_allow_html=True)
                st.markdown("<div class='card'><strong>💡 5 Specific Design Tips</strong>",unsafe_allow_html=True)
                for i,tip in enumerate(sug["tips"],1): st.markdown(f'<div class="suggestion-card"><strong>#{i}</strong> {tip}</div>',unsafe_allow_html=True)
                st.markdown("</div>",unsafe_allow_html=True)
            with cs2:
                st.markdown("<div class='card'><strong>🖼️ AI Generated Sample Image</strong>",unsafe_allow_html=True)
                iurl,_ = gen_image_url(pname,dstyle,ctheme,enotes)
                with st.spinner("🎨 Generating... (10-20 seconds)"):
                    try:
                        resp = requests.get(iurl,timeout=30)
                        if resp.status_code==200:
                            gi = Image.open(BytesIO(resp.content))
                            st.image(gi,use_container_width=True,caption=f"AI: {pname}")
                            ib = BytesIO(); gi.save(ib,format="PNG")
                            st.download_button("⬇️ Download Image",data=ib.getvalue(),file_name=f"{pname.replace(' ','_')}_concept.png",mime="image/png")
                        else: st.warning("Image service timed out. Try again.")
                    except: st.warning("Image service busy. Try again in a moment.")
                st.markdown("</div>",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — ELECTRONICS AI
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("""
    <div class="elec-card">
      <h3>🔬 Electronics Brand Attention Predictor</h3>
      <p style="color:rgba(255,255,255,0.85)">
        Powered by a Multimodal BERT + MobileNetV2 model trained on the
        Amazon Electronics Reviews Dataset (6 GB).
        Predicts: 🌟 Positive / 😐 Neutral / ⚠️ Negative consumer brand attention.
      </p>
    </div>
    """, unsafe_allow_html=True)

    elec_model, elec_device, elec_status = load_electronics_model()
    elec_tok = load_elec_tokenizer()

    if elec_model is None:
        st.error(f"❌ Model load failed: {elec_status}")
        st.info("Make sure the Google Drive file is publicly shared.")
    else:
        st.success("✅ Electronics AI Model Ready!")
        ea,eb = st.columns([2,1],gap="large")
        with ea:
            st.markdown("### 📝 Step 1 — Enter Product Details")
            ep_name = st.text_input("🏷️ Product Name",placeholder="e.g. Sony WH-1000XM5 Noise Cancelling Headphones",key="ep_name")
            ep_rev  = st.text_area("💬 Product Review or Description",placeholder="e.g. Amazing sound quality, very comfortable for long hours. Noise cancellation is top-notch and battery lasts all day.",height=150,key="ep_rev")
            ep_cat  = st.selectbox("📦 Product Category",list(CAT_TIPS.keys()),key="ep_cat")
        with eb:
            st.markdown("### 🖼️ Step 2 — Product Image (Optional)")
            up_ei = st.file_uploader("Upload product image",type=["jpg","jpeg","png","webp"],key="up_ei")
            if up_ei:
                pil_ei = Image.open(up_ei).convert("RGB")
                st.image(pil_ei,use_container_width=True,caption="Uploaded image")
            else:
                pil_ei = None
                st.markdown('<div style="background:rgba(255,255,255,0.03);border:2px dashed rgba(56,239,125,0.3);border-radius:12px;padding:40px;text-align:center;color:rgba(255,255,255,0.4)"><div style="font-size:2.5rem">📷</div><div style="margin-top:8px;font-size:0.85rem">Image optional — text alone works fine</div></div>',unsafe_allow_html=True)

        st.markdown("<br>",unsafe_allow_html=True)
        if st.button("🔬 Predict Brand Attention",key="elec_btn"):
            if not ep_rev.strip():
                st.warning("⚠️ Please enter a product review or description.")
            else:
                with st.spinner("🤖 Analysing with Multimodal AI..."):
                    pred,probs = predict_electronics(f"{ep_name} {ep_rev}".strip(),pil_ei,elec_model,elec_device,elec_tok)
                label,color,desc = ELEC_LABELS[pred]
                st.markdown(f'<div style="background:linear-gradient(135deg,{color}33,{color}11);border:2px solid {color};border-radius:16px;padding:24px;text-align:center;margin:16px 0"><div style="font-size:2rem;font-weight:700;color:{color}">{label}</div><div style="color:rgba(255,255,255,0.7);margin-top:8px">{desc}</div></div>',unsafe_allow_html=True)

                st.markdown("<div class='card'>",unsafe_allow_html=True)
                st.markdown("#### 📊 Confidence Scores")
                for i,(cn,cc) in enumerate([("⚠️ Negative","#ff416c"),("😐 Neutral","#ffd200"),("🌟 Positive","#38ef7d")]):
                    pct = int(probs[i]*100)
                    st.markdown(f'<div style="margin:8px 0"><div style="display:flex;justify-content:space-between;color:rgba(255,255,255,0.7);font-size:0.85rem;margin-bottom:4px"><span>{cn}</span><span style="color:{cc};font-weight:700">{pct}%</span></div><div style="background:rgba(255,255,255,0.1);border-radius:50px;height:10px"><div style="width:{pct}%;background:{cc};height:10px;border-radius:50px;box-shadow:0 0 8px {cc}88"></div></div></div>',unsafe_allow_html=True)
                st.markdown("</div>",unsafe_allow_html=True)

                st.markdown("<div class='card'>",unsafe_allow_html=True)
                st.markdown("#### 💡 Recommendations")
                for i,tip in enumerate(ELEC_ADVICE[pred],1):
                    icon = "✅" if pred==2 else "💡" if pred==1 else "🚨"
                    st.markdown(f'<div class="tip-card"><strong>{icon} #{i}</strong> {tip}</div>',unsafe_allow_html=True)
                st.markdown("</div>",unsafe_allow_html=True)

                st.markdown("<div class='card'>",unsafe_allow_html=True)
                st.markdown(f"#### 🏷️ {ep_cat} Insight")
                st.markdown(f'<div class="suggestion-card">💡 {CAT_TIPS.get(ep_cat,"Focus on quality and reliability.")}</div>',unsafe_allow_html=True)
                st.markdown("</div>",unsafe_allow_html=True)

                st.download_button("⬇️ Download Analysis Report",
                    data=json.dumps({"product":ep_name,"category":ep_cat,"review":ep_rev,"prediction":label,"confidence":{"negative":round(float(probs[0]),4),"neutral":round(float(probs[1]),4),"positive":round(float(probs[2]),4)},"recommendations":ELEC_ADVICE[pred]},indent=2),)


# ══════════════════════════════════════════
# TAB 6 — ELECTRONICS RECOMMENDER
# ══════════════════════════════════════════
with tab6:

    st.markdown("""
    <div style="background:linear-gradient(135deg,rgba(56,239,125,0.15),rgba(17,153,142,0.15));
                border:2px solid #38ef7d;border-radius:16px;padding:24px;margin:12px 0">
      <h3 style="color:white;margin:0">🛒 Electronics Product Recommender</h3>
      <p style="color:rgba(255,255,255,0.85);margin-top:8px">
        Tell us what you want to buy. Our AI ranks products by
        Brand Attention Score — higher score means stronger
        positive consumer response.
      </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Load catalog ────────────────────────────────────────
    @st.cache_data
    def load_catalog():
        catalog_path = "./electronics_catalog.json"
        if os.path.exists(catalog_path):
            with open(catalog_path) as f:
                return json.load(f)
        return []

    # ── Load electronics model ──────────────────────────────
    @st.cache_resource(show_spinner="🔬 Loading Brand Attention AI...")
    def load_elec_model():
        import torch
        import torch.nn as nn
        from transformers import BertModel, BertTokenizer
        from torchvision import models as tvm

        class MultimodalModel(nn.Module):
            def __init__(self, num_classes=3, dropout=0.3):
                super().__init__()
                self.bert    = BertModel.from_pretrained("bert-base-uncased")
                self.img_enc = tvm.mobilenet_v2(
                    weights=tvm.MobileNet_V2_Weights.DEFAULT)
                self.img_enc.classifier = nn.Identity()
                self.drop = nn.Dropout(dropout)
                self.fc   = nn.Sequential(
                    nn.Linear(768+1280, 512), nn.ReLU(), nn.Dropout(dropout),
                    nn.Linear(512, 128),     nn.ReLU(), nn.Dropout(dropout),
                    nn.Linear(128, num_classes)
                )
            def forward(self, input_ids, attention_mask, images):
                txt = self.bert(
                    input_ids=input_ids,
                    attention_mask=attention_mask
                ).pooler_output
                img = self.img_enc(images)
                return self.fc(self.drop(torch.cat([txt,img],dim=1)))

        device    = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        elec_path = "./electronics_model.pth"

        if not os.path.exists(elec_path):
            import gdown
            gdown.download(
                "https://drive.google.com/uc?id=1E01Zg4-07XprlPgwp0nvBQaDeyVXHXZb",
                elec_path, quiet=False
            )

        model     = MultimodalModel(num_classes=3).to(device)
        ckpt      = torch.load(elec_path, map_location=device)
        model.load_state_dict(ckpt["model_state_dict"], strict=False)
        model.eval()

        tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
        return model, tokenizer, device

    def get_attention_score(text, model, tokenizer, device):
        """Returns positive attention probability (0-1)"""
        from torchvision import transforms as T
        import torch
        IMG_TF = T.Compose([
            T.Resize((224,224)), T.ToTensor(),
            T.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
        ])
        enc  = tokenizer(
            text, padding="max_length", truncation=True,
            max_length=128, return_tensors="pt"
        )
        ids  = enc["input_ids"].to(device)
        mask = enc["attention_mask"].to(device)
        img  = IMG_TF(Image.new("RGB",(224,224),(200,200,200))).unsqueeze(0).to(device)
        with torch.no_grad():
            logits = model(ids, mask, img)
            probs  = torch.softmax(logits, dim=1).cpu().numpy()[0]
        # Return positive class probability as brand attention score
        return float(probs[2]), float(probs[1]), float(probs[0])

    catalog = load_catalog()

    if not catalog:
        st.error("❌ electronics_catalog.json not found. Run Step 1 in Colab first.")
    else:
        # ── SEARCH BAR ──────────────────────────────────────
        st.markdown("### 🔍 What do you want to buy?")

        col_s, col_f = st.columns([3,1], gap="large")

        with col_s:
            query = st.text_input(
                "",
                placeholder="e.g. laptop, headphone, smartphone, tablet, camera, speaker, smartwatch...",
                key="elec_query",
                label_visibility="collapsed"
            )

        with col_f:
            top_n = st.selectbox(
                "Show top",
                [3, 5, 10],
                key="top_n"
            )

        if st.button("🚀 Find Best Products", key="find_btn"):

            if not query.strip():
                st.warning("⚠️ Please type what you want to buy.")
            else:
                # Filter products by query keyword
                q = query.lower().strip()

                # Category keyword mapping
                keyword_map = {
                    "laptop":      "laptop",
                    "computer":    "laptop",
                    "notebook":    "laptop",
                    "headphone":   "headphone",
                    "earphone":    "headphone",
                    "earbuds":     "headphone",
                    "headset":     "headphone",
                    "phone":       "smartphone",
                    "smartphone":  "smartphone",
                    "mobile":      "smartphone",
                    "iphone":      "smartphone",
                    "android":     "smartphone",
                    "watch":       "smartwatch",
                    "smartwatch":  "smartwatch",
                    "speaker":     "speaker",
                    "bluetooth":   "speaker",
                    "tablet":      "tablet",
                    "ipad":        "tablet",
                    "camera":      "camera",
                    "dslr":        "camera",
                    "mirrorless":  "camera",
                    "gopro":       "camera",
                }

                # Find matching category
                matched_cat = None
                for kw, cat in keyword_map.items():
                    if kw in q:
                        matched_cat = cat
                        break

                # Filter catalog
                if matched_cat:
                    filtered = [p for p in catalog if p["category"] == matched_cat]
                else:
                    # Search by name and brand too
                    filtered = [p for p in catalog
                                if q in p["name"].lower()
                                or q in p["brand"].lower()
                                or q in p["category"].lower()]

                if not filtered:
                    st.warning(f"No products found for '{query}'. Try: laptop, headphone, smartphone, tablet, camera, speaker, smartwatch")
                else:
                    # Load model and score each product
                    with st.spinner(f"🤖 Scoring {len(filtered)} products with Brand Attention AI..."):
                        try:
                            model, tokenizer, device = load_elec_model()
                            model_loaded = True
                        except Exception as e:
                            model_loaded = False
                            st.error(f"Model error: {e}")

                    if model_loaded:
                        scored = []
                        prog   = st.progress(0, text="Analysing products...")

                        for i, product in enumerate(filtered):
                            pos, neu, neg = get_attention_score(
                                product["review"], model, tokenizer, device
                            )
                            scored.append({
                                **product,
                                "positive": round(pos*100, 1),
                                "neutral":  round(neu*100, 1),
                                "negative": round(neg*100, 1),
                                "score":    round(pos*100, 1),
                            })
                            prog.progress((i+1)/len(filtered),
                                text=f"Analysed: {product['name']}")

                        prog.empty()

                        # Sort by positive attention score
                        scored.sort(key=lambda x: x["score"], reverse=True)
                        top_products = scored[:top_n]

                        # ── RESULTS HEADER ──────────────────
                        st.markdown(f"""
                        <div style="background:linear-gradient(135deg,rgba(56,239,125,0.2),rgba(17,153,142,0.1));
                                    border:1px solid #38ef7d;border-radius:12px;
                                    padding:16px;text-align:center;margin:16px 0">
                          <h4 style="color:#38ef7d;margin:0">
                            🏆 Top {len(top_products)} {query.title()} Recommendations
                          </h4>
                          <p style="color:rgba(255,255,255,0.6);margin:4px 0 0;font-size:0.9rem">
                            Ranked by Brand Attention Score from highest to lowest
                          </p>
                        </div>
                        """, unsafe_allow_html=True)

                        # ── PRODUCT CARDS ────────────────────
                        for rank, product in enumerate(top_products, 1):
                            score = product["score"]

                            # Colour based on score
                            if score >= 70:
                                badge_col = "#38ef7d"
                                badge_txt = "🌟 Highly Recommended"
                            elif score >= 50:
                                badge_col = "#ffd200"
                                badge_txt = "👍 Good Choice"
                            else:
                                badge_col = "#ff416c"
                                badge_txt = "⚠️ Mixed Reviews"

                            rank_icons = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
                            rank_icon  = rank_icons[rank-1] if rank <= 10 else f"#{rank}"

                            # Product card
                            with st.container():
                                st.markdown(f"""
                                <div style="background:rgba(255,255,255,0.04);
                                            border:1px solid rgba(255,255,255,0.1);
                                            border-left:5px solid {badge_col};
                                            border-radius:16px;padding:20px;margin:10px 0">
                                  <div style="display:flex;justify-content:space-between;align-items:center">
                                    <div>
                                      <span style="font-size:1.5rem">{rank_icon}</span>
                                      <strong style="font-size:1.2rem;color:white;margin-left:8px">
                                        {product["name"]}
                                      </strong>
                                      <span style="color:rgba(255,255,255,0.5);font-size:0.85rem;margin-left:8px">
                                        by {product["brand"]}
                                      </span>
                                    </div>
                                    <div style="text-align:right">
                                      <div style="font-size:2rem;font-weight:700;color:{badge_col}">
                                        {score:.0f}%
                                      </div>
                                      <div style="color:rgba(255,255,255,0.5);font-size:0.75rem">
                                        Brand Attention
                                      </div>
                                    </div>
                                  </div>
                                  <div style="margin-top:8px">
                                    <span style="background:{badge_col}33;color:{badge_col};
                                                 padding:4px 12px;border-radius:20px;font-size:0.8rem;
                                                 font-weight:600">
                                      {badge_txt}
                                    </span>
                                    <span style="color:rgba(255,255,255,0.5);font-size:0.85rem;margin-left:12px">
                                      💰 {product["price"]}
                                    </span>
                                  </div>
                                </div>
                                """, unsafe_allow_html=True)

                                # Score bars inside expander
                                with st.expander(f"📊 See detailed scores for {product['name']}"):
                                    col1, col2, col3 = st.columns(3)

                                    for col, label, val, color in [
                                        (col1, "🌟 Positive", product["positive"], "#38ef7d"),
                                        (col2, "😐 Neutral",  product["neutral"],  "#ffd200"),
                                        (col3, "⚠️ Negative", product["negative"], "#ff416c"),
                                    ]:
                                        col.markdown(f"""
                                        <div style="text-align:center;background:rgba(255,255,255,0.05);
                                                    border-radius:12px;padding:12px">
                                          <div style="color:{color};font-size:1.5rem;font-weight:700">
                                            {val:.1f}%
                                          </div>
                                          <div style="color:rgba(255,255,255,0.6);font-size:0.8rem">
                                            {label}
                                          </div>
                                        </div>
                                        """, unsafe_allow_html=True)

                                    st.markdown(f"""
                                    <div style="background:rgba(255,255,255,0.05);border-radius:8px;
                                                padding:12px;margin-top:8px;color:rgba(255,255,255,0.7);
                                                font-size:0.85rem;font-style:italic">
                                      💬 "{product['review'][:180]}..."
                                    </div>
                                    """, unsafe_allow_html=True)

                        # ── COMPARISON TABLE ──────────────────
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown("### 📋 Quick Comparison")
                        rows = []
                        for rank, p in enumerate(top_products, 1):
                            rows.append({
                                "Rank":            f"{rank_icons[rank-1]}",
                                "Product":         p["name"],
                                "Brand":           p["brand"],
                                "Price":           p["price"],
                                "Attention Score": f"{p['score']:.0f}%",
                                "Verdict":         "🌟 Buy" if p["score"]>=70 else "👍 Consider" if p["score"]>=50 else "⚠️ Skip",
                            })
                        st.dataframe(rows, use_container_width=True)

                        # ── DOWNLOAD ──────────────────────────
                        st.download_button(
                            "⬇️ Download Recommendations",
                            data=json.dumps(top_products, indent=2),
                            file_name=f"{query}_recommendations.json",
                            mime="application/json"
 
                        )
                        

