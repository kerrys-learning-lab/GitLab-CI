# ============================================================================
FROM docker.io/bash:5.3.12-alpine3.23 AS base

FROM base AS unittest

ENV IMAGE_UNIT_TEST_WORKING_DIR=/var/lib/image-unit-test
ENV BUILD_ARG_FAILURE_FILE=${IMAGE_UNIT_TEST_WORKING_DIR}/build-arg-test-failed
ENV SECRET_FAILURE_FILE=${IMAGE_UNIT_TEST_WORKING_DIR}/secret-test-failed

COPY context/   /

ARG FLOBBER="not-provided"
RUN --mount=type=secret,id=foo-password,required=false  \
    /usr/local/bin/build-steps.sh

ENTRYPOINT ["/usr/local/bin/create-test-results.sh"]

FROM base
