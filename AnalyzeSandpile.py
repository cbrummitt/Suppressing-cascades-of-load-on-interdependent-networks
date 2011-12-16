from Sandpile import *

class AnalyzeSandpile:
	def __init__(self, G_input, cap, dr):
		self.G = G_input
		self.capacities = cap
		self.dissipation_rate = dr
		self.pile = Sandpile(self.G, self.capacities, self.dissipation_rate)

	def __repr__(self):
		return 'Sandpile({0}, dissipation {1})'.format(`self.G`, self.dissipation_rate)

	def run_transients(self, transients):
		# Transients
		for i in xrange(transients):
			self.pile.add_sand(False)
		
	def record_topplings(self, time_steps, file_name, plot_results = False):
		# Record # topplings
		topple_data = []
		num_sands_data = []
		for i in xrange(time_steps):
			topple_count = self.pile.add_sand(False)
			num_sands_data.append(self.pile.number_of_sands())
			if topple_count > 0:
				topple_data.append(topple_count)
		
		if self.G.number_of_nodes() <= 50:
			print('Sands: '+`self.pile.get_sands()`)
			print('Final capacities: '+`self.capacities`)
		else:
			random_50_indices = rnd.sample(range(self.G.number_of_nodes()),50)
			print('50 of the sands: '+`[self.pile.get_sands_at_node(i) for i in random_50_indices]`)
			print('50 of the capacities: '+`[self.capacities[i] for i in random_50_indices]`)
		if time_steps < 50:
			print('Topplings: '+`topple_data`)
		else:
			print('Last 50 topplings: '+`topple_data[-50:-1]`)
		
		log_bins = [10.0**(float(x)/5.0) for x in xrange(5*(1+int(np.log10(max(topple_data)))))]
		log_binned_data = np.histogram(topple_data, log_bins, normed = True)
		
		# Write the results to a file
		fw = open(file_name+'.txt', 'w')
		fw.write(`topple_data`)
		fw.close()
		
		# Convert the topple data to be readable by Mathematica
		fs = open(file_name+'.txt','r')
		fo = open(file_name+'_converted.txt','w')
		
		char = fs.read(1)
		while char != '':
			if char == '[':
				fo.write('{')
			elif char == ']':
				fo.write('}')
			elif char == '\'':
				fo.write('"')
			else:
				fo.write(char)
			char = fs.read(1)
			
		fs.close()
		fo.close()
		
		if plot_results == True:
			self.plot_topple_data(topple_data, log_binned_data, time_steps, file_name)
		
		return topple_data

	def plot_topple_data(self, topple_data, log_binned_data, time_steps, file_name):	
		# Clear the current figure
		plt.clf()
		
		# log y axis
		#plt.subplot(211)
		#plt.hist(topple_data, bins=10, range=None, normed=True, cumulative=False, bottom=None, histtype='step', align='mid', orientation='vertical', rwidth=None, log=True)
		#plt.title('Histogram')
		
		#plt.subplot(312)
		#plt.hist(map(lambda x: np.log(x),topple_data), bins=len(log_bins), range=None, normed=True, cumulative=False, bottom=None, histtype='step', align='mid', orientation='vertical', rwidth=None, log=True)
		#plt.title('Histogram')
		
		plt.subplot(2,3,1)
		plt.loglog(log_binned_data[1][0:-1], log_binned_data[0], marker = 'o')
		plt.grid(True)
		plt.xlabel('Avalanche size')
		plt.ylabel('Probability')
		plt.title(`sum(topple_data)`+' Topplings')
		
		plt.subplot(2,3,4)
		plt.title('Degrees (max = '+`max(self.G.degree().values())`+')')#+', ave = '+str(round(np.average(self.G.degree().values()),3))+')')
		plt.ylabel('degree')
		plt.xlabel('rank')
		plt.loglog(sorted(nx.degree(self.G).values(),reverse=True),'b-',marker='o')
		
		plt.subplot(2,3,3)
		plt.title('Sands over time')
		plt.ylabel('# sands')
		plt.xlabel('time')
		#plt.plot(xrange(time_steps), num_sands_data)
		
		plt.subplot(2,3,2)
		plt.title('Proximity to toppling')
		plt.ylabel('sands & capacity')
		plt.xlabel('degree rank')
		node_degrees = np.array([(i, self.G.degree(i)) for i in self.G.nodes()], dtype = [('label', int), ('degree', int)])
		nodes_sorted_by_degrees = map(lambda x: x[0], np.sort(node_degrees, order = 'degree'))
		sand_bars = [self.pile.get_sands_at_node(i) for i in nodes_sorted_by_degrees]
		capacity_minus_sand_bars = [self.capacities[i] - self.pile.get_sands_at_node(i) for i in nodes_sorted_by_degrees]
		plt.bar(nodes_sorted_by_degrees, sand_bars, width = 1, color ='r')
		plt.bar(nodes_sorted_by_degrees, capacity_minus_sand_bars, width = 1, color ='b', bottom=sand_bars)
		
		plt.subplot(2,3,5)
		plt.title('Capacities')#(max:'+`max(self.capacities)`+')')
		plt.ylabel('capacity')
		plt.xlabel('rank')
		#plt.loglog(sorted(original_capacities, reverse=True),'b-',marker='o')
		plt.loglog(sorted(self.pile.get_capacities(), reverse=True), 'r-', marker='^') 
		
		plt.subplot(2,3,6)
		plt.title(`sum(self.pile.get_capacity_changes())`+' cap. changes')
		plt.ylabel('capacity change')
		plt.xlabel('which node')
		#plt.plot(xrange(self.G.number_of_nodes()), self.pile.get_capacity_changes())
		
		plt.subplots_adjust(hspace=.8, wspace=.8)
		plt.suptitle(`self.G.number_of_nodes()`+' nodes, dissipation rate = '+str(round(self.dissipation_rate,3))+',  '+`time_steps`+' grains dropped',fontsize=12)
		#(after '+`transients`+' transients)'
		
		#total_time = time.time()-beginTime
		#print('{0:.3f} seconds, {1:.3f} minutes, {2:.3f} hours.'.format(total_time, total_time/60.0, total_time/3600.0))
	
		#plt.show()
		plt.savefig(file_name)