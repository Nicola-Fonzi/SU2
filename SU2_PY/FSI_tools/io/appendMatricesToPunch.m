function [] = appendMatricesToPunch(filename,workingDir,K,M)

home = pwd;
cd(workingDir)

fid = fopen(filename,'a');
writeMatrixElements(fid,K,'NDK');   % NON-DIAGONAL STIFFNESS MATRIX
writeMatrixElements(fid,M,'NDM');   % NON-DIAGONAL MASS MATRIX
%writeMatrixElements(fid,C,'NDC');   % NON-DIAGONAL DAMPING MATRIX -- %TODO???
fclose(fid);

cd(home)

function writeMatrixElements(fid,A,keyword)
    fprintf(fid,'%s\n',keyword);
    n = size(A,1);
    for i = 1:n
        j = 1;
        fprintf(fid,'%-8d',i);
        while j <= n
            k = 1;
            while k <= 5 && j <= n
                fprintf(fid,'%14.6E',A(i,j));
                k = k+1;
                j = j+1;
            end
            fprintf(fid,'\n');
            if j <= n
                fprintf(fid,'%-8s','-CONT-');
            end
        end
    end
end

end