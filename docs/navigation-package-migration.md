# 导航包迁移

本次从 `c7d53ac` 将导航域独立为 `navigation`。ROS 图中的名称、端点 ID、字段顺序、常量、QoS 和终态语义沿用原契约。下表各类型的包前缀由 `robot_motion_interfaces` 统一改为 `robot_navigation_interfaces`。

| 目录 | 类型 |
|---|---|
| action | `NavigateToPoseTask`、`DetectDroppedBoxes` |
| srv | `AddCurrentLandmark`、`AddLandmark`、`GetLandmark`、`GetSemanticMap`、`RemoveLandmark`、`SetMappingTurnState`、`UpdateLandmark` |
| msg | `Landmark`、`LandmarkArray`、`LocalizationStatus`、`DroppedBoxCandidate` |

端点的完整生产方和消费方见 [Navigation 域视图](../contract/views/navigation.md)。`/odom`、`/tf`、`/rt/base/cmd_vel` 使用 ROS 标准类型。`/navigation/readiness` 使用 `robot_system_interfaces/msg/DomainReadiness`。导航私有工作空间的 `robot_navigation_internal_interfaces` 继续承载域内协议。

## 升级窗口

1. 导航服务端、定位发布者、Autonomy 客户端、视觉地标调用方、导航仪表盘和外部工具锁定同一个经评审的中央提交。检查原 `robot_motion_interfaces` 的引用，仅迁移上表类型。使用抓放或运控状态的进程仍需依赖运控包。
2. 在 `package.xml` 添加 `robot_navigation_interfaces` 依赖。C++ 同步更新 `find_package`、目标依赖、头文件路径和类型命名空间。Python 更新相应的 `from ... import ...`，启动文件、脚本和测试里的 ROS 类型字符串也要更新。
3. 在独立安装目录重新构建，停掉旧版调用两端后一起切换。先核对 `/navigation/navigate_to_pose` 的类型，再验证地标 Service、定位 Topic 和导航 Action 的请求与结果。

```python
from robot_navigation_interfaces.action import NavigateToPoseTask, DetectDroppedBoxes
from robot_navigation_interfaces.srv import AddLandmark, GetSemanticMap
from robot_navigation_interfaces.msg import LocalizationStatus
```

```bash
ros2 interface show robot_navigation_interfaces/action/NavigateToPoseTask
ros2 interface show robot_navigation_interfaces/srv/GetSemanticMap
ros2 interface show robot_navigation_interfaces/msg/LocalizationStatus
```

混用不同包名时，进程可能均正常启动，但同名端点无法匹配。历史录包保留旧类型身份，读取时使用隔离的旧环境，或对数据显式转换。回滚时各调用方和服务端一起切回 `c7d53ac` 及其构建产物。
