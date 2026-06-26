#! /bin/bash

. $(dirname $(realpath $0))/log.sh
. $(dirname $(realpath $0))/str-slug.sh

#                                  +------------------------------------- Major (group 1)
#                                  |
#                                  |              +---------------------- Minor (group 2)
#                                  |              |
#                                  |              |                +----- Patch (group 3)
#                                  |              |                |
#                             vvvvvvvvvvvv    vvvvvvvvvvvv    vvvvvvvvvvvv
readonly RELEASE_TAG_REGEX='v([[:digit:]]+)\.([[:digit:]]+)\.([[:digit:]]+)'

#                                            +---------------------------- major (group 1)
#                                            |
#                                            |               +------------ minor (group 2)
#                                            |               |
#                                            |               |
#                                            |               |
#                                            |               |
#                                       vvvvvvvvvvvv    vvvvvvvvvvvv
readonly RELEASE_BRANCH_REGEX='release/([[:digit:]]+)\.([[:digit:]]+)'

COMMAND=print-env

GITLABCI_PIPELINE_TIMESTAMP=${GITLABCI_PIPELINE_TIMESTAMP:-$(date --iso-8601=seconds)}
GITLABCI_RELEASE_TRAIN=
GITLABCI_SEMANTIC_VERSION=
GITLABCI_SEMANTIC_VERSION_MAJOR=
GITLABCI_SEMANTIC_VERSION_MINOR=
GITLABCI_SEMANTIC_VERSION_PATCH=

OUTPUT_VARS=()
OUTPUT_VARS+=(GITLABCI_PIPELINE_TIMESTAMP)
OUTPUT_VARS+=(GITLABCI_RELEASE_TRAIN)
OUTPUT_VARS+=(GITLABCI_SEMANTIC_VERSION)
OUTPUT_VARS+=(GITLABCI_SEMANTIC_VERSION_MAJOR)
OUTPUT_VARS+=(GITLABCI_SEMANTIC_VERSION_MINOR)
OUTPUT_VARS+=(GITLABCI_SEMANTIC_VERSION_PATCH)


# ============================================================================
function process_ci_commit_tag() {
  if [[ ${CI_COMMIT_TAG} =~ ${RELEASE_TAG_REGEX} ]]; then
    if [[ "${CI_COMMIT_REF_PROTECTED}" == "false" ]]; then
      log_error "❌  Release tags (vX.Y.Z) should be protected ❌"
      exit 3
    fi

    GITLABCI_SEMANTIC_VERSION_MAJOR=${BASH_REMATCH[1]}
    GITLABCI_SEMANTIC_VERSION_MINOR=${BASH_REMATCH[2]}
    GITLABCI_SEMANTIC_VERSION_PATCH=${BASH_REMATCH[3]}

    GITLABCI_RELEASE_TRAIN=${GITLABCI_SEMANTIC_VERSION_MAJOR}.${GITLABCI_SEMANTIC_VERSION_MINOR}
    GITLABCI_SEMANTIC_VERSION=${GITLABCI_RELEASE_TRAIN}.${GITLABCI_SEMANTIC_VERSION_PATCH}

  elif [[ "${CI_COMMIT_REF_PROTECTED}" == "true" ]]; then
    log_error "❌  Protected tag (${CI_COMMIT_TAG}) is not a valid SemVer ❌"
    log_error "    Expected vX.Y.Z"
    exit 3
  fi
}


# ============================================================================
function process_release_branch() {
  if [[ ${CI_COMMIT_BRANCH} =~ ${RELEASE_BRANCH_REGEX} ]]; then
    if [[ "${CI_COMMIT_REF_PROTECTED}" == "false" ]]; then
      log_error "❌  Release branches (release/X.Y) should be protected ❌"
      exit 3
    fi

    GITLABCI_SEMANTIC_VERSION_MAJOR=${BASH_REMATCH[1]}
    GITLABCI_SEMANTIC_VERSION_MINOR=${BASH_REMATCH[2]}
    GITLABCI_SEMANTIC_VERSION_PATCH=0

    GITLABCI_RELEASE_TRAIN=${GITLABCI_SEMANTIC_VERSION_MAJOR}.${GITLABCI_SEMANTIC_VERSION_MINOR}

    # NOTE: TAGS_FOR_RELEASE_TRAIN will only ever be pre-defined when testing
    TAGS_FOR_RELEASE_TRAIN=${TAGS_FOR_RELEASE_TRAIN:-$(git tag -l "v${GITLABCI_RELEASE_TRAIN}.*")}
    if [[ -n "${TAGS_FOR_RELEASE_TRAIN}" ]]; then
      for tag in ${TAGS_FOR_RELEASE_TRAIN}; do
        if [[ ${tag} =~ ${RELEASE_TAG_REGEX} ]]; then
          tag_patch_level=${BASH_REMATCH[3]}
          if [[ ${tag_patch_level} -gt ${GITLABCI_SEMANTIC_VERSION_PATCH} ]]; then
            GITLABCI_SEMANTIC_VERSION_PATCH=${tag_patch_level}
          fi
        fi
      done

      # But, this is a release candidate for the *next* patch:
      GITLABCI_SEMANTIC_VERSION_PATCH=$((${GITLABCI_SEMANTIC_VERSION_PATCH} + 1))
    fi

    GITLABCI_SEMANTIC_VERSION=${GITLABCI_RELEASE_TRAIN}.${GITLABCI_SEMANTIC_VERSION_PATCH}-rc+${CI_PIPELINE_IID}
  fi
}


# ============================================================================
function process_other_ci_commit_ref() {
  if [[ ${DEFAULT_SEMVER_PREFIX:-v0.0.0} =~ ${RELEASE_TAG_REGEX} ]]; then
    GITLABCI_SEMANTIC_VERSION_MAJOR=${BASH_REMATCH[1]}
    GITLABCI_SEMANTIC_VERSION_MINOR=${BASH_REMATCH[2]}
    GITLABCI_SEMANTIC_VERSION_PATCH=${BASH_REMATCH[3]}

    SEMANTIC_VERSION_COMMIT_SLUG=$(str-slug ${CI_COMMIT_REF_NAME})
    GITLABCI_SEMANTIC_VERSION=${GITLABCI_SEMANTIC_VERSION_MAJOR}.${GITLABCI_SEMANTIC_VERSION_MINOR}.${GITLABCI_SEMANTIC_VERSION_PATCH}-${SEMANTIC_VERSION_COMMIT_SLUG}+${CI_PIPELINE_IID}

    if [[ ${CI_COMMIT_REF_PROTECTED} == true ]]; then
      GITLABCI_RELEASE_TRAIN=${SEMANTIC_VERSION_COMMIT_SLUG}
    fi

  fi
}


# ============================================================================
function ci-semver() {
  if [[ -n "${CI_COMMIT_TAG}" ]]; then
    process_ci_commit_tag
  else
    process_release_branch

    # If 'process_release_branch' was successful, GITLABCI_SEMANTIC_VERSION will
    # be defined...
    if [[ -z "${GITLABCI_SEMANTIC_VERSION}" ]]; then
      # If GITLABCI_SEMANTIC_VERSION isn't defined, then it wasn't a release
      # branch...

      if [[ "${CI_COMMIT_REF_PROTECTED}" == true && ${CI_COMMIT_BRANCH} != ${CI_DEFAULT_BRANCH} ]]; then
          log_error "❌  Protected branch (${CI_COMMIT_BRANCH}) is not valid ❌"
          log_error "    Expected: 'release/X.Y' or ${CI_DEFAULT_BRANCH}"
          exit 3
      fi

      process_other_ci_commit_ref

      if [[ -z "${GITLABCI_SEMANTIC_VERSION}" ]]; then
        log_error "❌  Unable to infer semantic version and DEFAULT_SEMVER_PREFIX is not valid ❌"
        log_error "    Expected: ${RELEASE_TAG_REGEX}"
        log_error "    Actual:   ${DEFAULT_SEMVER_PREFIX}"
        exit 6
      fi

    fi
  fi
}


# ============================================================================
function print-env() {
  for var in ${OUTPUT_VARS[@]}; do
    echo "${var}=${!var}"
  done
}


# ============================================================================
while [[ $# -gt 0 ]]; do
  case "$1" in
    -e|--env)
      COMMAND=print-env
      shift
      ;;
    -s|--semver|--semantic-version)
      COMMAND=GITLABCI_SEMANTIC_VERSION
      shift
      ;;
    -r|--release-train)
      COMMAND=GITLABCI_RELEASE_TRAIN
      shift
      ;;
    -h|--help)
      print-help
      shift
      exit 0
      ;;
    *)
      print-help
      exit 42
      shift
      ;;
  esac
done


ci-semver

if [[ "${COMMAND}" == "GITLABCI_"* ]]; then
  echo ${!COMMAND}
else
  ${COMMAND}
fi
