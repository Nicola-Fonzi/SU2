clear variables;
close all;
clc;


filename = 'D:\Desktop\wing3D\StructHistoryNodal.dat';
fid = fopen(filename);

data = textscan(fid,'%f%d%f%f%f%f%f%f','HeaderLines',1);

fclose(fid);

npoint = 63;


while true
    
    ID = str2double(input('ID: ','s'));

    index = data{2}==ID;
    if ~any(index)
        error('ID not found');
    end

    t = data{1}(index);
    ux = data{3}(index);
    uy = data{4}(index);
    uz = data{5}(index);
    vx = data{6}(index);
    vy = data{7}(index);
    vz = data{8}(index);

    figure();
    hold on;
    subplot(3,1,1);
    plot(t,ux);
    xlabel('t');
    ylabel('ux');
    title(['ID = ', num2str(ID), ': Displacement']);
    subplot(3,1,2);
    plot(t,uy);
    xlabel('t');
    ylabel('uy');
    subplot(3,1,3);
    plot(t,uz);
    xlabel('t');
    ylabel('uz');
    
    figure();
    hold on;
    subplot(3,1,1);
    plot(t,vx);
    xlabel('t');
    ylabel('vx');
    title(['ID = ', num2str(ID), ': Velocity']);
    subplot(3,1,2);
    plot(t,vy);
    xlabel('t');
    ylabel('vy');
    subplot(3,1,3);
    plot(t,uz);
    xlabel('t');
    ylabel('vz');

end