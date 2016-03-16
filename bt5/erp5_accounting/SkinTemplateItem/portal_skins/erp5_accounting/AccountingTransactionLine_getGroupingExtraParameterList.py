"""This script is a placeholder for projects to implement extra constraint to prevent grouping of accounting transaction lines.
Note that the sequence of letters will still remain unique for section, mirror_section and node, regardless of extra grouping parameters.

For instance, we can refuse to group together lines for different order by returning the reference of the order in that script.

The returned value must be hashable.
"""
