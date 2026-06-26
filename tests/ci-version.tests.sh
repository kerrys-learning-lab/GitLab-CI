SRC_DIR=context/usr/local/bin


# ----------------------------------------------------------------------------
function test_ci_version_release_tag() {
  export CI_COMMIT_TAG=v1.2.3
  export CI_COMMIT_REF_PROTECTED=true
  export CI_COMMIT_BRANCH=

  local actual=$(${SRC_DIR}/ci-semver.sh)

  assert_contains "GITLABCI_RELEASE_TRAIN=1.2"        "${actual}"
  assert_contains "GITLABCI_SEMANTIC_VERSION=1.2.3"   "${actual}"
  assert_contains "GITLABCI_SEMANTIC_VERSION_MAJOR=1" "${actual}"
  assert_contains "GITLABCI_SEMANTIC_VERSION_MINOR=2" "${actual}"
  assert_contains "GITLABCI_SEMANTIC_VERSION_PATCH=3" "${actual}"
}


# ----------------------------------------------------------------------------
function test_ci_version_unprotected_release_tag() {
  export CI_COMMIT_TAG=v1.2.3
  export CI_COMMIT_REF_PROTECTED=false
  export CI_COMMIT_BRANCH=

  ${SRC_DIR}/ci-semver.sh

  assert_unsuccessful_code
}


# ----------------------------------------------------------------------------
function test_ci_version_unprotected_release_branch() {
  export CI_COMMIT_BRANCH=release/1.2
  export CI_COMMIT_REF_PROTECTED=false
  export CI_COMMIT_TAG=

  ${SRC_DIR}/ci-semver.sh

  assert_exit_code 3
}


# ----------------------------------------------------------------------------
function test_ci_version_release_branch_with_no_tags() {
  export CI_COMMIT_BRANCH=release/1.2
  export CI_COMMIT_REF_PROTECTED=true
  export CI_PIPELINE_IID=42
  export CI_COMMIT_TAG=

  local actual=$(${SRC_DIR}/ci-semver.sh)

  assert_contains "GITLABCI_RELEASE_TRAIN=1.2"                            "${actual}"
  assert_contains "GITLABCI_SEMANTIC_VERSION=1.2.0-rc+${CI_PIPELINE_IID}" "${actual}"
  assert_contains "GITLABCI_SEMANTIC_VERSION_MAJOR=1"                     "${actual}"
  assert_contains "GITLABCI_SEMANTIC_VERSION_MINOR=2"                     "${actual}"
  assert_contains "GITLABCI_SEMANTIC_VERSION_PATCH=0"                     "${actual}"
}


# ----------------------------------------------------------------------------
function test_ci_version_release_branch_with_tags() {
  export CI_COMMIT_BRANCH=release/1.2
  export CI_COMMIT_REF_PROTECTED=true
  export CI_PIPELINE_IID=42
  export CI_COMMIT_TAG=
  export TAGS_FOR_RELEASE_TRAIN="v1.2.0  v1.2.1  v1.2.2"

  local actual=$(${SRC_DIR}/ci-semver.sh)

  assert_contains "GITLABCI_RELEASE_TRAIN=1.2"                            "${actual}"
  assert_contains "GITLABCI_SEMANTIC_VERSION=1.2.3-rc+${CI_PIPELINE_IID}" "${actual}"
  assert_contains "GITLABCI_SEMANTIC_VERSION_MAJOR=1"                     "${actual}"
  assert_contains "GITLABCI_SEMANTIC_VERSION_MINOR=2"                     "${actual}"
  assert_contains "GITLABCI_SEMANTIC_VERSION_PATCH=3"                     "${actual}"
}


# ----------------------------------------------------------------------------
function test_ci_version_default_branch() {
  export CI_COMMIT_TAG=
  export CI_COMMIT_BRANCH=main
  export CI_COMMIT_REF_NAME=${CI_COMMIT_BRANCH}
  export CI_COMMIT_REF_PROTECTED=true
  export CI_DEFAULT_BRANCH=${CI_COMMIT_BRANCH}
  export CI_PIPELINE_IID=42
  export CI_COMMIT_TAG=

  local actual=$(${SRC_DIR}/ci-semver.sh)

  assert_contains "GITLABCI_RELEASE_TRAIN=main"                             "${actual}"
  assert_contains "GITLABCI_SEMANTIC_VERSION=0.0.0-main+${CI_PIPELINE_IID}" "${actual}"
  assert_contains "GITLABCI_SEMANTIC_VERSION_MAJOR=0"                       "${actual}"
  assert_contains "GITLABCI_SEMANTIC_VERSION_MINOR=0"                       "${actual}"
  assert_contains "GITLABCI_SEMANTIC_VERSION_PATCH=0"                       "${actual}"
}


# ----------------------------------------------------------------------------
function test_ci_version_developer_branch() {
  export CI_COMMIT_BRANCH=feat/18-developer-doing-work
  export CI_COMMIT_REF_NAME=${CI_COMMIT_BRANCH}
  export CI_COMMIT_REF_PROTECTED=false
  export CI_DEFAULT_BRANCH=main
  export CI_PIPELINE_IID=42
  export CI_COMMIT_TAG=

  local actual=$(${SRC_DIR}/ci-semver.sh)

  assert_contains "GITLABCI_SEMANTIC_VERSION_MAJOR=0"                                               "${actual}"
  assert_contains "GITLABCI_SEMANTIC_VERSION_MINOR=0"                                               "${actual}"
  assert_contains "GITLABCI_SEMANTIC_VERSION_PATCH=0"                                               "${actual}"
  assert_contains "GITLABCI_SEMANTIC_VERSION=0.0.0-feat-18-developer-doing-work+${CI_PIPELINE_IID}" "${actual}"
}


# ----------------------------------------------------------------------------
function test_ci_version_release_tag_cli_args() {
  export CI_COMMIT_TAG=v1.2.3
  export CI_COMMIT_REF_PROTECTED=true
  export CI_COMMIT_BRANCH=

  local actual_release_train=$(${SRC_DIR}/ci-semver.sh --release-train)
  local actual_semantic_version=$(${SRC_DIR}/ci-semver.sh --semantic-version)

  assert_equals "1.2"   "${actual_release_train}"
  assert_equals "1.2.3" "${actual_semantic_version}"
}


# ----------------------------------------------------------------------------
function test_ci_version_release_branch_cli_args() {
  export CI_COMMIT_BRANCH=release/1.2
  export CI_COMMIT_REF_PROTECTED=true
  export CI_PIPELINE_IID=42
  export CI_COMMIT_TAG=

  local actual_release_train=$(${SRC_DIR}/ci-semver.sh --release-train)
  local actual_semantic_version=$(${SRC_DIR}/ci-semver.sh --semantic-version)

  assert_equals "1.2"         "${actual_release_train}"
  assert_equals "1.2.0-rc+42" "${actual_semantic_version}"
}


# ----------------------------------------------------------------------------
function test_ci_version_default_branch_cli_args() {
  export CI_COMMIT_TAG=
  export CI_COMMIT_BRANCH=main
  export CI_COMMIT_REF_NAME=${CI_COMMIT_BRANCH}
  export CI_COMMIT_REF_PROTECTED=true
  export CI_DEFAULT_BRANCH=${CI_COMMIT_BRANCH}
  export CI_PIPELINE_IID=42
  export CI_COMMIT_TAG=

  local actual_release_train=$(${SRC_DIR}/ci-semver.sh --release-train)
  local actual_semantic_version=$(${SRC_DIR}/ci-semver.sh --semantic-version)

  assert_equals "main"          "${actual_release_train}"
  assert_equals "0.0.0-main+42" "${actual_semantic_version}"
}


# ----------------------------------------------------------------------------
function test_ci_version_developer_branch_cli_args() {
  export CI_COMMIT_BRANCH=feat/18-developer-doing-work
  export CI_COMMIT_REF_NAME=${CI_COMMIT_BRANCH}
  export CI_COMMIT_REF_PROTECTED=false
  export CI_DEFAULT_BRANCH=main
  export CI_PIPELINE_IID=42
  export CI_COMMIT_TAG=

  local actual_release_train=$(${SRC_DIR}/ci-semver.sh --release-train)
  local actual_semantic_version=$(${SRC_DIR}/ci-semver.sh --semantic-version)

  assert_empty "${actual_release_train}"
  assert_equals "0.0.0-feat-18-developer-doing-work+42" "${actual_semantic_version}"
}


# ----------------------------------------------------------------------------
function test_ci_version_cli_error() {
  ${SRC_DIR}/ci-semver.sh --foo

  assert_unsuccessful_code
}
