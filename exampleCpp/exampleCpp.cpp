// exampleCpp.cpp : Defines the entry point for the application.
//

#include "exampleCpp.h"

#include <iostream>
#include <opencv2/opencv.hpp>
#include <gst/gst.h>
#include <gst/app/gstappsink.h>

bool shouldExit = false;

int loop(const std::string& streamUrl, const char* id, bool withFaceDetection) {
    std::cout << "Hello" << std::endl;

    std::string streamId = std::string(id);

    GstElement* pipeline = nullptr;
    GstElement* sink = nullptr;
    GstBus* bus = nullptr;
    GstMessage* msg = nullptr;
    GMainLoop* loop = nullptr;

    cv::CascadeClassifier faceCascade;

    if (withFaceDetection && !faceCascade.load("haarcascade_frontalface_default.xml")) {
        std::cerr << "Error loading Haar Cascade XML file!" << std::endl;
        return -1;
    }

    gst_init(0, nullptr);

    std::string pipelineDesc =
        "souphttpsrc location=" + streamUrl + " ! jpegdec ! videoconvert ! appsink name=sink";

    GError* pipelineError = nullptr;
    pipeline = gst_parse_launch(pipelineDesc.c_str(), &pipelineError);

    if (pipelineError) {
        std::cerr << "Failed to create the pipline: " << pipelineError->message << std::endl;
        g_error_free(pipelineError);
        return -1;
    }

    if (!pipeline) {
        std::cerr << "Failed to create the pipline";
        g_error_free(pipelineError);
        return -1;
    }

    sink = gst_bin_get_by_name(GST_BIN(pipeline), "sink");

    if (!sink) {
        std::cerr << "Failed to get the sink element" << std::endl;
        return -1;
    }

    gst_app_sink_set_emit_signals(GST_APP_SINK(sink), false);
    gst_app_sink_set_drop(GST_APP_SINK(sink), true);
    gst_app_sink_set_max_buffers(GST_APP_SINK(sink), 1);


    gst_element_set_state(pipeline, GST_STATE_PLAYING);

    std::cout << "Start" << std::endl;

    while (true) {
        if (shouldExit) {
			break;
		}
        GstSample* sample = gst_app_sink_pull_sample(GST_APP_SINK(sink));
        if (!sample) {
            std::cerr << "Failed to pull sample. Exiting loop." << std::endl;
            break;
        }

        GstBuffer* buffer = gst_sample_get_buffer(sample);
        GstMapInfo map;
        if (!gst_buffer_map(buffer, &map, GST_MAP_READ)) {
            std::cerr << "Failed to map buffer." << std::endl;
            gst_sample_unref(sample);
            continue;
        }

        GstCaps* caps = gst_sample_get_caps(sample);
        GstStructure* s = gst_caps_get_structure(caps, 0);
        int width, height;
        gst_structure_get_int(s, "width", &width);
        gst_structure_get_int(s, "height", &height);

        const gchar* pixel_format = gst_structure_get_string(s, "format");

        // Allocate space for the YUV data
        int y_size = width * height;  // Y plane size
        int uv_size = (width / 2) * (height / 2);  // U and V plane size

        // Create a cv::Mat with the I420 data
        cv::Mat yuv_image(height + height / 2, width, CV_8UC1, map.data);

        // Convert YUV to RGB using OpenCV (this will be displayed)
        cv::Mat rgb_image;
        cv::cvtColor(yuv_image, rgb_image, cv::COLOR_YUV2BGR_I420);

        if (withFaceDetection) {
            cv::Mat gray_frame;
            cv::cvtColor(rgb_image, gray_frame, cv::COLOR_BGR2GRAY);
            cv::resize(gray_frame, gray_frame, cv::Size(640, 480));
            cv::equalizeHist(gray_frame, gray_frame);

            std::vector<cv::Rect> faces;
            // Detect faces
            faceCascade.detectMultiScale(gray_frame, faces, 1.1, 3, 0, cv::Size(30, 30));

            // Draw rectangles around detected faces
            for (const auto& face : faces) {
                // Recalculate the face rectangle to the original frame size
                cv::Rect resizedFace(face.x * width / 640, face.y * height / 480, face.width * width / 640, face.height * height / 480);
                cv::rectangle(rgb_image, resizedFace, cv::Scalar(0, 255, 0), 2);
            }
        }

        // Display the frame in OpenCV window
        cv::imshow("Stream " + streamId, rgb_image);

        if (cv::waitKey(1) == 27) { // Exit on 'Esc'
            shouldExit = true;
            break;
        }

        // Cleanup
        gst_buffer_unmap(buffer, &map);
        gst_sample_unref(sample);

        // For measuring FPS
        std::cout << streamId;
        std::cout.flush();
    }

    std::cout << "End" << std::endl;

    gst_element_set_state(pipeline, GST_STATE_NULL);
    gst_object_unref(pipeline);
}

int main(int arg, char* argv[])
{
    std::cout << "Hello main" << std::endl;

    if (arg < 2) {
		std::cerr << "Usage: " << argv[0] << " <streamUrl>" << std::endl;
		return -1;
	}

    std::string streamUrl = argv[1];

    std::thread t1(loop, streamUrl, ".", true);
    std::thread t2(loop, streamUrl, ",", false);
    std::thread t3(loop, streamUrl, "a", true);
    std::thread t4(loop, streamUrl, "b", false);
    std::thread t5(loop, streamUrl, "c", false);
    std::thread t6(loop, streamUrl, "d", false);
    std::thread t7(loop, streamUrl, "e", false);
    std::thread t8(loop, streamUrl, "f", true);

    std::thread* threads[] = {&t1, &t2, &t3, &t4, &t5, &t6, &t7, &t8};

    for (auto& t : threads) {
		t->join();
	}

    // Clean up
    cv::destroyAllWindows();
    cv::waitKey(1);

    return 0;
}
