
# Data Management for Physical Training

## AUTHOR and HOMEPAGE

Copyright (C) 2021,2022,2023 by Alexander Tenbusch <https://github.com/raxdne/training>

## DESCRIPTION

This is a small Python package which supports Data Management for a personal endurance Training (planning, reporting).

![Demo](https://github.com/raxdne/training/blob/main/demo/ThunderbirdLightning.png)

Main features
1) plans for training periods and cycles
1) reports based on calendar or defined periods
1) definitions of plan and report in pure Python
1) Objects for
   - Training Unit + Combination + Pause,
   - Training Cycle and
   - Training Period
1) output of text-based formats
   - plain
   - HTML
   - Freemind XML
   - vCalendar
   - SVG

![Demo Mindmap](https://github.com/raxdne/training/blob/main/demo/Freemind.png)

![Demo](https://github.com/raxdne/training/blob/main/demo/Diagram.png)

![Edit in Inkscape](https://github.com/raxdne/training/blob/main/demo/Inkscape.png)

## Installation

using `pip`

	python3 -m pip install -e git+https://github.com/raxdne/training.git@v2.1#egg=training

OR all required packages

	pip3 install suntime icalendar

Test on MS Windows

	cd /d C:\UserData\src\training
	set PYTHONPATH=C:\UserData\src\training
	"C:\Program Files\Python311\python.exe" demo\Simple.py
	
