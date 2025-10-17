This is the backward facing step tutorial from OpenFOAM. 
As mentioned in the original README, the case is based on 
    
    D.M. Driver and H.L. Seegmiller. Features of a reattaching turbulent shear
    layer in divergent channel flow. AIAA Journal, 23(2):163–171, 1985.

My goal here is to try out the different turbulence models and play
around with the different parameters to see if I can get as close
experimental agreement with data provided at 

    https://turbmodels.larc.nasa.gov/backstep_val.html

I also want to explore turbulence model optimization techniques, and see if its
possible to apply the method of manufactured solutions either to this case
or the source code.

The point of this is to learn about optimization and correlation improvement.