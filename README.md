# 基于PHM失效分析实验台的风车轴承故障分析-上位机程序

## 配置环境
#### 请使用如下命令创建python环境
```
conda create -n blade-monitor python=3.9
conda activate blade-monitor
```
#### 请使用如下命令安装依赖
```
pip3 install -r requirements.txt -i http://nexus3.msxf.com/repository/pypi/simple --trusted-host nexus3.msxf.com
```

## 上位机通信规则
#### 发送到单片机
> 皆使用16进制
- 指定传输数据类型
  - m <所需数据类型数量> <数据1> <数据2> ...
  - 例如: 0x77 0x03 0x00 0x01 0x04
