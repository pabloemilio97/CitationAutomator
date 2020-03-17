from unidecode import unidecode
from fuzzywuzzy import fuzz
import functools

months = ['None', 'January', 'February', 'March', 'April', 'May', 'June', 'July',
    'August', 'September', 'October', 'November', 'December']
months_values = dict(zip(months, [x for x in range(13)]))

def fill_bib(object, values):
    for i, x in enumerate(values):
        if i % 2 != 0:
            object.bib[values[i - 1].replace(' ', '')] = values[i]

def standardize_authors(authors_str):
    authors = authors_str.split(' and ')
    for i, author in enumerate(authors):
        comma = author.find(',')
        if comma is not -1:
            authors[i] = author[comma + 2:] + ' ' + author[:comma]
    return authors

def fuzzy_in(query, arr):
    def matches(x, y=unidecode(query)):
        return fuzz.ratio(x, y) > 70
    ascii_arr = map(unidecode, arr)
    return any(map(matches, ascii_arr))

def concat_and(acum, x):
    return acum + ' and ' + x

def by_date(articles):
    by_date = dict()
    for article in articles:
        year = int(article.bib['year']) if article.bib['year'] != 'None' else 0
        month = months_values[article.bib['month']]
        if (year, month) not in by_date:
            by_date[(year, month)] = []
        by_date[(year, month)].append(article)
    return by_date

def by_year(articles):
    by_year = dict()
    for article in articles:
        year = int(article.bib['year']) if article.bib['year'] != 'None' else 0
        if year not in by_year:
            by_year[year] = []
        by_year[year].append(article)
    return by_year

def pubs_in_year(pubs_by_date, year):
    count = 0
    for y, m in pubs_by_date:
        if year == y:
            count += len(pubs_by_date[(y, m)])
    return count

class Pub:
    def __init__(self, pub):
        self.bib = dict()
        fill_bib(self, pub.split('--'))
        self.cites_a = []
        self.cites_b = []
        self.cites = []
        self.authors = standardize_authors(self.bib['author'])
        self.bib['author'] = functools.reduce(concat_and, self.authors)

    def cite(self, pub_id):
        citation = pub_id + ' '
        for key in self.bib:
            if self.bib[key] != 'None':
                if key == 'volume':
                    citation += 'Volume '
                elif key == 'number':
                    citation += 'Issue '
                elif key == 'pages':
                    citation += 'Pages '
                citation += f"{self.bib[key]}, "
                if key == 'month':
                    citation = citation[:-2] + ' '
        return citation[:-2] + '.'


class Cite:
    def __init__(self, cite):
        self.bib = dict()
        fill_bib(self, cite.split('--'))
        self.authors = standardize_authors(self.bib['author'])
        self.bib['author'] = functools.reduce(concat_and, self.authors)
        self.type = ""

    def determine_type(self, pub):
        exclution = 'Ruben Morales-Menendez'
        cite_authors = self.authors
        if fuzzy_in(exclution, self.authors):
            self.type = 'c'
        else:
            for author in pub.authors:
                if fuzzy_in(author, self.authors):
                    self.type = 'b'
                    return
            self.type = 'a'

    def cite(self, pub_id, cite_id):
        citation = f"{pub_id}_{cite_id} "
        for key in self.bib:
            if self.bib[key] != 'None':
                if key == 'volume':
                    citation += 'Volume '
                elif key == 'number':
                    citation += 'Issue '
                elif key == 'pages':
                    citation += 'Pages '
                citation += f"{self.bib[key]}, "
        return citation[:-2] + '.'



cites = []
pubs = []

with open('sanitized.txt', 'r') as file:
    for line in file:
        start = line.find(' ')
        if '*CITE*' in line:
            cite = Cite(line[start:])
            cites.append(cite)
        elif '*PUB*' in line:
            pub = Pub(line[start:])

            for cite in cites[:]:
                cite.determine_type(pub)
                if cite.type is 'a':
                    pub.cites_a.append(cite)
                elif cite.type is 'b':
                    pub.cites_b.append(cite)

            cites = []
            pubs.append(pub)

pubs_by_date = by_date(pubs)
for key in pubs_by_date:
    for pub in pubs_by_date[key]:
        pub.cites_a = by_year(pub.cites_a)
        pub.cites_b = by_year(pub.cites_b)

diff_years = [0] + [x for x in range(1980,2021)]
pubs_in_year = dict(zip(diff_years, [pubs_in_year(pubs_by_date, x) for x in diff_years]))
pubs_processed_in_year = dict(zip(diff_years, [0 for x in diff_years]))

with open('conacyt_citas.txt', 'a') as file:
    for pub_date in sorted(pubs_by_date.keys(), reverse=True):
        for pub in pubs_by_date[pub_date]:
            y, m = pub_date
            pub_id = f"{pub.bib['year']}_{pubs_in_year[y] - pubs_processed_in_year[y]}"
            pubs_processed_in_year[y] += 1
            file.write(pub.cite(pub_id) + '\n')

            file.write('\t' + 'Citas tipo A' + '\n')
            for year in sorted(pub.cites_a.keys(), reverse=True):
                count_cites_a = 0
                for cite in pub.cites_a[year]:
                    count_cites_a += 1
                for i, cite in enumerate(pub.cites_a[year]):
                    cite_id = f"{year}_{count_cites_a - i}"
                    file.write('\t\t' + cite.cite(pub_id, cite_id) + '\n')

            file.write('\t' + 'Citas tipo B' + '\n')
            for year in sorted(pub.cites_b.keys(), reverse=True):
                count_cites_b = 0
                for cite in pub.cites_b[year]:
                    count_cites_b += 1
                for i, cite in enumerate(pub.cites_b[year]):
                    cite_id = f"{year}_{count_cites_b - i}"
                    file.write('\t\t' + cite.cite(pub_id, cite_id) + '\n')
            file.write('\n')
