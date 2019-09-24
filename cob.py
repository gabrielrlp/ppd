class CausalOrderBroadcast():
    def broadcast(self, q_api_cob, q_cob_rb, V, mutex, host_key):
        """
        Tries to get a data from the Queue to apply the Causal Order Broadcast
        Broadcast logic which means update the current vector clock, increase the
        local signal number (lsn), and store this data into the next Queue.
        :param q_api_cob: A python Queue object that being used between 
        the Application and the Causal Order Broadcast.
        :param q_cob_rb: A python Queue object that being used between 
        the Causal Order Broadcast and the Reliable Broadcast.
        :param V: The vector clock.
        :param mutex: A mutex to be used in the vector clock critical area.
        :param host_key: The host key to know who is this process in another.
        """
        lsn = 0
        while True:
            data = q_api_cob.get()
            m = data[0]
            t = data[1]
            mutex.acquire()
            W = V
            mutex.release()
            W[host_key] = lsn
            lsn += 1
            q_cob_rb.put([host_key, W, m, t])
    
    def deliver(self, q_rb_cob, q_cob_api, V, mutex):
        """
        Tries to get a data from the Queue to apply the Causal Order Broadcast
        Deliver logic which means test if the current vector clock (V) is bigger or equal (<=)
        of the received vector clock (W). If true, updates the current vector clock (V) and
        deliver the actual data to the next Queue.
        :param q_rb_cob: A python Queue object that being used between the Reliable Broadcast
        and the Causal Order Broadcast.
        :param q_cob_api: A python Queue object that being used between the Causal Order Broadcast
        and the Application.
        :param V: The vector clock.
        :param mutex: A mutex to be used in the vector clock critial area.
        """
        while True:
            data = q_rb_cob.get()  # [host_key, W, m, t]
            p_key = data[0]
            W = data[1]
            mutex.acquire()
            if W <= V:
                V[p_key] += 1
                mutex.release()
                q_cob_api.put(data)
            else:
                q_rb_cob.put(data)