pipeline {
    agent admin

    triggers {
        pollSCM('*/5 * * * *')
    }
    options {
        skipDefaultCheckout(true)
        // Keep the 10 most recent builds
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
    }
    environment {
      PATH="/home/cis/Desktop/ENV/pybitenv/bin:$PATH"
    }

    stages {

        stage ("Code pull"){
            steps{
                checkout scm
            }
        }
        stage('Build environment') {
            steps {
                sh '''export WORKSPACE=`pwd`
                      source /home/cis/Desktop/ENV/pybitenv/bin/activate
                      pip install -r /home/cis/Desktop/Python/PyBitmessage/requirements.txt
                    '''
            }
        }
        stage('Test environment') {
            steps {
                sh '''export WORKSPACE=`pwd` 
                      source /home/cis/Desktop/ENV/pybitenv/bin/activate
                      cd /home/cis/Desktop/Python/PyBitmessage
                      sudo python setup.py install
                      sudo /home/cis/.local/bin/nosetests --with-xunit tests
                    '''
            }
        }
        stage('Test Run') {
            steps {
                sh '''python /home/cis/Desktop/Python/PyBitmessage/src/bitmessagemain.py -t
                    '''
            }
        }
    }
    post {
        failure {
            echo "Send e-mail, when failed"
        }
    }
}
