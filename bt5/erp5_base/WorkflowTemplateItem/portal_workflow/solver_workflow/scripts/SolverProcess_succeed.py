solver_process = state_change['object'].getParentValue()
# Before parsing sub objects was done directly here. And we had the
# case where you have parallel transactions solving a solver,
# each of theses transactions see remaining solver not in solved state,
# but once all transaction are finished, all solver are solved. This
# could lead to the case where solver_process is never moved to succeeded
# Instead of using serialize (which may lead to conflicts), just use
# activities in queue.
solver_process.activate(serialization_tag=solver_process.getRelativeUrl()
                        ).SolverProcess_tryToSucceed()
