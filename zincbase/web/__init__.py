class GraphCaster:
    def __init__(self, redis_address='redis://'):
        """Create a graph cast, so that a KB can be displayed
        on localhost:5000. It won't work if you installed basic
        Zincbase -- try `pip install zincbase[web]`.
        :param str redis_address: URL of the redis instance
        the graph cast should use. For local use, let the
        default stand, provided you have `docker run -p 6379:6379 -d redis`
        """
        try:
            from flask_socketio import SocketIO, emit
        except ImportError:
            print('Please install zincbase[web]')
            return False
        self.redis = redis_address
        self.socketio = SocketIO(message_queue=self.redis)
        self.socketio.emit('reset')
        self.node_update_queue = []
        self.edge_update_queue = []
   
    def add_node(self, node):
        """Add a node to the graph cast.

        :param Node node: A node in the KB.
        """
        attrs = { 'id': str(node) }
        attrs.update(node.attrs)
        self.socketio.emit('addNode', attrs, json=True)
    
    def add_edge(self, from_node, to_node, attributes):
        """Add an edge to the graph cast.
        """
        attrs = { 'source': str(from_node), 'target': str(to_node) }
        attrs.update(attributes)
        self.socketio.emit('addLink', attrs, json=True)
    
    def update_node(self, node, defer=False):
        """Update a node in the graph cast with its current attributes in the KB.
        
        :param Node node: The node to update
        :param bool defer: If False, send immediately (and cause immediate
        re-rendering on the client.) If True, batch and wait until `batch_update()`
        to send updates together and re-render only once.
        """
        attrs = { 'id': str(node) }
        attrs.update({ 'attributes': node.attrs })
        if not defer:
            self.socketio.emit('updateNode', attrs, json=True)
        else:
            self.node_update_queue.append(attrs)
    
    def update_edge(self, edge, defer=False):
        """Update an edge in the graph cast with its current attributes in the KB.
        
        :param str sub, pred, obj: The edge, described as subject, predicate, object
        :param KB kb: The knowledge base in which the edge exists
        :param bool defer: If False, send immediately (and cause immediate
        re-rendering on the client.) If True, batch and wait until `batch_update()`
        to send updates together and re-render only once.
        """
        attrs = { 'attributes': edge.attrs }
        attrs.update({'from': edge._sub, 'pred': edge._pred, 'to': edge._ob})
        if not defer:
            self.socketio.emit('updateEdge', attrs, json=True)
        else:
            self.edge_update_queue.append(attrs)
    
    def batch_update(self):
        """Perform a batch update. Any `update_node` or `update_edge` calls that
        were made with `defer=True` will now be sent to the frontend.
        """
        self.socketio.emit('batchUpdateNode', self.node_update_queue, json=True)
        self.socketio.emit('batchUpdateEdge', self.edge_update_queue, json=True)
        self.node_update_queue = []
        self.edge_update_queue = []

    def reset(self):
        """If any web client was already listening, reset it"""
        self.socketio.emit('reset')

    def render(self, node_color=0x11bb88, node_size=10, node_opacity=0.9,
               node_label='id', node_visibility=True, edge_label='pred',
               edge_opacity=1, edge_color=0x333333, edge_size=0,
               edge_visibility=True, arrow_size=0, arrow_color=0x000001,
               label_node=False, label_node_color='black', label_node_height=3,
               label_node_offset=1, label_edge=False, label_edge_color='black',
               label_edge_height=3, label_edge_offset=1,
               bg_color=0xffffff, engine='d3'):
        """Perform the initial setup/rendering of the current graph.

        :param node_color: Either a 24bit RGB int (such as 0xFF001A) or a string
        containing a Javascript function which takes `node` as an argument, for
        example `node => node.color`
        :param node_size: Either a number >= 0 or a string containing a Javascript
        function, for example `node => Math.log(node.enormity)`
        :param node_label: Either a string representing a property of the node
        to display (on hover) as its label, or a Javascript function returning a string.
        All nodes have a property called `id` which is their name/string repr.
        :param node_visibility: Either a string representing a property of the node
        which evaluates truthy/falsy (in Javascript) to determine whether to display
        the node, or a JS function that returns true or false, or True/False.
        :param label_node: If True, nodes will be labeled with `node_label`. Unlike
        `node_label`, which only displays on hover, this is a permanent text. Note
        that the value updates when the value of `node[node_label]` changes (in Python).
        :param label_node_color: RGB value for the color of a node's permanent label
        :param label_node_height: Text height for the node's permanent label
        :param label_node_offset: Integer specifying how far out from the node the 
        label should appear. Default is 1 unit on the z-axis.
        :param edge_visibility: Either a string representing a property of the edge
        which evaluates truthy/falsy (in Javascript) to determine whether to display
        the edge, or a JS function that returns true or false, or True/False.
        :param edge_label: Either a string representing a property of an edge
        to display (on hover) as its label, or a Javascript function returning a string.
        Defaults to the predicate.
        :param float edge_opacity: Opacity of the edges, from 0-1
        :param edge_color: Either a 24bit RGB int or a string containing a Javascript
        function which takes `edge` as an argument, for example `edge => edge.color`.
        :param edge_size: The width of an edge. Either a number >= 0 (where 0 means 1px)
        or a string containing a Javascript function.
        :param label_edge: If True, nodes will be labeled with `edge_label`. Unlike
        `edge_label`, which only displays on hover, this is a permanent text. Note
        that the value updates when the value of `edge[edge_label]` changes (in Python).
        :param label_edge_color: RGB value for the color of a edge's permanent label
        :param label_edge_height: Text height for the edge's permanent label
        :param label_edge_offset: Integer specifying how far out from the edge the 
        label should appear. Default is 1 unit on the z-axis.
        :param int arrow_size: If >0, display directional arrows on edges of that size.
        :param int arrow_color: Color of arrows (if arrow_size > 0)
        :param int bg_color: Hex background color for the graph, e.g. 0xFF0000 is red.
        :param str engine: Specify d3 or ngraph. ngraph is faster but can be buggy, and
        is only really suitable for static graphs. The layouts can look different also.
        """
        if label_node:
            label_node = {
                'color': 'black',
                'height': 3,
                'offset': node_size + label_node_offset
            }
        if label_edge:
            label_edge = {
                'color': 'black',
                'height': 3,
                'offset': edge_size + label_edge_offset
            }
        attributes = { 'node_color': node_color, 'node_size': node_size,
                       'node_opacity': node_opacity, 'node_label': node_label,
                       'node_visibility': node_visibility, 'edge_visibility': edge_visibility,
                       'edge_opacity': edge_opacity, 'edge_color': edge_color,
                       'edge_size': edge_size, 'edge_label': edge_label,
                       'arrow_size': arrow_size, 'arrow_color': arrow_color,
                       'label_node': label_node, 'label_edge': label_edge,
                       'engine': engine, 'bg_color': bg_color }
        self.socketio.emit('render', attributes, json=True)

    def from_kb(self, kb):
        # TODO Permit this to work with subsampling the KB
        for node in kb.G.nodes:
            self.add_node(kb.node(node))
        for from_node, to_node, edge_attributes in kb.G.edges.data():
            self.add_edge(from_node=from_node, to_node=to_node, attributes=edge_attributes)