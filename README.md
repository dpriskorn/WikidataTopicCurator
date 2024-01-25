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

## Documentation
https://www.wikidata.org/wiki/Wikidata:Tools/Wikidata_Topic_Curator

## Todo
* Support english plural also. 

## License
GPLv3+

## Inspiration
This app was inspired by [topictagger](https://github.com/lubianat/topictagger), AuthorDisambiguator and Scholia.
The bootstrap layout was inspired by [Wikidata Lexeme Forms](https://lexeme-forms.toolforge.org/)

## What I learned
* the syntax of flask and FastAPI seem very similar
* jinja2 templates are really cool
* pycharm has very nice html editing support :)
* chatgpt is very good at helping with flask apps, which really sped up development
* bootstrap is nice, I don't have to fiddle with CSS at all, just choose a few classes and it's good enough to get out the door
