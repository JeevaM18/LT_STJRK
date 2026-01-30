import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px

BACKEND = "http://127.0.0.1:8000"

st.set_page_config(layout="wide")
st.title("⚡ Intelligent SLD Risk Analyzer – L&T Hackathon")

# ---------------- UPLOAD ----------------
uploaded = st.file_uploader(
    "Upload Single Line Diagram (SLD)",
    ["png", "jpg", "jpeg"]
)

if not uploaded:
    st.stop()

res = requests.post(f"{BACKEND}/upload/", files={"file": uploaded})
data = res.json()

# ============================================================
# 🔹 TOP: IMAGE + CONNECTIVITY GRAPH
# ============================================================
img_col, graph_col = st.columns([1.2, 1])

with img_col:
    st.subheader("🖼️ Uploaded SLD")
    st.image(uploaded, use_column_width=True)

with graph_col:
    st.subheader("🔗 Connectivity Graph")
    flow = " → ".join(
        [e["from"] for e in data["connectivity"]["edges"]] +
        [data["connectivity"]["edges"][-1]["to"]]
    )
    st.code(flow)
    st.json(data["symbols"], expanded=False)

# ============================================================
# 🔹 OBJECT CONTEXT PANEL
# ============================================================
st.markdown("---")
st.subheader("📌 Object Context & Explainability")

component_col, why_col = st.columns([1, 2])

components = data["symbols"]
selected = component_col.selectbox(
    "Select Component",
    [s["id"] for s in components]
)

obj = next(s for s in components if s["id"] == selected)

with component_col:
    st.markdown("### 🔧 Component Details")
    st.write(f"**ID:** {obj['id']}")
    st.write(f"**Type:** {obj['type']}")
    st.write(f"**Voltage:** {obj.get('voltage', '—')}")
    st.write(f"**Criticality:** {data['criticality'].get(obj['id'], '—')}")

    COMPONENT_MEANING = {
        "SOURCE": "Primary power input to the system",
        "FEEDER": "Distributes power to downstream network",
        "BREAKER": "Protects and isolates equipment during faults",
        "TRANSFORMER": "Steps voltage up or down",
        "LOAD": "Consumes electrical power"
    }

    st.info(COMPONENT_MEANING.get(obj["type"], "—"))

with why_col:
    st.markdown("### 🧠 WHY This Component Is Involved")

    explained = False
    for r in data["why_explainer"]:
        if selected in r["symbols"]:
            st.error(
                f"**{r['rule']}**\n\n"
                f"{r['why']}\n\n"
                f"**Severity:** {r['severity']}  \n"
                f"**Confidence:** {r['confidence']}%"
            )
            explained = True

    if not explained:
        st.success("This component is not involved in any detected risk")

#============================================================
# 🔹 RISK SUMMARY DASHBOARD (WITH WHY + CONFIDENCE)
# ============================================================
st.markdown("---")
st.subheader("📊 Risk Summary Dashboard")

if not data.get("risks"):
    st.success("No risks detected in this SLD")
else:
    dashboard_cols = st.columns(3)

    for i, r in enumerate(data["risks"]):
        with dashboard_cols[i % 3]:

            color = {
                "HIGH": "#7f1d1d",
                "MEDIUM": "#78350f",
                "LOW": "#14532d"
            }.get(r["severity"], "#1f2933")

            st.markdown(
                f"""
                <div style="
                    background:{color};
                    padding:16px;
                    border-radius:14px;
                    min-height:160px;
                    box-shadow:0 6px 16px rgba(0,0,0,0.4);
                ">
                    <div style="font-size:16px;font-weight:700;">
                        {r['severity']} ({r['confidence']}%) – {r['rule']}
                    </div>
                    <hr style="opacity:0.3"/>
                    <div style="font-size:14px;">
                        {r['why']}
                    </div>
                    <div style="margin-top:8px;font-size:12px;opacity:0.8;">
                        Affected: {", ".join(r["symbols"])}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

# ============================================================
# 🔹 OVERALL SLD RISK PIE CHART
# ============================================================
st.markdown("---")
st.subheader("📈 Overall SLD Risk Distribution")

severity_count = (
    pd.DataFrame(data["risks"])
    .groupby("severity")
    .size()
    .reset_index(name="count")
)

fig = px.pie(
    severity_count,
    names="severity",
    values="count",
    color="severity",
    color_discrete_map={
        "HIGH": "#ef4444",
        "MEDIUM": "#f59e0b",
        "LOW": "#22c55e"
    },
    hole=0.4
)

st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 🔹 GIS IMPACT ANALYSIS (AUTO DISPLAY)
# ============================================================
st.markdown("---")
st.subheader("🗺️ GIS Impact Analysis")

if not data["gis"]:
    st.info("No geographic impact detected")
else:
    affected_areas = [g["area"] for g in data["gis"].values()]
    st.markdown(
        f"**Affected Areas:** {', '.join(set(affected_areas))}"
    )

    m = folium.Map(
        location=[13.07, 80.25],
        zoom_start=13,
        tiles="CartoDB positron"
    )

    for feeder, geo in data["gis"].items():
        folium.Polygon(
            geo["polygon"],
            color="red",
            fill=True,
            fill_opacity=0.35,
            popup=f"{feeder} → {geo['area']}"
        ).add_to(m)

    st_folium(m, width=900, height=450)
