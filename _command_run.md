pytest src/tests/ --browser chrome
pytest src/tests --browser chrome-headless --base-url ${RENDER_PROD_URL}
pytest src/tests --browser chrome --base-url http://127.0.0.1:8000/


docker start jenkins-server


docker start jenkins-server
docker restart jenkins-server
