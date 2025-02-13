import os
from render_dot_tree import render_dot_tree
from init_tree import xml_loader


def pyt_plot(xml_path, fig_name, plot_path):
    
    root = xml_loader(xml_path)

    # tree = py_trees.trees.BehaviourTree(root)

    render_dot_tree(root, name=fig_name, target_directory=plot_path)



if __name__ == '__main__':
    
    # ./BTGenDataset, ./BTGenDatasetExample
    data_path_prefix = "../BTGenDataset"
    # good, unreach, badlogic, example
    category = "good"
    xml_prefix_path = f"{data_path_prefix}/{category}/xml/"
    plot_prefix_path = f"{data_path_prefix}/{category}/plot/"
    
    # idx = 21
    for idx in range(1, 26):
        bt_xml_path = os.path.join(xml_prefix_path, f"{idx}.xml")
        pyt_plot(bt_xml_path, idx, plot_prefix_path)
    