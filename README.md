# automated-program-repair.org #

This website is a community-driven effort to provide up-to-date references about automated program repair. We'd love you to contribute new publications, tools and benchmarks to make information on automated-program-repair.org more objective, complete and accurate.

## Website content ##

Our website lists publications

* Describing systems, algorithm, empirical studies and other works on automated program repair
* Describing domain-specific automated program repair algorithms and tools
* Describing applications of automated program repair

Our website displays only tools and benchmarks that

* Have corresponding publications
* Publicly available
* Designed specifically for automated program repair

## Contrubiting via pull requests ##

All data (papers, tools, news, etc.) is stored in JSON format (see `data` directory). The HTML pages are rendered from the templates in `templates` directory.

To update information on the website:

1. Install Python 3 and pystache (e.g. `aptitude install python3-pystache`).
2. Modify files in the `data` directory.
3. Run build script (e.g. `python3 build.py`).
4. Open `index.html` in your browser to verify your modifications.
5. Commit changes and create a pull request.

## Contributing via Github Issues ##

To submit a new publication, you need to provide the following:

* Title and authors
* Journal/conference
* URL to pdf file (if it is publicly available)

To submit a new tool or benchmark, you need to provide the following:

* One line description
* Target (e.g. C source code, i386 binaries, etc)
* URL
* Related publication