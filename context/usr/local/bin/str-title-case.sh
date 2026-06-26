#! /bin/bash


# ============================================================================
function str-title-case () {
  for value in "$*"; do
    value=${value,,}
    value=${value//_/ }
    value=${value//-/ }
    value=$(echo "${value}" | sed -E 's/(.)/\L\1/g; s/\b(.)/\U\1/g')

    echo -n ${value}
  done
}


# ============================================================================
# If this script is being executed, produce the desired output
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  str-title-case $*
fi
