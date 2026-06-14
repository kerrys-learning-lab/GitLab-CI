#! /usr/local/bin/bash

set -e

cp /etc/image-unit-test/* /var/tmp/

ls -alF /var/tmp

TEST_RESULT_XML_FILE=/var/tmp/test-results.xml
PASSED_COUNT=0
FAILED_COUNT=0
if [[ -f ${BUILD_ARG_FAILURE_FILE} ]]; then
    FAILED_COUNT=$((FAILED_COUNT+1))
    FAILURE_MSG=$(tr '\n' '@' < ${BUILD_ARG_FAILURE_FILE})
    FAILURE_MSG=$(echo "${FAILURE_MSG}" | sed 's#@#<br/>#g' )
    XML_FAILURE_MSG="<failure message=\"Assertion failed for '--build-arg'\" type=\"AssertionError\">${FAILURE_MSG}</failure>"
    sed -i "s#BUILD_ARG_FAILURE_MSG#${XML_FAILURE_MSG}#g" ${TEST_RESULT_XML_FILE}
else
    PASSED_COUNT=$((PASSED_COUNT+1))
    sed -i "s/BUILD_ARG_FAILURE_MSG//g" ${TEST_RESULT_XML_FILE}
fi
if [[ -f ${SECRET_FAILURE_FILE} ]]; then
    FAILED_COUNT=$((FAILED_COUNT+1))
    FAILURE_MSG=$(tr '\n' '@' < ${SECRET_FAILURE_FILE})
    FAILURE_MSG=$(echo "${FAILURE_MSG}" | sed 's#@#<br/>#g' )
    XML_FAILURE_MSG="<failure message=\"Assertion failed for '--secret'\" type=\"AssertionError\">${FAILURE_MSG}</failure>"
    sed -i "s#SECRET_FAILURE_MSG#${XML_FAILURE_MSG}#g" ${TEST_RESULT_XML_FILE}
else
    PASSED_COUNT=$((PASSED_COUNT+1))
    sed -i "s/SECRET_FAILURE_MSG//g" ${TEST_RESULT_XML_FILE}
fi

sed -i "s/PASSED_COUNT/${PASSED_COUNT}/g" ${TEST_RESULT_XML_FILE}
sed -i "s/FAILED_COUNT/${FAILED_COUNT}/g" ${TEST_RESULT_XML_FILE}

exit ${FAILED_COUNT}
