# robot_interfaces_rolling_client

Rolling 发送端 C++ 客户端（M-09 批次、R-OUT-07 状态）。Motion 只传入轨迹窗口；协议的
epoch、sequence、首批确认和结束判断由本包处理。判断全部依据控制器报告的值，本包不推断
控制器内部行为，也不新增接口类型。

| 规则 | 处理 |
| --- | --- |
| 连接 | 有新鲜的 R-OUT-07 状态（不超过 200 ms）、命令发布端已匹配订阅端、控制器为 HOLDING，才发第一批 |
| 首批 | 发出后到 R-OUT-07 报告其结果前不再发送；超过调用方给定的等待时间无结果为 `kStartTimedOut`，不自动重发 |
| epoch / sequence | epoch 取控制器当前值；sequence 在同一 epoch 内严格递增，跨多段轨迹延续 |
| 结束 | 最后一个窗口置 `final`；控制器报 `STOP_COMPLETED` 为 `kCompleted` |
| 停止 | 本段 `stop_reason` 出现其他非 `STOP_NONE` 值为 `kStopped`；首批被拒为 `kRejected`；epoch 变化为 `kInterrupted` |

限位、拼接、提前量、final 末点静止等准入规则由 RT-Control 判断，结果原样放在 `Status` 中。

## 用法

```cpp
#include "robot_interfaces_rolling_client/rolling_sender.hpp"

using namespace robot_interfaces_rolling_client;

RollingSender sender(*node, std::chrono::milliseconds(100));  // 首批结果的等待时间

// 每个规划周期（M-09：30 Hz）
Window window;
window.replace_from = replace_from;  // ROS 时间，不早于当前时刻 + 替换提前量
window.points = points;              // 14 轴，首点 time_from_start = 0
window.final = last_window;          // 最后一个窗口：末点各轴速度为 0
switch (sender.send(window)) {
  case SendResult::kSent: break;
  case SendResult::kNotConnected:      // 控制器未激活或连接未建立：下一周期再发
  case SendResult::kControllerBusy:    // 控制器仍在执行或刹停其他轨迹
  case SendResult::kAwaitingFirstAck:  // 首批结果未到：本窗口未发送，下一周期继续
  case SendResult::kEnded:             // 本段已结束：看 status()，处理后 reset()
    break;
}

// status().phase 到 kCompleted / kStopped / kRejected / kStartTimedOut / kInterrupted 后
sender.reset();  // 开始下一段轨迹前
```

## 注意

- **首批之后看到 STARTING 是正常的**：控制器等到首批的 `replace_from` 才开始运行。
- **`kStartTimedOut` 不代表首批一定没被执行**：结果可能晚于等待时间才到达。之后控制器若仍在
  执行，下一段的第一批会得到 `kControllerBusy`，直到控制器回到 HOLDING。等待时间应明显长于
  状态发布周期（R-OUT-07 50 Hz）。
- **运行中的拒绝**不结束本段：控制器继续执行上一次接受的轨迹，`Status::rejections` 计数，
  `last_rejection` 给出原因。是否中止由调用方决定（停止发送即可，非 final 轨迹按更新超时刹停）。
- `final` 之后仍可发送新窗口替换轨迹；新窗口不是 final 时，控制器恢复更新超时。

`RollingSender` 的全部调用和状态回调由同一个互斥量串行化。协议逻辑在不依赖 ROS 通信的
`RollingStream` 中，测试见 `test/`。
