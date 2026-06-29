# 使用自由响应受试者工作特征曲线(FROC) 评估机器诊断肿瘤的准确性

Chaya S. Moskowitz

本章讨论了使用自由响应受试者工作特征曲线（FROC），验证检测病理切片上病灶定位的计算机算法的准确性。

在关于机器学习的研究中，Ehteshami Bejnordi 等  $ 评估且比较了 32 种计算机算法识别女性乳腺癌患者前哨淋巴结病理切片中转移病灶的存在和定位。作者使用自由响应受试者工作特征曲线（FROC）分析来评价诊断和定位的准确性。结果显示，最佳算法与病理学家在没有时间限制的情况下的诊断准确性类似（图 36.1）。

FROC 曲线可用于评价一种医学检查方法识别异常图像的能力。例如，识别放射图像中的肿瘤或组织切片中的恶性病灶。FROC 和更为人熟知的受试者工作特征（ROC）曲线有许多共同点  $。ROC 曲线主要用于评价诊断疾病的准确性，但无法评价是否可以准确地定位病灶。

## 为什么要使用 FROC 曲线？

FROC 曲线可用于评估一种检查是否可以定位某种疾病及该种检查是否优于其他检查。此外，还可以兼顾损伤部位的形态及其在图像中的定位。自由响应分析意味着某个人或某个机器可以读取并评估整个图像，在异常部位做好标记，

CAMELYON16：癌症淋巴结转移挑战，2016；CULab，中国大学实验室；FROC：自由响应受试者工作特征；HMS：哈佛医学院；MGH：麻省总医院；MIT：麻省理工学院；WOTC：没有时间限制。X轴为每张完整切片中假阳性的平均数量，范围0~0.125（蓝色）呈线性，0.125~8是以2为底的对数。各参与组均来自CAMELYON16竞赛。任务1的验证来自队列的129张切片的图像，其中49张包括转移性病灶。病理学家的诊断局部转移性病灶时未出现假阳性，且真阳性率达到0.724。

并判断该部位是否可以诊断疾病。单个图像可能在多个部位符合疾病特征。

为了完成上述分析，最终会得出一个关于疾病确诊可能性的分级（可被视为连续变量或等级变量）。被医生或机器识别出的病理性损伤可能与某些参考标准定义的疾病并不一致。被识别出的标记且确实患病的部分为真阳性，而被识别出但却并未患病的部分为假阳性。标记区域并不一定必须与真正的疾病区域完全重合，但必须“接近”真正的疾病区域，而“接近”的标准是由研究者指定的。当病灶部位并未被标记出时，则被视为假阴性。

由于病灶部位的数量已知，真阳性率（TPF）可由标记

为疾病的区域数量除以实际病灶区域的数量。这个概念与灵敏度类似。假阳性标记的数量可知，但 FROC 分析中没有类似真阴性的计算，因此无法计算假阳性率（FPR）。FPR 只能通过为每张图像中的假阳性区域平均数计算。

## 如何建立 FROC 曲线？

Ehteshami Bejnordi 等  $ 通过计算机算法标记可疑疾病区域建立 FROC 曲线，并在 0~1 中为其确诊的可能性分级。标记区域最初被分类为真阳性或假阳性取决于识别区域是否在实际病灶区域  \mu m $ 半径内，该实际病灶区域由两个病理学家使用免疫组化的方法确定。然后将这一分级与不同的阈值进行比较，从而分析其准确性。对于任一阈值（c）均可计算其对应的 FPR（c），即分级评分高于阈值（c）且最终确认为假阳性病变区域的数量除以无病灶的切片数量。一般情况下，仅推荐 FPR 在无疾病特征的图像切片中估计，这是因为病理学家在有病理损伤的切片时做出假阳性诊断的可能性要远高于其在无病理损伤的切片时做出假阳性诊断的概率。不仅如此，局部损伤的分级评分的分布在二者间也不尽相同  $。我们也可以计算任一阈值（c）对应的 TPF（c），即分级评分高于阈值（c）且最终确认为真阳性病变区域的数量除以所有切片的病灶区域数量。阈值（c）在分级标准不同时发生变化，最终可描记出不同阈值（c）对应的 FPR（c）和 TPF（c）值，并在各点之间由直线连接，从而绘制出 FROC 曲线。

## FROC 曲线的局限性是什么？

在 ROC 曲线分析中， ^{\circ} $ 对角线意味着一个检查无法区分患病与否，这条线可以作为判断测试诊断疾病效能的标志。但在 FROC 中没有一条类似这样的线，因此从 FROC

曲线中推断检查的表现比较困难。更有甚者，由于 FPR 不是一个比例，取值可能大于 1，FROC 曲线可能会沿着横轴无限延伸。

计算 FROC 曲线的关键因素是如何定义“接近”的标准。选择的距离不同可导致不同的 FROC 曲线  $。如何处理在单个病灶附近的多个发现，也会影响 FROC 曲线  $。此外，由于产生偏差的因素较多，FROC 数据相对比较复杂，如何校正这些混杂因素也是一个难题  $。

## 如何解读研究中的 FROC 曲线？

Ehteshami Bejnordi 等  $ 研究中的 FROC 曲线（其文章中的 Figure 1 和 eFigure 4）有助于将各种不同的计算机算法分级和金标准比对结果的可视化。对应每张切片的平均 FPR，HMS-MIT（哈佛医学院和麻省总医院）II 组计算得出的 TPF 更高。除了观察完整的 FROC 曲线，也可以分析特定点上的受试者工作特征。在特定的 FPR 情况下，计算相应的 TPF 可帮助读者判断该算法是否适合在临床中应用。例如，每张切片出现至多 1 个假阳性区域是可以接受的，而 HMS-MIT II 组的 TPF 值仅为 0.81（见文章补充部分的 eTable 4），此时意味着这种算法下转移病灶的识别率是 81%，漏诊率为 19%。

## 查看 FROC 曲线时的注意事项

FROC 曲线的结果依赖于样本的选择，并不一定可以推广至其他患病人群或病灶区域定位不同的病例  $。尽管也有一些参数被提出，并用于量化 FROC 分析的结果  $，但目前并没有一个可以像 ROC 曲线下面积那样得到公认。Ehteshami Bejnordi 等的研究中采用了特定的 FPR 及其对应的 TPF 的平均数作为评价 FROC 评价的参数。

## 致谢

这篇文章首次发表在 方法学 上时，声明了以下情况。

利益冲突声明：没有报道。

基金 / 支持：该研究受到美国国家癌症研究所（National Cancer Institute）对 Memorial Sloan Kettering 肿瘤中心的核心基金 P30 CA008748 的资助。

基金支持者的作用：美国国家癌症研究所（National Cancer Institute）未参与本文的撰写、投稿、修回及批准发表。

## 参考文献

[1] Ehteshami Bejnordi B, Veta M, van Diest PJ, et al. CAMELYON16 Consortium. Diagnostic assessment of deep learning algorithms for detection of lymph nodes metastases in women with breast cancer. 方法学, 2017, 318(22): 2199–2210. DOI:10.1001/方法学.2017.14585.

[2] Alba AC, Agoritsas T, Walsh M, et al. Discrimination and calibration of clinical prediction models: Users' Guides to the Medical Literature. 方法学, 2017, 318(14): 1377–1384. Medline: 29049590.

[3] Hanley JA. Receiver operating characteristic (ROC) methodology: the state of the art. Crit Rev Diagn Imaging, 1989, 29(3): 307–335. Medline: 2667567.

[4] Chakraborty DP. A brief history of free-response receiver operating characteristic paradigm data analysis. Acad Radiol, 2013, 20(7): 915–919. Medline: 23583665.

[5] Zou KH, Liu A, Bandos AI, et al. Statistical Evaluation of Diagnostic Performance: Topics in ROC Analysis. Boca Raton, FL: Chapman & Hall, 2012.

[6] Gur D, Rockette HE. Performance assessments of diagnostic systems under the FROC paradigm: experimental, analytical, and results interpretation issues. Acad Radiol, 2008, 15(10): 1312–1315. Medline: 18790403.

[7] Bandos AI, Rockette HE, Song T, et al. Area under the free-response ROC curve (FROC) and a related summary index. Biometrics, 2009, 65(1): 247–256. Medline: 18479482.

(胡婕译)

# 随机效应 meta 分析： 谨慎地总结证据

Stylianos Serghiou, Steven N. Goodman

本章解释了固定和随机效应 meta 分析评估治疗效应的差异，以及为什么要在基于入组标准不一致的随机对照试验的 meta 分析中使用随机效应模型。

一种医学治疗策略往往需要多个研究去反复验证。例如，大量的研究分析了阿片类药物和安慰剂或非阿片类药物类似物治疗慢性疼痛的差异。在 方法学 发表的一项研究中，Busse 等  $评价了来自 96 项随机对照试验的结果，其中 42 项研究采用相同的结局评价指标（即 10cm 视觉模拟评分）比较了阿片类药物和安慰剂在镇痛方面的作用。作者随即在亚组分析中使用随机效应 meta 分析来合并上述 42 个试验的结果（Busse 等文章的图 2  $）。Meta 分析将多个研究的结果合并为单个结果，是循证医学的依据。随机效应 meta 分析是最为常用的方法。

## 为什么要使用随机效应 meta 分析？

每一项评估治疗效应的研究都会给出一个基于观察或统计学估计的结果。一项研究中，在视觉模拟评分法的标尺上显示，阿片类药物比安慰剂可多降低疼痛感受约为0.54cm  $，这是基于实际观察得到的效应量。在研究设计完善的前提下，




