% This function computes the required Re for a given Ma and U set

clear all;close all;clc

imposeRho = 0;

if imposeRho==1
    Ma = 0.82;
    U = [30 60 90 120 140 150];
    
    L = 0.2;
    
    c = U/Ma;
    
    T = c.^2/1.4/287;
    
    mu = (1.458e-6*T.^1.5)./(T+110.4);
    
    Re = 1.225*U*L./mu;
else
    Ma = [0.65 0.75 0.82 0.9];
    gamma = 1.4;
    R = 287;
    Ttot = 305;
    Ptot = 101325;
    L = 0.2;
    
    T = Ttot./( 1+ ((gamma-1)/2).*Ma.^2 )
    c = sqrt(gamma*R*T);
    U = c.*Ma
    P = Ptot./( 1+ ((gamma-1)./2).*Ma.^2 ).^(gamma/(gamma-1))
    rho = P./R./T;
    
    mu = (1.458e-6*T.^1.5)./(T+110.4);
    
    Re = rho.*U.*L./mu
end