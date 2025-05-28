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
                // This step implicitly checks out the repo for the current pipeline.
                // It's a standard practice for declarative pipelines.
                checkout scm
            }
        }

        // This stage ('Checkout SUT Code') is redundant because 'Declarative: Checkout SCM'
        // already checks out the `majd.kassem.business_qa` repository (which contains the SUT code
        // and the Selenium test code).
        // If your "SUT Code" is in a *different* repository, you would need a separate
        // `git` checkout step for that *other* repository.
        // As it stands, you're checking out the same repository three times.
        // I'm commenting it out, you can remove it if it's truly not needed.
        /*
        stage('Checkout SUT Code') {
            steps {
                script {
                    checkout scm // This checks out the same repo again
                    echo "System Under Test (SUT) code checked out."
                }
            }
        }
        */

        stage('Checkout Selenium Test Code') {
            steps {
                script {
                    // This is also redundant if 'Declarative: Checkout SCM' already checks out this repo.
                    // However, if for some reason you want to ensure a clean checkout for tests,
                    // or if the test code was in a separate repo, this would be valid.
                    // Given your project structure (Jenkinsfile, src/, Dockerfile are all in the same repo),
                    // 'Declarative: Checkout SCM' at the pipeline start is usually sufficient.
                    // I'll keep it as you had it, but be aware it's likely an unnecessary second checkout
                    // of the exact same repository content in the same workspace.
                    git url: 'https://github.com/majd-j-kassem/majd.kassem.business_qa.git',
                        branch: 'dev', // Explicitly use the 'dev' branch
                        credentialsId: 'f83fa332-1b50-46cb-ab54-d71eeb19ae4f' // Use the credential that works
                    sh 'ls -la' // Keep this for debugging if needed, can remove later once stable
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
                    // The working directory inside the container is automatically mapped
                    // to the Jenkins workspace (e.g., /var/lib/jenkins/workspace/QA-Selenium-Pipeline@2).
                    // No extra 'args' like -w are typically needed here for that.
                    // If you needed specific user permissions for Docker, you might add:
                    // args: "-u \$(id -u jenkins):\$(id -g jenkins)"
                    // But your previous logs show -u 113:132 which seems to be auto-handled or configured.
                }
            }
            steps {
                script {
                    echo "Running tests against Render Dev: ${params.SUT_DEV_URL} inside custom Docker image."
                    sh 'mkdir -p test-results allure-results'
                    sh 'chmod -R 777 test-results allure-results' // Ensure permissions for these directories
                    echo "--- Inside Docker Container (Before Pytest) ---"
                    sh "pwd"
                    sh "ls -la"

                    echo "Attempting to run pytest..."
                    // **CRITICAL FIX: Add PYTHONPATH=. to allow Python to find 'src' module**
                    // Re-added Allure options as they were missing in the last log
                    sh """
                        mkdir -p test-results allure-results
                        chmod -R 777 test-results allure-results
                        echo "--- Inside Docker Container (Before Pytest) ---"
                        pwd
                        ls -la
                        echo "Attempting to run pytest..."
                        # Try a simpler pytest command first
                        PYTHONPATH=. /opt/venv/bin/python -m pytest
                    """
                    echo "Pytest command finished."
                    echo "--- Inside Docker Container (After Pytest) ---"
                    sh "ls -la test-results" // Verify if junit-report.xml is present
                    sh "ls -la allure-results" // Verify if allure results are present
                }
            }
            post {
                always {
                    script {
                        // Publish JUnit report
                        if (fileExists('test-results/junit-report.xml')) {
                            junit 'test-results/junit-report.xml'
                            echo "JUnit report published."
                        } else {
                            echo "WARNING: JUnit report file not found at test-results/junit-report.xml. Skipping JUnit publishing."
                        }

                        // Generate and publish Allure report (if Allure plugin is configured)
                        // This assumes you have the Allure Jenkins plugin installed and configured.
                        // The Allure plugin will look for 'allure-results' by default.
                        if (fileExists('allure-results/')) {
                            echo "Allure results found. Attempting to generate and publish report."
                            allure([
                                reportDir: 'allure-results',
                                results: [[path: 'allure-results']]
                            ])
                            echo "Allure report published."
                        } else {
                            echo "WARNING: Allure results directory not found at allure-results/. Skipping Allure report publishing."
                        }
                    }
                }
                failure {
                    // Use `currentBuild.result` to get the actual result (e.g., FAILURE, ABORTED)
                    error "Pytest tests failed (exit code: ${currentBuild.result}). Check logs above for details."
                    echo "Tests against Render Dev FAILED! Build will stop here. ❌"
                }
                success {
                    echo "All Selenium tests passed against Render Dev! ✅"
                }
            }
        }

        stage('Deploy to Render Live (CD Phase)') {
            // This stage will be skipped if previous stages fail due to the `failFast` option (not explicit here, but default behavior).
            // Or if you explicitly `error` in a previous `post` block.
            steps {
                echo "Triggering deployment to Render Live Service..."
                build job: 'Deploy-to-Live-Service',
                      parameters: [
                          string(name: 'SUT_BUILD_NUMBER', value: params.SUT_BUILD_NUMBER)
                          // Pass other necessary parameters if 'Deploy-to-Live-Service' expects them
                      ]
                echo "Deployment to Render Live triggered."
            }
        }

        stage('Cleanup') {
            // This stage will also be skipped if previous stages fail.
            // If you want cleanup to always run, even on failure, you'd put it in a `post { always { ... } }` block
            // at the `pipeline` level, not as a separate stage.
            steps {
                script {
                    echo "Cleaning up workspace..."
                    cleanWs() // Cleans the workspace after build
                    echo "Workspace cleaned."
                }
            }
        }
    }

    // Post-pipeline actions, always run regardless of stage success/failure
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