#! /bin/bash


# ============================================================================
function str-slug() {
  for value in "$*"; do
    value="${value//\//-}"
    value="${value//+/.}"
    value="${value,,}"

    echo -n ${value}
  done
}


# ============================================================================
# If this script is being executed, produce the desired output
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  str-slug $*
fi
