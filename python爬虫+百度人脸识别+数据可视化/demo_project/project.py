import base64
import os
import webbrowser
import shutil
import tkinter as tk
from tkinter import ttk
from pyecharts.charts import Bar, Line, Pie, EffectScatter, Page
from pyecharts import options as opts
from aip import AipFace
from icrawler.builtin import BingImageCrawler
from pyecharts.globals import ThemeType

""" 三码 """
APP_ID = '请在此输入'
API_KEY = '请在此输入'
SECRET_KEY = '请在此输入'

keyword = ''
count_red = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # 存储每个颜色分类下的图片数量
count_blue = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
count_green = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
count_black = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

### 原有核心功能函数 start ###
def bing_image_crawler(keyword, max_num):
    """
    通过Bing搜索下载四种颜色的图片
    :param keyword: 关键字
    :param max_num: 最大尝试数量
    :return:
    """
    dic_red = 'red_img'
    dic_blue = 'blue_img'
    dic_green = 'green_img'
    dic_black = 'black_img'
    # 如果有之前的文件夹，先删了
    if os.path.exists(dic_red):
        shutil.rmtree(dic_red)
    if os.path.exists(dic_blue):
        shutil.rmtree(dic_blue)
    if os.path.exists(dic_green):
        shutil.rmtree(dic_green)
    if os.path.exists(dic_black):
        shutil.rmtree(dic_black)
    # 颜色筛选器
    filters_red = dict(size="large", color="red")
    filters_blue = dict(size="large", color="blue")
    filters_green = dict(size="large", color="green")
    filters_black = dict(size="large", color="black")
    bing_crawler_red = BingImageCrawler(
        feeder_threads=2,
        parser_threads=4,
        downloader_threads=8,
        storage={'root_dir': dic_red}
    )
    bing_crawler_blue = BingImageCrawler(
        feeder_threads=2,
        parser_threads=4,
        downloader_threads=8,
        storage={'root_dir': dic_blue}
    )
    bing_crawler_green = BingImageCrawler(
        feeder_threads=2,
        parser_threads=4,
        downloader_threads=8,
        storage={'root_dir': dic_green}
    )
    bing_crawler_black = BingImageCrawler(
        feeder_threads=2,
        parser_threads=4,
        downloader_threads=8,
        storage={'root_dir': dic_black}
    )
    bing_crawler_red.crawl(keyword=keyword, max_num=max_num, filters=filters_red)
    bing_crawler_blue.crawl(keyword=keyword, max_num=max_num, filters=filters_blue)
    bing_crawler_green.crawl(keyword=keyword, max_num=max_num, filters=filters_green)
    bing_crawler_black.crawl(keyword=keyword, max_num=max_num, filters=filters_black)


def get_file_content(file_path):
    """
    文件转BASE64编码字符串
    :param file_path: 文件路径
    :return: 转换后的结果
    """
    file = open(file_path, 'rb')
    data = file.read()
    content = base64.b64encode(data)
    file.close()
    base = content.decode('utf-8')
    return base


def detect_face(base):
    """
    送给百度服务器进行人脸检测
    :param base: BASE64编码之后的图片
    :return: 服务器返回的JSON数据
    """
    client = AipFace(APP_ID, API_KEY, SECRET_KEY)
    options = {'face_field': 'beauty'}
    json = client.detect(base, 'BASE64', options)
    return json


def parse_json(json):
    """
    解析服务器返回的JSON数据
    :param json:
    :return:解析出的颜值，如果检测失败返回-1
    """
    # 判断是否成功
    code = json['error_code']
    if code == 0:
        # 成功检测到人脸，返回颜值分数(十分制)
        beauty = int(json['result']['face_list'][0]['beauty'] / 10) + 1
    else:
        beauty = -1
    return beauty


def classify(root_dir, count):
    """
    先爬取图片，百度检测每张图片，在Windows中按照颜值分拣成不同的文件夹
    :param count: 颜值数组
    :param root_dir: 图片根目录
    :return:void
    """
    file_list = os.listdir(root_dir)  # 把文件夹中的文件名都存到列表中
    print(file_list)
    # 遍历图片
    for i in file_list:
        # 拼接出文件路径
        path = root_dir + '/' + i
        print(path)
        # 判断是否是文件
        if os.path.isfile(path):
            base = get_file_content(path)  # BASE64
            json = detect_face(base)  # 百度
            beauty = parse_json(json)  # 解析颜值
            # 统计图片数量
            if beauty == -1:  # 不是人脸
                count[0] += 1  # 计数 + 1
            else:  # 是人脸
                count[beauty] += 1  # 计数+1
            # 把图片分类到不同的目录
            dic = root_dir + '/' + str(beauty)  # 文件夹路径
            if not os.path.exists(dic):  # 如果文件夹不存在
                os.makedirs(dic)  # 创建文件夹
            # 移动文件到所属的目录位置
            # 参数1：源文件的位置
            # 参数2：目标文件位置
            os.rename(path, dic + '/' + i)


def draw_charts(key_word, count_red, count_blue, count_green, count_black):
    bar = Bar(init_opts=opts.InitOpts(theme=ThemeType.CHALK))
    # 添加x轴
    bar.add_xaxis(['无人脸', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])
    # 添加y轴
    bar.add_yaxis(key_word, count_red)
    # 设置标题
    bar.set_global_opts(title_opts=opts.TitleOpts(title="红色风格颜值图"))
    # 生成网页,参数为网页名称
    bar.chart_id = "82086c37c73949dab4fb2927d0def2f1"

    # 折线图
    line = Line(init_opts=opts.InitOpts(theme=ThemeType.CHALK))
    # 添加x轴
    line.add_xaxis(['无人脸', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])
    # 添加y轴
    line.add_yaxis(key_word, count_blue)
    # 设置标题
    line.set_global_opts(title_opts=opts.TitleOpts(title="蓝色风格颜值图"))
    # 生成网页,参数为网页名称
    line.chart_id = "c2e096d0e3584ef08c659566358363d2"

    # 饼图
    x_data = ['无人脸', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    y_data = count_green
    data_pair = [list(z) for z in zip(x_data, y_data)]
    data_pair.sort(key=lambda x: x[1])
    a = (
        Pie(init_opts=opts.InitOpts(theme=ThemeType.CHALK))
       .add("", [list(z) for z in zip(x_data, y_data)])
       .set_colors(["blue", "green", "yellow", "red", "pink", "orange", "purple", "Pink", "Purple", "MidnightBlue",
                    "DoderBlue"])
       .set_global_opts(title_opts=opts.TitleOpts(title='绿色风格颜值图'))
       .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    )
    a.chart_id = "7c4a2530675a4bc3a39816ce0e60b370"

    # 散点图
    c = (
        EffectScatter(init_opts=opts.InitOpts(theme=ThemeType.CHALK))
       .add_xaxis(['无人脸', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])
       .add_yaxis(key_word, count_black)
       .set_global_opts(title_opts=opts.TitleOpts(title="黑色风格颜值图"))
    )
    c.chart_id = "c545bd47e9bd4a70a03b7e00b78b46c0"

    # 创建一个网页对象
    page = Page(layout=Page.DraggablePageLayout)  # 参数为可拖拽
    # 把统计添加到一个网页中，如果有多张图可以一直添加
    page.add(bar, line, a, c)
    # 生成网页
    file_name = '数据大屏.html'
    page.render(file_name)

    # 加载JSON数据，重新改变布局
    page.save_resize_html(
        source='数据大屏.html',  # 原来的网页
        cfg_file='chart_config.json',  # JSON文件
        dest='数据大屏.html')  # 新生成的布局网页
    return file_name

### 原有核心功能函数 end ###

### 新增GUI相关代码 start ###
def start_analysis():
    """GUI中开始分析的回调函数"""
    keyword = entry_keyword.get().strip()
    try:
        max_num = int(entry_max_num.get())
        if not keyword:
            tk.messagebox.showerror("错误", "请输入关键字")
            return
        if max_num <= 0:
            tk.messagebox.showerror("错误", "查询数量需大于 0")
            return

        # 执行原有逻辑
        bing_image_crawler(keyword, max_num)
        classify('red_img', count_red)
        classify('blue_img', count_blue)
        classify('green_img', count_green)
        classify('black_img', count_black)
        file = draw_charts(keyword, count_red, count_blue, count_green, count_black)
        webbrowser.open(file)

        tk.messagebox.showinfo("提示", "分析完成，已打开图表网页")
    except ValueError:
        tk.messagebox.showerror("错误", "查询数量请输入有效的整数")


# 创建GUI界面
root = tk.Tk()
root.title("人脸颜值分析工具")
root.geometry("400x200")
root.resizable(False, False)

# 设置字体以确保中文显示正常（可根据需要调整）
font_config = ('SimHei', 10)
root.option_add("*Font", font_config)

# 输入框架
input_frame = ttk.LabelFrame(root, text="分析设置")
input_frame.pack(fill=tk.X, padx=20, pady=10)

# 关键字输入
ttk.Label(input_frame, text="关键字：").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
entry_keyword = ttk.Entry(input_frame, width=30)
entry_keyword.grid(row=0, column=1, padx=5, pady=5)
entry_keyword.focus()

# 查询数量输入
ttk.Label(input_frame, text="查询数量：").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
entry_max_num = ttk.Entry(input_frame, width=30)
entry_max_num.insert(0, "20")  # 设置默认值
entry_max_num.grid(row=1, column=1, padx=5, pady=5)

# 开始分析按钮
btn_frame = ttk.Frame(root)
btn_frame.pack(fill=tk.X, padx=20, pady=5)
btn_start = ttk.Button(btn_frame, text="开始分析", command=start_analysis)
btn_start.pack(fill=tk.X)

# 启动GUI主循环
root.mainloop()
### 新增GUI相关代码 end ###
