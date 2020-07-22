clear variables;
close all;
clc;


filename = 'StructHistoryModal.dat';
fid = fopen(filename);

nmodes = 10;

formatSpec = '%f';
for i = 1:nmodes
    formatSpec = [formatSpec, '%f%f%f'];    
end
data = textscan(fid,formatSpec,'HeaderLines',1);
data = cell2mat(data);

fclose(fid);

t = data(:,1);

while true
    
    n = str2double(input('n: ','s'));
    if n > 10
        error(['Mode not found. NMODES = ',num2str(nmodes)]);
    end
    
    i = 1+(n-1)*3;
    q = data(:,i+1);
    qdot = data(:,i+2);
    qddot = data(:,i+3);

    figure();
    hold on;
    subplot(3,1,1);
    plot(t,q);
    xlabel('t');
    ylabel('$q$','interpreter','latex','FontSize',14);
    title(['Mode n. ', num2str(n)]);
    subplot(3,1,2);
    plot(t,qdot);
    xlabel('t');
    ylabel('$\dot{q}$','interpreter','latex','FontSize',14);
    subplot(3,1,3);
    plot(t,qddot);
    xlabel('t');
    ylabel('$\ddot{q}$','interpreter','latex','FontSize',14);

end