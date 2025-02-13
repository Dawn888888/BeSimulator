from py_trees import behaviour, blackboard, common, composites, console, decorators, utilities
import typing
import os
import pydot
import uuid
from init_tree import Action_Behavior, Condition_Behavior
# from Node import Node

unicode_symbols = {
    "space": " ",
    "left_arrow": console.left_arrow,
    "right_arrow": console.right_arrow,
    "left_right_arrow": console.left_right_arrow,
    "bold": console.bold,
    "bold_reset": console.reset,
    "memory": console.circled_m,
    "synchronised": console.lightning_bolt,
    "sequence_with_memory": "{-}",
    "selector_with_memory": "{o}",
    "sequence_without_memory": "[-]",
    "selector_without_memory": "[o]",
    "parallel": "/_/",
    "decorator": "-^-",
    "behaviour": "-->",
    common.Status.SUCCESS: console.green + console.check_mark + console.reset,
    common.Status.FAILURE: console.red + console.multiplication_x + console.reset,
    common.Status.INVALID: console.yellow + "-" + console.reset,
    common.Status.RUNNING: console.blue + "*" + console.reset,
}
"""Symbols for a unicode, escape sequence capable console."""

ascii_symbols = {
    "space": " ",
    "left_arrow": "<-",
    "right_arrow": "->",
    "left_right_arrow": "<->",
    "bold": console.bold,
    "bold_reset": console.reset,
    "memory": "M",
    "synchronised": "s",
    "sequence_with_memory": "{-}",
    "selector_with_memory": "{o}",
    "sequence_without_memory": "[-]",
    "selector_without_memory": "[o]",
    "parallel": "/_/",
    "decorator": "-^-",
    "behaviour": "-->",
    common.Status.SUCCESS: console.green + "o" + console.reset,
    common.Status.FAILURE: console.red + "x" + console.reset,
    common.Status.INVALID: console.yellow + "-" + console.reset,
    common.Status.RUNNING: console.blue + "*" + console.reset,
}


def dot_tree(
    root: behaviour.Behaviour,
    visibility_level: common.VisibilityLevel = common.VisibilityLevel.DETAIL,
    collapse_decorators: bool = False,
    with_blackboard_variables: bool = False,
    with_qualified_names: bool = False,
) -> pydot.Dot:
    """
    Paint your tree on a pydot graph.

    .. seealso:: :py:func:`render_dot_tree`.

    Args:
        root (:class:`~py_trees.behaviour.Behaviour`): the root of a tree, or subtree
        visibility_level (optional): collapse subtrees at or under this level
        collapse_decorators (optional): only show the decorator (not the child), defaults to False
        with_blackboard_variables (optional): add nodes for the blackboard variables
        with_qualified_names (optional): print the class information for each behaviour in each node, defaults to False

    Returns:
        pydot.Dot: graph

    Examples:
        .. code-block:: python

            # convert the pydot graph to a string object
            print("{}".format(py_trees.display.dot_graph(root).to_string()))
    """

    def get_node_attributes(node: behaviour.Behaviour) -> typing.Tuple[str, str, str]:
        blackbox_font_colours = {
            common.BlackBoxLevel.DETAIL: "dodgerblue",
            common.BlackBoxLevel.COMPONENT: "lawngreen",
            common.BlackBoxLevel.BIG_PICTURE: "white",
        }
        if isinstance(node, composites.Selector):
            attributes = ("box", "cyan", "black")  # octagon
        elif isinstance(node, composites.Sequence):
            attributes = ("box", "orange", "black")
        elif isinstance(node, composites.Parallel):
            attributes = ("box", "gold", "black")
        elif isinstance(node, decorators.Decorator):
            attributes = ("ellipse", "ghostwhite", "black")
        elif isinstance(node, Action_Behavior):
            attributes = ("box", "gray", "black")
        elif isinstance(node, Condition_Behavior):
            attributes = ("ellipse", "gray", "black")
        else:
            raise NotImplementedError("No This Node")
        try:
            if node.blackbox_level != common.BlackBoxLevel.NOT_A_BLACKBOX:
                attributes = (
                    attributes[0],
                    "gray20",
                    blackbox_font_colours[node.blackbox_level],
                )
        except AttributeError:
            # it's a blackboard client, not a behaviour, just pass
            pass
        return attributes

    def get_node_label(node_name: str, behaviour: behaviour.Behaviour) -> str:
        """
        Create a more detailed string (when applicable) to use for the node name.

        This prefixes the node name with additional information about the node type (e.g. with
        or without memory). Useful when debugging.
        """
        # Custom handling of composites provided by this library. Not currently
        # providing a generic mechanism for others to customise visualisations
        # for their derived composites.
        prefix = ""
        policy = ""
        symbols = unicode_symbols if console.has_unicode() else ascii_symbols
        if isinstance(behaviour, composites.Composite):
            try:
                if behaviour.memory:  # type: ignore[attr-defined]
                    prefix += symbols["memory"]  # console.circled_m
            except AttributeError:
                pass
            try:
                if behaviour.policy.synchronise:  # type: ignore[attr-defined]
                    prefix += symbols["synchronised"]  # console.lightning_bolt
            except AttributeError:
                pass
            try:
                policy = behaviour.policy.__class__.__name__  # type: ignore[attr-defined]
            except AttributeError:
                pass
            try:
                indices = [
                    str(behaviour.children.index(child))
                    for child in behaviour.policy.children  # type: ignore[attr-defined]
                ]
                policy += "({})".format(", ".join(sorted(indices)))
            except AttributeError:
                pass
        node_label = f"{prefix} {node_name}" if prefix else node_name
        if policy:
            node_label += f"\n{str(policy)}"
        if with_qualified_names:
            node_label += f"\n({utilities.get_fully_qualified_name(behaviour)})"
            
        node_label = node_label.strip("*")
        
        # if node_label == "Sequence":
        #     node_label = "->"
        # elif node_label == "Fallback":
        #     node_label = "?"
            
        return node_label

    fontsize = 9
    blackboard_colour = "blue"  # "dimgray"
    graph = pydot.Dot(graph_type="digraph", ordering="out")
    graph.set_name(
        "pastafarianism"
    )  # consider making this unique to the tree sometime, e.g. based on the root name
    # fonts: helvetica, times-bold, arial (times-roman is the default, but this helps some viewers, like kgraphviewer)
    graph.set_graph_defaults(
        fontname="times-roman"
    )  # splines='curved' is buggy on 16.04, but would be nice to have
    graph.set_node_defaults(fontname="times-roman")
    graph.set_edge_defaults(fontname="times-roman")
    (node_shape, node_colour, node_font_colour) = get_node_attributes(root)
    
    
    node_root = pydot.Node(
        name=root.name,
        label=get_node_label(root.name, root),
        shape=node_shape,
        style="filled",
        fillcolor=node_colour,
        fontsize=fontsize,
        fontcolor=node_font_colour,
    )
    graph.add_node(node_root)
    behaviour_id_name_map = {root.id: root.name}

    def add_children_and_edges(
        root: behaviour.Behaviour,
        root_node: pydot.Node,
        root_dot_name: str,
        visibility_level: common.VisibilityLevel,
        collapse_decorators: bool,
    ) -> None:
        if isinstance(root, decorators.Decorator) and collapse_decorators:
            return
        if visibility_level < root.blackbox_level:
            node_names = []
            for c in root.children:
                (node_shape, node_colour, node_font_colour) = get_node_attributes(c)
                node_name = c.name
                while node_name in behaviour_id_name_map.values():
                    node_name += "*"
                behaviour_id_name_map[c.id] = node_name
                # Node attributes can be found on page 5 of
                #    https://graphviz.gitlab.io/_pages/pdf/dot.1.pdf
                # Attributes that may be useful: tooltip, xlabel
                
                # if get_node_label(node_name, c) in["->", "?"]:
                #     node = pydot.Node(
                #     name=node_name,
                #     label=get_node_label(node_name, c),
                #     shape=node_shape,
                #     style="filled",
                #     fillcolor=node_colour,
                #     fontsize=18,
                #     fontcolor=node_font_colour,
                # )
               
                node = pydot.Node(
                    name=node_name,
                    label=get_node_label(node_name, c),
                    shape=node_shape,
                    style="filled",
                    fillcolor=node_colour,
                    fontsize=fontsize,
                    fontcolor=node_font_colour,
                )
                node_names.append(node_name)
                graph.add_node(node)
                edge = pydot.Edge(root_dot_name, node_name)
                graph.add_edge(edge)
                if c.children != []:
                    add_children_and_edges(
                        c, node, node_name, visibility_level, collapse_decorators
                    )

    add_children_and_edges(
        root, node_root, root.name, visibility_level, collapse_decorators
    )

    def create_blackboard_client_node(blackboard_client_name: str) -> pydot.Node:
        return pydot.Node(
            name=blackboard_client_name,
            label=blackboard_client_name,
            shape="ellipse",
            style="filled",
            color=blackboard_colour,
            fillcolor="gray",
            fontsize=fontsize - 2,
            fontcolor=blackboard_colour,
        )

    def add_blackboard_nodes(
        blackboard_id_name_map: typing.Dict[uuid.UUID, str]
    ) -> None:
        data = blackboard.Blackboard.storage
        metadata = blackboard.Blackboard.metadata
        clients = blackboard.Blackboard.clients
        # add client (that are not behaviour) nodes
        subgraph = pydot.Subgraph(
            graph_name="Blackboard",
            id="Blackboard",
            label="Blackboard",
            rank="sink",
        )
        for unique_identifier, client_name in clients.items():
            if unique_identifier not in blackboard_id_name_map:
                subgraph.add_node(create_blackboard_client_node(client_name))
        # add key nodes
        for key in blackboard.Blackboard.keys():
            try:
                value = utilities.truncate(str(data[key]), 20)
                label = key + ": " + "{}".format(value)
            except KeyError:
                label = key + ": " + "-"
            blackboard_node = pydot.Node(
                key,
                label=label,
                shape="box",
                style="filled",
                color=blackboard_colour,
                fillcolor="white",
                fontsize=fontsize - 1,
                fontcolor=blackboard_colour,
                width=0,
                height=0,
                fixedsize=False,  # only big enough to fit text
            )
            subgraph.add_node(blackboard_node)
            for unique_identifier in metadata[key].read:
                try:
                    edge = pydot.Edge(
                        blackboard_node,
                        blackboard_id_name_map[unique_identifier],
                        color="green",
                        constraint=False,
                        weight=0,
                    )
                except KeyError:
                    edge = pydot.Edge(
                        blackboard_node,
                        clients[unique_identifier],
                        color="green",
                        constraint=False,
                        weight=0,
                    )
                graph.add_edge(edge)
            for unique_identifier in metadata[key].write:
                try:
                    edge = pydot.Edge(
                        blackboard_id_name_map[unique_identifier],
                        blackboard_node,
                        color=blackboard_colour,
                        constraint=False,
                        weight=0,
                    )
                except KeyError:
                    edge = pydot.Edge(
                        clients[unique_identifier],
                        blackboard_node,
                        color=blackboard_colour,
                        constraint=False,
                        weight=0,
                    )
                graph.add_edge(edge)
            for unique_identifier in metadata[key].exclusive:
                try:
                    edge = pydot.Edge(
                        blackboard_id_name_map[unique_identifier],
                        blackboard_node,
                        color="deepskyblue",
                        constraint=False,
                        weight=0,
                    )
                except KeyError:
                    edge = pydot.Edge(
                        clients[unique_identifier],
                        blackboard_node,
                        color="deepskyblue",
                        constraint=False,
                        weight=0,
                    )
                graph.add_edge(edge)
        graph.add_subgraph(subgraph)

    if with_blackboard_variables:
        blackboard_id_name_map = {}
        for b in root.iterate():
            for bb in b.blackboards:
                blackboard_id_name_map[bb.id()] = behaviour_id_name_map[b.id]
        add_blackboard_nodes(blackboard_id_name_map)

    return graph


def render_dot_tree(
    root: behaviour.Behaviour,
    visibility_level: common.VisibilityLevel = common.VisibilityLevel.DETAIL,
    collapse_decorators: bool = False,
    name: typing.Optional[str] = None,
    target_directory: typing.Optional[str] = None,
    with_blackboard_variables: bool = False,
    with_qualified_names: bool = False,
) -> typing.Dict[str, str]:
    """
    Render the dot tree to dot, svg, png. files.

    By default, these are saved in the current
    working directory and will be named with the root behaviour name.

    Args:
        root: the root of a tree, or subtree
        visibility_level: collapse subtrees at or under this level
        collapse_decorators: only show the decorator (not the child)
        name: name to use for the created files (defaults to the root behaviour name)
        target_directory: default is to use the current working directory, set this to redirect elsewhere
        with_blackboard_variables: add nodes for the blackboard variables
        with_qualified_names: print the class names of each behaviour in the dot node

    Example:
        Render a simple tree to dot/svg/png file:

        .. graphviz:: dot/sequence.dot

        .. code-block:: python

            root = py_trees.composites.Sequence(name="Sequence", memory=True)
            for job in ["Action 1", "Action 2", "Action 3"]:
                success_after_two = py_trees.behaviours.StatusQueue(
                    name=job,
                    queue=[py_trees.common.Status.RUNNING],
                    eventually = py_trees.common.Status.SUCCESS
                )
                root.add_child(success_after_two)
            py_trees.display.render_dot_tree(root)

    .. tip::

        A good practice is to provide a command line argument for optional rendering of a program so users
        can quickly visualise what tree the program will execute.
    """
    if target_directory is None:
        target_directory = os.getcwd()
    graph = dot_tree(
        root,
        visibility_level,
        collapse_decorators,
        with_blackboard_variables=with_blackboard_variables,
        with_qualified_names=with_qualified_names,
    )
    filename_wo_extension_to_convert = root.name if name is None else name
    filename_wo_extension = utilities.get_valid_filename(
        filename_wo_extension_to_convert
    )
    filenames: typing.Dict[str, str] = {}
    for extension, writer in {
        "dot": graph.write,
        "png": graph.write_png,
        "svg": graph.write_svg,
    }.items():
        filename = filename_wo_extension + "." + extension
        pathname = os.path.join(target_directory, filename)
        print("Writing {}".format(pathname))
        writer(pathname)
        filenames[extension] = pathname
    return filenames