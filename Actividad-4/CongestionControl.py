class CongestionControl():
    def __init__(self, MSS: int):
        
        self.current_state = "slow_start"
        self.MSS = MSS
        self.cwnd = 1*MSS
        self.ssthresh = None

    def get_cwnd(self):
        return int(self.cwnd)
    
    def get_MSS_in_cwnd(self):
        if (self.cwnd % self.MSS) != 0:
            return int((self.cwnd // self.MSS) + 1)
        
        return int(self.cwnd // self.MSS)
    
    def event_ack_received(self):
        if self.current_state == "slow_start":
            self.cwnd += self.MSS
            if self.ssthresh is not None and self.cwnd >= self.ssthresh:
                self.current_state = "congestion_avoidance"
        elif self.current_state == "congestion_avoidance":
            self.cwnd += (self.MSS // self.get_MSS_in_cwnd())


    def event_timeout(self):
        self.ssthresh = self.cwnd // 2
        self.cwnd = self.MSS
        self.current_state = "slow_start"

    def is_state_slow_start(self):
        return self.current_state == "slow_start"
    
    def is_state_congestion_avoidance(self):
        return self.current_state == "congestion_avoidance"
    
    def get_ssthresh(self):
        return self.ssthresh