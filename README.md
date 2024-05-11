# Local election results analysis
Scraping, querying, and visualisation of local election results from raw HTML, using Python, SQLite, and Tableau.

The local elections for Sheffield were held recently (2nd May 2024), and results published to the sheffield.gov.uk website.
https://www.sheffield.gov.uk/your-city-council/election-results
I decided it would be insightful to analyse the election results, to interrogate the data, and gain insights about the area. 
You can also perform your own analysis on the data with the results provided.

I used PyCharm, which has built-in SQLite console support for querying the data after scraping. requirements.txt included.
One thing to be aware of is only running the script once or you will have duplicates in your SQL database (this could be fixed with IF NOT EXISTS, but I wanted to keep the query simple).

# Preparation
To run the script on the raw html, I recommend copying and pasting the HTML source of the website to a .txt, then deleting any unnecesary info (I chose to only analyse 2024 results, so script will not handle the other years and may get confused). Manually encompass the results in a div (place <div> at the beginning and </div> at the end of the txt) so that bettersoup can identify this as the parent tag, and search between child/sibling tags inside this. This can now be saved and file path copied into the script.

# Usage
- Run Python script election_results_scraping.py, on sheffield_election_results.txt, with packages from requirements.txt
- Open SQLite console and execute the queries (saved in txt files named ..._query.txt)
- Visualise

# Output data notes
Where there is only one candidate running for a party, they are both the most and least voted for candidate in their party.
Field names are not present on the output CSV files.

You may also be able to just download the database election_results.db and query that using your SQL flavour of choice.

![Example visualisation of total party votes](https://github.com/willhampshire/election_results/blob/main/total_party_votes_bubbles.png?raw=true)
