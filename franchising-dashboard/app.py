"""Streamlit interface for the thesis's three franchising performance models."""
from dataclasses import asdict
from io import StringIO
import csv
import json

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from model import (MODEL_NAMES, PRESETS, SWEEP_VALUES, Parameters,
                   coefficients, performance, summarise, with_parameter)

st.set_page_config(page_title="Franchising sensitivity explorer", page_icon="📈", layout="wide")
COLORS = ["#1D6B67", "#BE673E", "#506CB1", "#9A7D20", "#774A88", "#547768"]
LABELS = {
    "pi": "Potential profit (π)", "c_op": "Constant operating cost (Cₒₚ)",
    "H": "Base overhead per company outlet (H)", "v": "Support cost coefficient (v)",
    "N": "Outlet scale (N)", "a": "Franchisee effort (a)",
    "theta": "Effort effectiveness (θ)", "delta": "Duplication cost (δ)",
    "vN": "Combined support burden (vN)",
}


def apply_preset():
    name = st.session_state["preset"]
    model, p = PRESETS[name]
    st.session_state["model"] = model
    for key, value in asdict(p).items():
        st.session_state[key] = float(value)
    st.session_state["baseline_params"] = asdict(p)
    st.session_state["baseline_name"] = name
    st.session_state["selected_share"] = 50


def reset_inputs():
    apply_preset()


def save_baseline():
    st.session_state["baseline_params"] = {k: st.session_state[k] for k in asdict(Parameters())}
    st.session_state["baseline_name"] = "Your saved comparison"


def compare_regimes():
    vN = st.session_state["v"] * st.session_state["N"]
    st.session_state["sweep_parameter_duplication"] = "delta"
    st.session_state["sweep_values_delta"] = ", ".join(f"{x:.12g}" for x in [0.0, vN, 2*vN])


def share_text(summary, which="maximum"):
    if summary.all_shares_tied:
        return "Any share"
    points = summary.maximisers if which == "maximum" else summary.minimisers
    return " or ".join(f"{x:.1%}" for x in points)


def new_figure(title):
    fig = go.Figure()
    fig.update_layout(
        title=dict(text=title, font=dict(size=19)),
        template="plotly_white", height=465,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial, sans-serif", size=13, color="#22322F"),
        margin=dict(l=35, r=20, t=65, b=85),
        xaxis=dict(title="Franchising intensity F", range=[0, 1], tickformat=".0%", dtick=0.2),
        yaxis=dict(title="Performance · normalised units", zerolinecolor="#CDD5D0"),
        legend=dict(orientation="h", y=-0.23, x=0), hovermode="x unified",
    )
    return fig


def add_curve(fig, f, model, p, label, color, dash="solid", show_maximum=True):
    fig.add_trace(go.Scatter(x=f, y=performance(f, model, p), mode="lines", name=label,
                            line=dict(color=color, width=3, dash=dash),
                            hovertemplate="F=%{x:.1%}<br>P=%{y:.4f}<extra>%{fullData.name}</extra>"))
    summary = summarise(model, p)
    if show_maximum and not summary.all_shares_tied:
        xs = summary.maximisers
        fig.add_trace(go.Scatter(x=xs, y=performance(xs, model, p), mode="markers",
                                name=f"{label} · maximum", showlegend=False,
                                marker=dict(color=color, size=11, line=dict(color="white", width=2)),
                                hovertemplate="Maximum at F=%{x:.2%}<br>P=%{y:.4f}<extra></extra>"))
    return summary


def csv_bytes(rows):
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


if "preset" not in st.session_state:
    st.session_state["preset"] = next(iter(PRESETS))
    apply_preset()

with st.sidebar:
    st.title("Model controls")
    st.selectbox("Start from an example", list(PRESETS), key="preset", on_change=apply_preset)
    st.selectbox("Performance model", list(MODEL_NAMES), format_func=MODEL_NAMES.get, key="model")
    st.caption("Examples use illustrative values. Adjust one input to see its effect.")
    st.button("Reset example", on_click=reset_inputs, use_container_width=True)
    st.subheader("Profit and effort")
    st.slider(LABELS["pi"], 0.0, 2.0, step=0.01, key="pi", help="First-best profit in the same normalised units as costs.")
    st.slider(LABELS["a"], 0.0, 1.0, step=0.01, key="a", help="An assumed effort level, held fixed along each F curve.")
    st.slider(LABELS["theta"], 0.1, 10.0, step=0.1, key="theta", help="In p(a)=1−exp(−θa), a higher θ makes a given effort more effective.")
    st.subheader("Operating structure")
    model = st.session_state["model"]
    st.slider(LABELS["c_op"], 0.0, 2.0, step=0.01, key="c_op", disabled=model != "baseline",
              help="Used only by the constant-overhead model.")
    st.slider(LABELS["H"], 0.0, 2.0, step=0.01, key="H", disabled=model == "baseline",
              help="Normalised overhead per company outlet; not a total headquarters budget.")
    st.slider(LABELS["v"], 0.0, 1.0, step=0.01, key="v", disabled=model == "baseline")
    st.slider(LABELS["N"], 0.1, 10.0, step=0.1, key="N", disabled=model == "baseline",
              help="Normalised outlet scale. Fractional values follow the appendix's N comparisons; this is not a literal outlet count.")
    st.slider(LABELS["delta"], 0.0, 1.0, step=0.01, key="delta", disabled=model != "duplication",
              help="Used only by the third model. The loss δF(1−F) peaks at 50% and vanishes at either endpoint.")
    st.caption("Grey controls are inactive in the selected model.")
    st.button("Save inputs as comparison", on_click=save_baseline, use_container_width=True)
    st.caption("The saved comparison stays fixed while you adjust the controls. Changing the model evaluates both sets of inputs in that model.")

p = Parameters(**{k: st.session_state[k] for k in asdict(Parameters())})
baseline = Parameters(**st.session_state["baseline_params"])
f = np.linspace(0.0, 1.0, 501)
summary = summarise(model, p)

st.caption("MSc Business Economics thesis · Tahtia Sazwara · University of Amsterdam")
st.title("Franchising sensitivity explorer")
st.markdown("How does the share of franchised outlets change performance? Explore the trade-off between operating costs, franchisee effort and the cost of maintaining two organisational structures.")
st.caption("A theoretical model explorer using normalised units. The controls change model assumptions; the app does not fit regressions or forecast a particular firm.")
explore, sensitivity, notes = st.tabs(["Explore the model", "Compare parameter values", "Equations and assumptions"])

with explore:
    st.subheader(MODEL_NAMES[model])
    st.write(summary.shape)
    m1, m2, m3 = st.columns(3)
    m1.metric("Best-performing franchised share", share_text(summary))
    m2.metric("Maximum performance", f"{summary.maximum:.4f}")
    m3.metric("Franchisee success probability", f"{p.probability:.1%}")
    fig = new_figure("Performance as franchising intensity changes")
    add_curve(fig, f, model, baseline, "Saved comparison", "#8D9691", dash="dash", show_maximum=False)
    add_curve(fig, f, model, p, "Current inputs", COLORS[0])
    st.plotly_chart(fig, use_container_width=True, key="main_chart")
    st.caption("Dots mark global maxima. The dashed curve uses your saved inputs. Hover over a curve to inspect a value.")
    st.slider("Inspect a franchised share (%)", 0, 100, step=1, key="selected_share")
    selected_f = st.session_state["selected_share"] / 100
    selected_y = float(performance(selected_f, model, p))
    comparison_y = float(performance(selected_f, model, baseline))
    left, middle, right = st.columns(3)
    left.metric(f"Performance at {selected_f:.0%} franchised", f"{selected_y:.4f}", delta=f"{selected_y-comparison_y:+.4f} vs saved inputs")
    middle.metric("Fully company-run · F = 0", f"{float(performance(0, model, p)):.4f}")
    right.metric("Fully franchised · F = 1", f"{p.franchise_payoff:.4f}")
    if summary.stationary_kind == "minimum":
        st.write(f"The lowest performance occurs at {summary.stationary_share:.1%} franchised. This turning point is a minimum; the highest performance is at an endpoint.")
    elif summary.stationary_kind == "maximum":
        st.write(f"The model favours a mixed structure: performance peaks at {summary.stationary_share:.1%} franchised.")
    elif summary.all_shares_tied:
        st.write("Every share delivers the same performance under these assumptions.")
    else:
        st.write(f"Within the feasible interval, performance is highest at {share_text(summary)} franchised.")
    st.caption(f"Effort cost c(a) = {p.effort_cost:.4f}; franchise payoff p(a)π − c(a) = {p.franchise_payoff:.4f}; combined support burden vN = {p.vN:.4f}.")
    if p.franchise_payoff < 0:
        st.info("These inputs give a negative franchise payoff. This is a mathematical scenario; a non-negative entry fee cannot extract negative surplus when the outside option is zero.")
    if st.checkbox("Also show the other two models", key="show_other_models"):
        all_fig = new_figure("Same inputs, different operating structures")
        for i, key in enumerate(MODEL_NAMES):
            add_curve(all_fig, f, key, p, MODEL_NAMES[key], COLORS[i])
        st.plotly_chart(all_fig, use_container_width=True, key="all_models_chart")
        st.caption(f"The constant-overhead model uses Cₒₚ = {p.c_op:.2f}. The other models use H = {p.H:.2f}, v = {p.v:.2f} and N = {p.N:.2f}; only the third subtracts duplication costs.")
    rows = [{"F": float(x), "current_performance": float(y), "saved_performance": float(z)}
            for x, y, z in zip(f, performance(f, model, p), performance(f, model, baseline))]
    d1, d2 = st.columns(2)
    d1.download_button("Download curve data · CSV", csv_bytes(rows), "franchising_curves.csv", "text/csv")
    state = {"model": model, "parameters": asdict(p), "saved_parameters": asdict(baseline),
             "units": "normalised performance and costs; N is outlet scale", "effort_mode": "fixed input"}
    d2.download_button("Download inputs · JSON", json.dumps(state, indent=2), "franchising_inputs.json", "application/json")

with sensitivity:
    st.subheader("Change one assumption at a time")
    st.write("Each curve uses the current sidebar inputs, changing only the chosen parameter. Dots mark global maxima.")
    options = ["c_op", "pi", "a", "theta"] if model == "baseline" else ["H", "N", "v", "vN", "pi", "a", "theta"]
    if model == "duplication":
        options = ["delta"] + options
    parameter = st.selectbox("Parameter to compare", options, format_func=LABELS.get, key=f"sweep_parameter_{model}")
    default = ", ".join(f"{x:g}" for x in SWEEP_VALUES[parameter])
    raw = st.text_input("Comparison values, separated by commas", value=default, key=f"sweep_values_{parameter}")
    st.caption("H, N, v, vN and δ comparison values follow the varied values visible in Appendices C and E. The other inputs come from your controls; these are not exact reproductions of the published figures.")
    if parameter == "vN":
        st.caption("The vN comparison holds N fixed and changes v to achieve the requested product. Each implied v must be between 0 and 1.")
    if model == "duplication":
        st.button("Compare δ = 0, vN and 2vN", on_click=compare_regimes,
                  disabled=p.vN == 0 or 2*p.vN > 1,
                  help="Requires 0 < 2vN ≤ 1 to stay within the thesis's δ range.")
    sweep_fig = new_figure(f"Sensitivity to {LABELS[parameter]}")
    try:
        values = [float(s.strip()) for s in raw.split(",")]
        if not 2 <= len(values) <= 6:
            raise ValueError("Enter between two and six numbers.")
        if len(set(values)) != len(values):
            raise ValueError("Use distinct comparison values.")
        parameters = [with_parameter(p, parameter, x) for x in values]
    except ValueError as exc:
        st.error(f"Check the comparison values: {exc}")
    else:
        table, long_rows = [], []
        for i, (value, params) in enumerate(zip(values, parameters)):
            s = add_curve(sweep_fig, f, model, params, f"{parameter} = {value:g}", COLORS[i])
            table.append({"Value": value, "Curve": s.shape, "Best F": share_text(s),
                          "Maximum P": round(s.maximum, 6), "Lowest F": share_text(s, "minimum"),
                          "Minimum P": round(s.minimum, 6)})
            long_rows.extend({"parameter": parameter, "value": value, "F": float(x), "performance": float(y)}
                             for x, y in zip(f, performance(f, model, params)))
        st.plotly_chart(sweep_fig, use_container_width=True, key="sweep_chart")
        st.dataframe(table, use_container_width=True, hide_index=True)
        st.download_button("Download sensitivity data · CSV", csv_bytes(long_rows), "franchising_sensitivity.csv", "text/csv")
    if model == "duplication":
        st.write(f"Curvature changes sign at δ = vN = {p.vN:.4f}. Below that value the curve is concave; above it the curve is convex. At equality the curve is linear. A U or inverted-U shape also requires the turning point to lie between 0% and 100%.")

with notes:
    st.subheader("The three performance functions")
    st.latex(r"p(a)=1-e^{-\theta a},\qquad c(a)=\frac{a^2}{2},\qquad q=p(a)\pi-c(a)")
    st.latex(r"P_0(F)=(1-F)(\pi-C_{op})+Fq")
    st.latex(r"C_{op}(F)=H+v(1-F)N")
    st.latex(r"P_1(F)=(1-F)[\pi-H-v(1-F)N]+Fq")
    st.latex(r"P_2(F)=P_1(F)-\delta F(1-F)")
    st.write("Source: the thesis's theoretical framework and Appendices B and D. The app retains the appendix's effort cost and success function. It does not introduce the draft's additional effort-cost coefficient.")
    st.subheader("Units and interpretation")
    st.write("Performance is average performance in normalised units, not currency or an estimated return on assets. π, Cₒₚ, H, the vN support term and δ must use a consistent scale. H is a base overhead per company outlet in the implemented equation, rather than a total headquarters budget.")
    st.write("N is presented as a normalised outlet-scale parameter because Appendix C compares N = 0.3, 1, 2 and 4. A fractional N does not mean a fraction of a physical restaurant. A larger N increases the company-operated support burden when v is held fixed.")
    st.write("Effort a is an assumed input, held fixed across F. Although the theory derives an incentive constraint, this explorer does not solve for a royalty contract or optimise effort. Royalty and entry fees drop out of the reduced-form payoff under the thesis's rent-extraction assumption.")
    st.write("Default scenarios are selected for illustration, not calibrated from the thesis's regression data. The appendix figures show comparison values but do not provide every fixed parameter in their captions; this app therefore reproduces their equations and comparison approach, without claiming exact numerical replication of each figure.")
    st.subheader("Finding the best share")
    st.latex(r"P(F)=A+BF+CF^2,\qquad F_s=-\frac{B}{2C}\quad(C\ne0)")
    st.write("The app evaluates both endpoints and any stationary point inside [0,1]. It compares their performance to find global maxima and minima, preserving ties. It handles linear and flat cases separately.")
    st.latex(r"P_1''(F)=-2vN,\qquad P_2''(F)=2(\delta-vN)")
    st.write("For P₂, a stationary point is a minimum when δ > vN. Clipping that minimum to the feasible interval would not find the maximum. At δ = vN the quadratic term vanishes, so no stationary-point division is attempted.")
    st.latex(r"F_{s,2}=\frac{H-\pi+q+2vN-\delta}{2(vN-\delta)}\quad(\delta\ne vN)")
    st.subheader("What is held fixed")
    st.dataframe([{"Input": LABELS[k], "Current value": value} for k, value in asdict(p).items()], hide_index=True, use_container_width=True)
    A, B, C = coefficients(model, p)
    st.code(f"P(F) = {A:.6f} + ({B:.6f}) F + ({C:.6f}) F²", language=None)
    st.markdown("[View the research repository](https://github.com/sazwara/thesis-modelling)")
