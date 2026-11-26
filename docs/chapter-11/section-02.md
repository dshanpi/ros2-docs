---
title: "11.2 PWM控制"
sidebar_label: "11.2 PWM控制"
slug: /chapter-11/section-02/
---

## 11.2.1 PWM硬件知识

1. <strong>PWM的基本定义</strong>

PWM（Pulse Width Modulation，脉冲宽度调制）是一种通过控制数字信号“高电平”持续时间的方法，实现对模拟设备功率输出的精准调节。其原理是：在一个固定周期内，通过改变高电平所占的比例（即占空比），间接控制能量输出。

PWM 信号虽为数字形式（只有高低电平），但当周期足够短时，能在视觉、电机或电路层面近似模拟连续的模拟电压输出。

2. <strong>PWM的工作原理</strong>

PWM 信号具有以下三个核心参数：

<table>
<tbody>
<tr>
<th scope="col"><strong>参数</strong></th>
<th scope="col"><strong>含义</strong></th>
</tr>
<tr>
<td>周期（Period）</td>
<td>一个完整波形的持续时间</td>
</tr>
<tr>
<td>占空比（Duty Cycle）</td>
<td>高电平时间与周期的比值，控制“输出强度”</td>
</tr>
<tr>
<td>频率（Frequency</td>
<td>周期的倒数，决定了波形切换速度，影响平滑程度</td>
</tr>
</tbody>
</table>

示意图如下：

[![图 13-2](/img/manual/image120.png)](/img/manual/image120.png)

*图 13-2*

在一个 PWM 信号中，每一个完整的脉冲都由“高电平”和“低电平”组成，这段完整的时间称为<strong>周期（T）</strong>。如果每秒钟有多少个周期，就是<strong>频率（f）</strong>，即 f = 1 / T。

在周期内，高电平持续的时间叫做<strong>脉宽时间</strong>。<strong>占空比</strong>就是高电平时间占整个周期时间的比例。例如：

```bash
如果一个周期是 10 毫秒，高电平持续了 8 毫秒，那么占空比就是：
8ms / 10ms = 80%，
这就是一个占空比为 80% 的 PWM 信号。
```

PWM 就是脉冲宽度调制，它的核心思想就是：通过调节高电平所占的比例（占空比），来控制输出的能量大小。

比如（当然还需要考虑极性问题）：

- 占空比高，LED 就更亮、电机转得更快；

- 占空比低，LED 就变暗、电机转慢或停止。

3. <strong>PWM的极性</strong>

PWM 信号的极性决定了“高电平”和“低电平”的含义：

- 正极性（normal polarity）：默认高电平表示“有效”，占空比表示高电平持续时间。

- 反极性（inversed polarity）：高电平表示“关闭”，低电平才“有效”。

## 11.2.2 Linux下PWM操作接口

在 Linux 系统中，PWM（脉宽调制）接口通常通过 sysfs 文件系统进行访问和控制，路径位于 /sys/class/pwm/。Linux 将 PWM 设备抽象为文件，用户可通过“读写文件”的方式完成对 PWM 信号的配置和控制。

1. <strong>基本概念说明</strong>

进入 /sys/class/pwm/ 这个路径，经常看到一些接口名称，如下表：

<table>
<tbody>
<tr>
<th scope="col"><strong>接口名称</strong></th>
<th scope="col"><strong>功能说明</strong></th>
</tr>
<tr>
<td>pwmchipX</td>
<td>表示第 X 个 PWM 控制器设备</td>
</tr>
<tr>
<td>npwm</td>
<td>该 PWM 控制器支持的通道数</td>
</tr>
<tr>
<td>export</td>
<td>启用一个 PWM 通道（将其导出为可配置状态）</td>
</tr>
<tr>
<td>unexport</td>
<td>禁用一个 PWM 通道（释放资源）</td>
</tr>
<tr>
<td>pwmX</td>
<td>表示导出的第 X 个 PWM 通道的控制目录</td>
</tr>
</tbody>
</table>

例如：/sys/class/pwm/pwmchip0/pwm0/ 表示 pwmchip0 控制器下的第 0 通道。

2. <strong>操作步骤</strong>

以下操作以控制 pwmchip0 的第 0 通道为例：

1. <strong>导出pwm通道</strong>

```bash
echo 0 > /sys/class/pwm/pwmchip0/export
```

执行此命令后，将在 /sys/class/pwm/pwmchip0/ 目录下生成名为 pwm0 的目录。

2. <strong>设置pwm周期</strong>

```bash
echo 1000000 > /sys/class/pwm/pwmchip0/pwm0/period
```

周期单位为纳秒（ns），例如 1000000ns 表示 1ms 的周期（即 1kHz 频率）。

3. <strong>设置占空比</strong>

```bash
echo 500000 > /sys/class/pwm/pwmchip0/pwm0/duty_cycle
```

占空比单位也为纳秒（ns），必须小于周期值。上例表示占空比为 50%。

4. <strong>启用pwm输出</strong>

```bash
echo 1 > /sys/class/pwm/pwmchip0/pwm0/enable
```

写入 1 表示启用 PWM，0 表示关闭。

3. <strong>PWM控制LED实现呼吸灯</strong>

k1-x-MUSE-Pi-Pro主板的扩展引脚中并没有PWM控制引脚，但是我们可以通过GPIO来模拟PWM输出。后续将使用python来控制gpio引脚，先安装gpiozero库，具体操作步骤如下：

1. 安装gpiozero库

```bash
sudo apt install python3-gpiozero
```

2. 赋予权限

```bash
sudo chmod a+rw /dev/gpiochip*
```

3. 执行pinout，查看引脚

```bash
pinout
```

结果如下图所示：

[![图 13-3](/img/manual/image121.png)](/img/manual/image121.png)

*图 13-3*

接下来，编写一个python代码来控制gpio74引脚，模拟pwm信号实现呼吸灯。

pwm\_breath\_led.py示例代码如下：

```python
from gpiozero.pins.lgpio import LGPIOFactory
from gpiozero import Device, LED
import time
import signal
import sys

# 常量定义
DEFAULT_PIN = 70
DEFAULT_FREQ = 100  # Hz
DEFAULT_STEP = 1    # 每次变化占空比的步长
DEFAULT_DUTY = 0    # 初始占空比为0，表示灯全灭

class SoftwarePWM:
    def __init__(self, pin=DEFAULT_PIN, frequency=DEFAULT_FREQ, duty_cycle=DEFAULT_DUTY):
        """初始化软件PWM（呼吸灯）"""
        if not isinstance(pin, int) or pin < 0:
            raise ValueError("引脚号必须是正整数")
        if frequency <= 0 or frequency > 1000:
            raise ValueError("频率应在1-1000Hz范围内")
        if duty_cycle < 0 or duty_cycle > 100:
            raise ValueError("占空比应在0-100%范围内")

        Device.pin_factory = LGPIOFactory()
        self.led = LED(pin)
        self.set_params(frequency, duty_cycle)
        self.running = False

        # 注册信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def set_params(self, frequency=None, duty_cycle=None):
        """动态设置PWM参数"""
        if frequency is not None:
            self.frequency = frequency
            self.period = 1.0 / frequency
        if duty_cycle is not None:
            self.duty_cycle = max(0, min(100, duty_cycle))

    def _signal_handler(self, signum, frame):
        """处理终止信号"""
        self.stop()
        sys.exit(0)

    def start(self):
        """启动呼吸灯效果"""
        self.running = True
        print(f"启动呼吸灯: 引脚{self.led.pin}, 基础频率 {self.frequency}Hz")

        try:
            step = DEFAULT_STEP
            direction = 1  # 1表示变亮，-1表示变暗

            while self.running:
                # PWM控制：高电平时间 / 低电平时间
                high_time = (self.duty_cycle / 100) * self.period
                low_time = self.period - high_time

                self.led.on()
                time.sleep(high_time)
                self.led.off()
                time.sleep(low_time)

                # 调整占空比实现呼吸
                self.duty_cycle += direction * step
                if self.duty_cycle >= 100:
                    self.duty_cycle = 100
                    direction = -1
                elif self.duty_cycle <= 0:
                    self.duty_cycle = 0
                    direction = 1

        except Exception as e:
            self.stop()
            raise RuntimeError(f"呼吸灯运行时错误: {str(e)}")

    def stop(self):
        """停止PWM并释放资源"""
        if self.running:
            self.running = False
            self.led.off()
            self.led.close()
            print("PWM已停止")

def main():
    try:
        pwm = SoftwarePWM(
            pin=DEFAULT_PIN,
            frequency=DEFAULT_FREQ,
            duty_cycle=DEFAULT_DUTY
        )
        pwm.start()
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

执行以下指令编译、运行：

```bash
python3 pwm_breath_led.py
```
