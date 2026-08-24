# puprisa/ui/widgets/mpl_canvas.py
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

class MatplotlibFigureCanvas(FigureCanvasQTAgg):
    """A Qt widget that embeds a matplotlib figure for interactive plotting.
    Args:
        parent: Optional parent Qt widget.
        figure: Optional :class:`matplotlib.figure.Figure` instance to embed.
            When omitted, a new figure is created.
    """
    def __init__(self, parent=None, figure=None):
        if figure is None:
            figure = Figure()
        super().__init__(figure)
        if parent is not None:
            self.setParent(parent)