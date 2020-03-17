Scripts
-----
`fetcher.py`: Use scholarly library to fetch information belonging to certain author, output that information to `data.txt` in a parsed manner.

`write_word.py`: Take information from `sanitized.txt`, order it, categorize it and output to `result.txt`

Files
-----
* `data.txt`: Raw data obtained from scholarly library, represented in a way in which it can be parsed later.

* `sanitized.txt`: LateX special characters are now represented as Unicode special characters.

* `result.txt`: Ordered citations

Notes
-----
The way information is parsed into `data.txt` is not the optimal way, because it uses `--`, and some citations have their range of pages using that string. Therefore, extra processing has to be made. This can just be changed to be another string such as '$/*-' or similar (any combination which is highly improbable).
