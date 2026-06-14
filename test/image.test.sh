# ============================================================================
function set_up_before_script() {
  rm -rf .image-build/secrets

  TMP_FAKE_DOCKERFILE=$(mktemp)
}


# ============================================================================
function test_image_full_name_default() {
  CI_REGISTRY_IMAGE=foo/bar/baz
  CI_PIPELINE_IID=42

  EXPECTED_FULL_NAME=${CI_REGISTRY_IMAGE}
  EXPECTED_VERSION=build.${CI_PIPELINE_IID}
  EXPECTED_FULL_URI=${EXPECTED_FULL_NAME}:${EXPECTED_VERSION}

  fn_image_as_built_name_components

  assert_equals "${EXPECTED_FULL_NAME}" "${IMAGE_FULL_NAME}"
  assert_equals "${EXPECTED_VERSION}"   "${IMAGE_AS_BUILT_VERSION}"
  assert_equals "${EXPECTED_FULL_URI}"  "${IMAGE_AS_BUILT_URI}"
}


# ============================================================================
function test_image_full_name_custom() {
  CI_REGISTRY_IMAGE=foo/bar/baz
  CI_PIPELINE_IID=42
  IMAGE_BUILD_NAME=bop

  EXPECTED_FULL_NAME=${CI_REGISTRY_IMAGE}/${IMAGE_BUILD_NAME}
  EXPECTED_VERSION=build.${CI_PIPELINE_IID}
  EXPECTED_FULL_URI=${EXPECTED_FULL_NAME}:${EXPECTED_VERSION}

  fn_image_as_built_name_components

  assert_equals "${EXPECTED_FULL_NAME}" "${IMAGE_FULL_NAME}"
  assert_equals "${EXPECTED_VERSION}"   "${IMAGE_AS_BUILT_VERSION}"
  assert_equals "${EXPECTED_FULL_URI}"  "${IMAGE_AS_BUILT_URI}"
}


# ============================================================================
function test_image_cli_tag_default() {
  CI_REGISTRY_IMAGE=foo/bar/baz
  CI_PIPELINE_IID=42

  EXPECTED_FULL_NAME=${CI_REGISTRY_IMAGE}
  EXPECTED_VERSION=build.${CI_PIPELINE_IID}
  EXPECTED_FULL_URI=${EXPECTED_FULL_NAME}:build.${CI_PIPELINE_IID}

  fn_image_as_built_name_components
  fn_image_calculate_build_cli

  assert_contains "--tag ${EXPECTED_FULL_URI}" "${IMAGE_BUILD_CLI_ARGS[*]}"
}


# ============================================================================
function test_image_cli_tag_custom() {
  CI_REGISTRY_IMAGE=foo/bar/baz
  CI_PIPELINE_IID=42
  IMAGE_BUILD_NAME=bop

  EXPECTED_FULL_NAME=${CI_REGISTRY_IMAGE}/${IMAGE_BUILD_NAME}
  EXPECTED_VERSION=build.${CI_PIPELINE_IID}
  EXPECTED_FULL_URI=${EXPECTED_FULL_NAME}:build.${CI_PIPELINE_IID}

  fn_image_as_built_name_components
  fn_image_calculate_build_cli

  assert_contains "--tag ${EXPECTED_FULL_URI}" "${IMAGE_BUILD_CLI_ARGS[*]}"
}


# ============================================================================
function test_image_cli_dockerfile() {
  fn_image_calculate_build_cli

  EXPECTED_DOCKERFILE_ARG=./Dockerfile

  assert_contains "--file ${EXPECTED_DOCKERFILE_ARG}" "${IMAGE_BUILD_CLI_ARGS[*]}"
}


# ============================================================================
function test_image_cli_custom_dockerfile_and_context() {
  IMAGE_BUILD_CONTEXT=$(dirname ${TMP_FAKE_DOCKERFILE})
  IMAGE_BUILD_DOCKERFILE=$(basename ${TMP_FAKE_DOCKERFILE})

  fn_image_calculate_build_cli

  EXPECTED_CONTEXT_ARG=${IMAGE_BUILD_CONTEX}
  EXPECTED_DOCKERFILE_ARG=${TMP_FAKE_DOCKERFILE}

  assert_contains "--file ${EXPECTED_DOCKERFILE_ARG}" "${IMAGE_BUILD_CLI_ARGS[*]}"
  assert_contains "${EXPECTED_CONTEXT_ARG}"           "${IMAGE_BUILD_CLI_ARGS[*]}"
}


# ============================================================================
function test_image_cli_custom_target() {
  IMAGE_BUILD_TARGET=foo

  fn_image_calculate_build_cli

  assert_contains "--target ${IMAGE_BUILD_TARGET}" "${IMAGE_BUILD_CLI_ARGS[*]}"
}


# ============================================================================
function test_image_cli_custom_ignorefile_and_context() {
  IMAGE_BUILD_CONTEXT=$(dirname ${TMP_FAKE_DOCKERFILE})
  IMAGE_BUILD_IGNOREFILE=$(basename ${TMP_FAKE_DOCKERFILE})

  fn_image_calculate_build_cli

  EXPECTED_CONTEXT_ARG=${IMAGE_BUILD_CONTEX}
  EXPECTED_IGNOREFILE_ARG=${TMP_FAKE_DOCKERFILE}

  assert_contains "--ignorefile ${EXPECTED_IGNOREFILE_ARG}" "${IMAGE_BUILD_CLI_ARGS[*]}"
  assert_contains "${EXPECTED_CONTEXT_ARG}"                 "${IMAGE_BUILD_CLI_ARGS[*]}"
}


# ============================================================================
function test_image_cli_labels() {
  CI_PROJECT_TITLE=blah-blah
  CI_PROJECT_DESCRIPTION="This is the blah blah project"
  CI_PROJECT_URL=https://foo.com/path/to/blah-blah
  CI_COMMIT_REF_NAME=release/1.2
  CI_COMMIT_SHA=123456789abcdefgh

  fn_image_calculate_build_cli

  assert_contains "--label org.opencontainers.image.title=${CI_PROJECT_TITLE}"              "${IMAGE_BUILD_CLI_ARGS[*]}"
  assert_contains "--label org.opencontainers.image.description=${CI_PROJECT_DESCRIPTION}"  "${IMAGE_BUILD_CLI_ARGS[*]}"
  assert_contains "--label org.opencontainers.image.url=${CI_PROJECT_URL}"                  "${IMAGE_BUILD_CLI_ARGS[*]}"
  assert_contains "--label org.opencontainers.image.version=release-1.2"                    "${IMAGE_BUILD_CLI_ARGS[*]}"
  assert_contains "--label org.opencontainers.image.revision=${CI_COMMIT_SHA}"              "${IMAGE_BUILD_CLI_ARGS[*]}"
}


# ============================================================================
function test_image_build_args() {
  CI_COMMIT_REF_NAME=feat/73-this-is-my-task
  CI_PIPELINE_IID=763
  IMAGE_BUILD_ARG_FLOBBER=blam
  IMAGE_BUILD_ARG_FLIM_FLAM=flim-flam
  GITLABCI_RELEASE_TRAIN=1.2
  GITLABCI_SEMANTIC_VERSION=1.2.3-rc+763

  fn_image_calculate_build_cli

  assert_contains "--build-arg CI_COMMIT_REF_NAME=feat/73-this-is-my-task"  "${IMAGE_BUILD_CLI_ARGS[*]}"
  assert_contains "--build-arg CI_PIPELINE_IID=763"                         "${IMAGE_BUILD_CLI_ARGS[*]}"
  assert_contains "--build-arg FLOBBER=blam"                                "${IMAGE_BUILD_CLI_ARGS[*]}"
  assert_contains "--build-arg FLIM_FLAM=flim-flam"                         "${IMAGE_BUILD_CLI_ARGS[*]}"
  assert_contains "--build-arg GITLABCI_RELEASE_TRAIN=1.2"                           "${IMAGE_BUILD_CLI_ARGS[*]}"
  assert_contains "--build-arg GITLABCI_SEMANTIC_VERSION=1.2.3-rc+763"               "${IMAGE_BUILD_CLI_ARGS[*]}"
}


# ============================================================================
function test_image_build_secret_file() {
  IMAGE_BUILD_SECRET_FILE_FOO_BAR=/foo/bar

  fn_image_calculate_build_cli

  assert_contains "--secret id=foo-bar,src=/foo/bar"  "${IMAGE_BUILD_CLI_ARGS[*]}"
}


# ============================================================================
function test_image_build_secret_string() {
  IMAGE_BUILD_SECRET_STRING_FOO_BAR="this is the secret value"

  EXPECTED_SECRET_FILE=.image-build/secrets/foo-bar

  fn_image_calculate_build_cli

  assert_file_exists    "${EXPECTED_SECRET_FILE}"
  assert_file_contains  "${EXPECTED_SECRET_FILE}"                         "${IMAGE_BUILD_SECRET_STRING_FOO_BAR}"
  assert_contains       "--secret id=foo-bar,src=${EXPECTED_SECRET_FILE}" "${IMAGE_BUILD_CLI_ARGS[*]}"
}
