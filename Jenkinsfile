// Jenkinsfile in majd.kassem.business_qa.git
pipeline {
    agent { docker { image 'python:3.13-slim-bookworm' } }
    parameters {
        string(name: 'SUT_BASE_URL', defaultValue: 'https://majd-kassem-business-dev.onrender.com/', description: 'SUT URL for tests.')
    }
    environment {
        BASE_URL = "${params.SUT_BASE_URL}"
        TEST_IMAGE = "majd-selenium-runner:${BUILD_NUMBER}"
    }
    stages {
        stage('Checkout QA Main') {
            steps {
                git branch: 'main', url: 'https://github.com/majd-j-kassem/majd.kassem.business_qa.git'
            }
        }
        stage('Build Test Image') {
            steps {
                script{
                 docker.build(TEST_IMAGE, ".") 
                }
                 } // Dockerfile for test runner in QA repo root
        }
        stage('Run Tests') {
            steps {
                sh 'mkdir -p test-results allure-results && chmod -R 777 test-results allure-results'
                script{
                docker.image(TEST_IMAGE).inside {
                    def pytestExitCode = sh(script: "pytest src/tests --browser chrome-headless --base-url ${BASE_URL} --junitxml=${WORKSPACE}/test-results/junit-report.xml --alluredir=${WORKSPACE}/allure-results", returnStatus: true)
                    if (pytestExitCode != 0) { error "Tests failed!" }
                }
                }
            }
            post {
                always {
                    junit 'test-results/junit-report.xml'
                    allure([reportBuildPolicy: 'ALWAYS', results: [[path: 'allure-results']]])
                }
            }
        }
        stage('Cleanup') {
            steps {
                sh "rm -rf test-results allure-results"
                sh "docker rmi -f ${TEST_IMAGE}"
            }
        }
    }
    post { always { echo "QA Pipeline finished: ${currentBuild.result}" } }
}