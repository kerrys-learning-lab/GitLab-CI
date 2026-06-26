SRC_DIR=context/usr/local/bin


# ----------------------------------------------------------------------------
function test_str_title_case() {
  local test_str='THIS_IS_miXed-CAPS'
  local expected='This Is Mixed Caps'

  local actual=$(${SRC_DIR}/str-title-case.sh ${test_str})

  assert_equals "${expected}" "${actual}"
}
