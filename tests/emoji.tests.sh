SRC_DIR=context/usr/local/bin


# ----------------------------------------------------------------------------
function assert_is_emoji() {
  echo "$1" | rg "[\\p{Emoji}--\\p{Ascii}]"

  if [[ $? -eq 0 ]]; then
    bashunit::assertion_passed
  else
    bashunit::assertion_failed "Valid emoji" "$1"
  fi
}


# ----------------------------------------------------------------------------
function test_random_emoji() {
  local actual=$(${SRC_DIR}/emoji.sh --random)

  assert_is_emoji "${actual}"
}


# ----------------------------------------------------------------------------
function test_show_all() {
  local actual=$(${SRC_DIR}/emoji.sh --show-all)

  if [[ $(echo "${actual}" | wc -l) -lt 10 ]]; then
    bashunit::fail "Expected multi-line output from 'emoji.sh --show-all'"
  fi

  bashunit::assertion_passed
}


# ----------------------------------------------------------------------------
function test_xray_emoji() {
  local actual=$(${SRC_DIR}/emoji.sh xray)

  assert_equals "🩻" "${actual}"
}


# ----------------------------------------------------------------------------
function test_hammer_wrench_emoji() {
  local actual=$(${SRC_DIR}/emoji.sh HAMMER-WRENCH)

  assert_equals "🛠️" "${actual}"
}


# ----------------------------------------------------------------------------
function test_invalid_emoji() {
  ${SRC_DIR}/emoji.sh foo

  assert_unsuccessful_code
}
