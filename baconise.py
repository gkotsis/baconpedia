#!/usr/bin/python
# -*- coding: utf-8 -*-
import networkx as nx

def produceGraph(data):
	import itertools
	import pandas as pd
	actors = data[data.predicate=='starring'].object.unique()
	films = data.subject.unique()
	g = nx.Graph()
	for actor in actors:
		# actor = to_unicode_or_bust(actor)
		g.add_node(actor)

	i = 0
	for film in films:
		i = i + 1
		print "[" + str(i) + "]" +film
		# if (i>100):
		# 	break
		tmp = data[data.subject==film]
		actorsFilm = tmp[tmp.predicate=='<starring>'].object.unique()
		tmp = pd.DataFrame(list(itertools.product(actorsFilm, actorsFilm)))
		if (len(tmp)>0):
			tmp = tmp.rename(columns={0:'actorA'})
			tmp = tmp.rename(columns={1:'actorB'})
			tmp = tmp[tmp.actorA!=tmp.actorB]
			tuples = tmp
			for r in tuples.itertuples():
				if g.get_edge_data(r[1],r[2]) is None:
					g.add_edge(r[1], r[2], film=film)
				else:
					tmp = g.get_edge_data(r[1], r[2])['film']
					g.add_edge(r[1], r[2], film=film+"\n"+tmp)

	return g

def findClosest(g, actor):
	import jellyfish
	i = -1
	maxMatch = -1
	rs = None
	for node in g.nodes():
		tmp = jellyfish.jaro_distance(node, actor)
		if tmp>maxMatch:
			rs = node
			maxMatch = tmp

	print actor + " is matched with value " + str(maxMatch) + " against " + rs
	return rs

def baconise(g, actorA, actorB):
	actorA = actorA.replace("_", " ")
	actorB = actorB.replace("_", " ")

	if not(actorA in g.nodes()):
		actorA = findClosest(g, actorA)

	if not(actorB in g.nodes()):
		actorB = findClosest(g, actorB)

	lists = nx.all_shortest_paths(g, actorA, actorB)
	lista = lists.next()
	i = 1
	actors = []
	while not(lista is None):
		try:
			printPath(g, lista)
			lista = lists.next()
			actors = actors +lista
			i = i+1
		except StopIteration:
			break

	print "found " + str(i) + " paths of length " + str(len(lista))
	return list(set(actors))

def baconiseJSON(g, actorA, actorB):
	from networkx.readwrite import json_graph
	rs = baconise(g, actorA, actorB)
	str = json_graph.dumps(g.subgraph(rs))
	return str

def printPath(g, lista):
	i = 0
	while (i<len(lista)-1):
		tmp = g.get_edge_data(lista[i], lista[i+1])['film']
		tmp = list(set(tmp.splitlines()))
		# return tmp
		print lista[i] + "\t" +', '.join(tmp) + "\t" + lista[i+1]
		i = i +1
	return

def cleanActorName(str):
	tmp = str
	tmp = tmp[1:-1] #<actor name> ---> actor name
	if tmp.endswith(" (actor)"):
		tmp = tmp.replace(" (actor)", "")
	if tmp.endswith(" (actress)"):
		tmp = tmp.replace(" (actress)", "")
	return tmp

def loadFromFile(filename):
	import pickle
	g = pickle.load(open(filename))

	newNodes = {}
	for n in g.nodes():
		tmp = cleanActorName(n)
		newNodes[n] = tmp
	g = nx.relabel_nodes(g, newNodes)
	return g

def writeDot(g, filename):
	f = open(filename, 'w')
	f.write("graph graphname {\n")
	for n1, n2 in g.edges():
		n1 = n1.replace("<", "")
		n1 = n1.replace(">", "")
		n1 = n1.replace(" ", "_")
		n1 = n1.replace("-", "_")
		n2 = n2.replace("<", "")
		n2 = n2.replace(">", "")
		n2 = n2.replace(" ", "_")
		n2 = n2.replace("-", "_")
		f.write(n1+ " -- " + n2 + ";\n")
	f.write("}")
	return


	return

print "loadFromFile, baconise, baconiseJSON, produceGraph are available!"

# from operator import itemgetter
# tmp = sorted(g.degree_iter(),key=itemgetter(1),reverse=True)
# In [28]: nx.average_shortest_path_length(g)
# Out[28]: 5.173661925543939
# diameter is 19
