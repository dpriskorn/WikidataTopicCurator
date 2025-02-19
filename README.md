# Wikidata Topic Curator
This is a simplified rewrite of ItemSubjector into a webapp 
to help wikimedians curate scientific articles with topics.

Start page:

![image](https://github.com/dpriskorn/WikidataTopicCurator/assets/68460690/8aff0406-cf93-432b-b033-7fd09524b430)

Subtopic page:

![image](https://github.com/dpriskorn/WikidataTopicCurator/assets/68460690/c4506983-d990-4d2b-a3c9-e375c73e7f19)

Query page:

![image](https://github.com/dpriskorn/WikidataTopicCurator/assets/68460690/e050b4f2-5985-46a8-b99a-137a86af4f87)

Results page:

![image](https://github.com/dpriskorn/WikidataTopicCurator/assets/68460690/ef5f3103-161b-45ae-bd07-cc6bd75134e3)

## Features
See the documentation.

## Documentation
https://www.wikidata.org/wiki/Wikidata:Tools/Wikidata_Topic_Curator

## Participating
See the issues in Github. Feel free to open a new one or send a pull request. :)

## License
AGPLv3+

## Updating the dependencies and docker image
1. open pycharm and make sure there is a local interpreter
2. if no local interpreter: 
   3. delete the .venv directory
   3. create a new venv in pycharm
1. run $pip install --upgrade pip && pip install poetry
1. search for a suitable updated python image here https://hub.docker.com/_/python/
2. update the Dockerfile with the new python image name
3. run ./[update_poetry.sh](update_poetry.sh)
5. run ./[build_and_run_container.sh](build_and_run_container.sh)
6. commit and push changes
7. go to the vps and pull & rebuild the image & start the docker container

## Inspiration
This app was inspired by [topictagger](https://github.com/lubianat/topictagger), AuthorDisambiguator and Scholia.
The bootstrap layout was inspired by [Wikidata Lexeme Forms](https://lexeme-forms.toolforge.org/)

## What I learned
* the syntax of flask and FastAPI seem very similar
* jinja2 templates are really cool
* pycharm has very nice html editing support :)
* chatgpt is very good at helping with flask apps, which really sped up development
* bootstrap is nice, I don't have to fiddle with CSS at all, just choose a few classes and it's good enough to get out the door
* chatgpt can generate all the javascript I'll ever need for simple projects like this one. Very nice not having to learn and keep that in memory at all.

## Effort
This software is a product of about two weeks work of time.
