# ---------------------1- Reporting using Allure

# (Optional: Activate your Python virtual environment if you're using one)
# source venv/bin/activate # On Linux/macOS
# .venv\Scripts\activate # On Windows

# Ensure the allure-results directory is clean or created
rm -rf allure-results # On Linux/macOS (use rmdir /s /q allure-results on Windows)
mkdir allure-results

# Run your pytest tests with the --alluredir flag
pytest src/tests --alluredir=allure-results --browser chrome-headless --baseurl http://127.0.0.1:8000/
pytest src/tests --alluredir=allure-results --browser chrome --baseurl http://127.0.0.1:8000/
pytest src/tests --browser chrome --baseurl http://127.0.0.1:8000/
allure serve allure-results

# ---------------------2- Reporting using Allure
pytest src/tests/ --browser chrome
pytest src/tests --browser chrome-headless --base-url ${RENDER_PROD_URL}
pytest src/tests --browser chrome --baseurl http://127.0.0.1:8000/
# ###################################################################

# ########### Test Cases ###############################################################

# Teacher
TC1: Valid joining 
TC2: Valid Pending
TC3: Valid Course Adding 
pytest src/tests/teachers --browser chrome --baseurl http://127.0.0.1:8000/
# Home
TC1: Valid Login 
TC2: Invalid Login 
pytest src/tests/home --browser chrome --baseurl http://127.0.0.1:8000/ 


