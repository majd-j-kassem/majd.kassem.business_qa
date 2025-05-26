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

        // --- Simplified internal paths for reports ---
        // These paths will now be relative to the Jenkins workspace on the host,
        // which is mounted to the same path as inside the container.
        JUNIT_REPORT_FILE_INTERNAL = 'test-results/junit-report.xml'
        ALLURE_RESULTS_PATH_INTERNAL = 'allure-results'

        // --- Name for your custom Docker image ---
        CUSTOM_DOCKER_IMAGE_NAME = 'majd-selenium-runner'

        // --- Full Docker image name including tag, derived from BUILD_NUMBER ---
        FULL_DOCKER_IMAGE_IMAGE_NAME = "${CUSTOM_DOCKER_IMAGE_NAME}:${BUILD_NUMBER}"

        // --- Allure Commandline Tool Name ---
        // This MUST match the name you configured under Jenkins > Manage Jenkins > Tools > Allure Commandline installations
        // Example: 'Allure_2.27.0' or whatever you named it.
        ALLURE_COMMANDLINE_TOOL_NAME = 'Allure_2.27.0' // <--- IMPORTANT: Adjust this if your tool name is different!
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
                // Using 'node('jenkins')' ensures the test execution happens on a Jenkins agent,
                // which is good practice for Docker operations.
                node('jenkins') {
                    // We'll leave the `checkout scm` here as it was in your original file.
                    // It ensures the workspace for *this specific node block* is fresh,
                    // which can be helpful if previous stages touched the workspace.
                    checkout scm

                    withEnv(["BASE_URL=${RENDER_DEV_URL}"]) {
                        script {
                            echo "Running tests against Render Dev: ${env.BASE_URL} inside custom Docker image."

                            // --- IMPORTANT: Create directories on the Jenkins host's workspace ---
                            // These directories will be mounted into the Docker container.
                            sh "mkdir -p ${env.JUNIT_REPORT_FILE_INTERNAL.split('/')[0]} ${env.ALLURE_RESULTS_PATH_INTERNAL}"
                            // Set permissions for these directories ON THE JENKINS HOST.
                            // This ensures the container user can write to them.
                            sh "chmod -R 777 ${env.JUNIT_REPORT_FILE_INTERNAL.split('/')[0]} ${env.ALLURE_RESULTS_PATH_INTERNAL}"

                            // Now, run pytest inside the Docker container
                            docker.image(env.FULL_DOCKER_IMAGE_NAME).inside {
                                echo "--- Inside Docker Container (Before Pytest) ---"
                                sh 'pwd' // Should show the Jenkins workspace path inside the container
                                sh "ls -la ${env.JUNIT_REPORT_FILE_INTERNAL.split('/')[0]}"
                                sh "ls -la ${env.ALLURE_RESULTS_PATH_INTERNAL}"
                                echo "Attempting to run pytest..."

                                // Pytest command will write to the mounted volumes using the WORKSPACE variable,
                                // which points to the Jenkins agent's workspace mounted inside the container.
                                def pytestCommand = "pytest src/tests --browser chrome-headless --base-url ${env.BASE_URL} --junitxml=${WORKSPACE}/${env.JUNIT_REPORT_FILE_INTERNAL} --alluredir=${WORKSPACE}/${env.ALLURE_RESULTS_PATH_INTERNAL}"
                                def pytestExitCode = sh(script: pytestCommand, returnStatus: true)

                                echo "Pytest command finished with exit code: ${pytestExitCode}"

                                echo "--- Inside Docker Container (After Pytest) ---"
                                sh "ls -la ${env.JUNIT_REPORT_FILE_INTERNAL.split('/')[0]}"
                                sh "ls -la ${env.ALLURE_RESULTS_PATH_INTERNAL}"

                                // Fail the build if pytest didn't exit cleanly
                                if (pytestExitCode != 0) {
                                    error "Pytest tests failed (exit code: ${pytestExitCode}). Check logs above for details."
                                }
                            } // End of docker.image().inside {}

                            // --- REPORT PUBLISHING (MOVED OUTSIDE DOCKER CONTAINER BLOCK) ---
                            // These steps now run on the Jenkins agent's host machine AFTER the Docker container
                            // has finished and written the report files to the shared workspace.
                            echo "--- Publishing Reports (Outside Docker Container) ---"

                            // JUnit Report Publishing
                            if (fileExists(env.JUNIT_REPORT_FILE_INTERNAL)) { // Check path relative to Jenkins workspace
                                echo "Found JUnit report file: ${env.JUNIT_REPORT_FILE_INTERNAL}. Publishing results."
                                junit env.JUNIT_REPORT_FILE_INTERNAL // Path relative to Jenkins workspace
                            } else {
                                echo "WARNING: JUnit report file not found at ${env.JUNIT_REPORT_FILE_INTERNAL}. Skipping JUnit publishing."
                            }

                            // Allure Report Publishing
                            if (fileExists(env.ALLURE_RESULTS_PATH_INTERNAL)) { // Check if the directory exists
                                // Now, check if the directory is empty by getting its content count
                                def fileCount = sh(script: "ls -A ${env.ALLURE_RESULTS_PATH_INTERNAL} | wc -l", returnStdout: true).trim() as int

                                if (fileCount > 0) {
                                    echo "Found Allure results in ${env.ALLURE_RESULTS_PATH_INTERNAL}. Publishing Allure Report."
                                    // Use 'tool' step to ensure Allure command-line tool is on PATH
                                    withEnv(["PATH+ALLURE=${tool env.ALLURE_COMMANDLINE_TOOL_NAME}/bin"]) {
                                        allure([
                                            reportBuildPolicy: 'ALWAYS',
                                            results: [[path: env.ALLURE_RESULTS_PATH_INTERNAL]]
                                        ])
                                    }
                                    echo "Allure Report publishing complete."
                                } else {
                                    echo "WARNING: Allure results directory found but empty at ${env.ALLURE_RESULTS_PATH_INTERNAL}. Skipping Allure Report publishing."
                                }
                            } else {
                                echo "WARNING: Allure results directory not found at ${env.ALLURE_RESULTS_PATH_INTERNAL}. Skipping Allure Report publishing."
                            }
                        } // End of script block
                    } // End of withEnv
                } // End of node('jenkins')
            } // End of steps
            // Removed the `post` block from inside the stage, as the failure check is now combined
            // with the pytestExitCode check and the report publishing is in the main steps block.
            post {
                // This post block will run after all steps in this stage are completed.
                failure {
                    echo "Tests against Render Dev FAILED! Build will stop here. ❌"
                }
            }
        }

        stage('Deploy to Render Live (CD Phase)') {
            when {
                // Only run this stage if the previous stages (especially tests) were successful
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                script {
                    echo "Tests passed. Triggering deployment of the System Under Test to Render Live..."
                    // Use withCredentials to securely inject the API key
                    withCredentials([string(credentialsId: env.RENDER_API_KEY_CREDENTIAL_ID, variable: 'RENDER_API_KEY')]) {
                        // Using double quotes for the entire curl command and escaping internal quotes
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
                    sh "rm -rf ${env.JUNIT_REPORT_FILE_INTERNAL.split('/')[0]} ${env.ALLURE_RESULTS_PATH_INTERNAL}" // Use env vars for consistency
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