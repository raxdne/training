
# TODO

## Requirements

REQ: append note/description as normal child in cycle and period ?? #scope

REQ: report of current cycle should use the days between start and today #scope ✔

BUG: report of time-only value cycle #scope ✔

REQ: make colorcoding configurable ✔

REQ: link some units of different types into one unit (e.g. Triathlon)

DONE: configuration of significant chars of type string ('B' or 'Bic' or 'Bicycle') ✔

DONE: configuration of distance units ✔

DONE: configure Apache HTTP Server `mod_python` https://github.com/grisha/mod_python
- http://headstation.com/archives/installing-modpython-apache/

DONE: configure Apache HTTP Server `mod_wsgi`  ('libapache2-mod-wsgi-py3')
- https://github.com/GrahamDumpleton/mod_wsgi
- https://modwsgi.readthedocs.io/en/master/
- https://tecadmin.net/install-apache-with-python-mod-wsgi-on-ubuntu-20-04/

TODO: configure Apache HTTP Server using simple CGI

REQ: simple generic frontend script ✔

REQ: combination of units like `20211010;25RG+5LG+KG;3:00;`

REQ: different parser/generator modules for input formats

## Output Formats

### Plain text

### iCal

TEST: calendar output format in different applications
+ Thunderbird Lightning ✔
+ https://github.com/Etar-Group/Etar-Calendar
+ https://github.com/SufficientlySecure/calendar-import-export

### Freemind XML

REQ: use Mindmap as input (`mm2py.xsl`)

### SVG

REQ: accumulated Diagram for comparison of multiple periods

<https://pypi.org/project/svgwrite/>

<https://pypi.org/project/drawSvg/>

