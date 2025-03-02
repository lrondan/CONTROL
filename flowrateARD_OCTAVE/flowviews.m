%  GNU-OCTAVE visualization for the flow project
%  by: Rojas Rondan
%
clc, clear;
% Load instrument control PKG
pkg load instrument-control;

% config serial port
port = 'COM7'; % Change this for ('COM5','COM7')
bd = 9600;  % baud rate from Arduino

% Open serial port
s = serial(port, bd);

% Start vector values
display_time = [];
value1 = [];
value2 = [];

% Start read config (in secounds)
duration = 100; % number of durations
start_time = time(); % Get start time

% Create a fig
figure;

% Principal loop for read and display
while time() - start_time < duration
    % Read a line completly
    line = '';
    while isempty(line) || line(end) != char(10) % 10 es el código ASCII para '\n'
        line = [line, char(srl_read(s, 1))];
    end

    % Quit first character
    line = strtrim(line); % clean lines

    % Divide the line in 2 values
    values = strsplit(line, ',');

    % Check
    if numel(values) == 2
        % Convert values in numbers
        flowrate = str2double(values{1});
        vol = str2double(values{2});

        % Save data
        new_time = time() - start_time;
        display_time = [display_time, new_time];
        value1 = [value1, flowrate];
        value2 = [value2, vol];

        % Display values
        disp(['Time: ', num2str(new_time), ' s, FlowRate: ', num2str(flowrate), ', Vol: ', num2str(vol)]);

        % Start graph in real time
        clf; % Clean graphs

        % Graf
        subplot(2, 1, 1); % 2 rows, 1 column, 1st graph
        plot(display_time, value1, 'r', 'LineWidth', 1.5);
        xlabel('Time (s)');
        ylabel('FlowRate (L/min)');
        title('FlowRate vs Time');
        grid on;

        % 2nd graph
        subplot(2, 1, 2); % 2 rows, 1 column, 2nd graph
        plot(display_time, value2, 'b', 'LineWidth', 1.5);
        xlabel('Time (s)');
        ylabel('Vol (L)');
        title('Vol vs Time');
        grid on;

        % Update the fig
        drawnow;
    else
        disp('Error: Something is wrong, two values ​​were not received');
    end

    pause(0.1); % pause
end

% Close serial port
fclose(s);
