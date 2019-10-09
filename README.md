# [源码学习](https://github.com/Xu-Jian/PythonSpider/blob/master/mzitu-done.py)

## 初版

* 2019/09/09: 独立完成网站爬取
* 爬取网站：https://www.mzitu.com/
* 爬取内容： 妹子图
* 图片存储路径：./image

## 配置

```python
# mzitu.py
# run():
page_count = 2  # 下载2页（48组）图库的图片
url = 'https://www.mzitu.com/page/12/'  # 从第12页开始下载
```

## 执行

```shell
pip install requests
pip install pyquery
python3 meizitu.py
```

## 执行效果

```shell
(venv) zuoy@zuoy-pc ~/code/spiders/mzitu $ python mzitu.py
```

![19b02.jpg](./image/31b14.jpg)
![19b01.jpg](./image/19b01.jpg)

## [执行log](run.log)
