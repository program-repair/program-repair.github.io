# program-repair.org #

This website is a community-driven effort to provide up-to-date references about automated program repair.

## Bibliography ##

Our website lists publications

* Describing systems, algorithm, empirical studies and other works on automated program repair
* Describing domain-specific automated program repair algorithms and tools
* Describing applications of automated program repair

The bibliographic records on this website are automatically extracted from dblp.org.

## Tools and benchmarks ##

Our website displays only tools and benchmarks that

* Have corresponding publications in the bibliography section
* Publicly available
* Designed for program repair

## Community projects ##

The goal of program-repair.org community projects is to make automated program repair research, data and dissemination accessible to all levels of an inquiring society in accordance with the principles of open science.
If you would like to maintain a community project under program-repair.org GitHub organization, please create an issue.

## Contributing via pull requests ##

The website is automatically generated from data in the `data` directory. The HTML pages are rendered from the templates in `templates` directory.

To update information on the website:

1. Install Python 3 and dependencies (e.g. `pip3 install -r requirements.txt`).
2. Modify files in the `data` directory.
3. Run build script (e.g. `python3 build.py`).
4. Open `index.html` in your browser to verify your modifications.
5. Commit changes and create a pull request.

## Contributing via GitHub Issues ##

To submit a new publication, you need to provide the following:

* dblp key (find the publication on dblp.org and click `export record -> dblp key`)

To submit a new tool or benchmark, you need to provide the following:

* Name
* One line description
* Target (e.g. C/C++, Binaries, etc)
* Website and/or repository
* dblp key of the related publication