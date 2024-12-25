import sys
import time
import psutil
import subprocess
import threading


import matplotlib.pyplot as plt

dot_count = 0


def read_stream(stream, name):
    global dot_count
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
    fps_data = []
    time_data = []

    prev_dot_count = 0
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
        global dot_count
        dots_in_this_interval = dot_count - prev_dot_count
        prev_dot_count = dot_count
        fps = dots_in_this_interval / 1.0
        fps_data.append(fps)
        time_data.append(now)

        print(
            f"Debug: Time={now:.1f}s CPU={cpu_usage:.2f}% Mem={mem_usage:.2f}MB FPS={fps:.2f}"
        )

        if process.poll() is not None:
            print("Debug: Subprocess finished, breaking loop.")
            break

    # Join threads to ensure we read remaining output
    out_thread.join()
    err_thread.join()

    print("Debug: Plotting results")
    fig, axs = plt.subplots(3, 1, figsize=(8, 8))

    axs[0].plot(time_data, cpu_data, label="CPU %")
    axs[0].set_ylabel("CPU (%)")
    axs[0].legend()
    axs[0].grid(True)

    axs[1].plot(time_data, mem_data, label="Memory (MB)", color="orange")
    axs[1].set_ylabel("Mem (MB)")
    axs[1].legend()
    axs[1].grid(True)

    axs[2].plot(time_data, fps_data, label="FPS", color="green")
    axs[2].set_ylabel("FPS")
    axs[2].set_xlabel("Time (s)")
    axs[2].legend()
    axs[2].grid(True)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
