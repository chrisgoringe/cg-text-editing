from .text_edit_node import TextEdit

VERSION = "0.0.1"

NODE_CLASS_MAPPINGS = { "Text Edit" : TextEdit }

WEB_DIRECTORY = "./js"
__all__ = ["NODE_CLASS_MAPPINGS", "WEB_DIRECTORY"]