import psutil
import subprocess
import time
import matplotlib.pyplot as plt
import threading
import queue
import argparse


# Function to monitor resources
def monitor_resources(proc, q):
    cpu_usage = []
    memory_usage = []
    timestamps = []
    stdout_values = []

    def read_stdout():
        """Reads the process's stdout and stores values."""
        while True:
            try:
                line = proc.stdout.readline()
                if line == b"" and proc.poll() is not None:
                    break
                if line:
                    try:
                        value = float(line.decode().strip())
                        stdout_values.append((time.time() - start_time, value))
                    except ValueError:
                        pass
            except Exception:
                break

    start_time = time.time()
    stdout_thread = threading.Thread(target=read_stdout)
    stdout_thread.daemon = True
    stdout_thread.start()

    try:
        while proc.poll() is None:
            try:
                process = psutil.Process(proc.pid)
                with process.oneshot():
                    cpu = process.cpu_percent(interval=0.1)
                    memory = process.memory_info().rss / (1024 * 1024)  # Convert to MB
                    timestamp = time.time() - start_time

                    # Collect data
                    cpu_usage.append((timestamp, cpu))
                    memory_usage.append((timestamp, memory))
                    timestamps.append(timestamp)

                time.sleep(0.5)  # Poll every 0.5 seconds
            except psutil.NoSuchProcess:
                break

        stdout_thread.join()
    except KeyboardInterrupt:
        proc.terminate()
    finally:
        q.put((cpu_usage, memory_usage, stdout_values))


# Function to plot results
def plot_results(cpu_usage, memory_usage, stdout_values):
    fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

    # Plot CPU usage
    if cpu_usage:
        cpu_timestamps, cpu_values = zip(*cpu_usage)
        axs[0].plot(cpu_timestamps, cpu_values, label="CPU Usage (%)", color="blue")
        axs[0].set_ylabel("CPU Usage (%)")
        axs[0].legend()
        axs[0].grid(True)

    # Plot memory usage
    if memory_usage:
        mem_timestamps, mem_values = zip(*memory_usage)
        axs[1].plot(
            mem_timestamps, mem_values, label="Memory Usage (MB)", color="green"
        )
        axs[1].set_ylabel("Memory Usage (MB)")
        axs[1].legend()
        axs[1].grid(True)

    # Plot stdout values
    if stdout_values:
        out_timestamps, out_values = zip(*stdout_values)
        axs[2].plot(out_timestamps, out_values, label="Stdout Values", color="red")
        axs[2].set_ylabel("Output Value")
        axs[2].legend()
        axs[2].grid(True)

    axs[2].set_xlabel("Time (s)")
    plt.tight_layout()
    plt.show()


# Main function
def main():
    parser = argparse.ArgumentParser(
        description="Monitor and plot resource usage of a process."
    )
    parser.add_argument("command", nargs="+", help="The command to run.")
    args = parser.parse_args()

    # Start the process
    with subprocess.Popen(
        args.command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
        universal_newlines=False,
    ) as proc:
        q = queue.Queue()
        monitor_thread = threading.Thread(target=monitor_resources, args=(proc, q))
        monitor_thread.start()
        monitor_thread.join()

        # Retrieve collected data
        cpu_usage, memory_usage, stdout_values = q.get()

    # Plot results
    plot_results(cpu_usage, memory_usage, stdout_values)


if __name__ == "__main__":
    main()
