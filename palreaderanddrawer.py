contentlist=[]
with open('target.pal', 'rb') as f:
        content = f.read().hex()
        print(content)

        for i in range(256):
                start=i*6
                end=i*6+6
                section=content[start:end]
                contentlist.append(section)
        print(contentlist)
#byd这个色盘是6bit
colorlist=[]
for i in contentlist:
        temptup=(    int(int(i[0:2],16)*4.0476)   ,int(int(i[2:4],16)*4.0476)  ,int(int(i[4:6],16)*4.0476)     )
        print(temptup)
        colorlist.append(temptup)
print("111")
print(colorlist[0][0])

#===========================================hsl调整函数
# 定义一个函数用于调整HSL颜色
def adjust_hsl_color(rgb_color, h_adjust=0, s_adjust=0, l_adjust=0):
    # 将RGB颜色转换为HSL颜色
    hsl_color = cv2.cvtColor(np.uint8([[rgb_color]]), cv2.COLOR_RGB2HLS)[0][0]

    # 调整HSL值
    hsl_color[0] += h_adjust  # 调整色相
    hsl_color[1] = np.clip(hsl_color[1] + s_adjust, 0, 255)  # 调整饱和度
    hsl_color[2] = np.clip(hsl_color[2] + l_adjust, 0, 255)  # 调整亮度

    # 将HSL颜色转换回RGB颜色
    adjusted_rgb_color = cv2.cvtColor(np.uint8([[hsl_color]]), cv2.COLOR_HLS2RGB)[0][0]

    return adjusted_rgb_color


#本文件用于测试绘制一个色盘
#pal显示习惯上采用32x8的显示方式。
#单个色块20X8

#长256宽160
import cv2
import numpy as np

# 创建一张空白的画布
canvas2 = np.zeros((256, 160, 3), dtype=np.uint8)
k=0
adjuster=0
for i in range(256):
    if i%32==0 and i!=0:
        #print(i)
        k = k +1
        adjuster=adjuster+32

    top_left = (0+(k*20), 0+((i-adjuster)*8))
    bottom_right = (20+(k*20), 8+((i-adjuster)*8))
    #color = (254, 0, 0)  # 狗娘养的,bgr??? rgb得转过去
    color=(colorlist[i][2],colorlist[i][1],colorlist[i][0])
    print(colorlist[i])
    thickness = -1
    cv2.rectangle(canvas2, top_left, bottom_right, color, thickness)

cv2.imshow('Canvas', canvas2)
cv2.waitKey(0)
cv2.destroyAllWindows()


#HSV转换
# 调整HSL值
h_adjust = 20  # 色相增加20度
s_adjust = 0   # 饱和度不变
l_adjust = 0   # 亮度不变.

adjed_colorlist=[]
for i in colorlist:
      adjusted_color = adjust_hsl_color(i, h_adjust, s_adjust, l_adjust)
      adjusted_color = adjusted_color.tolist()
      adjusted_color= tuple(adjusted_color)
      adjed_colorlist.append(adjusted_color)

print(type(adjusted_color))
print(adjusted_color)



canvas = np.zeros((256, 160, 3), dtype=np.uint8)
k=0
adjuster=0
for i in range(256):
    if i%32==0 and i!=0:
        #print(i)
        k = k +1
        adjuster=adjuster+32



    top_left = (0+(k*20), 0+((i-adjuster)*8))
    bottom_right = (20+(k*20), 8+((i-adjuster)*8))
    #color = (254, 0, 0)  # 狗娘养的,bgr??? rgb得转过去
    color=(adjed_colorlist[i][2],adjed_colorlist[i][1],adjed_colorlist[i][0])
    thickness = -1
    cv2.rectangle(canvas, top_left, bottom_right, color, thickness)

cv2.imshow('Canvas', canvas)
cv2.waitKey(0)
cv2.destroyAllWindows()

#把天杀的色盘存回去
#定义8转6神必函数
def convert_8bit_to_6bit(rgb):
    r, g, b = rgb
    r_6bit = round((r / 255) * 63)
    g_6bit = round((g / 255) * 63)
    b_6bit = round((b / 255) * 63)
    return (r_6bit, g_6bit, b_6bit)
def convert_6bit_to_hex(rgb):
    r, g, b = rgb
    # Convert each 6-bit channel to hexadecimal
    r_hex = format(r, '02X')  # Convert to 2-digit hexadecimal
    g_hex = format(g, '02X')
    b_hex = format(b, '02X')
    # Concatenate the hexadecimal values
    hex_color = '#' + r_hex + g_hex + b_hex
    return hex_color

trans6colorlist=[]
for i in adjed_colorlist:
     k=convert_8bit_to_6bit(i)
     o=convert_6bit_to_hex(k)[1:]
     trans6colorlist.append(o)

print(trans6colorlist)
combined_string = ''.join(trans6colorlist)
print(combined_string)
#保存神必文件
with open('pal edited.pal', 'wb') as f:
    f.write(bytes.fromhex(combined_string))