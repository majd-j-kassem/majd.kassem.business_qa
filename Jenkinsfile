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
                // The 'node' step is important for specifying where this part of the pipeline runs.
                // Ensure you have a Jenkins agent (like your Built-in Node) with the label 'jenkins'.
                // If not, change 'jenkins' to 'master' or 'any' or the label of your agent.
                node('jenkins') {
                    checkout scm // Ensure the workspace is clean for this stage

                    // Use withEnv to set BASE_URL for the duration of this block
                    withEnv(["BASE_URL=${RENDER_DEV_URL}"]) {
                        script {
                            echo "Running tests against Render Dev: ${env.BASE_URL} inside custom Docker image."

                            // --- IMPORTANT PERMISSION FIXES (Executed on Jenkins Host) ---
                            // 1. Create directories on the Jenkins host's workspace
                            //    These directories will be mounted into the Docker container.
                            sh 'mkdir -p test-results allure-results'

                            // 2. Set permissions for these directories ON THE JENKINS HOST.
                            //    This should be sufficient as Docker usually respects host permissions for mounted volumes.
                            sh 'chmod -R 777 test-results allure-results'

                            // Now, run pytest inside the Docker container
                            // Use the FULL_DOCKER_IMAGE_NAME that was built earlier
                            docker.image(env.FULL_DOCKER_IMAGE_NAME).inside {
                                // --- DEBUGGING COMMANDS START HERE ---
                                echo "--- Inside Docker Container (Before Pytest) ---"
                                sh 'pwd' // Show current working directory inside container
                                sh 'ls -la' // List contents of current working directory
                                // Check if the *mounted* directories exist and have correct permissions from container's perspective
                                sh 'ls -la test-results'
                                sh 'ls -la allure-results'
                                echo "Attempting to run pytest..."

                                // Run pytest.
                                // Use the simplified internal paths that are relative to the container's working directory.
                                // The Docker plugin automatically handles the base workspace volume mount.
                                def pytestExitCode = sh(script: "pytest src/tests --browser chrome-headless --base-url ${env.BASE_URL} --junitxml=${JUNIT_REPORT_FILE_INTERNAL} --alluredir=${ALLURE_RESULTS_PATH_INTERNAL}", returnStatus: true)

                                echo "Pytest command finished with exit code: ${pytestExitCode}"

                                echo "--- Inside Docker Container (After Pytest) ---"
                                sh 'ls -la test-results' // Check if junit-report.xml was created
                                sh 'ls -la allure-results' // Check if allure files were created
                                // --- DEBUGGING COMMANDS END HERE ---

                                // If pytest failed, ensure the pipeline fails immediately.
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
                    // Check if the report file exists on the host before trying to publish.
                    script {
                        def junitReportPath = "test-results/junit-report.xml" // Path relative to Jenkins workspace
                        if (fileExists(junitReportPath)) {
                            echo "Found JUnit report file: ${junitReportPath}. Publishing results."
                            junit junitReportPath
                        } else {
                            echo "WARNING: JUnit report file not found at ${junitReportPath}. Skipping JUnit publishing."
                            // If you want the build to fail if no report is found, uncomment the line below:
                            // error "JUnit report not found. Build will fail."
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