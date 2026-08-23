# 面向强震动产品的两阶段处理窗质量审计方法

## 摘要

强震动记录的处理窗决定了参与峰值、能量和反应谱计算的波形范围。固定时长便于资料归档和批量生产，但同一窗长在不同资料库中可能对应完全不同的产品保留水平。本文选取 InstanceGM 和 K-NET 的 44,674 条三分量加速度记录开展主分析，并以 6,107 条 PNWAccelerometers 记录进行外部检验。全部波形统一采用线性去趋势和 0.1 Hz 四阶零相位高通滤波。所提出的离线质量审计分为两级：第一级从不依赖目录到时的候选窗中选取最短合格窗，要求各分量峰值保留率的最小值不低于 0.99、三分量平方运动积分保留率不低于 0.95，且各分量全记录峰值时刻均位于窗内；第二级计算 0.2、1.0 和 3.0 s 周期的 5% 阻尼伪谱加速度（PSA），要求最不利分量的 PSA 保留率均不低于 0.95。初选窗未通过反应谱复核时，依次改用带前后延拓的 1%－99% 累积能量窗和全记录。起点前含 2 s、起点后含 40 s 的固定窗在 InstanceGM、K-NET 和 PNW 中的不稳定率分别为 67.55%、4.15% 和 86.56%。第一级选窗将主数据集的中位窗长缩短至 34.25 s，但仍有 37.16% 的记录在 3.0 s 周期未达到 PSA 保留要求。经过第二级复核，主数据集中 60.08% 的记录直接采用初选窗，19.96% 改用能量百分位窗，19.96% 保留全记录，最终中位窗长为 60.00 s。PNW 中三类比例分别为 34.42%、48.03% 和 17.55%，中位窗长为 150.01 s。1,521 条固定分层样本的端到端试验显示，0.05 和 0.10 Hz 设置下的全记录采用率分别为 22.81% 和 21.43%。该方法给出了处理窗、产品保留量和采用理由之间可追溯的对应关系，可用于强震动产品离线生产中的固定窗风险检查和保守选窗。

**关键词：** 强震动记录；处理窗；质量控制；伪谱加速度；反应谱；产品保留率

## 1 引言

强震动记录是地震动模型、震害评估、结构抗震分析和震后工程复核的基础资料。台网取得原始记录后，还需完成仪器校正、基线处理、滤波、截窗和产品计算。峰值加速度、速度、位移、持时、傅里叶谱和反应谱均受这一处理链影响。已有研究对基线漂移、低频噪声和滤波参数进行了系统讨论，指出处理条件必须与结果一并记录（Boore, 2001；Boore and Bommer, 2005；Douglas and Boore, 2011；Boore et al., 2012）。处理窗确定了产品计算实际使用的样本范围，同样属于产品质量控制的一部分。

强震动资料的自动处理已经形成多种业务系统。美国地质调查局开发的 PRISM 可生成校正波形、反应谱和地震动强度指标，并提供记录复核界面（Jones et al., 2017）；gmprocess 面向近实时地震动处理和产品计算（Thompson et al., 2025）。欧洲 RRSM 与 ESM 分别提供快速强震参数和经过质量控制的工程强震动资料（Cauzzi et al., 2016；Luzi et al., 2016）。国内地震预警台网的强震动数据处理系统也覆盖 PGA、PGV、PGD、烈度、持时和反应谱等产品（Liu et al., 2025）。Inocente and Maruyama (2026) 将 P 波识别与高通截止频率选择纳入自动处理。此类系统需要明确记录每一步采用的参数及质量状态，才能在资料更新和产品复算时追溯结果。

已有选窗研究多从具体分析任务出发。Kishida et al. (2016) 面向 NGA-West2 傅里叶幅值谱提出半自动选窗流程；Perron et al. (2018) 综合震相到时、震源持时、传播时间和累积能量，确定 P 波、S 波、尾波及噪声窗；Ryu et al. (2025) 比较不同强震动预处理方法，并采用前后各延拓 15 s 的 1%－99% 归一化 Arias 强度区间作为信号窗。这些方法解决了有效信号范围的定位问题。批量产品生产还需要回答一个更直接的问题：某个候选窗是否完整保留了准备发布的地震动产品。

公开资料集中广泛采用固定窗，主要原因是记录长度统一后便于索引、批量读取和模型训练。固定窗通常围绕原资料集的用途设计；将记录用于新的工程产品时，还需重新检查产品完整性。震源持时、传播路径、盆地效应、触发与停止记录逻辑以及可用尾波长度都会改变窗外运动的比例。跨资料库直接沿用同一窗长，容易在部分记录中截去后续运动，也可能在另一批记录中保留大量无用样本。

本文把处理窗选择定义为离线产品质量审计。资料归档和批量产品生成时，全记录已经可用，因而可以把候选窗内产品与全记录产品逐条比较。候选窗先通过分量峰值和平方运动积分检查，再接受反应谱复核。输出包括最终窗、各项保留率、候选来源和是否采用全记录。图 1 给出了两阶段审计流程。

研究围绕四个问题展开：不同资料库中的固定窗稳定性相差多大；峰值与能量检查之后还剩多少周期相关误差；达到给定 PSA 保留要求需要付出多大的窗长和全记录采用代价；主要结论能否在另一高通截止频率和外部资料库中保持。本文据此建立面向强震动产品离线生产的处理窗质量控制方法。

## 2 数据与方法

### 2.1 主数据集及记录筛选

主分析采用 INSTANCE 数据体系中的 InstanceGM 和日本防灾科学技术研究所（NIED）发布的 K-NET 记录（数据来源见“数据和资源”）。INSTANCE 汇集了意大利地震波形及配套元数据（Michelini et al., 2021）；K-NET 是日本全国强震动观测体系的重要组成部分（Aoi et al., 2004；Okada et al., 2004）。

初始工作列表只保留加速度记录，共 45,652 条，其中 InstanceGM 23,533 条，K-NET 元数据记录 22,119 条。产品计算前逐条加载波形。InstanceGM 全部加载成功；转换后的 K-NET 波形归档有 978 条元数据记录找不到对应波形键，最终可分析 K-NET 记录为 21,141 条。这 978 条记录只计入资料可用性统计，不进入任何比例的分母。主分析实际包含 44,674 条加速度记录（表 1）。

InstanceGM 记录来自 8,811 个事件和 299 个台站，K-NET 记录来自 1,528 个事件和 917 个台站。两者中位采样率均为 100 Hz，中位记录时长分别为 120.00 s 和 119.00 s。K-NET 记录时长的 5% 和 95% 分位数分别为 60.00 s 和 120.00 s。本文只比较同一记录内候选窗与全记录的比例，恒定的幅值单位换算不会改变保留率。

为观察震级构成，记录分为 M<3、3≤M<4 和 M≥4 三组。分组只用于统计和固定样本抽取，不参与选窗。InstanceGM 三组记录数依次为 9,000、9,000 和 5,533；K-NET 依次为 21、5,647 和 15,473。各组资料见表 2。

### 2.2 外部检验数据

外部检验采用 SeisBench 提供的 PNWAccelerometers（Ni et al., 2023；数据来源见“数据和资源”）。本次检验共纳入 6,107 条三分量加速度记录，涉及 3,433 个事件和 168 个台站，中位记录时长为 150.01 s，中位震级为 1.83。三个震级组分别有 5,563、468 和 76 条记录。PNW 的事件构成和归档方式与主数据集不同，所有结果单独报告，不并入 44,674 条主分母。

### 2.3 统一预处理与波形特征

所有记录均先进行线性去趋势，再采用 0.1 Hz 截止频率的四阶 Butterworth 零相位高通滤波。计算保留原采样率，不进行重采样，各资料库均在相同预处理条件下比较。滤波灵敏度试验从“资料库－震级组”中各抽取不超过 300 条记录，样本总数为 1,521 条；0.05 和 0.10 Hz 两种设置使用完全相同的记录，并从特征提取开始重跑全部流程。

记第 \(c\) 个分量的加速度为 \(a_c(t)\)，三分量合成幅值写为

\[
v(t)=\left[\sum_{c=1}^{3}a_c^2(t)\right]^{1/2}。
\]

对 \(v^2(t)\) 积分并除以全记录积分，得到归一化累积平方运动曲线。其 1% 和 95% 时刻分别作为能量起点和能量终点。阈值起点由记录前 3 s 的中位绝对偏差估计噪声尺度，连续 0.1 s 超过 6 倍稳健标准差时触发。能量起点与阈值起点中较早的有限值作为特征起点。

### 2.4 候选处理窗

每条记录构造以下候选窗：以特征起点为基准、起点前保留 2 s、起点后分别保留 20、40、60 和 90 s 的固定窗；以能量起点为基准的 40 s 窗；从特征起点前 2 s 延伸至 95% 能量时刻后 3 s 的自适应窗；从 1% 到 99% 累积平方运动时刻并向前后各扩展 15 s 的能量百分位窗；以及全记录。所有边界均限制在实际可用样本范围内。另以目录 P 到时构造起点后 40 s 的对照窗，主选窗不使用目录到时。

能量百分位窗与 Arias 强度的累积形式一致。本文对三分量平方和积分，常数因子不影响百分位时刻（Arias, 1970）。在信噪比较低的长记录中，背景噪声也会进入累积曲线，因而该窗被放在第二级备选位置，并接受同样的产品检查。

### 2.5 第一级：分量峰值与能量审计

设候选窗为 \(I\)，全记录为 \(F\)。分量峰值保留率定义为

\[
r_A(I)=\min_c\frac{\max_{t\in I}|a_c(t)|}{\max_{t\in F}|a_c(t)|}。
\]

三分量平方运动积分保留率为

\[
r_E(I)=\frac{\sum_c\int_I a_c^2(t)\,dt}{\sum_c\int_F a_c^2(t)\,dt}。
\]

候选窗同时满足 \(r_A\geq0.99\)、\(r_E\geq0.95\)，且三个非零分量的全记录绝对峰值时刻都在窗内，方可通过第一级审计。取三个分量比值中的最小值，可以防止强分量掩盖其他分量的峰值损失。0.99 和 0.95 是预先设定的质量控制参数。主规则从不含目录 P 信息的合格候选中选取时长最短者；没有非全记录候选通过时采用全记录。

### 2.6 第二级：反应谱复核

峰值和积分能量不能直接约束单自由度振子的最大响应。本文进一步计算 0.2、1.0 和 3.0 s 周期的 5% 阻尼伪谱加速度。相对位移方程为

\[
\ddot u_c+2\zeta\omega\dot u_c+\omega^2u_c=-a_c(t)，
\qquad PSA_c(T)=\omega^2\max_t|u_c(t)|，
\]

其中 \(\zeta=0.05\)，\(\omega=2\pi/T\)。连续系统通过双线性变换离散。每段输入结束后继续计算 5 个周期的零输入自由振动，避免处理窗边界提前截断振子响应。

周期 \(T\) 下的 PSA 保留率取最不利分量：

\[
r_S(T,I)=\min_c\frac{PSA_c(T,I)}{PSA_c(T,F)}。
\]

初选窗在三个周期均满足 \(r_S\geq0.95\) 时直接采用。若有任一周期未通过，则改用能量百分位窗重新计算；能量百分位窗仍未通过时采用全记录。最终形成“初选窗－能量百分位窗－全记录”三类输出。三个受检周期最终均达标是规则本身的质量保证，评价重点是达到这一要求所需的升级比例、全记录比例和窗长。

### 2.7 评价方法

固定窗在峰值、能量或峰值时刻任一检查中未通过，记为不稳定。PSA 保留率低于 0.95，记为相应周期的谱产品未保留。结果按资料库和震级组报告，并统计三类输出比例、中位窗长和 75% 分位窗长。另将谱阈值改为 0.90 和 0.98，考察质量要求与处理成本的关系。

PNW 的信噪比分析使用目录 P、S 到时划分诊断区间，排序和分组均在合并选窗结果之前完成。噪声均方根取 P 到时前 22～2 s；信号均方根取 P 到时至 P+20 s 与 S+20 s 中较晚的时刻。按 3 dB 和 10 dB 分组，用于比较弱信号和强信号记录的选窗结果。

## 3 结果

### 3.1 固定窗稳定性随资料库显著变化

图 2 给出了固定窗时长试验。特征起点后分别保留 20、40、60 和 90 s 时，InstanceGM 的不稳定率依次为 94.36%、67.55%、50.10% 和 32.90%；K-NET 依次为 47.30%、4.15%、0.84% 和 0.15%；PNW 依次为 91.01%、86.56%、82.71% 和 75.90%。增加窗长能够降低不稳定率，但三套资料的下降速度和剩余风险差别很大。

以起点后 40 s 的固定窗为例，InstanceGM 有 15,896 条记录未通过，其中 15,847 条能量不足，6,269 条至少有一个分量的全记录峰值位于窗外，6,170 条分量峰值保留率不足。K-NET 共有 877 条失败记录，全部存在能量不足，46 条遗漏分量峰值时刻。PNW 有 5,286 条失败记录，全部存在能量不足，4,980 条遗漏分量峰值时刻。同一记录可同时具有多种失败原因，上述数量不能相加。

### 3.2 峰值与能量合格后仍存在长周期损失

第一级规则仅有 37 条 InstanceGM、1 条 PNW 采用全记录，K-NET 没有记录在此阶段采用全记录。InstanceGM、K-NET 和 PNW 的初选窗中位时长分别为 62.00、22.00 和 142.37 s，主数据集合并中位数为 34.25 s。

初选窗在峰值和能量上均已通过，反应谱仍表现出明显的周期差异。主数据集在 0.2、1.0 和 3.0 s 周期的 PSA 保留失败率分别为 0.11%、7.59% 和 37.16%；42 s 固定窗的对应比例为 11.85%、26.80% 和 58.30%。图 4 对比了固定窗、初选窗和最终处理窗。3.0 s 结果说明，峰值与总能量合格不能代替长周期产品复核。

### 3.3 最终分流与处理窗时长

图 3 给出了最终分流和窗长。主数据集中，60.08% 的记录直接采用初选窗，19.96% 改用能量百分位窗，19.96% 采用全记录；最终中位窗长为 60.00 s，75% 分位数为 110.23 s。三套资料的分流比例列于表 3。

InstanceGM 三类比例分别为 69.26%、24.97% 和 5.77%，最终中位窗长为 92.00 s。K-NET 分别为 49.86%、14.38% 和 35.76%，中位窗长为 44.81 s。PNW 分别为 34.42%、48.03% 和 17.55%，中位数和 75% 分位数均为 150.01 s。PNW 至少一半记录需要保留至现有全记录长度，原因是较短候选在受检周期上不能满足保留要求。

谱阈值从 0.90 提高到 0.95 和 0.98 后，主数据集采用全记录的比例从 18.28% 增至 19.96% 和 21.65%，初选窗直接采用率从 66.01% 降至 60.08% 和 53.13%。前两种阈值下的中位窗长均为 60.00 s，0.98 阈值下增至 65.18 s。PNW 的全记录比例分别为 16.70%、17.55% 和 18.39%。阈值提高主要增加了能量百分位窗的使用，并使部分边界记录转为全记录。

### 3.4 滤波灵敏度与外部资料诊断

图 5 给出了端到端滤波灵敏度。1,521 条相同记录在 0.05 和 0.10 Hz 下重新提取特征、生成候选并完成两级审计。3.0 s 初选窗失败率分别为 40.30% 和 39.51%，最终全记录比例分别为 22.81% 和 21.43%，中位窗长分别为 69.00 和 66.59 s。InstanceGM 的全记录比例为 5.44% 和 6.00%，K-NET 为 47.99% 和 43.80%。两种滤波设置下，资料库差异和第二级反应谱复核的必要性均保持不变。

图 6 给出了 PNW 的信噪比分组结果。小于 3 dB、3～10 dB 和不低于 10 dB 的记录数分别为 1,175、2,223 和 2,709。三组固定窗不稳定率分别为 99.15%、99.69% 和 70.32%，3.0 s 初选窗失败率分别为 50.81%、63.34% 和 66.67%，最终采用全记录的比例分别为 0.68%、0.76% 和 38.65%。高信噪比组的全记录比例最高，外部资料中的长窗需求在强信号记录中同样存在。三组中位震级分别为 1.49、1.74 和 2.22；区分震级、持时和传播路径的独立作用需要进一步分层。

## 4 讨论

### 4.1 固定窗便于公开资料使用，但仍需产品审计

固定窗解决了资料形状统一的问题。统一长度便于索引、并行读取和机器学习，也便于记录原始提取规则。产品是否完整取决于窗内保留的运动。InstanceGM 和 PNW 中相当一部分记录在起点后 40 s 仍有产品相关运动，K-NET 多数记录在相同时长内已经通过第一级检查。若统一延长到 90 s，InstanceGM 和 PNW 仍分别有 32.90% 和 75.90% 的记录不稳定，同时 K-NET 中大量记录被不必要地延长。

资料库差异可能来自多种环节。事件截取规则决定前后可用时长，仪器触发和停止记录条件决定尾波范围，震源持时、传播距离、盆地效应和晚到震相改变实际运动长度。弱记录中的背景噪声也会影响累积能量终点，这是能量选窗已有的使用边界（Perron et al., 2018；Ryu et al., 2025）。本文测量这些因素共同作用后的产品保留结果；区分各机制的独立贡献还需结合资料库的采集、触发和截取元数据。

### 4.2 反应谱复核的工程含义

分量峰值和平方运动积分分别描述极值与总量，单自由度振子的最大响应还与运动的时间组织和频率成分有关。第一级之后仍有 37.16% 的主数据记录在 3.0 s 周期损失超过 5%，两类判据之间存在实质差别。第二级直接检查准备生产的谱产品，从而避免用峰值或能量间接替代反应谱。

最终处理窗在三个受检周期的失败率为 0，这一结果由全记录回退规则直接保证，不涉及独立模型的预测精度。方法的实际代价体现在三类分流比例和最终窗长。当前保证只覆盖 0.1 Hz 预处理、5% 阻尼、0.2～3.0 s 周期和 0.95 保留阈值。若产品包含更长周期、其他阻尼比或傅里叶谱，应把相应指标直接加入第二级审计。

### 4.3 在产品生产中的使用方式

两阶段审计适合放在波形读取之后、产品表生成之前。每条记录输出候选来源、窗起止样本、分量峰值保留率、能量保留率、峰值时刻状态、三个周期的 PSA 保留率、最终分流以及预处理参数。业务系统可把这些字段与产品共同归档。资料更新后可以用相同参数复算，采用全记录的记录也能按失败原因单独检查。

PNW 的中位最终窗长等于现有记录长度，说明紧凑选窗不适合该资料中相当一部分记录和当前产品目标。在这类记录上，保留全记录是满足当前产品阈值的审计结果；统一压缩窗长会造成未报告的谱值损失。

本文把现有全记录产品作为参照。全记录中可能含有背景噪声、次生事件或记录异常，这些内容也可能改变谱值。信噪比分组只检查了其中一个因素。后续业务试验可把本方法与成熟的记录质量筛查结合（Douglas, 2003；Bellagamba et al., 2019），并选取人工复核样本核对分流结果。本文已经验证产品保留和记录分流，尚未测量操作人员的实际耗时变化。

## 5 结论

InstanceGM、K-NET 和 PNWAccelerometers 对固定处理窗表现出显著不同的产品稳定性。特征起点后 40 s 的固定窗不稳定率从 K-NET 的 4.15% 到 PNW 的 86.56% 不等，固定时长不能直接作为跨资料库质量标准。

第一级峰值－能量审计能够生成较紧凑的候选窗，主数据集中位窗长为 34.25 s；其中仍有 37.16% 的记录在 3.0 s 周期未达到 0.95 的 PSA 保留率。第二级反应谱复核据此延长处理窗。0.95 阈值下，主数据集中 60.08% 采用初选窗，19.96% 采用能量百分位窗，19.96% 采用全记录。

该方法为强震动产品离线生产提供了记录级处理窗质量审计。最终结果同时给出处理窗、保留指标和采用理由，可用于固定窗风险检查、谱产品完整性控制和资料复算追溯。

## 数据和资源

InstanceGM/INSTANCE 数据通过 https://doi.org/10.13127/INSTANCE 获取，访问日期为 2026 年 6 月 16 日。K-NET 数据通过 NIED 的 https://doi.org/10.17598/NIED.0004 获取，访问日期为 2026 年 6 月 16 日。PNWAccelerometers 通过 SeisBench 数据接口获取，访问日期为 2026 年 6 月 18 日；资料说明见 Ni et al. (2023)，https://doi.org/10.26443/seismica.v2i1.368。

代码、测试、派生审计表、图件源数据和复现命令归档于 https://github.com/zhouhaoyiu/strong-motion-product-window-qc/releases/tag/v0.2.0，最后访问时间为 2026 年 7 月。仓库不重新分发原始波形，原始资料仍遵循数据提供方的使用条款。源代码采用 MIT License，派生表格、图件和文档采用 CC BY 4.0。研究过程中使用 OpenAI Codex 桌面应用 26.707.31428 版辅助程序编辑、一致性检查和语言校订，文中数值均由归档程序生成。作者检查了程序和文中数值与归档输出的对应关系，并审查了图件、科学解释和最终文字。

## 致谢

感谢 INSTANCE、NIED K-NET、PNWAccelerometers 和 SeisBench 团队维护并开放相关波形资料。本研究未获得外部基金资助。

## 利益冲突声明

作者声明不存在利益冲突。

## 参考文献

1. Aoi, S., Kunugi, T., and Fujiwara, H. (2004). Strong-motion seismograph network operated by NIED: K-NET and KiK-net. *Journal of Japan Association for Earthquake Engineering*, 4(3), 65-74. doi: 10.5610/jaee.4.3_65

2. Arias, A. (1970). A measure of earthquake intensity. In R. J. Hansen (Ed.), *Seismic Design for Nuclear Power Plants* (pp. 438-483). MIT Press.

3. Bellagamba, X., Lee, R., and Bradley, B. A. (2019). A neural network for automated quality screening of ground motion records from small magnitude earthquakes. *Earthquake Spectra*, 35(4), 1637-1661. doi: 10.1193/122118EQS292M

4. Boore, D. M. (2001). Effect of baseline corrections on displacements and response spectra for several recordings of the 1999 Chi-Chi, Taiwan, earthquake. *Bulletin of the Seismological Society of America*, 91(5), 1199-1211. doi: 10.1785/0120000703

5. Boore, D. M., Azari Sisi, A., and Akkar, S. (2012). Using pad-stripped acausally filtered strong-motion data. *Bulletin of the Seismological Society of America*, 102(2), 751-760. doi: 10.1785/0120110222

6. Boore, D. M., and Bommer, J. J. (2005). Processing of strong-motion accelerograms: needs, options and consequences. *Soil Dynamics and Earthquake Engineering*, 25(2), 93-115. doi: 10.1016/j.soildyn.2004.10.007

7. Cauzzi, C., Sleeman, R., Clinton, J., Ballesta, J. D., Galanis, O., and Kastli, P. (2016). Introducing the European Rapid Raw Strong-Motion database. *Seismological Research Letters*, 87(4), 977-986. doi: 10.1785/0220150271

8. Douglas, J. (2003). What is a poor quality strong-motion record? *Bulletin of Earthquake Engineering*, 1(1), 141-156. doi: 10.1023/A:1024861528201

9. Douglas, J., and Boore, D. M. (2011). High-frequency filtering of strong-motion records. *Bulletin of Earthquake Engineering*, 9(2), 395-409. doi: 10.1007/s10518-010-9208-4

10. Inocente, I., and Maruyama, Y. (2026). Automated strong-motion record processing via deep learning-based simultaneous P-wave identification and high-pass corner-frequency selection. *The Seismic Record*, 6(2), 219-229. doi: 10.1785/0320260007

11. Jones, J. M., Kalkan, E., Stephens, C. D., and Ng, P. (2017). PRISM software: Processing and Review Interface for Strong-Motion Data. *Seismological Research Letters*, 88(3), 851-866. doi: 10.1785/0220160200

12. Kishida, T., Ktenidou, O.-J., Darragh, R. B., and Silva, W. J. (2016). *Semi-Automated Procedure for Windowing Time Series and Computing Fourier Amplitude Spectra for the NGA-West2 Database*. PEER Report 2016/02, Pacific Earthquake Engineering Research Center, University of California, Berkeley.

13. Liu, Y., Zou, L., Zhang, Q., and Li, X. (2025). Strong-motion data processing and product generation system for earthquake early warning network. *Applied System Innovation*, 8(6), 172. doi: 10.3390/asi8060172

14. Luzi, L., Puglia, R., Russo, E., D'Amico, M., Felicetta, C., Pacor, F., Lanzano, G., et al. (2016). The Engineering Strong-Motion Database: A platform to access pan-European accelerometric data. *Seismological Research Letters*, 87(4), 987-997. doi: 10.1785/0220150278

15. Michelini, A., Cianetti, S., Gaviano, S., Giunchi, C., Jozinovic, D., and Lauciani, V. (2021). INSTANCE: The Italian seismic dataset for machine learning. *Earth System Science Data*, 13(12), 5509-5544. doi: 10.5194/essd-13-5509-2021

16. Ni, Y., Hutko, A., Skene, F., Denolle, M., Malone, S., Bodin, P., Hartog, R., and Wright, A. (2023). Curated Pacific Northwest AI-ready Seismic Dataset. *Seismica*, 2(1). doi: 10.26443/seismica.v2i1.368

17. Okada, Y., Kasahara, K., Hori, S., Obara, K., Sekiguchi, S., Fujiwara, H., and Yamamoto, A. (2004). Recent progress of seismic observation networks in Japan: Hi-net, F-net, K-NET and KiK-net. *Earth, Planets and Space*, 56(8), xv-xxviii. doi: 10.1186/BF03353076

18. Perron, V., Laurendeau, A., Hollender, F., Bard, P.-Y., Gelis, C., Traversa, P., and Drouet, S. (2018). Selecting time windows of seismic phases and noise for engineering seismology applications: a versatile methodology and algorithm. *Bulletin of Earthquake Engineering*, 16(6), 2211-2225. doi: 10.1007/s10518-017-0131-9

19. Ryu, B., Bang, S., and Kwak, D. (2025). Earthquake ground motion characteristics as a function of a preprocessing procedure. *Applied Sciences*, 15(23), 12453. doi: 10.3390/app152312453

20. Thompson, E. M., Hearne, M., Aagaard, B. T., Rekoske, J. M., Worden, C. B., Moschetti, M. P., Hunsinger, H. E., et al. (2025). Automated, near real-time ground-motion processing at the U.S. Geological Survey. *Seismological Research Letters*, 96(1), 538-553. doi: 10.1785/0220240021
