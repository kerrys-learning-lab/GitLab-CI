

# ----------------------------------------------------------------------------
function test_pipeline_version_release_tag() {
  CI_COMMIT_TAG=v1.2.3
  CI_COMMIT_REF_PROTECTED=true
  CI_COMMIT_BRANCH=

  fn_calculate_pipeline_version

  assert_equals "1.2"     "${GITLABCI_RELEASE_TRAIN}"
  assert_equals "1.2.3"   "${GITLABCI_SEMANTIC_VERSION}"
  assert_equals "1"       "${GITLABCI_SEMANTIC_VERSION_MAJOR}"
  assert_equals "2"       "${GITLABCI_SEMANTIC_VERSION_MINOR}"
  assert_equals "3"       "${GITLABCI_SEMANTIC_VERSION_PATCH}"
}


# ----------------------------------------------------------------------------
function test_pipeline_version_unprotected_release_tag() {
  CI_COMMIT_TAG=v1.2.3
  CI_COMMIT_REF_PROTECTED=false
  CI_COMMIT_BRANCH=

  # NOTE: We use sub-shell syntax in order to catch the exit code without
  #       killing the actual bashunit process:
  (fn_calculate_pipeline_version)

  assert_exit_code 3
}


# ----------------------------------------------------------------------------
function test_pipeline_version_unprotected_release_branch() {
  CI_COMMIT_BRANCH=release/1.2
  CI_COMMIT_REF_PROTECTED=false
  CI_COMMIT_TAG=

  # NOTE: We use sub-shell syntax in order to catch the exit code without
  #       killing the actual bashunit process:
  (fn_calculate_pipeline_version)

  assert_exit_code 3
}


# ----------------------------------------------------------------------------
function test_pipeline_version_release_branch_with_no_tags() {
  CI_COMMIT_BRANCH=release/1.2
  CI_COMMIT_REF_PROTECTED=true
  CI_PIPELINE_IID=42
  CI_COMMIT_TAG=

  fn_calculate_pipeline_version

  assert_equals "1.2"                         "${GITLABCI_RELEASE_TRAIN}"
  assert_equals "1.2.0-rc+${CI_PIPELINE_IID}" "${GITLABCI_SEMANTIC_VERSION}"
  assert_equals "1"                           "${GITLABCI_SEMANTIC_VERSION_MAJOR}"
  assert_equals "2"                           "${GITLABCI_SEMANTIC_VERSION_MINOR}"
  assert_equals "0"                           "${GITLABCI_SEMANTIC_VERSION_PATCH}"
}


# ----------------------------------------------------------------------------
function test_pipeline_version_release_branch_with_tags() {
  CI_COMMIT_BRANCH=release/1.2
  CI_COMMIT_REF_PROTECTED=true
  CI_PIPELINE_IID=42
  CI_COMMIT_TAG=
  TAGS_FOR_RELEASE_TRAIN="v1.2.0  v1.2.1  v1.2.2"

  fn_calculate_pipeline_version

  assert_equals "1.2"                         "${GITLABCI_RELEASE_TRAIN}"
  assert_equals "1.2.3-rc+${CI_PIPELINE_IID}" "${GITLABCI_SEMANTIC_VERSION}"
  assert_equals "1"                           "${GITLABCI_SEMANTIC_VERSION_MAJOR}"
  assert_equals "2"                           "${GITLABCI_SEMANTIC_VERSION_MINOR}"
  assert_equals "3"                           "${GITLABCI_SEMANTIC_VERSION_PATCH}"
}


# ----------------------------------------------------------------------------
function test_pipeline_version_default_branch() {
  CI_COMMIT_TAG=
  CI_COMMIT_BRANCH=main
  CI_COMMIT_REF_NAME=${CI_COMMIT_BRANCH}
  CI_COMMIT_REF_PROTECTED=true
  CI_DEFAULT_BRANCH=${CI_COMMIT_BRANCH}
  CI_PIPELINE_IID=42
  CI_COMMIT_TAG=

  fn_calculate_pipeline_version

  assert_equals "main"                          "${GITLABCI_RELEASE_TRAIN}"
  assert_equals "0.0.0-main+${CI_PIPELINE_IID}" "${GITLABCI_SEMANTIC_VERSION}"
  assert_equals "0"                             "${GITLABCI_SEMANTIC_VERSION_MAJOR}"
  assert_equals "0"                             "${GITLABCI_SEMANTIC_VERSION_MINOR}"
  assert_equals "0"                             "${GITLABCI_SEMANTIC_VERSION_PATCH}"
}


# ----------------------------------------------------------------------------
function test_pipeline_version_developer_branch() {
  CI_COMMIT_BRANCH=feat/18-developer-doing-work
  CI_COMMIT_REF_NAME=${CI_COMMIT_BRANCH}
  CI_COMMIT_REF_PROTECTED=false
  CI_DEFAULT_BRANCH=main
  CI_PIPELINE_IID=42
  CI_COMMIT_TAG=

  fn_calculate_pipeline_version

  assert_empty  "${GITLABCI_RELEASE_TRAIN}"
  assert_equals "0"                                                     "${GITLABCI_SEMANTIC_VERSION_MAJOR}"
  assert_equals "0"                                                     "${GITLABCI_SEMANTIC_VERSION_MINOR}"
  assert_equals "0"                                                     "${GITLABCI_SEMANTIC_VERSION_PATCH}"
  assert_equals "0.0.0-feat-18-developer-doing-work+${CI_PIPELINE_IID}" "${GITLABCI_SEMANTIC_VERSION}"
}
