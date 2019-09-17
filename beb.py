class BestEfforBroadcast():
    def broadcast(self, q_rb_beb, q_beb_pp, users, host_key):
        while True:
            data = q_rb_beb.get()
            # send N vezes para os usuarios
            for u in users:
                if u != host_key:
                    local_data = data
                    local_data.append(users[u]) # [host_key, W, m, t, ip]
                    q_beb_pp.put(local_data)
    
    def deliver(self, q_pp_beb, q_beb_rb):
        while True:
            data = q_pp_beb.get()
            q_beb_rb.put(data)