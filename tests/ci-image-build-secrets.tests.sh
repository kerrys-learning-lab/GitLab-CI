SRC_DIR=context/usr/local/bin

# ============================================================================
function set_up_before_script() {
  rm -rf .image-build/secrets
}


# ============================================================================
function test_image_build_secret_file() {
  export IMAGE_BUILD_SECRET_FILE_FOO_BAR=/foo/bar

  local actual=$(${SRC_DIR}/ci-image-build-secrets.sh)

  assert_contains "--secret id=foo-bar,src=/foo/bar"  "${actual}"
}


# ============================================================================
function test_image_build_secret_string() {
  export IMAGE_BUILD_SECRET_STRING_FOO_BAR="this is the secret value"

  EXPECTED_SECRET_FILE=.image-build/secrets/foo-bar

  local actual=$(${SRC_DIR}/ci-image-build-secrets.sh)

  assert_file_exists    "${EXPECTED_SECRET_FILE}"
  assert_file_contains  "${EXPECTED_SECRET_FILE}"                         "${IMAGE_BUILD_SECRET_STRING_FOO_BAR}"
  assert_contains       "--secret id=foo-bar,src=${EXPECTED_SECRET_FILE}" "${actual}"
}
