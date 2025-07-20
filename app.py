# app.py
# This file sets up the Dash application for book recommendations.
# It includes the layout and callback functions to handle user interactions.
# And prints the recommendations based on the selected method.

from dash import dcc, html, Output, Input, State, Dash
import dash_bootstrap_components as dbc
from src.prod_book_rec import recommend
from src.app_utils import create_layout, process_recommendations


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