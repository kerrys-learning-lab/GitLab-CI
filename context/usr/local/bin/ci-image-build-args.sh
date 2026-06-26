#! /bin/bash
#
# Usage:  ci-image-build-args.sh [OPTIONS]
#
# Description:  Creates build-args suitable for injecting into an image build
#               command.
#
# Options:
#   -s, --separator <sep>       Specifies how to separate each resulting
#                               argument.  Must be one of 'null', 'newline',
#                               'space'.  Default: 'space'
#   -h, --help                  Shows this help message
# ============================================================================


NULL_SEPARATOR='%s\0'
NEWLINE_SEPARATOR='%s\n'
SPACE_SEPARATOR='%s '
SEPARATOR=${SPACE_SEPARATOR}


# ============================================================================
function ci-image-build-args () {
  # Selected values from the Pipeline are always injected:
  for var_name in  CI_COMMIT_REF_NAME  CI_PIPELINE_IID  GITLABCI_SEMANTIC_VERSION  GITLABCI_RELEASE_TRAIN; do
    if [[ -n "${!var_name}" ]]; then
      IMAGE_BUILD_ARGS+=(--build-arg "${var_name}=${!var_name}")
    fi
  done

  # These values are dynamic, based on what the Pipline user is manually
  # injecting
  for var_name in $(compgen -v IMAGE_BUILD_ARG_); do
    arg=${var_name#IMAGE_BUILD_ARG_}
    IMAGE_BUILD_ARGS+=(--build-arg ${arg}="${!var_name}")
  done

  printf "${SEPARATOR}" "${IMAGE_BUILD_ARGS[@]}"
}


# ============================================================================
function print-help() {
  sed -E -n '/^#!/d; /^# ==+/q; /^#/p; /^[^#]/q' "$0" | sed 's/^# \?//'
}


# ============================================================================
# If this script is being executed, produce the desired output
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -s|--separator)
        SEPARATOR_NAME=$2
        SEPARATOR_NAME=${SEPARATOR_NAME^^}_SEPARATOR
        if [[ ! -v "${SEPARATOR_NAME}" ]]; then
          echo "$(basename $0): Unrecognized separator: '$2'.  Expected one of: null, newline, space"
          exit 10
        fi
        SEPARATOR=${!SEPARATOR_NAME}
        shift 2
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

  ci-image-build-args $*
fi
