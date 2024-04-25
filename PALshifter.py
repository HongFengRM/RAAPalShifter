#非图形化的色盘偏移器
import cv2 
import numpy as np

# 全局变量
g_hls_h = []  # 图片分量 hls
g_hls_l = []
g_hls_s = []
# 滑动设置值
g_diff_h, g_diff_l, g_diff_s = 0, 0, 0

#PAL读取函数 参数是文件路径，默认为target.pal，返回色盘的颜色列表 里面是256个元组，元组为8位RGB
def LoadPAL(PATH = 'target.pal'): 
    contentlist=[]
    with open(PATH, 'rb') as f:
            content = f.read().hex()
            #print(content)

            for i in range(256):
                    start=i*6
                    end=i*6+6
                    section=content[start:end]
                    contentlist.append(section)
            #print(contentlist)
    #byd这个色盘是6bit
    colorlist=[]
    for i in contentlist:
            temptup=(    int(int(i[0:2],16)*4.0476)   ,int(int(i[2:4],16)*4.0476)  ,int(int(i[4:6],16)*4.0476)     )
            #print(temptup)
            colorlist.append(temptup)
    return(colorlist)




# HSL调整函数， 输入RGB颜色和三个调整值输出调整后的RGB颜色 针对单个颜色元组888
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

# 色盘HSL调整函数 对上一个的调用 返回新的列表888
def PAL_hsl_adj(Target_list, h_adjust=0, s_adjust=0, l_adjust=0):
    adjed_colorlist=[]
    for i in Target_list:
        adjusted_color = adjust_hsl_color(i, h_adjust, s_adjust, l_adjust)
        adjusted_color = adjusted_color.tolist()
        adjusted_color= tuple(adjusted_color)
        adjed_colorlist.append(adjusted_color)
    return(adjed_colorlist)



#色盘绘制函数 直接读取色盘内容以表明读取结果 返回一个cv的图形 输入8位色深元组 256个 列表

def PALdraw(Target_list):
    canvas2 = np.zeros((512, 320, 3), dtype=np.uint8)
    k=0
    adjuster=0
    for i in range(256):
        if i%32==0 and i!=0:
            #print(i)
            k = k +1
            adjuster=adjuster+32

        top_left = (0+(k*40), 0+((i-adjuster)*16))
        bottom_right = (40+(k*40), 16+((i-adjuster)*16))
        #color = (254, 0, 0)  # 狗娘养的,bgr??? rgb得转过去
        color=(Target_list[i][2],Target_list[i][1],Target_list[i][0])
        #print(Target_list[i])
        thickness = -1
        cv2.rectangle(canvas2, top_left, bottom_right, color, thickness)
    #cv2.imshow('Canvas', canvas2)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    return(canvas2)



# 定义pal储存函数 直接在内部再定义俩函数 给888列表直接转为文件存储起来
def PAL_save(Target_list,Saving_Path="pal edited.pal"):
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
    for i in Target_list:
            k=convert_8bit_to_6bit(i)
            o=convert_6bit_to_hex(k)[1:]
            trans6colorlist.append(o)

    #print(trans6colorlist)
    combined_string = ''.join(trans6colorlist)
    #print(combined_string)
        #保存神必文件
    with open(Saving_Path, 'wb') as f:
            f.write(bytes.fromhex(combined_string))


# 实时显示的更新函数 修改图片各分量 组合成新图片
def change_hls():
    global g_hls_h, g_hls_l, g_hls_s, g_diff_h, g_diff_l, g_diff_s

    # h分量
    hls_hf = g_hls_h.astype(float)
    hls_hf += g_diff_h
    hls_hf[hls_hf > 180] -= 180  # 超过180
    hls_hf[hls_hf < 0] += 180  # 小于0
    new_hls_h = hls_hf.astype("uint8")

    # l分量
    hls_lf = g_hls_l.astype(float)
    hls_lf += g_diff_l
    hls_lf[hls_lf < 0] = 0
    hls_lf[hls_lf > 255] = 255
    new_hls_l = hls_lf.astype("uint8")

    # s分量
    hls_ls = g_hls_s.astype(float)
    hls_ls += g_diff_s
    hls_ls[hls_ls < 0] = 0
    hls_ls[hls_ls > 255] = 255
    new_hls_s = hls_ls.astype("uint8")

    # 重新组合新图片 并转换成BGR图片
    new_bgr = cv2.cvtColor(cv2.merge([new_hls_h, new_hls_l, new_hls_s]), cv2.COLOR_HLS2BGR)

    cv2.imshow("image", new_bgr)

    #print("本次更新的HLS差值："+str(g_diff_h)+"\\"+str(g_diff_l)+"\\"+str(g_diff_s))


# h分量 值修改
def on_value_h(a):
    global g_diff_h
    value = cv2.getTrackbarPos("value_h", "image")
    value = (value - 180)
    g_diff_h = value
    change_hls()


# l分量 值修改
def on_value_l(a):
    global g_diff_l
    value = cv2.getTrackbarPos("value_l", "image") * 2
    value -= 255
    g_diff_l = value
    change_hls()


# s分量 值修改
def on_value_s(a):
    global g_diff_s
    value = cv2.getTrackbarPos("value_s", "image") * 2
    value -= 255
    g_diff_s = value
    change_hls()



def main():
#加入虚假的UI
    import os
    import tkinter.filedialog
    global g_hls_h, g_hls_l, g_hls_s

    #print("===========================================")
    #print("            色盘HSL调整器")
    #print("请输入目标色盘路径或回车以读取target.pal")
    # 创建根窗口
    root = tkinter.Tk()
    # 隐藏根窗口
    root.withdraw()

    Inputpath = tkinter.filedialog.askopenfilename(title = "请选择一个要打开的PAL文件",
                                 filetypes = [("WestWood 色盘文件", "*.pal")])

    #Inputpath=input()
    if Inputpath=="":
          Inputpath="target.pal"
    #先给色盘读取出来
    loadedpal=LoadPAL(Inputpath)
    img_org=PALdraw(loadedpal)

        #然后准备一个窗口和实时读取
    # hls分量拆分
    hls = cv2.cvtColor(img_org, cv2.COLOR_BGR2HLS)
    g_hls_h = hls[:, :, 0]
    g_hls_l = hls[:, :, 1]
    g_hls_s = hls[:, :, 2]

    #print("在弹出的图形窗口里进行调整，调整结束后按回车键保存 不要点右上角关闭窗口！")

    #print(img_org.shape)

    # 滑动条创建、设置初始值
    cv2.namedWindow("image")
    cv2.createTrackbar("value_h", "image", 0, 360, on_value_h)
    cv2.createTrackbar("value_l", "image", 0, 255, on_value_l)
    cv2.createTrackbar("value_s", "image", 0, 255, on_value_s)
    cv2.setTrackbarPos("value_h", "image", 180)
    cv2.setTrackbarPos("value_l", "image", 127)
    cv2.setTrackbarPos("value_s", "image", 127)

    # 退出
    while True:
        key = cv2.waitKey(50) & 0xFF
        if key == 13 or  cv2.getWindowProperty("image", cv2.WND_PROP_VISIBLE) < 1.0:  # 退出 esc
            break

    
    cv2.destroyAllWindows()


    #保存部分  print("本次更新的HLS差值："+str(g_diff_h)+"\\"+str(g_diff_l)+"\\"+str(g_diff_s))
    adjedcolorlist=PAL_hsl_adj(loadedpal,g_diff_h,g_diff_l,g_diff_s)

    save_file_path = tkinter.filedialog.asksaveasfilename(title = "请创建或者选择一个保存数据的PAL文件",
                                   filetypes =  [("WestWood 色盘文件", "*.pal")],
                                   defaultextension = ".pal")
    if save_file_path=="":
          save_file_path="targetedited.pal"
    PAL_save(adjedcolorlist,save_file_path)
    #print("文件保存 程序退出")

if __name__ == '__main__':
    main()
