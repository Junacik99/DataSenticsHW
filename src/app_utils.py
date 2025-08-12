# app_utils.py
# This module contains utility functions for the Dash application layout and processing recommendations.

from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd


def create_layout(app):
    """
    Create the layout for the Dash application.

    Parameters:
        app (Dash): The Dash application instance.
    """

    return html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col(html.H1(app.title), className="text-center mb-4")
            ], justify="center"),

            # Dropdown for selecting recommendation algorithm
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(
                        id='algorithm-dropdown',
                        options=[
                            {'label': 'Content-Based', 'value': 'cb'},
                            {'label': 'Correlation', 'value': 'corr'},
                            {'label': 'Association rules', 'value': 'assoc'}
                        ],
                        value='corr',
                        clearable=False,
                        style={'width': '300px'}
                    ),
                    width="auto",
                    className="mb-2 d-flex justify-content-center"
                )
            ], justify="center"),

            # Input for book title
            dbc.Row([
                dbc.Col(
                    dcc.Input(
                        id='book-input',
                        type='text',
                        placeholder='Enter book title',
                        style={'width': '300px'}
                    ),
                    width="auto",
                    className="mb-2 d-flex justify-content-center"
                ),
            ], justify="center"),

            # Button to trigger search
            dbc.Row([
                dbc.Col(
                    dbc.Button(
                        'Search', 
                        id='search-button', 
                        color='primary', 
                        style={'width': '300px'}
                    ),
                    width="auto",
                    className="mb-2 d-flex justify-content-center"
                ),
            ], justify="center"),

            # Output area for displaying results in a vertically scrollable grid
            dbc.Row([
                dbc.Col(
                    html.Div(
                        id='results-output',
                        className="mt-4",
                        style={
                            'display': 'grid',
                            'gridTemplateColumns': 'repeat(auto-fill, minmax(180px, 1fr))',
                            'gap': '20px',
                            'maxHeight': '600px',
                            'overflowY': 'auto',
                            'padding': '10px',
                            'backgroundColor': '#f8f9fa',
                            'borderRadius': '8px'
                        }
                    ),
                )
            ])
        ])
    ])


def process_recommendations(recommendations, algorithm):
    """
    Process the recommendations based on the selected algorithm.

    Parameters:
        recommendations (list or pd.DataFrame): The recommendations returned by the recommendation function.
        algorithm (str): The selected recommendation method ('cb', 'assoc', 'corr').

    Returns:
        list: A list of Dash components representing the recommendations.
    """

    placeholder_url = "/assets/book_placeholder.png" # Placeholder image URL

    if algorithm == 'cb':
        books = []
        for book in recommendations:
            books.append(
                dbc.Row([
                    dbc.Col(
                        html.Div([
                            html.Img(src=placeholder_url, alt="Book cover", style={"width": "100px", "display": "block", "margin": "0 auto"}),
                            html.Div(book, style={"textAlign": "center", "marginTop": "10px"})
                        ]),
                        width="auto"
                    )
                ], className="mt-2", justify="center")
            )
        return books

    elif algorithm == 'assoc':
        books = []
        for book in recommendations:
            books.append(
                dbc.Row([
                    dbc.Col(
                        html.Div([
                            html.Img(src=placeholder_url, alt="Book cover", style={"width": "100px", "display": "block", "margin": "0 auto"}),
                            html.Div(book, style={"textAlign": "center", "marginTop": "10px"})
                        ]),
                        width="auto"
                    )
                ], className="mt-2", justify="center")
            )
        return books

    elif algorithm == 'corr':
        books = []
        for _, row in recommendations.iterrows():
            books.append(
                dbc.Row([
                    dbc.Col(
                        html.Div([
                            html.Img(src=row['image_url'] if row['image_url'] is not None else placeholder_url , alt="Book cover", style={"width": "100px", "display": "block", "margin": "0 auto"}),
                            html.Div(row['book'], style={"textAlign": "center", "marginTop": "10px"})
                        ]),
                        width="auto"
                    )
                ], className="mt-2", justify="center")
            )
        return books

    else:
        return dbc.Alert("Invalid recommendation method selected.", color="danger")