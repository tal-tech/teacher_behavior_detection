# TeacherBehaviorDetector
输入ASR文本，判断每句话是否为某种教学行为(鼓励、举例、提醒笔记、引导、复述、复习、寒暄、总结)。


## 安装

1、安装虚拟环境
```sh
conda create --name=4s_dev python=3.7.5
source activate behavior_dev
```

>确保当前环境是`behavior_dev`

2、安装依赖

第一步：
`conda install tensorflow-gpu==1.13.1  cudatoolkit=10.0.130=0`

第二步:

`pip install torch==1.5.0+cu101 torchvision==0.6.0+cu101 -f https://download.pytorch.org/whl/torch_stable.html`

然后

`pip install -r requirements_gpu.txt`

3、为jupyter安装core(可选）

`ipython kernel install --user --name=behavior_dev`

这时你发现jupyter 多了一个叫`behavior_dev`的core。

删除核心

`jupyter kernelspec remove behavior_dev`


# 算法指标

参考算法文档: 
https://wiki.zhiyinlou.com/pages/viewpage.action?pageId=99908958

# Usage

参考demo.py