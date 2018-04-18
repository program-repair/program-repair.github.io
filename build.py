#!/usr/bin/env python3

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


root_dir = os.path.dirname(os.path.realpath(__file__))

cache_dir = join(root_dir, "cache")

bibliography_file = join(root_dir, 'data', 'bibliography.txt')
tools_file = join(root_dir, 'data', 'tools.json')
benchmarks_file = join(root_dir, 'data', 'benchmarks.json')
analytics_file  = join(root_dir, 'analytics.txt')
meta_file = join(root_dir, 'meta.txt')

home_template_file = join(root_dir, 'templates', 'index.html')
bibliography_template_file = join(root_dir, 'templates', 'bibliography.html')
tools_template_file = join(root_dir, 'templates', 'tools.html')
benchmarks_template_file = join(root_dir, 'templates', 'benchmarks.html')

home_output_file = join(root_dir, 'index.html')
bibliography_output_file = join(root_dir, 'bibliography.html')
tools_output_file = join(root_dir, 'tools.html')
benchmarks_output_file = join(root_dir, 'benchmarks.html')

dblp_schema = "https://dblp.org/rdf/schema-2017-04-18"
rdf_syntax = "http://www.w3.org/1999/02/22-rdf-syntax-ns"
title_ref = rdflib.URIRef(dblp_schema + "#title")
pageNumbers_ref = rdflib.URIRef(dblp_schema + "#pageNumbers")
primaryFullPersonName_ref = rdflib.URIRef(dblp_schema + "#primaryFullPersonName")
publishedInBook_ref = rdflib.URIRef(dblp_schema + "#publishedInBook")
publishedInJournal_ref = rdflib.URIRef(dblp_schema + "#publishedInJournal")
publishedInJournalVolume_ref = rdflib.URIRef(dblp_schema + "#publishedInJournalVolume")
publishedInJournalVolumeIssue_ref = rdflib.URIRef(dblp_schema + "#publishedInJournalVolumeIssue")
yearOfPublication_ref = rdflib.URIRef(dblp_schema + "#yearOfPublication")
primaryElectronicEdition_ref = rdflib.URIRef(dblp_schema + "#primaryElectronicEdition")

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

with open(bibliography_file) as f:
    dblp_keys = [x.strip() for x in f.readlines()]

top_papers = dblp_keys[:6]

for key in tqdm.tqdm(dblp_keys):
    entry = dict()
    rdf_xml_url = "https://dblp.org/rec/rdf/{}.rdf".format(key)
    rdf_xml_file = join(cache_dir, key.replace('/', '_') + ".rdf")
    if not os.path.isfile(rdf_xml_file):
        urllib.request.urlretrieve(rdf_xml_url, rdf_xml_file)
    with open(rdf_xml_file) as f:
        data = f.read()
    paper_graph = rdflib.Graph()
    paper_graph.parse(data=data, format='xml')
    title = list(paper_graph.objects(None, title_ref))[0].rstrip('.')
    if len(list(paper_graph.objects(None, pageNumbers_ref))) > 0:
        pageNumbers = list(paper_graph.objects(None, pageNumbers_ref))[0]
    else:
        pageNumbers = ""
    yearOfPublication = list(paper_graph.objects(None, yearOfPublication_ref))[0]
    book_results = list(paper_graph.objects(None, publishedInBook_ref))
    if len(book_results) > 0:
        venue = book_results[0]
        if pageNumbers == "":
            venue_details = yearOfPublication
        else:
            venue_details = yearOfPublication + ": " + pageNumbers
    else:
        journal = list(paper_graph.objects(None, publishedInJournal_ref))[0]
        volume = list(paper_graph.objects(None, publishedInJournalVolume_ref))[0]
        venue = journal
        venue_details = volume
        issue_results = list(paper_graph.objects(None, publishedInJournalVolumeIssue_ref))
        if len(issue_results) > 0:
            venue_details = venue_details + "(" + issue_results[0] + ")"
        if pageNumbers == "":
            venue_details = venue_details + " (" + yearOfPublication + ")"
        else:
            venue_details = venue_details + ": " + pageNumbers + " (" + yearOfPublication + ")"
    primaryElectronicEdition = list(paper_graph.objects(None, primaryElectronicEdition_ref))[0]
    entry['title'] = title
    entry['anchor'] = key.replace('/', '_')
    entry['scholar'] = "https://scholar.google.com/scholar?q={}".format(title.replace(' ', '+'))
    entry['bibtex'] = "http://dblp.org/rec/bibtex1/{}".format(key)
    
    # using xml parser because rdflib is not order-preserving
    root = ET.fromstring(data)
    publication = root.find("{" + dblp_schema + "#}Publication")
    authors_nodes = publication.findall("{" + dblp_schema + "#}authoredBy")
    authors_uris = [n.attrib["{" + rdf_syntax + "#}resource"] for n in authors_nodes]
    authors = []
    for author_uri in authors_uris:
        disassembled = urllib.parse.urlparse(author_uri)
        author_file = join(cache_dir, basename(disassembled.path).replace(':','_') + ".rdf")
        if not os.path.isfile(author_file):
            urllib.request.urlretrieve(author_uri + ".rdf", author_file)
        with open(author_file) as f:
            author_data = f.read()
        author_graph = rdflib.Graph()
        author_graph.parse(data=author_data, format='xml')
        name = list(author_graph.objects(None, primaryFullPersonName_ref))[0]
        authors.append(name.toPython())

    authors_str = authors[0]
    for a in authors[1:]:
        authors_str = authors_str + ", " + a

    entry['key'] = key
    entry['authors'] = authors_str.encode('ascii', 'xmlcharrefreplace').decode()
    entry['venue'] = venue
    entry['venue_details'] = venue_details
    entry['year'] = yearOfPublication
    entry['url'] = primaryElectronicEdition

    for tool in tools_data:
        if tool['dblp'] == key:
            entry['tool'] = tool['name']
            break

    for benchmark in benchmarks_data:
        if 'dblp' in benchmark and benchmark['dblp'] == key:
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
