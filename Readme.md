# 5G-mm-wave simulations comparison and debuging. 

## Introduction
The purpose of this repository is to debug the code present in [catproof/Localization-For-5G-MIMO-Using-Beam-Steering-and-Channel-Estimation](https://github.com/catproof/Localization-For-5G-MIMO-Using-Beam-Steering-and-Channel-Estimation). As it is a python translation of [henkwymeersch/5GPositioning](https://github.com/henkwymeersch/5GPositioning), both repositories are copied here and modified for debug purposes. 

## Method 
To enable a reliable comparison between the two scripts, it is essential to eliminate any non-deterministic behavior. First, the `sigma` parameters in both scripts are set to zero, ensuring the absence of randomly generated noise. Additionally, predetermined values are assigned to the positions of scatter points, ensuring consistency across executions.

Another source of non-determinism arises from the population of the three-dimensional arrays `y` and `F`. To achieve deterministic behavior, the values of `y` and `F` are exported from the Matlab code, and the exported values are utilized in both Matlab and Python during subsequent executions. As direct import/export of three-dimensional structures is not supported by Matlab or Python's Numpy library, multiple export files are created, each containing two-dimensional structures. It is important to note that a minor modification is required before using the export files in Python due to the difference in the notation for the imaginary unit. In Matlab, the imaginary unit is denoted by `i`, while Python uses `j`.

In Matlab one time export is done 

```matlab
for i=1:N
    writematrix(y(:,:,i), sprintf('y_%d.csv', i));
    writematrix(F(:,:,i), sprintf('F_%d.csv', i));
end
```

Then the corresponding Matlab and Python imports are done 

```matlab
for i=1:N
    y(:,:,i) = readmatrix(sprintf('y_%d.csv', i));
    F(:,:,i) = readmatrix(sprintf('F_%d.csv', i));
end
```

```python
for n in range(0, N):
    yFilename = os.path.join(DIR_PATH,'y_{}.csv'.format(n+1))
    y[:,:, n] = np.genfromtxt(yFilename, delimiter=",", dtype='complex_');

    FFilename = os.path.join(DIR_PATH,'F_{}.csv'.format(n+1))
    F[:,:, n]  = np.genfromtxt(FFilename,delimiter=",", dtype='complex_');
```


After eliminating all non-deterministic behavior, the scripts are executed, and each line is compared by examining corresponding variables. If any discrepancies are found, the corresponding line is debugged. This process is continued until the end of both scripts. Due to the large number of elements in certain structures, such as `Omega` with over 13 million entries, a selection of random positions is made to compare elements reliably. It is important to note that the indexing of structures differs between Python and Matlab. For instance, `Omega[1,2,3]` in Matlab corresponds to `Omega[0,1,2]` in Python.

By following this approach, the following discrepancies are identified and corrected: 
In Matlab, the `'` operator is used in the initialization of `H` and `Omega`. The operator results in a complex conjugate transpose of a matrix. However, in the corresponding lines of the Python script, a normal transpose is used (equivalent to Matlab's "`.'`" operator). The necessary corrections are
```python
H[:, :, n] += t1 * np.outer(t2, np.conjugate(t3))
...
omega[:, :, n] = np.kron((Ut.conjugate().transpose().dot(F[:, :, n])).transpose(), Ur) 
```

To initialize `yb`, the `reshape` function is utilized. It is important to note that Matlab follows a Fortran-like index order, while Python's Numpy library follows a C-like index order. In order to align with Matlab's behavior, the necessary correction are

```python
yb[:, n] = 
    np.reshape(y[:, :, n],...
        [Nr * G, 1], order='F')[:,0] 
```

Another discrepancy is identified in the `get_response_vector` function. In the Matlab implementation, a minus sign is employed. To rectify this inconsistency, the correction is applied in the Python script as demonstrated

```python
def get_response_vector(N,phi,d,lambda_n):
...
    response_vector = np.exp(-1j*antennas*2*math.pi*d*np.sin(phi)/lambda_n)/math.sqrt(N)
```

### Additional tools and organization 
All the export files for `F` and `y` are present correspondingly in `5GPositioning/debug_export_data` and `Localization-For-5G-MIMO-Using-Beam-Steering-and-Channel-Estimation/debug_export_data`.  A python script rewriting the complex number to `j` in the export files to be used in Python is present in `Localization-For-5G-MIMO-Using-Beam-Steering-and-Channel-Estimation/debug_export_data/convert_i2j.py`.


### Conclusion
The simulation present in [catproof/Localization-For-5G-MIMO-Using-Beam-Steering-and-Channel-Estimation](https://github.com/catproof/Localization-For-5G-MIMO-Using-Beam-Steering-and-Channel-Estimation) was successfully debugged, therefore can be more reliably used. 


#### Disclaimers
This repository does not claim any intelectual rights. The code provided here is only slightly modified version of the work present in  [catproof/Localization-For-5G-MIMO-Using-Beam-Steering-and-Channel-Estimation](https://github.com/catproof/Localization-For-5G-MIMO-Using-Beam-Steering-and-Channel-Estimation) and [henkwymeersch/5GPositioning](https://github.com/henkwymeersch/5GPositioning). 
The code provided in this repository comes with no warranty. 
No claims about the accuracy of the simulation are made.  
