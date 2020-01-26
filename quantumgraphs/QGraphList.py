from typing import List
from . import QGraph
from p_tqdm import p_imap
from IPython.display import display
import pandas as pd
from collections import defaultdict
import seaborn as sns
import numpy as np

class QGraphList:
    """
    A class to manage a collection of `QGraphs` with several helper functions.
    A `QGraphList` object allows one to generate and add random graphs to the list, 
    access them via index notation (e.g. GL[3]), display a Pandas DataFrame summary with the
    properties of the graphs 
    """

    def __init__(self, lst: List = None):
        if lst is None or isinstance(lst, list):
            self.list = lst or []
        else:
            raise ValueError('Initialize `QGraphList` with a list of `QGraph` objects or as `QGraphList()`')

        self.dataframe_ = None
        self.numbers = {1:'one', 2:'two', 3:'three', 4:'four', 5:'five', 6:'six', 7:'seven', 8:'eight'}
        self.filename = None
    
    def __getitem__(self, index: int):
        return self.list[index]

    def __len__(self):
        return len(self.list)

    def __contains__(self, element):
        if not isinstance(element, QGraph):
            return False
        return hash(element) in [hash(G) for G in self.list]

    def __repr__(self):
        df = pd.DataFrame([(G.exploration, G.walkers, G.nodes) for G in self.list], columns=['exploration', 'walkers', 'nodes'])
        display(df)
        return ''

    def __add__(self, other):
        """
        Dunder method to merge two QGraphList objects by adding them, e.g. GL = GL1 + GL2
        """
        try:
            merged_list = self.list + other.list
            GL = QGraphList(lst = merged_list)

            if self.dataframe_ is not None and other.dataframe_ is not None:
                GL.dataframe_ = self.dataframe_.append(other.dataframe_)
        except:
            raise TypeError('Adding is allowed only between QGraphList objects')

        return GL

    @property
    def dataframe(self):
        """
        Descriptive pandas dataframe with information about diameter, degree distribution,
        clustering coefficient and leaf fraction for all the graphs in the list.
        """
        if self.dataframe_ is None:
            self.dataframe_ = pd.DataFrame([(G.exploration, self.numbers[G.walkers], G.nodes,
                            G.diameter, G.clustering_coefficient, G.degree_distribution, G.leaf_fraction) for G in self.list], 
            columns=['exploration', 'walkers', 'nodes', 'diameter', 'clustering', 'degree distribution', 'leaf fraction'])
        
        # if possible, save again to keep eventually new QGraph properties
        if self.filename:
            self.save(self.filename) 
            
        return self.dataframe_
        
    def append(self, G:QGraph):
        """
        Appends a new QGraph object to the list.
        It also resets the dataframe, as the new entry needs to be computed. As QGraph properties are lazy
        (i.e. their values is retained once computed), this will not impact the overall performance by much.
        """
        self.list.append(G)
        self.dataframe_ = None # Not a big deal, as we only need to compute the properties of G

    def save(self, filename: str):
        """
        Saves the QGraphList object to disk in npy format. 
        Arguments:
            filename (str): name of the file to save
        """
        if filename[-4:] != '.npy':
            raise ValueError('expected fileype: .npy')

        self.filename = filename
        np.save(filename, self.list)

    def load(self, filename: str):
        """
        Loads a QGraphList object from an npy file 
        Arguments:
            filename (str): name of the file to load
        """
        if filename[-4:] != '.npy':
            raise ValueError('expected fileype: .npy')
        self.filename = filename
        self.list = np.load(filename, allow_pickle=True)

    def select(self, property:str, values: list):
        """
        Returns a new QGraphList containing only the QGraph objects with `property`
        having value in `values`. By returning a new QGraphList instance, calls to 
        select and exclude can be chained (e.g. `G.select('exploration', 0.1).exclude('diameter',2)`)

        Arguments:
            property (str): the property to select, e.g. 'diameter'
            values (list): the value(s) that we want to select

        Returns:
            QGraphList: new QGraphList object with the selected QGraph objects
        """
        return QGraphList([G for G in self.list if getattr(G, property) in values])

    def exclude(self, property:str, values: list):
        """
        Returns a new QGraphList containing only the QGraph objects with `property`
        NOT having value in `values`. By returning a new QGraphList instance, calls to 
        select and exclude can be chained (e.g. `G.select('exploration', 0.1).exclude('diameter',2)`)

        Arguments:
            property (str): the property to exclude, e.g. 'diameter'
            values (int or list): the value(s) that we want to exclude

        Returns:
            QGraphList: new QGraphList object without the excluded QGraph objects
        """
        
        return QGraphList([G for G in self.list if getattr(G, property) not in values])

    def lineplot(self, **kwargs):
        """
        Produces a Seaborn lineplot from the graph data.
        
        Arguments:
            **kwargs: the keyword argument we wish to pass to `sns.lineplot`.
            The recommended ones are `x` and `y`, as well as specifications for `hue` and/or `style`.

        Returns:
            matplotlib.axis: the axis object of the plot to further customize the plot

        Example
            ax = GL.lineplot(x='exploration', y='diameter', hue='walkers', style='nodes')
            ax.set_xscale('log')
        """
            
        sns.set()
        sns.set(rc={'figure.figsize':(8,5)})
        sns.set(font_scale=1.2)
        sns.set_style("whitegrid")

        return sns.lineplot(data=self.dataframe, **kwargs)

    def grow_random_graphs(self, specs:List[dict]):
        """
        Fills the QGraphList with random graphs, grown according to `specs`
        Arguments:
            specs (list of dicts): a list of dicts specifying the number of walkers,
            the value of exploration and the number of nodes for the graph to be generated.
            Example: `specs = [{'walkers':1, 'exploration':0.1, 'nodes':100}]`
        """

        def grow_one_graph(spec: dict):
            G = QGraph(spec['walkers'], spec['exploration'])
            G.add_nodes(spec['nodes'] - 1) # the first node is already there
            return G

        iterator = p_imap(grow_one_graph, specs)
        
        try:
            for G in iterator:
                self.append(G)
        except KeyboardInterrupt:
            print('Evaluation interrupted, stopping gracefully.')
