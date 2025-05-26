pipeline {
    agent {
        // You can specify an agent label here, e.g., agent { label 'my-linux-agent' }
        // For now, it will run on any available agent
        label 'jenkins-agent' // Example label, ensure you have an agent with this label or remove if running on main controller
    }
    options {
        // Set a timeout for the entire pipeline (e.g., 60 minutes)
        timeout(time: 60, unit: 'MINUTES')
        // Discard old builds to save disk space
        buildDiscarder(logRotator(numToKeepStr: '5'))
        // Enable timestamps in console output
        timestamps()
        // Prevent concurrent builds
        disableConcurrentBuilds()
    }
    parameters {
        string(name: 'BROWSER', defaultValue: 'chrome-headless', description: 'Browser to run tests on (e.g., chrome, firefox, chrome-headless, firefox-headless)')
        string(name: 'BASE_URL_DEV', defaultValue: 'https://majd-kassem-business-dev.onrender.com/', description: 'Base URL for the development environment')
        string(name: 'BASE_URL_LIVE', defaultValue: 'https://majd-kassem-business.onrender.com/', description: 'Base URL for the live environment')
        string(name: 'RENDER_SERVICE_ID_DEV', defaultValue: 'srv-d0h686q4d50c73c6g410', description: 'Render Service ID for Dev environment deployment')
        string(name: 'RENDER_SERVICE_ID_LIVE', defaultValue: 'srv-d0h686q4d50c73c6g410', description: 'Render Service ID for Live environment deployment') // You might want a different one for Live
    }

    environment {
        // Define environment variables here, e.g., for secrets from Jenkins Credentials
        // This makes sure the variables are available throughout the pipeline
        // Ensure 'RENDER_API_KEY_CREDENTIAL_ID' matches your Jenkins credential ID
        RENDER_API_KEY = credentials('RENDER_API_KEY_CREDENTIAL_ID')
        // Define the path to your Dockerfile for clarity
        DOCKERFILE_PATH = 'Dockerfile'
        // Increment build number for Docker image tag
        BUILD_TAG = "majd-selenium-runner:${BUILD_NUMBER}"
        // Define test report paths
        JUNIT_REPORT_PATH = "test-results/junit-report.xml"
        ALLURE_RESULTS_DIR = "allure-results"
        ALLURE_COMMANDLINE_HOME = tool 'Allure_2.27.0' // Ensure this matches your configured Allure commandline tool name in Jenkins
    }

    stages {
        stage('Declarative: Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Checkout Selenium Test Code') {
            steps {
                script {
                    // Assuming your Selenium tests are in the same repository.
                    // If they are in a different repo, you would add another 'git' step here.
                    // Example if in a separate repo:
                    // git branch: 'main', credentialsId: 'your-git-credential-id', url: 'https://github.com/your-org/your-selenium-repo.git'
                    // For now, assuming current repo contains the tests.
                    echo "Checking out test code from the current repository..."
                    // It's already checked out in the Declarative Checkout SCM stage,
                    // but you might want to re-checkout here if you have submodules or specific needs.
                    // For this setup, we'll just confirm the presence of key files
                    sh 'ls -la'
                    echo "Selenium test code checked out."
                }
            }
        }

        stage('Build Custom Test Image') {
            steps {
                script {
                    echo "Building custom Docker image: ${BUILD_TAG}"
                    // Build the Docker image based on the Dockerfile in the workspace
                    dir ('.') { // Ensure we are in the root of the workspace
                        docker.build("${BUILD_TAG}", "-f ${DOCKERFILE_PATH} .")
                    }
                    echo "Custom Docker Image built: ${BUILD_TAG}"
                }
            }
        }

        stage('Run Tests - Render Dev (CI Phase)') {
            agent {
                // Using a dedicated agent for running tests might be beneficial for resources
                // and to avoid issues with the main controller's Docker setup.
                label 'jenkins-agent'
            }
            steps {
                script {
                    echo "Running tests against Render Dev: ${BASE_URL_DEV} inside custom Docker image."
                    // Create directories for test results inside the workspace
                    sh "mkdir -p ${JUNIT_REPORT_PATH.replace('/junit-report.xml', '')} ${ALLURE_RESULTS_DIR}"
                    sh "chmod -R 777 ${JUNIT_REPORT_PATH.replace('/junit-report.xml', '')} ${ALLURE_RESULTS_DIR}"


                    // Run tests inside the Docker container
                    docker.image("${BUILD_TAG}").inside {
                        echo "--- Inside Docker Container (Before Pytest) ---"
                        sh 'pwd'
                        sh 'ls -la'
                        sh "ls -la ${JUNIT_REPORT_PATH.replace('/junit-report.xml', '')}"
                        sh "ls -la ${ALLURE_RESULTS_DIR}"

                        echo "Attempting to run pytest..."
                        // Execute pytest, outputting JUnit XML and Allure results
                        // Ensure paths are correct relative to the container's working directory
                        def pytestExitCode = sh(script: "pytest src/tests --browser ${BROWSER} --base-url ${BASE_URL_DEV} --junitxml=${JUNIT_REPORT_PATH} --alluredir=${ALLURE_RESULTS_DIR}", returnStatus: true)

                        echo "Pytest command finished with exit code: ${pytestExitCode}"

                        echo "--- Inside Docker Container (After Pytest) ---"
                        sh "ls -la ${JUNIT_REPORT_PATH.replace('/junit-report.xml', '')}"
                        sh "ls -la ${ALLURE_RESULTS_DIR}"

                        // --- JUnit Report Publishing (MOVED HERE) ---
                        if (fileExists(JUNIT_REPORT_PATH)) {
                            echo "Found JUnit report file: ${JUNIT_REPORT_PATH}. Publishing results."
                            junit JUNIT_REPORT_PATH
                        } else {
                            echo "WARNING: JUnit report file NOT found at ${JUNIT_REPORT_PATH}. Skipping JUnit publishing."
                        }

                        // --- Allure Report Publishing (MOVED HERE) ---
                        if (fileExists(ALLURE_RESULTS_DIR)) {
                            def fileCount = sh(script: "ls -A ${ALLURE_RESULTS_DIR} | wc -l", returnStdout: true).trim() as int
                            if (fileCount > 0) {
                                echo "Found Allure results in ${ALLURE_RESULTS_DIR}. Publishing Allure Report."
                                // The 'allure' step uses the path relative to the Jenkins workspace.
                                allure([
                                    reportBuildPolicy: 'ALWAYS',
                                    results: [[path: ALLURE_RESULTS_DIR]]
                                ])
                                echo "Allure Report publishing complete."
                            } else {
                                echo "WARNING: Allure results directory found but empty at ${ALLURE_RESULTS_DIR}. Skipping Allure Report publishing."
                            }
                        } else {
                            echo "WARNING: Allure results directory NOT found at ${ALLURE_RESULTS_DIR}. Skipping Allure Report publishing."
                        }

                        // Fail the build if pytest didn't exit cleanly
                        if (pytestExitCode != 0) {
                            error "Pytest tests failed!"
                        }
                    }
                }
            }
        }

        stage('Deploy to Render Live (CD Phase)') {
            steps {
                script {
                    echo "Tests passed. Triggering deployment of the System Under Test to Render Live..."
                    withCredentials([string(credentialsId: 'RENDER_API_KEY_CREDENTIAL_ID', variable: 'RENDER_API_KEY')]) {
                        sh "curl -X POST -H 'Authorization: Bearer ${RENDER_API_KEY}' https://api.render.com/v1/services/${RENDER_SERVICE_ID_LIVE}/deploys"
                    }
                    echo "Deployment trigger sent to Render Live! Check Render dashboard for status."
                }
            }
        }

        stage('Cleanup') {
            steps {
                script {
                    echo "Cleaning up workspace and removing custom Docker image..."
                    sh "rm -rf ${JUNIT_REPORT_PATH.replace('/junit-report.xml', '')} ${ALLURE_RESULTS_DIR}"
                    sh "docker rmi -f ${BUILD_TAG}"
                }
            }
        }
    }

    post {
        always {
            echo "Pipeline finished for job ${JOB_NAME}, build number ${BUILD_NUMBER}."
        }
        success {
            echo "Overall pipeline SUCCESS: All tests passed and Render Live deployment triggered. 🎉"
        }
        failure {
            echo "Overall pipeline FAILED: Tests against Render Dev FAILED! Build will stop here. ❌"
            // You might want to add additional notifications here for failure
        }
    }
}