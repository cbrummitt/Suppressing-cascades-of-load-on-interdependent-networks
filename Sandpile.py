import networkx as nx
import random as rnd
import numpy as np
#import scipy as sp
import matplotlib.pyplot as plt
import time
from sets import Set


class Sandpile:
	def __init__(self, input_graph, input_capacities, input_dissipation):
		self.G = input_graph
		self.nodes = self.G.nodes()
		self.num_nodes = len(self.nodes)
		self.capacities = input_capacities
		self.sands = [rnd.randint(0,input_capacities[i]-1) for i in xrange(self.num_nodes)]
		self.dissipation = input_dissipation
		self.topple_list = Set([])
		self.num_sands = sum(self.sands)
		self.capacity_changes = [0 for i in xrange(self.num_nodes)]
	
	def __repr__(self):
		return 'Sandpile(%s nodes)' % len(self.nodes)
	
	def get_capacities(self):
		return self.capacities
	
	def get_capacity_changes(self):
		return self.capacity_changes
	
	def get_sands(self):
		return self.sands

	def get_sands_at_node(self, node):
		return self.sands[node]
		
	def number_of_sands(self):
		return self.num_sands

	def add_sand_random_node(self, modify_capacity = False):
		return self.add_sand(rnd.choice(self.nodes), modify_capacity)
	
	def add_sand(self, modify_capacity = False):
		return self.add_sand(rnd.choice(self.nodes), modify_capacity)
		
	def add_sand(self, target, modify_capacity = False):
		'''
		Add one grain of sand to the node 'target'. If needed, topple nodes until equilibrium is restored.
		Return the number of topplings that occurred in the avalanche.
		'''
		num_topplings = 0
		self.sands[target] += 1
		self.num_sands += 1
		if self.sands[target] >= self.capacities[target]:
			self.topple_list.add(target)
		
		while(len(self.topple_list) > 0):
			# Create temporary list of sands for the next round
			# (needed to avoid weird things in the synchronous update)
			next_sands_list = [0 for i in xrange(self.num_nodes)]
			
			# Topple all those nodes that must topple in this round of topplings
			num_topplings += len(self.topple_list)
			for node in self.topple_list:
				# Topple the node
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
					self.sands[node] = np.mod(self.sands[node], num_nbrs)
					
					# ...and if there are any grains leftover, shed them randomly to neighbors
					nbrs_to_get_one_more_grain = rnd.sample(self.G.neighbors(node), self.sands[node])
					for nbr in nbrs_to_get_one_more_grain:
						if rnd.random() > self.dissipation: # with probability given by dissipation, a grain is deleted
							# The grain is successfully shed
							next_sands_list[nbr] += 1
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
		return num_topplings