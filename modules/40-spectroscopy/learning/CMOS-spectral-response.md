---
id: cmos-spectral-response
title: CMOS Sensor 光谱响应与色彩特性
type: learning
domains:
  - spectroscopy
  - sensor
status: draft
source: "https://zhuanlan.zhihu.com/p/100777121"
author:
  - "刘斯宁"
---

## 1 CMOS Sensor 光谱响应基础

### 1.2 硅材料光谱响应

目前大部分的sensor都是以硅为感光材料制造的，硅材料的光谱响应如下图所示。

![](https://picx.zhimg.com/v2-789f0ebdc5b56dc46c1c8f093428e787_1440w.jpg)

从图中可以看到，硅材料的光谱响应在波长1000nm的红外光附近达到峰值，在400nm的蓝光处只有峰值的15%左右，因此硅材料用于蓝光检测其实不算特别理想。在实际CIS产品中，特别是在暗光环境下，蓝色像素往往贡献了主要的噪声来源，成为影响图像质量的主要因素。从上图中可以看到，裸硅在可见光波段的光电转换效率大约是峰值的20%~60%，与入射光的波长有关。

### 1.4 [Bayer Filter](https://zhida.zhihu.com/search?content_id=110525519&content_type=Article&match_order=1&q=Bayer+Filter&zhida_source=entity)

为了能够区分颜色，人们在硅感光区上面设计了一层滤光膜，每个像素上方的滤光膜可以透过红、绿、蓝三种波长中的一种，而过滤掉另外两种，如下图所示。

![](https://pica.zhimg.com/v2-899592d04d00f748adb8edf14002a328_1440w.jpg)

![](https://picx.zhimg.com/v2-fc8925e0e5b946436c514468798df25f_1440w.jpg)

像点之所以叫像点而不叫像素正式因为这了原因，一个严格意义上的像素，即pixel，是一个具备红、绿、蓝三个颜色分量的组合体，能够表达RGB空间中的一个点。而sensor上的一个像点只能表达三种颜色中的一个，所以在sensor范畴内并不存在严格意义上的像素概念。但是很多情况下人们并不刻意区分像素和像点在概念上的差别，经常会用像素来指代像点，一般也不会引起歧义。

所有的像点按照一定格式紧密排成一个阵列，构成sensor的像敏区，即color imaging array。像点阵列的微观效果如下图所示。

![](https://pic1.zhimg.com/v2-a9e7bfab824e3ca8cc85656f74a4a340_1440w.jpg)

其中感光膜的布局叫做Bayer Mosaic Color Filter Arrary，通常简写为Bayer CFA或CFA。

早期的工艺微透镜之间是存在无效区域的，为了提高光能量的利用率，人们会努力扩大微透镜的有效面积，最终实现了无缝的透镜的阵列。

![](https://pic1.zhimg.com/v2-f1b6b9f0881f517b535a91c045ae9118_1440w.jpg)

索尼的Power HAD CCD 技术在Hyper HAD 技术基础上缩小了微透镜间距，进一步提升了像素感光能力。

![](https://pic4.zhimg.com/v2-696d47418760bda72f2d409c942766ef_1440w.jpg)

Bayer格式图片是伊士曼·柯达公司科学家Bryce Bayer发明的，拜耳阵列被广泛运用与数字图像处理领域。

![](https://picx.zhimg.com/v2-db9d0f537d71e82a33aeae3b54ec139d_1440w.jpg)

不同的sensor可能设计成不同的布局方式，下面是几种常见的布局

![](https://pic2.zhimg.com/v2-83e9b4759577c4d0c9cb23c36a02f713_1440w.jpg)

![](https://pic4.zhimg.com/v2-fd92a4e35ff5f4a9247ca5b8024a5147_1440w.jpg)

下面是光线通过微透镜和Bayer阵列会聚到硅势阱激发出光生电子这一物理过程的示意图。需要说明的是光生电子本身是没有颜色概念的，此图中把电子的颜色只是为了说明该电子与所属像点的关系。

![](https://pica.zhimg.com/v2-08748e2acf105fdd09be41e5d8fd002a_1440w.jpg)

Bayer格式的数据一般称为RAW格式，需要用一定的算法变换成人们熟悉的RGB格式。

![](https://pic4.zhimg.com/v2-e095749973ac29f39906765b5077bf09_1440w.jpg)

从RAW 数据计算RGB 数据的过程在数学上是一种不适定问题（ill-posed problem），理论上有无穷多种方法，因此与其说是一种科学，不如说是一种艺术。

下面介绍一种最简单的方法。这个方法考虑3x3范围内的9个像素，为简单起见只考虑两种情形，即中心像素为红色和绿色，其它情形同理。

![](https://picx.zhimg.com/v2-acc79396e1806e51fd067153146ee769_1440w.jpg)

中心像素为R

![](https://pic3.zhimg.com/v2-47f997284956b4c18004791f789c8678_1440w.jpg)

中心像素为Gr

上述过程常称为Bayer Demosaic，或者Debayer，经过此操作之后，每个像素就包含了3个完整的颜色分量，如下图所示。

![](https://pic1.zhimg.com/v2-4a82c836bbbb27d83f193f8024cb27ca_1440w.jpg)

![](https://picx.zhimg.com/v2-f49970f158ecd7bbbf5e0bf7514a304f_1440w.jpg)

上述各种Bayer格式的共同特点是接受一种颜色而拒绝两种颜色，因此理论上可以近似认为光能量损失了2/3，这是非常可惜的。**为了提高光能量的利用率，人们提出了RYYB的pattern，这是基于CMY三基色的CFA pattern，Cyan是青色（Red的补色），Magenta是品红（Green的补色），Yellow是黄色（Blue的补色）**。目前这种特殊的Bayer pattern已经在华为P30系列和荣耀20手机上实现了量产。据华为终端手机产品线总裁何刚透露，为了保证RYYB阵列在调色方面的准确性，华为付出了整整3年的时间。

![](https://pic3.zhimg.com/v2-28788084079243301991ca35ba745422_1440w.jpg)

### 3.1 量子效率 （Quantum Efficiency）

量子效率是描述光电器件光电转换能力的一个重要参数，它是在某一特定波长下单位时间内产生的平均光电子数与入射光子数之比。

由于sensor存在三种像素，所以量子效率一般针对三种像素分别给出。下图是一个实际sensor的量子效率规格示例。

![](https://pic1.zhimg.com/v2-cec889c7c70da7ff403f0550d744d064_1440w.jpg)

### 3.6 灵敏度 （Sensitivity）

CMOS sensor 对入射光功率的响应能力用灵敏度参数衡量，常用的定义是在1μm2单位像素面积上，标准曝光条件下(1Lux照度，F5.6光圈)，在1s时间内积累的光子数能激励出多少mV的输出电压。

在量子效率一定的情况下，sensor 的灵敏度主要取决于电荷/电压转换系数(Charge/Voltage Factor, CVF)。在下图的例子中，CVF =220uV/e，这意味着阱容2000e的像素能够激励出最大440mV的电压信号。

![](https://pic2.zhimg.com/v2-70f105b3f1c2601ecfba6ff22f2a025b_1440w.jpg)

在曝光、增益相同的条件下，灵敏度高的sensor信噪比更高，这意味着至少在两个方面可以获得比较优势，

- 在图像噪声水平接近的情况下，灵敏度高的sensor图像亮度更高、细节更丰富
- 在图像整体亮度接近的情况下，灵敏度高的sensor噪声水平更低，图像画质更细腻

EMVA 1288 定义了评价camera 灵敏度的标准，即多少个光子可以引起camera像素值变化1，即一个DN。根据量子力学的公式，

$$
E = h\nu = \frac{hc}{\lambda}
$$

1个波长为540 nm的绿光光子携带的能量是

$$
E_{540nm} = \frac{6.626 \times 10^{-34} \times 3 \times 10^8}{540 \times 10^{-9}} \approx 3.68 \times 10^{-19}\,J
$$

Camera 技术手册中会给出像素灵敏度规格，

![](https://pic4.zhimg.com/v2-288ce1c1b5a257f6fd627f9c1bf68a93_1440w.jpg)

根据此规格即可计算像素值变化1需要多少个光子。下面的链接给出了一个具体的例子。

下图给出了普通灵敏度和高灵敏度sensor在噪声、亮度方面的效果对比。

![](https://pic1.zhimg.com/v2-cfd3c3bf79a10264472015135590bece_1440w.jpg)

![](https://pic3.zhimg.com/v2-5c7c13f8fa9db829e4b73e4a16cea1e8_1440w.jpg)

Panasonic high sensitivity sensors

![](https://pic3.zhimg.com/v2-f5486cc89dfa8c3dc43b892b84e14ff6_1440w.jpg)

### 3.17 Foveon sensor

研究发现，不同波长的光在硅材料中能够穿透的深度是不同的，下表是关于穿深的统计。

![](https://pic2.zhimg.com/v2-0c7241be125961c35c8a6bf4ccfa3627_1440w.jpg)

Foveon 公司开发了一款可以在一个像素上捕捉全部色彩的图像传感器，型号为Foveon X3。与传统的Bayer阵列原理不同，Foveon 利用了蓝光穿透距离小，红光穿透距离大的原理，采用三层感光元件堆叠布局，每层记录一个颜色通道。

![](https://pica.zhimg.com/v2-84048ecf96de1e386260e69d8e27df26_1440w.jpg)

![](https://pic4.zhimg.com/v2-3a37fd07e43ec6c466649e099c7b5cb9_1440w.jpg)