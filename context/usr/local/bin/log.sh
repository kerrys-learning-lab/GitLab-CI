#! /bin/bash

. $(dirname $(realpath $0))/ansi-colors.sh
. $(dirname $(realpath $0))/emoji.sh


declare -A LOG_LEVEL_VALUES
LOG_LEVEL_VALUES[TRACE]=0
LOG_LEVEL_VALUES[DEBUG]=1
LOG_LEVEL_VALUES[INFO]=2
LOG_LEVEL_VALUES[WARNING]=3
LOG_LEVEL_VALUES[ERROR]=4
LOG_LEVEL_VALUES[FATAL]=5


declare -A LOG_LEVEL_COLORS
LOG_LEVEL_COLORS[TRACE]=${COLOR_WHITE}
LOG_LEVEL_COLORS[DEBUG]=${COLOR_CYAN}
LOG_LEVEL_COLORS[INFO]=${COLOR_INTNS_GREEN}
LOG_LEVEL_COLORS[WARNING]=${COLOR_YELLOW}
LOG_LEVEL_COLORS[ERROR]=${COLOR_RED}
LOG_LEVEL_COLORS[FATAL]=${COLOR_BLACK}${COLOR_BG_YELLOW}


# ----------------------------------------------------------------------
# Log a message (at the given log-level) to stderr.
function log_msg {
  local level_name=${1^^}; shift
  local level_value=${LOG_LEVEL_VALUES[${level_name}]}
  local color=${LOG_LEVEL_COLORS[${level_name}]}
  local end_color=${COLOR_RESET}
  local timestamp=$(date --iso-8601=seconds)
  local message="$*"

  if [[ -n "${NO_COLOR}" ]]; then
    color=
    end_color=
  fi

  if [[ ${level_value} -ge ${EFFECTIVE_LOG_LEVEL_VALUE} ]]; then
    message=$(printf "${timestamp} ${color}%-10s${end_color}${message}\n" "${level_name}")

    if [[ -n "${STDOUT}" ]]; then
      echo -e "${message}"
    else
      echo -e "${message}" >&2
    fi
  fi
}


# ============================================================================
function log_trace    { log_msg "TRACE"   "$@"; }
function log_debug    { log_msg "DEBUG"   "$@"; }
function log_info     { log_msg "INFO"    "$@"; }
function log_warning  { log_msg "WARNING" "$@"; }
function log_error    { log_msg "ERROR"   "$@"; }
function log_fatal    { log_msg "FATAL"   "$@"; }


# ============================================================================
function log_building   { log_info 🛠️ Building $*;    }
function log_publishing { log_info 🚀 Publishing $*;  }
function log_testing    { log_info 📋 Testing $*;     }


# ============================================================================
function print-help() {
  sed -E -n '/^#!/d; /^# ==+/q; /^#/p; /^[^#]/q' "$0" | sed 's/^# \?//'
}


EFFECTIVE_LOG_LEVEL=${LOG_LEVEL:-INFO}
EFFECTIVE_LOG_LEVEL=${EFFECTIVE_LOG_LEVEL^^}
EFFECTIVE_LOG_LEVEL_VALUE=${LOG_LEVEL_VALUES[${EFFECTIVE_LOG_LEVEL}]}


# If this script is being executed, actually log the arguments
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  LOG_FUNCTION_STEM=
  LOG_ARGS=()

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --no-color)
        NO_COLOR=true
        shift
        ;;
      --stdout)
        STDOUT=true
        shift
        ;;
      *)
        if [[ -z "${LOG_FUNCTION_STEM}" ]]; then
          LOG_FUNCTION_STEM=$1
        else
          LOG_ARGS+=($1)
        fi
        shift
        ;;
    esac
  done

  if [[ -z "${EFFECTIVE_LOG_LEVEL_VALUE}" ]]; then
    EFFECTIVE_LOG_LEVEL_VALUE=${LOG_LEVEL_VALUES[INFO]}
    log_warning "$(basename $0): Invalid LOG_LEVEL: ${LOG_LEVEL}"
  fi

  LOG_FUNCTION=log_${LOG_FUNCTION_STEM,,}

  if declare -F "${LOG_FUNCTION}" > /dev/null; then
    ${LOG_FUNCTION} "${LOG_ARGS[@]}"
  else
    echo "$(basename $0): Error: Invalid log command: ${LOG_FUNCTION_STEM}"
    log_error "${LOG_ARGS[@]}"
  fi

fi
