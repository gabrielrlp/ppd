class ReliableBroadcast():
	def broadcast(self, q_cob_rb, q_rb_beb):
		while True:
			data = q_cob_rb.get()
			q_rb_beb.put(data)

	def deliver(self, q_rb_beb, q_beb_rb, q_rb_cob):
		delivered = []
		while True:
			data = q_beb_rb.get()  # [host_key, W, m, t, ip]
			found = True if data in delivered else False
			if not found:
				delivered.append(data)
				q_rb_beb.put(data)
				q_rb_cob.put(data)
				