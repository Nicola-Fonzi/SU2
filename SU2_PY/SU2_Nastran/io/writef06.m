clear variables;
close all;
clc;

filename = 'D:\Desktop\wing3D\StructHistoryNodal.dat';
fid = fopen(filename);
data = textscan(fid,'%f%d%f%f%f%f%f%f','HeaderLines',1);
fclose(fid);

npoint = 63;
IDs = data{2}(1:npoint);

filename = 'load_tip_disp.f06';
fido = fopen(filename,'w');
fprintf(fido,'1\n');
fprintf(fido,'\n'); 

for i = 1:npoint
    
    ID = IDs(i);
    index = data{2} == ID;
    
    t = data{1}(index);
    ux = data{3}(index);
    uy = data{4}(index);
    uz = data{5}(index);
    vx = data{6}(index);
    vy = data{7}(index);
    vz = data{8}(index);
    
    fprintf(fido,'1                                                       **STUDENT EDITION*      MAY  30, 2018  MSC Nastran  7/13/17   PAGE    1\n');
    fprintf(fido,'\n');
    fprintf(fido,'0\n');
    fprintf(fido,'      POINT-ID = %9d\n', ID);
    fprintf(fido,'                                             D I S P L A C E M E N T   V E C T O R\n');
    fprintf(fido,'\n'); 
    fprintf(fido,'       TIME       TYPE          T1             T2             T3             R1             R2             R3\n');

    for j = 1:10:length(t)

        fprintf(fido,'%15.6e     G   %15.6e%15.6e%15.6e%15.6e%15.6e%15.6e\n',...
            t(j), ux(j), uy(j), uz(j), 0., 0., 0.);

    end

end

%fprintf(fido,'                                            A C C E L E R A T I O N    V E C T O R\n');


fclose(fido);