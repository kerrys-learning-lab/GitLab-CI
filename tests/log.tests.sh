SRC_DIR=context/usr/local/bin

DEFAULT_LOG_ARGS=()
DEFAULT_LOG_ARGS+=(--no-color)
DEFAULT_LOG_ARGS+=(--stdout)


# ----------------------------------------------------------------------------
function assert_log_level() {
  local expected_level=$1; shift
  local actual_level=$(echo "$*" | cut -d' ' -f2)

  sed -E 's/\x1B\[[0-9;]*[a-zA-Z]//g'

  if [[ "${expected_level^^}" == "${actual_level}" ]]; then
    bashunit::assertion_passed
  else
    bashunit::assertion_failed "${expected_level^^}" "${actual_level}"
  fi
}


# ----------------------------------------------------------------------------
function test_log_trace() {
  LOG_ARGS=(${DEFAULT_LOG_ARGS[@]})
  LOG_ARGS+=(trace)
  LOG_ARGS+=(This is a test of 'trace')

  local msg=$(LOG_LEVEL=trace ${SRC_DIR}/log.sh "${LOG_ARGS[@]}")

  assert_log_level trace "${msg}"
}


# ----------------------------------------------------------------------------
function test_log_trace_not_enabled() {
  LOG_ARGS=(${DEFAULT_LOG_ARGS[@]})
  LOG_ARGS+=(trace)
  LOG_ARGS+=(This is a test of 'trace')

  local msg=$(LOG_LEVEL=fatal ${SRC_DIR}/log.sh "${LOG_ARGS[@]}")

  assert_empty "${msg}"
}


# ----------------------------------------------------------------------------
function test_log_debug() {
  LOG_ARGS=(${DEFAULT_LOG_ARGS[@]})
  LOG_ARGS+=(debug)
  LOG_ARGS+=(This is a test of 'debug')

  local msg=$(LOG_LEVEL=debug ${SRC_DIR}/log.sh "${LOG_ARGS[@]}")

  assert_log_level debug "${msg}"
}


# ----------------------------------------------------------------------------
function test_log_debug_not_enabled() {
  LOG_ARGS=(${DEFAULT_LOG_ARGS[@]})
  LOG_ARGS+=(debug)
  LOG_ARGS+=(This is a test of 'debug')

  local msg=$(LOG_LEVEL=fatal ${SRC_DIR}/log.sh "${LOG_ARGS[@]}")

  assert_empty "${msg}"
}


# ----------------------------------------------------------------------------
function test_log_info() {
  LOG_ARGS=(${DEFAULT_LOG_ARGS[@]})
  LOG_ARGS+=(info)
  LOG_ARGS+=(This is a test of 'info')

  local msg=$(LOG_LEVEL=info ${SRC_DIR}/log.sh "${LOG_ARGS[@]}")

  assert_log_level info "${msg}"
}


# ----------------------------------------------------------------------------
function test_log_info_not_enabled() {
  LOG_ARGS=(${DEFAULT_LOG_ARGS[@]})
  LOG_ARGS+=(info)
  LOG_ARGS+=(This is a test of 'info')

  local msg=$(LOG_LEVEL=fatal ${SRC_DIR}/log.sh "${LOG_ARGS[@]}")

  assert_empty "${msg}"
}


# ----------------------------------------------------------------------------
function test_log_warning() {
  LOG_ARGS=(${DEFAULT_LOG_ARGS[@]})
  LOG_ARGS+=(warning)
  LOG_ARGS+=(This is a test of 'warning')

  local msg=$(LOG_LEVEL=warning ${SRC_DIR}/log.sh "${LOG_ARGS[@]}")

  assert_log_level warning "${msg}"
}


# ----------------------------------------------------------------------------
function test_log_warning_not_enabled() {
  LOG_ARGS=(${DEFAULT_LOG_ARGS[@]})
  LOG_ARGS+=(warning)
  LOG_ARGS+=(This is a test of 'warning')

  local msg=$(LOG_LEVEL=fatal ${SRC_DIR}/log.sh "${LOG_ARGS[@]}")

  assert_empty "${msg}"
}


# ----------------------------------------------------------------------------
function test_log_error() {
  LOG_ARGS=(${DEFAULT_LOG_ARGS[@]})
  LOG_ARGS+=(error)
  LOG_ARGS+=(This is a test of 'error')

  local msg=$(LOG_LEVEL=info ${SRC_DIR}/log.sh "${LOG_ARGS[@]}")

  assert_log_level error "${msg}"
}


# ----------------------------------------------------------------------------
function test_log_error_not_enabled() {
  LOG_ARGS=(${DEFAULT_LOG_ARGS[@]})
  LOG_ARGS+=(error)
  LOG_ARGS+=(This is a test of 'error')

  local msg=$(LOG_LEVEL=fatal ${SRC_DIR}/log.sh "${LOG_ARGS[@]}")

  assert_empty "${msg}"
}


# ----------------------------------------------------------------------------
function test_log_fatal() {
  LOG_ARGS=(${DEFAULT_LOG_ARGS[@]})
  LOG_ARGS+=(fatal)
  LOG_ARGS+=(This is a test of 'fatal')

  local msg=$(LOG_LEVEL=info ${SRC_DIR}/log.sh "${LOG_ARGS[@]}")

  assert_log_level fatal "${msg}"
}


# ----------------------------------------------------------------------------
function test_log_unknown_msg_level() {
  LOG_ARGS=(${DEFAULT_LOG_ARGS[@]})
  LOG_ARGS+=(foo)
  LOG_ARGS+=(This is a test of an unknown msg log level)

  local msg=$(LOG_LEVEL=info ${SRC_DIR}/log.sh "${LOG_ARGS[@]}")

  assert_contains "ERROR" "${msg}"
  assert_contains "Invalid log command: foo" "${msg}"
}


# ----------------------------------------------------------------------------
function test_log_unknown_effective_level() {
  LOG_ARGS=(${DEFAULT_LOG_ARGS[@]})
  LOG_ARGS+=(info)
  LOG_ARGS+=(This is a test of an effective log level)

  local msg=$(LOG_LEVEL=foo ${SRC_DIR}/log.sh "${LOG_ARGS[@]}")

  assert_contains "Invalid LOG_LEVEL" "${msg}"
}
