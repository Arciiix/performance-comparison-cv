import os
import sys
import time
import psutil
import subprocess
import threading
import matplotlib.pyplot as plt

dot_count = 0
comma_count = 0


def read_stream(stream, name):
    global dot_count, comma_count
    print(f"Debug: Starting thread to read {name}")
    while True:
        chunk = stream.read(1)  # Read character-by-character
        if not chunk:
            print(f"Debug: {name} stream ended")
            break
        text = chunk.decode("utf-8")
        sys.stdout.write(text)
        sys.stdout.flush()
        if text == ".":
            dot_count += 1
        elif text == ",":
            comma_count += 1


def measure_usage(proc):
    print("Debug: Gathering CPU and memory usage")
    total_cpu = 0.0
    total_mem = 0.0
    procs = [proc] + proc.children(recursive=True)
    for p in procs:
        if p.is_running():
            try:
                total_cpu += p.cpu_percent(interval=None)
                total_mem += p.memory_info().rss
            except psutil.NoSuchProcess:
                pass
    return total_cpu, total_mem / (1024 * 1024)  # Convert to MB


def main():
    if len(sys.argv) < 2:
        print("Usage: python measure.py <command> [args...]")
        sys.exit(1)
    command = sys.argv[1:]
    print(f"Debug: Command to run is {command}")

    # If it's an executable, cd to its directory
    if "/" in command[0]:
        exe_dir = command[0].rsplit("/", 1)[0]
        print(f"Debug: Changing directory to {exe_dir}")
        os.chdir(exe_dir)
        command[0] = command[0].rsplit("/", 1)[1]

    print("Debug: Spawning subprocess")
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=False,
        bufsize=0,
    )

    # Threads to read stdout and stderr
    out_thread = threading.Thread(
        target=read_stream, args=(process.stdout, "stdout"), daemon=True
    )
    err_thread = threading.Thread(
        target=read_stream, args=(process.stderr, "stderr"), daemon=True
    )
    out_thread.start()
    err_thread.start()

    ps_proc = psutil.Process(process.pid)
    print("Debug: Created psutil.Process")

    cpu_data = []
    mem_data = []
    dot_fps_data = []
    comma_fps_data = []
    time_data = []

    prev_dot_count = 0
    prev_comma_count = 0
    start_time = time.time()

    while True:
        # Wait a bit before measuring
        time.sleep(1.0)
        now = time.time() - start_time

        # Measure CPU and memory usage
        cpu_usage, mem_usage = measure_usage(ps_proc)
        cpu_data.append(cpu_usage)
        mem_data.append(mem_usage)

        # Calculate FPS (dots/second) in last interval
        global dot_count, comma_count
        dots_in_this_interval = dot_count - prev_dot_count
        commas_in_this_interval = comma_count - prev_comma_count
        prev_dot_count = dot_count
        prev_comma_count = comma_count
        dot_fps = dots_in_this_interval / 1.0
        comma_fps = commas_in_this_interval / 1.0
        dot_fps_data.append(dot_fps)
        comma_fps_data.append(comma_fps)
        time_data.append(now)

        print(
            f"Debug: Time={now:.1f}s CPU={cpu_usage:.2f}% Mem={mem_usage:.2f}MB Dot FPS={dot_fps:.2f} Comma FPS={comma_fps:.2f}"
        )

        if process.poll() is not None:
            print("Debug: Subprocess finished, breaking loop.")
            break

    # Join threads to ensure we read remaining output
    out_thread.join()
    err_thread.join()

    print("Debug: Plotting results")
    fig, axs = plt.subplots(4, 1, figsize=(8, 10))

    # Plot CPU usage
    axs[0].plot(time_data, cpu_data, label="CPU %")
    axs[0].set_ylabel("CPU (%)")
    axs[0].legend()
    axs[0].grid(True)

    # Plot memory usage
    axs[1].plot(time_data, mem_data, label="Memory (MB)", color="orange")
    axs[1].set_ylabel("Mem (MB)")
    axs[1].legend()
    axs[1].grid(True)

    # Plot dot FPS
    axs[2].plot(time_data, dot_fps_data, label="Face Recog FPS", color="green")
    axs[2].set_ylabel("Face Recog FPS")
    axs[2].legend()
    axs[2].grid(True)

    # Plot comma FPS
    axs[3].plot(time_data, comma_fps_data, label="Raw Stream FPS", color="blue")
    axs[3].set_ylabel("Raw Stream FPS")
    axs[3].set_xlabel("Time (s)")
    axs[3].legend()
    axs[3].grid(True)

    # Function to calculate statistics
    def calculate_stats(data):
        non_zero_data = [d for d in data if d > 0]
        if not non_zero_data:
            return 0, 0, 0, 0
        non_zero_data.sort()
        n = len(non_zero_data)
        median = (
            non_zero_data[n // 2]
            if n % 2 == 1
            else (non_zero_data[n // 2 - 1] + non_zero_data[n // 2]) / 2
        )
        return (
            min(non_zero_data),
            max(non_zero_data),
            sum(non_zero_data) / len(non_zero_data),
            median,
        )

    # Calculate statistics for each metric
    stats = [
        calculate_stats(cpu_data),
        calculate_stats(mem_data),
        calculate_stats(dot_fps_data),
        calculate_stats(comma_fps_data),
    ]

    # Annotate statistics on plots
    for i, (min_val, max_val, avg_val, median_val) in enumerate(stats):
        axs[i].annotate(
            f"Min: {min_val:.2f}\nMax: {max_val:.2f}\nAvg: {avg_val:.2f}\nMedian: {median_val:.2f}",
            xy=(0.01, 0.99),
            xycoords="axes fraction",
            verticalalignment="top",
            bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white"),
        )

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
