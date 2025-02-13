from xml.dom import minidom
import py_trees
import xml.parsers.expat
from py_trees.behaviour import Behaviour

class Condition_Behavior(Behaviour):
    """
    Condition Node
    """
    def __init__(self, name):
        self.state = None
        self.condition_name = name
       
        super(Condition_Behavior, self).__init__(name)

    def update(self):
        print("\n\ncondition node " + self.condition_name)

        return self.state


class Action_Behavior(Behaviour):
    """
    Action Node
    """
    def __init__(self, name, instance_name):
        self.state = None
        self.action_name = name
        self.instance_name = instance_name

        super(Action_Behavior, self).__init__(name)
        

    def update(self):
        print("\n\naction node " + self.action_name + " instance name " + self.instance_name)
        
       
        return self.state

def xml_loader(bt_xml_path): 
    '''
    解析XML文件, 转化为树结构
    '''
    try:
        with open(bt_xml_path, "r") as f:
            xml_doc = minidom.parse(f) # Document对象
        root = xml_doc.documentElement # 根元素
    except xml.parsers.expat.ExpatError as e:
        return "XML_ERROR"
    tree = xml_to_tree(root)
    return tree
    

def xml_to_tree(xml_element:minidom.Element):
    '''
    将XML元素转化为py_trees树结构
    '''

    # 处理控制节点
    p_name = xml_element.tagName
    if p_name == "Sequence":
        p_node = py_trees.composites.Sequence("Sequence",memory=False)
    elif p_name == "Fallback":
        p_node = py_trees.composites.Selector("Fallback",memory=False)
    elif p_name == "Parallel":
        # 需要对根据参数策略选择进行调整
        p_node = py_trees.composites.Parallel("Parallel", policy=py_trees.common.ParallelPolicy.SuccessOnAll(synchronise=True))
    else:
        raise Exception("control node name not found")

    # for循环, 处理子节点
    node_list = []
    for child in xml_element.childNodes:
        if child.nodeType == child.ELEMENT_NODE:
            # 子节点有子树, 递归处理 --- 控制节点
            if child.hasChildNodes(): 
                node = xml_to_tree(child)
            # 子节点没有子树 --- 条件节点 or 动作节点
            elif child.tagName == "Condition":
                node = Condition_Behavior(child.getAttribute("instance_name"))
            elif child.tagName == "Action":
                node = Action_Behavior(child.getAttribute("class"), child.getAttribute("instance_name"))
            else:
                raise Exception("leaf node name not found")
                
            node_list.append(node)

    p_node.add_children(node_list) 

    return p_node # 根节点
