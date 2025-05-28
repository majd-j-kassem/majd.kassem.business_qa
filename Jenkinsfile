// Jenkinsfile in majd.kassem.business_qa repo
pipeline {
    agent any // Or a specific agent label

    // Parameters expected from the SUT pipeline trigger g
    parameters {
        string(name: 'SUT_DEV_URL', defaultValue: 'http://localhost:8080/', description: 'URL of the deployed DEV SUT service')
        string(name: 'SUT_BUILD_NUMBER', defaultValue: 'N/A', description: 'Build number of the SUT that triggered this run')
    }

    stages {
        stage('Declarative: Checkout SCM') {
            steps {
                checkout scm
            }
        }

        // This stage is still redundant if your QA tests don't need the SUT's source code locally.
        // Consider removing it unless there's a specific reason.
        stage('Checkout SUT Code') {
            steps {
                script {
                    checkout scm // This checks out the same repo again
                    echo "System Under Test (SUT) code checked out."
                }
            }
        }

        stage('Checkout Selenium Test Code') {
            steps {
                script {
                    // Fix the credential ID here if 'majd-qa-repo-credentials' doesn't exist
                    // Otherwise, keep 'using credential f83fa332-1b50-46cb-ab54-d71eeb19ae4f'
                    git url: 'https://github.com/majd-j-kassem/majd.kassem.business_qa.git',
                        branch: 'dev', // Explicitly use the 'dev' branch
                        credentialsId: 'f83fa332-1b50-46cb-ab54-d71eeb19ae4f' // Use the credential that works
                    sh 'ls -la' // Keep this for debugging if needed, can remove later
                    echo "Selenium test code (QA Project) checked out into 'majd.kassem.business_qa' folder."
                }
            }
        }

        stage('Build Custom Test Image') {
            steps {
                script {
                    echo "Building custom Docker image: majd-selenium-runner:${env.BUILD_NUMBER}"
                    // Make sure your Dockerfile is in the root of the checked-out repo
                    sh "docker build -t majd-selenium-runner:${env.BUILD_NUMBER} ."
                    echo "Custom Docker Image built: majd-selenium-runner:${env.BUILD_NUMBER}"
                }
            }
        }

         stage('Run Tests - Render Dev (CI Phase)') {
            agent {
                docker {
                    image "majd-selenium-runner:${env.BUILD_NUMBER}"
                    // It's good that you mentioned args. We don't need them for this specific error,
                    // as the default workspace mapping handles it.
                    // The `-w` argument handles the working directory inside the container.
                }
            }
            steps {
                script {
                    echo "Running tests against Render Dev: ${params.SUT_DEV_URL} inside custom Docker image."
                    sh "mkdir -p test-results allure-results"
                    sh "chmod -R 777 test-results allure-results"

                    echo "--- Inside Docker Container (Before Pytest) ---"
                    sh "pwd"
                    sh "ls -la"

                    echo "Attempting to run pytest..."
                    // Here's the key modification: Pass browser and base_url to pytest
                    // Note: We use the SUT_DEV_URL parameter directly.
                    // And we hardcode 'chrome-headless' for CI.
                    sh """
                        /opt/venv/bin/pytest src/tests \\
                            --alluredir=allure-results \\
                            --clean-alluredir \\
                            --browser=chrome-headless \\
                            --base-url=${params.SUT_DEV_URL}
                    """
                    echo "Pytest command finished."
                    echo "--- Inside Docker Container (After Pytest) ---"
                    sh "ls -la test-results"
                    sh "ls -la allure-results"
                }
            }
            post {
                always {
                    script {
                        // Assuming your pytest generates a JUnit XML report. If not, you might need to configure pytest to do so.
                        // For example: pytest --junitxml=test-results/junit-report.xml src/tests ...
                        // Your initial log shows 'collected 2 items', which means pytest ran.
                        // You might need to adjust your pytest command to ensure it generates this report.
                        if (fileExists('test-results/junit-report.xml')) {
                            junit 'test-results/junit-report.xml'
                            echo "JUnit report published."
                        } else {
                            echo "WARNING: JUnit report file not found at test-results/junit-report.xml. Skipping JUnit publishing."
                        }

                        if (fileExists('allure-results/')) {
                            echo 'Generating Allure report...'
                            allure([[allureCmdline: 'Allure_CLI_2.25.0', reportBuildPolicy: 'ALWAYS', source: 'allure-results']])
                            echo 'Allure report generated.'
                        } else {
                            echo 'Allure results directory not found. Skipping Allure report generation.'
                        }
                    }
                }
                failure {
                    error "Pytest tests failed (exit code: ${currentBuild.result}). Check logs above for details."
                    echo "Tests against Render Dev FAILED! Build will stop here. ❌"
                }
                success {
                    echo "All Selenium tests passed against Render Dev! ✅"
                }
            }
        }

        stage('Deploy to Render Live (CD Phase)') {
            steps {
                echo "Triggering deployment to Render Live Service..."
                build job: 'Deploy-to-Live-Service',
                      parameters: [
                          string(name: 'SUT_BUILD_NUMBER', value: params.SUT_BUILD_NUMBER)
                          // Pass other necessary parameters
                      ]
                echo "Deployment to Render Live triggered."
            }
        }

        stage('Cleanup') {
            steps {
                script {
                    echo "Cleaning up workspace..."
                    cleanWs() // Cleans the workspace after build
                    echo "Workspace cleaned."
                }
            }
        }
    }

    post {
        always {
            echo "Pipeline finished for job QA-Selenium-Pipeline, build number ${env.BUILD_NUMBER}."
            allure([
                results: ['allure-results'], 
])
        }
        success {
            echo "Overall pipeline SUCCESS! ✅"
        }
        failure {
            echo "Overall pipeline FAILED: Some tests did not pass or deployment failed. ❌"
        }
    }
}