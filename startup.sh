#!/usr/bin/env bash

# shellcheck disable=SC1091,SC2034,SC2317,SC2046

set -euo pipefail

# $USER
[[ -n $(logname >/dev/null 2>&1) ]] && logged_in_user=$(logname) || logged_in_user=$(whoami)

# $UID
# logged_in_uid=$(id -u "${logged_in_user}")

# $HOME
# logged_in_home=$(eval echo "~${logged_in_user}")

# get the root directory
GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
if [[ -n "$GIT_ROOT" ]]; then
	TLD="$(git rev-parse --show-toplevel)"
else
	TLD="${SCRIPT_DIR}"
fi

# activate virtual environment
if [[ -d "${TLD}/.venv" ]]; then
	source "${TLD}/.venv/bin/activate"
fi

trap_card() {
	# deactivate .venv and code as exit 0
	if [[ -d "${TLD}/.venv" ]]; then
		deactivate 2>/dev/null || true
	fi
}
# trap exit signals: 0, 1, 2, 15
trap trap_card EXIT SIGHUP SIGINT SIGTERM

# get ip address
if [[ $(uname -s) = "Darwin" ]]; then
	PRIVATE_IP=$(ifconfig | awk '/inet /{print $2}' | grep -Ev "127.0.0.1|192.168.1" | head -n 1)
elif [[ $(uname -s) = "Linux" ]]; then
	PRIVATE_IP=$(hostname -I | awk '{print $1}')
fi

# set the environment file
if [[ $(uname -s) = "Darwin" ]] || [[ "$PRIVATE_IP" =~ 192.168 ]]; then
	ENV_FILE="${TLD}/.env"
fi

# set the environment variables
if [[ -f "${ENV_FILE}" ]]; then
	export $(grep -v '^#' "${ENV_FILE}" | xargs)
else
	export $(env | grep -v '^#' | xargs)
fi

# start the server
gunicorn \
	-k uvicorn.workers.UvicornWorker \
	-b "0.0.0.0:${PORT}" \
	--reload \
	--reload-extra-file="${TLD}/templates/index.html" \
	--reload-extra-file="${TLD}/static/styles.css" \
	app:app

exit 0
