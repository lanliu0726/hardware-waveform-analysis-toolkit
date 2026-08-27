import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def load_waveform(filename, time_column, voltage_column): #讲文件转换为数据
    df = pd.read_csv(filename) #读取文件
    df = df[[time_column, voltage_column]].dropna() #当time/voltage存在缺失，删除行
    times = df[time_column].to_numpy() 
    voltages = df[voltage_column].to_numpy()

    if len(times) < 2:
        raise ValueError("Not enough waveform samples.") #数据太少则报错停止

    return times, voltages

def calculate_sample_rate(times): #采样间隔，采样率
    dt = np.diff(times) #计算采样间隔
    sample_interval = np.mean(dt) #计算平均采样间隔
    sample_rate = 1 / sample_interval #计算采样率

    return sample_interval, sample_rate

def interpolate_crossing(times, voltages, index, threshold): #精确计算穿过阈值时的时间
    t1 = times[index - 1]
    t2 = times[index]

    v1 = voltages[index - 1]
    v2 = voltages[index]

    ratio = (threshold - v1) / (v2 - v1)
    crossing_time = t1 + ratio * (t2 - t1)

    return crossing_time

def detect_edges(voltages, threshold, times): #检测上升/下降沿
    high = voltages >= threshold #判断high or low
    digital = high.astype(int) #转换为1/0
    changes = np.diff(digital) #计算差值

    rising_indices = np.where(changes == 1)[0] + 1 #当为1时，代表发生了rising，取发生的index
    falling_indices = np.where(changes == -1)[0] + 1 #当为-1时，代表发生了falling，取发生的index

    rising_times = []
    falling_times = []

    for index in rising_indices: #调用计算穿过阈值时的时间函数，添加进数组
        crossing_time = interpolate_crossing(times, voltages, index, threshold)
        rising_times.append(crossing_time)

    for index in falling_indices:
        crossing_time = interpolate_crossing(times, voltages, index, threshold)
        falling_times.append(crossing_time)
    
    rising_times = np.array(rising_times) #转换为numpy数组
    falling_times = np.array(falling_times) 
    
    return rising_indices, falling_indices, rising_times, falling_times

def calculate_waveform_parameters(rising_times, falling_times):
    periods = []
    frequencies = []
    pulse_widths = []
    duty_cycles = []

    for i in range(len(rising_times) - 1): #从0开始循环

        rising = rising_times[i]
        next_rising = rising_times[i + 1]

        valid_falling = falling_times[
            (falling_times > rising) &
            (falling_times < next_rising)] #找到当前rising和下一个rising之间的falling
        
        if len(valid_falling) != 1:
            continue #对于单pwm，一个周期内只有一个falling，不符合则跳过

        falling = valid_falling[0] #将array的数提取出来

        period = next_rising -rising #计算周期
        pulse_width = falling - rising #计算脉冲宽度
        frequency = 1 / period #计算频率
        duty_cycle = pulse_width / period * 100 #计算占空比

        periods.append(period) #将计算所得数值添加进数组
        frequencies.append(frequency)
        pulse_widths.append(pulse_width)
        duty_cycles.append(duty_cycle)
    # 此处退出循环
    if len(periods) == 0: #如未找到有效周期，则返回error，程序在此停止
        raise ValueError("No valid PWM cycles detected")

    return periods, frequencies, pulse_widths, duty_cycles

def plot_waveform(times, voltages): #画图
    plt.plot(times, voltages) #以times,voltages画图
    plt.xlabel("Time (s)") #添加x坐标轴
    plt.ylabel("Voltage (V)") #添加y坐标轴
    plt.title("Waveform") #添加图标标题
    plt.grid() #添加网格
    plt.savefig("waveform_plot.png", dpi=300)
    plt.show()

def save_results(sample_rate, low_level, high_level, periods, frequencies,
                 pulse_widths, duty_cycles, rise_times, fall_times): #将结果生成文件
    results = [
        ["Sample Rate", sample_rate, np.nan, np.nan, np.nan, "Sa/s"],
        ["Low Level", low_level, np.nan, np.nan, np.nan, "V"],
        ["High Level", high_level, np.nan, np.nan, np.nan, "V"],
        ["", np.nan, np.nan, np.nan, np.nan, ""],
        ["Period",
         np.mean(periods) * 1000,
         np.min(periods) * 1000,
         np.max(periods) * 1000,
         np.std(periods) * 1000,
         "ms"],
        ["", np.nan, np.nan, np.nan, np.nan, ""],
        ["Frequency",
         np.mean(frequencies),
         np.min(frequencies),
         np.max(frequencies),
         np.std(frequencies),
         "Hz"],
        ["", np.nan, np.nan, np.nan, np.nan, ""],
        ["Pulse Width",
         np.mean(pulse_widths) * 1000,
         np.min(pulse_widths) * 1000,
         np.max(pulse_widths) * 1000,
         np.std(pulse_widths) * 1000,
         "ms"],
        ["", np.nan, np.nan, np.nan, np.nan, ""],
        ["Duty Cycle",
         np.mean(duty_cycles),
         np.min(duty_cycles),
         np.max(duty_cycles),
         np.std(duty_cycles),
         "%"],
        ["", np.nan, np.nan, np.nan, np.nan, ""],
        ["Rise Time",
         np.mean(rise_times) * 1e6,
         np.min(rise_times) * 1e6,
         np.max(rise_times) * 1e6,
         np.std(rise_times) * 1e6,
         "us"],
        ["", np.nan, np.nan, np.nan, np.nan, ""],
        ["Fall Time",
         np.mean(fall_times) * 1e6,
         np.min(fall_times) * 1e6,
         np.max(fall_times) * 1e6,
         np.std(fall_times) * 1e6,
         "us"]]

    result_df = pd.DataFrame(results,
        columns=["Parameter", "Mean", "Min", "Max", "Std", "Unit"])

    result_df.to_csv("analysis_results.csv", index=False,
                     float_format="%.3f", na_rep="")

filename = "waveform.csv" #定义文件名
time_column = "Time" #定义抬头time列名
voltage_column = "Voltage" #定义抬头voltage列名

try:
    times, voltages = load_waveform(filename,time_column, voltage_column)

except FileNotFoundError: #文件名错误
    print(f"Error: File '{filename}' was not found.")
    raise SystemExit

except KeyError as error: #列名错误
    print(f"Error: Column {error} was not found in the CSV file.")
    raise SystemExit

low_level = np.percentile(voltages, 10) #使用第10百分位数估计低电平
high_level = np.percentile(voltages, 90) #使用第90百分位数估计高电平
#如输入数据为平线，则停止
if high_level <= low_level:
    raise ValueError("Unable to determine valid signal levels.")

threshold_10 = low_level + 0.1 * (high_level - low_level)
threshold_90 = low_level + 0.9 * (high_level - low_level)
threshold = (low_level + high_level) / 2 #计算阈值

sample_interval, sample_rate = calculate_sample_rate(times)
rising_indices, falling_indices, rising_times, falling_times = detect_edges(
    voltages,threshold,times)
periods, frequencies, pulse_widths, duty_cycles = calculate_waveform_parameters(
             rising_times, falling_times)

_,_, rising_10_times, falling_10_times = detect_edges(
    voltages,threshold_10,times) #计算穿过10%电压值的时间
_,_, rising_90_times, falling_90_times = detect_edges(
    voltages,threshold_90,times) #计算穿过90%电压值的时间

rise_count = min(len(rising_10_times),len(rising_90_times)) #取两者更小值
fall_count = min(len(falling_10_times),len(falling_90_times)) #如数组长度不一致，则后续计算无法进行

rise_times = (rising_90_times[:rise_count]
              - rising_10_times[:rise_count]) #计算上升时间
fall_times = (falling_10_times[:fall_count]
              - falling_90_times[:fall_count]) #计算下降时间

rise_times = rise_times[rise_times > 0] #排除小于0的异常数据
fall_times = fall_times[fall_times > 0]

print("=== Waveform Analysis Result ===")
print(f"Samples: {len(times)}") #打印数据行数
print(f"Sample interval: {sample_interval * 1000:.3f} ms") #打印采样间隔
print(f"Sample rate: {sample_rate:.3f} Sa/s") #打印采样率
print(f"Low  level: {low_level:.3f} V")
print(f"High level: {high_level:.3f} V")
print(f"50% threshold: {threshold:.3f} V\n")

rising_text = ",".join(
    f"{t * 1000:.3f}" for t in rising_times[:10])#将前10位数据用,连接组成text
falling_text = ",".join(
    f"{t * 1000:.3f}" for t in falling_times[:10])
print(f"First 10 rising edges: [{rising_text}] ms\n") #打印上升沿
print(f"First 10 falling edges: [{falling_text}] ms") #打印下降沿

print(f"\nValid cycles analyzed: {len(periods)}\n") #打印检测到周期数
print(f"Period:\n"
      f" Mean: {np.mean(periods) * 1000:.3f} ms\n"
      f" Min : {np.min(periods) * 1000:.3f} ms\n"
      f" Max : {np.max(periods) * 1000:.3f} ms\n"
      f" Std : {np.std(periods) * 1000:.3f} ms\n") #打印周期，std为标准差
print(f"Frequency:\n"
      f" Mean: {np.mean(frequencies):.3f} Hz\n"
      f" Min : {np.min(frequencies):.3f} Hz\n"
      f" Max : {np.max(frequencies):.3f} Hz\n"
      f" Std : {np.std(frequencies):.3f} Hz\n") #打印频率
print(f"Pulse width:\n"
      f" Mean: {np.mean(pulse_widths) * 1000:.3f} ms\n"
      f" Min : {np.min(pulse_widths) * 1000:.3f} ms\n"
      f" Max : {np.max(pulse_widths) * 1000:.3f} ms\n") #打印脉冲宽度

print(f"Duty cycle:\n"
      f" Mean: {np.mean(duty_cycles):.3f}%\n"
      f" Min : {np.min(duty_cycles):.3f}%\n"
      f" Max : {np.max(duty_cycles):.3f}%\n"
      f" Std : {np.std(duty_cycles):.3f}%\n") #打印占空比

print(f"Rise time:\n"
      f" Mean: {np.mean(rise_times) * 1e6:.3f} us\n"
      f" Min : {np.min(rise_times) * 1e6:.3f} us\n"
      f" Max : {np.max(rise_times) * 1e6:.3f} us\n"
      f" Std : {np.std(rise_times) * 1e6:.3f} us\n") #打印上升时间

print(f"Fall time:\n"
      f" Mean: {np.mean(fall_times) * 1e6:.3f} us\n"
      f" Min : {np.min(fall_times) * 1e6:.3f} us\n"
      f" Max : {np.max(fall_times) * 1e6:.3f} us\n"
      f" Std : {np.std(fall_times) * 1e6:.3f} us") #打印下降时间

plot_waveform(times, voltages)
save_results(sample_rate, low_level, high_level, periods, frequencies,
    pulse_widths, duty_cycles, rise_times, fall_times)



























    
