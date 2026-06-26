SRC_DIR=context/usr/local/bin


# ============================================================================
function test_image_cli_labels() {
  export CI_PROJECT_TITLE=blah-blah
  export CI_PROJECT_DESCRIPTION="This is the blah blah project"
  export CI_PROJECT_URL=https://foo.com/path/to/blah-blah
  export CI_COMMIT_REF_NAME=release/1.2
  export CI_COMMIT_SHA=123456789abcdefgh

  local actual=$(${SRC_DIR}/ci-image-labels.sh)

  assert_contains "--label org.opencontainers.image.title=${CI_PROJECT_TITLE}"              "${actual}"
  assert_contains "--label org.opencontainers.image.description=${CI_PROJECT_DESCRIPTION}"  "${actual}"
  assert_contains "--label org.opencontainers.image.url=${CI_PROJECT_URL}"                  "${actual}"
  assert_contains "--label org.opencontainers.image.version=release-1.2"                    "${actual}"
  assert_contains "--label org.opencontainers.image.revision=${CI_COMMIT_SHA}"              "${actual}"
}


# ============================================================================
function test_image_cli_labels_predefined_date() {
  export CI_PROJECT_TITLE=blah-blah
  export CI_PROJECT_DESCRIPTION="This is the blah blah project"
  export CI_PROJECT_URL=https://foo.com/path/to/blah-blah
  export CI_COMMIT_REF_NAME=release/1.2
  export CI_COMMIT_SHA=123456789abcdefgh
  export GITLABCI_PIPELINE_TIMESTAMP=2026-06-25T11:58:26-06:00

  local actual=$(${SRC_DIR}/ci-image-labels.sh)

  assert_contains "--label org.opencontainers.image.title=${CI_PROJECT_TITLE}"              "${actual}"
  assert_contains "--label org.opencontainers.image.description=${CI_PROJECT_DESCRIPTION}"  "${actual}"
  assert_contains "--label org.opencontainers.image.url=${CI_PROJECT_URL}"                  "${actual}"
  assert_contains "--label org.opencontainers.image.version=release-1.2"                    "${actual}"
  assert_contains "--label org.opencontainers.image.revision=${CI_COMMIT_SHA}"              "${actual}"
  assert_contains "--label org.opencontainers.image.created=${GITLABCI_PIPELINE_TIMESTAMP}" "${actual}"
}
