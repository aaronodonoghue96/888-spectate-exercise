"""
    Finds the total number of internal nodes in the given tree
    i.e. those with at least one child

    Time complexity: O(n) - iterates through tree once, adding all parent nodes
    to set (i.e. any value in the list that is also an index in the range of
    the list's length, excluding dummy values like -1 to indicate no parent).
    In any case, all n nodes in the tree will need to be checked, which is O(n)
    
    Space complexity: O(n) - creates a set of parent nodes, which is used to
    calculate the number of internal nodes, as all parent nodes are internal
    nodes. In the worst case (a vertical line tree), all but one of the nodes
    could be parents, i.e. n - 1, which is O(n)
"""
def find_internal_nodes_num(tree):

    """
    Finds the total number of internal nodes in the given tree
    i.e. those with at least one child

    Time complexity: O(n) - iterates through tree once, adding all parent nodes
    to set (i.e. any value in the list that is also an index in the range of
    the list's length, excluding dummy values like -1 to indicate no parent).
    In any case, all n nodes in the tree will need to be checked, which is O(n)
    
    Space complexity: O(n) - creates a set of parent nodes, which is used to
    calculate the number of internal nodes, as all parent nodes are internal
    nodes. In the worst case (a vertical line tree), all but one of the nodes
    could be parents, i.e. n - 1, which is O(n)
"""

    internal_nodes = set() #set to ensure no double-counting of nodes

    # for each node i in the tree, its parent is tree[i], all parent nodes
    # are automatically internal nodes as they have at least one child
    for i in range(len(tree)):
        # check if parent is in the range of indexes of the tree
        # i.e. exclude -1 or other dummy values to show root has no parent
        # and exclude nodes that are already counted as internal nodes
        if tree[i] in range(len(tree)):
            internal_nodes.add(tree[i])

    # return the amount of internal nodes in the set, i.e. the number of
    # distinct values in the list, excluding the dummy value -1
    return len(internal_nodes)

# sample tree provided in question
my_tree = [4, 4, 1, 5, -1, 4, 5]

# empty tree to ensure it handles empty input
empty_tree = []

# tree with just a root, no internal nodes as the root is also a leaf node
root_only = [-1]

# worst case scenario, the tree looks like a straight line, and every node
# is the child of the previous
straight_line_tree = [-1, 0, 1, 2, 3, 4, 5]

# big tree with many nodes
big_tree = [-1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2,
            2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4,
            4, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 12, 9, 8,
            7, 11, 10, 7, 12, 8, 5, 1, 3, 4, 5, 2]

# testing that the method calculates the number of internal nodes correctly
assert find_internal_nodes_num(my_tree) == 3
assert find_internal_nodes_num(empty_tree) == 0
assert find_internal_nodes_num(root_only) == 0
assert find_internal_nodes_num(straight_line_tree) == 6
assert find_internal_nodes_num(big_tree) == 13
