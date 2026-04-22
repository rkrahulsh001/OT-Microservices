@Library('my-shared-library') _

pipeline {
    agent any

    parameters {
        choice(
            name: 'ENVIRONMENT',
            choices: ['dev', 'staging', 'prod'],
            description: 'Select deployment environment'
        )
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'master',
                url: 'https://github.com/rkrahulsh001/OT-Microservices.git'
            }
        }

        stage('Validate Environment') {
            steps {
                script {
                    deployObj = new Deployment(this)
                    deployObj.validate(params.ENVIRONMENT)
                }
            }
        }

        stage('Deploy Application') {
            steps {
                script {
                    deployObj.deploy(params.ENVIRONMENT)
                }
            }
        }
    }

    post {
        failure {
            script {
                deployObj.rollback(params.ENVIRONMENT)
            }
        }

        success {
            echo "Deployment Successful"
        }
    }
}
