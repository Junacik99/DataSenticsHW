from dash import dcc, html, Output, Input, State, Dash
import dash_bootstrap_components as dbc
from prod_book_rec import recommend


def create_layout(app):
    return html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col(html.H1(app.title), className="text-center mb-4")
            ], justify="center"),
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
            dbc.Row([
                dbc.Col(
                    html.Ul(id='results-output', className="mt-4"),
                )
            ])
        ])
    ])


def process_recommendations(recommendations, algorithm):
    if algorithm == 'cb':
        return recommendations
    
    elif algorithm == 'corr':
        return recommendations.to_json()
    
    elif algorithm == 'assoc':
        return recommendations
    else:
        return dbc.Alert("Invalid recommendation method selected.", color="danger")


def main():
    app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

    @app.callback(
        Output('results-output', 'children'),
        Input('search-button', 'n_clicks'),
        State('book-input', 'value'),
        State('algorithm-dropdown', 'value')
    )
    def handle_search(n_clicks, book_title, algorithm):
        if not n_clicks:
            return ""
        if not book_title:
            return dbc.Alert("Please enter a book title.", color="warning")
        
        # Recommendation logic
        books_file = 'data/goodreads.csv' if algorithm == 'cb' else 'data/Books.csv' 
        try:
            recommendations = recommend(
                ratings_file='data/BX-Book-Ratings.csv', 
                books_file=books_file, 
                book=book_title, 
                method=algorithm
            )

            result = process_recommendations(recommendations, algorithm)
            return result
        except Exception as e:
            return dbc.Alert(f"An error occurred: {str(e)}", color="danger")

    app.title = 'Book Recommendations'
    app.layout = create_layout(app)

    app.run(debug=True)


if __name__ == '__main__':
    main()