class ReliableBroadcast():
	def broadcast(self, q_cob_rb, q_rb_beb):
		while True:
			data = q_cob_rb.get()
			q_rb_beb.put(data)

	def deliver(self, q_rb_beb, q_beb_rb, q_rb_cob):
		delivered = []
		while True:
			data = q_beb_rb.get()  # [host_key, W, m, t, ip]
			time_ip = [data[3],data[4]]
			found = True if time_ip in delivered else False
			# found = True if all(data in delivered) else False
			if not found:
				delivered.append(time_ip)
				q_rb_cob.put(data)
				data.pop()
				q_rb_beb.put(data) #return to beb without ip
				