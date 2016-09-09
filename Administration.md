# Administration #

All data (papers, tools, news, etc.) is stored in JSON format.

To update information on the website:

1. Install Python 3 and pystache (e.g. `aptitude install python-pystache`).
2. Modify files in the `data` directory.
3. Run `python3 build.py` script.
4. Open `index.html` in your browser to verify your modifications.
5. Commit and push changes.
