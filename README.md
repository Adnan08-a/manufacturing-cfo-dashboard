# Manufacturing CFO Cockpit

A production-ready, multi-page **Streamlit** CFO dashboard for a manufacturing
company: executive KPIs, revenue & profitability analysis, operational
metrics, statistical forecasting, scenario planning, variance bridges, and
AI-generated insights -- all on a gradient-blue "command center" theme.

![pages](https://img.shields.io/badge/pages-8-blue) ![python](https://img.shields.io/badge/python-3.10%2B-blue) ![streamlit](https://img.shields.io/badge/streamlit-1.36%2B-FF4B4B)

---

## 1. What's inside

| Page | What it shows |
|---|---|
| 🏠 Home | Orientation, quick KPI snapshot, methodology notes |
| 📊 Executive Summary | Headline KPIs, P&L waterfall, auto-generated commentary, top/bottom performers |
| 💵 Revenue Analysis | Trend, region/product mix, heatmap, revenue driver tree (treemap), growth rates |
| 📈 Profitability Analysis | Gross/EBITDA/Net margin trends, cost-structure waterfall, profitability heatmap |
| ⚙️ Operational KPIs | On-time delivery, quality, inventory turns, downtime, labor productivity, correlations |
| 🔮 Forecasting | Holt-Winters / linear-trend revenue & EBITDA forecasts with adjustable horizon |
| 🎯 Scenario Planning | Price/volume/cost/opex sliders, EBITDA bridge, sensitivity tornado chart |
| 📋 Variance Analysis | Actual vs. prior-period or YoY bridges, variance heatmap and detail table |
| 🧠 AI Insights | Rule-based insight cards (no API key needed) + optional live Claude Q&A |

### KPIs tracked
Revenue · Gross Profit · EBITDA · Net Margin · Inventory Turns · Working Capital
(see **Methodology** below for exact formulas).

### Tech stack
Streamlit · Plotly · Pandas · NumPy · statsmodels · (optional) Anthropic SDK.

---

## 2. Project structure

```
cfo-dashboard/
├── app.py                          # Home page (entry point)
├── pages/
│   ├── 1_📊_Executive_Summary.py
│   ├── 2_💵_Revenue_Analysis.py
│   ├── 3_📈_Profitability_Analysis.py
│   ├── 4_⚙️_Operational_KPIs.py
│   ├── 5_🔮_Forecasting.py
│   ├── 6_🎯_Scenario_Planning.py
│   ├── 7_📋_Variance_Analysis.py
│   └── 8_🧠_AI_Insights.py
├── utils/
│   ├── data_loader.py               # load / clean / filter the dataset
│   ├── kpis.py                      # KPI calculations
│   ├── formatting.py                # currency / number / % formatting
│   ├── styling.py                   # theme CSS, Plotly template, KPI cards
│   ├── charts.py                    # reusable Plotly chart builders
│   ├── forecasting.py               # Holt-Winters / linear forecasting
│   ├── insights.py                  # rule-based + optional Claude-powered insights
│   └── app_state.py                 # shared sidebar (data source + filters)
├── data/
│   └── manufacturing_company_dataset.xlsx   # bundled sample dataset
├── .streamlit/
│   ├── config.toml                  # theme + server config
│   └── secrets.toml.example         # template -- copy to secrets.toml locally
├── requirements.txt
├── .gitignore
└── README.md
```

Every page calls `utils.app_state.render_sidebar_and_load()` first, which
renders the dataset uploader and the Date / Region / Product filters and
keeps them in sync across pages via `st.session_state`.

---

## 3. Run it locally

```bash
# 1. Clone your repo (after you've pushed it -- see Section 4)
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

# 2. Create a virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) enable live AI Q&A on the "AI Insights" page
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# then edit .streamlit/secrets.toml and paste your real ANTHROPIC_API_KEY

# 5. Run the app
streamlit run app.py
```

The app opens at `http://localhost:8501`. The bundled sample dataset loads
automatically -- no upload required. To use your own data instead, expand
**📁 Data source** in the sidebar and upload an `.xlsx`/`.csv` with the same
column schema (see the README "Methodology" section, or the in-app caption
under the uploader).

---

## 4. Push to GitHub

```bash
cd cfo-dashboard
git init
git add .
git commit -m "Initial commit: Manufacturing CFO Cockpit dashboard"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

> `.streamlit/secrets.toml` is already excluded via `.gitignore` -- never
> commit real API keys. Only `secrets.toml.example` (with a placeholder) is
> tracked.

---

## 5. Deploy to Streamlit Community Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)** and sign in with GitHub.
2. Click **"New app"**.
3. Pick your repository, the `main` branch, and set the **main file path** to:
   ```
   app.py
   ```
4. (Optional, for live AI Q&A) Click **"Advanced settings" → "Secrets"** and paste:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-your-real-key"
   ```
   Without this, the dashboard still works fully -- the rule-based insight
   cards on the AI Insights page need no key, and end users can also paste
   their own key into the in-app session field.
5. Click **"Deploy"**. The first build installs `requirements.txt` and
   typically takes 1-3 minutes.
6. Your dashboard will be live at:
   ```
   https://<your-app-name>.streamlit.app
   ```

### Updating after deployment
Streamlit Cloud auto-redeploys on every push to the connected branch:
```bash
git add .
git commit -m "Update dashboard"
git push
```

### Using your own data permanently
Replace `data/manufacturing_company_dataset.xlsx` with your own file of the
same schema, commit, and push -- it becomes the new default dataset for
every visitor (no per-session upload needed).

---

## 6. KPI methodology

This dashboard derives a few standard FP&A metrics from the raw dataset.
Since the sample dataset doesn't ship with a full chart of accounts, the
following conventions are applied **consistently across every page**:

| Metric | Formula |
|---|---|
| Gross Profit | `Revenue − Cost` (Cost = COGS) |
| Gross Margin % | `Gross Profit ÷ Revenue` |
| EBITDA | `Gross Profit − Manufacturing Cost` (treated as operating expense) |
| EBITDA Margin % | `EBITDA ÷ Revenue` |
| Net Profit | the dataset's reported `Profit` column, used as-is |
| Net Margin % | `Net Profit ÷ Revenue` |
| Inventory Turns (annualized) | `(Total COGS ÷ Average Inventory Level) × (365 ÷ days in period)` |
| Working Capital | approximated by **average Inventory Levels** -- the dataset has no receivables/payables, so treat this as an inventory-investment proxy, not a full working-capital figure |

Because the bundled dataset is synthetic, these derived metrics may not
reconcile perfectly with one another in absolute terms -- the formulas are
applied consistently so that period-over-period and segment-over-segment
**comparisons** stay meaningful even where exact reconciliation isn't
guaranteed. Swap in your own dataset with real accounting data and these
same formulas will produce fully reconciling figures.

### Expected data schema
| Column | Type |
|---|---|
| Date | date |
| Region | text |
| Product | text |
| Revenue | number |
| Cost | number |
| Profit | number |
| Units Sold | number |
| Customer Satisfaction | number (1-5) |
| Manufacturing Cost | number |
| Labor Hours | number |
| Machine Downtime (hours) | number |
| Inventory Levels | number |
| Order Lead Time (days) | number |
| Return Rate (%) | number |
| On-Time Delivery (%) | number |

---

## 7. Customizing

- **Theme/colors**: edit the `COLORS` dict and CSS in `utils/styling.py`
  (and `.streamlit/config.toml` for the base Streamlit theme).
- **Add a KPI**: extend `compute_kpis()` in `utils/kpis.py`, then reference
  the new key in any page's `kpi_grid([...])` call.
- **Add a chart type**: add a builder function to `utils/charts.py` that
  returns a `go.Figure`; the active Plotly template (registered in
  `styling.py`) will style it automatically.
- **Add a page**: drop a new `N_<emoji>_Page_Name.py` file into `pages/`,
  starting with `configure_page(...)` and `render_sidebar_and_load()`.

---

## 8. Notes on the "AI" features

- **Insight cards** (AI Insights page) are fully rule-based -- trend
  detection, outlier flags, and correlation analysis computed locally with
  pandas/NumPy. They work with **zero configuration and no API key**.
- **Free-form Q&A** on the same page calls the Anthropic API
  (`claude-sonnet-4-6`) with a compact text summary of the *filtered* KPIs
  only -- never the raw row-level dataset. This feature is optional and
  degrades gracefully (with a clear in-app message) when no API key is set.
