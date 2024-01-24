# Wikidata Topic Curator
This is a simplified rewrite of ItemSubjector into a webapp 
to help wikimedians curate scientific articles with topics.

![image](https://github.com/dpriskorn/WikidataTopicCurator/assets/68460690/52dc9ff4-98d8-4952-9b14-8decc6963eeb)
Start page

![image](https://github.com/dpriskorn/WikidataTopicCurator/assets/68460690/dd2c9b49-ffab-41a4-ae43-d8fb357518db)
Result page

## Features
Based on a given topic QID it fetches articles 
matching the label, aliases or a custom user-provided term 
of that QID that is currently missing the main subject property.

After the user has approved the matches they can be sent to 
quickstatements for batch upload.

* Multi-term support
* Populating terms from label and aliases
* User defined terms
* Excluding items with a certain term (via CirrusSearch affix, see below)
* Support batch upload by sending the matches to QuickStatement

### Limit
It supports user-supplied limit like so: http://127.0.0.1:5000/Q1334131?limit=50

### Cirrussearch prefix
It supports user-supplied cirrussearch parameters:

default prefix: 'haswbstatement:P31=Q13442814 -haswbstatement:P921={topic QID}'

For e.g. parental alienation syndrome Q1334131 it becomes: 'haswbstatement:P31=Q13442814 -haswbstatement:P921=Q1334131'

This tells cirrussearch to get all results that is a scientific article and does not have this topic in a main topic statement already.

Example url that searches for parental alienation syndrome but only returns those without any P921: 127.0.0.1:5000/Q1334131?limit=50&cirrussearch=haswbstatement%3AP31%3DQ13442814%20-haswbstatement%3AP921%3DQ1334131%20%22parental%20alienation%20syndrome%22

See https://www.mediawiki.org/wiki/Help:Extension:WikibaseCirrusSearch for documentation on all possible parameters.

PLEASE NOTE: https://www.mediawiki.org/wiki/Help:CirrusSearch/Logical_operators -> OR is not supported and AND is implied
We work around this by running multiple queries.

### Cirrussearch string affix
This is appended to the cirrussearch string

#### Use case parental alienation without "syndrome"
http://127.0.0.1:5000/Q1949144?limit=20 -> lots of false positives because parental alienation syndrome Q1334131 has the same string before "syndrome".
We tell cirrussearch to exclude all items with "syndrome" by adding: '-inlabel:syndrome'
Url: 

## Todo
* Support english plural also. 

## User script
See https://www.wikidata.org/wiki/User:So9q/item-subjector-app-link.js

## License
GPLv3+

## Thanks
This app was inspired by AuthorDisambiguator and Scholia.

## What I learned
* the syntax of flask and FastAPI seem very similar
* jinja2 templates are really cool
* pycharm has very nice html editing support :)
* chatgpt is very good at helping with flask apps, which really sped up development