SRC_DIR=context/usr/local/bin


# ----------------------------------------------------------------------------
function test_str_slug() {
  local test_str='THIS/IS/miXed+CAPS'
  local expected='this-is-mixed.caps'

  local actual=$(${SRC_DIR}/str-slug.sh ${test_str})

  assert_equals "${expected}" "${actual}"
}
