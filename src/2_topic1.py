import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import numpy as np
from scipy.optimize import newton
from datetime import datetime

app = dash.Dash(__name__)
server = app.server

# Function to calculate bond price
def bond_price(face_value, coupon_rate, ytm, years_to_maturity, comp_per_year):
    periods = years_to_maturity * comp_per_year
    coupon = (face_value * coupon_rate) / comp_per_year
    price = 0
    for t in range(1, periods + 1):
        price += coupon / ((1 + ytm / comp_per_year) ** t)
    price += face_value / ((1 + ytm / comp_per_year) ** periods)
    return price

# Function to calculate YTM
def calculate_ytm(face_value, coupon_rate, price, years_to_maturity, comp_per_year):
    def ytm_func(y):
        return bond_price(face_value, coupon_rate, y, years_to_maturity, comp_per_year) - price
    try:
        return newton(ytm_func, coupon_rate, maxiter=100)
    except:
        return np.nan

# Function to calculate accrued interest
def accrued_interest(face_value, coupon_rate, settlement_date, last_coupon_date, next_coupon_date, comp_per_year):
    days_in_period = (next_coupon_date - last_coupon_date).days
    days_accrued = (settlement_date - last_coupon_date).days
    coupon_payment = (face_value * coupon_rate) / comp_per_year
    return coupon_payment * (days_accrued / days_in_period)

# Function to calculate zero-coupon bond price
def zero_coupon_bond_price(face_value, ytm, years_to_maturity):
    return face_value / ((1 + ytm) ** years_to_maturity)

app.layout = html.Div([
    html.H1("Interactive Bond Valuation Dashboard", style={'textAlign': 'center', 'marginBottom': '30px'}),
    
    html.Div([
        # Left Side: Regular Bond and Zero-Coupon Bond Sections
        html.Div([
            # Regular Bond Section
            html.Div([
                html.H3("Regular Bond Valuation", style={'fontWeight': 'bold', 'marginBottom': '20px'}),
                html.Div([
                    html.Label("Face Value ($)", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Input(id='face-value', type='number', value=1000,
                             style={'width': '100%', 'padding': '8px', 'marginBottom': '15px'}),
                    
                    html.Label("Annual Coupon Rate (%)", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Input(id='coupon-rate', type='number', value=5,
                             style={'width': '100%', 'padding': '8px', 'marginBottom': '15px'}),
                    
                    html.Label("Current Price ($)", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Input(id='price', type='number', value=950,
                             style={'width': '100%', 'padding': '8px', 'marginBottom': '15px'}),
                    
                    html.Label("Years to Maturity", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Input(id='years', type='number', value=5,
                             style={'width': '100%', 'padding': '8px', 'marginBottom': '15px'}),
                    
                    html.Label("Compounding Periods/Year", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id='compounding',
                        options=[{'label': i, 'value': i} for i in [1, 2, 4, 12]],
                        value=2,
                        style={'width': '100%', 'marginBottom': '20px'}
                    ),
                    
                    html.Label("Settlement Date", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Input(id='settlement-date', type='text', value='2023-10-01',
                             style={'width': '100%', 'padding': '8px', 'marginBottom': '15px'}),
                    
                    html.Label("Last Coupon Date", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Input(id='last-coupon-date', type='text', value='2023-04-01',
                             style={'width': '100%', 'padding': '8px', 'marginBottom': '15px'}),
                    
                    html.Label("Next Coupon Date", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Input(id='next-coupon-date', type='text', value='2023-10-01',
                             style={'width': '100%', 'padding': '8px', 'marginBottom': '20px'}),
                    
                    html.Button('Calculate Regular Bond', id='calculate-button', n_clicks=0,
                               style={'width': '100%', 'padding': '12px', 
                                      'backgroundColor': '#e6f3ff', 'color': '#2c3e50',
                                      'border': '2px solid #3498db', 'borderRadius': '5px',
                                      'cursor': 'pointer', 'fontSize': '16px'}),
                    
                    html.Div(id='calculation-results', 
                            style={'marginTop': '20px', 'padding': '20px', 
                                   'borderRadius': '5px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
                ], style={'width': '100%', 'padding': '20px'})
            ], style={'marginBottom': '30px'}),
            
            # Zero-Coupon Bond Section
            html.Div([
                html.H3("Zero-Coupon Bond Valuation", style={'fontWeight': 'bold', 'marginBottom': '20px'}),
                html.Div([
                    html.Label("Face Value ($)", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Input(id='zero-face-value', type='number', value=1000,
                             style={'width': '100%', 'padding': '8px', 'marginBottom': '15px'}),
                    
                    html.Label("Yield to Maturity (%)", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Input(id='zero-ytm', type='number', value=5,
                             style={'width': '100%', 'padding': '8px', 'marginBottom': '15px'}),
                    
                    html.Label("Years to Maturity", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Input(id='zero-years', type='number', value=5,
                             style={'width': '100%', 'padding': '8px', 'marginBottom': '20px'}),
                    
                    html.Button('Calculate Zero-Coupon Bond', id='zero-calculate-button', n_clicks=0,
                               style={'width': '100%', 'padding': '12px', 
                                      'backgroundColor': '#e6f3ff', 'color': '#2c3e50',
                                      'border': '2px solid #3498db', 'borderRadius': '5px',
                                      'cursor': 'pointer', 'fontSize': '16px'}),
                    
                    html.Div(id='zero-calculation-results', 
                            style={'marginTop': '20px', 'padding': '20px', 
                                   'borderRadius': '5px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
                ], style={'width': '100%', 'padding': '20px'})
            ])
        ], style={'width': '30%', 'float': 'left'}),
        
        # Right Side: Graphs
        html.Div([
            # Price-Yield Relationship Graph
            html.Div([
                html.H3("Price-Yield Relationship Graph", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                html.P("The Price-Yield Relationship Graph shows how the price of a bond changes as the yield to maturity (YTM) changes. The X-axis shows YTM in percentages (e.g., 2%, 4%). Key points to observe:"),
                html.Ul([
                    html.Li("When YTM = Coupon Rate, the bond trades at par (price = face value)."),
                    html.Li("When YTM > Coupon Rate, the bond trades at a discount (price < face value)."),
                    html.Li("When YTM < Coupon Rate, the bond trades at a premium (price > face value)."),
                ]),
                dcc.Graph(id='price-yield-curve', style={'height': '45vh', 'marginBottom': '20px'})
            ], style={'marginBottom': '30px'}),
            
            # Bond Cash Flow Diagram
            html.Div([
                html.H3("Bond Cash Flow Diagram", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                html.P("The Bond Cash Flow Diagram shows the timing and amount of cash flows (coupon payments and principal repayment) over the life of the bond. Each bar represents a cash flow, with the final bar including both the last coupon payment and the face value repayment."),
                dcc.Graph(id='cash-flow-diagram', style={'height': '45vh'})
            ], style={'marginBottom': '30px'}),
            
            # Zero-Coupon Bond Graph
            html.Div([
                html.H3("Zero-Coupon Bond Price vs. Yield", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                html.P("The graph below shows the relationship between the price of a zero-coupon bond and its yield to maturity (YTM). Zero-coupon bonds do not pay periodic coupons; instead, they are issued at a discount and pay the face value at maturity."),
                dcc.Graph(id='zero-coupon-graph', style={'height': '45vh'})
            ])
        ], style={'width': '65%', 'float': 'right', 'padding': '20px'})
    ])
])

# Callback for Regular Bond
@app.callback(
    [Output('calculation-results', 'children'),
     Output('price-yield-curve', 'figure'),
     Output('cash-flow-diagram', 'figure')],
    [Input('calculate-button', 'n_clicks')],
    [State('face-value', 'value'),
     State('coupon-rate', 'value'),
     State('price', 'value'),
     State('years', 'value'),
     State('compounding', 'value'),
     State('settlement-date', 'value'),
     State('last-coupon-date', 'value'),
     State('next-coupon-date', 'value')]
)
def update_output(n_clicks, face_value, coupon_rate, price, years, comp, settlement_date, last_coupon_date, next_coupon_date):
    coupon_rate = coupon_rate / 100
    ytm = calculate_ytm(face_value, coupon_rate, price, years, comp)
    
    # Calculate accrued interest
    settlement_date = datetime.strptime(settlement_date, '%Y-%m-%d')
    last_coupon_date = datetime.strptime(last_coupon_date, '%Y-%m-%d')
    next_coupon_date = datetime.strptime(next_coupon_date, '%Y-%m-%d')
    accrued = accrued_interest(face_value, coupon_rate, settlement_date, last_coupon_date, next_coupon_date, comp)
    dirty_price = price + accrued
    
    # Determine status and colors
    if np.isnan(ytm):
        status = "Invalid Inputs"
        color = '#f8d7da'
        ytm_color = '#721c24'
    else:
        if price > face_value:
            status = "Premium Bond (Price > Face Value)"
            color = '#f8d7da'  # Light red
            ytm_color = '#dc3545'
        elif price < face_value:
            status = "Discount Bond (Price < Face Value)"
            color = '#d4edda'  # Light green
            ytm_color = '#28a745'
        else:
            status = "Par Bond (Price = Face Value)"
            color = '#fff3cd'  # Light yellow
            ytm_color = '#ffc107'
    
    # Update results box style
    results_style = {
        'backgroundColor': color,
        'border': f'2px solid {ytm_color}',
        'color': ytm_color,
        'fontWeight': 'bold'
    }
    
    # Create price-yield curve
    ytm_values = np.linspace(0.001, 0.20, 50)
    prices = [bond_price(face_value, coupon_rate, y, years, comp) for y in ytm_values]
    
    price_curve = go.Figure()
    price_curve.add_trace(go.Scatter(x=ytm_values*100, y=prices, mode='lines', name='Price-Yield Curve'))
    price_curve.add_trace(go.Scatter(x=[ytm*100], y=[price], mode='markers', 
                                   marker=dict(size=12, color=ytm_color), name='Current Position'))
    price_curve.update_layout(
        title='<b>Price-Yield Relationship</b>',
        xaxis_title='Yield to Maturity (YTM in %)',
        yaxis_title='Bond Price ($)',
        template='plotly_white',
        showlegend=True
    )
    
    # Create cash flow diagram
    periods = years * comp
    cash_flows = [(face_value * coupon_rate)/comp] * periods
    cash_flows[-1] += face_value
    
    cash_flow_fig = go.Figure()
    cash_flow_fig.add_trace(go.Bar(x=[f"Period {i+1}" for i in range(periods)], y=cash_flows,
                                 marker_color=ytm_color))
    cash_flow_fig.update_layout(
        title='<b>Bond Cash Flow Diagram</b>',
        xaxis_title='Period',
        yaxis_title='Cash Flow ($)',
        template='plotly_white'
    )
    
    # Prepare results
    results = html.Div([
        html.H4("Calculation Results", style={'marginBottom': '15px'}),
        html.Div([
            html.Span("Yield to Maturity (YTM): ", style={'fontWeight': 'bold'}),
            html.Span(f"{ytm*100:.2f}%", style={'color': ytm_color})
        ], style={'marginBottom': '10px'}),
        
        html.Div([
            html.Span("Bond Status: ", style={'fontWeight': 'bold'}),
            html.Span(status)
        ], style={'marginBottom': '10px'}),
        
        html.Div([
            html.Span("Coupon Rate: ", style={'fontWeight': 'bold'}),
            html.Span(f"{coupon_rate*100:.2f}%")
        ], style={'marginBottom': '10px'}),
        
        html.Div([
            html.Span("Clean Price: ", style={'fontWeight': 'bold'}),
            html.Span(f"${price:.2f}")
        ], style={'marginBottom': '10px'}),
        
        html.Div([
            html.Span("Accrued Interest: ", style={'fontWeight': 'bold'}),
            html.Span(f"${accrued:.2f}")
        ], style={'marginBottom': '10px'}),
        
        html.Div([
            html.Span("Dirty Price: ", style={'fontWeight': 'bold'}),
            html.Span(f"${dirty_price:.2f}")
        ])
    ], style=results_style)
    
    return results, price_curve, cash_flow_fig

# Callback for Zero-Coupon Bond
@app.callback(
    [Output('zero-calculation-results', 'children'),
     Output('zero-coupon-graph', 'figure')],
    [Input('zero-calculate-button', 'n_clicks')],
    [State('zero-face-value', 'value'),
     State('zero-ytm', 'value'),
     State('zero-years', 'value')]
)
def update_zero_coupon_output(n_clicks, face_value, ytm, years):
    ytm = ytm / 100  # Convert percentage to decimal
    price = zero_coupon_bond_price(face_value, ytm, years)
    
    # Create zero-coupon bond graph
    ytm_values = np.linspace(0.001, 0.20, 50)
    prices = [zero_coupon_bond_price(face_value, y, years) for y in ytm_values]
    
    zero_coupon_graph = go.Figure()
    zero_coupon_graph.add_trace(go.Scatter(x=ytm_values*100, y=prices, mode='lines', name='Zero-Coupon Bond Price'))
    zero_coupon_graph.add_trace(go.Scatter(x=[ytm*100], y=[price], mode='markers', 
                                marker=dict(size=12, color='red'), name='Current Position'))
    zero_coupon_graph.update_layout(
        title='<b>Zero-Coupon Bond Price vs. Yield</b>',
        xaxis_title='Yield to Maturity (YTM in %)',
        yaxis_title='Bond Price ($)',
        template='plotly_white',
        showlegend=True
    )
    
    # Prepare results
    results = html.Div([
        html.H4("Zero-Coupon Bond Results", style={'marginBottom': '15px'}),
        html.Div([
            html.Span("Face Value: ", style={'fontWeight': 'bold'}),
            html.Span(f"${face_value:.2f}")
        ], style={'marginBottom': '10px'}),
        
        html.Div([
            html.Span("Yield to Maturity (YTM): ", style={'fontWeight': 'bold'}),
            html.Span(f"{ytm*100:.2f}%")
        ], style={'marginBottom': '10px'}),
        
        html.Div([
            html.Span("Years to Maturity: ", style={'fontWeight': 'bold'}),
            html.Span(f"{years}")
        ], style={'marginBottom': '10px'}),
        
        html.Div([
            html.Span("Bond Price: ", style={'fontWeight': 'bold'}),
            html.Span(f"${price:.2f}")
        ])
    ], style={'padding': '20px', 'borderRadius': '5px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
    
    return results, zero_coupon_graph

if __name__ == '__main__':
    app.run_server(debug=True)