import numpy as np

#[1]

#1
M = np.arange(2,27)
print(M)
print("\n")

#2
M = M.reshape(5,5)
print(M)
print("\n")

#3
M[1:4,1:4] = 0
print(M)
print("\n")

#4
M = M@M
print(M)
print("\n")

#5
tmp = M*M
dab = 0
for i in tmp[0]:
    dab += i
print(np.sqrt(dab))
print("\n")
