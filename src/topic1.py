import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import numpy as np
import math

# Initialize the Dash app
app = dash.Dash(__name__)

# Define financial calculation functions
def future_value(PV, r, m, T):
    """Calculate Future Value with discrete compounding: FV = PV * (1 + r/m)^(T*m)"""
    N = T * m
    return PV * (1 + r / m) ** N

def future_value_continuous(PV, r, T):
    """Calculate Future Value with continuous compounding: FV = PV * e^(r*T)"""
    return PV * math.exp(r * T)

def future_value_simple(PV, r, T):
    """Calculate Future Value with simple interest: FV = PV * (1 + r*T)"""
    return PV * (1 + r * T)

def present_value(FV, r, m, T):
    """Calculate Present Value with discrete compounding: PV = FV / (1 + r/m)^(T*m)"""
    N = T * m
    return FV / (1 + r / m) ** N

def discount_factor(r, m, T):
    """Calculate discount factor: D(T) = 1 / (1 + r/m)^(T*m)"""
    N = T * m
    return 1 / (1 + r / m) ** N

def bond_valuation(coupon, face_value, r, m, T):
    """Calculate bond price as sum of discounted cash flows"""
    periods = int(T * m)
    coupon_payment = coupon * face_value / m
    cash_flows = [coupon_payment] * periods
    cash_flows[-1] += face_value
    
    times = np.arange(1/m, T + 1/m, 1/m)
    PV = 0
    for i, cf in enumerate(cash_flows):
        PV += cf * discount_factor(r, m, times[i])
    return PV, cash_flows, times

# Layout of the Dash app
app.layout = html.Div([
    html.H1("Interactive FV, PV, Discount Factor & Bond Valuation Explorer"),
    html.P("Adjust the sliders and watch the graphs update in real-time as you drag!"),
    
    # Two-column layout
    html.Div([
        # Left column - Controls and Results
        html.Div([
            # General Inputs
            html.H3("General Inputs"),
            html.Label("Present Value (PV):"),
            dcc.Slider(id='PV', min=50.0, max=10000.0, step=5.0, value=100.0, marks={50: '50', 10000: '10000'}, updatemode='drag'),
            html.Label("Annual Interest Rate (r):"),
            dcc.Slider(id='r', min=0.01, max=1.00, step=0.01, value=0.05, marks={0.01: '1%', 1.00: '100%'}, updatemode='drag'),
            html.Label("Compounding Periods per Year (m):"),
            dcc.Slider(id='m', min=1, max=12, step=1, value=2, marks={1: '1', 12: '12'}, updatemode='drag'),
            html.Label("Time in Years (T):"),
            dcc.Slider(id='T', min=0.5, max=20.0, step=0.5, value=2.0, marks={0.5: '0.5', 20: '10'}, updatemode='drag'),
            html.Label("Future Value (FV) for Present Value Graph:"),
            dcc.Slider(id='FV_adjustable', min=1.0, max=10000.0, step=1.0, value=100.0, marks={1: '1', 10000: '10000'}, updatemode='drag'),
            
            # Bond-Specific Inputs
            html.H3("Bond-Specific Inputs"),
            html.Label("Coupon Rate:"),
            dcc.Slider(id='coupon', min=0.01, max=0.10, step=0.01, value=0.05, marks={0.01: '1%', 0.10: '10%'}, updatemode='drag'),
            html.Label("Face Value:"),
            dcc.Slider(id='face_value', min=50.0, max=20000.0, step=5.0, value=100.0, marks={50: '50', 20000: '20000'}, updatemode='drag'),
            
            # Results Section at the bottom
            html.Hr(),
            html.H2("Results"),
            html.Div(id='results')
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '20px', 'vertical-align': 'top'}),
        
        # Right column - Graphs
        html.Div([
            html.H2("Interactive Graphs"),
            
            # Definitions for compounding methods
            html.Div([
                html.P("Discrete compounding (periodic interest): Interest is calculated at specific intervals."),
                html.P("Continuous compounding (exponential growth): Interest is calculated continuously."),
                html.P("Simple interest (linear growth): Interest is calculated only on the principal amount.")
            ], style={'margin-bottom': '20px'}),
            
            html.P("Future Value Over Time: This graph shows how your investment grows over time under three methods: discrete compounding (periodic interest), continuous compounding (exponential growth), and simple interest (linear growth)."),
            dcc.Graph(id='fig1'),
            html.P("Note: Adjust PV, r, m, T sliders to see changes in this graph."),
            
            html.Hr(),
            
            html.P("Discount Factor and Present Value Over Time: This section includes two graphs. The first shows how the discount factor decreases over time, reflecting the time value of money. The second graph shows how the value of a future amount (set via the FV slider) to be received at time T appreciates as time progresses towards T."),
            dcc.Graph(id='fig2'),
            dcc.Graph(id='fig3'),
            html.P("Note: This graph shows how the value of the future amount appreciates as time approaches T. Adjust FV, r, m, T sliders to see changes."),
            
            html.Hr(),
            
            html.P("Bond Cash Flows and Their Present Values: This bar chart compares the bond’s future cash flows (coupon payments plus principal at maturity) with their present values, showing how each payment is discounted based on when it’s received."),
            dcc.Graph(id='fig4'),
            html.P("Note: Adjust coupon rate, face_value, r, m, T sliders to see changes in this graph.*")
        ], style={'width': '65%', 'display': 'inline-block', 'padding': '20px'})
    ])
])

# Callback to update results and graphs
@app.callback(
    [
        Output('results', 'children'),
        Output('fig1', 'figure'),
        Output('fig2', 'figure'),
        Output('fig3', 'figure'),
        Output('fig4', 'figure')
    ],
    [
        Input('PV', 'value'),
        Input('r', 'value'),
        Input('m', 'value'),
        Input('T', 'value'),
        Input('FV_adjustable', 'value'),
        Input('coupon', 'value'),
        Input('face_value', 'value')
    ]
)
def update_app(PV, r, m, T, FV_adjustable, coupon, face_value):
    # Perform calculations
    fv_discrete = future_value(PV, r, m, T)
    fv_continuous = future_value_continuous(PV, r, T)
    fv_simple = future_value_simple(PV, r, T)
    pv = present_value(fv_discrete, r, m, T)
    discount = discount_factor(r, m, T)
    bond_value, cash_flows, times_bond = bond_valuation(coupon, face_value, r, m, T)

    # Results
    results = html.Div([
        html.P(f"Future Value (Discrete Compounding): ${fv_discrete:.2f}"),
        html.P(f"Future Value (Continuous Compounding): ${fv_continuous:.2f}"),
        html.P(f"Future Value (Simple Interest): ${fv_simple:.2f}"),
        html.P(f"Present Value (from FV Discrete): ${pv:.2f}"),
        html.P(f"Discount Factor (at T): {discount:.4f}"),
        html.P(f"Bond Value: ${bond_value:.2f}")
    ])

    # Graph 1: Future Value Over Time
    times = np.linspace(0, T, 100)
    fv_discrete_plot = [future_value(PV, r, m, t) for t in times]
    fv_continuous_plot = [future_value_continuous(PV, r, t) for t in times]
    fv_simple_plot = [future_value_simple(PV, r, t) for t in times]

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=times, y=fv_discrete_plot, mode='lines', name='Discrete Compounding'))
    fig1.add_trace(go.Scatter(x=times, y=fv_continuous_plot, mode='lines', name='Continuous Compounding', line=dict(dash='dash')))
    fig1.add_trace(go.Scatter(x=times, y=fv_simple_plot, mode='lines', name='Simple Interest', line=dict(dash='dot')))
    fig1.update_layout(
        title=dict(text="Future Value Growth", font=dict(size=20, color="black", weight='bold')),
        xaxis_title="Time (Years)",
        yaxis_title="Future Value ($)",
        hovermode="x",
        xaxis=dict(range=[0, T])
    )

    # Graph 2: Discount Factor Over Time
    discount_plot = [discount_factor(r, m, t) for t in times]
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=times, y=discount_plot, mode='lines', name='Discount Factor', line=dict(color='purple')))
    fig2.update_layout(
        title=dict(text="Discount Factor Decay", font=dict(size=20, color="black", weight='bold')),
        xaxis_title="Time (Years)",
        yaxis_title="Discount Factor",
        hovermode="x",
        xaxis=dict(range=[0, T])
    )

    # Graph 3: Value Over Time of FV to be Received at Time T
    s_times = np.linspace(0, T, 100)
    pv_over_time = [present_value(FV_adjustable, r, m, T - s) for s in s_times]
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=s_times, y=pv_over_time, mode='lines', name='Present Value', line=dict(color='green')))
    fig3.update_layout(
        title=dict(text=f"Value Over Time of ${FV_adjustable:.2f} to be Received at T={T:.1f} Years", font=dict(size=20, color="black", weight='bold')),
        xaxis_title="Current Time (s Years from Now)",
        yaxis_title="Value at Time s ($)",
        hovermode="x",
        xaxis=dict(range=[0, T])
    )

    # Graph 4: Bond Cash Flows and Present Values
    pv_cash_flows = [cf * discount_factor(r, m, t) for cf, t in zip(cash_flows, times_bond)]
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(x=times_bond, y=cash_flows, name='Future Cash Flows', marker_color='blue', opacity=0.7))
    fig4.add_trace(go.Bar(x=times_bond, y=pv_cash_flows, name='Present Values', marker_color='orange', opacity=0.7))
    fig4.update_layout(
        title="Bond Cash Flows vs. Present Values",
        xaxis_title="Time (Years)",
        yaxis_title="Value ($)",
        barmode='group',
        hovermode="x"
    )

    return results, fig1, fig2, fig3, fig4

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)