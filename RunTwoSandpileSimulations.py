from SimulateIntSandpiles import *
import random as rnd
import networkx as nx
import numpy as np

#size_exponent = int(raw_input('size of each network = 10^'))
#Na = 10**size_exponent
greeting = 'Select network type:\n\t[RR] Random regular graph\n\t[ER] Erdos-Renyi\n'
network_type = raw_input(greeting)
possible_network_types = ['RR','ER']
while not(network_type in possible_network_types):
	network_type = raw_input('Enter something in '+`possible_network_types`+'\n'+greeting)
Na = int(raw_input('size of network a = '))
Nb = int(raw_input('size of network b = '))
#pvalues = [0.001, 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5]
#pvalues = [0.0005, 0.065, 0.085]
pvalues = [0.0, 0.07, 0.08]
#pvalues = [.1, .2]
za = int(raw_input('z_a = '))
zb = int(raw_input('z_b = '))
dissipation_rate = float(raw_input('dissipation rate = '))
transients = 10**5
time_steps = 2*10**6

append_to_filename = raw_input('anything to append to the filename? ')

def bern(p):
	'''
	Return 1 with probability p, 0 with probability 1-p
	'''
	if rnd.random() < p:
		return 1
	else:
		return 0

def ERBER(Na, Nb, za, zb, p):
	'''
	Return a NetworkX graph composed of two random ER random graphs
	of sizes Na, Nb, mean degrees za, zb,
	with Bernoulli(p) distributed coupling.
	'''
	network_build_time = time.time()
	
	a_internal_graph = nx.erdos_renyi_graph(Na, float(za)/float(Na))
	b_internal_graph = nx.erdos_renyi_graph(Nb, float(zb)/float(Nb))
	
	
	# Just use the largest connected component
	a_internal_graph = nx.connected_component_subgraphs(a_internal_graph)[0]
	b_internal_graph = nx.connected_component_subgraphs(b_internal_graph)[0]
	# Relabe the nodes to count from 0 (since Sandpile uses this structure)
	mapping_a = dict(zip(a_internal_graph.nodes(),np.arange(0,len(a_internal_graph.nodes()))))
	mapping_b = dict(zip(b_internal_graph.nodes(),np.arange(0,len(b_internal_graph.nodes()))))
	a_internal_graph = nx.relabel_nodes(a_internal_graph,mapping_a)
	b_internal_graph = nx.relabel_nodes(b_internal_graph,mapping_b)
	
	
	a_inter_stubs = [bern(p) for i in a_internal_graph.nodes()]
	b_inter_stubs = [bern(p) for i in b_internal_graph.nodes()]
	while sum(a_inter_stubs) != sum(b_inter_stubs) or abs(sum(a_inter_stubs)-(p*a_internal_graph.number_of_nodes())) > 1:
		a_inter_stubs = [bern(p) for i in a_internal_graph.nodes()]
		b_inter_stubs = [bern(p) for i in b_internal_graph.nodes()]
	
	G = nx.bipartite_configuration_model(a_inter_stubs, b_inter_stubs)
	
	for u, v in a_internal_graph.edges():
		G.add_edge(u, v)
	for u, v in b_internal_graph.edges():
		G.add_edge(a_internal_graph.number_of_nodes()+u, a_internal_graph.number_of_nodes()+v)
	
	network_build_time = time.time() - network_build_time
	print('Generating the network took {0:.3f} seconds, {1:.3f} minutes, {2:.3f} hours.'.format(network_build_time, network_build_time/60.0, network_build_time/3600.0))
	print('The network has {0} nodes, {1} edges'.format(G.number_of_nodes(), G.number_of_edges()))
	return G

def RBR(Na, Nb, za, zb, p):
	'''
	Return a NetworkX graph composed of two random za-, zb-regular graphs of sizes Na, Nb,
	with Bernoulli(p) distributed coupling.
	'''
	network_build_time = time.time()
	
	a_internal_graph = nx.random_regular_graph(za, Na)
	b_internal_graph = nx.random_regular_graph(zb, Nb)

	a_inter_stubs = [bern(p) for i in xrange(Na)]
	b_inter_stubs = [bern(p*float(Na)/float(Nb)) for i in xrange(Nb)]
	while sum(a_inter_stubs) != sum(b_inter_stubs) or abs(sum(a_inter_stubs)-(p*Na)) > 0:
		a_inter_stubs = [bern(p) for i in xrange(Na)]
		b_inter_stubs = [bern(p*float(Na)/float(Nb)) for i in xrange(Nb)]
	
	G = nx.bipartite_configuration_model(a_inter_stubs, b_inter_stubs)
	
	for u, v in a_internal_graph.edges():
		G.add_edge(u, v)
	for u, v in b_internal_graph.edges():
		G.add_edge(Na+u, Na+v)
	
	network_build_time = time.time() - network_build_time
	print('Generating the network took {0:.3f} seconds, {1:.3f} minutes, {2:.3f} hours.'.format(network_build_time, network_build_time/60.0, network_build_time/3600.0))
	return G

start_time = time.time()

for p in pvalues:	
	print('-----------  p = ' + `p` + '  -----------')
	if network_type == 'RR':
		G = RBR(Na, Nb, za, zb, p)
	else:
		G = ERBER(Na, Nb, za, zb, p)
	file_name = network_type + `za` + '-B' + `p` + '-'+ network_type + `zb` + '-Na=' + `Na`+ '-Nb=' + `Nb` + '-f=' + `dissipation_rate` + append_to_filename
	capacities = [G.degree(i) for i in G.nodes()]
	sim = SimulateIntSandpiles(G, capacities, dissipation_rate, Na)
	sim.run_transients(transients)
	sim.record_topplings(time_steps, file_name, plot_results = False)
	
total_runtime = time.time() - start_time
print('Simulation for p in '+`pvalues`+' took {0:.3f} seconds, {1:.3f} minutes, {2:.3f} hours, {3:.3f} days.'.format(total_runtime, total_runtime/60.0, total_runtime/3600.0, total_runtime/86400.0))