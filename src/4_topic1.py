import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import numpy as np

app = dash.Dash(__name__)
server = app.server

# ======================================================================
# Core Calculation Functions
# ======================================================================
def calculate_repo_transaction(principal, repo_rate, days):
    """Calculate repo transaction repayment amount"""
    if days <= 0 or repo_rate < 0 or principal <= 0:
        return 0.0
    interest = principal * repo_rate * days / 360
    repayment = principal + interest
    return repayment

def calculate_forward_price(dirty_price, repo_rate, days_to_forward, coupon=0, days_to_coupon=0):
    """Calculate forward price with financing and coupon adjustment"""
    if days_to_forward <= 0:
        return dirty_price
    
    financing_cost = dirty_price * repo_rate * days_to_forward / 360
    
    if days_to_coupon < days_to_forward and days_to_coupon > 0:
        coupon_fv = coupon * (1 + repo_rate * (days_to_forward - days_to_coupon) / 360)
    else:
        coupon_fv = 0
    
    forward_dirty = dirty_price * (1 + repo_rate * days_to_forward / 360) - coupon_fv
    return forward_dirty

def calculate_carry(spot_price, forward_price):
    """Calculate carry between spot and forward prices"""
    return forward_price - spot_price

def calculate_roll_down(current_yield, historical_yields):
    """Calculate roll-down yield"""
    if len(historical_yields) == 0:
        return 0.0
    return current_yield - historical_yields[-1]

def repo_adjusted_yield(special_yield, gc_rate, special_rate, holding_days, pv01):
    """Calculate repo-adjusted yield"""
    if pv01 <= 0 or holding_days <= 0:
        return special_yield
    adjustment = ((gc_rate - special_rate) * 365 * holding_days) / (360 * pv01 * 100)
    return special_yield + adjustment

# ======================================================================
# App Layout
# ======================================================================
app.layout = html.Div([
    html.H1("Fixed Income Analytics Dashboard", 
           style={'textAlign': 'center', 'color': '#2c3e50', 'padding': '20px'}),
    
    html.Div([
        # Left Panel - Inputs and Results
        html.Div([
            html.H3("Input Parameters", style={'color': '#3498db'}),
            
            html.Div([
                html.Label("Principal Amount ($)"),
                dcc.Input(id='principal', value=1000000, type='number', min=0)
            ], style={'margin': '10px 0'}),
            
            html.Div([
                html.Label("Repo Rate (%)"),
                dcc.Input(id='repo-rate', value=3.5, type='number', min=0, step=0.1)
            ], style={'margin': '10px 0'}),
            
            html.Div([
                html.Label("Days Horizon"),
                dcc.Input(id='days', value=30, type='number', min=1)
            ], style={'margin': '10px 0'}),
            
            html.Div([
                html.Label("Coupon Payment ($)"),
                dcc.Input(id='coupon', value=0, type='number', min=0)
            ], style={'margin': '10px 0'}),
            
            html.Div([
                html.Label("Days to Coupon"),
                dcc.Input(id='coupon-days', value=0, type='number', min=0)
            ], style={'margin': '10px 0'}),
            
            html.Div([
                html.Label("Current Yield (%)"),
                dcc.Input(id='current-yield', value=4.0, type='number', min=0, step=0.1)
            ], style={'margin': '10px 0'}),
            
            html.Div([
                html.Label("GC Rate (%)"),
                dcc.Input(id='gc-rate', value=3.75, type='number', min=0, step=0.1)
            ], style={'margin': '10px 0'}),
            
            html.Div([
                html.Label("PV01 (cents)"),
                dcc.Input(id='pv01', value=1.898, type='number', min=0, step=0.1)
            ], style={'margin': '10px 0'}),
            
            html.Button('Calculate All', id='calculate-btn', 
                       style={'backgroundColor': '#3498db', 'color': 'white', 
                              'padding': '10px 20px', 'margin': '20px 0'}),
            
            html.Div(id='results', style={'backgroundColor': '#f9f9f9', 'padding': '20px',
                                        'borderRadius': '5px', 'marginTop': '20px'})
            
        ], style={'width': '30%', 'float': 'left', 'padding': '20px'}),
        
        # Right Panel - Visualizations
        html.Div([
            # Repo Transaction
            html.Div([
                html.H3("Repo Transaction Flow"),
                dcc.Graph(id='repo-plot'),
                html.P("Interpretation: Shows the growth of repo financing over time. The curve represents the total repayment amount.",
                      style={'color': '#7f8c8d', 'fontSize': '14px'})
            ], style={'marginBottom': '40px'}),
            
            # Forward Price Analysis
            html.Div([
                html.H3("Forward Price Composition"),
                dcc.Graph(id='forward-plot'),
                html.P("Interpretation: Breakdown of forward price into components: spot price, financing cost, and coupon adjustment.",
                      style={'color': '#7f8c8d', 'fontSize': '14px'})
            ], style={'marginBottom': '40px'}),
            
            # Carry Analysis
            html.Div([
                html.H3("Carry Over Time"),
                dcc.Graph(id='carry-plot'),
                html.P("Interpretation: Shows the profit/loss from holding a position over time, considering financing costs and coupon income.",
                      style={'color': '#7f8c8d', 'fontSize': '14px'})
            ], style={'marginBottom': '40px'}),
            
            # Roll-Down Analysis
            html.Div([
                html.H3("Roll-Down Analysis"),
                dcc.Graph(id='roll-down-plot'),
                html.P("Interpretation: Shows the yield change as the bond's maturity shortens over time.",
                      style={'color': '#7f8c8d', 'fontSize': '14px'})
            ])
            
        ], style={'width': '65%', 'float': 'right', 'padding': '20px'})
    ])
])

# ======================================================================
# Callbacks
# ======================================================================
@app.callback(
    [Output('repo-plot', 'figure'),
     Output('forward-plot', 'figure'),
     Output('carry-plot', 'figure'),
     Output('roll-down-plot', 'figure'),
     Output('results', 'children')],
    [Input('calculate-btn', 'n_clicks')],
    [State('principal', 'value'),
     State('repo-rate', 'value'),
     State('days', 'value'),
     State('coupon', 'value'),
     State('coupon-days', 'value'),
     State('current-yield', 'value'),
     State('gc-rate', 'value'),
     State('pv01', 'value')]
)
def update_plots(n_clicks, principal, repo_rate, days, coupon, coupon_days, current_yield, gc_rate, pv01):
    # Input validation and conversion
    principal = principal if principal else 0
    repo_rate = repo_rate / 100 if repo_rate else 0
    days = days if days else 1
    coupon = coupon if coupon else 0
    coupon_days = coupon_days if coupon_days else 0
    current_yield = current_yield / 100 if current_yield else 0
    gc_rate = gc_rate / 100 if gc_rate else 0
    pv01 = pv01 if pv01 else 0

    # Generate time range
    days_range = np.arange(1, days + 1)
    
    # Calculations
    repo_values = [calculate_repo_transaction(principal, repo_rate, d) for d in days_range]
    forward_prices = [calculate_forward_price(principal, repo_rate, d, coupon, coupon_days) 
                     for d in days_range]
    carries = [calculate_carry(principal, fp) for fp in forward_prices]
    
    # Roll-down analysis
    historical_yields = np.linspace(current_yield - 0.02, current_yield, 10)
    roll_downs = [calculate_roll_down(current_yield, historical_yields[:i+1]) 
                 for i in range(len(historical_yields))]
    
    # Create figures
    repo_fig = go.Figure()
    repo_fig.add_trace(go.Scatter(x=days_range, y=repo_values, 
                                mode='lines+markers', name='Repo Value'))
    repo_fig.update_layout(title='Repo Financing Growth',
                          xaxis_title='Days',
                          yaxis_title='Value ($)')
    
    forward_fig = go.Figure(go.Waterfall(
        name="Price",
        orientation="v",
        measure=["absolute", "relative", "relative", "total"],
        x=["Spot Price", "Financing Cost", "Coupon Adjustment", "Forward Price"],
        textposition="outside",
        text=[f"${principal:,.2f}", f"+${principal * repo_rate * days / 360:,.2f}", 
              f"-${coupon * (1 + repo_rate * (days - coupon_days)/360):,.2f}", ""],
        y=[principal, principal * repo_rate * days / 360, 
           -coupon * (1 + repo_rate * (days - coupon_days)/360), 0],
        connector={"line":{"color":"rgb(63, 63, 63)"}},
    ))
    forward_fig.update_layout(title='Forward Price Breakdown')
    
    carry_fig = go.Figure()
    carry_fig.add_trace(go.Bar(x=days_range, y=carries, name='Daily Carry'))
    carry_fig.update_layout(title='Daily Carry Analysis',
                           xaxis_title='Days',
                           yaxis_title='Carry ($)')
    
    roll_down_fig = go.Figure()
    roll_down_fig.add_trace(go.Scatter(x=np.arange(len(historical_yields)), y=roll_downs, 
                                     mode='lines+markers', name='Roll-Down'))
    roll_down_fig.update_layout(title='Roll-Down Analysis',
                               xaxis_title='Time Periods',
                               yaxis_title='Roll-Down Yield (%)',
                               yaxis_tickformat=".2%")
    
    # Results calculation
    final_repo = calculate_repo_transaction(principal, repo_rate, days)
    final_forward = calculate_forward_price(principal, repo_rate, days, coupon, coupon_days)
    final_carry = calculate_carry(principal, final_forward)
    repo_adjusted = repo_adjusted_yield(current_yield, gc_rate, repo_rate, days, pv01)
    
    # Format results
    results = html.Div([
        html.H4("Transaction Results", style={'color': '#2c3e50'}),
        html.Div([
            html.Div([
                html.Span("Final Repo Value:", style={'fontWeight': 'bold'}),
                html.Span(f"${final_repo:,.2f}", style={'float': 'right'})
            ], style={'margin': '10px 0'}),
            
            html.Div([
                html.Span("Forward Price:", style={'fontWeight': 'bold'}),
                html.Span(f"${final_forward:,.2f}", style={'float': 'right'})
            ], style={'margin': '10px 0'}),
            
            html.Div([
                html.Span("Total Carry:", style={'fontWeight': 'bold'}),
                html.Span(f"${final_carry:,.2f}", style={'float': 'right'})
            ], style={'margin': '10px 0'}),
            
            html.Div([
                html.Span("Repo-Adjusted Yield:", style={'fontWeight': 'bold'}),
                html.Span(f"{repo_adjusted * 100:.2f}%", style={'float': 'right'})
            ], style={'margin': '10px 0'})
        ])
    ])
    
    return repo_fig, forward_fig, carry_fig, roll_down_fig, results

# ======================================================================
# Run Server
# ======================================================================
if __name__ == '__main__':
    app.run_server(debug=True)