## Introduction
This package is for growing random graphs and trees by using continuous quantum walks.
One or more quantum walkers explore a graph and at random times they collapse on its nodes, where a new node is attached. By alternatning evolution and collapse and by controlling the average exploration time, graphs and trees with various characteristics can be grown.

## `QGraph` class

### initialization and basic usage
The `QGraph` class represents a single graph, which is instantiated as a trivial graph with a single node.
The required parameters are the number of quantum walkers and the average exploration time between collapses:
```python
G = QGraph(walkers = 1, exploration=0.5)
```

We can grow the graph by adding nodes:
```python
G.add_nodes(nodes = 100)
```
Now the graph `G` has 101 nodes (`G.nodes` returns 101).

### visualizations
We can visualize a graph via
```python
G.draw()
```
![img](/plots/examplegraph.pdf "Example graph")

and export the diagram (several extensions are supported):
```python
G.export('my_graph.pdf')
```

## `QGraphList` class
The `QGraphList` class is for managing a collection of `QGraph` objects, which are internally stored in a list.
The `QGraphList` class contains a number of utilities and it's meant to work in a flexible way.
The `repr` of a `QGraphList` object returns a handy Pandas DataFrame with a summary of its contents, which is particularly nice when working in a jupyter notebook environment.

### initialization and basic usage
```python
GL = QGraphList()
```
We populate it by growing random graphs according to the desired specs. This is automatically done in parallel, with a visual bar that indicates the status of the computation:
```python
specs = [{'walkers':w, 'nodes':n, 'exploration':t} for t in [0.1,0.5,1.0] for w in [1,2,3] for n in [100,200]]
GL.grow_random_graphs(specs)
```
We can populate the database at any time, any number of times. Each new graph is treated as a distinct object.
We can observe some properties of the graphs by invoking `GL.dataframe`.

### visualizations
The properties of the graphs can be plotted via an internal use of Seaborn:
```python
ax = G.lineplot(x='exploration', y='diameter', hue='walkers')
ax.set_xscale('log')
```
![img](/plots/diameter.pdf "Diameter plot")
Notice that the `lineplot` method returns a matplotlib axis instance to allow for further customizaion.

### utilities
`QGraphList` objects can be added to merge their internal (e.g. `G = G1 + G2`), and if possible their dataframes.

We can also select and/or exclude parts of the collection:
```python
G.select('walkers', 2).exclude('nodes', 200)
```

as the `select` and `exclude` methods return new instances of `QGraphList`, we can chain them with any other class method:
```python
G.exclude('walkers', 1).select('nodes', 200).lineplot(x='exploration', y='clustering', hue='walkers')
```

`QGraphList` objects are iterable:
```python
[g.nodes for g in G]
```

`QGraphList` objects can be merged simply by summing them:
```python
G1 = QGraphList().grow_random_graphs([{'walkers':1, 'nodes':50, 'exploration':0.1}]*5)
G2 = QGraphList().grow_random_graphs([{'walkers':2, 'nodes':50, 'exploration':0.1}]*5)
G = G1 + G2 
```

### Saving and loading
As computations might become expensive, we can save and load a `QGraphList` object:
```python
G.save('large_database.npy')

G2 = QGraphList()
G2.load('large_database.npy')
```
Once we save a `QGraphList` object, saving becomes automatic every time we add new `QGraph` objects to it.