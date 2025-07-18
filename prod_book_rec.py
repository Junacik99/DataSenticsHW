# TODO:
# - parametrize columns as well
# - use iterative load if the dataset would be too big

import click
import pandas as pd
import numpy as np
from mlxtend.frequent_patterns import apriori, association_rules

def assoc_rules(
    dataset: pd.DataFrame, 
    books_to_compare: pd.Index,
    book: str,
    min_lift: float = 2.0
) -> pd.DataFrame:
    """
    Generate association rules for a given book.
    
    Parameters:
        dataset (pd.DataFrame): The dataset containing user ratings and book titles.
        books_to_compare (pd.Index): Index of books to compare against.
        book (str): The title of the book to find recommendations for.
        min_support (float): Minimum support for frequent itemsets.
        min_lift (float): Minimum lift for association rules.
        
    Returns:
        list: A list of recommended books based on association rules with lift above threshold.
    """
    # Create a binary matrix: 1 if user rated the book, 0 otherwise
    user_book_matrix = dataset[
        dataset['Book-Title'].isin(books_to_compare)
    ].pivot_table(
        index='User-ID',
        columns='Book-Title',
        values='Book-Rating',
        aggfunc=lambda x: 1 if len(x) > 0 else 0
    ).fillna(0).astype(bool)

    # Find frequent itemsets
    frequent_itemsets = apriori(user_book_matrix, min_support=0.05, use_colnames=True)

    # Generate association rules
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=min_lift)

    # Filter rules where the target book is in the antecedents
    target_rules = rules[rules['antecedents'].apply(lambda x: book in x)]
    target_rules = target_rules[['consequents', 'support', 'confidence', 'lift']].sort_values('lift', ascending=False)
    
    # Get list of distinct consequents (recommended books)
    distinct_books = target_rules['consequents'].explode().unique()

    # Return recommended books (consequents) with lift > threshold
    return distinct_books


def corr_recommendations(
    dataset: pd.DataFrame, 
    books_to_compare: pd.Index,
    book: str
) -> pd.DataFrame:
    """
    Generate recommendations based on correlation with a given book.
    
    Parameters:
        dataset (pd.DataFrame): The dataset containing user ratings and book titles.
        books_to_compare (pd.Index): Index of books to compare against.
        book (str): The title of the book to find recommendations for.
        
    Returns:
        None: Prints the top correlated books.
    """
    # Create the pivot table directly, computing mean ratings
    user_book_matrix = dataset[
        dataset['Book-Title'].isin(books_to_compare)
    ].pivot_table(
        index='User-ID',
        columns='Book-Title',
        values='Book-Rating',
        aggfunc='mean'
    )

    # Compute correlations for all other books with the target book
    correlations = user_book_matrix.drop(columns=[book], errors='ignore').corrwith(user_book_matrix[book])

    # Compute average ratings for all books at once
    avg_ratings = dataset.groupby('Book-Title')['Book-Rating'].mean()

    # Build the DataFrame
    correlated_books = pd.DataFrame({
        'book': correlations.index,
        'corr': correlations.values,
        'avg_rating': correlations.index.map(avg_ratings)
    })
    
    return correlated_books.sort_values('corr', ascending=False)


@click.command()
@click.option('-r', '--ratings_file', default='data/BX-Book-Ratings.csv', help='Path to the ratings CSV file.')
@click.option('-b', '--books_file', default='data/Books.csv', help='Path to the books CSV file.')
@click.option('-i', '--book', default='the fellowship of the ring (the lord of the rings, part 1)', help='Book title to find recommendations for.')
@click.option('-m', '--method', default='assoc', type=click.Choice(['assoc', 'corr'], case_sensitive=False), help='Method for recommendations: "assoc" for association rules or "corr" for correlation-based.')
def main(ratings_file, books_file, book, method):
    # Toad dataset
    ratings = pd.read_csv(ratings_file, encoding='cp1251', sep=';')
    ratings = ratings[ratings['Book-Rating']!=0]
    books = pd.read_csv(
        books_file,  
        encoding='cp1251', 
        sep=',', 
        on_bad_lines='skip', 
        low_memory=False,
        usecols=['ISBN', 'Book-Title', 'Book-Author']
        )
    dataset = pd.merge(ratings, books, on=['ISBN']).apply(
        # To lowercase
        lambda x: x.str.lower() if x.dtype == 'object' and all(isinstance(val, str) for val in x.dropna()) else x
    )
    
    # Check if the book exists in the dataset
    if book.lower() not in dataset['Book-Title'].str.lower().values:
        print(f"Book '{book}' not found in the dataset.")
        return

    # Filter dataset based on the readers of the book
    book_readers = dataset['User-ID'][dataset['Book-Title'] == book].to_list()
    book_readers = np.unique(book_readers)    
    dataset = dataset[dataset['User-ID'].isin(book_readers)]

    # Find books with at least 8 ratings
    book_counts = dataset['Book-Title'].value_counts()
    books_to_compare = book_counts[book_counts >= 8].index

    if method == 'assoc':
        # Use association rules to find recommendations
        recommendations = assoc_rules(dataset, books_to_compare, book)
        print(f"Association rule recommendations for '{book}':")
        print(recommendations)
        return
    elif method == 'corr':
        # Use correlation to find recommendations
        recommendations = corr_recommendations(dataset, books_to_compare, book)
        print(f"Correlation-based recommendations for '{book}':")
        print(recommendations.head(10))
        return
    else:
        print("Invalid method specified. Use 'assoc' for association rules or 'corr' for correlation-based recommendations.")
        return




if __name__ == '__main__':
    main()