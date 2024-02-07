class PlotGraph:

    def __init__(self, graph, title, cmap, type='image',lines=None, num=None, colors = None, markers = None, linestyle=None, labels=None):
        self.graph = graph
        self.title = title
        self.cmap = cmap
        self.type = type
        self.lines = lines
        self.num = num
        self.labels = labels
        self.linestyle = linestyle
        self.colors = colors
        self.markers = markers