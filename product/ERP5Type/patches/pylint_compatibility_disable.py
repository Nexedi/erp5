"""A dummy checker to register messages from pylint3, to be able to
disable the messages on python2 without causing bad-option-value
"""
from __future__ import absolute_import
from pylint import checkers, interfaces

class CompatibilityDisableChecker(checkers.BaseChecker):

    name = "compatibility-disable"
    msgs = {
        "E9990": (
            "not-an-iterable",
            "not-an-iterable",
            "",
        ),
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
            "modified-iterating-list",
            "",
        ),
        "E9995": (
            "unsubscriptable-object",
            "unsubscriptable-object",
            "",
        ),
        "E9996": (
            "invalid-unary-operand-type",
            "invalid-unary-operand-type",
            "",
        ),
        "E9997": (
            "unbalanced-dict-unpacking",
            "unbalanced-dict-unpacking",
            "",
        ),
        "E9998": (
            "self-cls-assignment",
            "self-cls-assignment",
            "",
        ),
        "E9999": (
            "deprecated-class",
            "deprecated-class",
            "",
        ),
    }


def register(linter):
    linter.register_checker(CompatibilityDisableChecker(linter))
