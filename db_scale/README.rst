Simulate long-term observations
===============================
Bart Scheers, May 2013
----------------------------

This script simulates a series of measurements of a given number of  
base sources with the goal to monitor long-term query behaviour.     
                                                                  
In the main function, you may specify the following:                 
                                                                  
* nbasesources  := the number of base sources                          
* basearea      := the area in which the base sources (and measurements) fall                                  
* nimages       := the number of images in which all base source is (re)measured                                        
* kappa         := parameter to dexcribe the compactness of the Fisher distribution                                         
* freqs         := the frequencies of an image                         
                                                                  
This script generates a number of base sources within the specified  
area. nimages specifies for how many images we follow the base       
sources. For every base source a random postion is drawn from a      
Fisher distribution, characterised by its kappa parameter.           
                                                                  
Then the main function iterates over all the images and inserts and  
associates the sources in the database.                              
                                                                  
Accumulative query times are written to log files in the tkp code.   


Requires database.
