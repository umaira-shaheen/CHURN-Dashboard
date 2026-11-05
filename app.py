"""Subscription Plans & Pricing — presentation-ready Streamlit dashboard.

To run: streamlit run app.py
"""

from __future__ import annotations

from pathlib import Path
import html

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from analytics import (
    ALL_PLANS,
    BAND_LABELS,
    PLAN_ORDER,
    charge_band_summary,
    overall_summary,
    plan_summary,
    prepare_data,
)

st.set_page_config(
    page_title="Subscription Churn | Plans & Pricing",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DATA_PATH = Path(__file__).resolve().parent / "data" / "subscription_churn_full.csv"
COLORS = {
    "All plans": "#5464DE",
    "Basic": "#D76C48",
    "Standard": "#168D87",
    "Premium": "#8066C8",
}
INK = "#1B2841"
MUTED = "#63748B"
GRID = "#E9EEF5"

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
    html, body, [data-testid="stApp"] {font-family:'DM Sans',system-ui,sans-serif;}
    [data-testid="stAppViewContainer"] {background:#F6F8FC;}
    .block-container {max-width:1250px; padding-top:2rem; padding-bottom:4rem;}
    h1, h2, h3, h4 {font-family:'Manrope',system-ui,sans-serif; letter-spacing:-.035em;}
    h1 {font-size:2.15rem !important;}
    div[data-testid="stVerticalBlockBorderWrapper"] > div {border-color:#E6ECF4 !important;}
    .hero {background:linear-gradient(115deg,#1A2A47 0%,#283A6C 68%,#394C89 100%);
      border-radius:22px; padding:30px 34px 29px; color:white; box-shadow:0 14px 32px rgba(25,39,77,.11);}
    .hero-eyebrow {text-transform:uppercase;font-size:11px;font-weight:800;letter-spacing:.15em;color:#ACBDFB;margin-bottom:14px;}
    .hero h1 {color:white;font-size:36px !important; line-height:1.16; margin:0 0 10px; font-weight:800;}
    .hero p {color:#D7E0F8;font-size:15px; margin:0;max-width:760px;line-height:1.65;}
    .hero-strip {display:flex;gap:9px;flex-wrap:wrap;margin-top:21px;}
    .hero-pill {background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2);
      border-radius:999px;font-size:11px;letter-spacing:.03em;padding:6px 11px;color:#ECF0FF;}
    .section-kicker {font-size:11px;letter-spacing:.13em;text-transform:uppercase;color:#6170B6;font-weight:800;margin-bottom:2px;}
    .section-heading {color:#20304D;font-size:23px;font-weight:800;margin:0 0 6px;}
    .section-description {font-size:14px;color:#697A8F;line-height:1.65;margin-bottom:12px;}
    .metric-card {min-height:130px;background:white;border:1px solid #E7EDF5;border-radius:18px;
      padding:20px 20px 17px;box-shadow:0 4px 15px rgba(37,58,94,.035);}
    .metric-label {color:#6D7D92;font-size:12px;font-weight:700;letter-spacing:.01em;}
    .metric-value {color:#202F4A;font-family:'Manrope',sans-serif;font-weight:800;font-size:29px;letter-spacing:-.05em;margin:9px 0 2px;}
    .metric-note {color:#728196;font-size:11px;}
    .metric-highlight {background:#EEF2FF;border-color:#DEE5FF;}
    .metric-highlight .metric-value {color:#3E4FB8;}
    .insight-card {background:#F4F6FF;border:1px solid #E5EAFD;border-radius:16px;
      padding:19px 19px 18px; margin:4px 0 16px;}
    .insight-title {font-size:11px;letter-spacing:.11em;text-transform:uppercase;color:#5464BD;font-weight:800;margin:0 0 11px;}
    .insight-main {font-family:'Manrope',sans-serif;color:#23345C;font-weight:800;font-size:17px;line-height:1.35;margin-bottom:10px;}
    .insight-body {font-size:13px;line-height:1.65;color:#5F6F88;}
    .mini-stat {border-top:1px solid #DDE4F8;padding-top:12px;margin-top:15px;color:#5F6F88;font-size:12px;}
    .mini-stat strong {font-weight:800;color:#2E4165;}
    .method-note {font-size:12px;line-height:1.7;color:#77869A;}
    .footer {font-size:12px;color:#718197;text-align:center;padding-top:17px;}
    [data-testid="stRadio"] p {font-size:12px;font-weight:700;color:#5B6E8C;}
    [data-testid="stHorizontalBlock"] {align-items:stretch;}
    @media (max-width:700px) {
      .hero {padding:24px 22px;border-radius:18px;}
      .hero h1 {font-size:28px !important;}
      .metric-card {min-height:116px;}
      .block-container {padding-top:1.1rem;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def metric_card(label: str, value: str, note: str, highlight: bool = False) -> None:
    highlight_class = " metric-highlight" if highlight else ""
    st.markdown(
        f'<div class="metric-card{highlight_class}">'
        f'<div class="metric-label">{html.escape(label)}</div>'
        f'<div class="metric-value">{html.escape(value)}</div>'
        f'<div class="metric-note">{html.escape(note)}</div></div>',
        unsafe_allow_html=True,
    )


def section_header(number: str, heading: str, description: str) -> None:
    st.markdown(
        f'<div class="section-kicker">{html.escape(number)}</div>'
        f'<div class="section-heading">{html.escape(heading)}</div>'
        f'<div class="section-description">{html.escape(description)}</div>',
        unsafe_allow_html=True,
    )


def insight_card(heading: str, main: str, body: str, tail: str = "") -> None:
    tail_html = f'<div class="mini-stat">{tail}</div>' if tail else ""
    st.markdown(
        f'<div class="insight-card"><div class="insight-title">{html.escape(heading)}</div>'
        f'<div class="insight-main">{html.escape(main)}</div>'
        f'<div class="insight-body">{html.escape(body)}</div>{tail_html}</div>',
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def load_data(path: str) -> pd.DataFrame:
    return prepare_data(pd.read_csv(path))


def base_layout(height: int = 375) -> dict:
    return dict(
        template="plotly_white",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, Arial, sans-serif", size=12, color=INK),
        margin=dict(l=52, r=18, t=37, b=56),
        showlegend=False,
        hoverlabel=dict(bgcolor="#20304D", font_color="white", font_size=12),
    )


def make_plan_chart(summary: pd.DataFrame) -> go.Figure:
    source = summary[summary["customers"] > 0]
    colors = [COLORS[name] for name in source["SubscriptionType"]]
    fig = go.Figure()
    fig.add_bar(
        x=source["SubscriptionType"],
        y=source["cancellation_pct"],
        marker=dict(color=colors, line=dict(color="rgba(0,0,0,0)", width=0)),
        width=0.51,
        text=[f"{x:.2f}%" for x in source["cancellation_pct"]],
        textposition="outside",
        textfont=dict(size=17, color=INK, family="Manrope, sans-serif"),
        customdata=source[["customers", "cancelled"]].to_numpy(),
        hovertemplate=(
            "<b>%{x}</b><br>Cancellation rate: <b>%{y:.2f}%</b>"
            "<br>Customers: %{customdata[0]:,}"
            "<br>Cancelled: %{customdata[1]:,}<extra></extra>"
        ),
    )
    ymax = max(25.0, float(source["cancellation_pct"].max()) * 1.23)
    fig.update_layout(**base_layout(340), bargap=0.40)
    fig.update_yaxes(
        title_text="Cancellation rate (%)",
        range=[0, ymax],
        ticksuffix="%",
        showgrid=True,
        gridcolor=GRID,
        zeroline=False,
        tickfont=dict(color=MUTED, size=11),
        title_font=dict(color=MUTED, size=12),
        dtick=5,
    )
    fig.update_xaxes(
        title_text=None,
        tickfont=dict(color=INK, size=13),
        showgrid=False,
        linecolor="#DFE6EF",
    )
    return fig


def make_band_chart(
    frame: pd.DataFrame,
    selected_plan: str,
    overlay_plans: bool,
) -> go.Figure:
    fig = go.Figure()
    overlays = list(PLAN_ORDER) if overlay_plans else [selected_plan]

    for plan in overlays:
        source = charge_band_summary(frame, plan)
        is_primary = (plan == selected_plan or not overlay_plans)
        name = "All customers" if plan == ALL_PLANS else plan
        color = COLORS[plan]
        point_text = (
            [f"{value:.1f}%" if pd.notna(value) else "" for value in source["cancellation_pct"]]
            if not overlay_plans else None
        )
        fig.add_trace(go.Scatter(
            x=list(BAND_LABELS),
            y=source["cancellation_pct"],
            mode="lines+markers+text" if point_text is not None else "lines+markers",
            name=name,
            line=dict(color=color, width=3.5 if is_primary else 2.5, shape="linear"),
            marker=dict(size=11 if is_primary else 9, color=color, line=dict(color="white", width=2)),
            text=point_text,
            textposition="top center",
            textfont=dict(size=12, color=color, family="Manrope, sans-serif"),
            customdata=source[["customers", "cancelled"]].to_numpy(),
            hovertemplate=(
                f"<b>{html.escape(name)}</b><br>Charge band: %{{x}}"
                "<br>Cancellation rate: <b>%{y:.2f}%</b>"
                "<br>Customers: %{customdata[0]:,}"
                "<br>Cancelled: %{customdata[1]:,}<extra></extra>"
            ),
            connectgaps=False,
        ))

    fig.update_layout(**base_layout(366))
    fig.update_layout(
        margin=dict(l=52, r=25, t=45, b=73),
        showlegend=overlay_plans,
        legend=dict(orientation="h", yanchor="bottom", y=1.10, x=0.0, xanchor="left", font=dict(size=11)),
        hovermode="x unified" if overlay_plans else "closest",
    )
    fig.update_yaxes(
        title_text="Cancellation rate (%)",
        range=[0, 34],
        ticksuffix="%",
        dtick=5,
        gridcolor=GRID,
        zeroline=False,
        tickfont=dict(color=MUTED, size=11),
        title_font=dict(color=MUTED, size=12),
    )
    # Labels are deliberately ordinal; this is NOT a chronological time-series chart.
    fig.update_xaxes(
        title_text="Monthly-charge bands (currency not provided)",
        categoryorder="array",
        categoryarray=list(BAND_LABELS),
        tickfont=dict(color=INK, size=11),
        title_font=dict(color=MUTED, size=12),
        showgrid=False,
        linecolor="#DFE6EF",
    )
    return fig


try:
    df = load_data(str(DATA_PATH))
except (OSError, ValueError, pd.errors.ParserError) as exc:
    st.error(f"Could not load the dashboard data: {exc}")
    st.stop()

stats = overall_summary(df)
plans = plan_summary(df)
nonempty_plans = plans.loc[plans["customers"] > 0]
highest = nonempty_plans.sort_values("cancellation_pct", ascending=False).iloc[0]
lowest = nonempty_plans.sort_values("cancellation_pct", ascending=True).iloc[0]
plan_gap = float(highest["cancellation_pct"] - lowest["cancellation_pct"])

st.markdown(
    '<div class="hero">'
    '<div class="hero-eyebrow">Customer retention / Group analysis / Individual contribution</div>'
    '<h1>Subscription plans &amp; pricing</h1>'
    '<p>How are subscription plan and monthly charges associated with cancellation? '
    'Explore the differences between Basic, Standard and Premium — then filter the charge-band trend.</p>'
    '<div class="hero-strip"><span class="hero-pill">243K+ customer records</span>'
    '<span class="hero-pill">2 required visualisations</span>'
    '<span class="hero-pill">Interactive plan comparison</span>'
    '<span class="hero-pill">CMP7227 · Humaira</span></div></div>',
    unsafe_allow_html=True,
)
st.write("")
st.markdown('<div class="section-kicker">The big picture</div>', unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4, gap="small")
with k1:
    metric_card("Customers analysed", f'{stats["customers"]:,}', "Unique CustomerID values")
with k2:
    metric_card("Cancelled subscriptions", f'{stats["cancelled"]:,}', "Churn = 1")
with k3:
    metric_card("Overall cancellation rate", f'{stats["cancellation_pct"]:.2f}%', "Cancelled / all customers", True)
with k4:
    metric_card("Highest-cancellation plan", str(highest["SubscriptionType"]), f'{highest["cancellation_pct"]:.2f}% cancelled')

st.write("")
st.write("")
section_header(
    "01 / PLAN COMPARISON",
    "Which plan has the highest cancellation percentage?",
    "A common zero baseline makes the three plan rates directly comparable. Customer totals appear below and on hover.",
)
plan_chart_col, plan_insight_col = st.columns([3.05, 1.15], gap="large")
with plan_chart_col:
    with st.container(border=True):
        st.plotly_chart(make_plan_chart(plans), width="stretch", theme=None, config={"displaylogo": False, "responsive": True})
        counts_str = "  ·  ".join(
            f'{r.SubscriptionType}: {int(r.customers):,} customers'
            for r in plans.itertuples()
        )
        st.caption(f"Sample size — {counts_str}")
with plan_insight_col:
    insight_card(
        "Key takeaway",
        f'{highest["SubscriptionType"]} has the highest cancellation rate.',
        f'{float(highest["cancellation_pct"]):.2f}% of {highest["SubscriptionType"]} customers cancelled, versus '
        f'{float(lowest["cancellation_pct"]):.2f}% for {lowest["SubscriptionType"]}.',
        f'<strong>{plan_gap:.2f} percentage-point gap</strong> between the highest and lowest plans.',
    )
    st.markdown(
        '<div class="method-note">Each bar shows a percentage of customers within that plan, '
        'not the number of cancelled customers. Hover for both the numerator and denominator.</div>',
        unsafe_allow_html=True,
    )

st.write("")
st.write("")
section_header(
    "02 / CHARGE-BAND PATTERN",
    "How does cancellation vary with monthly charges?",
    "Five ordered charge ranges show cancellation percentage, not elapsed time. Select a plan to test whether the pattern changes.",
)
controls_left, controls_right = st.columns([3.1, 1], gap="large")
with controls_left:
    selected = st.radio(
        "Show charge-band rates for",
        options=[ALL_PLANS, *PLAN_ORDER],
        horizontal=True,
        index=0,
        help="The line updates to show cancellation within the selected subscription plan.",
    )
with controls_right:
    compare = st.checkbox("Compare all three plans", value=False, help="Overlay separate lines for Basic, Standard and Premium.")

band_chart_col, band_insight_col = st.columns([3.05, 1.15], gap="large")
source = charge_band_summary(df, selected)
nonempty = source.loc[source["customers"] > 0]
first_rate = float(nonempty.iloc[0]["cancellation_pct"])
last_rate = float(nonempty.iloc[-1]["cancellation_pct"])
diff_rate = last_rate - first_rate
with band_chart_col:
    with st.container(border=True):
        st.plotly_chart(
            make_band_chart(df, selected, compare),
            width="stretch",
            theme=None,
            config={"displaylogo": False, "responsive": True},
        )
        band_counts = "  ·  ".join(
            f'{row.ChargeBand}: n={int(row.customers):,}' for row in source.itertuples()
        )
        st.caption("Read left to right as increasing monthly-charge ranges, **not time**. "
                   "Hover for cancellations and customer totals.")
        st.caption(f"Selected group by band — {band_counts}")
with band_insight_col:
    subject = "All customers" if selected == ALL_PLANS else f"{selected} customers"
    direction = "higher" if diff_rate > 0 else "lower" if diff_rate < 0 else "unchanged"
    insight_card(
        "What the selection shows",
        f"{subject}: {abs(diff_rate):.2f} pp {direction} in the highest band.",
        f"Lowest band: {first_rate:.2f}% cancelled. Highest band: {last_rate:.2f}% cancelled. "
        "This comparison is descriptive, not causal.",
        f'<strong>{int(nonempty["customers"].sum()):,} customers</strong> in the selected group.',
    )
    st.markdown(
        '<div class="method-note">Changing the plan recalculates each percentage '
        'using customers <em>within that plan and charge band</em> as the denominator.</div>',
        unsafe_allow_html=True,
    )

st.write("")
with st.expander("Explore the exact numbers — customer counts and cancellation rates"):
    st.markdown("**Subscription plan summary**")
    plan_table = plans.rename(columns={
        "SubscriptionType": "Plan", "customers": "Customers", "cancelled": "Cancelled",
        "cancellation_pct": "Cancellation rate (%)",
    })
    st.dataframe(
        plan_table.style.format({"Customers": "{:,.0f}", "Cancelled": "{:,.0f}", "Cancellation rate (%)": "{:.2f}%"}),
        hide_index=True, width="stretch",
    )
    st.markdown(f"**Monthly-charge bands — {selected}**")
    band_table = source.rename(columns={
        "ChargeBand": "Monthly-charge band", "customers": "Customers", "cancelled": "Cancelled",
        "cancellation_pct": "Cancellation rate (%)",
    })
    st.dataframe(
        band_table.style.format({"Customers": "{:,.0f}", "Cancelled": "{:,.0f}", "Cancellation rate (%)": "{:.2f}%"}),
        hide_index=True, width="stretch",
    )
    st.download_button(
        "Download selected charge-band summary (CSV)",
        data=band_table.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"charge_band_summary_{selected.lower().replace(' ', '_')}.csv",
        mime="text/csv",
    )

st.write("")
st.divider()
footer_left, footer_right = st.columns([1.4, 1], gap="large")
with footer_left:
    st.markdown("### How to interpret these charts")
    st.markdown(
        "**One finding:** Basic has the highest observed plan cancellation percentage, and the rate rises across "
        "monthly-charge bands in the full sample.\n\n"
        "**One limitation:** These are observational associations. Other factors may influence cancellation, "
        "and the data does not establish that prices or plan choice *cause* cancellations.\n\n"
        "**Why these charts work:** Bars compare three categories from zero; an ordered line makes the "
        "charge-band pattern easy to follow. Labels, counts and interactive filtering support fair comparisons."
    )
with footer_right:
    st.markdown("### Calculation & data notes")
    st.markdown(
        "**Cancellation (%)** = cancelled customers ÷ customers in the relevant group × 100.  "
        "`Churn = 1` denotes cancellation.\n\n"
        "**Bands:** 4.99–<8; 8–<11; 11–<14; 14–<17; 17–<20. "
        "Ranges are ordered categories, not dates.\n\n"
        "**Currency:** Not specified in the supplied CSV or work plan; no £ or $ symbol is assumed. "
        "**Dataset:** `subscription_churn_full.csv`."
    )

with st.expander("Presentation support · suggested 2-minute talking track"):
    st.markdown(
        "**0:00–0:20 — Question:** ‘Our shared goal is to identify who is more likely to cancel. "
        "My contribution examines subscription plan and monthly charges.’\n\n"
        "**0:20–0:55 — First visual:** ‘I used a bar chart because it compares three distinct plans "
        "on the same percentage scale. Basic has the highest rate at 19.65%, Premium the lowest at 16.28%, "
        "and Standard is in between at 18.43%.’\n\n"
        "**0:55–1:30 — Second visual:** ‘I grouped monthly charges into five increasing bands. "
        "Across all customers, the percentage rises from 13.00% to 23.80%. "
        "I can select a plan and see whether this association is similar within it.’\n\n"
        "**1:30–1:50 — Interpretation:** ‘The charts communicate differences clearly using "
        "a zero baseline, ordered bands, exact percentages and customer counts.’\n\n"
        "**1:50–2:00 — Limitation:** ‘These are associations, not evidence of causation. "
        "The charge currency also needs confirming.’"
    )

st.markdown(
    '<div class="footer">CMP7227 · Data Visualisation · Individual contribution: Humaira '
    '· Subscription plans and pricing</div>',
    unsafe_allow_html=True,
)
