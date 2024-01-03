import matplotlib.pyplot as plt

class PlotUtils:

    def set_fig_size(fig,size):
        dpi = 100

        # Convertir la taille en pixels en pouces
        inches_width = size[0] / dpi
        inches_height = size[1] / dpi
        fig.set_dpi(dpi)
        fig.set_figheight(inches_height)
        fig.set_figwidth(inches_width)

    @staticmethod
    def get_figure():
        fig,ax= plt.subplots()
        return fig,ax
    

    @staticmethod
    def generate_matplotlib(figure, graph):
        fig, ax = figure
        
        if graph.type=='image':
            ax.imshow(graph.graph,cmap=graph.cmap)
        elif graph.type=='plot':
            (x,y) = graph.graph
            ax.plot(x,y)
        
        if graph.lines!=None:
            for i in graph.lines:
                ax.axvline(x=i, color='r', linestyle='--')


        ax.set_title(graph.title)
        return fig,ax


    @staticmethod
    def close():
        plt.close()