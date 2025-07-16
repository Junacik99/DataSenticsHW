# DataSenticsHW
Martin Takács

## Code Review
file: book_rec.py
- DS path and book list (*LoR_list*) should be parametrized
- *error_bad_lines* is deprecated and should be replaced with *on_bad_lines = 'skip'*
- code should not contain unnecessary lines/comments (user ratings)
- check if value is string before trying to lowercase it
    - attribute 'Year of Publication' was lost due to the error
- variable naming: *tolkein_readers* are actually readers of the LOTR 1
- what if the *books_to_compare* was empty?
    - error on drop empty result
- there's no need to do count aggregation on every column, counting users is sufficient
- after the count aggregation, *User ID* attribute no longer stands for the ID, but the count of IDs (naming)
- *dataset_for_corr* might be too wide
- if *LoR_book* is not specified/undefined -> error
