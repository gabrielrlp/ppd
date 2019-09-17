class CausalOrderBroadcast():
    def broadcast(self, q_api_cob, q_cob_rb, V, host_key):
        lsn = 0
        while True:
            data = q_api_cob.get()
            m = data[0] # msg
            t = data[1] # time
            W = V
            W[host_key] = lsn
            lsn += 1
            q_cob_rb.put([host_key, W, m, t])
    
    def deliver(self, q_rb_cob, q_cob_api, V, mutex):
        while True:
            data = q_rb_cob.get()  # [host_key, W, m, t, ip]
            p_key = data[0]
            W = data[1]
            if W[p_key] <= V[p_key]:
                mutex.acquire()
                V[p_key] += 1
                mutex.release()
                q_cob_api.put(data)
            else:
                q_rb_cob.put(data)