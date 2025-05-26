pipeline {
    // We use 'agent any' at the top level because we'll build our custom Docker image
    // in a specific stage and then use that image in subsequent stages.
    agent any

    environment {
        // --- Render Service URLs ---
        RENDER_DEV_URL = 'https://majd-kassem-business-dev.onrender.com/'
        RENDER_PROD_URL = 'https://majd-kassem-business.onrender.com/'

        // --- IMPORTANT: Render Live Service ID ---
        // Get this from your Render Dashboard URL for your Live service (e.g., srv-xxxxxxxxxxxxxxxxx)
        RENDER_LIVE_SERVICE_ID = 'srv-d0h686q4d50c73c6g410' // This is now correctly set

        // --- IMPORTANT: Jenkins Credential ID for Render API Key ---
        // This MUST match the ID you gave your Secret text credential in Jenkins.
        RENDER_API_KEY_CREDENTIAL_ID = 'render-api-key'

        // --- NEW: Simplified internal paths for reports ---
        // These paths will now be relative to the Jenkins workspace INSIDE the container,
        // which is mounted to the same path as on the host.
        JUNIT_REPORT_FILE_INTERNAL = 'test-results/junit-report.xml'
        ALLURE_RESULTS_PATH_INTERNAL = 'allure-results' // No longer /home/seluser/...

        // --- Name for your custom Docker image ---
        CUSTOM_DOCKER_IMAGE_NAME = 'majd-selenium-runner'

        // --- Full Docker image name including tag, derived from BUILD_NUMBER ---
        FULL_DOCKER_IMAGE_NAME = "${CUSTOM_DOCKER_IMAGE_NAME}:${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout Selenium Test Code') {
            steps {
                script {
                    // This checks out your Selenium test automation project from GitHub
                    git branch: 'dev', url: 'https://github.com/majd-j-kassem/majd.kassem.business_qa.git'
                    sh 'ls -la' // List files to verify checkout
                    echo "Selenium test code checked out."
                }
            }
        }

        stage('Build Custom Test Image') {
            steps {
                script {
                    echo "Building custom Docker image: ${env.FULL_DOCKER_IMAGE_NAME}"
                    // Build the Docker image. It will be automatically tagged with FULL_DOCKER_IMAGE_NAME
                    docker.build(env.FULL_DOCKER_IMAGE_NAME, ".")
                    echo "Custom Docker Image built: ${env.FULL_DOCKER_IMAGE_NAME}"
                }
            }
        }

        stage('Run Tests - Render Dev (CI Phase)') {
            steps {
                node('jenkins') {
                    checkout scm

                    withEnv(["BASE_URL=${RENDER_DEV_URL}"]) {
                        script {
                            echo "Running tests against Render Dev: ${env.BASE_URL} inside custom Docker image."

                            // --- IMPORTANT PERMISSION FIXES (Executed on Jenkins Host) ---
                            // 1. Create directories on the Jenkins host's workspace
                            sh 'mkdir -p test-results allure-results'
                            // 2. Set permissions for these directories ON THE JENKINS HOST.
                            sh 'chmod -R 777 test-results allure-results'

                            // Now, run pytest inside the Docker container
                            docker.image(env.FULL_DOCKER_IMAGE_NAME).inside {
                                echo "--- Inside Docker Container (Before Pytest) ---"
                                sh 'pwd'
                                sh 'ls -la'
                                sh 'ls -la test-results'
                                sh 'ls -la allure-results'
                                echo "Attempting to run pytest..."

                                // The paths for --junitxml and --alluredir should be relative
                                // to the WORKDIR inside the container.
                                // Since your Dockerfile sets WORKDIR /home/seluser,
                                // and then you are running in /var/lib/jenkins/workspace/y-app-dev-deploy-and-tes@2
                                // due to the Jenkins Docker plugin's mounting...
                                // The key is to ensure the mount is correct.
                                // Let's try simplifying the pytest output paths to ensure they write
                                // directly into the mounted directories.

                                // Pytest command will write to the mounted volumes:
                                // /var/lib/jenkins/workspace/y-app-dev-deploy-and-tes@2/test-results/junit-report.xml
                                // /var/lib/jenkins/workspace/y-app-dev-deploy-and-tes@2/allure-results
                                def pytestExitCode = sh(script: "pytest src/tests --browser chrome-headless --base-url ${env.BASE_URL} --junitxml=${WORKSPACE}/test-results/junit-report.xml --alluredir=${WORKSPACE}/allure-results", returnStatus: true)

                                echo "Pytest command finished with exit code: ${pytestExitCode}"

                                echo "--- Inside Docker Container (After Pytest) ---"
                                sh 'ls -la test-results'
                                sh 'ls -la allure-results'

                                if (pytestExitCode != 0) {
                                    error "Pytest tests failed (exit code: ${pytestExitCode}). Check logs above for details."
                                }
                            }
                        }
                    }
                }
            }
            post {
                always {
                    script {
                        // --- JUnit Report Publishing ---
                        // These paths are relative to the Jenkins workspace on the HOST.
                        def junitReportPath = "test-results/junit-report.xml"
                        if (fileExists(junitReportPath)) {
                            echo "Found JUnit report file: ${junitReportPath}. Publishing results."
                            junit junitReportPath
                        } else {
                            echo "WARNING: JUnit report file not found at ${junitReportPath}. Skipping JUnit publishing."
                        }

                        // --- Allure Report Publishing ---
                        def allureResultsDir = "allure-results" // Path relative to Jenkins workspace on the HOST
                        if (fileExists(allureResultsDir) && sh(script: "ls -A ${allureResultsDir} | wc -l", returnStdout: true).trim() as int > 0) { // Check if directory exists and is not empty
                            echo "Found Allure results in ${allureResultsDir}. Publishing Allure Report."
                            allure([
                                reportBuildPolicy: 'ALWAYS',
                                results: [[path: allureResultsDir]]
                            ])
                            echo "Allure Report publishing complete."
                        } else {
                            echo "WARNING: Allure results directory not found or empty at ${allureResultsDir}. Skipping Allure Report publishing."
                        }
                    }
                }
                failure {
                    echo "Tests against Render Dev FAILED! Build will stop here. ❌"
                }
            }
        }

        stage('Deploy to Render Live (CD Phase)') {
            when {
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                script {
                    echo "Tests passed. Triggering deployment of the System Under Test to Render Live..."
                    withCredentials([string(credentialsId: env.RENDER_API_KEY_CREDENTIAL_ID, variable: 'RENDER_API_KEY')]) {
                        sh "curl -X POST -H \"Authorization: Bearer ${RENDER_API_KEY}\" \"https://api.render.com/v1/services/${env.RENDER_LIVE_SERVICE_ID}/deploys\""
                    }
                    echo "Deployment trigger sent to Render Live! Check Render dashboard for status."
                }
            }
            post {
                failure {
                    echo "Failed to trigger Render Live deployment! Please check API key, Service ID, or Render status. ❌"
                }
                success {
                    echo "Successfully triggered Render Live deployment. 🎉"
                }
            }
        }

        stage('Cleanup') {
            steps {
                script {
                    echo "Cleaning up workspace and removing custom Docker image..."
                    // Remove the generated report files from the host workspace
                    sh "rm -rf test-results allure-results" // Relative paths to workspace
                    // Remove the custom Docker image to save space
                    sh "docker rmi -f ${env.FULL_DOCKER_IMAGE_NAME}"
                }
            }
        }
    }

    post {
        // Global actions after the entire pipeline finishes
        always {
            echo "Pipeline finished for job ${env.JOB_NAME}, build number ${env.BUILD_NUMBER}."
        }
        success {
            echo "Overall pipeline SUCCESS: All tests passed and Render Live deployment triggered. 🎉"
        }
        failure {
            echo "Overall pipeline FAILED: Some tests did not pass or deployment failed. ❌"
        }
        aborted {
            echo "Overall pipeline ABORTED: Build was manually stopped. 🚫"
        }
    }
}