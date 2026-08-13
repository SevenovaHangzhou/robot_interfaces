# `robot_interfaces` AI 接口变更执行规约

---
document_type: ai_execution_playbook
repository: https://github.com/SevenovaHangzhou/robot_interfaces.git
default_base_branch: main
primary_registry: contract/endpoints.yaml
wire_schema: "robot_*_interfaces/**/*.{msg,srv,action}"
target_ros_distribution: humble
---

## 0. 本文件的用途

本文件是交给 AI 编码代理执行的操作规约，不是面向人的教程。

当用户要求新增、修改或删除跨域 ROS 2 接口时，AI 必须：

1. 在 `robot_interfaces` 中定位权威定义；
2. 判断接口归属、生产者、消费者和兼容性；
3. 修改所有必须同步的契约文件；
4. 运行生成器、门禁、测试和全包构建；
5. 输出可审查的变更说明、验证结果和升级影响；
6. 不复制 IDL，不允许生产者和消费者长期使用不同 schema。

用户只需要描述业务变更，不需要提前给出文件路径。能从仓库发现的信息由 AI 自行发现，
不要反问用户。

## 1. 同事如何向 AI 提交任务

将本文件与下面的请求一起提供给 AI：

```text
请严格按照《robot_interfaces AI 接口变更执行规约》执行。

操作：新增 / 修改 / 删除
目标：endpoint ID、ROS 名称、类型名，或自然语言描述
需求：希望增加、改变或删除的行为
原因：当前存在的具体问题
已知语义：字段含义、单位、坐标系、时效、成功/失败条件
授权范围：仅本地修改 / 允许推送分支 / 允许创建 PR
```

允许简化为：

```text
按规约修改 N-05：给 LocalizationStatus 增加定位器重初始化代次，
Perception 每次重初始化递增，Motion 和 Autonomy 发现变化后废弃旧缓存。
仅完成本地修改和验证，不要推送。
```

如果用户没有填写某项，AI 先从 `contract/endpoints.yaml`、IDL、调用引用和历史中查找。
只有缺失信息会改变 wire schema 或业务语义时才允许暂停询问。

## 2. 指令优先级和事实源

AI 按以下优先级执行：

1. 用户本次明确要求；
2. 仓库及父目录中的 `AGENTS.md`、`CLAUDE.md` 等代理指令；
3. `contract/endpoints.yaml`：endpoint、类型、生产者、消费者、QoS、约束的唯一注册表；
4. `.msg`、`.srv`、`.action`：wire schema 的唯一事实源；
5. 各包的 `CMakeLists.txt` 和 `package.xml`：构建依赖事实源；
6. `contract/CHANGELOG.md`：契约变更历史；
7. `contract/interface-table.md`、`contract/views/*.md`：生成产物，只能由生成器更新。

不要把本文件中的示例 SHA、旧分支或旧版本当作当前状态。每次执行都必须读取仓库当前状态。

## 3. 不可违反的契约不变量

1. 一个跨域接口只能有一个定义位置。
2. 自定义 IDL 按 endpoint 提供方归档，而不是按调用方归档。
3. 消费域直接依赖提供方的接口包，禁止复制 IDL。
4. 域内接口留在各域的 `*_internal_interfaces`，不得进入公共仓库。
5. ROS 标准类型能直接表达时，不得再包装同义自定义类型；只登记 endpoint 和语义。
6. 一个仓库 commit SHA 表示一次原子契约版本。
7. 即使只是新增字段，也不允许生产者和消费者长期混用不同 SHA。
8. 不手工编辑 `contract/interface-table.md` 或 `contract/views/*.md`。
9. 不猜测字段单位、坐标系、时间戳、QoS、成功条件、失败条件或重试语义。
10. 不用破坏性 Git 命令覆盖用户已有改动，不修改与任务无关的文件。

## 4. 包归属与允许的 schema 依赖

| 业务域 | 自定义接口包 | 组织团队 |
| --- | --- | --- |
| Autonomy / 导航 | `robot_autonomy_interfaces` | `@SevenovaHangzhou/autonomy-interface-owners` |
| Perception / 视觉 | `robot_perception_interfaces` | `@SevenovaHangzhou/perception-interface-owners` |
| Motion | `robot_motion_interfaces` | `@SevenovaHangzhou/motion-interface-owners` |
| RT-Control | `robot_rt_control_interfaces` | `@SevenovaHangzhou/rt-control-interface-owners` |
| 四域共享 | `robot_system_interfaces` | 根据实际生产者和消费者共同评审 |
| 四域共享 | `robot_interfaces_qos` | 根据受影响 endpoint 共同评审 |

允许的 schema 依赖方向：

```text
robot_autonomy_interfaces   -> robot_system_interfaces
robot_perception_interfaces -> robot_system_interfaces
robot_rt_control_interfaces -> robot_system_interfaces
robot_motion_interfaces     -> robot_system_interfaces
                            -> robot_perception_interfaces
                            -> robot_rt_control_interfaces
robot_interfaces_qos        -> rclcpp / rclpy
```

不得为了完成一次改动引入反向依赖或循环依赖。运行时调用方向不等于 schema 依赖方向。

## 5. AI 开始工作前必须执行

### 5.1 确认目标仓库

确认当前目录属于目标仓库：

```bash
git rev-parse --show-toplevel
git remote -v
git branch --show-current
git status --short
```

目标远端应为：

```text
SevenovaHangzhou/robot_interfaces
```

如果不在目标仓库，先定位正确克隆；不能在业务域仓库中创建公共 IDL 副本。

### 5.2 保护现有工作

- 检查工作树是否有未提交改动。
- 未知改动视为用户资产，不得覆盖、回退或顺手格式化。
- 如果用户改动与本任务重叠，先说明冲突再请求处理方式。
- 如果不重叠，保留并绕开它们继续工作。
- 禁止使用 `git reset --hard`、强制 checkout 或其他丢失数据的操作。

### 5.3 确认基线

- 默认从最新 `main` 创建分支。
- 先确认 `main` 上存在 `contract/endpoints.yaml` 和各域接口包。
- 如果默认分支尚未包含当前契约结构，而请求指向其他集成分支，停止并询问正确 base。
- 不要从本文件猜测基线 commit。

推荐分支名：

```text
feat/<endpoint-id>-<short-description>
fix/<endpoint-id>-<short-description>
breaking/<endpoint-id>-<short-description>
```

创建分支前，确保不会覆盖用户现有分支工作：

```bash
git switch main
git pull --ff-only
git switch -c <branch-name>
```

只有用户明确允许网络和分支操作时才执行 pull、push 或创建 PR。

## 6. 变更判定决策树

按顺序回答：

### 6.1 是否跨业务域

只有生产者和消费者跨越 RT-Control、Perception、Motion、Autonomy 域边界的接口，
才进入本仓库。

- 如果只在一个域内部使用：不要修改中央接口包；建议放入对应
  `*_internal_interfaces`。
- 如果跨域：继续下一步。

### 6.2 是否可以直接使用 ROS 标准类型

- 可以：在 `contract/endpoints.yaml` 登记标准类型，并设置 `external_type: true`；
  不创建包装 IDL。
- 不可以：在提供方所属包中创建或修改自定义 IDL。

### 6.3 判定变更类型

| 分类 | 包含情况 | 最低处理要求 |
| --- | --- | --- |
| `新增` | 新 endpoint、新 IDL、新常量 | 更新注册表、IDL/构建配置、changelog、生成文档和测试 |
| `非破坏性` | 已有类型新增字段、新增错误码 | 列出生产者和全部消费者，统一 SHA 升级 |
| `破坏性` | 删除/重命名字段，改类型、单位、坐标系、终态语义、错误语义、包名 | 先有设计决策、迁移与回滚方案，全部受影响域确认，原子发布 |

重命名等价于“删除旧接口 + 新增新接口”，按破坏性变更处理。

如果用户要求破坏性修改，但没有明确旧行为、新行为、迁移、回滚和部署顺序，
AI 不得直接删除或改写 wire schema；应先输出缺失决策并请求确认。

## 7. 从仓库确定影响范围

不要只根据包名猜消费者。必须：

1. 在 `contract/endpoints.yaml` 定位 endpoint ID；
2. 读取 `producer`、`consumers`、`type`、`qos`、`constraint`；
3. 使用 `rg` 搜索类型和 endpoint 的全部引用；
4. 检查 IDL 是否引用其他公共类型；
5. 检查 `member_types` 中的间接载荷；
6. 共享类型变更时，反查所有引用它的 IDL 和 endpoint；
7. `external` 消费者存在时，明确外部集成负责人和升级方式。

建议命令：

```bash
rg -n '<endpoint-id>|<ros-name>|<TypeName>' contract robot_*_interfaces tools
rg -n 'robot_system_interfaces|robot_perception_interfaces|robot_motion_interfaces|robot_rt_control_interfaces' \
  robot_*_interfaces
```

## 8. 每类操作的文件修改规则

### 8.1 新增 endpoint 或自定义类型

必须完成：

1. 为 endpoint 分配稳定且不重复的 ID；
2. 在 `contract/endpoints.yaml` 填写：
   - `id`
   - `ros_name`
   - `kind`
   - `type`
   - `producer`
   - `consumers`
   - `qos`
   - `constraint`
   - 时效、频率、watchdog 等适用字段
3. 自定义类型放入生产域对应包的 `msg/`、`srv/` 或 `action/`；
4. 新 IDL 加入该包 `CMakeLists.txt` 的 `rosidl_generate_interfaces()`；
5. 新增外部类型依赖时，同步更新：
   - `find_package()`
   - `rosidl_generate_interfaces(... DEPENDENCIES ...)`
   - `package.xml`
6. 仅作为其他 IDL 成员、不会独立出现在 ROS graph 的类型，登记到 `member_types`；
7. 在 `contract/CHANGELOG.md` 的 `[Unreleased]` 追加条目；
8. 运行生成器，不手工编辑生成文档；
9. 增加或更新能覆盖新规则的门禁测试。

### 8.2 修改已有接口

必须完成：

1. 先记录原 schema 和原语义；
2. 判断修改是否影响类型哈希、单位、坐标系、时序、QoS、成功/失败或重试行为；
3. 更新对应 IDL；
4. 更新 `contract/endpoints.yaml` 中的约束；
5. 更新 `[Unreleased]` changelog；
6. 更新相关测试；
7. 生成并校验总表和分域视图；
8. 明确所有生产者和消费者必须升级到同一新 SHA。

已有 IDL 只增加内置字段、且未引入新依赖时，通常不修改 `CMakeLists.txt` 和
`package.xml`。AI 必须根据实际依赖判断，不能机械修改。

### 8.3 删除 endpoint、字段或类型

删除属于破坏性变更。执行前必须存在：

- 删除原因；
- 所有生产者和消费者清单；
- 替代接口或明确的退出方案；
- 迁移步骤；
- 回滚方案；
- 同一部署窗口安排；
- 全部受影响域的确认。

得到确认后，AI 必须检查并同步处理：

1. 从 `endpoints` 中删除或替换 endpoint；
2. 将废弃 ROS 名称登记到 `removed_endpoints`，防止重新出现；
3. 删除或修改 IDL；
4. 从 `CMakeLists.txt` 移除已删除 IDL；
5. 从 `member_types` 移除不再使用的成员类型；
6. 仅在确认无其他引用时，移除 `package.xml` 和 CMake 依赖；
7. 更新测试、changelog 和生成文档；
8. 搜索仓库，确保不存在悬空引用或同名替代副本。

## 9. 同一个 PR 必须保持一致的内容

按实际变更检查以下集合：

```text
IDL (.msg/.srv/.action)
对应包 CMakeLists.txt
对应包 package.xml
contract/endpoints.yaml
contract/CHANGELOG.md
contract/interface-table.md          # 生成
contract/views/*.md                  # 生成
tools/ 门禁与测试
必要的 README / 迁移说明
```

禁止把 schema 修改、注册表修改和 changelog 拆成互相不可独立通过 CI 的 PR。

## 10. CHANGELOG 写法

在 `contract/CHANGELOG.md` 的 `[Unreleased]` 下追加：

```markdown
### <新增|非破坏性|破坏性>：<一句话说明>

- **接口**：<endpoint ID、ROS 名称、类型全名、字段>
- **原因**：<触发变更的具体问题，禁止只写“优化”或“完善”>
- **提出人**：@<GitHub 用户名>（<业务域>）
- **影响域**：<生产域、全部消费域、外部调用方及升级要求>
```

破坏性条目还必须说明：若未原子升级，会发生什么具体失败。

## 11. 必须运行的生成和验证

先生成，再校验：

```bash
python3 tools/gen_domain_views.py \
  --master-table contract/interface-table.md

python3 tools/gen_domain_views.py \
  --check \
  --master-table contract/interface-table.md
```

运行全部契约门禁：

```bash
python3 tools/contract_gate.py
python3 tools/error_code_gate.py
python3 tools/changelog_gate.py --base origin/main
python3 -m unittest discover -s tools/tests -p 'test_*.py'
git diff --check
```

在 ROS 2 Humble 环境中全量构建中央仓库：

```bash
source /opt/ros/humble/setup.bash
rosdep install --from-paths . --ignore-src -r -y
colcon build --event-handlers console_direct+
```

规则：

- 中央接口仓库必须全量构建，不能只构建当前部门使用的包。
- 新增系统依赖时运行 `rosdep`；安装系统包需要权限时先征得用户同意。
- 如果环境中没有 ROS 2 Humble、网络或系统依赖，继续完成可运行的门禁，
  并准确列出未运行项和原因。
- 未执行的检查不得写成“通过”。
- 修复验证失败时，只修改与本任务相关的问题；无关既有失败单独报告。

## 12. AI 自检清单

提交结果前逐项确认：

- [ ] 这是跨域接口，不是域内实现细节
- [ ] 标准 ROS 类型不能直接满足需求，或已正确标记 `external_type`
- [ ] IDL 位于生产域所属包
- [ ] endpoint ID、ROS 名称和类型全名一致
- [ ] 生产者和消费者来自注册表证据
- [ ] 单位、坐标系、时间戳、QoS、时效和成功/失败语义明确
- [ ] CMake 与 `package.xml` 依赖闭合
- [ ] IDL 与 `endpoints.yaml` 双向闭合
- [ ] changelog 四要素完整
- [ ] 生成文件由生成器更新且 `--check` 通过
- [ ] 门禁、单元测试和全包构建结果已记录
- [ ] 没有公共 IDL 副本或同名包
- [ ] 没有修改无关文件或覆盖用户改动
- [ ] 所有受影响域都有升级和回滚说明

## 13. Git、PR 与评审规则

### 13.1 本地提交

提交信息建议：

```text
feat(interfaces): add <endpoint or capability>
fix(interfaces): correct <endpoint semantics>
feat(interfaces)!: change <breaking schema>
```

提交前审查：

```bash
git status --short
git diff --stat
git diff --check
git diff
```

### 13.2 外部操作授权

- 用户仅要求修改时：只完成本地文件修改与验证，不自动 push、创建 PR、合并或打 tag。
- 用户明确允许推送时：推送当前功能分支，不直接推送 `main`。
- 用户明确允许创建 PR 时：创建 PR，但不自动合并。
- 合并、发布 tag、修改仓库设置或触发正式部署，需要单独明确授权。

### 13.3 PR 内容

PR 至少包含：

```markdown
## 接口

- Endpoint：
- 类型：
- 提供方：
- 消费方：
- 变更分类：新增 / 非破坏性 / 破坏性

## 原因

<具体问题和证据>

## Schema 与语义

<字段、单位、坐标系、时间、QoS、成功与失败条件>

## 兼容性与迁移

<生产者、消费者、是否允许混跑；默认不允许>

## 发布与回滚

<统一 SHA、升级顺序、部署窗口、回滚 SHA>

## 验证

- [ ] generated views check
- [ ] contract gate
- [ ] error code gate
- [ ] changelog gate
- [ ] tools unit tests
- [ ] ROS 2 Humble full build
```

### 13.4 评审选择

仓库当前最低硬门禁是：`main` 上的 PR 至少两名 reviewer 批准；新提交会使旧批准失效。
AI 每次执行时应读取当前 Ruleset，不能假设规则永远不变。

评审人员选择仍应遵循：

- 普通跨域变更：请求生产域负责人和至少一个直接消费域负责人；
- 多消费域变更：通知所有受影响消费域；
- 破坏性变更：全部受影响消费域必须明确确认；
- 共享系统类型和 QoS：根据实际引用请求所有受影响域。

不要声称当前仓库强制 CODEOWNER 审批；以实时 Ruleset 为准。

### 13.5 commit、push 或创建 PR 前的强制复核

在执行 `git commit`、`git push` 或创建/更新 PR 之前，AI 必须重新阅读本文件，至少复核
第 3、8～13、15 和 17 节，并执行：

1. 对照第 12 节逐项检查当前 diff；
2. 确认改动符合用户授权和变更分类；
3. 确认应生成的文件已经生成，禁止提交过期生成物；
4. 运行第 11 节中所有当前环境可执行的验证；
5. 检查 `git status --short`、`git diff --check` 和待提交 diff；
6. 发现不符合规约时，先修正或明确报告，不得带病提交；
7. 在提交结果中记录实际执行的验证和未执行项。

根目录 `AGENTS.md` 会要求 AI 在任务开始和提交前执行上述复核。即使工具已自动加载
`AGENTS.md`，AI 也必须在提交前重新打开本文件，而不是依赖对早期上下文的记忆。

## 14. 合并、发布和下游升级

接口包按域维护，但版本按整个 `robot_interfaces` 仓库发布。

合并后的标准顺序：

```text
中央 PR 合并
  -> 固化 changelog / 契约版本
  -> 创建人类可读 tag
  -> 记录 tag 对应不可变 commit SHA
  -> 受影响部门分别更新依赖 SHA
  -> 各域编译、测试、接口 smoke test
  -> 在约定窗口统一部署
```

部门工作空间必须引入完整仓库，而不是复制某个包：

```yaml
repositories:
  robot_interfaces:
    type: git
    url: https://github.com/SevenovaHangzhou/robot_interfaces.git
    version: <RELEASE_COMMIT_SHA>
```

部门依赖升级 PR 至少记录：

- 旧 SHA 与新 SHA；
- 跨过的 contract 版本和 changelog；
- 受影响生产/消费节点；
- 本域编译、测试和 smoke test；
- 部署顺序与回滚 SHA。

典型直接依赖参考；业务包仍只声明代码实际使用的包：

| 工作空间 | 常见公共接口直接依赖 |
| --- | --- |
| RT-Control | `robot_rt_control_interfaces`、`robot_system_interfaces`、`robot_interfaces_qos` |
| Perception | `robot_perception_interfaces`、`robot_rt_control_interfaces`、`robot_system_interfaces`、`robot_interfaces_qos` |
| Motion | `robot_motion_interfaces`、`robot_perception_interfaces`、`robot_rt_control_interfaces`、`robot_system_interfaces`、`robot_interfaces_qos` |
| Autonomy | `robot_autonomy_interfaces`、`robot_perception_interfaces`、`robot_motion_interfaces`、`robot_rt_control_interfaces`、`robot_system_interfaces`、`robot_interfaces_qos` |

下游构建建议：

```bash
vcs import src < dependencies.repos
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --packages-up-to <business-package> --event-handlers console_direct+
```

## 15. 必须暂停并向用户确认的情况

仅在以下情况暂停：

1. 无法确定生产域或消费域，且不同选择会改变 schema 归属；
2. 字段单位、坐标系、时间基准、QoS 或成功/失败语义缺失；
3. 用户要求破坏性变更，但没有迁移、回滚或原子发布决策；
4. 工作树中存在与任务重叠的未知改动；
5. 当前默认分支不包含预期契约结构，无法确定正确基线；
6. 需要新增反向依赖、循环依赖或违反包归属；
7. 需要超出用户授权执行 push、PR、合并、tag、仓库设置或部署；
8. 实际代码或注册表证据互相矛盾，无法安全选择。

不要因为能从仓库查到的文件路径、包名、endpoint ID、现有消费者或构建命令而暂停询问。

## 16. AI 的最终交付格式

完成后必须按下面结构报告：

```markdown
## 结果

<已实现 / 因明确条件阻塞>

## 变更判定

- 操作：新增 / 修改 / 删除
- 分类：新增 / 非破坏性 / 破坏性
- Endpoint：
- 类型：
- 生产者：
- 消费者：

## 修改文件

- <path>：<修改原因>

## 验证

- PASS：<实际执行的命令>
- FAIL：<失败和原因>
- NOT RUN：<未运行项和原因>

## 兼容性与发布

- 是否允许新旧 SHA 混跑：否，除非契约明确证明并经批准
- 受影响域：
- 升级顺序：
- 回滚方式：

## 待人工动作

- <评审、push、PR、tag、部署等尚未授权或尚未执行的动作>
```

### 16.1 必须主动提示下一步

最终回复不能只写“已完成”。AI 必须根据当前实际阶段，主动告诉用户紧接着要做什么：

| 当前阶段 | 必须提示的下一步 |
| --- | --- |
| 仅完成本地修改 | 是否需要 AI commit、push 和创建 PR；给出建议分支名和提交信息 |
| 已 commit、尚未 push | 建议推送目标分支，并说明尚未执行的远端操作 |
| 已 push | 给出 PR 链接，或提示创建 PR，并列出应邀请的生产域和消费域 reviewer |
| PR 已创建 | 提示等待 CI、取得两名批准；有新提交时需要重新批准 |
| PR 已合并 | 提示固化版本/tag、记录 SHA，并为受影响部门创建依赖升级 PR |
| 下游已升级 | 提示跨域 smoke test、统一部署窗口和回滚 SHA |
| 存在阻塞 | 明确由谁提供什么决策或权限，解除后从哪一步继续 |

提示必须具体到责任人/业务域、目标分支或 PR、所需验证和授权边界。AI 不得擅自执行尚未
授权的合并、tag、下游改仓或部署，但必须明确提出这些后续动作。

## 17. 完成定义

只有同时满足以下条件，AI 才能说“接口修改完成”：

1. 请求的 schema 和语义已正确实现；
2. 注册表、IDL、构建元数据、changelog 和生成文档一致；
3. 所有可运行门禁和测试通过；
4. ROS 环境可用时全包构建通过；
5. 兼容性、生产者、消费者和升级顺序已说明；
6. 没有未解释的失败、未提交生成文件或无关改动；
7. 未执行的外部动作被明确列为待人工动作。

如果任一项不满足，必须准确报告“部分完成”或“阻塞”，不得用模糊措辞宣称完成。
