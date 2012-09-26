import time
from TwoSandpile import TwoSandpile

# p = 0.001, 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5


class SimulateIntSandpiles:
	def __init__(self, G_input, cap, dr, num_a_nodes):
		self.G = G_input
		self.Na = num_a_nodes
		self.Nb =  G_input.number_of_nodes() - num_a_nodes
		self.capacities = cap
		self.dissipation_rate = dr
		self.pile = TwoSandpile(self.G, self.capacities, self.dissipation_rate, self.Na, self.Nb)

	def __repr__(self):
		return 'Sandpile({0}, dissipation {1})'.format(`self.G`, self.dissipation_rate)

	def run_transients(self, transients):
		# Transients
		for i in xrange(transients):
			self.pile.add_sand(False)


	def record_topplings(self, time_steps, file_name, plot_results = False):
		beginTime = time.time()
		# Record # topplings
		topple_data = []
		area_data = []

		#num_sands_data = []
		#num_sands_per_net_data = []
		for i in xrange(time_steps):
			topple_count = self.pile.add_sand(False)

			if sum(topple_count[1]['number of topplings']) > 0: # If at least one node toppled
				topple_data.append([topple_count[0],topple_count[1]['number of topplings']])
				area_data.append([topple_count[0],topple_count[1]['number of nodes that toppled']])
			#if sum(topple_count[1]) > 0:
			#	topple_data.append(topple_count)
			#num_sands_data.append(self.pile.number_of_sands())
			#num_sands_per_net_data.append(pile.number_of_sands_per_network().values())
			if i % (time_steps/10) == 0:
				progress_time = time.time()-beginTime
				print('Dropped '+`i`+' grains = '+`int(100.0*float(i)/float(time_steps))`+'% after {0:.3f} seconds, {1:.3f} minutes, {2:.3f} hours.'.format(progress_time, progress_time/60.0, progress_time/3600.0))
		
		#log_bins = [10.0**(float(x)/5.0) for x in xrange(5*(1+int(np.log10(max(topple_data)))))]
		#log_binned_data = np.histogram(topple_data, log_bins, normed = True)
		


		# Write the results to a file
		fw = open(file_name+'-topple_data.txt', 'w')
		fw.write(`topple_data`)
		fw.close()
	
		fw = open(file_name+'-area_data.txt', 'w')
		fw.write(`area_data`)
		fw.close()
		
		# Convert the topple data to be readable by Mathematica
		for dataset in ['topple_data','area_data']:
			fs = open(file_name + '-'+ dataset + '.txt','r')
			fo = open(file_name + '-'+ dataset + '_converted.txt','w')
			
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


# Write the results to a file
# 		fw = open(file_name+'.txt', 'w')
# 		fw.write(`topple_data`)
# 		fw.close()
# 		
# Convert the topple data to be readable by Mathematica
# 		fs = open(file_name+'.txt','r')
# 		fo = open(file_name+'_converted.txt','w')
# 		
# 		char = fs.read(1)
# 		while char != '':
# 			if char == '[':
# 				fo.write('{')
# 			elif char == ']':
# 				fo.write('}')
# 			elif char == '\'':
# 				fo.write('"')
# 			else:
# 				fo.write(char)
# 			char = fs.read(1)
# 			
# 		fs.close()
# 		fo.close()
		
		if plot_results == True:
			self.plot_topple_data(topple_data, log_binned_data, time_steps, file_name)
		
		return topple_data

	def plot_topple_data(self, topple_data, log_binned_data, time_steps, file_name):	
		def log_bin(data):
			'''
			Returns the data binned into logarithmic sized bins, as well as the endpoints of the logarithmic bins
			'''
			if len(data) == 0:
				return [[0,0,0],[0,1,2],plt.plot([0,2],[0,0])]  #Placeholder in case we always drop grains in one network
			else:
				log_bins = [10.0**(float(x)/5.0) for x in xrange(5*(1+int(np.log10(max(data)))))]
				log_binned_data = np.histogram(data, log_bins, normed = True)
				lines, = plt.loglog(log_binned_data[1][0:-1], log_binned_data[0], marker = 'o')
				plt.grid(True)
				plt.xlabel('Avalanche size')
				plt.ylabel('Probability')
				return [log_binned_data, log_bins, lines]
			
		topplings_begun_in_a = map(lambda x: x[1],filter(lambda x: x[0]=='a', topple_data))
		topplings_begun_in_b = map(lambda x: x[1],filter(lambda x: x[0]=='b', topple_data))
		
		if len(topplings_begun_in_a) > 0:
			a_topplings_begun_in_a, b_topplings_begun_in_a = map(list, zip(*topplings_begun_in_a))
		else:
			 a_topplings_begun_in_a, b_topplings_begun_in_a = [[],[]]
		if len(topplings_begun_in_b) > 0:
			a_topplings_begun_in_b, b_topplings_begun_in_b = map(list, zip(*topplings_begun_in_b))
		else:
			a_topplings_begun_in_b, b_topplings_begun_in_b = [[], []]
		
		total_topplings = map(lambda x: x[1][0] + x[1][1], topple_data)
		
		a_topplings = map(lambda x: x[1][0], topple_data)
		b_topplings = map(lambda x: x[1][1], topple_data)

		
		# Clear the current figure
		plt.clf()
		plt.figure(figsize=(20,11))
		plt.suptitle(`self.G.number_of_nodes()`+' nodes, dissipation rate = '+str(round(self.dissipation_rate,3))+',  '+`len(topple_data)`+' avalanches ',fontsize=11)
		
		plt.subplot(2,3,1)
		log_binned_data_aa, log_bins_aa, linesaa = log_bin(a_topplings_begun_in_a)
		log_binned_data_ab, log_bins_ab, linesab = log_bin(b_topplings_begun_in_a)
		legend((linesaa, linesab), ('a','b'), 'upper right', numpoints=1, borderpad=.2)
		plt.title('Begun in a')
		
		plt.subplot(2,3,2)
		log_binned_data_ba, log_bins_ba, linesba = log_bin(a_topplings_begun_in_b)
		log_binned_data_bb, log_bins_bb, linesbb = log_bin(b_topplings_begun_in_b)
		legend((linesba, linesbb), ('a','b'), 'upper right', numpoints=1, borderpad=.2)
		plt.title('Begun in b')
		
		plt.subplot(2,3,3)
		#log_binned_data_total, log_bins_total, lines_total = log_bin(total_topplings)
		log_bin(total_topplings)
		plt.title('Total topplings')
		
		plt.subplot(2,3,4)
		log_binned_data_a, log_bins_a, linesa = log_bin(a_topplings)
		log_binned_data_b, log_bins_b, linesb = log_bin(b_topplings)
		legend((linesa, linesb), ('a','b'), 'upper right', numpoints=1, borderpad=.2)
		plt.title('Topplings in a, b')
		
		plt.subplot(2,3,5)
		plt.title('Degrees (max: '+`max(G.degree().values())`+')')#+', ave = '+str(round(np.average(G.degree().values()),3))+')')
		plt.ylabel('degree')
		plt.xlabel('rank')
		lines_dega, = plt.loglog(sorted(nx.degree(G).values()[0:self.Na],reverse=True),'b-',marker='o')
		lines_degb, = plt.loglog(sorted(nx.degree(G).values()[self.Na:self.Na+self.Nb],reverse=True),'g-',marker='o')
		legend((lines_dega, lines_degb), ('a','b'), 'upper right', numpoints=1, borderpad=.2)
		
		'''
		plt.subplot(2,4,6)
		plt.title('p_a')
		plt.ylabel('degree')
		plt.xlabel('rank')
		lines_degaa, = plt.loglog(sorted(nx.degree(a_internal_graph).values(),reverse=True),'b-',marker='o')
		lines_degab, = plt.loglog(sorted(a_inter_stubs,reverse=True),'g-',marker='o')
		legend((lines_degaa, lines_degab), ('k_aa','k_ab'), 'upper right', numpoints=1, borderpad=.2)
		
		plt.subplot(2,4,7)
		plt.title('p_b')
		plt.ylabel('degree')
		plt.xlabel('rank')
		lines_degbb, = plt.loglog(sorted(nx.degree(b_internal_graph).values(),reverse=True),'b-',marker='o')
		lines_degba, = plt.loglog(sorted(b_inter_stubs,reverse=True),'g-',marker='o')
		legend((lines_degba, lines_degbb), ('k_ba','k_bb'), 'upper right', numpoints=1, borderpad=.2)
		'''		
		'''
		plt.subplot(2,4,6)
		plt.title('Capacities')#(max:'+`max(capacities)`+')')
		plt.ylabel('capacity')
		plt.xlabel('rank')
		plt.loglog(sorted(original_capacities[0:self.Na], reverse=True),'b-',marker='o')
		plt.loglog(sorted(original_capacities[self.Na:self.Na+self.Nb], reverse=True), 'r-', marker='o') 
		#plt.loglog(sorted(original_capacities, reverse=True),'b-',marker='o')
		#plt.loglog(sorted(pile.get_capacities(), reverse=True), 'r-', marker='^') 
		
		plt.subplot(2,4,7)
		plt.title('Proximity to toppling')
		plt.ylabel('sands & capacity')
		plt.xlabel('degree rank')
		node_degrees = np.array([(i, G.degree(i)) for i in G.nodes()], dtype = [('label', int), ('degree', int)])
		nodes_sorted_by_degrees = map(lambda x: x[0], np.sort(node_degrees, order = 'degree'))
		sand_bars = [pile.get_sands_at_node(i) for i in nodes_sorted_by_degrees]
		capacity_minus_sand_bars = [capacities[i] - pile.get_sands_at_node(i) for i in nodes_sorted_by_degrees]
		plt.bar(nodes_sorted_by_degrees, sand_bars, width = 1, color ='r')
		plt.bar(nodes_sorted_by_degrees, capacity_minus_sand_bars, width = 1, color ='b', bottom=sand_bars)
		'''
		
		'''plt.subplot(2,4,8)
		plt.title('Sands over time')
		plt.ylabel('# sands')
		plt.xlabel('time')
		plt.plot(xrange(time_steps), num_sands_data)
		'''
		'''
		plt.subplot(2,4,8)
		plt.title('Sands in each network over time')
		plt.ylabel('# sands')
		plt.xlabel('time')
		lines_a_sands, = plt.plot(xrange(time_steps), map(lambda x: x[0], num_sands_per_net_data), 'b')
		lines_b_sands, = plt.plot(xrange(time_steps), map(lambda x: x[1], num_sands_per_net_data), 'g')
		total_capacity_per_net = pile.total_capacity_per_network()
		plt.plot([0, time_steps],[total_capacity_per_net['a'], total_capacity_per_net['a']],'b--')
		plt.plot([0, time_steps],[total_capacity_per_net['b'], total_capacity_per_net['b']],'g--')
		legend((lines_a_sands, lines_b_sands), ('a', 'b'), 'upper right', numpoints=1, borderpad=.2)
		'''		
		#plt.subplots_adjust(hspace=.4, wspace=.4)
		
		#total_time = time.time()-beginTime
		#print('{0:.3f} seconds, {1:.3f} minutes, {2:.3f} hours.'.format(total_time, total_time/60.0, total_time/3600.0))
		
		plt.show()
		plt.savefig(file_name)