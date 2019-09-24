class ReliableBroadcast():
	def broadcast(self, q_cob_rb, q_rb_beb):
		"""
        Tries to get a data from the Queue to simply retransmit this data to the
		next Queue.
        :param q_cob_rb: A python Queue object that being used between 
        the Causal Order Broadcast and the Reliable Broadcast.
        :param q_rb_beb: A python Queue object that being used between 
        the Reliable Broadcast and the Best Effort Broadcast.
        """
		while True:
			data = q_cob_rb.get()
			q_rb_beb.put(data)

	def deliver(self, q_rb_beb, q_beb_rb, q_rb_cob):
		"""
        Tries to get a data from the Queue to apply the Reliable Broadcast
        Deliver logic which means create a delivered list and being storing all messages
		that will be received. Everytime a message is not found in the delivered list,
		it needs to be delivered and re-broadcasted.
        :param q_rb_beb: A python Queue object that being used between the Reliable Broadcast
        and the Best Effort Broadcast.
        :param q_beb_rb: A python Queue object that being used between the Best Effort Broadcast
		and the Reliable Broadcast.
		:param q_rb_cob: A python Queue object that being used between the Reliable Broadcast
		and the Causal Order Broadcast.
        """
		delivered = []
		while True:
			data = q_beb_rb.get()  # [host_key, W, m, t]
			m = [data[0], data[3]]
			found = True if m in delivered else False
			if not found:
				delivered.append(m)
				q_rb_beb.put(data)
				q_rb_cob.put(data)