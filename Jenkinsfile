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

        stage('Checkout Selenium Test Code') {
            steps {
                script {
                    git url: 'https://github.com/majd-j-kassem/majd.kassem.business_qa.git',
                        branch: 'dev',
                        credentialsId: 'f83fa332-1b50-46cb-ab54-d71eeb19ae4f'
                    sh 'ls -la'
                    echo "Selenium test code (QA Project) checked out into 'majd.kassem.business_qa' folder."
                }
            }
        }

        stage('Build Custom Test Image') {
            steps {
                script {
                    echo "Building custom Docker image: majd-selenium-runner:${env.BUILD_NUMBER}"
                    sh "docker build -t majd-selenium-runner:${env.BUILD_NUMBER} ."
                    echo "Custom Docker Image built: majd-selenium-runner:${env.BUILD_NUMBER}"
                }
            }
        }

        stage('Cleanup Pytest Cache') {
            steps {
                script {
                    sh 'rm -rf .pytest_cache'
                    sh 'find . -name "__pycache__" -exec rm -rf {} +'
                }
            }
        }

        stage('Run Tests - Render Dev (CI Phase)') {
            agent {
                docker {
                    image "majd-selenium-runner:${env.BUILD_NUMBER}"
                }
            }
            steps {
                script {
                    echo "Running tests against Render Dev: ${params.SUT_DEV_URL} inside custom Docker image."
                    sh 'mkdir -p test-results' // Only create test-results, no allure-results
                    sh 'chmod -R 777 test-results' // Ensure permissions
                    echo "--- Inside Docker Container (Before Pytest) ---"
                    sh "pwd"
                    sh "ls -la"

                    echo "Attempting to run pytest..."
                    // This is the CRITICAL command for debugging the ValueError
                    // Allure-related flags (--alluredir) are removed
                    sh """
                        PYTHONPATH=. /opt/venv/bin/pytest src/tests \\
                        --browser chrome-headless \\
                        --base-url ${params.SUT_DEV_URL} \\ 
                        -s -v --trace-config
                    """
                    echo "Pytest command finished."

                    echo "--- Inside Docker Container (After Pytest) ---"
                    sh "ls -la test-results" // Verify if junit-report.xml is present (optional)

                    // ALLURE GENERATION COMMAND REMOVED
                    // echo "Generating Allure report inside the container..."
                    // sh '/opt/allure-commandline/bin/allure generate allure-results -c -o allure-report'
                    // sh 'ls -la allure-report'
                }
            }
            post { // THIS IS THE STAGE-LEVEL POST BLOCK
                always {
                    script {
                        // Publish JUnit report (if you're generating it)
                        // This assumes your tests generate a junit-report.xml somehow, e.g., via --junitxml flag
                        if (fileExists('test-results/junit-report.xml')) {
                            junit 'test-results/junit-report.xml'
                            echo "JUnit report published."
                        } else {
                            echo "WARNING: JUnit report file not found at test-results/junit-report.xml. Skipping JUnit publishing."
                        }

                        // ALLURE PUBLISH COMMAND REMOVED
                        // if (fileExists('allure-report/')) {
                        //     echo "Allure report found. Attempting to publish."
                        //     allure([reportDir: 'allure-report'])
                        //     echo "Allure report published."
                        // } else {
                        //     echo "WARNING: Allure report directory not found at allure-report/. Skipping Allure report publishing."
                        // }
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
        stage('Deploy to Dev Service') {
            **steps { // <-- ADDED THIS 'steps' BLOCK**
                script {
                    echo "Triggering deployment of SUT to Render Dev Service: https://majd-kassem-business-dev.onrender.com/"
            // Use the ID you assigned to your credential in Jenkins
                    withCredentials([string(credentialsId: 'RENDER_API_KEY', variable: 'RENDER_API_KEY_VAR')]) {
                        sh """
                        curl -X POST -H "Authorization: Bearer ${RENDER_API_KEY_VAR}" https://api.render.com/v1/services/srv-d0pau63e5dus73dkco6g/deploys
                        """
                    }
                    echo "Deployment trigger sent to Render Dev! Check Render dashboard for status."
                    echo "Waiting a few seconds for Render to initiate deployment..."
                    sleep 10
                }
            **} // <-- CLOSED THE 'steps' BLOCK**
            post {
                success {
                    echo "Successfully triggered Render Dev deployment. 🎉"
                }
            }
        }
        stage('Deploy to Render Live (CD Phase)') {
            steps {
                echo "Triggering deployment to Render Live Service..."
                build job: 'Deploy-to-Live-Service',
                      parameters: [
                          string(name: 'SUT_BUILD_NUMBER', value: params.SUT_BUILD_NUMBER)
                      ]
                echo "Deployment to Render Live triggered."
            }
        }

        stage('Cleanup') {
            steps {
                script {
                    echo "Cleaning up workspace..."
                    cleanWs()
                    echo "Workspace cleaned."
                }
            }
        }
    }

    post { // This is the pipeline-level post block
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