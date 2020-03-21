let query = require('query-string').parse(window.location.search.substring(1));
let server = undefined;
if (!query.server) {
    server = 'localhost:5000';
} else {
    server = query.server;
}
const ForceGraph3D = require('3d-force-graph');
window.SpriteText = require('three-spritetext');
const io = require('socket.io-client');
let graph = undefined;
let gData = { nodes: [], links: [] };
const socket = io(server);
let do_auto_refresh = false;

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
    let label_node = undefined;
    let label_edge = undefined;
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
        if (data.label_node) {
            let the_label = 'id';
            if (typeof(node_label) === 'function') {
                the_label = 'id'; // not supported, currently, to set
                // this by a function.
            } else {
                the_label = node_label;
            }
            let fn = Function(`return node => {
                const sprite = new SpriteText(node['${the_label}']);
                sprite.color = '${data.label_node.color}';
                sprite.textHeight = ${data.label_node.height};
                sprite.position.z += ${data.label_node.offset};
                return sprite;
            }`);
            try {
                fn = fn();
                if (!fn) {
                    label_node = undefined;
                } else {
                    label_node = fn;
                }
            } catch {
                label_node = undefined;
            }
            do_auto_refresh = true;
        }
        if (data.label_edge) {
            let the_label = 'pred';
            if (typeof(edge_label) === 'function') {
                the_label = 'pred'; // not supported, currently, to set
                // this by a function.
            } else {
                the_label = edge_label;
            }
            let fn = Function(`return edge => {
                const sprite = new SpriteText(edge['${the_label}']);
                sprite.color = '${data.label_edge.color}';
                sprite.textHeight = ${data.label_edge.height};
                sprite.position.z += ${data.label_edge.offset};
                return sprite;
            }`);
            try {
                fn = fn();
                if (!fn) {
                    label_edge = undefined;
                } else {
                    label_edge = fn;
                }
            } catch {
                label_edge = undefined;
            }
            do_auto_refresh = true;
        }
    }
    graph = ForceGraph3D()
            .forceEngine(engine)
            .nodeOpacity(node_opacity)
            .linkOpacity(edge_opacity)
            .nodeColor(node_color)
            .nodeVal(node_size)
            .nodeLabel(node_label)
            .nodeThreeObject(label_node)
            .nodeThreeObjectExtend(true)
            .nodeVisibility(node_visibility)
            .linkVisibility(edge_visibility)
            .linkLabel(edge_label)
            .linkColor(edge_color)
            .linkWidth(edge_size)
            .linkDirectionalArrowLength(arrow_size)
            .linkDirectionalArrowColor(arrow_color)
            .linkDirectionalArrowRelPos(0.95)
            .linkThreeObject(label_edge)
            .linkThreeObjectExtend(true)
            .linkPositionUpdate((sprite, { start, end }) => {
                if (!sprite) return undefined;
                const middlePos = Object.assign(...['x', 'y', 'z'].map(c => ({
                  [c]: start[c] + (end[c] - start[c]) / 2
                })));
                Object.assign(sprite.position, middlePos);
              })
            .backgroundColor(bg_color)
            (document.getElementById('container')).graphData(gData);
});
socket.on('updateNode', data => {
    let node = gData.nodes.filter(node => node.id == data.id);
    if (!node || !node.length) return false;
    node = node[0];
    Object.assign(node, data.attributes);
    graph.graphData(gData);
    if (do_auto_refresh) {
        graph.refresh();
    }
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
    if (do_auto_refresh) {
        graph.refresh();
    }
});

socket.on('batchUpdateNode', data => {
    for (const update of data) {
        let node = gData.nodes.filter(node => node.id === update.id);
        if (!node || !node.length) return false;
        node = node[0];
        Object.assign(node, update.attributes);
    }
    graph.graphData(gData);
    if (do_auto_refresh) {
        graph.refresh();
    }
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
    if (do_auto_refresh) {
        graph.refresh();
    }
});