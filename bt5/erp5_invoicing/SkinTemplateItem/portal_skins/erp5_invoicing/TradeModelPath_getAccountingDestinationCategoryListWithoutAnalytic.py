return [
    c for c in [
        movement.getDestinationSection(base=True),
        movement.getDestinationPayment(base=True),
        context.getDestination(base=True)
    ] if c
]
