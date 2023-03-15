LISTBOX_MIMETYPE = "application/x-item"

"""

Setting for sphere_base nodes

"""

OP_SPHERE_NODE_BASE = 0
OP_SPHERE_NODE_PERSON = 1
OP_SPHERE_NODE_ITEM = 2
OP_SPHERE_EDGE = 3

SPHERE_NODE_EDITOR = 1
SPHERE_NODES = {}
IMG_DIR = "..//sphere_base/model/resources/meshes/"


DICTIONARY_SPHERE_NODE_ICONS = \
    {
        "Female": "woman_icon", "LGBT": "lgbt_icon", "Male": "man_icon",
        "Type": "item_icon", "landline": "landline_icon", "laptop": "laptop_icon",
        "mobile": "mobile_icon", "passport": "passport_icon", "pc": "pc_icon",
        "rfid tag": "rfid_tag_icon", "smart card": "smart_card_icon", "smart tv": "smart_tv_icon",
        "smart phone": "smart_phone_icon", "smart watch": "smart_watch_icon", "tablet": "tablet_icon",
        "webcam": "webcam_icon", "wifi": "wifi_icon"
    }


class ConfException(Exception): pass
class InvalidNodeRegistration(ConfException): pass
class OpCodeNotRegistered(ConfException): pass


def register_node_now(op_code, class_reference, editor_type):
    nodes = SPHERE_NODES
    if op_code in nodes:
        raise InvalidNodeRegistration("Duplicate node registration of '%s'. There is already %s" % (
            op_code, nodes[op_code]
        ))
    nodes[op_code] = class_reference


def register_node(op_code, editor_type):
    def decorator(original_class):
        register_node_now(op_code, original_class, editor_type)
        return original_class
    return decorator


def get_class_from_type(node_type, editor_type):

    nodes = SPHERE_NODES
    if node_type not in nodes:
        raise OpCodeNotRegistered("OpCode '%d' is not registered" % node_type)
    return nodes[node_type]


# import all nodes both from the sphere_iot spheres as from the detail node editor and register them
from sphere_base.sphere_overlay.sphere_nodes import *


