import click
import pandas as pd





@click.command()
@click.option('-r', '--ratings_file', default='data/BX-Book-Ratings.csv', help='Path to the ratings CSV file.')
@click.option('-b', '--books_file', default='data/BX-Books.csv', help='Path to the books CSV file.')
@click.option('-i', '--book', default='the fellowship of the ring (the lord of the rings, part 1)', help='Book title to find recommendations for.')
def main(ratings_file, books_file, book):
    # load dataset
    ratings = pd.read_csv(ratings_file, encoding='cp1251', sep=';')
    ratings = ratings[ratings['Book-Rating']!=0]
    books = pd.read_csv(books_file,  encoding='cp1251', sep=';',on_bad_lines='skip')
    dataset = pd.merge(ratings, books, on=['ISBN']).apply(
        # to lowercase
        lambda x: x.str.lower() if x.dtype == 'object' and all(isinstance(val, str) for val in x.dropna()) else x
    )
    



if __name__ == '__main__':
    main()