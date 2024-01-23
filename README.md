# ItemSubjectorApp
This is a simplified rewrite of ItemSubjector into a webapp 
to help wikimedians curate scientific articles with topics.

## Features
Based on a given QID it fetches articles 
matching the label of that QID that is currently missing ANY main theme property.

### Limit
It supports user-supplied limit like so: http://127.0.0.1:5000/Q1334131?limit=50

## Todo
* Let users choose the matching string like https://lubianat.shinyapps.io/topictagger/
* Support english plural also
