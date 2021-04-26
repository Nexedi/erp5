return [
    c for c in [
        movement.getSourceSection(base=True),
        movement.getSourcePayment(base=True),
        context.getSource(base=True),
    ] if c
]
