pipeline {
    agent any
    triggers {
        pollSCM('*/5 * * * 1-5')
    }
    options {
        // skipDefaultCheckout(true)
        // Keep the 10 most recent builds
        buildDiscarder(logRotator(numToKeepStr: '10'))
        // timestamps()
    }
    environment {
        projectName = 'BitMessage'
        emailTo = 'kuldeep.m@cisinlabs.com'
        emailFrom = 'cis.dev393@gmail.com'
        VIRTUAL_ENV = "${env.WORKSPACE}/venv"
    }

    stages {

        
        // stage ('Checkout') {
        //     steps {
        //         checkout scm
        //     }
        // }
        

        stage ('Install_Requirements') {
            steps {
                sh """
                    echo ${SHELL}
                    [ -d venv ] && rm -rf venv
                    #virtualenv --python=python2.7 venv
                    virtualenv venv
                    #. venv/bin/activate
                    export PATH=${VIRTUAL_ENV}/bin:${PATH}
                    pip install --upgrade pip
                    pip install -r requirements.txt -r dev-requirements.txt
                    make clean
                """
            }
        }


        // stage ('Check_style') {
        //     steps {
        //         sh """
        //             if [ ! -d venv ] ; then

        //                virtualenv --python=python2.7 venv
        //             fi
        //             source venv/bin/activate
        //             export PYTHONPATH="$PWD:$PYTHONPATH"

        //             pip install pylint

        //             cd repo
        //             ### Need this because some strange control sequences when using default TERM=xterm
        //             export TERM="linux"

        //             ## || exit 0 because pylint only exits with 0 if everything is correct
        //             pylint --rcfile=pylint.cfg $(find . -maxdepth 1 -name "*.py" -print) MYMODULE/ > pylint.log || exit 0
        //         """
        //         step([$class: 'WarningsPublisher',
        //           parserConfigurations: [
        //           [
        //             parserName: 'pylint',
        //             pattern: 'report/pylint.log'
        //           ]],
        //           unstableTotalAll: '0',
        //           usePreviousBuildAsReference: true
        //         ])
        //     }
        // }

        stage('changes in script check') {
            steps {
                sh '''
                echo ${SHELL}
                '''
                // sudo /home/cis/.local/bin/nosetests --with-xunit tests
            }
        }

        stage('Test environment') {
            steps {
                sh '''
                echo ${SHELL}
                [ -d venv ] && rm -rf venv
                #virtualenv --python=python2.7 venv
                virtualenv venv
                #. venv/bin/activate
                export PATH=${VIRTUAL_ENV}/bin:${PATH}
                python setup.py install
                pip install pylint
                pip install radon
                pip install coverage
                '''
                // sudo /home/cis/.local/bin/nosetests --with-xunit tests
            }
        }



        stage('Pylint Checker'){
            steps{
                sh '''
                export TERM="linux"                
                pylint --rcfile=pylint.cfg $(find . -maxdepth 1 -name "*.py" -print) PyBitmessage/src > pylint.log || exit 0
                '''
            }
        }


        // stage('Nosetest'){
        //     steps{
        //         sh '''
        //         echo ${SHELL}
        //         [ -d venv ] && rm -rf venv
        //         #virtualenv --python=python2.7 venv
        //         virtualenv venv
        //         #. venv/bin/activate
        //         export PATH=${VIRTUAL_ENV}/bin:${PATH}
        //         python setup.py install
        //         sudo apt-get install python-mock python-nose python-coverage pylint
                
        //         '''
        //     }
        // }   

        // stage('Pylint Checker') {
        //     steps {
        //         sh '''
        //             echo ${SHELL}
        //             [ -d venv ] && rm -rf venv
        //             #virtualenv --python=python2.7 venv
        //             virtualenv venv
        //             #. venv/bin/activate
        //             export PATH=${VIRTUAL_ENV}/bin:${PATH}

        //             pip install pylint

                    
        //             export TERM="linux"

        //             ## || exit 0 because pylint only exits with 0 if everything is correct
        //             pylint --rcfile=pylint.cfg $(find . -maxdepth 1 -name "*.py" -print) Pybitmessage/ > pylint.log || exit 0
        //         '''
        //     }
        // }

        stage('Static code metrics') {
            steps {
                echo "Raw metrics"
                sh  ''' echo ${SHELL}
                        [ -d venv ] && rm -rf venv
                        #virtualenv --python=python2.7 venv
                        virtualenv venv
                        #. venv/bin/activate
                        export PATH=${VIRTUAL_ENV}/bin:${PATH}
                        python setup.py install
                        pip install radon
                        radon raw --json PyBitmessage/ > raw_report.json
                        radon cc --json PyBitmessage/ > cc_report.json
                        radon mi --json PyBitmessage/ > mi_report.json  
                    '''


                echo "Test coverage"
                sh  '''
                        echo ${SHELL}
                        [ -d venv ] && rm -rf venv
                        #virtualenv --python=python2.7 venv
                        virtualenv venv
                        #. venv/bin/activate
                        export PATH=${VIRTUAL_ENV}/bin:${PATH}
                        python setup.py install 
                        pip install coverage
                        coverage run src/bitmessagemain.py -t 1 1 2 3
                        python -m coverage xml -o PyBitmessage/coverage.xml
                    '''
                
                echo "Style check"
                sh  ''' echo ${SHELL}
                        [ -d venv ] && rm -rf venv
                        #virtualenv --python=python2.7 venv
                        virtualenv venv
                        #. venv/bin/activate
                        export PATH=${VIRTUAL_ENV}/bin:${PATH}
                        python setup.py install 
                        pip install pylint
                        pylint PyBitmessage || true
                    '''
            }
            post{
                always{
                    step([$class: 'CoberturaPublisher',
                                   autoUpdateHealth: false,
                                   autoUpdateStability: false,
                                   coberturaReportFile: 'PyBitmessage/coverage.xml',
                                   failNoReports: false,
                                   failUnhealthy: false,
                                   failUnstable: false,
                                   maxNumberOfBuilds: 10,
                                   onlyStable: false,
                                   sourceEncoding: 'ASCII',
                                   zoomCoverageChart: false])
                }
            }
        }

        stage('Unit tests') {
            steps {
                sh  ''' export PATH=${VIRTUAL_ENV}/bin:${PATH}
                        pip install pytest
                        pip install psutil
                        pip install python-prctl==1.5.0
                        python -m pytest --verbose --junit-xml results.xml
                    '''
            }
            post {
                always {
                    // Archive unit tests for the future
                    junit allowEmptyResults: true, testResults: 'results.xml'
                }
            }
        }

        stage('Setup Test') {
            steps {
                sh  ''' export PATH=${VIRTUAL_ENV}/bin:${PATH}
                        pip install pytest
                        pip install psutil
                        pip install python-prctl==1.5.0
                        python -m pytest --verbose --junit-xml results.xml
                    '''
            }
            post {
                always {
                    // Archive unit tests for the future
                    junit allowEmptyResults: true, testResults: 'results.xml'
                }
            }
        }
        // stage('Unit tests') {
        //     steps {
        //         sh  ''' source activate ${BUILD_TAG}
        //                 python -m pytest --verbose --junit-xml reports/unit_tests.xml
        //             '''
        //     }
        //     post {
        //         always {
        //             // Archive unit tests for the future
        //             junit (allowEmptyResults: true,
        //                   testResults: './reports/unit_tests.xml',
        //                   testResults: true)
        //         }
        //     }
        // }


        stage('Test Run') {
            steps {
                sh '''python src/bitmessagemain.py -t'''
            }
        }

        stage ('Cleanup') {
            steps {
                sh 'rm -rf venv'
            }
        }
    }


    post {
        failure {
            mail body: "${env.JOB_NAME} (${env.BUILD_NUMBER}) ${env.projectName} build error " +
                       "is here: ${env.BUILD_URL}\nStarted by ${env.BUILD_CAUSE}" ,
                 from: env.emailFrom,
                 //replyTo: env.emailFrom,
                 subject: "${env.projectName} ${env.JOB_NAME} (${env.BUILD_NUMBER}) build failed",
                 to: env.emailTo
        }
        success {
            mail body: "${env.JOB_NAME} (${env.BUILD_NUMBER}) ${env.projectName} build successful\n" +
                       "Started by ${env.BUILD_CAUSE}",
                 from: env.emailFrom,
                 //replyTo: env.emailFrom,
                 subject: "${env.projectName} ${env.JOB_NAME} (${env.BUILD_NUMBER}) build successful",
                 to: env.emailTo
        }

        
    }


}
