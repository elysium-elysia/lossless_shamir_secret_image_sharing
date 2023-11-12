from PIL import Image
import numpy as np
from Crypto.Util.number import *
path = "test.png"

def image_read(path):#读取图像数据
    img = Image.open(path)
    img_array = np.asarray(img)
    return img_array.flatten(), img_array.shape
    #返回图像的一维数组和图像维度

def polynomial(img, n, r):#Shamir秘密共享方案，通过多项式生成影子图像
    num_pixels = img.shape[0]
    coef = np.random.randint(low=0, high=257, size=(num_pixels, r - 1))
    gen_imgs = []
    for i in range(1, n + 1):
        base = np.array([i ** j for j in range(1, r)])
        base = np.matmul(coef, base)
        img_ = img + base
        img_ = img_ % 257
        gen_imgs.append(img_)
    return np.array(gen_imgs)

def lagrange(x, y, num_points, x_test):#拉格朗日插值计算
    # 所有的基函数值，每个元素代表一个基函数的值
    l = np.zeros(shape=(num_points,))
    # 计算第k个基函数的值
    for k in range(num_points):
        # 乘法时必须先有一个值
        l[k] = 1
        # 计算第k个基函数中第k_个项（每一项：分子除以分母）
        for k_ in range(num_points):
            if k != k_:
                # 基函数需要通过连乘得到,k!=k_(即分母不为0)
                inver = inverse(int(x[k] - x[k_]), 257)
                l[k] = l[k] * (x_test - x[k_]) * inver
            else:
                continue
    L = 0
    for i in range(num_points):
        # 求所有基函数值的和
        L += y[i] * l[i]
    return L

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

def eliminate(input_imgs):#除去影子图像的冗余
    ia = []
    for i in range(len(input_imgs)):
        b = input_imgs[i][:len(input_imgs[i]) // 2]
        c = input_imgs[i][len(input_imgs[i]) // 2:]
        b = np.where(c == 0, 256, b)
        ia.append(b)
    ia = np.array(ia)
    return ia

if __name__ == "__main__":
    print("请输入所要实现的门限方案(r,n)")
    r = int(input("r: "))
    n = int(input("n: "))
    img_flattened, shape = image_read(path)
    gen_imgs = polynomial(img_flattened, n = n, r = r)
    gen_imgs = redundancy(gen_imgs)
    to_save = []
    for i in range(len(gen_imgs)):
        a = gen_imgs[i].reshape((shape[0], 2 * shape[1], shape[2]))
        to_save.append(a)
    to_save = np.array(to_save)
    for i, img in enumerate(to_save):#保存影子图像
        Image.fromarray(img.astype(np.uint8)).save("test_{}.png".format(i + 1))
    print("影子图像保存完成")
    print("输入拟用来恢复原图的影子图像序号，每输入一个数字用回车隔开")
    num_list = []
    for i in range(r):#确定哪些是用来还原的影子图像
        num = int(input())
        num_list.append(num)
    input_imgs = []
    shadow_imgs = []
    shadow_shape = ()
    for i in range(n):
        img, _ = image_read("test_{}.png".format(i + 1))
        shadow_imgs.append(img)
    shadow_imgs = np.array(shadow_imgs)
    shadow_imgs = eliminate(shadow_imgs)
    hint = "这次使用影子图像"
    for i in num_list:
        input_imgs.append(shadow_imgs[i - 1])
        hint += str(i) + "、"
    hint = hint.strip('、') + '恢复原图像'
    print(hint)
    _, shadow_shape = image_read("test_1.png")
    origin_shape = (shadow_shape[0], shadow_shape[1] // 2, shadow_shape[2])
    #获取原图尺寸
    print("还原图像中")
    origin_img = decode_from_secret(np.array(input_imgs),num_list, r=r, n=n)
    origin_img = origin_img.reshape(*origin_shape)
    Image.fromarray(origin_img.astype(np.uint8)).save("test_origin.png")
    print("图像还原工作完成")

