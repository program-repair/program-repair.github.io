#!/usr/bin/env python3

import datetime
import os
from os.path import join, basename
import json
import rdflib
import xml.etree.ElementTree as ET
import urllib.request
import urllib.parse
import tqdm
import pystache
from operator import itemgetter
import csv
from collections import namedtuple


root_dir = os.path.dirname(os.path.realpath(__file__))

cache_dir = join(root_dir, "cache")

bibliography_file = join(root_dir, 'data', 'bibliography.csv')
tools_file = join(root_dir, 'data', 'tools.json')
benchmarks_file = join(root_dir, 'data', 'benchmarks.json')
analytics_file  = join(root_dir, 'analytics.txt')
meta_file = join(root_dir, 'meta.txt')

home_template_file = join(root_dir, 'templates', 'index.html')
bibliography_template_file = join(root_dir, 'templates', 'bibliography.html')
tools_template_file = join(root_dir, 'templates', 'tools.html')
benchmarks_template_file = join(root_dir, 'templates', 'benchmarks.html')
statistics_template_file = join(root_dir, 'templates', 'statistics.html')

home_output_file = join(root_dir, 'index.html')
bibliography_output_file = join(root_dir, 'bibliography.html')
tools_output_file = join(root_dir, 'tools.html')
benchmarks_output_file = join(root_dir, 'benchmarks.html')
statistics_output_file = join(root_dir, 'statistics.html')

dblp_schema = "https://dblp.org/rdf/schema"
rdf_syntax = "http://www.w3.org/1999/02/22-rdf-syntax-ns"
title_ref = rdflib.URIRef(dblp_schema + "#title")
primaryFullPersonName_ref = rdflib.URIRef(dblp_schema + "#primaryFullCreatorName")
publishedInBook_ref = rdflib.URIRef(dblp_schema + "#publishedInBook")
publishedInJournal_ref = rdflib.URIRef(dblp_schema + "#publishedInJournal")
publishedInJournalVolume_ref = rdflib.URIRef(dblp_schema + "#publishedInJournalVolume")
publishedInJournalVolumeIssue_ref = rdflib.URIRef(dblp_schema + "#publishedInJournalVolumeIssue")
yearOfPublication_ref = rdflib.URIRef(dblp_schema + "#yearOfPublication")
primaryElectronicEdition_ref = rdflib.URIRef(dblp_schema + "#primaryElectronicEdition")

# year -> num
publications_per_year = dict()

# venue -> num
publications_per_venue = dict()

# author_id -> (name, num)
publications_per_author = dict()

NUM_LAST_YEARS_PER_AUTHOR=4
# author_id -> (name, num)
publications_per_author_last_years = dict()

# year -> {...}
authors_per_year = dict()

# meta -> {...}, analytics -> {...}, papers -> [...], tools -> [...], benchmarks -> [...]
home = dict()
home['papers'] = []
home['tools'] = []
home['benchmarks'] = []

with open(tools_file) as f:
    tools_data = json.load(f)

top_tools = [tool['name'] for tool in tools_data[:3]]

tools_data = sorted(tools_data, key=itemgetter('name'))

tools = dict()
tools['tools'] = []

tool_targets = sorted(list(set([tool['target'] for tool in tools_data])))

for target in tool_targets:
    tools_entry = dict()
    tools_entry['target'] = target
    tools_entry['tools_for_target'] = []
    for tool in tools_data:
        if not (tool['target'] == target):
            continue
        tool['anchor'] = tool['name']
        tool['paper_link'] = tool['dblp'].replace('/', '_')
        tools_entry['tools_for_target'].append(tool)
        if tool['name'] in top_tools:
            home['tools'].append(tool)
    tools['tools'].append(tools_entry)

with open(benchmarks_file) as f:
    benchmarks_data = json.load(f)

top_benchmarks = [benchmark['name'] for benchmark in benchmarks_data[:3]]

benchmarks_data = sorted(benchmarks_data, key=itemgetter('name'))

benchmarks = dict()
benchmarks['benchmarks'] = []

benchmark_targets = sorted(list(set([benchmark['target'] for benchmark in benchmarks_data])))

for target in benchmark_targets:
    benchmarks_entry = dict()
    benchmarks_entry['target'] = target
    benchmarks_entry['benchmarks_for_target'] = []
    for benchmark in benchmarks_data:
        if not (benchmark['target'] == target):
            continue
        benchmark['anchor'] = benchmark['name']
        if 'dblp' in benchmark:
            benchmark['paper_link'] = benchmark['dblp'].replace('/', '_')
        benchmarks_entry['benchmarks_for_target'].append(benchmark)
        if benchmark['name'] in top_benchmarks:
            home['benchmarks'].append(benchmark)
    benchmarks['benchmarks'].append(benchmarks_entry)


print("fetching data from dblp")

# year -> list of publications
bib = dict()

BibItem = namedtuple('BibItem', ['key', 'venue'])

bib_items = []

with open(bibliography_file) as csvfile:
    spamreader = csv.reader(csvfile)
    for row in spamreader:
        bib_items.append(BibItem(row[0], row[1]))

top_papers = [item.key for item in bib_items[:6]]

for bib_item in tqdm.tqdm(bib_items):
    entry = dict()
    rdf_xml_url = "https://dblp.org/rec/rdf/{}.rdf".format(bib_item.key)
    rdf_xml_file = join(cache_dir, bib_item.key.replace('/', '_') + ".rdf")
    if not os.path.isfile(rdf_xml_file):
        urllib.request.urlretrieve(rdf_xml_url, rdf_xml_file)
    with open(rdf_xml_file) as f:
        data = f.read()
    paper_graph = rdflib.Graph()
    paper_graph.parse(data=data, format='xml')
    title = list(paper_graph.objects(None, title_ref))[0].rstrip('.')
    yearOfPublication = list(paper_graph.objects(None, yearOfPublication_ref))[0]
    if yearOfPublication not in publications_per_year:
        publications_per_year[yearOfPublication] = 0
    publications_per_year[yearOfPublication] += 1
    book_results = list(paper_graph.objects(None, publishedInBook_ref))
    if len(book_results) > 0:
        venue = book_results[0]
        venue_details = yearOfPublication
    else:
        journal = list(paper_graph.objects(None, publishedInJournal_ref))[0]
        volume = list(paper_graph.objects(None, publishedInJournalVolume_ref))[0]
        venue = journal
        venue_details = volume
        issue_results = list(paper_graph.objects(None, publishedInJournalVolumeIssue_ref))
        if len(issue_results) > 0:
            venue_details = venue_details + " (" + issue_results[0] + ")"
        venue_details = venue_details + " " + yearOfPublication
    if bib_item.venue:
        venue_id = bib_item.venue
    else:
        venue_id = str(venue)
    venue_short_id = {
        "SIGSOFT FSE": "FSE",
        "ESEC/SIGSOFT FSE": "FSE",
        "CAV (1)": "CAV",
        "CAV (2)": "CAV",
        "ACM Trans. Softw. Eng. Methodol.": "TOSEM",
        "IEEE Symposium on Security and Privacy": "S&P",
        "IEEE Trans. Software Eng.": "TSE",
        "Empirical Software Engineering": "EMSE",
        "Empir. Softw. Eng.": "EMSE",
        "ICSE (1)": "ICSE",
        "Proc. ACM Program. Lang. 3 (OOPSLA)": "OOPSLA",
        "Proc. ACM Program. Lang. 3 (POPL)": "POPL",
        "Sci. China Inf. Sci.": "SCI",
        "Proc. ACM Program. Lang. 2 (OOPSLA)": "OOPSLA"
    }
    if venue_id in venue_short_id:
        venue_id = venue_short_id[venue_id]
    if venue_id not in publications_per_venue:
        publications_per_venue[venue_id] = 0
    publications_per_venue[venue_id] += 1
    primaryElectronicEdition = list(paper_graph.objects(None, primaryElectronicEdition_ref))[0]
    entry['title'] = title
    entry['anchor'] = bib_item.key.replace('/', '_')
    entry['scholar'] = "https://scholar.google.com/scholar?q={}".format(title.replace(' ', '+'))
    entry['bibtex'] = "http://dblp.org/rec/bibtex/{}".format(bib_item.key)
    
    # using xml parser because rdflib is not order-preserving
    root = ET.fromstring(data)
    publication = root.find("{" + dblp_schema + "#}Inproceedings")
    if not publication:
        publication = root.find("{" + dblp_schema + "#}Article")
    authors_nodes = publication.findall("{" + dblp_schema + "#}authoredBy")
    authors_uris = [n.attrib["{" + rdf_syntax + "#}resource"] for n in authors_nodes]
    authors = []
    if yearOfPublication not in authors_per_year:
        authors_per_year[yearOfPublication] = set()
    for author_uri in authors_uris:
        disassembled = urllib.parse.urlparse(author_uri)
        if str(disassembled.path) not in authors_per_year[yearOfPublication]:
            authors_per_year[yearOfPublication].add(str(disassembled.path))
        author_file = join(cache_dir, basename(disassembled.path).replace(':','_') + ".rdf")
        if not os.path.isfile(author_file):
            urllib.request.urlretrieve(author_uri + ".rdf", author_file)
        with open(author_file) as f:
            author_data = f.read()
        author_graph = rdflib.Graph()
        author_graph.parse(data=author_data, format='xml')
        name = list(author_graph.objects(None, primaryFullPersonName_ref))[0]
        authors.append(name.toPython())
        if str(disassembled.path) not in publications_per_author:
            publications_per_author[str(disassembled.path)] = (name, 0)
        (n, p) = publications_per_author[str(disassembled.path)]
        publications_per_author[str(disassembled.path)] = (n, p+1)
        if int(yearOfPublication) >= datetime.datetime.now().year - NUM_LAST_YEARS_PER_AUTHOR:
            if str(disassembled.path) not in publications_per_author_last_years:
                publications_per_author_last_years[str(disassembled.path)] = (name, 0)
            (n, p) = publications_per_author_last_years[str(disassembled.path)]
            publications_per_author_last_years[str(disassembled.path)] = (n, p+1)


    authors_str = authors[0]
    for a in authors[1:]:
        authors_str = authors_str + ", " + a

    entry['key'] = bib_item.key
    entry['authors'] = authors_str.encode('ascii', 'xmlcharrefreplace').decode()
    entry['venue'] = venue_id
    entry['venue_details'] = venue_details
    entry['year'] = yearOfPublication
    entry['url'] = primaryElectronicEdition

    for tool in tools_data:
        if tool['dblp'] == bib_item.key:
            entry['tool'] = tool['name']
            break

    for benchmark in benchmarks_data:
        if 'dblp' in benchmark and benchmark['dblp'] == bib_item.key:
            entry['benchmark'] = benchmark['name']
            break
        
    if not (yearOfPublication in bib):
        bib[yearOfPublication] = []
    bib[yearOfPublication].append(entry)
    if entry['key'] in top_papers:
        home['papers'].append(entry)

bibliography = dict()
bib_list = []
sorted_years = sorted(bib.keys(), reverse=True)
for year in sorted_years:
    papers = bib[year]
    sorted_by_title = sorted(papers, key=itemgetter('title'))    
    sorted_by_venue = sorted(sorted_by_title, key=itemgetter('venue'))
    bib_list.append({ 'year': year, 'papers': sorted_by_venue })
bibliography['bibliography'] = bib_list

statistics = dict()
all_years = sorted(publications_per_year.keys())
all_authors = set()

NUM_TOP_VENUES=10
NUM_TOP_AUTHORS=10

top_venues = list(k for (k,v) in sorted(publications_per_venue.items(), key=itemgetter(1), reverse=True)[:NUM_TOP_VENUES])
top_authors_ids = list(k for (k,v) in sorted(publications_per_author.items(), key=(lambda x: x[1][1]), reverse=True)[:NUM_TOP_AUTHORS])
top_authors_last_years_ids = \
    list(k for (k,v) in sorted(publications_per_author_last_years.items(), key=(lambda x: x[1][1]), reverse=True))
top_authors_names = []
for id in top_authors_ids:
    top_authors_names.append(publications_per_author[id][0])
top_authors_last_years = []
for id in top_authors_last_years_ids:
    top_authors_last_years.append(publications_per_author_last_years[id])

with open('top_authors_last_years.csv', 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile)
    for (author, num_publications) in top_authors_last_years:
        spamwriter.writerow([author, num_publications])

statistics["publicationsPerYear_X"] = ",".join(all_years)
statistics["authorsPerYear_X"] = ",".join(all_years)
statistics["newAuthorsPerYear_X"] = ",".join(all_years)
statistics["publicationsPerAuthor_X"] = ",".join("\"" + venue + "\"" for venue in top_authors_names)
statistics["publicationsPerVenue_X"] = ",".join("\"" + venue + "\"" for venue in top_venues)
num_publications_per_year = []
num_publications_per_venue = []
num_publications_per_author = []
for year in all_years:
    num_publications_per_year.append(str(publications_per_year[year]))
for venue in top_venues:
    num_publications_per_venue.append(str(publications_per_venue[venue]))
for id in top_authors_ids:
    num_publications_per_author.append(str(publications_per_author[id][1]))
for year in all_years:
    num_publications_per_year.append(str(publications_per_year[year]))
num_new_authors_per_year = []
num_authors_per_year = []
for year in all_years:
    num_authors_per_year.append(str(len(authors_per_year[year])))
for year in all_years:
    num_new_authors_per_year.append(str(len(authors_per_year[year].difference(all_authors))))
    all_authors |= authors_per_year[year]
statistics["publicationsPerYear_Y"] = ",".join(num_publications_per_year)
statistics["publicationsPerAuthor_Y"] = ",".join(num_publications_per_author)
statistics["publicationsPerVenue_Y"] = ",".join(num_publications_per_venue)
statistics["authorsPerYear_Y"] = ",".join(num_authors_per_year)
statistics["newAuthorsPerYear_Y"] = ",".join(num_new_authors_per_year)


print("generating html")

renderer = pystache.Renderer()

with open(bibliography_template_file, 'r') as file:
    bibliography_template = file.read()
with open(bibliography_output_file, 'w') as file:
    file.write(renderer.render(bibliography_template, bibliography))

with open(tools_template_file, 'r') as file:
    tools_template = file.read()
with open(tools_output_file, 'w') as file:
    file.write(renderer.render(tools_template, tools))

with open(benchmarks_template_file, 'r') as file:
    benchmarks_template = file.read()
with open(benchmarks_output_file, 'w') as file:
    file.write(renderer.render(benchmarks_template, benchmarks))

with open(home_template_file, 'r') as file:
    home_template = file.read()
with open(meta_file, 'r') as file:
    home['meta'] = file.read()
with open(analytics_file, 'r') as file:
    home['analytics'] = file.read()
with open(home_output_file, 'w') as file:
    file.write(pystache.render(home_template, home))

with open(statistics_template_file, 'r') as file:
    statistics_template = file.read()
with open(statistics_output_file, 'w') as file:
    file.write(renderer.render(statistics_template, statistics))
