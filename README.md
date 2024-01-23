# ItemSubjectorApp
This is a simplified rewrite of ItemSubjector into a webapp 
to help wikimedians curate scientific articles with topics.

![image](https://github.com/dpriskorn/ItemSubjectorApp/assets/68460690/3c60444f-695c-48e2-828d-23e35072ae7e)

## Features
Based on a given QID it fetches articles 
matching the label of that QID that is currently missing ANY main theme property.

### Limit
It supports user-supplied limit like so: http://127.0.0.1:5000/Q1334131?limit=50

### Cirrussearch string
It supports user-supplied cirrussearch parameters:

default parameter: 'haswbstatement:P31=Q13442814 -haswbstatement:P921={self.main_subject_item}'

For e.g. parental alienation syndrome Q1334131 it becomes: 'haswbstatement:P31=Q13442814 -haswbstatement:P921=Q1334131 "parental alienation syndrome"'
This tells cirrussearch to get all results that is a scientific article and does not have this topic in a main topic statement already.

A more precise search that only considers english labels is: 'haswbstatement:P31=Q13442814 -haswbstatement:P921=Q1334131 inlabel:"parental alienation syndrome"@en'

Use https://www.urlencoder.io/ or similar to encode the parameter.

Example url that searches for parental alienation syndrome but only returns those without any P921: 127.0.0.1:5000/Q1334131?limit=50&cirrussearch=haswbstatement%3AP31%3DQ13442814%20-haswbstatement%3AP921%3DQ1334131%20%22parental%20alienation%20syndrome%22

See https://www.mediawiki.org/wiki/Help:Extension:WikibaseCirrusSearch for documentation on all possible parameters.

### Cirrussearch string affix
This is appended to the cirrussearch string
#### Use case parental alienation without "syndrome"
http://127.0.0.1:5000/Q1949144?limit=20 -> lots of false positives because parental alienation syndrome Q1334131 has the same string before "syndrome".
We tell cirrussearch to exclude all items with "syndrome" by adding: '-inlabel:syndrome'
Url: 

## Todo
* Support english plural also. 
This is already supported by adding a CirrusSearch affix, e.g. csa=inlabel:plural-form-of-term

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