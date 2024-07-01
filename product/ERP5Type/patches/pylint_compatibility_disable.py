"""A dummy checker to register messages from pylint3, to be able to
disable the messages on python2 without causing bad-option-value
"""
from __future__ import absolute_import
from pylint import checkers, interfaces

class CompatibilityDisableChecker(checkers.BaseChecker):

    name = "compatibility-disable"
    msgs = {
        "E9999": (
            "not-an-iterable",
            "not-an-iterable",
            "",
        ),
        "E9998": (
            "misplaced-bare-raise",
            "misplaced-bare-raise",
            "",
        ),
        "E9997": (
            "unused-private-member",
            "unused-private-member",
            "",
        ),
        "E9996": (
            "using-constant-test",
            "using-constant-test",
            ""
        ),
        "E9995": (
            "modified-iterating-list",
            "modified-iterating-list",
            "",
        ),
        "E9994": (
            "unsubscriptable-object",
            "unsubscriptable-object",
            "",
        ),
        "E9993": (
            "invalid-unary-operand-type",
            "invalid-unary-operand-type",
            "",
        ),
        "E9992": (
            "unbalanced-dict-unpacking",
            "unbalanced-dict-unpacking",
            "",
        ),
        "E9991": (
            "self-cls-assignment",
            "self-cls-assignment",
            "",
        ),
        "E9990": (
            "deprecated-class",
            "deprecated-class",
            "",
        ),
        "E9989": (
            "possibly-used-before-assignment",
            "possibly-used-before-assignment",
            ""
        )
    }


def register(linter):
    linter.register_checker(CompatibilityDisableChecker(linter))
