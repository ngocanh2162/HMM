import math

class Model(object):
    def __init__(self,states,observation,phi, A, B):
        self.states = states # B,I,O
        self.observation = observation
        self.phi = phi
        self.A = A
        self.B = B

    def forward(self, observations):
        o_len = len(observations)
        alpha = [[] for i in range(o_len)]
        alpha[0] = {}
        for i in range(len(self.states)):
            alpha[0][i] = self.B[i][observations[0]]*self.phi[i]
        for i in range(1, o_len):
            alpha[i] = {} 
            for state_to in range(len(self.states)):
                prob = 0
                for state_from in range(len(self.states)):
                    prob += alpha[i-1][state_from]*self.A[state_from][state_to]
                alpha[i][state_to]=self.B[state_to][observations[i]]*prob
        return alpha

    def backward(self, observations):
        o_len = len(observations)
        beta = [[] for i in range(o_len)]
        beta[o_len-1] = {}
        for i in range(len(self.states)):
            beta[o_len-1][i] = 1
        i = o_len - 1
        while i > 0:
            beta[i-1] = {}
            for state_from in range(len(self.states)):
                prob = 0
                for state_to in range(len(self.states)):
                    prob += self.A[state_from][state_to] * self.B[state_to][observations[i]]*beta[i][state_to]
                beta[i-1][state_from] = prob
            i += -1
        return beta
 
    def cal_gamma(self, observations, alpha, beta):
        T = len(observations)
        gamma = [[] for i in range(T)]
        for t in range(T):
            gamma[t] = {}
            sum_prob = 0
            for state in range(len(self.states)):
                prob = alpha[t][state]*beta[t][state]
                gamma[t][state] = prob
                sum_prob += prob
            for state in range(len(self.states)):
                if gamma[t][state] == 0:
                    continue
                else:
                    gamma[t][state] /= sum_prob
        return gamma
            
    def cal_epsi(self, observations, alpha, beta, A, B):
        T = len(observations)
        epsi = [[] for i in range(T-1)]
        for t in range(T-1):
            epsi[t] = {}
            sum_prob = 0
            for i in range(len(self.states)):
                epsi[t][i] = {}
                for j in range(len(self.states)):
                    prob = alpha[t][i]*A[i, j]*B[j][observations[t+1]]*beta[t+1][j]
                    epsi[t][i][j] = prob
                    sum_prob += prob
            for i in range(len(self.states)):
                for j in range(len(self.states)):
                    if epsi[t][i][j] == 0:
                        continue
                    else:
                        epsi[t][i][j] /= sum_prob
        return epsi

    def cal_PMI(self, observations, word_count, i, j):
        o_len = len(observations)
        sum = 0
        for k in range(len(word_count)):
            sum += word_count[k]
        temp1 = word_count(observations[i])
        temp2 = word_count(observations[j])
        temp3 = 0
        for k in range(o_len):
            if observations[k] == observations[i] and observations[k+1] == observations[j]:
                temp3 += 1
        p1 = float(temp1 + 1)/float(sum - temp1 + o_len)
        p2 = float(temp3 + 1)/float(temp2 + o_len)
        return math.log(p2/p1)


    def cal_w(self, observations, word_count, t):
        if t == 0 or t == 1:
            return 1 
        else:
            W = self.cal_PMI(observations, word_count, t-1, t)
            return W

    def estimate(self, gamma, epsi, observations):
        T = len(observations)
        phi = gamma[0]
        A, B = {},{}
        for state in range(len(self.states)):
            A[state] = {}
            B[state] = {}
        for i in range(len(self.states)):
            for j in range(len(self.states)):
                gamma_t, epsi_t = 0, 0
                for t in range(T-1):
                    epsi_t += epsi[t][i][j]
                    gamma_t += gamma[t][i]
                A[i][j] = epsi_t/gamma_t
        for i in self.states:
            for j in observations:
                gamma_t, gamma_tt = 0
                for t in range(T):
                    if observations[t] == j:
                        gamma_tt += gamma[t][i]
                    gamma_t = gamma[t][i]
                B[i][j] = gamma_tt/gamma_t
        return (phi, A, B)

    def viterbi(self, observations, word_count):
        o_len = len(observations)
        mu = [[] for i in range(o_len)]
        mu[0] = {}
        for i in range(len(self.states)):
            mu[0][i] = self.B[i][observations[0]]*self.phi[i]
        for i in range(1, o_len):
            mu[i] = {}
            for state_to in range(len(self.states)):
                temp_max = 0 #???
                for state_from in range(len(self.states)):
                    temp = mu[i-1][state_from]*self.A[state_from][state_to]*self.B[state_to,observations[i]]*self.cal_w(observations, word_count, state_to)
                    if temp > temp_max:
                        temp_max = temp
                mu[i][state_to] = temp_max
        return mu  

    def decode(self, observations, word_count):
        o_len = len(observations)
        mu = self.viterbi(observations, word_count)
        sequence = mu[o_len-1]
        state = sorted(sequence, key = sequence.get, reversed = True)[0]
        theta = [0 for i in range(o_len)]
        i = o_len - 1
        theta[i] = state
        while i>0:
            prob = {}
            for state_from in range(len(self.states)):
                prob[state_from] = mu[i-1][state_from]*self.A[state_from][state]
            state = sorted(prob, key = prob.get, reversed = True)[0]
            i -= 1
            theta[i] = state
        return theta

    # def commonInit(self):
    #     phi, A, B = {}, {}, {}
    #     N = len(self.states)
    #     M = len(self.observation)
    #     for i in self.states:
    #         phi[i] = 1.0/N
    #         A[i], B[i] = {}, {}
    #         for j in self.states:
    #             A[i][j] = 1.0/N
    #         for j in self.observation:
    #             B[i][j] = 1.0/N
    #     phi = self.phi
    #     A = self.A
    #     B = self.B
    #     return (phi, A, B)

    def learningPhase(self, observations, iter_num, A, B):
        for i in range(iter_num):
            alpha = self.forward(observations)
            beta = self.backward(observations)
            gamma = self.cal_gamma(observations, alpha, beta)
            epsi = self.cal_epsi(observations, alpha, beta, A, B)
            phi, A, B = self.estimate(gamma, epsi, observations)
        phi = self.phi
        A = self.A
        B = self.B   


#####
    def BIOestimate(self, gamma, epsi, observations):
        T = len(observations)
        phi = gamma[0]
        phi[1] = 0
        A, B = {}, {}
        for state in self.states:
            A[state] = {}
            B[state] = {}
        for i in range(3): #chỉ update A[state_from = B|I]
            for j in self.states:
                gamma_t, epsi_t = 0, 0
                for t in range(T-1):
                    epsi_t += epsi[t][i][j]
                    gamma_t += gamma[t][i]
                A[i][j] = epsi_t/gamma_t
        for i in self.states: # update trừ B[observation = O]
            for j in observations:
                gamma_t, gamma_tt = 0
                for t in range(T):
                    if observations[t] == j:
                        gamma_tt += gamma[t][i]
                    gamma_t = gamma[t][i]
                B[i][j] = gamma_tt/gamma_t #
        return (phi, A, B)
    
    def BIOcal_gamma(self, observations, alpha, beta):
        T = len(observations)
        gamma = [[] for i in range(T)]
        for t in range(T):
            gamma[t] = {}
            sum_prob = 0
            for state in self.states:
                prob = alpha[t][state]*beta[t][state]
                gamma[t][state] = prob
                sum_prob += prob
            for state in self.states:
                if gamma[t][state] == 0:
                    continue
                else:
                    gamma[t][state] /= sum_prob
            gamma[t][1] = 0
        return gamma
    
    def BIOlearningPhase(self, observations):
        phi, A, B = self.BIOinit()
        for i in range(self.iter_num):
            alpha = self.forward(observations)
            beta = self.backward(observations)
            gamma = self.BIOcal_gamma(observations, alpha, beta)
            epsi = self.cal_epsi(observations, alpha, beta, A, B)
            phi, A, B = self.BIOestimate(gamma, epsi, observations)
        phi = self.phi
        A = self.A
        B = self.B 