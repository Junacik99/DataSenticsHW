# TODO:
# - parametrize columns as well
# - use iterative load if the dataset would be too big

import click
import pandas as pd
import numpy as np
from rec_methods import assoc_rules, corr_recommendations, content_based_recommendations

def recommend(
    ratings_file, 
    books_file, 
    book, 
    method,
    top_n=10
    ):
    """
    Recommend books based on the specified method.

    Parameters:
        ratings_file (str): Path to the ratings CSV file.
        books_file (str): Path to the books CSV file.
        book (str): Title of the book to find recommendations for.
        method (str): Method for recommendations ('assoc', 'corr', 'cb').

    Returns:
        None: Prints recommendations to the console.
    """
    # Load dataset
    ratings = pd.read_csv(ratings_file, encoding='cp1251', sep=';')
    ratings = ratings[ratings['Book-Rating']!=0]
    books = pd.read_csv(
        books_file,  
        encoding='cp1251', 
        sep=',', 
        on_bad_lines='skip', 
        low_memory=False,
        usecols=['ISBN', 'Book-Title', 'Book-Author', 'genres'] if method == 'cb' else ['ISBN', 'Book-Title', 'Book-Author']
        )
    # Include ratings in the dataset if method is not Content-Based
    dataset = books if method == 'cb' else pd.merge(ratings, books, on=['ISBN'])
    dataset = dataset.apply(
        # To lowercase
        lambda x: x.str.lower() if x.dtype == 'object' and all(isinstance(val, str) for val in x.dropna()) else x
    )

    
    # Check if the book exists in the dataset
    book = book.lower()
    if book not in dataset['Book-Title'].values:
        print(f"Book '{book}' not found in the dataset.")
        raise ValueError(f"Book '{book}' not found in the dataset.")
    
    # if (method == 'corr' or method == 'assoc') and :
    
    if method == 'cb':
        # Get content-based recommendations
        similar_books = content_based_recommendations(dataset, book)

        # Display top recommendations
        print(f"Content-based recommendations for '{book}':")
        recommendations = [dataset.iloc[idx]['Book-Title'] for idx, _ in similar_books[:top_n]]
        for idx, score in similar_books[:top_n]:
            print(f"- {dataset.iloc[idx]['Book-Title']} (Score: {score:.2f})")
        
        return recommendations

    ## If method is not 'cb', proceed with collaborative filtering methods ##

    # Filter dataset based on the readers of the book
    book_readers = dataset['User-ID'][dataset['Book-Title'] == book].to_list()
    book_readers = np.unique(book_readers)    
    dataset = dataset[dataset['User-ID'].isin(book_readers)]

    # Find books with at least 8 ratings
    book_counts = dataset['Book-Title'].value_counts()
    books_to_compare = book_counts[book_counts >= 8].index

    if books_to_compare.empty:
        raise Exception("No books with sufficient ratings to compare.")

    if method == 'assoc':
        # Use association rules to find recommendations
        recommendations = assoc_rules(dataset, books_to_compare, book)
        print(f"Association rule recommendations for '{book}':")
        print(recommendations[:top_n])
        return recommendations
    
    elif method == 'corr':
        # Use correlation to find recommendations
        recommendations = corr_recommendations(dataset, books_to_compare, book)
        print(f"Correlation-based recommendations for '{book}':")
        print(recommendations.head(top_n))
        return recommendations
    
    else:
        print("Invalid method specified. Use 'assoc' for association rules or 'corr' for correlation-based recommendations.")
        return

@click.command()
@click.option('-r', '--ratings_file', default='data/BX-Book-Ratings.csv', help='Path to the ratings CSV file.')
@click.option('-b', '--books_file', default='data/Books.csv', help='Path to the books CSV file.')
@click.option('-i', '--book', default='the fellowship of the ring (the lord of the rings, part 1)', help='Book title to find recommendations for.')
@click.option('-m', '--method', default='assoc', type=click.Choice(['assoc', 'corr', 'cb'], case_sensitive=False), help='Method for recommendations: "assoc" for association rules or "corr" for correlation-based.')
@click.option('-n', '--top_n', default=10, help='Number of top recommendations to display.')
def main(
    ratings_file, 
    books_file, 
    book, 
    method,
    top_n
    ):
    recommend(
        ratings_file=ratings_file, 
        books_file=books_file, 
        book=book, 
        method=method,
        top_n=top_n
    )


if __name__ == '__main__':
    main()