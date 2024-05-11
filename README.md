# Local election results analysis
Scraping, querying, and visualisation of local election results from raw HTML, using Python, SQLite, and Tableau.

The local elections for Sheffield were held recently (2nd May 2024), and results published to the sheffield.gov.uk website.
https://www.sheffield.gov.uk/your-city-council/election-results
I decided it would be insightful to analyse the election results, to interrogate the data, and gain insights about the area. 
You can also perform your own analysis on the data with the results provided.

I used PyCharm, which has built-in SQLite console support for querying the data after scraping. requirements.txt included.
One thing to be aware of is only running the script once or you will have duplicates in your SQL database (this could be fixed with IF NOT EXISTS, but I wanted to keep the query simple).

# Usage
- Run Python script, election_results_scraping.py, with packages requirements.txt
- Open SQLite console and execute the queries (saved in txt files)
- Visualise


