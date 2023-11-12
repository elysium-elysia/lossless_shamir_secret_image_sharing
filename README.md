# lossless_shamir_secret_image_sharing
​本项目实现了基于Shamir门限法的无损图像秘密共享，在(r, n)门限方案下 ，该算法可以生成n张影子图像，并利用其中r张影子图像实现对原图像的恢复。

## 功能特性

- 无损图像秘密共享
- 支持RGB和灰度图像
- 存在冗余数据的影子图像

## 原理

​秘密分割（加密生成影子图像）通过构建多项式来实现，而秘密恢复（解密恢复原图像）通过拉格朗日插值法进行。图像秘密共享与一般的秘密共享在本质上是相同的，只不过待分割的秘密值变为了图像中的各像素点的值。在本实验的图像秘密共享中，分割时，构建r - 1次多项式（常数项指定为待分割秘密，其他系数此处为0-256之间的随机数），并用 n 个 key 值代入计算生成n份影子图像；恢复时，用拉格朗日插值法对r份以上影子图像进行处理即可恢复原图像。

​同时，由于8bitRGB图像（灰度图像同理）本身像素值的范围为[0,255]，因此有限域的大素数P的选取有一定的限制，这里选择的为257，因为257相对251更接近256，影响较小。但模257仍存在噪点，这是因为模257的结果中存在256，而256不在8bitRGB的像素范围中，当将模了257后的numpy数组存成图像时，大于255的值会自动压缩（模256），即256会变为0。这就导致了影子图像中读取的数据和生成影子图像的数据不一致，这部分不一致的内容经拉格朗日插值无法恢复，便导致了噪点。

为解决这一问题，我在影子图像中添加了冗余项。具体来说，我先对影子图像加冗余，在存取影子图像数据的numpy数组后拼接了一个等长的随机数组（取值范围为[1,255]，同时利用np.where()方法统计出的原numpy数组中值为256的下标将这个随机数组里对应下标的数修改为0）。表现在具体图像上，每个影子图像的长变为原来的两倍。再在读取影子图像时利用预先标好的0将对应256值还原出来，并去掉冗余项。这里选择使用空间换时间，最终也实现了无损的图像秘密共享。加冗余和去冗余代码实现如下：

```python
def decode_from_secret(imgs, index, r, n):#将影子图像转化为原图像
    assert imgs.shape[0] >= r
    x = np.array(index)
    dim = imgs.shape[1]
    img = []
    for i in range(dim):
        y = imgs[:, i]
        # y为图像数组里第i个元素
        pixel = lagrange(x, y, r, 0) % 257
        img.append(pixel)
    return np.array(img)

def redundancy(imgs):#往影子图像中加冗余保证无损图像秘密共享，此处为增加一倍冗余
    temp = []
    for i in range(len(imgs)):
        arr1 = np.random.randint(low=1, high=256, size=(len(imgs[i])))
        arr1 = np.where(imgs[i] != 256, arr1, 0)
        img_temp = np.append(imgs[i], arr1)
        temp.append(img_temp)
    temp = np.array(temp)
    return temp
```

此外，由于jpg 等有损图像储存格式会导致像素值缺失，因此影子图像的存取得使用 png 格式。（原图像的选取和最终还原图像的保存不受影响）
## 依赖项

- Python 3.x
- numpy
- pillow
- pycryptodome

你可以使用如下命令安装所需的包：

```
pip install -r requirements
```

但要注意的是，由于crypto库的混乱性，crypto库导入可能存在问题。如果显示导入报错，先卸载安装过的所有的crypto模块（pip list，看一看带crypto名字的，全都pip uninstall xxx）

全部卸载干净后，再重新执行上述命令或执行：

```
pip install pycryptodome
```

如果已经安装过pycryptodome，也要卸载，不然依然可能报错。必须卸载完所有安装的crypto模块，最后安装pycryptodome。

## 使用方法

由于本人太懒（），本算法并未实现图形化界面或任何命令的绑定，运行后按照终端提示输入即可。

## 对比实验

下列采用消融实验展现该算法在图像还原方面的优势。

下面四张图分别为原图、模251结果图、模257结果图和无损算法实现图。三张恢复结果图都采用同样的(5,10)门限方案，并都选取影子图像2、3、6、7、9来恢复原图像。

![img](https://picdm.sunbangyan.cn/2023/11/13/e4ec279c2d93f201e53ba636d6a223dd.png) 

原图

![img](https://picdm.sunbangyan.cn/2023/11/13/52234851ba3ec16d5c60743bdad64208.png) 

模251结果图像（即原算法生成结果）

![img](https://picdm.sunbangyan.cn/2023/11/13/40a060fb9f6a868a47831213a8824bcb.png) 

模257结果图像（只修改了大素数P的值）

![img](https://picss.sunbangyan.cn/2023/11/13/ad5dad0ec8acb4de8d81529215294713.png) 

实现无损秘密共享结果图像

从这四幅图显著地展示出本算法无损图像压缩的优势，能准确地还原出原图，不存在失真情况。

## 算法分析

![img](https://picst.sunbangyan.cn/2023/11/13/c275d32585e5639ce98c682719ab0b39.png)

由于采用用空间换时间的策略，该算法有较高的运行效率。但影子图像本身的大小却由于冗余项的增加，变为原来图像的8倍左右。
