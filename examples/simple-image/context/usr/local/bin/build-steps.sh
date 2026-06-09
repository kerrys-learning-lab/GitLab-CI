EXPECTED_BUILD_ARG_VALUE=blam
EXPECTED_PASSWORD_VALUE=foo-is-the-password
ACTUAL_BUILD_ARG_VALUE=${FLOBBER}
ACTUAL_PASSWORD_VALUE=

mkdir -p ${IMAGE_UNIT_TEST_WORKING_DIR}

if [[ "${EXPECTED_BUILD_ARG_VALUE}" != "${ACTUAL_BUILD_ARG_VALUE}" ]]; then
    echo "ERROR:  Assertion failed within Dockerfile"               | tee -a ${BUILD_ARG_FAILURE_FILE}
    echo "        Expected build-arg: ${EXPECTED_BUILD_ARG_VALUE}"  | tee -a ${BUILD_ARG_FAILURE_FILE}
    echo "        Actual build-arg:   ${ACTUAL_BUILD_ARG_VALUE}"    | tee -a ${BUILD_ARG_FAILURE_FILE}
fi


if [[ -f /run/secrets/foo-password ]]; then
    ACTUAL_PASSWORD_VALUE=$(cat /run/secrets/foo-password)
fi

if [[ "${EXPECTED_PASSWORD_VALUE}" != "${ACTUAL_PASSWORD_VALUE//[[:space:]]/}" ]]; then
    echo "ERROR:  Assertion failed within Dockerfile"           | tee -a ${SECRET_FAILURE_FILE}
    echo "        Expected secret: ${EXPECTED_PASSWORD_VALUE}"  | tee -a ${SECRET_FAILURE_FILE}
    echo "        Actual secret:   ${ACTUAL_PASSWORD_VALUE}"    | tee -a ${SECRET_FAILURE_FILE}
fi
