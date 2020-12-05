function [] = writePunch(filename,workingDir,K,U,GridType,ID)

% Modifiche del 11/07/2020
% - uso GridType_list, che equivale al vecchio GridType
% - aggiungo ID come argomento della function (temo che prima scrivessimo
%   gli ID dei GRID sbagliati)
% - aggiungo la stampa delle rotazioni


home = pwd;
cd(workingDir)

fid = fopen(filename,'w');

%npoints = length(GridType);
[node_list,ia,~] = unique(ID(:,1));
GridType_list = GridType(ia);
npoints = length(node_list);
nmodes = size(U,2);

l = 1;

for j = 1:nmodes
    fprintf(fid,'$EIGENVALUE =  %9.7E  MODE = %5d%38d\n',K(j,j),j,l);
    l = l+1;
    index = 1;
    for i = 1:npoints
        id = node_list(i);
        if GridType_list(i) == 'G' 
            fprintf(fid,'%10d       G     %13.6E     %13.6E     %13.6E%8d\n',id,...
                U(index,j),U(index+1,j),U(index+2,j),l);
            l = l+1;
            fprintf(fid,'-CONT-                 %13.6E     %13.6E     %13.6E%8d\n',...
                U(index+3,j),U(index+4,j),U(index+5,j),l);
        else
            fprintf(fid,'%10d       S     %13.6E     %13.6E     %13.6E%8d\n',id,...
                U(index,j),0,0,l);
            l = l+1;
            fprintf(fid,'-CONT-                 %13.6E     %13.6E     %13.6E%8d\n',...
                0,0,0,l);
        end
        l = l+1;
        if GridType_list(i) == 'G'
            index = index+6;
        else
            index = index+1;
        end
    end
end

fclose(fid);

cd(home)

end