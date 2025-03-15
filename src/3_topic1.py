import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
import numpy as np

app = dash.Dash(__name__)
server = app.server

# Bond calculation functions
def calculate_bond_price(face_value, coupon_rate, ytm, years_to_maturity, periods_per_year=2):
    period_rate = ytm / periods_per_year
    n_periods = years_to_maturity * periods_per_year
    coupon = (face_value * coupon_rate) / periods_per_year
    
    price = 0
    for t in range(1, n_periods + 1):
        price += coupon / ((1 + period_rate) ** t)
    price += face_value / ((1 + period_rate) ** n_periods)
    return price

def pv01(face_value, coupon_rate, ytm, years_to_maturity):
    price_base = calculate_bond_price(face_value, coupon_rate, ytm, years_to_maturity)
    price_shift = calculate_bond_price(face_value, coupon_rate, ytm + 0.0001, years_to_maturity)
    return (price_base - price_shift) * 100  # In cents

def pvbp(face_value, coupon_rate, ytm, years_to_maturity):
    price_base = calculate_bond_price(face_value, coupon_rate, ytm, years_to_maturity)
    price_shift = calculate_bond_price(face_value, coupon_rate + 0.0001, ytm, years_to_maturity)
    return (price_shift - price_base) * 100  # In cents

def convexity(face_value, coupon_rate, ytm, years_to_maturity):
    price_up = calculate_bond_price(face_value, coupon_rate, ytm + 0.0001, years_to_maturity)
    price_base = calculate_bond_price(face_value, coupon_rate, ytm, years_to_maturity)
    price_down = calculate_bond_price(face_value, coupon_rate, ytm - 0.0001, years_to_maturity)
    return (price_up + price_down - 2 * price_base) * 100 / (price_base * (0.0001 ** 2))

# App layout
app.layout = html.Div([
    html.H1("Bond Analytics Dashboard", style={'textAlign': 'center', 'marginBottom': '30px'}),
    
    html.Div([
        # Left side controls
        html.Div([
            html.H3("Bond Parameters", style={'fontWeight': 'bold', 'marginBottom': '20px'}),
            html.Label("Face Value ($)", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.Input(id='face-value', type='number', value=1000,
                     style={'width': '100%', 'padding': '8px', 'marginBottom': '15px'}),
            
            html.Label("Coupon Rate (%)", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.Input(id='coupon-rate', type='number', value=5,
                     style={'width': '100%', 'padding': '8px', 'marginBottom': '15px'}),
            
            html.Label("Yield to Maturity (%)", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.Input(id='ytm', type='number', value=6,
                     style={'width': '100%', 'padding': '8px', 'marginBottom': '15px'}),
            
            html.Label("Years to Maturity", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.Input(id='years-maturity', type='number', value=5,
                     style={'width': '100%', 'padding': '8px', 'marginBottom': '20px'}),
            
            html.Button('Calculate All Metrics', id='calculate-button', n_clicks=0,
                       style={'width': '100%', 'padding': '12px', 
                              'backgroundColor': '#e6f3ff', 'color': '#2c3e50',
                              'border': '2px solid #3498db', 'borderRadius': '5px',
                              'cursor': 'pointer', 'fontSize': '16px'}),
            
            html.Div(id='metrics-output', style={'marginTop': '20px', 'padding': '20px', 
                                                'borderRadius': '5px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
            
            html.Hr(),
            html.H3("Yield Curve Trade", style={'fontWeight': 'bold', 'marginBottom': '20px'}),
            dcc.Input(id='yc-bp-change', type='number', value=10, placeholder='BP Change',
                     style={'width': '100%', 'padding': '8px', 'marginBottom': '15px'}),
            html.Button('Analyze Yield Curve', id='yc-button', n_clicks=0,
                       style={'width': '100%', 'padding': '12px', 
                              'backgroundColor': '#e6f3ff', 'color': '#2c3e50',
                              'border': '2px solid #3498db', 'borderRadius': '5px',
                              'cursor': 'pointer', 'fontSize': '16px'}),
            
            html.Hr(),
            html.H3("Butterfly Trade", style={'fontWeight': 'bold', 'marginBottom': '20px'}),
            dcc.Input(id='fly-bp-change', type='number', value=5, placeholder='BP Change',
                     style={'width': '100%', 'padding': '8px', 'marginBottom': '15px'}),
            html.Button('Analyze Butterfly', id='fly-button', n_clicks=0,
                       style={'width': '100%', 'padding': '12px', 
                              'backgroundColor': '#e6f3ff', 'color': '#2c3e50',
                              'border': '2px solid #3498db', 'borderRadius': '5px',
                              'cursor': 'pointer', 'fontSize': '16px'}),
        ], style={'width': '30%', 'float': 'left', 'padding': '20px'}),
        
        # Right side graphs and definitions
        html.Div([
            html.Div([
                html.H3("Price-Yield Relationship", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                html.P("Definition: The Price-Yield Relationship shows how the bond price changes as the yield changes. It is typically downward-sloping, indicating that bond prices fall as yields rise."),
                dcc.Graph(id='price-yield-curve', style={'height': '300px'}),
                html.P("Interpretation: The curve shows the sensitivity of the bond price to changes in yield. A steeper curve indicates higher sensitivity.",
                      style={'marginTop': '10px'})
            ], style={'marginBottom': '30px'}),
            
            html.Div([
                html.H3("Convexity Impact", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                html.P("Definition: Convexity measures the curvature of the Price-Yield Relationship. It shows how the bond's duration changes as yields change."),
                dcc.Graph(id='convexity-plot', style={'height': '300px'}),
                html.P("Interpretation: A higher convexity means the bond price is more sensitive to large yield changes. Positive convexity is beneficial as it increases price gains when yields fall and reduces price losses when yields rise.",
                      style={'marginTop': '10px'})
            ], style={'marginBottom': '30px'}),
            
            html.Div([
                html.H3("Trade Impact Analysis", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                html.P("Definition: This graph shows the impact of yield curve or butterfly trades on bond prices."),
                dcc.Graph(id='trade-impact-plot', style={'height': '300px'}),
                html.P("Interpretation: The bars represent the price impact of the trade strategy. Positive values indicate price gains, while negative values indicate price losses.",
                      style={'marginTop': '10px'})
            ])
        ], style={'width': '65%', 'float': 'right', 'padding': '20px'})
    ])
])

# Callbacks
@app.callback(
    [Output('metrics-output', 'children'),
     Output('price-yield-curve', 'figure'),
     Output('convexity-plot', 'figure')],
    [Input('calculate-button', 'n_clicks')],
    [State('face-value', 'value'),
     State('coupon-rate', 'value'),
     State('ytm', 'value'),
     State('years-maturity', 'value')]
)
def update_metrics(n_clicks, face_value, coupon_rate, ytm, years_maturity):
    coupon_rate /= 100
    ytm /= 100
    
    # Calculate metrics
    pv01_val = pv01(face_value, coupon_rate, ytm, years_maturity)
    pvbp_val = pvbp(face_value, coupon_rate, ytm, years_maturity)
    conv_val = convexity(face_value, coupon_rate, ytm, years_maturity)
    price = calculate_bond_price(face_value, coupon_rate, ytm, years_maturity)
    
    # Create yield curve
    ytm_range = np.linspace(ytm - 0.02, ytm + 0.02, 50) * 100
    prices = [calculate_bond_price(face_value, coupon_rate, y/100, years_maturity) for y in ytm_range]
    
    price_yield_fig = go.Figure()
    price_yield_fig.add_trace(go.Scatter(x=ytm_range, y=prices, mode='lines'))
    price_yield_fig.update_layout(
        title='Price-Yield Relationship',
        xaxis_title='Yield (%)',
        yaxis_title='Price ($)',
        template='plotly_white'
    )
    
    # Convexity plot
    conv_x = np.linspace(-100, 100, 50)
    conv_y = [0.5 * conv_val * (bp/10000)**2 * 100 for bp in conv_x]
    
    convexity_fig = go.Figure()
    convexity_fig.add_trace(go.Scatter(x=conv_x, y=conv_y, mode='lines'))
    convexity_fig.update_layout(
        title='Convexity Impact',
        xaxis_title='Yield Change (bps)',
        yaxis_title='Price Impact (cents)',
        template='plotly_white'
    )
    
    metrics = html.Div([
        html.H4("Calculated Metrics", style={'marginBottom': '15px'}),
        html.Div([
            html.Span("PV01: ", style={'fontWeight': 'bold'}),
            html.Span(f"{pv01_val:.2f} cents")
        ], style={'marginBottom': '10px'}),
        
        html.Div([
            html.Span("PVBP: ", style={'fontWeight': 'bold'}),
            html.Span(f"{pvbp_val:.2f} cents")
        ], style={'marginBottom': '10px'}),
        
        html.Div([
            html.Span("Convexity: ", style={'fontWeight': 'bold'}),
            html.Span(f"{conv_val:.2f}")
        ], style={'marginBottom': '10px'}),
        
        html.Div([
            html.Span("Current Price: ", style={'fontWeight': 'bold'}),
            html.Span(f"${price:.2f}")
        ])
    ], style={'padding': '20px', 'borderRadius': '5px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
    
    return metrics, price_yield_fig, convexity_fig

@app.callback(
    Output('trade-impact-plot', 'figure'),
    [Input('yc-button', 'n_clicks'),
     Input('fly-button', 'n_clicks')],
    [State('yc-bp-change', 'value'),
     State('fly-bp-change', 'value')]
)
def update_trade_plots(yc_clicks, fly_clicks, yc_bp, fly_bp):
    ctx = dash.callback_context
    if not ctx.triggered:
        return go.Figure()
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'yc-button':
        x = ['2Y', '5Y', '10Y']
        y = [-yc_bp * 0.3, -yc_bp * 0.5, -yc_bp * 0.7]
        title = f'Yield Curve Steepening ({yc_bp}bps) Impact'
    else:
        x = ['Short 2Y', 'Long 5Y', 'Short 10Y']
        y = [fly_bp * 0.5, -fly_bp * 1.2, fly_bp * 0.7]
        title = f'Butterfly Trade ({fly_bp}bps) Impact'
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=x, y=y, marker_color='#3498db'))
    fig.update_layout(
        title=title,
        yaxis_title='Price Impact (cents)',
        template='plotly_white'
    )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)