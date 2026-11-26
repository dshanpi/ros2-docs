---
title: "15.3 摄像头模块调试"
sidebar_label: "15.3 摄像头模块调试"
slug: /chapter-15/section-03/
---

## 15.3.1 UVC模块介绍

1. <strong>UVC简介</strong>

UVC（USB Video Class）是由USB-IF组织发布的USB视频设备类规范，用于标准化通过USB接口连接的视频捕捉设备，如摄像头、电视调谐卡、视频采集盒等。

符合UVC协议的设备可以即插即用，在支持UVC的操作系统（如Windows、Linux、macOS、Android）中无需安装专有驱动。

2. <strong>UVC的主要功能</strong>

UVC（USB Video Class）是一种通用的视频设备协议，具有良好的跨平台兼容性。现代操作系统普遍内置其驱动支持，用户可无需额外安装驱动，即可使用各类 USB 摄像设备。UVC 模块主要具备以下功能：

- 视频采集：支持多种分辨率和帧率的视频流捕捉；

- 图像控制：支持亮度、对比度、曝光、白平衡等参数调节；

- 多媒体同步：可与音频设备协同工作，支持音视频同步；

- 热插拔支持：可动态识别和挂载UVC设备。

3. <strong>UVC在Linux系统中的支持</strong>

Linux内核原生支持UVC设备，主要通过以下模块驱动：

- 驱动模块：uvcvideo

- 设备节点：/dev/videoX（通常为 /dev/video0）

可以通过 v4l2-ctl、ffmpeg、gst-launch 等工具对UVC设备进行控制与调试。

4. <strong>典型 UVC 应用场景</strong>

得益于其良好的通用性、稳定性与即插即用的特性，UVC 摄像头在多个行业和应用场景中得到了广泛应用，尤其适用于需要视频采集与图像处理的系统。常见的应用场景包括：

- 视频会议系统：作为主要的视频采集设备，用于远程会议中的实时人像传输与交流。

- 在线教育与远程教学：用于教师授课画面的采集和直播，提升互动性与教学质量。

- 安防监控系统：广泛应用于家庭、商业和工业安防中，进行图像监控与录像。

- 工业机器视觉检测：在自动化生产线上进行图像识别、缺陷检测、尺寸测量等任务。

- 移动机器人视觉模块：为服务型机器人、巡检机器人等提供环境感知与导航视觉输入。

## 15.3.2 使用UVC驱动进行图像采集

在了解 UVC 模块后，下一步是通过程序实际驱动摄像头采集图像数据。本节将结合 OpenCV 工具，展示如何基于系统提供的 UVC 驱动接口获取摄像头图像帧，并进一步实现一个人脸识别的示例程序。

1. <strong>工程目录说明</strong>

为便于后续项目中复用图像采集与人脸识别功能，本节将上述功能模块封装为一个静态库。工程目录结构如下所示：

```text
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/Test/face_camera$ tree
.
├── CMakeLists.txt
├── include
│   └── uvc_camera.h
├── README.md
└── src
    ├── face_recognition_test.cpp   # 人脸识别例程
    ├── main.cpp                      # 采集图像帧例程
    └── uvc_camera.cpp

3 directories, 6 files
```

2. <strong>图像采集程序说明</strong>

图像采集程序通过 OpenCV 调用UVC摄像头，有gui环境则实时显示，无gui环境则保存图像帧。

功能说明：

- 初始化视频设备；

- 从 /dev/video20 获取图像帧；

- 显示图像或保存图像。

uvc\_camera.cpp初始化设备实现：

```cpp
bool UVCCamera::open() {
    // ===== 1. 使用V4L2 API进行底层参数设置 =====
    fd_ = ::open(device_path_.c_str(), O_RDWR);
    if (fd_ < 0) {
        std::cerr << "无法打开设备: " << device_path_ << " (" << strerror(errno) << ")" << std::endl;
        return false;
    }

    // 设置格式 (优先使用MJPEG)
    v4l2_format fmt = {0};
    fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
    fmt.fmt.pix.width = width_;
    fmt.fmt.pix.height = height_;
    fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_MJPEG;
    if (!setV4L2Parameter(VIDIOC_S_FMT, &fmt, "格式 (MJPEG)")) {
        std::cout << "MJPEG设置失败，尝试YUYV..." << std::endl;
        fmt.fmt.pix.pixelformat = V4L2_PIX_FMT_YUYV;
        if (!setV4L2Parameter(VIDIOC_S_FMT, &fmt, "格式 (YUYV)")) {
            close(fd_);
            fd_ = -1;
            return false;
        }
    }

    // 设置特定于V4L2的参数
    setV4L2Control(V4L2_CID_AUTO_WHITE_BALANCE, 0, "自动白平衡");
    setV4L2Control(V4L2_CID_WHITE_BALANCE_TEMPERATURE, 6000, "白平衡温度");
    setV4L2Control(V4L2_CID_EXPOSURE_AUTO, V4L2_EXPOSURE_MANUAL, "曝光模式");

    close(fd_); // 底层设置完成
    fd_ = -1;

    // ===== 2. 使用OpenCV采集视频流 =====
    cap_.open(device_path_, cv::CAP_V4L2);
    if (!cap_.isOpened()) {
        std::cerr << "OpenCV无法打开设备: " << device_path_ << std::endl;
        return false;
    }

    // 使用OpenCV设置通用参数
    if (!cap_.set(cv::CAP_PROP_FRAME_WIDTH, width_)) std::cerr << "警告: 无法设置宽度" << std::endl;
    if (!cap_.set(cv::CAP_PROP_FRAME_HEIGHT, height_)) std::cerr << "警告: 无法设置高度" << std::endl;
    if (!cap_.set(cv::CAP_PROP_FPS, fps_)) std::cerr << "警告: 无法设置FPS" << std::endl;

    is_initialized_ = true;
    return true;
}
```

uvc\_camera.cpp获取图像帧实现：

```text
bool UVCCamera::captureFrame(cv::Mat& frame) {
    if (!is_initialized_ || !cap_.isOpened()) {
        return false;
    }
    return cap_.read(frame);
}
```

显示图像和图像保存在上层main.cpp实现：

```cpp
if (gui_enabled) {
        std::string window_name = "UVC Capture: " + std::string(device);
        cv::namedWindow(window_name, cv::WINDOW_NORMAL);

        while (true) {
            if (!camera.captureFrame(frame)) {
                std::cerr << "错误: 无法读取帧!" << std::endl;
                break;
            }
            if (frame.empty()) {
                std::cerr << "警告: 收到空帧!" << std::endl;
                continue;
            }

            cv::imshow(window_name, frame);

            int key = cv::waitKey(1);
            if (key == 27) break; // ESC
            else if (key == 's' || key == 'S') {
                std::string filename = "capture.jpg";
                if (cv::imwrite(filename, frame)) {
                    std::cout << "图像已保存为 " << filename << std::endl;
                } else {
                    std::cerr << "错误: 无法保存图像!" << std::endl;
                }
            }
        }
        cv::destroyAllWindows();
    } else {
        std::cout << "无GUI模式: 正在捕获一帧并保存..." << std::endl;
        if (!camera.captureFrame(frame)) {
            std::cerr << "错误: 无法读取帧!" << std::endl;
        } else if (frame.empty()) {
            std::cerr << "错误: 收到空帧!" << std::endl;
        } else {
            std::string dir_path = "data";
            if (mkdir(dir_path.c_str(), 0755) != 0 && errno != EEXIST) {
                std::cerr << "错误: 无法创建目录 '" << dir_path << "': " << strerror(errno) << std::endl;
            }
            std::string filename = dir_path + "/me.jpg";
            if (cv::imwrite(filename, frame)) {
                std::cout << "图像已成功保存为 " << filename << std::endl;
            } else {
                std::cerr << "错误: 无法保存图像!" << std::endl;
            }
        }
    }
```

3. <strong>人脸识别程序说明</strong>

该程序在图像采集的基础上，利用了OpenCV 的人脸识别模块 cv2.CascadeClassifier 进行检测。

功能说明：

- 加载 Haar 特征级联分类器；

- 对图像帧进行灰度化；

- 检测人脸并在图像中标记。

uvc\_camera.cpp加载 Haar 特征级联分类器功能实现如下：

```cpp
bool UVCCamera::loadFaceDetectionModel(const std::string& model_path) {
    if (!face_cascade_.load(model_path)) {
        std::cerr << "ERROR: Could not load face cascade model from " << model_path << std::endl;
        return false;
    }
    return true;
}
```

对图像帧进行灰度化功能在上层face\_recognition\_test.cpp中实现：

```text
cv::Mat my_face = cv::imread("data/me.jpg", cv::IMREAD_GRAYSCALE);
training_faces.push_back(my_face);
training_labels.push_back(0);
```

首先从文件系统加载训练图像，然后转化为灰度图（符合LBPH要求），最后添加到训练集并设置标签为0。

uvc\_camera.cpp检测人脸并在图像中标记功能实现如下：

```cpp
void UVCCamera::trainFaceRecognizer(const std::vector<cv::Mat>& faces, const std::vector<int>& labels) {
    if (faces.empty() || labels.empty() || faces.size() != labels.size()) {
        std::cerr << "ERROR: Invalid training data." << std::endl;
        return;
    }
    face_recognizer_->train(faces, labels);
    // 假设标签0是“MeiHao”
    label_info_[0] = "MeiHao";
    label_info_[1] = "Unknown";
}

int UVCCamera::recognizeFace(const cv::Mat& face) {
    int predicted_label = -1;
    double confidence = 0.0;
    face_recognizer_->predict(face, predicted_label, confidence);
    // 这里可以根据置信度来判断是否是可信的识别结果
    // 为简单起见，我们直接返回标签，但可以设置一个阈值
    if (confidence < 100) { // 置信度越低越好
        return predicted_label;
    }
    return 1; // 返回“Unknown”
}
```

以上便是主要代码的讲解，具体可以阅读完整工程代码。接下来演示如何进行编译。

4. <strong>编译、运行程序</strong>

在工程根目录下，执行以下指令进行编译：

```text
mkdir build
cd build
cmake ..
make
```

运行图像采集程序：

```text
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/Test/face_camera/build$ ./uvc_app --no-gui
无法设置 曝光模式: Invalid argument
无GUI模式: 正在捕获一帧并保存...
图像已成功保存为 date/me.jpg
```

运行人脸识别程序：

```text
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/Test/face_camera/build$ ./face_recognition_test /dev/video20 --no-gui
Running in --no-gui mode.
Using device: /dev/video20
无法设置 曝光模式: Invalid argument
Starting face recognition...
Result: MeiHao detected.
Saved annotated image to recognition_result.jpg
```

注意：

运行人脸检测前，需要在build目录下，从opencv仓库地址下载人脸检测模型haarcascade\_frontalface\_default.xml 文件，并且准备一张自己的清晰正面照片，命名为 me.jpg，并放入 data 文件夹。
