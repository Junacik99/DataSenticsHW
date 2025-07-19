import pandas as pd

def assoc_rules(
    dataset: pd.DataFrame, 
    books_to_compare: pd.Index,
    book: str,
    min_lift: float = 2.0
) -> list:
    """
    Generate association rules for a given book.
    
    Parameters:
        dataset (pd.DataFrame): The dataset containing user ratings and book titles.
        books_to_compare (pd.Index): Index of books to compare against.
        book (str): The title of the book to find recommendations for.
        min_lift (float): Minimum lift for association rules.
        
    Returns:
        list: A list of recommended books based on association rules with lift above threshold.
    """
    from mlxtend.frequent_patterns import apriori, association_rules

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
        pd.DataFrame: DataFrame containing books correlated with the target book, sorted by correlation.
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


def content_based_recommendations(
    dataset: pd.DataFrame, 
    book: str,
) -> list:
    """
    Generate content-based recommendations for a given book.
    
    Parameters:
        dataset (pd.DataFrame): The dataset containing book titles, authors, and genres.
        book (str): The title of the book to find recommendations for.
        
    Returns:
        list: A list of tuples - recommended books based on content similarity.
    """
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    # Combine author and genres into a feature
    dataset['features'] = dataset['Book-Author'] + ' ' + dataset['genres']

    # Vectorize features
    count_vectorizer = CountVectorizer()
    feature_matrix  = count_vectorizer.fit_transform(dataset['features'])

    # Cosine similarity
    cosine_sim = cosine_similarity(feature_matrix)

    # Find the index of the book
    book_idx = dataset[dataset['Book-Title'] == book].index[0]

    # Find similar books
    similar_books = list(enumerate(cosine_sim[book_idx]))
    similar_books = sorted(similar_books, key=lambda x: x[1], reverse=True)

    # Exclude the book itself
    similar_books = [x for x in similar_books if x[0] != book_idx]

    return similar_books