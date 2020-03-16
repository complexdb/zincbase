let query = require('query-string').parse(window.location.search.substring(1));
let server = undefined;
if (!query.server) {
    server = 'localhost:5000';
} else {
    server = query.server;
}
const ForceGraph3D = require('3d-force-graph');
const io = require('socket.io-client');
let graph = undefined;
let gData = { nodes: [], links: [] };
const socket = io(server);

socket.on('addNode', data => {
    gData.nodes.push(data);
});
socket.on('addLink', data => {
    gData.links.push(data);
});
socket.on('reset', () => {
    graph = undefined;
    gData = { nodes: [], links: [] };
})
socket.on('render', data => {
    let node_color = 0x11bb88;
    let node_size = 10;
    let node_opacity = 0.9;
    let node_label = 'id';
    let node_visibility = true;
    let edge_visibility = true;
    let edge_label = 'pred';
    let edge_opacity = 1;
    let edge_color = 0x333333;
    let edge_size = 0; // ==1px
    let arrow_size = 0, arrow_color = 1;
    let bg_color = 0xffffff;
    let engine = 'd3';
    if (data) {
        if (data.bg_color) {
            bg_color = data.bg_color;
        }
        if (data.engine) {
            engine = data.engine;
        }
        if (data.node_opacity) {
            node_opacity = data.node_opacity;
        }
        if (data.edge_opacity) {
            edge_opacity = data.edge_opacity;
        }
        if (data.arrow_size) {
            arrow_size = data.arrow_size;
            arrow_color = data.arrow_color;
        }
        if (data.node_color) {
            let fn = Function('return ' + data.node_color);
            try {
                fn = fn();
                if (!fn) {
                    node_color = data.node_color; // a value
                } else {
                    node_color = fn;
                }
            } catch {
                node_color = data.node_color; // a value
            }
        }
        if (data.node_size) {
            let fn = Function('return ' + data.node_size);
            try {
                fn = fn();
                if (!fn) {
                    node_size = data.node_size; // a value
                } else {
                    node_size = fn;
                }
            } catch {
                node_size = data.node_size; // a value
            }
        }
        if (data.node_label) {
            let fn = Function('return ' + data.node_label);
            try {
                fn = fn();
                if (!fn) {
                    node_label = data.node_label; // a value
                } else {
                    node_label = fn;
                }
            } catch {
                node_label = data.node_label; // a value
            }
        }
        if (data.node_visibility !== undefined) {
            let fn = Function('return ' + data.node_visibility);
            try {
                fn = fn();
                if (!fn) {
                    node_visibility = data.node_visibility; // a value
                } else {
                    node_visibility = fn;
                }
            } catch {
                node_visibility = data.node_visibility; // a value
            }
        }
        if (data.edge_visibility !== undefined) {
            let fn = Function('return ' + data.edge_visibility);
            try {
                fn = fn();
                if (!fn) {
                    edge_visibility = data.edge_visibility; // a value
                } else {
                    edge_visibility = fn;
                }
            } catch {
                edge_visibility = data.edge_visibility; // a value
            }
        }
        if (data.edge_label) {
            let fn = Function('return ' + data.edge_label);
            try {
                fn = fn();
                if (!fn) {
                    edge_label = data.edge_label; // a value
                } else {
                    edge_label = fn;
                }
            } catch {
                edge_label = data.edge_label; // a value
            }
        }
        if (data.edge_color) {
            let fn = Function('return ' + data.edge_color);
            try {
                fn = fn();
                if (!fn) {
                    edge_color = data.edge_color; // a value
                } else {
                    edge_color = fn;
                }
            } catch {
                edge_color = data.edge_color; // a value
            }
        }
        if (data.edge_size) {
            let fn = Function('return ' + data.edge_size);
            try {
                fn = fn();
                if (!fn) {
                    edge_size = data.edge_size; // a value
                } else {
                    edge_size = fn;
                }
            } catch {
                edge_size = data.edge_size; // a value
            }
        }
    }
    graph = ForceGraph3D()
            .forceEngine(engine)
            .nodeOpacity(node_opacity)
            .linkOpacity(edge_opacity)
            .nodeColor(node_color)
            .nodeVal(node_size)
            .nodeLabel(node_label)
            .nodeVisibility(node_visibility)
            .linkVisibility(edge_visibility)
            .linkLabel(edge_label)
            .linkColor(edge_color)
            .linkWidth(edge_size)
            .linkDirectionalArrowLength(arrow_size)
            .linkDirectionalArrowColor(arrow_color)
            .linkDirectionalArrowRelPos(0.95)
            .backgroundColor(bg_color)
            (document.getElementById('container')).graphData(gData);
});
socket.on('updateNode', data => {
    const node = gData.nodes[data.id];
    Object.assign(node, data.attributes);
    graph.graphData(gData);
});
socket.on('updateEdge', data => {
    let edge = gData.links.filter(edge =>
        edge.source.id == data.from &&
        edge.target.id == data.to &&
        edge.pred == data.pred
    );
    if (!edge || !edge.length) return false;
    edge = edge[0];
    Object.assign(edge, data.attributes);
    graph.graphData(gData);
});

socket.on('batchUpdateNode', data => {
    for (const update of data) {
        const node = gData.nodes[update.id];
        Object.assign(node, update.attributes);
    }
    graph.graphData(gData);
});
socket.on('batchUpdateEdge', data => {
    for (const update of data) {
        let edge = gData.links.filter(edge =>
            edge.source.id == update.from &&
            edge.target.id == update.to &&
            edge.pred == update.pred
        );
        if (!edge || !edge.length) continue;
        edge = edge[0];
        Object.assign(edge, update.attributes);
    }
    graph.graphData(gData);
});