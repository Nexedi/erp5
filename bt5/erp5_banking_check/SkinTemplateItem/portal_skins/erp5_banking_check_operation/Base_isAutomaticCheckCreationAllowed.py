# This script must be overloaded to allow automatic creation of checks.
# A use case for this functionnality is to cover the transition time  between
# initial site installation and the time all processed checks a re supposed
# to be known to the system beforehand, ie emitted during the site lifespan.

# Return True is the creation is allowed.
# Return False otherwise.
return False
