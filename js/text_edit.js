import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

function send_message(node_id, message) {
    const body = new FormData();
    body.append('message',message);
    body.append('node_id',node_id);
    api.fetchApi("/textedit_response", { method: "POST", body, });
}

function textedit_request(msg) {
    const node = app.graph._nodes_by_id[msg.detail.node_id]
    if (node && node.receive_textedit_request) {
        if (msg.detail.timeup) node.receive_textedit_timeup()
        else node.receive_textedit_request(msg.detail.message)
    } else {
        console.log(`textedit request fell on empty ears - node ${msg.detail.node_id} didn't want it`)
    }
}

app.registerExtension({
	name: "cg.textedit",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeType?.comfyClass==="Text Edit") {
            nodeType.prototype.receive_textedit_request = function(msg) {
                this.widgets[2].value = msg
                this.widgets[2].element.disabled = false
            }
            nodeType.prototype.receive_textedit_timeup = function() {
                send_message( this.id, this.widgets[2].value )
                this.widgets[2].element.disabled = true
            }
            nodeType.prototype.handle_key = function(e) {
                if (e.key == 'Enter' && e.shiftKey) {
                    send_message( this.id, this.widgets[2].value )
                    this.widgets[2].element.disabled = true
                }
            }
        }
    },
    async nodeCreated(node) {
        if (node.receive_textedit_request) {
            node.widgets[2].element.disabled = true
            node.widgets[2].element.addEventListener('keydown',node.handle_key.bind(node))
        }
    },
    setup() {
        api.addEventListener("textedit_request", textedit_request);
    }

})