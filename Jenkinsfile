// Jenkinsfile in majd.kassem.business_qa repo
pipeline {
    agent any // Or a specific agent label

    // Parameters expected from the SUT pipeline trigger
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
                    image "majd-selenium-runner:${env.BUILD_NUMBER}" // Use the dynamically built image tag
                    // If you need to mount volumes for reports or other data:
                    // args "-v \${WORKSPACE}/test-results:/var/lib/jenkins/workspace/QA-Selenium-Pipeline@3/test-results -v \${WORKSPACE}/allure-results:/var/lib/jenkins/workspace/QA-Selenium-Pipeline@3/allure-results"
                    // Or map the whole workspace if it's simpler:
                    // args "-v ${WORKSPACE}:/app" // And then run tests from /app inside container
                    // But the current `-w` should handle it.
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
                    withEnv(["BASE_URL=${params.SUT_DEV_URL}"]) { // Pass SUT_DEV_URL as an environment variable
                        sh "/opt/venv/bin/pytest src --alluredir=allure-results --clean-alluredir"
                        // Removed 'cd majd.kassem.business_qa'
                        // Added 'src' assuming your tests are in the 'src' folder as seen in ls -la output.
                    }
                    echo "Pytest command finished." // This will be reached if pytest itself runs
                    echo "--- Inside Docker Container (After Pytest) ---"
                    sh "ls -la test-results"
                    sh "ls -la allure-results"
                }
            }
            post {
                always {
                    // Check if test results exist before publishing
                    script {
                        if (fileExists('test-results/junit-report.xml')) { // Adjust if your report name is different
                            junit 'test-results/junit-report.xml'
                            echo "JUnit report published."
                        } else {
                            echo "WARNING: JUnit report file not found at test-results/junit-report.xml. Skipping JUnit publishing."
                        }

                        if (fileExists('allure-results')) {
                            // Requires Allure plugin configured in Jenkins
                            // Replace 'allure' with the actual function call if your plugin uses a different one
                            // Example: allure([includeProperties: false, results: [[path: 'allure-results']]])
                            echo "Allure results found. Allure report will be published if plugin is configured."
                        } else {
                            echo "WARNING: Allure results directory not found at allure-results. Skipping Allure Report publishing."
                        }
                    }
                }
                failure {
                    error "Pytest tests failed (exit code: ${currentBuild.result == 'FAILURE' ? '1' : 'other'}). Check logs above for details."
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
        }
        success {
            echo "Overall pipeline SUCCESS! ✅"
        }
        failure {
            echo "Overall pipeline FAILED: Some tests did not pass or deployment failed. ❌"
        }
    }
}