# Seam Carving 实现图像智能缩放

- [Seam Carving 实现图像智能缩放](#seam-carving-实现图像智能缩放)
    - [一、项目代码说明](#一项目代码说明)
      - [1. 开发环境](#1-开发环境)
      - [2. 目录结构](#2-目录结构)
      - [3. 运行方式](#3-运行方式)
    - [二、实现功能](#二实现功能)
    - [三、代码实现思路](#三代码实现思路)
      - [1. 基本算法思路](#1-基本算法思路)
      - [2. 图像扩展实现思路](#2-图像扩展实现思路)
    - [四、实验结果及分析](#四实验结果及分析)

### 一、项目代码说明
#### 1. 开发环境
- `Python 3.7`
- `macOS Big Sur 11.1`

#### 2. 目录结构
- `src/imgs/input`: 输入图像目录
- `src/imgs/output`: 输出图像目录
- `src/GUI.py`: 由 Qt 生成的初始化界面的类
- `src/SeamCarving.py`: 负责窗口创建，算法实现
- `src/requirements.txt`: 代码依赖库
- `report.pdf`: 实验报告

#### 3. 运行方式
1. 在 `src` 目录下执行：

    ``` shell
    pip install -r requirements.txt
    ```
    完成依赖库的安装。  

2. 再执行
    ``` shell
    python SeamCarving.py [-h] -i IMAGE [-e ENERGYFUNCTION] 
                          [-W WIDTH] [-H HEIGHT]
    ```
    以启动程序。如：  
    - 启动图形界面，编辑 `imag1.jpg`，直接通过拖动 GUI 界面边缘完成缩放，最终的结果保存在 `src/imgs/output`：

        ``` shell
        python SeamCarving.py -i img1.jpg
        ```
    
    - 不启动图形界面，使用 `Saliency Measure` 作为能量函数直接输出 `500*500` 的结果图片：
        ``` shell
        python SeamCarving.py -i img1.jpg -e 1 -W 500 -H 600
        ```

3. 参数说明（使用 `-h` 参数获取）
    ```
    optional arguments:
        -h, --help              帮助、使用说明
        -i IMAGE, --image IMAGE
                                输入图片路径，必要参数
        -e ENERGYFUNCTION, --energyfunction ENERGYFUNCTION
                                能量函数, 0: gradient, 
                                1: saliency measure. Default: 0
        -W WIDTH, --width WIDTH
                                设置宽度并直接输出结果
        -H HEIGHT, --height HEIGHT
                                设置高度度并直接输出结果
    ```

</br>
</br>

### 二、实现功能
1. 基本算法
2. 图像扩展
3. GUI

</br>
</br>

### 三、代码实现思路
#### 1. 基本算法思路
1. 获取能量图 $e$  
将输入图像转化为灰度图，根据能量函数生成能量图 $e$，这里实现了梯度（gradient）和 显著性（saliency measure）两种能量函数。

2. 最小能量矩阵 $M$  
首先初始化一个与输入图像等大的矩阵 $M$，其首行为 1 中能量图的首行，之后根据下列方程使用动态规划的方法补充完成矩阵 $M$
：
$$M(x, y) = min \{M(x − 1, y − 1), M(x, y − 1), M(x + 1, y − 1)\} + e(x, y)$$

3. 回溯得到最优的细缝
从 2 中获得的 $M$ 的最后一行的最小值开始即可回溯找到能量最小（最优）的细缝。

4. 删除细缝
将 3 中获取到的细缝从图中删除，并重复上述步骤，直到减小到目标大小。

5. 同时缩小长度和宽度时，未采取最优化的顺序，使用的是先横向缩小，再纵向缩小的方法。

#### 2. 图像扩展实现思路
基本思路同缩小时删除细缝，即找到能量最小的细缝，在其左侧插入细缝，插入的细缝的像素点取其左右两侧像素点的平均值。  
但需要注意的是：由于扩展时找到的最优细缝未被删除，因此在下一次迭代时最优细缝不变，从而插入位置不变，在同一个位置执行多次插入，因此选择的是一次找出所有带插入位置后统一插入所有像素的方法。

</br>
</br>

### 四、实验结果及分析
实验结果如下：
1. 画，纵横同时缩放
<div style="display: flex; justify-content:center;">
    <div style="width: 50%;">
        <img src="https://aimerlover.cn/storage/img/img1.png">
        <div style="text-align: center;">图4.1.1 原图，608*620</div>
    </div>
</div> 
</br>

<div style="display: flex;">
    <div style="width: 80%; margin-left: 10%;">
        <img src="https://aimerlover.cn/storage/img/carved_img1_whe800.png">
        <div style="text-align: center;">图4.1.2 梯度放大，800*800</div>
    </div>
    <div style="width: 80%; margin-left: 5%; margin-right: 10%;">
        <img src="https://aimerlover.cn/storage/img/carved_img1_whe800_1.png">
        <div style="text-align: center;">图4.1.3 显著性放大，800*800</div>
    </div>
</div> 
</br>

<div style="display: flex;">
    <div style="width: 80%; margin-left: 10%;">
        <img src="https://aimerlover.cn/storage/img/carved_img1_whn400.png">
        <div style="text-align: center;">图4.1.4 梯度缩小，400*400</div>
    </div>
    <div style="width: 80%; margin-left: 5%; margin-right: 10%;">
        <img src="https://aimerlover.cn/storage/img/carved_img1_whn400_1.png">
        <div style="text-align: center;">图4.1.5 显著性缩小，400*400</div>
    </div>
</div> 
由于画面本身的复杂性，在使用两种不同的能量函数时，不管是缩小还是放大，画面的整体效果均较好，但值得注意的是，画面顶端的红条、左下和右上角的红方块文字这些较为规则的部分在缩放的时候都产生了较大的变形，添加物体保护（mask）即可较好地解决这个问题。

</br>
</br>

2. 海豚，纵横同时缩小
<div style="display: flex; justify-content:center;">
    <div style="width: 50%;">
        <img src="https://aimerlover.cn/storage/img/img2.png">
        <div style="text-align: center;">图4.2.1 原图，482*404</div>
    </div>
</div> 
</br>

<div style="display: flex;">
    <div style="width: 80%; margin-left: 10%;">
        <img src="https://aimerlover.cn/storage/img/carved_img2_wn200.png">
        <div style="text-align: center;">图4.2.2 梯度横向缩小，200*404</div>
    </div>
    <div style="width: 80%; margin-left: 5%; margin-right: 10%;">
        <img src="https://aimerlover.cn/storage/img/carved_img2_wn200_1.png">
        <div style="text-align: center;">图4.2.3 显著性横向缩小，200*404</div>
    </div>
</div> 
</br>

<div style="display: flex;">
    <div style="width: 80%; margin-left: 10%;">
        <img src="https://aimerlover.cn/storage/img/carved_img2_hn200.png">
        <div style="text-align: center;">图4.2.4 <b style="color: red;">效果差</b>，梯度纵向缩小，482*200</div>
    </div>
    <div style="width: 80%; margin-left: 5%; margin-right: 10%;">
        <img src="https://aimerlover.cn/storage/img/carved_img2_hn200_1.png">
        <div style="text-align: center;">图4.2.5 <b style="color: red;">效果差</b>，显著性纵向缩小，482*200</div>
    </div>
</div> 
这幅图是比较典型的复杂和简单场景分割明确，上为简单的天空，下为复杂的海面（纵向分割），但画面的主体海豚却在简单场景的部分，可以想象，无论是那种能量函数，在纵向缩放时均会严重破坏主体的形状，但在横向缩放时，由于场景的分割是纵向的，则不会受到太大的影响，依然可以较好地保留主体部分。同时，当画面过小时，显著性缩小在边界（非主体）处会出现明显不自然当痕迹。

</br>
</br>

3. 人与雪人，纵横同时放大
<div style="display: flex; justify-content:center;">
    <div style="width: 50%;">
        <img src="https://aimerlover.cn/storage/img/img3.png">
        <div style="text-align: center;">图4.3.1 原图，592*472</div>
    </div>
</div> 
</br>

<div style="display: flex;">
    <div style="width: 80%; margin-left: 10%;">
        <img src="https://aimerlover.cn/storage/img/carved_img3_we800.png">
        <div style="text-align: center;">图4.3.2 梯度横向放大，800*472</div>
    </div>
    <div style="width: 80%; margin-left: 5%; margin-right: 10%;">
        <img src="https://aimerlover.cn/storage/img/carved_img3_we800_1.png">
        <div style="text-align: center;">图4.3.3 显著性横向放大，800*472</div>
    </div>
</div> 
</br>

<div style="display: flex;">
    <div style="width: 80%; margin-left: 10%;">
        <img src="https://aimerlover.cn/storage/img/carved_img3_he700.png">
        <div style="text-align: center;">图4.3.4 梯度纵向放大，592*700</div>
    </div>
    <div style="width: 80%; margin-left: 5%; margin-right: 10%;">
        <img src="https://aimerlover.cn/storage/img/carved_img3_he700_1.png">
        <div style="text-align: center;">图4.3.5 显著性纵向放大，592*700</div>
    </div>
</div> 
由于背景和主体对比明显（颜色梯度大），且面部占比小，因此较好地保留了面部结构。

</br>
</br>

4. 海岸，使用梯度缩放
<div style="display: flex; justify-content:center;">
    <div style="width: 50%;">
        <img src="https://aimerlover.cn/storage/img/img4.png">
        <div style="text-align: center;">图4.4.1 原图，814*544</div>
    </div>
</div> 
</br>

<div style="display: flex;">
    <div style="width: 80%; margin-left: 10%;">
        <img src="https://aimerlover.cn/storage/img/carved_img4_we1200.png">
        <div style="text-align: center;">图4.4.2 横向放大，1200*544</div>
    </div>
    <div style="width: 80%; margin-left: 5%; margin-right: 10%;">
        <img src="https://aimerlover.cn/storage/img/carved_img4_hn200.png">
        <div style="text-align: center;">图4.4.3 纵向缩小，814*200</div>
    </div>
</div> 
</br>

<div style="display: flex;">
    <div style="width: 80%; margin-left: 10%;">
        <img src="https://aimerlover.cn/storage/img/carved_img4_he800.png">
        <div style="text-align: center;">图4.4.4 纵向放大，814*800</div>
    </div>
    <div style="width: 80%; margin-left: 5%; margin-right: 10%;">
        <img src="https://aimerlover.cn/storage/img/carved_img4_wn400.png">
        <div style="text-align: center;">图4.4.5 横向缩小，400*544</div>
    </div>
</div> 
效果较好，保留了画面中央礁石和带有绿植部分的陆地，而减少或增加了天空和海滩的部分。

</br>
</br>