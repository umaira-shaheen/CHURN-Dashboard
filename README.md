# Subscription churn: plans & pricing

An interactive, presentation-ready **Streamlit data visualisation dashboard** for Humaira's individual contribution to a group assignment (CMP7227).

## What the dashboard answers

**Group question:** Who is more likely to cancel their subscription?

**Individual question:** How are subscription plan and monthly charges associated with cancellation?

It implements the exact two charts and interaction in `Humaira_Visualisation_Work_Plan.pdf`:

1. **Plan-level bar chart:** Basic, Standard and Premium cancellation percentages, with customer counts.
2. **Monthly-charge band line chart:** five ordered ranges and cancellation percentages, with point-level counts.
3. **Interactive plan selector:** see the charge-band pattern for one plan, or overlay all three plans to compare them.

Also includes four summary KPIs, dynamic takeaways, a method and limitations section, downloadable aggregated data, and a two-minute presentation script.

## Quick start

Python 3.10+ recommended. In a terminal, from the repository root:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

The local app opens in your browser (usually `http://localhost:8501`). The CSV is already included, so no manual upload or additional credentials are required. Before making the repository **public**, confirm you are allowed to republish this customer-level dataset; it includes individual customer identifiers. For a public-only-aggregates alternative, the remaining customer-level data would need to be replaced with summary counts and the loading code adapted.

## Deploy from GitHub to Streamlit Community Cloud

1. Create a new GitHub repository (for example `subscription-churn-dashboard`).
2. Upload **all files and directories** in this project (including `data/` and `.streamlit/`) to the repository's root.
3. Visit [share.streamlit.io](https://share.streamlit.io), sign in with GitHub, and choose **Create app**.
4. Select your repository and branch; set **Main file path** to `app.py`.
5. Select **Deploy**. The dashboard can then be shared using its `streamlit.app` link.

More details: [official Streamlit deployment instructions](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).

## Repository structure

```text
humaira_streamlit_dashboard/
├── app.py                      # Streamlit application & Plotly visualisations
├── analytics.py                # Reusable, testable calculations
├── data/
│   └── subscription_churn_full.csv
├── .streamlit/
│   └── config.toml             # Light theme + dashboard colours
├── tests/
│   └── test_analytics.py       # Calculations and data checks
├── requirements.txt
├── PRESENTATION_NOTES.md
├── .gitignore
└── README.md
```

## Analysis methodology

- The supplied data contains **243,787 records**. Customer IDs are unique in the supplied file.
- The deployable CSV is a **lossless projection of the four fields used by this page** (`CustomerID`, `SubscriptionType`, `MonthlyCharges`, `Churn`). Other original columns are intentionally left out to reduce the GitHub upload size; no customers or rows were removed.
- `Churn = 1` = cancelled, `Churn = 0` = retained.
- **Cancellation percentage** = `cancelled customers / customers in a selected group × 100`.
- Plan percentages use each plan's customer count as the denominator.
- Band percentages use each selected plan-and-band group's customer count as the denominator.
- Charge bands: `4.99–<8`, `8–<11`, `11–<14`, `14–<17`, `17–<20`.
- Monthly charge **currency is not given** in the dataset/work plan, so the dashboard never assumes £ or $.
- The line chart's x-axis is an **ordered categorical scale**, not a time series.
- These patterns describe **association, not causation**. Differences may reflect unmeasured factors.

## Data visualisation choices

- **Bars begin at zero**, so a small difference in plan rates is not visually exaggerated.
- **Consistent colours** identify Basic, Standard and Premium across both charts.
- **Direct percentage labels** help the audience read precise rates without relying on colour alone.
- **Hover details, sample sizes, and a summary table** make denominators transparent.
- **Ordered charge bands** preserve the intended rising charge sequence without implying calendar periods.
- **Focused interaction** supports a clear two-minute speaking contribution.

## Integrating into the group dashboard

Your colleagues can copy the functions in `analytics.py` and import `make_plan_chart()` / `make_band_chart()` from `app.py` with minor refactoring (to avoid executing the page upon import). The simpler approach is to retain this module as its own Streamlit page within a multipage group app. For example, place the page code in a `pages/` folder and keep `analytics.py` and `data/` accessible from the repository root. Update `DATA_PATH` if the directory structure changes.

## Testing

```bash
python -m pip install pytest
python -m pytest -q
```

The checked-in CSV is used only for visualisation; no model fitting, statistical significance, or causal identification is claimed.
