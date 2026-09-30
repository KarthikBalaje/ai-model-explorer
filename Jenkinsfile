pipeline {

    agent any

    environment {
        IMAGE_NAME = "ai-model-explorer"
        REGISTRY = "localhost:5001"
        IMAGE_TAG = "${BUILD_NUMBER}"
        FULL_IMAGE = "${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
    }

    stages {

        stage("Checkout") {
            steps {
                checkout scm
            }
        }

        stage("Build") {
            steps {
                echo "Installing development dependencies..."

                bat "python -m pip install -r requirements-dev.txt"

                echo "Running Black..."

                bat "python -m black --check app.py tests"

                echo "Running Flake8..."

                bat "python -m flake8 app.py tests"

                echo "Running Pytest..."

                bat "python -m pytest -v"
            }
        }

        stage("Docker Build") {
            steps {

                echo "Building Docker image..."

                bat """
                    docker build -t ${FULL_IMAGE} .
                """

                echo "Running Trivy vulnerability scan..."

                bat """
                    trivy image ^
                        --exit-code 1 ^
                        --severity HIGH,CRITICAL ^
                        --ignore-unfixed ^
                        ${FULL_IMAGE}
                """

                echo "Trivy scan passed. Pushing image..."

                bat """
                    docker push ${FULL_IMAGE}
                """
            }
        }
    }

    post {

        success {
            echo "CI/CD pipeline completed successfully."
            echo "Docker image: ${FULL_IMAGE}"
        }

        failure {
            echo "Pipeline failed. Check the stage logs."
        }

        always {
            echo "Pipeline execution completed."
        }
    }
}