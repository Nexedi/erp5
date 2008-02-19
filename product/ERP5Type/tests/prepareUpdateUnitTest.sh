#!/bin/sh
##############################################################################
#
# Copyright (c) 2008 Nexedi SARL and Contributors. All Rights Reserved.
#                     Vincent Pelletier <vincent@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

if [ $# -lt 2 ]; then
  echo <<EOF
Usage: $0 from to [argument [...]]

  Upgrade a "source" site with "destination" products and business
  templates.
  Everything is done in working directory.

  from
    Path containint "source" code revision.

  to
    Path containing "destination" code revision.

  arguments
    Arguments to provide to runUnitTest.py
EOF
fi

SOURCE_REVISION="$1"
shift
DESTINATION_REVISION="$1"
shift
ARGS="$*"

RUN_UNIT_TESTS="Products/ERP5Type/tests/runUnitTest.py"
COPY_PATH_LIST="Products bt5"

get_revision() {
  local REVISION="$1"
  local COPY_PATH
  for COPY_PATH in $COPY_PATH_LIST; do
    rm -f "$COPY_PATH"
    ln -s "$REVISION/$COPY_PATH" "$COPY_PATH"
  done
}

error() {
  echo "$*"
  exit 1
}

check_directory() {
  local DIRECTORY="$1"
  if [ ! -d "$DIRECTORY" ]; then
    error "Missing directory: '$DIRECTORY'"
  fi
}

check_run_unit_tests() {
  local RUN_UNIT_TESTS="$1"
  if [ ! -x "$RUN_UNIT_TESTS" ]; then
    error "Not executable: '$RUN_UNIT_TESTS'"
  fi
}

check_revision() {
  local DIRECTORY="$1"
  local COPY_PATH
  check_directory "$DIRECTORY"
  for COPY_PATH in $COPY_PATH_LIST; do
    check_directory "$DIRECTORY/$COPY_PATH"
  done
  check_run_unit_tests "$DIRECTORY/$RUN_UNIT_TESTS"
}

# Sanity checks
check_revision "$SOURCE_REVISION"
check_revision "$DESTINATION_REVISION"

# Get first revision
get_revision "$SOURCE_REVISION"
# Create site and save
echo "Creating initial version $SOURCE_REVISION_1..."
set -x
"$RUN_UNIT_TESTS" --save --portal_id portal $ARGS
set +x

# Update to second revision
checkout_revision "$DESTINATION_REVISION"
echo "Updating to version $DESTINATION_REVISION..."
set -x
"$RUN_UNIT_TESTS" --save --load --portal_id portal --update_business_templates $ARGS
set +x

echo "All done. You can run unit tests with command:"
echo "\"$RUN_UNIT_TESTS\" --load --portal_id portal $ARGS"

