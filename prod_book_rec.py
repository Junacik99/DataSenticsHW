# TODO:
# - parametrize columns as well
# - use iterative load if the dataset would be too big

import click
import pandas as pd
import numpy as np




@click.command()
@click.option('-r', '--ratings_file', default='data/BX-Book-Ratings.csv', help='Path to the ratings CSV file.')
@click.option('-b', '--books_file', default='data/Books.csv', help='Path to the books CSV file.')
@click.option('-i', '--book', default='the fellowship of the ring (the lord of the rings, part 1)', help='Book title to find recommendations for.')
def main(ratings_file, books_file, book):
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

    # Create the pivot table directly, computing mean ratings
    dataset_for_corr = dataset[
        dataset['Book-Title'].isin(books_to_compare)
    ].pivot_table(
        index='User-ID',
        columns='Book-Title',
        values='Book-Rating',
        aggfunc='mean'
    )

    # Compute correlations for all other books with the target book
    correlations = dataset_for_corr.drop(columns=[book], errors='ignore').corrwith(dataset_for_corr[book])

    # Compute average ratings for all books at once
    avg_ratings = dataset.groupby('Book-Title')['Book-Rating'].mean()

    # Build the DataFrame
    correlated_books = pd.DataFrame({
        'book': correlations.index,
        'corr': correlations.values,
        'avg_rating': correlations.index.map(avg_ratings)
    })
    correlated_books = correlated_books.sort_values('corr', ascending=False)

    print(f"Recommendations for '{book}':")
    print(correlated_books.head(10))

if __name__ == '__main__':
    main()