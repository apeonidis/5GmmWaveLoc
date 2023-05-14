# Chat GPT answer to what is DCS_SOMP
# DC_SOMP stands for "Distributed Coordinated Scheduling with Separate Optimization of Macro and Millimeter Wave". In the context of 5G mmWave, this refers to a scheduling method for allocating radio resources between macro and millimeter wave (mmWave) cells in a 5G network. The goal of this scheduling method is to efficiently coordinate the resource allocation between the different cell types in order to improve the overall network performance.
# mmWave technology is an important part of 5G, as it enables much higher data rates compared to traditional sub-6GHz bands. However, the propagation characteristics of mmWave signals are different than those of sub-6GHz signals, which makes it challenging to effectively utilize mmWave resources in a cellular network. DC_SOMP is one approach to addressing these challenges and optimizing the use of both macro and mmWave resources in a 5G network.


import string
import numpy as np
import numpy.random
import os
from DCS_SOMP import modified_DCS_SOMP

from util import norm_2, print_debug
from classical_beamforming import get_response_vector

# predefined parameters
L = 4        #number of paths (including both LOS and NLOS)
               #this also control how many scatters we have
N=10         # number of subcarriers 
Nt=32        # number of TX antennas
Nr=Nt        # number of RX antennas
Nb=Nt*2      # number of beams in dictionary
G = 10       # number of beams sent
c = 299.792458      # speed of light in meter/us
Rs=10       # total BW in MHz
Ts=1/Rs      # sampling period in us
alpha = 0.2  # UE orientation
sigma=0#0.1    # noise standard deviation

def fiveG_positioning_experiement(posRx: np.ndarray, d: np.double, lambda_n: np.double, iteration_name: string):
  print("  Starting experiment {}".format(iteration_name))
  # computed parameters
  TOA = np.ndarray(shape=[L], dtype=np.double)
  AOD = np.ndarray(shape=[L], dtype=np.double)
  AOA = np.ndarray(shape=[L], dtype=np.double)
  #SP = np.random.rand(L-1,2) * 5
  # SP = np.random.rand(L-1,2) * 20 - 10  # random positions for L-1 scatters uniformly placed in a 20 m x 20 m area 
  SP = np.array([[8.1716, -6.3877],[0.9172, -8.3818],[-0.6265, 7.5314]]) # for debugging and controlling the randomness
  # first index [0] is parameters for LOS path
    # be careful, numpy by default uses Frobenius norm while matlab uses 2-norm, need to explicitly specify 2-norm in python
    # see https://stackoverflow.com/questions/26680412/getting-different-answers-with-matlab-and-python-norm-functions
  TOA[0] = norm_2(posRx) / c  
  AOD[0] = np.arctan2(posRx[1], posRx[0])
  AOA[0] = np.arctan2(posRx[1], posRx[0])-np.pi-alpha

  # other indices except [0] are parameters for NLOS paths
  for i in range(1,L):
      i_s = i - 1 # index for SP, since len(SP) = len(TOA) - 1
      AOD[i] = np.arctan2(SP[i_s,1], SP[i_s,0])
      AOA[i] = np.arctan2(SP[i_s,1] - posRx[1], SP[i_s,0] - posRx[0]) - alpha
      TOA[i] = (norm_2(SP[i_s,:]) + norm_2(np.tile(np.expand_dims(posRx, 1), 1) - SP[i_s,:]) ) / c # simulating matlab where posRx is a column vector and is subtracted by the row vector SP[i_s,:]
     
  # there is two way to create 1-d array, first one is [1, L], second way is [L]
  # in fact, the first way typically is a 2d array with only one row
  h = 10 * np.ones([L])

  # create dictionary 
  Ut: np.ndarray = np.zeros([Nt, Nb], dtype="complex_")
  Ur: np.ndarray = np.zeros([Nr, Nb], dtype="complex_")
  # have to put int(), but Nb is always Nt * 2, so it's fine
  # also, range() is [), but matlab : is [], so Nb/2 - 1 is changed to Nb/2
  aa_old = np.arange(int(-Nb / 2), int(Nb / 2)) 
  aa = 2 * aa_old / Nb

  for m in range(0, Nb):
    Ut[:, m] = get_response_vector(Nt, np.arcsin(aa[m]), d, lambda_n) * np.sqrt(Nt)
    Ur[:, m] = get_response_vector(Nr, np.arcsin(aa[m]), d, lambda_n) * np.sqrt(Nr)

  # Generate channel H, eq. (1)-(5) from the paper 
  H = np.zeros([Nr, Nt, N], dtype="complex_")
  for n in range(0, N):
    for l in range(0, L):
      t1 = h[l] * np.exp(-1j * 2 * np.pi * TOA[l] * n / (N * Ts)) 
      t2 = np.sqrt(Nr) * get_response_vector(Nr, AOA[l], d, lambda_n)
      t3 = np.sqrt(Nt) * get_response_vector(Nt, AOD[l], d, lambda_n)
      H[:, :, n] += t1 * np.outer(t2, numpy.conjugate(t3))

  # generate observation and beamformers
  DIR_PATH = os.path.dirname(os.path.abspath(__file__))
  y =  np.zeros([Nr, G, N], dtype="complex_")
  F = np.zeros([Nt, G, N], dtype="complex_")
 
  # Deterministic values for y and F (the same as from Matlab)
  for n in range(0, N):
    yFilename = os.path.join(DIR_PATH, 'debug_export_data/exported_y_{}.csv'.format(n+1))
    y[:,:, n] = np.genfromtxt(yFilename, delimiter=",", dtype='complex_');

    FFilename = os.path.join(DIR_PATH, 'debug_export_data/exported_F_{}.csv'.format(n+1))
    F[:,:, n]  = np.genfromtxt(FFilename, delimiter=",", dtype='complex_');
   
  # Non deterministic - values, not used due to debuging purposes. 
  # for g in range(0, G):
  #   for n in range(0, N):
  #     F[:, g, n] = np.exp(1j * np.random.rand(Nt, 1)[:,0] * 2 * np.pi) # random bean former
  #     # F[:, g, n] = np.sqrt(Nt) * get_response_vector(Nt, np.sin(-AOD[0]))
  #     # in python, A * B is not a matrix multiplication, is elementery-wise multiplication, 
  #     # to do the real matrix multiplication, use .dot() method https://stackoverflow.com/questions/21562986/numpy-matrix-vector-multiplication
  #     y[:, g, n] = H[:, :, n].dot(F[:, g, n]) + sigma / np.sqrt(2) * (np.random.randn(Nr, 1)[:,0] + 1j * np.random.randn(Nr, 1)[:,0]) # the randomness here should not be controlled as it is part of the algorithm

  # print_debug("F = {}, y = {}".format(F, y))

  yb = np.zeros([Nr * G, N], dtype="complex_")
  omega = np.zeros([Nr * G, Nb * Nb, N], dtype="complex_")
  for n in range(0, N):
    yb[:, n] = np.reshape(y[:, :, n], [Nr * G, 1], order='F')[:,0]
    # WARNING: correctness of Omega is unchecked as it is too big to inspect in matlab
    omega[:, :, n] = np.kron((Ut.conjugate().transpose().dot(F[:, :, n])).transpose(), Ur)

  # run the DCS-SOMP
  indices, h_hat = modified_DCS_SOMP(yb, omega, L)  ## Neglegable error in indices with respect to Matlab

  # estimation or Rx position
  distances = np.zeros([L])
  for l in range(0, L):
    distances[l] = -np.mean(np.diff(np.unwrap(np.angle(h_hat[l, :])))) * (N * Ts) * c / (2 * np.pi)
    distances[l] = distances[l] + N * Ts * c if (distances[l] < 0) else distances[l]

  min_i = np.argmin(distances)

  index1 = np.zeros([L], dtype=int)
  index2 = np.zeros([L], dtype=int)
  AOD_hat = np.zeros([L])
  AOA_hat = np.zeros([L])
  for l in range(0, L):
    index1[l] = np.floor(indices[l]/Nb)
    index2[l] = indices[l] - (index1[l]) * Nb
    AOD_hat[l] = np.arcsin(aa[index1[l]])
    AOA_hat[l] = (np.pi * np.sign(np.arcsin(aa[index2[l]])) 
      - np.arcsin(aa[index2[l]])
    )

  # final estimated results
  posRx_hat = distances[min_i] * np.array([np.cos(AOD_hat[min_i]), np.sin(AOD_hat[min_i])]).transpose()
  alpha_hat = np.mod(AOD_hat[min_i] - AOA_hat[min_i] - np.pi, np.pi)

  print("  posRx_hat = {}, alpha_hat = {}".format(posRx_hat, alpha_hat))
  error_of_posRx_estimation = norm_2(posRx_hat - posRx)
  error_of_alpha_estimation = np.abs(alpha_hat - alpha) # can not find the MATLAB norm() equilavent method for scalar in python, then simply to a substraction

  print("  localization error = {}m".format(error_of_posRx_estimation))
  print("  oritenation error = {} rad".format(error_of_alpha_estimation))

  return error_of_posRx_estimation, error_of_alpha_estimation

fiveG_positioning_experiement(posRx=np.array([5,1]), d=1, lambda_n=2, iteration_name="main_iteration")