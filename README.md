# web_ocr
#swagger:127.0.0.1:5000/apidocs/
#### 介绍
使用 `Flask` 构建图片比对服务，提供HTTP接口，Pyinstaller打包项目为可独立运行的exe程序。
#### api.py可模拟Post请求
#### main.py的
get_diff(pic1,pic2,taskno)，其中:
pic1：第一个图片base64字符串
pic2：第二个图片base64字符串
taskno：任务号
该方法接两个图片，先将图片转成文字，在将对比结果转成网页，文件名为taskno.html，一体机直接引用。

#### 配置文件说明 `config.ini`：
``` ini
[config]
; 服务端口号，默认5000
port=5000

#### 开发环境

> 安装所需文件打包下载地址：[face_recognition_win10_install_requires.zip](https://pan.baidu.com/s/1vneStX-WuObn4VHqUlbvDg)

- Windows 10 64 Bit
- Python 3.6
- numpy-1.15.0+mkl-cp36-cp36m-win_amd64
- scipy-1.1.0-cp36-cp36m-win_amd64
- boost_1_68_0-msvc-14.0-64
- dlib-19.15
- cmake-3.12.1-win64-x64
```

#### 安装要求

> 新版本dlib 不再需要 Boost了，所以你可以跳过它。请记住，您仍需要满足以下要求
1. 安装了C / C ++编译器的Microsoft Visual Studio 2015（或更高版本）
2. `Python3`（我使用的是 `Python 3.6 x64`，其他版本应该也可以）
3. `Boost` 库版本1.63或更新的版本
4. `CMake` 安装并且添加到系统环境变量
5. `pip show dlib`
6. `pip install face_recognition`
7. `pip install configparser flask flask_cors`
8. `cd 当前项目目录`
9. `python main.py` 
10. 基于paddleocr  `pip show paddleocr` `pip show paddlepaddle`  #也可以用chineseocr，不过深度学习模型需要自己部署搭建


#### 项目打包教程

> 参考教程：[Freeze your script with Pyinstaller](https://github.com/ageitgey/face_recognition/issues/357)

1. 确保您已经正确安装了项目相关依赖，并且脚本能正常运行
2. `pip install pyinstaller`
3. 运行 `pyinstaller -F main.py`
4. 复制`config.ini`和`templates`,`static`文件夹到`dist/mian/`
5. 在`dist/mian/`下添加`static`文件夹
6. 请享用


