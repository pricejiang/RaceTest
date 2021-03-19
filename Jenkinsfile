pipeline {
    agent any
    stages {
        stage('Obtain Controller Code'){
            steps {
                script {
                    echo "Build ${OBJECT_NAME}"
                    echo '${SCORE}'
                    sh 'docker exec graic_con pkill python3 & echo "Clean for Start"'
                    sh 'docker exec graic_con pkill ros & echo "Clean for Start"'
                    sh 'docker exec graic_con pkill Carla & echo "Clean for Start"'
                    sh 'docker exec graic_con2 pkill python3 & echo "Clean for Start"'
                    sh 'docker exec graic_con2 pkill ros & echo "Clean for Start"'
                    sh 'docker exec graic_con2 pkill Carla & echo "Clean for Start"'
                    // sh 'docker exec graic_con aws s3 cp s3://jenkins-graic-bucket/${OBJECT_NAME} .'
                }
            }
        }
        stage('Start Carla') {
            parallel {
                stage('t1') {
                    steps {
                        script {
                            sh 'docker exec graic_con ./runCarla.sh 2000 & echo "Start Carla"'
                            sh 'docker exec graic_con sleep 5'
                        }
                    }
                }
                stage('t2') {
                    steps {
                        script {
                            sh 'docker exec graic_con2 ./runCarla.sh 3000 & echo "Start Carla"'
                            sh 'docker exec graic_con2 sleep 5'
                        }
                    }
                }
            }
        }
        stage('Start ROS') {
            parallel{
                stage('t1') {
                    steps {
                        script {
                            sh 'docker exec graic_con ./launch.sh 2000 & echo "Start ROS"'
                            sh 'docker exec graic_con sleep 30'
                        }
                    }
                }
                stage('t2') {
                    steps {
                        script {
                            sh 'docker exec graic_con2 ./launch.sh 3000 & echo "Start ROS"'
                            sh 'docker exec graic_con2 sleep 30'
                        }
                    }
                }
            }
        }
        stage('Start Race') {
            parallel{
                stage('t1') {
                    steps {
                        script {
                            sh 'docker exec graic_con ./race.sh ${OBJECT_NAME} & echo "Start Race"'
                            sh 'docker exec graic_con sleep 60'
                        }
                    }
                }
                stage('t2') {
                    steps {
                        script {
                            sh 'docker exec graic_con2 ./race.sh ${OBJECT_NAME} & echo "Start Race"'
                            sh 'docker exec graic_con2 sleep 60'
                        }
                    }
                }
            }
            
        }
        stage('End Carla and ROS'){
            steps {
                script {
                    sh 'docker exec graic_con pkill python3 & echo "End ROS"'
                    sh 'docker exec graic_con pkill ros & echo "End ROS"'
                    sh 'docker exec graic_con pkill Carla & echo "End Carla"'
                    sh 'docker exec graic_con2 pkill python3 & echo "End ROS"'
                    sh 'docker exec graic_con2 pkill ros & echo "End ROS"'
                    sh 'docker exec graic_con2 pkill Carla & echo "End Carla"'
                    sh 'docker cp graic_con:home/carla/graic-workspace/src/race_util_module/evaluation_node/src/$(docker exec graic_con ls -t graic-workspace/src/race_util_module/evaluation_node/src/ | head -1) ./score.txt'
                    sh 'docker cp graic_con2:home/carla/graic-workspace/src/race_util_module/evaluation_node/src/$(docker exec graic_con2 ls -t graic-workspace/src/race_util_module/evaluation_node/src/ | head -1) ./score2.txt'
                }
            }
        }
    }
    post {
        always {
            emailext attachLog:true, attachmentsPattern: 'score*.txt', body: 'Build is done with ${OBJECT_NAME}', to: 'mjiang24@illinois.edu', subject: 'Build Done'
        }
    }
}
