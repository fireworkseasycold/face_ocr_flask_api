### 接口说明

#### 1 word转pdf

> url: http://localhost:5000/ocr/word_to_pdf/

>请求方式：POST

| |参数1|参数2|
|:----|:----|:---|
|名称|sourcePath|targetPath|
|是否必填|是|是|
|数据类型|string|string|
|说明|word文件路径|生成pdf文件路径|

返回值类型参考
```
{
  "pdfPath": "d:/nginx/upload/seal/pdfPath/doc1.pdf",
  "success": true,
  "totalTime": 11
}
```
#### 2 图片pdf对比api

> url: http://localhost:5000/ocr/image_pdf_diff/

>请求方式：POST

| |参数1|参数2|参数3|参数4|
|:----:|:----:|:----:|:----:|:----:|
|名称|picUrl |pdfUrl |pageNo |fileName |
|是否必填|是|是|是|是|
|数据类型|string|string|number|string|
|说明|图片url|pdf url|页数|文件名|

返回值类型参考
```
{
  "diffPageUrl": "/difffile/test/",
  "success": true,
  "totalTime": 9
}
```

#### 3 图图对比api

> url: http://localhost:5000/ocr/image_diff/

>请求方式：POST

| |参数1|参数2|参数3|参数4|
|:----:|:----:|:----:|:----:|:----:|
|名称|pic1  |pic2  |pageNo |fileName |
|是否必填|是|是|是|是|
|数据类型|string|string|number|string|
|说明|图片url|图片url|页数|文件名|

返回值类型参考
```
{
  "diffPageUrl": "/difffile/test/",
  "success": true,
  "totalTime": 9
}
```

#### 4 图片文字对比api

> url: http://localhost:5000/ocr/image_text_diff/

>请求方式：POST

| |参数1|参数2|参数3|参数4|
|:----:|:----:|:----:|:----:|:----:|
|名称|picPath|diffText|pageNo |fileName |
|是否必填|是|是|是|是|
|数据类型|string|string|number|string|
|说明|图片url|比对文字|页数|文件名|

返回值类型参考
```
{
  "diffPageUrl": "/difffile/test/",
  "success": true,
  "totalTime": 9
}
```

#### 5 查看对比差异api

> url: http://localhost:5000/difffile/<string:filename>/

>请求方式：POST

| |参数1|
|:----:|:----:|
|名称|filename|
|是否必填|是|
|数据类型|string|
|说明|对比文件名|

返回值类型：网页
请求示例
```
http://localhost:5000/difffile/test/
```

#### 6 文件下载

> url: http://localhost:5000/download

>请求方式：GET

| |参数1|
|:----:|:----:|
|名称|filepath|
|是否必填|是|
|数据类型|string|
|说明|需要下载文件的文件目录|

返回值类型：网页
请求示例
```
http://localhost:5000/download?filepath=d:/project/ocr/doc1.pdf
```

#### 7 pdf文件添加空白页

> url: /pdf/add_blank_page/

>请求方式：POST

|参数名称|是否必填|数据类型|说明|
|:----:|:----:|:----:|:----|
|filePath|是|string|需要添加水印的文件路径|
|targetPath|是|string|输出pdf路径|
|onlyLast|否|number|是否只最后一页添加空白页(0:否 1:是 默认 0)|


返回值参考
```
{
  "path": "/difffile/test/",
  "success": true,
}
```

#### 8 pdf文件添加文字水印

> url: /pdf/create_text_watermark/

>请求方式：POST

|参数名称|是否必填|数据类型|说明|
|:----:|:----:|:----:|:----|
|filePath|是|string|需要添加水印的文件路径|
|text|是|string|水印文字|
|fontSize|否|number|水印文字字体大小 默认值：40|
|left|否|number|左偏移（单位厘米） 默认值：1|
|bottom|否|number|下偏移（单位厘米） 默认值：5|
|rotate|否|number|旋转角度 默认值：30|
|opacity|否|number|透明度 默认值：0.8|
|targetPath|是|string|输出pdf路径|

返回值参考
```
{
  "path": "/difffile/test/",
  "success": true,
}
```

#### 9 pdf文件添加图片水印

> url: /pdf/create_image_watermark/

>请求方式：POST

|参数名称|是否必填|数据类型|说明|
|:----:|:----:|:----:|:----|
|filePath|是|string|需要添加水印的文件路径|
|left|否|number|左偏移（单位厘米） 默认：10|
|bottom|否|number|下偏移（单位厘米） 默认：0|
|width|否|number|图片宽度 默认：60|
|height|否|number|图片宽度 默认：60|
|picPath|是|number|水印图片路径|
|targetPath|是|string|输出pdf路径|

返回值参考
```
{
  "path": "/difffile/test/",
  "success": true,
}
```


#### 10 pdf文件添加二维码

> url: /pdf/create_qrcode/

>请求方式：POST

|参数名称|是否必填|数据类型|说明|
|:----:|:----:|:----:|:----|
|filePath|是|string|需要添加水印的文件路径|
|text|是|string|水印文字|
|left|否|number|左偏移（单位厘米） 默认：0|
|bottom|否|number|下偏移（单位厘米）默认：10|
|width|否|number|图片宽度 默认：60|
|height|否|number|图片宽度 默认：60|
|targetPath|是|string|输出pdf路径|

返回值参考
```
{
  "path": "/difffile/test/",
  "success": true,
}
```
#### 11 pdf换页

> url: /pdf/transformPage/

>请求方式：POST

|参数名称|是否必填|数据类型|说明|
|:----:|:----:|:----:|:----|
|filePath|是|string|需要添加水印的文件路径|
|targetPath|是|string|输出pdf路径|
|pageList|是|string|需要转换的页，参数用逗号隔开(实例：1,2或者5,7)|

返回值参考
```
{
  "path": "/difffile/test/",
  "success": true,
}
```

#### 11 pdf盖骑缝章

> url: /pdf/perforationWithType

>请求方式：POST

|参数名称|是否必填|数据类型|说明|
|:----:|:----:|:----:|:----|
|filePath|是|string|需要添加水印的文件路径|
|targetPath|是|string|输出pdf路径|
|imagePath|是|string|印章图片|
|isDoublePrint|是|number|是否双面打印(0：否 1：是 默认：0)|


返回值参考
```
{
  "path": "/difffile/test/",
  "success": true,
}
```

#### 12 pdf转图片

> url: /pdf/pdfToImage/

>请求方式：POST

|参数名称|是否必填|数据类型|说明|
|:----:|:----:|:----:|:----|
|filePath|是|string|需要添加水印的文件路径|
|targetImageFolder|是|string|输出图片文件夹路径|


返回值参考
```
{
  "path": "/difffile/test/",
  "success": true,
}
```

#### 13 关键词定位

> url: /ocr/keyword_position/

>请求方式：POST

|参数名称|是否必填|数据类型|说明|
|:----:|:----:|:----:|:----|
|picPath|是|string|图片路径|
|keyword|是|string|关键词|


返回值参考
```
{
  "message": "成功",
  "res": [
    [
      {
        "height": 34,
        "left": 325,
        "text": "公",
        "top": 1898,
        "width": 86
      },
      {
        "height": 53,
        "left": 375,
        "text": "章",
        "top": 1894,
        "width": 25
      }
    ]
  ],
  "success": true,
  "totalTime": 4
}
```

#### 14 基于chineseocr 单张图片转文字

> url: /ocr/get_image_text/

>请求方式：POST

|参数名称|是否必填|数据类型|说明|
|:----:|:----:|:----:|:----|
|picPath|是|string|图片路径|


返回值参考
```
{
  "message": "成功",
  "res": "方应承担由此给乙方造成的实际损失。\n...",
  "success": true,
  "totalTime": 1
}
```

#### 15 基于chineseocr 图片文字对比

> url: /ocr/cimage_text_diff/

>请求方式：POST

|参数名称|是否必填|数据类型|说明|
|:----:|:----:|:----:|:----|
|picPath|是|string|图片路径|
|diffText |是|string|对比文字|
|pageNo|是|string|页码|
|fileName|是|string|文件名称|


返回值参考
```
{
  "diffPageUrl": "/difffile/test/",
  "success": true,
  "totalTime": 9
}
```


#### 16 基于chineseocr 两张图片对比

> url: /ocr/cimage_diff/

>请求方式：POST

|参数名称|是否必填|数据类型|说明|
|:----:|:----:|:----:|:----|
|pic1|是|string|第一张图片路径|
|pic2|是|string|第二章图片路径|
|pageNo|是|string|页码|
|fileName|是|string|文件名称|
|needRemoveSeal|否|string|是否需要去掉图片上的印章，（用于用印前后文件对比，（0不需要，1需要）默认为0，不需要）|


返回值参考
```
{
  "diffPageUrl": "/difffile/test/",
  "success": true,
  "totalTime": 9
}
```

#### 16 复印件鉴别

> url: /ocr/cimage_diff/

>请求方式：POST

|参数名称|是否必填|数据类型|说明|
|:----:|:----:|:----:|:----|
|pic1|是|string|第一张图片路径|
|pic2|是|string|第二章图片路径|


返回值参考
```
{
  "message": "成功",
  "res": 100, //相似度  值为0-100  完全一样为100  数值越大约相似
  "success": true,
  "totalTime": 0
}
```




