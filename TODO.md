
# TODO

## Requirements

REQ: cut(b,a) to skip an interval
- cut(a,b) to delete out-of-interval elements

REQ: merge(a,b)
- cut(a).append(cut(b))

REQ: Notes in Markdown format

REQ: read data from CalDAV server
- https://github.com/python-caldav/caldav/blob/master/examples/basic_usage_examples.py
- https://github.com/python-caldav/caldav/blob/master/docs/source/index.rst

REQ: handle [Time Intervals and Repeating intervals](https://en.wikipedia.org/wiki/ISO_8601#Time_intervals)
- <https://github.com/gweis/isodate>

REQ: accumulated time chart ✔

REQ: multi-user data, synchronized team

REQ: append note/description as normal child in cycle and period  ✔

REQ: report of current cycle should use the days between start and today  ✔

BUG: report of time-only value cycle #scope ✔

REQ: make colorcoding configurable ✔

REQ: link some units of different types into one unit (e.g. Triathlon) ✔

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

## Input

### CSV

REQ: define Combinations in CSV Report

## Output Formats

### Plain text

### SQLite dump

### iCal

TEST: calendar output format in different applications
1) Thunderbird Lightning ✔
1) https://github.com/Etar-Group/Etar-Calendar
1) https://github.com/SufficientlySecure/calendar-import-export

### Freemind XML

REQ: use Mindmap as input (`mm2py.xsl`)

### SVG

REQ: overlay plan and report Gantt chart (reuse SVG strings + opacity)

REQ: accumulated Diagram for comparison of multiple periods ✔

<https://pypi.org/project/svgwrite/>

<https://pypi.org/project/drawSvg/>

### [Streamlit](https://streamlit.io/)

“Turn your data scripts into shareable web apps in minutes. All in pure Python. No front‑end experience required.”

[Streamlit Crash Course: From Zero to Data App](https://www.youtube.com/watch?v=d7fnzDQ5qM8)

https://docs.streamlit.io/

https://github.com/streamlit/streamlit

REQ: WebUI

    python3 -m venv ~/python/streamlit
    ~/python/streamlit/bin/pip3 install streamlit
    ~/python/streamlit/streamlit hello

use `app-starter-kit` on Github as Template

    if __name__ == "__main__":
        try:
            # https://discuss.streamlit.io/t/how-to-check-if-code-is-run-inside-streamlit-and-not-e-g-ipython/23439/8
            from streamlit.runtime.scriptrunner import get_script_run_ctx
            if get_script_run_ctx():
                    st.set_page_config(layout="wide")
                    st.write("""
                    # My first app
                    Hello *world* ABC!
                    """)

                    
                    # https://discuss.streamlit.io/t/adding-an-svg-image-and-listen-to-events-on-the-image/51006

                    b64 = base64.b64encode(s.toSVGGanttChart().encode('utf-8')).decode("utf-8")
                    html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64

                    c = st.container()
                    c.write(html, unsafe_allow_html=True)
                    c.write(config.style, unsafe_allow_html=True)
                    #c.write(s.toHtmlTableOfContent(), unsafe_allow_html=True)
                    c.html(s.toHtmlTableOfContent())
                    #s.setPlot(True)
                    c.html(s.toHtml())
            else:
                pass
        except ModuleNotFoundError:
            pass
