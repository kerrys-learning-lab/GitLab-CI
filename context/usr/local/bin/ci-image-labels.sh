#! /bin/bash
#
# Usage:  ci-image-labels.sh [OPTIONS]
#
# Description:  Creates labels suitable for injecting into an image build
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


. $(dirname $(realpath $0))/str-slug.sh


# ============================================================================
function ci-image-labels () {
  IMAGE_CREATED_TIMESTAMP=${GITLABCI_PIPELINE_TIMESTAMP:-$(date --iso-8601=seconds)}
  IMAGE_VERSION_SLUG=$(str-slug ${CI_COMMIT_REF_NAME})

  IMAGE_LABELS+=(--label "org.opencontainers.image.title=${CI_PROJECT_TITLE}")
  IMAGE_LABELS+=(--label "org.opencontainers.image.description=${CI_PROJECT_DESCRIPTION}")
  IMAGE_LABELS+=(--label "org.opencontainers.image.created=${IMAGE_CREATED_TIMESTAMP}")
  IMAGE_LABELS+=(--label "org.opencontainers.image.url=${CI_PROJECT_URL}")
  IMAGE_LABELS+=(--label "org.opencontainers.image.version=${IMAGE_VERSION_SLUG}")
  IMAGE_LABELS+=(--label "org.opencontainers.image.revision=${CI_COMMIT_SHA}")

  printf "${SEPARATOR}" "${IMAGE_LABELS[@]}"
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

  ci-image-labels $*
fi
