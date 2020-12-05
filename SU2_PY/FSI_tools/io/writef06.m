clear variables;
close all;
clc;


path = 'D:\Desktop\pysu2\';
filename_modal = [path, 'StructHistoryModal.dat'];
filename_pch = 'modal.pch';

[ID,GridType,U,Ux,Uy,Uz,K,M,Uxr,Uyr,Uzr,Usp] = readPunchShapes(filename_pch,path);

[node_list,ia,ic] = unique(ID(:,1));
GridType_list = GridType(ia);
npoint = length(node_list);

i_G = unique(ID(GridType == 'G',1));
i_S = ID(GridType == 'S',1);

h = 10;
nmodes = size(U,2);
for n = 1:nmodes
    [t,q,qdot,qddot] = readHistoryModal(filename_modal,nmodes,n,false);
    jj = 1:h:length(t);
    q_mat(n,:) = q(jj)';
    %qdot_mat(n,:) = qdot(jj)';
    %qddot_mat(n,:) = qddot(jj)';
end

t = t(jj);

ux = Ux*q_mat;
uy = Uy*q_mat;
uz = Uz*q_mat;
% vx = Ux*qdot_mat;
% vy = Uy*qdot_mat;
% vz = Uz*qdot_mat;
% ax = Ux*qddot_mat;
% ay = Uy*qddot_mat;
% az = Uz*qddot_mat;
uxr = Uxr*q_mat;
uyr = Uyr*q_mat;
uzr = Uzr*q_mat;
usp = Usp*q_mat;

filename = 'wing3D.f06';
fido = fopen(filename,'w');
fprintf(fido,'1\n');
fprintf(fido,'\n'); 

for i = 1:npoint
    
    id = node_list(i);
    indexS = find(i_S==id,1);
    indexG = find(i_G==id,1);

    fprintf(fido,'1                                                       **STUDENT EDITION*      MAY  30, 2018  MSC Nastran  7/13/17   PAGE    1\n');
    fprintf(fido,'\n');
    fprintf(fido,'0\n');
    fprintf(fido,'      POINT-ID = %9d\n', id);
    fprintf(fido,'                                             D I S P L A C E M E N T   V E C T O R\n');
    fprintf(fido,'\n'); 
    fprintf(fido,'       TIME       TYPE          T1             T2             T3             R1             R2             R3\n');

    for j = 1:length(t)
        
        if indexG
            fprintf(fido,'%15.6e     G   %15.6e%15.6e%15.6e%15.6e%15.6e%15.6e\n',...
                t(j), ux(indexG,j), uy(indexG,j), uz(indexG,j), uxr(indexG,j), uyr(indexG,j), uzr(indexG,j));
        elseif indexS
            fprintf(fido,'%15.6e     S   %15.6e\n',...
                t(j), usp(indexS,j));
        end

    end

end

%fprintf(fido,'                                            A C C E L E R A T I O N    V E C T O R\n');


fclose(fido);