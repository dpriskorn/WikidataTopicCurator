# Updating the dependencies and docker image
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
