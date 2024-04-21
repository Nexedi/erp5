"""A dummy checker to register messages from pylint3, to be able to
disable the messages on python2 without causing bad-option-value
"""
from __future__ import absolute_import
from pylint import checkers, interfaces

class CompatibilityDisableChecker(checkers.BaseChecker):

    name = "compatibility-disable"
    msgs = {
        "E9991": (
            "The raise statement is not inside an except clause",
            "misplaced-bare-raise",
            "",
        ),
        "W9992": (
            "Unused private member",
            "unused-private-member",
            "",
        ),
    }


def register(linter):
    linter.register_checker(CompatibilityDisableChecker(linter))
