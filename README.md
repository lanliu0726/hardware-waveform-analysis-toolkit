# Hardware Waveform Analysis Toolkit

This is a small Python project for analysing periodic PWM waveform data from CSV files.

The program reads time-voltage data, detects waveform edges, calculates common timing parameters, and saves the results as a plot and a CSV file.

## What it does

- Reads waveform data from a CSV file
- Estimates the high and low voltage levels
- Uses 10%, 50% and 90% thresholds for timing measurements
- Detects rising and falling edges
- Uses linear interpolation to estimate edge crossing times
- Calculates period, frequency, pulse width, duty cycle, rise time and fall time
- Calculates mean, minimum, maximum and standard deviation over multiple PWM cycles
- Saves a waveform plot
- Saves the analysis results to a CSV file

## Input

The input CSV should contain one time column and one voltage column.

Example:

```csv
Time,Voltage
0.000000,0.01
0.000005,0.02
0.000010,0.03
...
```

The filename and column names can be changed in the script:

```python
filename = "waveform.csv"
time_column = "Time"
voltage_column = "Voltage"
```

## Requirements

```bash
python3 -m pip install -r requirements.txt
```

The project uses NumPy, pandas and Matplotlib.

## Run

```bash
python3 waveform_analyzer.py
```

The program prints the analysis results in the terminal and also creates:

```text
waveform_plot.png
analysis_results.csv
```

## Example result

The sample data in this repository is a simulated PWM waveform with 4,000 samples and about 20 cycles.

One example run produced:

```text
Sample rate: 200000.000 Sa/s
Low level: 0.006 V
High level: 3.309 V
50% threshold: 1.657 V

Valid cycles analyzed: 19

Period mean: 1.000 ms
Frequency mean: 1000.223 Hz
Pulse width mean: 0.402 ms
Duty cycle mean: 40.257%
Rise time mean: 20.424 us
Fall time mean: 24.359 us
```

## Notes

This project is mainly intended for simple and stable periodic PWM/pulse waveforms.

For waveforms with severe noise, ringing, very small duty cycles, multiple pulses in one period, or unusual oscilloscope CSV formats, extra processing may be needed.
