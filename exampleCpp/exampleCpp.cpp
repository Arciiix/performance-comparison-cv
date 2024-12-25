// exampleCpp.cpp : Defines the entry point for the application.
//

#include "exampleCpp.h"

#include <iostream>
#include <opencv2/opencv.hpp>
#include <gst/gst.h>
#include <gst/app/gstappsink.h>

std::string streamUrl = "http://192.168.0.251:8080/video";


int main(int arg, char* argv[])
{
    std::cout << "Hello" << std::endl;

    GstElement* pipeline = nullptr;
    GstElement* sink = nullptr;
    GstBus* bus = nullptr;
    GstMessage* msg = nullptr;
    GMainLoop* loop = nullptr;

    gst_init(&arg, &argv);

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

        // Display the frame in OpenCV window
        cv::imshow("Stream", rgb_image);

        if (cv::waitKey(1) == 27) { // Exit on 'Esc'
            break;
        }

        // Cleanup
        gst_buffer_unmap(buffer, &map);
        gst_sample_unref(sample);

        // For measuring FPS
        std::cout << ".";
        std::cout.flush();
    }
  
    
    // Clean up
    cv::destroyAllWindows();
    cv::waitKey(1);
    gst_element_set_state(pipeline, GST_STATE_NULL);
    gst_object_unref(pipeline);

    return 0;
}
