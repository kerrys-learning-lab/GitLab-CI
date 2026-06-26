SRC_DIR=context/usr/local/bin

# ============================================================================
function test_image_build_args_defaults() {
  export CI_COMMIT_REF_NAME=feat/73-this-is-my-task
  export CI_PIPELINE_IID=763
  export GITLABCI_RELEASE_TRAIN=1.2
  export GITLABCI_SEMANTIC_VERSION=1.2.3-rc+763

  local actual=$(${SRC_DIR}/ci-image-build-args.sh)

  assert_contains "--build-arg CI_COMMIT_REF_NAME=feat/73-this-is-my-task"  "${actual}"
  assert_contains "--build-arg CI_PIPELINE_IID=763"                         "${actual}"
  assert_contains "--build-arg GITLABCI_RELEASE_TRAIN=1.2"                  "${actual}"
  assert_contains "--build-arg GITLABCI_SEMANTIC_VERSION=1.2.3-rc+763"      "${actual}"
}


# ============================================================================
function test_image_build_args_custom() {
  export IMAGE_BUILD_ARG_FLOBBER=blam
  export IMAGE_BUILD_ARG_FLIM_FLAM=flim-flam

  local actual=$(${SRC_DIR}/ci-image-build-args.sh)

  assert_contains "--build-arg FLOBBER=blam"        "${actual}"
  assert_contains "--build-arg FLIM_FLAM=flim-flam" "${actual}"
}
