from Sandpile import Sandpile

import random as rnd
import numpy as np
#import scipy as sp
#import matplotlib.pyplot as plt
#import time
from sets import Set


class TwoSandpile(Sandpile):
	def __init__(self, input_graph, input_capacities, input_dissipation, Na, Nb):
		if input_graph.number_of_nodes() != Na + Nb:
			raise ValueError('The number of a- and b-nodes do not sum to the number of nodes')
		Sandpile.__init__(self, input_graph, input_capacities, input_dissipation)
		self.num_a_nodes = Na
		self.num_b_nodes = Nb
		self.topplings_begun_in_a = []
		self.topplings_begun_in_b = []
		self.num_sands_per_net = {'a': sum([self.sands[i] for i in xrange(Na)]), 'b': sum([self.sands[i] for i in xrange(Na, Na+Nb)])}
	
	def __repr__(self):
		return 'TwoSandpile({0} a-nodes, {1} b-nodes)'.format(self.num_a_nodes, self.num_b_nodes)

	
	def number_of_sands_per_network(self):
		return self.num_sands_per_net
	
	def total_capacity_per_network(self):
		return {'a': sum([self.capacities[i] for i in xrange(self.num_a_nodes)]), 'b': sum([self.capacities[i] for i in xrange(self.num_a_nodes, self.num_a_nodes + self.num_b_nodes)])}
	
	def add_sand(self, modify_capacity = False):
		if rnd.choice(xrange(0, self.num_a_nodes + self.num_b_nodes)) in xrange(0, self.num_a_nodes):
			return self.add_sand_to_network('a', modify_capacity)
		else:
			return self.add_sand_to_network('b', modify_capacity)
	
	def add_sand_to_network(self, which_network, modify_capacity = False):
		if which_network == 'a':
			target = rnd.choice(xrange(0, self.num_a_nodes))
			return ['a', self.add_sand_two_nets(target, modify_capacity)]
		else:
			target = rnd.choice(xrange(self.num_a_nodes, self.num_a_nodes + self.num_b_nodes))
			return ['b',self.add_sand_two_nets(target, modify_capacity)]
	
	def add_sand_two_nets(self, target, modify_capacity):
		'''
		Add one grain of sand to the node 'target'. If needed, topple nodes until equilibrium is restored.
		Return the number of topplings that occurred in the avalanche in both networks [a_topplings, b_topplings].
		'''
		num_a_topplings = 0
		num_b_topplings = 0
		self.sands[target] += 1
		self.num_sands += 1
		if target in xrange(0, self.num_a_nodes):
			self.num_sands_per_net['a'] += 1
		else:
			self.num_sands_per_net['b'] += 1
		
		if self.sands[target] >= self.capacities[target]:
			self.topple_list.add(target)
		
		while(len(self.topple_list) > 0):
			'''
			Create temporary list of sands for the next round (this is needed to avoid weird things in the synchronous update)
			'''
			next_sands_list = [0 for i in xrange(self.num_nodes)]
			
			# Count the topplings (distinguishing a and b nodes)
			for node in self.topple_list:
				if node in xrange(0, self.num_a_nodes):
					num_a_topplings += 1
				else:
					num_b_topplings += 1
			
			# Topple all those nodes that must topple in this round of topplings
			for node in self.topple_list:
				# Figure out to which network the node belongs ('a' or 'b')
				nodes_network = 'a'
				if node in xrange(self.num_a_nodes, self.num_a_nodes + self.num_b_nodes):
					nodes_network = 'b'
					
				# Topple the node
				self.num_sands_per_net[nodes_network] -= self.sands[node] #We eventually get rid of all of node's grains
				num_nbrs = len(self.G.neighbors(node))
				if num_nbrs == 0:
					self.sands[node] = 0 # If no neighbors, delete those grains of sand
				else:
					# Shed evenly to neighbors
					sands_per_neighbor = self.sands[node] / num_nbrs # Evaluates to an integer (floor function)
					for i in self.G.neighbors(node):
						if sands_per_neighbor > 0:
							# With probability given by dissipation f, a grain is deleted
							transferred_sands = np.random.binomial(sands_per_neighbor, 1 - self.dissipation) 
							next_sands_list[i] += transferred_sands
							self.num_sands += transferred_sands - sands_per_neighbor
							if i in xrange(0, self.num_a_nodes):
								self.num_sands_per_net['a'] += transferred_sands
							else:
								self.num_sands_per_net['b'] += transferred_sands
					self.sands[node] = np.mod(self.sands[node], num_nbrs)
					
					# ...and if there are any grains leftover, shed them randomly to neighbors
					nbrs_to_get_one_more_grain = rnd.sample(self.G.neighbors(node), self.sands[node])
					for nbr in nbrs_to_get_one_more_grain:
						if rnd.random() > self.dissipation: # with probability given by dissipation, a grain is deleted
							# The grain is successfully shed
							next_sands_list[nbr] += 1
							if nbr in xrange(0, self.num_a_nodes):
								self.num_sands_per_net['a'] += 1
							else:
								self.num_sands_per_net['b'] += 1
						else:
							# The grain is deleted
							self.num_sands -= 1
					self.sands[node] = 0
					
			# After all the topplings, add the grains in next_sands_list to self.sands
			# ... and record which ones must topple in the next round of topplings
			self.topple_list = Set([])
			for node in self.nodes:
				self.sands[node] += next_sands_list[node]
				if self.sands[node] >= self.capacities[node]:
					self.topple_list.update([node])
				
		# After all the toppling events, if we are modifying capacities, increment the capacity of the initial node
		if (modify_capacity == True and num_topplings > .001 * self.num_nodes):
			self.capacities[target] += 1
			self.capacity_changes[target] += 1
			
		# Return the number of toppling events in networks a, b
		return [num_a_topplings, num_b_topplings]