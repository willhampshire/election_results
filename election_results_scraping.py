from bs4 import BeautifulSoup as bs
import html
import time
from icecream import ic
import sqlite3
import re

# put filepath to your extracted html .txt here (using .html as the extension does not work)
fpath_election_results = "sheffield_election_results.txt"

# define function to remove newline wrap char from web and replace with space
def clean(text: str) -> str:
    new_text = text.replace('\xa0', ' ') # a character is put in to identify where text is cut off before a new line
    return new_text

# open the raw html and unescape tags
with open(fpath_election_results, "r", encoding="utf-8") as file:
    election_results = html.unescape(file.read())

parsed_election_results = bs(election_results, 'html.parser')
#ic(parsed_election_results) # debug - has raw data been imported correctly

# create entries dict
entries = {}
no_h4_tags = 0 # debug variable

# Find all <p> tags with class "p1" that are siblings of <div> tags with class "field--name-localgov-text"
p_tags = parsed_election_results.find_all('div', class_='field--name-localgov-text')[0].find_next_siblings('p', class_='p1')
# create candidates dict
candidates_dict = {}

# iterate through the <p> tags found
for p_tag in p_tags:
    # Get constituency from the preceding <h4> tag
    h4_tags = p_tag.find_previous('div', class_='field--name-localgov-text').find_all('h4')
    #ic(h4_tags)

    # <h4> contains the constituency name
    if h4_tags:
        constituency_names = [clean(h4_tag.text.strip()) for h4_tag in h4_tags]
        for constituency_name in constituency_names:

            try: # create constituency key if not already exists
                candidates_dict[constituency_name] # attempt to access the key
            except KeyError as ke:
                #ic(ke)
                candidates_dict[constituency_name] = [] # create key

            try: # create constituency key if not already exists
                entries[constituency_name]
            except KeyError as ke:
                #ic(ke)
                entries[constituency_name] = {}
                try:
                    entries[constituency_name]["candidate"]
                except KeyError as ke2:
                    #ic(ke2)
                    entries[constituency_name]["candidate"] = []


            # Get candidate information from list tags <li> within the <p> tag
            li_tags = p_tag.find_all('li')
            for li_tag in li_tags:
                candidate_info_str = li_tag.text.strip().rsplit(',')
                # strip each element of info (split by commas) in candidate info list item
                candidate_info_split = [clean(can.strip()).replace(' votes', '') for can in candidate_info_str]
                candidate_info_dict = {"name": candidate_info_split[0], "party": candidate_info_split[1], "votes": int(candidate_info_split[2])}

                if candidate_info_dict not in candidates_dict[constituency_name]:
                    candidates_dict[constituency_name].append(candidate_info_dict)

                    entries[constituency_name]["candidate"] = candidates_dict[constituency_name]

            try:
                entries[constituency_name]["electorate"]
            except KeyError as ke:
                # ic(ke)
                entries[constituency_name]["electorate"] = {}

            # more <p> tags that contain electorate information rather than the candidates
            p_tags_2 = p_tag.find('p')
            if p_tags_2:
                electorate = p_tags_2.text.strip().replace('\xa0', ' ').replace('\n', ' ').rsplit('          ')
                #ic(electorate)
                #ic(len(electorate))

                # use regex patterns to get the information
                pattern_elected = r'Elected: (.*), (.*)'
                pattern_votes = r'Total votes: (\d*)'
                pattern_rej_ballots = r'Rejected ballots: (\d*)'
                pattern_electorate = r'Electorate: (\d*(?:\,\d*)?)'
                pattern_turnout = r'Turnout: (\d+(?:\.\d+)?)%'

                try: # extra p heading in firth park for multiple candidates throws exception. Append data manually.
                    match_elected = re.match(pattern_elected, electorate[0])
                    entries[constituency_name]["electorate"]["candidate"] = match_elected.group(1)
                    entries[constituency_name]["electorate"]["party"] = match_elected.group(2)

                    match_votes = re.match(pattern_votes, electorate[1])
                    entries[constituency_name]["electorate"]["votes"] = int(match_votes.group(1))

                    match_rej_ballots = re.match(pattern_rej_ballots, electorate[2])
                    entries[constituency_name]["electorate"]["rejected_ballots"] = int(match_rej_ballots.group(1))

                    match_electorate = re.match(pattern_electorate, electorate[3])
                    entries[constituency_name]["electorate"]["electorate_size"] = int(match_electorate.group(1).replace(',',''))

                    match_turnout = re.match(pattern_turnout, electorate[4])
                    entries[constituency_name]["electorate"]["turnout_pc"] = float(match_turnout.group(1))

                    #ic(entries[constituency_name]["electorate"]) # debug
                except AttributeError:
                    pass

    else:
        no_h4_tags += 1
        constituency_name = 'unknown'
        continue


#ic(no_h4_tags) # debug
#ic(entries)

# check the entries have been appended
for idx, entry in enumerate(entries, start=1):
    print(f"Entry {idx}: {entry}\n")

# make sqlite connection / create database, create tables, write results
conn = sqlite3.connect('election_results.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS candidates (
                    id INTEGER PRIMARY KEY,
                    constituency TEXT,
                    name TEXT,
                    party TEXT,
                    votes INTEGER
                  )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS electorates (
                    id INTEGER PRIMARY KEY,
                    constituency TEXT,
                    candidate TEXT,
                    electorate_size INTEGER,
                    party TEXT,
                    rejected_ballots INTEGER,
                    turnout_pc REAL,
                    votes INTEGER
                  )''')

# Insert data into the 'candidates' table
for constituency, data in entries.items():
    for candidate in data['candidate']:

        cursor.execute('''INSERT INTO candidates (constituency, name, party, votes)
                          VALUES (?, ?, ?, ?)''',
                       (constituency, candidate['name'], candidate['party'], candidate['votes']))

# Insert data into the 'electorates' table
for constituency, data in entries.items():

    try:
        electorate_data = data['electorate']
        cursor.execute('''INSERT INTO electorates (constituency, candidate, electorate_size, party, rejected_ballots, turnout_pc, votes)
                              VALUES (?, ?, ?, ?, ?, ?, ?)''',
                       (constituency, electorate_data['candidate'], electorate_data['electorate_size'],
                        electorate_data['party'], electorate_data['rejected_ballots'], electorate_data['turnout_pc'],
                        electorate_data['votes']))

    except KeyError as ke3: # problem where the constituency data was not found due to earlier error with multiple candidates for one constituency
        print(f"KeyError - {constituency} - {ke3}\nData not found.")
        continue


# Commit changes to database and close connection
conn.commit()
conn.close()