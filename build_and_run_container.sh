# Build and run the container
# --rm means don't store changes
touch /tmp/gunicorn_ipc.sock ; docker build -t topiccurator .; docker run --rm -p 5000:5000 topiccurator