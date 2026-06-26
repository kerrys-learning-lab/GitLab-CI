#! /bin/bash
#
# Usage:  emoji.sh <emoji-name>...
#         emoji.sh --show-all
#         emoji.sh --random
#
# Description: Prints an emoji to stdout.
#
# Arguments:
#   <emoji-name>  The name of the emoji to print.
#
# Options:
#   -r, --random    Prints a random emoji
#   -s, --show-all  Shows all available emojis and their name
#   -h, --help      Shows this help message
#
# Error codes:
#   10  Emoji name does not exist
# ============================================================================


# --- Emoji
readonly EMOJI_1ST_PLACE_MEDAL=$'🥇'
readonly EMOJI_ATHLETIC_SHOE=$'👟'
readonly EMOJI_BEACH_UMBRELLA=$'🏖️'
readonly EMOJI_BLOSSOM=$'🌼'
readonly EMOJI_BLUE_HEART=$'💙'
readonly EMOJI_BOAT=$'⛵'
readonly EMOJI_CHECKERED_FLAG=$'🏁'
readonly EMOJI_CLIPBOARD=$'📋'
readonly EMOJI_DOWNARROW=$'⤵️'
readonly EMOJI_EMPTY_NEST=$'🪹'
readonly EMOJI_FIRE=$'🔥'
readonly EMOJI_GREEN_CIRCLE=$'🟢'
readonly EMOJI_HAMMER_WRENCH=$'🛠️'
readonly EMOJI_RAINBOW=$'🌈'
readonly EMOJI_REDX=$'❌'
readonly EMOJI_ROCKET=$'🚀'
readonly EMOJI_SHELL=$'🐚'
readonly EMOJI_STOP_BUTTON=$'⏹️'
readonly EMOJI_STOP_SIGN=$'🛑'
readonly EMOJI_TURTLE=$'🐢'
readonly EMOJI_UNLOCK=$'🔓'
readonly EMOJI_VIDEO_GAME=$'🎮'
readonly EMOJI_WAFFLE=$'🧇'
readonly EMOJI_XRAY=$'🩻'
readonly EMOJI_YARN=$'🧶'
readonly EMOJI_ZOMBIE=$'🧟'

RANDOM_EMOJIS=()
RANDOM_EMOJIS+=(${EMOJI_1ST_PLACE_MEDAL})
RANDOM_EMOJIS+=(${EMOJI_ATHLETIC_SHOE})
RANDOM_EMOJIS+=(${EMOJI_BEACH_UMBRELLA})
RANDOM_EMOJIS+=(${EMOJI_BLOSSOM})
RANDOM_EMOJIS+=(${EMOJI_BLUE_HEART})
RANDOM_EMOJIS+=(${EMOJI_BOAT})
RANDOM_EMOJIS+=(${EMOJI_RAINBOW})
RANDOM_EMOJIS+=(${EMOJI_ROCKET})
RANDOM_EMOJIS+=(${EMOJI_SHELL})
RANDOM_EMOJIS+=(${EMOJI_TURTLE})
RANDOM_EMOJIS+=(${EMOJI_UNLOCK})
RANDOM_EMOJIS+=(${EMOJI_VIDEO_GAME})
RANDOM_EMOJIS+=(${EMOJI_WAFFLE})
RANDOM_EMOJIS+=(${EMOJI_XRAY})
RANDOM_EMOJIS+=(${EMOJI_YARN})
RANDOM_EMOJIS+=(${EMOJI_ZOMBIE})


# ============================================================================
function print-random() {
  echo -n ${RANDOM_EMOJIS[$RANDOM % ${#RANDOM_EMOJIS[@]}]}
}


# ============================================================================
function print-all() {
  local TABLE="==========;==========\n"

  for var in $(compgen -v EMOJI_); do
    name=${var#EMOJI_}
    name=${name,,}
    name=${name//_/-}
    TABLE+="${name};${!var}\n"
  done

  printf "${TABLE}" | column  --table  \
                              --separator ';' \
                              --output-separator ' | '  \
                              --table-column name=Name \
                              --table-column name=Emoji
}


# ============================================================================
function print-emoji() {
  emoji_name="EMOJI_${1}"
  emoji_name=${emoji_name^^}
  emoji_name=${emoji_name//-/_}

  emoji=${!emoji_name}

  if [[ -z "${emoji}" ]]; then
    echo "$(basename $0): No such emoji: '${1}'" >&2
    exit 10
  fi

  echo -n ${emoji}
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
      -r|--random)
        print-random
        shift
        ;;
      -s|--show-all)
        print-all
        shift
        ;;
      -h|--help)
        print-help
        shift
        ;;
      *)
        print-emoji $1
        shift
        ;;
    esac
  done
fi
