class PlotGraph:

    def __init__(self, graph, title, cmap, type='image',lines=None, num=None):
        self.graph = graph
        self.title = title
        self.cmap = cmap
        self.type = type
        self.lines = lines
        self.num = num