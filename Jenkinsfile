pipeline {
    agent any
    stages {
        stage('Start Carla') {
            steps {
                script {
                    sh 'docker exec graic_con ./carla-simulator/CarlaUE4.sh -opengl & echo "Start Carla"'
                    sh 'docker exec graic_con sleep 5'
                }
            }
        }
        stage('Start ROS') {
            steps {
                script {
                    sh 'docker exec graic_con ./launch.sh & echo "Start ROS"'
                    sh 'docker exec graic_con sleep 30'
                }
            }
        }
        stage('Start Race') {
            steps {
                script {
                    sh 'docker exec graic_con ./race.sh & echo "Start Race"'
                    sh 'docker exec graic_con sleep 60'
                }
            }
        }
        stage('End Carla and ROS'){
            steps {
                script {
                    sh 'docker exec graic_con pkill python3 & echo "End ROS"'
                    sh 'docker exec graic_con pkill ros & echo "End ROS"'
                    sh 'docker exec graic_con pkill Carla & echo "End Carla"'
                    sh 'docker exec graic_con cat graic-workspace/src/race_util_module/evaluation_node/src/$(docker exec graic_con ls -t graic-workspace/src/race_util_module/evaluation_node/src/ | head -1)'
                }
            }
        }
    }
}
