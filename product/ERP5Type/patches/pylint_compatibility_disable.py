"""A dummy checker to register messages from pylint3, to be able to
disable the messages on python2 without causing bad-option-value
"""
from __future__ import absolute_import
from pylint import checkers, interfaces

class CompatibilityDisableChecker(checkers.BaseChecker):

    name = "compatibility-disable"
    msgs = {
        "E9991": (
            "misplaced-bare-raise",
            "misplaced-bare-raise",
            "",
        ),
        "W9992": (
            "unused-private-member",
            "unused-private-member",
            "",
        ),
        "E9993": (
            "using-constant-test",
            "using-constant-test",
            ""
        ),
        "E9994": (
            "modified-iterating-list",
            'modified-iterating-list",
            "",
        ),
        "E9995": (
            "unsubscriptable-object",
            "unsubscriptable-object",
            "",
        )
    }


def register(linter):
    linter.register_checker(CompatibilityDisableChecker(linter))
