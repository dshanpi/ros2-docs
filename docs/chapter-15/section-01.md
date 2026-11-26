---
title: "15.1 超声波调试"
sidebar_label: "15.1 超声波调试"
slug: /chapter-15/section-01/
---

## 15.1.1 超声波工作原理

后续将使用HC-SR04 超声波模块进行调试，接下来，我们先来了解一下该模块工作原理：

1. <strong>模块概述​</strong>

HC-SR04 超声波模块是一款常用于距离测量的电子模块，具有价格低廉、易于使用等特点，广泛应用于机器人避障、物体测距等场景。该模块主要由发射器、接收器和控制电路三部分组成。发射器负责发射超声波信号，接收器用于接收反射回来的超声波信号，而控制电路则协调发射和接收过程，并根据信号传播时间计算出目标物体的距离。

2. <strong>工作原理详细解析​</strong>

1. 信号发射​

当外部设备（如微控制器）向 HC-SR04 超声波模块发送一个触发信号（通常为一个持续时间极短的高电平信号，一般大于 10μs）时，模块内部的控制电路接收到该触发信号后，会立即启动发射器。发射器开始工作，以 40kHz 的频率向外发射一组超声波脉冲信号。这组信号以声波的形式在空气中向四周传播，其传播速度在常温（20℃）下约为 343 米 / 秒 ，并且会随着环境温度的变化而有所波动（温度每升高 1℃，声速约增加 0.6 米 / 秒）。如下图所示：

[![图 15.1 HC-SR04工作原理图](/img/manual/image184.png)](/img/manual/image184.png)

*图 15.1 HC-SR04工作原理图*

​

2. 信号传播与反射​

发射出去的超声波信号在空气中直线传播，当遇到前方的物体时，会发生反射现象。就如同我们对着山谷喊话，声音遇到山体反射回来形成回声一样，超声波信号碰到物体后，一部分信号会沿着原路返回，朝着模块的接收器传播。

​

3. 信号接收与时间测量​

接收器一直在等待接收反射回来的超声波信号。一旦接收到反射信号，模块内部的控制电路会立即记录从发射信号开始到接收到反射信号为止所经历的时间，这个时间我们称之为“渡越时间”（用t表示）。渡越时间的长短直接反映了超声波信号传播的距离远近，物体距离模块越远，渡越时间就越长；反之，物体距离模块越近，渡越时间就越短。

4. 距离计算

根据物理学中距离、速度和时间的关系（距离 = 速度 × 时间），我们可以计算出模块与目标物体之间的距离。由于超声波信号是从模块发射出去，碰到物体后再反射回模块，所以超声波实际传播的距离是模块到物体距离的两倍。因此，模块与物体之间的实际距离d的计算公式为：  
<math xmlns="http://www.w3.org/1998/Math/MathML" display="block"><mrow><mrow><mtext>d</mtext></mrow><mrow><mtext>=</mtext></mrow><mfrac><mrow><mrow><mtext>v</mtext></mrow><mrow><mtext>×</mtext></mrow><mrow><mtext>t</mtext></mrow></mrow><mrow><mrow><mtext>t</mtext></mrow></mrow></mfrac></mrow></math>

其中v为超声波在空气中的传播速度，t为渡越时间。在实际应用中，通常会根据环境温度对声速v进行修正，以提高测量的准确性。

## 15.1.2 超声波测距实现

1. <strong>硬件连接</strong>

连接图如下所示：

[![图 15.2 硬件连接图](/img/manual/image185.png)](/img/manual/image185.png)

*图 15.2 硬件连接图*

2. <strong>测距代码实现</strong>

前面讲了超声波模块测距的原理，而我们在写代码的过程中，需要满足的要求是：

- 精确生成 10μs TTL脉冲输出到trig引脚​​

- 精准测量echo引脚高电平时长t​​

- 用t/58将时间转为距离（含25°温度补偿完整公式：<math xmlns="http://www.w3.org/1998/Math/MathML" display="block"><mrow><mrow><mtext>d</mtext></mrow><mrow><mtext>=</mtext></mrow><mfrac><mrow><mrow><mtext>(331.4+0.6</mtext></mrow><mrow><mtext>×</mtext></mrow><mrow><mtext>T)</mtext></mrow><mrow><mtext>×</mtext></mrow><mrow><mtext>t</mtext></mrow></mrow><mrow><mrow><mtext>20000</mtext></mrow></mrow></mfrac></mrow></math>）

注意:一个完整的工作周期至少是50ms。

UltrasonicSensor.cpp核心代码如下：

```cpp
// ...

std::optional<float> UltrasonicSensor::singleMeasure() {
    try {
        // 1. 发送触发脉冲
        gpiod_line_set_value(trigLine_, 1); // 将Trig引脚设为高电平
        std::this_thread::sleep_for(std::chrono::microseconds(10)); // 保持10微秒
        gpiod_line_set_value(trigLine_, 0); // 设回低电平

        // 记录开始等待的时间点，用于超时判断
        auto start_time = std::chrono::steady_clock::now();
        auto timeout = std::chrono::milliseconds(config_.timeoutMs);

        // 2. 等待Echo引脚变为高电平
        while (gpiod_line_get_value(echoLine_) == 0) {
            // 如果等待超时，则返回失败
            if (std::chrono::steady_clock::now() - start_time > timeout) {
                // ...日志记录...
                return std::nullopt;
            }
        }
        
        // 记录Echo变为高电平的精确时间点
        auto pulse_start = std::chrono::steady_clock::now();

        // 3. 等待Echo引脚变回低电平
        while (gpiod_line_get_value(echoLine_) == 1) {
            // 同样进行超时检查
            if (std::chrono::steady_clock::now() - start_time > timeout) {
                // ...日志记录...
                return std::nullopt;
            }
        }
        // 记录Echo变回低电平的精确时间点
        auto pulse_end = std::chrono::steady_clock::now();
        
        // 4. 计算脉冲持续时间
        auto pulse_duration = std::chrono::duration_cast<std::chrono::microseconds>(pulse_end - pulse_start);
        
        // 5. 根据声速和时间计算距离
        float distance = pulse_duration.count() * getSoundSpeed() / 20000.0f;

        // 6. 检查距离是否在有效范围内
        if (distance >= config_.minDistanceCm && 
            distance <= config_.maxDistanceCm) {
            return distance; // 返回有效距离
        }
        // ...日志记录...

    } catch (const std::exception& e) {
        // ...错误处理...
    }
    
    return std::nullopt; // 测量失败
}

// ...
```

具体实现可以去阅读完整的代码，目录结构如下：

```text
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/Test/hc-sr04$ tree
.
├── CMakeLists.txt
├── Doxyfile
├── examples
│   └── hc-sr04_test.cpp
├── include
│   └── UltrasonicSensor.hpp
├── README.md
└── src
    └── UltrasonicSensor.cpp

4 directories, 6 files
```

执行以下指令进行编译：

```text
mkdir build
cd build
cmake ..
make
```

运行：

```text
./hc-sr04_test
```

结果如下：

```text
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/hc-sr04/build$ ./hc-sr04_test
Initializing ultrasonic sensor...Trig: 92, Echo: 91
Ultrasonic sensor initialized successfully: Trig=92, Echo=91
Starting measurement, press Ctrl+C to exit...
Distance: 47.4463 cm (Time: 75ms)
Distance: 47.4463 cm (Time: 75ms)
Distance: 5.59517 cm (Time: 68ms)
Distance: 3.63773 cm (Time: 67ms)
Distance: 47.4463 cm (Time: 75ms)
Distance: 46.8227 cm (Time: 75ms)
Distance: 48.2605 cm (Time: 75ms)
Distance: 3.96685 cm (Time: 68ms)
...
```
