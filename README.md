
# Seidel software for FRET-nanoscopy analysis  
## functionality  
1) reading photon streams from picoquant .ptu files and transforming them into xy-lifetime images
2) Bayesian framework to optimally determine the number and location of emitters in an image snapshot
3) Forming individual emitters into FRET pairs and calculating FRET parameters   
4) Bayesian framework for fitting 1D histograms with non-centered Chi and Gaussian distributions.
5) Molecular assembly particle averaging based on coarse alignment and Prokrustes analysis

## template notebook & data
For a step-by-step instruction on how to use the code, refer to this notebook.  
FRET-nanoscopy datasets are several Gigabytes, please contact voort@hhu.de for an example dataset.

## Developer's notice
To make this tools usable for non-programmers, functionalities 4) and 5) will receive a dedicated GUI. Other sections will be re-written to make use of libraries that were unavailable at the time of initial writing.
Developer's contact: voort@hhu.de
