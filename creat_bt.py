from xml.dom import minidom
import py_trees
from behaviors import *
import xml.parsers.expat


def xml_loader(args, bt_xml_path, emulator, blackboard, action_node_des, condition_node_des, logger): 
    
    try:
        with open(bt_xml_path, "r") as f:
            xml_doc = minidom.parse(f) 
        root = xml_doc.documentElement 
    except xml.parsers.expat.ExpatError as e:
        return "XML_ERROR"
    tree = xml_to_tree(root, args, emulator, blackboard, action_node_des, condition_node_des, logger)
    return tree
    

def xml_to_tree(xml_element:minidom.Element, args, emulator, blackboard, action_node_des, condition_node_des, logger):
    

    p_name = xml_element.tagName
    if p_name == "Sequence":
        p_node = py_trees.composites.Sequence("Sequence",memory=False)
    elif p_name == "Fallback":
        p_node = py_trees.composites.Selector("Fallback",memory=False)
    elif p_name == "Parallel":        
        p_node = py_trees.composites.Parallel("Parallel", policy=py_trees.common.ParallelPolicy.SuccessOnAll(synchronise=True))
    else:
        raise Exception("control node name not found")

    
    node_list = []
    for child in xml_element.childNodes:
        if child.nodeType == child.ELEMENT_NODE:
            
            if child.hasChildNodes(): 
                node = xml_to_tree(child, args, emulator, blackboard, action_node_des, condition_node_des, logger)
            
            
            elif child.tagName == "Condition":
                node_str = condition_node_des[child.getAttribute("instance_name")]
                node = Condition_Behavior(child.getAttribute("instance_name"), emulator, blackboard, node_str, logger)
            
            elif child.tagName == "Action":
                action_description_dict = action_node_des[child.getAttribute("class")]
                node = Action_Behavior(child.getAttribute("class"), 
                                       child.getAttribute("instance_name"), 
                                       action_description_dict, 
                                       emulator, 
                                       blackboard, 
                                       logger)
                
            else:
                raise Exception("leaf node name not found")
                
            node_list.append(node)

    p_node.add_children(node_list) 

    return p_node 