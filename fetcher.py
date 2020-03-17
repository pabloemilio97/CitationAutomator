import docx
import scholarly

months = {
    '1': 'January',
    '2': 'February',
    '3': 'March',
    '4': 'April',
    '5': 'May',
    '6': 'June',
    '7': 'July',
    '8': 'August',
    '9': 'September',
    '10': 'October',
    '11': 'November',
    '12': 'December'
}

class PubCites:
    def __init__(self, pub, cites):
        self.pub = pub
        self.cites = cites

search_query = scholarly.search_author('Ruben Morales-Menendez')
author = next(search_query).fill()
pub_cites = []
start_from_pub = int(input('Start from pub: '))
start_from_cite = int(input('Start from cite: '))

with open('data.txt', 'a') as file:
    for pub_index, pub in enumerate(author.publications):
        if pub_index < start_from_pub:
            continue
        print(pub_index, pub.bib.get("title"))
        pub.fill()
        pub_citation_to_print = f"*PUB* author--{pub.bib.get('author')}-- title--{pub.bib.get('title')}-- journal--{pub.bib.get('journal')}-- volume--{pub.bib.get('volume')}-- number--{pub.bib.get('number')}-- pages--{pub.bib.get('pages')}-- publisher--{pub.bib.get('publisher')}-- month--{months[str(pub.bib.get('month'))] if pub.bib.get('month') else None}-- year--{pub.bib.get('year')}--"
        for cite_index, cite in enumerate(pub.get_citedby()):
            if pub_index == start_from_pub and cite_index < start_from_cite:
                continue
            print(cite_index, cite.bib.get("title"))
            cite.fill()
            cite_citation_to_print = f"*CITE* author--{cite.bib.get('author')}-- title--{cite.bib.get('title')}-- journal--{cite.bib.get('journal') if cite.bib.get('journal') else cite.bib.get('booktitle')}-- volume--{cite.bib.get('volume')}-- number--{cite.bib.get('number')}-- pages--{cite.bib.get('pages')}-- publisher--{cite.bib.get('publisher') if cite.bib.get('publisher') else cite.bib.get('organization')}-- year--{cite.bib.get('year')}--"
            file.write(cite_citation_to_print + '\n')
        file.write(pub_citation_to_print + '\n')
