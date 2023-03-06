% PARAMETERS (can change)
location            = 'StudyZone-D1F2';    % location used for figure name
start_freq          = 100e6;         % sweep start frequency
stop_freq           = 1750e6;       % sweep stop frequency
rtlsdr_id           = '0';          % RTL-SDR stick ID
rtlsdr_fs           = 2.8e6;        % RTL-SDR sampling rate in Hz
rtlsdr_gain         = 40;           % RTL-SDR tuner gain in dB
rtlsdr_frmlen       = 4096;         % RTL-SDR output data frame size
rtlsdr_datatype     = 'single';     % RTL-SDR output data type
rtlsdr_ppm          = 0;            % RTL-SDR tuner parts per million correction
% PARAMETERS (can change, but may break code)
nfrmhold            = 2;           % number of frames to receive
fft_hold            = 'avg';        % hold function "max" or "avg"
nfft                = 4096;         % number of points in FFTs (2^something)
dec_factor          = 16;           % output plot downsample
overlap             = 0.5;          % FFT overlap to counter rolloff
nfrmdump            = 1;          % number of frames to dump after retuning (to clear b

% CALCULATIONS
rtlsdr_tunerfreq  = start_freq:rtlsdr_fs*overlap:stop_freq;     % range of tuner frequency in Hz
if( max(rtlsdr_tunerfreq) < stop_freq )                         % check the whole range is covered, if not, add an extra tuner freq
    rtlsdr_tunerfreq(length(rtlsdr_tunerfreq)+1) = max(rtlsdr_tunerfreq)+rtlsdr_fs*overlap;
end
nretunes = length(rtlsdr_tunerfreq);                            % calculate number of retunes required
freq_bin_width = (rtlsdr_fs/nfft);                              % create xaxis
freq_axis = (rtlsdr_tunerfreq(1)-rtlsdr_fs/2*overlap  :  freq_bin_width*dec_factor  :  (rtlsdr_tunerfreq(end)+rtlsdr_fs/2*overlap)-freq_bin_width)/1e6;

obj_rtlsdr = comm.SDRRTLReceiver(...
            rtlsdr_id,...
            'CenterFrequency',      rtlsdr_tunerfreq(1),...
            'EnableTunerAGC', 		false,...
            'TunerGain', 			rtlsdr_gain,...
            'SampleRate',           rtlsdr_fs, ...
            'SamplesPerFrame', 		rtlsdr_frmlen,...
            'OutputDataType', 		rtlsdr_datatype ,...
            'FrequencyCorrection', 	rtlsdr_ppm );

rtlsdr_data = obj_rtlsdr();
rtlsdr_data = rtlsdr_data - mean(rtlsdr_data);
rtlsdr_data_fft = abs(fft(rtlsdr_data,nfft))';
%fft_reorder(( 1 : (overlap*nfft/2) ))      = rtlsdr_data_fft( (overlap*nfft/2)+(nfft/2)+1 : end );   % -ve
%fft_reorder(( (overlap*nfft/2)+1 : end ))  = rtlsdr_data_fft( 1 : (overlap*nfft/2) ); 
figure(1);
plot(rtlsdr_data_fft);

obj_rtlsdr.CenterFrequency = rtlsdr_tunerfreq(1)+1.4e6;

for i = 1:1
    rtlsdr_data = obj_rtlsdr();
end
rtlsdr_data = obj_rtlsdr();
rtlsdr_data = rtlsdr_data - mean(rtlsdr_data);
rtlsdr_data_fft = abs(fft(rtlsdr_data,nfft))';
figure(2);
plot(rtlsdr_data_fft);