pytest src/tests/ --browser chrome
pytest src/tests --browser chrome-headless --base-url ${RENDER_PROD_URL}



docker start jenkins-server


docker start jenkins-server
docker restart jenkins-server
