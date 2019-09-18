from HMM import Model
from pre import Prep
import re

train_data = "data/train.txt"
test_data = "data/test.txt"
syllables_path = "data/syllables.txt"
S = [0,1,2] #0:B, 1: I, 2: O
pro = Prep(train_data, S)
proT = Prep(test_data, S)
test = proT.getData()
X = pro.getData()

hidden_states, word_count = pro.wordCount(X, syllables_path)
observation = word_count.keys()
X_train = pro.str2words(X)
observations_test = pro.str2words(test)
_, test_wordcount = pro.wordCount(test, syllables_path)

# fix cứng 
# A[state_from=O][state_to=B] =1, A[state_from=O][state_to=I|O] = 0
# B[observation = O] thì B[state=O]=1, B[state=B|I]=0
# phi(I) = 0

B = pro.BIOconf(X_train, word_count, test_wordcount, hidden_states)
phi = [0.9, 0, 0.1]
A = [[0.45, 0.35, 0.2], [0.6, 0.2, 0.2], [0.7, 0, 0.3]] 
o_hiddenstate = []
model = Model(S, observation, phi, A, B)

phi, A, B = model.learningPhase(X_train, 3, A, B)
for obser in observations_test:
    length = len(obser)
    i, sub_obser, state = 0, [], []
    while i < length:
        sub_obser.append(obser[i])
        if obser[i] == '.' or obser[i] == ',' or (i == length - 1):
            sub_state = model.decode(sub_obser, word_count)
            sub_obser = []
            state += sub_state
        i += 1
    o_hiddenstate.append(state)

word_sequence = pro.word_sequence(observations_test, o_hiddenstate)
print(word_sequence)
    
