// exampleCpp.cpp : Defines the entry point for the application.
//

#include "exampleCppFfmpeg.h"

#include <iostream>
#include <opencv2/opencv.hpp>

bool shouldExit = false;

int loop(const std::string& streamUrl, const char* id, bool withFaceDetection) {
    std::cout << "Hello" << std::endl;

    std::string streamId = std::string(id);

    cv::CascadeClassifier faceCascade;

    if (withFaceDetection && !faceCascade.load("haarcascade_frontalface_default.xml")) {
        std::cerr << "Error loading Haar Cascade XML file!" << std::endl;
        return -1;
    }

    std::cout << "Start" << std::endl;

    cv::VideoCapture cap(streamUrl);
    cap.set(cv::CAP_PROP_BUFFERSIZE, 1);

    while (true) {
        if (shouldExit) {
            break;
        }
       
        cv::Mat frame;
        cap >> frame;

       if (frame.empty()) {
			std::cerr << "Error: Empty frame" << std::endl;
            continue;
		}

       int width = frame.cols;
       int height = frame.rows;

        if (withFaceDetection) {
            cv::Mat gray_frame;
            cv::cvtColor(frame, gray_frame, cv::COLOR_BGR2GRAY);
            cv::resize(gray_frame, gray_frame, cv::Size(640, 480));
            cv::equalizeHist(gray_frame, gray_frame);

            std::vector<cv::Rect> faces;
            // Detect faces
            faceCascade.detectMultiScale(gray_frame, faces, 1.1, 3, 0, cv::Size(30, 30));

            // Draw rectangles around detected faces
            for (const auto& face : faces) {
                // Recalculate the face rectangle to the original frame size
                cv::Rect resizedFace(face.x * width / 640, face.y * height / 480, face.width * width / 640, face.height * height / 480);
                cv::rectangle(frame, resizedFace, cv::Scalar(0, 255, 0), 2);
            }
        }

        // Display the frame in OpenCV window
        cv::imshow("Stream " + streamId, frame);

        if (cv::waitKey(1) == 27) { // Exit on 'Esc'
            shouldExit = true;
            break;
        }

        // For measuring FPS
        std::cout << streamId;
        std::cout.flush();
    }

    std::cout << "End" << std::endl;

    cap.release();
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

    for (int i = 0; i < 8; i++) {
		threads[i]->join();
	}

    // Clean up
    cv::destroyAllWindows();
    cv::waitKey(1);

    return 0;
}
