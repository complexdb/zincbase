class GraphCaster:
    def __init__(self, redis_address='redis://'):
        try:
            from flask_socketio import SocketIO, emit
        except ImportError:
            print('Please install zincbase[web]')
            return False
        self.redis = redis_address
        self.socketio = SocketIO(message_queue=self.redis)
        self.socketio.emit('reset')
        self.update_queue = []
   
    def add_node(self, node, initial_color=None):
        node = str(node)
        self.socketio.emit('addNode', {'id': node, 'initial_color': initial_color}, json=True)
    
    def add_edge(self, from_node, to_node, initial_color):
        from_node = str(from_node)
        to_node = str(to_node)
        self.socketio.emit('addLink', {'from': from_node, 'to': to_node,
                                       'initial_color': initial_color, 'data': {'zig': 1}}, json=True)
    
    def update_node(self, node, color=None, size=None, defer=False):
        node = str(node)
        assert not (color is None and size is None)
        attributes = { 'id': node }
        if color:
            attributes.update({'color': color})
        if size:
            attributes.update({'size': size})
        if not defer:
            self.socketio.emit('updateNode', attributes, json=True)
        else:
            self.update_queue.append(attributes)
    
    def batch_update(self):
        self.socketio.emit('batchUpdateNode', self.update_queue, json=True)
        self.update_queue = []

    def initial_render(self, bg_color=0xffffff):
        """Perform the initial setup/rendering of the current graph.

        :param int bg_color: Hex background color for the graph, e.g. 0xFF0000 is red.
        """
        attributes = {}
        if bg_color:
            attributes.update({'bg_color': bg_color})
        self.socketio.emit('render', attributes, json=True)

    def from_kb(self, kb, initial_node_color=None, initial_link_color=None):
        for node in kb.G.nodes:
            self.add_node(kb.node(node), initial_color=initial_node_color)
        for from_node, to_node, _ in kb.G.edges:
            self.add_edge(from_node=from_node, to_node=to_node, initial_color=initial_link_color)