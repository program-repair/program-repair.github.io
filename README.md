# program-repair.org #

This website is a community-driven effort to provide up-to-date automated program repair bibliography, and links to publicly available tools and benchmarks.

## Content ##

The website lists publications describing

* systems, algorithm, empirical studies and other works on automated program repair
* domain-specific automated program repair algorithms and tools
* applications of automated program repair

The bibliographic records on this website are automatically extracted from dblp.org.

The website displays tools and benchmarks that

* have corresponding publications in the bibliography section
* publicly available
* designed for program repair

The website also hosts community pages &mdash; static webpages that present some information that is useful for program repair community.
If you would like to maintain a community page under program-repair.org GitHub organization, please create an issue.

## Contributing via GitHub Issues ##

To submit a new publication via GitHub issues, please provide its DBLP key. To get the DBLP key, find the publication on dblp.org, and hover mouse over "export record". To submit a new tool or benchmark, please provide the DBLP key of its corresponding publication.

## Contributing via pull requests ##

The website is automatically generated from data in the `data` directory. The HTML pages are rendered from the templates in `templates` directory.

To update information on the website:

1. Install Python 3 and dependencies (e.g. `pip3 install -r requirements.txt`).
2. Modify files in the `data` directory.
3. Run build script (e.g. `python3 build.py`).
4. Open `index.html` in your browser to verify your modifications.
5. Commit changes and create a pull request.
