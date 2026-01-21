#!/bin/bash
set -e

docker compose run --rm commitlint sh -c 'git log -1 --pretty=format:"%B" | commitlint'
