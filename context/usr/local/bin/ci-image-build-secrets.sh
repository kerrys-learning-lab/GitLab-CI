#! /bin/bash
#
# Usage:  ci-image-build-secrets.sh [OPTIONS]
#
# Description:  Creates secrets suitable for injecting into an image build
#               command.  Within the build process, the secrets will be
#               securely mounted at /run/secrets and WILL NOT become part of
#               the built image.
#
# Options:
#   -d, --destination-directory The destination directory to write secrets,
#                               if the secret it not already in a file.
#   -s, --separator <sep>       Specifies how to separate each resulting
#                               argument.  Must be one of 'null', 'newline',
#                               'space'.  Default: 'space'
#   -h, --help                  Shows this help message
# ============================================================================


DESTINATION_DIR=${DESTINATION_DIR:-.image-build/secrets}
NULL_SEPARATOR='%s\0'
NEWLINE_SEPARATOR='%s\n'
SPACE_SEPARATOR='%s '
SEPARATOR=${SPACE_SEPARATOR}


# ============================================================================
function ci-image-build-secrets () {

  # -- File secrets:
  for var_name in $(compgen -v IMAGE_BUILD_SECRET_FILE_); do
    id=${var_name#IMAGE_BUILD_SECRET_FILE_}
    id=${id//_/-}
    id=${id,,}
    IMAGE_BUILD_SECRETS+=(--secret "id=${id},src=${!var_name}")
  done

  # --- String secrets:
  mkdir -p ${DESTINATION_DIR}
  for var_name in $(compgen -v IMAGE_BUILD_SECRET_STRING_); do
    id=${var_name#IMAGE_BUILD_SECRET_STRING_}
    id=${id//_/-}
    id=${id,,}

    echo "${!var_name}" > ${DESTINATION_DIR}/${id}
    IMAGE_BUILD_SECRETS+=(--secret "id=${id},src=${DESTINATION_DIR}/${id}")
  done

  printf "${SEPARATOR}" "${IMAGE_BUILD_SECRETS[@]}"
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
      -d|--dest-dir|--destination-dir)
        DESTINATION_DIR=$2
        shift 2
        ;;
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

  ci-image-build-secrets $*
fi
