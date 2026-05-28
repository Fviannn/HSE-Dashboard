import plotly.graph_objects as go
import pandas as pd

from config import CHART_BG, FONT_MONO, FONT_MAIN, GRID_CLR, TEXT_SEC


def chart_trend(df: pd.DataFrame) -> go.Figure:
    """Trend kepatuhan 30 hari — area + line + target."""
    fig = go.Figure()

    # Area fill
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["compliance_rate"],
        mode="none", fill="tozeroy", fillcolor="rgba(0,212,255,0.06)",
        showlegend=False, hoverinfo="skip",
    ))

    # Main line
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["compliance_rate"],
        mode="lines+markers",
        line=dict(color="#00D4FF", width=2, shape="spline"),
        marker=dict(size=5, color="#00D4FF",
                    line=dict(color="#080B10", width=1.5)),
        hovertemplate="<b>%{x}</b><br>Kepatuhan: <b>%{y}%</b><extra></extra>",
        showlegend=False,
    ))

    # Highlight last data point
    if not df.empty:
        last = df.iloc[-1]
        fig.add_trace(go.Scatter(
            x=[last["date"]], y=[last["compliance_rate"]],
            mode="markers",
            marker=dict(size=10, color="#00D4FF",
                        line=dict(color="#080B10", width=2),
                        symbol="circle"),
            hovertemplate=(f"<b>HARI INI</b><br>"
                           f"Kepatuhan: <b>{last['compliance_rate']}%</b><br>"
                           f"Total: {last['total']} | Patuh: {last['compliant']}"
                           "<extra></extra>"),
            showlegend=False,
        ))

    # Target line
    fig.add_hline(
        y=85, line_dash="dot", line_color="rgba(245,166,35,0.5)", line_width=1,
        annotation_text="Target 85%",
        annotation_font=dict(color="#F5A623", size=10, family=FONT_MONO),
        annotation_position="right",
    )

    fig.update_layout(
        paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
        margin=dict(l=0, r=60, t=10, b=0), height=220,
        font=dict(family=FONT_MAIN, color=TEXT_SEC, size=11),
        xaxis=dict(showgrid=False, zeroline=False, tickangle=-30, nticks=10,
                   tickfont=dict(family=FONT_MONO, size=10, color=TEXT_SEC)),
        yaxis=dict(range=[50, 105], showgrid=True, gridcolor=GRID_CLR, zeroline=False,
                   ticksuffix="%", tickfont=dict(family=FONT_MONO, size=10, color=TEXT_SEC)),
        showlegend=False,
        hoverlabel=dict(bgcolor="#141A22", bordercolor="#00D4FF",
                        font=dict(family=FONT_MONO, size=11, color="#E8EDF2")),
    )
    return fig


def chart_apd_donut(summary: dict) -> go.Figure:
    """Donut chart jenis APD yang dilanggar."""
    values = [
        summary["missing_helmet_count"],
        summary["missing_vest_count"],
        summary["missing_mask_count"],
    ]
    total_apd = sum(values)

    fig = go.Figure(go.Pie(
        labels=["Tanpa Helm", "Tanpa Rompi", "Tanpa Masker"], values=values, hole=0.68,
        marker=dict(colors=["#FF3B3B", "#F5A623", "#00D4FF"],
                    line=dict(color="#080B10", width=3)),
        textinfo="none",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Jumlah: <b>%{value}</b><br>"
            "Porsi: <b>%{percent}</b>"
            "<extra></extra>"
        ),
    ))

    fig.add_annotation(text=f"<b>{total_apd}</b>",
                       font=dict(family=FONT_MONO, size=26, color="#E8EDF2"),
                       showarrow=False, x=0.5, y=0.55)
    fig.add_annotation(text="kasus",
                       font=dict(family=FONT_MAIN, size=11, color=TEXT_SEC),
                       showarrow=False, x=0.5, y=0.38)

    fig.update_layout(
        paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
        margin=dict(l=0, r=0, t=0, b=0), height=220, showlegend=True,
        legend=dict(font=dict(family=FONT_MAIN, size=12, color=TEXT_SEC),
                    orientation="v", x=1.05, y=0.5, bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor="#141A22", bordercolor="#FF3B3B",
                        font=dict(family=FONT_MONO, size=11, color="#E8EDF2")),
    )
    return fig


def chart_daily_violations(df: pd.DataFrame) -> go.Figure:
    """Bar chart pelanggaran 7 hari terakhir."""
    last7  = df.tail(7)
    colors = [
        "#FF3B3B" if r < 80 else "#F5A623" if r < 87 else "#3DCC7E"
        for r in last7["compliance_rate"]
    ]
    violations = last7["total"] - last7["compliant"]

    fig = go.Figure(go.Bar(
        x=last7["date"], y=violations,
        marker_color=colors, marker_line_width=0,
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Pelanggaran: <b>%{y}</b>"
            "<extra></extra>"
        ),
    ))

    fig.update_layout(
        paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
        margin=dict(l=0, r=0, t=10, b=0), height=170,
        font=dict(family=FONT_MAIN, color=TEXT_SEC, size=11),
        xaxis=dict(showgrid=False, zeroline=False,
                   tickfont=dict(family=FONT_MONO, size=9, color=TEXT_SEC)),
        yaxis=dict(showgrid=True, gridcolor=GRID_CLR, zeroline=False,
                   tickfont=dict(family=FONT_MONO, size=9, color=TEXT_SEC)),
        bargap=0.3,
        hoverlabel=dict(bgcolor="#141A22", bordercolor="#F5A623",
                        font=dict(family=FONT_MONO, size=11, color="#E8EDF2")),
    )
    return fig
