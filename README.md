A simple comparison between different programming languages for a basic computer vision task.

There's a performance benchmark and my personal UX opinion on each language.

# Steps to test

## Before you start

1. Before running the code, make sure you have the following libraries installed:

- [OpenCV](https://opencv.org/)
- [Gstreamer](https://gstreamer.freedesktop.org/)

2. Create a Python venv and install the Python dependencies:

```bash
python -m venv venv

# For Unix (Linux, macOS)
source venv/bin/activate

# For Windows
venv\Scripts\activate

pip install -r requirements.txt
```

3. Make sure you have a MJPEG stream URL to test the code with.
   You can use a free Android app called "IP Webcam" to create a stream from your phone's camera.

For example, a stream URL can look like this: `http://192.168.0.251:8080/video`

Make sure to replace the `<stream_url>` placeholder with your stream URL in the commands below.

## C++

> Important: Use an external terminal (i.e. not the one integrated in your IDE, you can e.g. use normal Command Prompt). It didn't work for me when I tried to use the VSCode terminal.

1. Open the terminal in the `exampleCpp` directory
2. Build the project with CMake:

```bash
mkdir build
cd build
cmake ..
make
```

3. Go back to the root directory:

```bash
cd ..
```

4. Run the measure script

```
python measure.py ./exampleCpp/out/build/x64-release/exampleCpp.exe <stream_url>
```

e.g.

```
python measure.py ./exampleCpp/out/build/x64-release/exampleCpp.exe http://192.168.0.251:8080/video
```
