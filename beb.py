class BestEfforBroadcast():
    def broadcast(self, q_rb_beb, q_beb_pp, users, host_key):
        """
        Best Effort Broadcast primitive, broadcasts a message m (data)
        to all process (users) appending the user ip at the end of the array.
        :param q_rb_beb: A python Queue object that being used between 
        the Reliable Broadcast and the Best Effort Broadcast.
        :param q_beb_pp: A python Queue object that being used between 
        the Best Effort Broadcast and the Perfect Point to Point Links.
        :param users: A python dictionary with the group of users.
        :param host_key: The host key to get the host ip from the users dictionary.
        """
        while True:
            data = q_rb_beb.get()
            # send N vezes para os usuarios
            for u in users:
                if u != host_key:
                    q_beb_pp.put(data + [users[u]]) # [host_key, W, m, t, ip]
    
    def deliver(self, q_pp_beb, q_beb_rb):
        """
        Delivers a message m (data) broadcast by process p.
        :param q_pp_beb: A python Queue object that being used between 
        the Perfect Point to Point Links and the Best Effort Broadcast.
        :param q_beb_rb: A python Queue object that being used between 
        the Best Effort Broadcast and the Reliable Broadcast.
        """
        while True:
            data = q_pp_beb.get()
            q_beb_rb.put(data)