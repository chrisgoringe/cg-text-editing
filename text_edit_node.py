from server import PromptServer
from aiohttp import web
import time

class TextEdit:
    RETURN_TYPES = ("STRING",)
    FUNCTION = "func"
    CATEGORY = "text"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text" : ( "STRING", {"forceInput":True}),
				"timeout": ("INT", { "default": 60, "min": 1, "max": 600, "step": 1, "tooltip":"Time in seconds to wait before passing the input text on"}),
            },
            "optional": {"editor": ("STRING", {"default":"", "multiline":True, "tooltip":"edit here, press 'shift-return' to submit"}),},
            "hidden": {"node_id":"UNIQUE_ID"},
        }
    
    def func(self, text, timeout, node_id, editor=None):
        try:
            POBox.waiting[node_id] = self
            self.message = None
            PromptServer.instance.send_sync("textedit_request", {"node_id": node_id, "message":text, "timeup":False})
            endat = time.monotonic() + timeout
            while time.monotonic() < endat and self.message is None:
                time.sleep(0.1)
            if self.message is None:
                PromptServer.instance.send_sync("textedit_request", {"node_id": node_id, "timeup":True})
                endat = time.monotonic() + 5
                while time.monotonic() < endat and self.message is None:
                    time.sleep(0.1)               
            return ( self.message or text, )
        finally:
            POBox.waiting.pop(node_id,None)

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")

class POBox:
    waiting:dict[int,TextEdit] = {}
    @classmethod
    def send(cls, node_id, message):
        if (the_node := cls.waiting.get(node_id,None)):
            the_node.message = message

routes = PromptServer.instance.routes
@routes.post('/textedit_response')
async def make_image_selection(request):
    post = await request.post()
    POBox.send(post['node_id'], post['message'])
    return web.json_response({})