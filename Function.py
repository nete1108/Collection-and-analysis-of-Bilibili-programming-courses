from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
import datetime
import time
from bilibili_UI import *
from DB import *
import pymysql
import requests
from lxml import etree
from pyecharts import options as opts
from pyecharts.charts import Funnel
from pyecharts.render import make_snapshot
from pyecharts.globals import ThemeType
from pyecharts import options as opts
from pyecharts.charts import Pie
from pyecharts.charts import Bar
from pyecharts.charts import WordCloud


class DataThread(QThread):
    signal = pyqtSignal(str, str, str, str, int, int, str)
    def __init__(self):
        QThread.__init__(self)
        self.state = 1
        self.page_number = 1
        self.o_number = 0
        self.key = []
        self.value = []
    def run(self):
        # while(self.state):
            # 爬虫准备工作
        base_url = 'https://search.bilibili.com/all?vt=77434542&keyword=%E7%BC%96%E7%A8%8B%E8%AF%BE%E7%A8%8B&from_source=webtop_search&spm_id_from=333.1007&search_source=5'
        params = {}

        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
        }
            # page_number = 1
            # o_number = 0
        unique_links = set()
        video_data_by_keyword = ['C语言', 'C++', 'Python', 'PHP', '算法', 'Java', 'go语言','Mysql','C#','Scratch','web','计算机']
        while self.page_number <= 34:
            params['page'] = str(self.page_number)
            params['o'] = str(self.o_number)
            response = requests.get(base_url, params=params, headers=headers)
            html = response.text
            html = response.content.decode('utf-8')
            parse = etree.HTMLParser(encoding='utf-8')
            contentPath = []
            contentname = []
            contentauthor = []
            contentVV = []
            contentCM = []
            contentDR = []
            doc = etree.HTML(html)
            doc.xpath('//div[@class="bili-video-card__info--right"]//a/@href')
            contentPath = doc.xpath('//div[@class="bili-video-card__info--right"]/a/@href')
            contentname = doc.xpath('//div[@class="bili-video-card__info--right"]//h3[@class="bili-video-card__info--tit"]/@title')
            contentauthor = doc.xpath('//div[@class="bili-video-card__info--right"]//span[@class="bili-video-card__info--author"]/text()')
            contentVV = doc.xpath('//div[@class="bili-video-card__stats--left"]/span[@class="bili-video-card__stats--item"][1]/span/text()')
            contentCM = doc.xpath('//div[@class="bili-video-card__stats--left"]/span[@class="bili-video-card__stats--item"][2]/span/text()')
            contentDR = doc.xpath('//div[@class="bili-video-card__stats"]/span[@class="bili-video-card__stats__duration"]/text()')
            # print(contentVV)
            # print(contentCM)
            for link, name,auther,vv,cm,dr in zip(contentPath,contentname,contentauthor,contentVV,contentCM,contentDR):
                category_found = False
                VideoID = str(self.data)
                VideoName = name
                VideoAuther = auther
                if vv[-1] == '万':
                    num = float(vv[0:-1])
                    num *= 10000
                    VideoView = int(num)
                else:
                    VideoView = int(vv)
                if cm[-1] == '万':
                    num = float(cm[0:-1])
                    num *= 10000
                    Comment = int(num)
                else:
                    Comment = int(cm)
                Duration = dr
                Category = None
                for keyword in video_data_by_keyword:
                    lower_keyword = keyword.lower()  # 将关键词转换为小写
                    if lower_keyword in name.lower():
                        Category = keyword
                        if link not in unique_links:
                            if self.state:
                                self.signal.emit(VideoID, VideoName, VideoAuther, Category, VideoView, Comment, Duration)
                                self.data += 1
                                time.sleep(0.1)
                            unique_links.add(link)
                            break

                # for keyword in video_data_by_keyword:
                #     if keyword.lower() in name.lower():
                #         Category = keyword
                #         if self.state:
                #             self.signal.emit(VideoID, VideoName, VideoAuther, Category, VideoView, Comment, Duration)
                #             self.data += 1
                #             time.sleep(0.2)
                #         break
            self.page_number += 1
            self.o_number += 24

    def Stop(self):
        self.state = 0


class MyWindow(Ui_MainWindow,QMainWindow):
    signal = pyqtSignal(str, str, str, str, int, int, str)
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.Operate()
        self.dt = {'C语言': 0, 'C++': 0, 'Python': 0, 'PHP': 0, '算法': 0, 'Java': 0, 'go语言': 0, 'Mysql': 0, 'C#': 0, 'Scratch': 0, 'web': 0, '计算机': 0}
        self.showflag = 0

    # 初始化并指明各个函数
    def Operate(self):
        self.tabWidget.currentChanged.connect(self.ShowSelWindow)
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget1.currentChanged.connect(self.ShowSelWindow)
        self.tabWidget1.setCurrentIndex(0)
        self.InitTable()
        self.ConnectDB()
        self.CreateThread()
        self.pButton_data_collection.clicked.connect(self.StartThread)
        self.pButton_show_four_picture.clicked.connect(self.show_four_htmls)
        self.pButton_show1.clicked.connect(self.show1)
        self.pButton_show2.clicked.connect(self.show2)
        self.pButton_show3.clicked.connect(self.show3)

    # 初始化各个图表
    def InitTable(self):
    # 设置列个数
        self.tableWidget_show_all_datas.setColumnCount(7)
        # 标题
        self.tableWidget_show_all_datas.setHorizontalHeaderLabels(
            ['视频ID号', '视频名称', '视频作者', '相关分类', '视频观看量', '评论数', '视频时长'])
        # 设置整行选中模式
        self.tableWidget_show_all_datas.setSelectionBehavior(True)
        # 设置列宽度
        self.tableWidget_show_all_datas.setColumnWidth(0, 147)
        self.tableWidget_show_all_datas.setColumnWidth(1, 630)
        self.tableWidget_show_all_datas.setColumnWidth(2, 247)
        self.tableWidget_show_all_datas.setColumnWidth(3, 147)
        self.tableWidget_show_all_datas.setColumnWidth(4, 120)
        self.tableWidget_show_all_datas.setColumnWidth(5, 120)
        self.tableWidget_show_all_datas.setColumnWidth(6, 147)
        # 最后一列自动填充剩余宽度
        # self.tableWidget_show_all_datas.horizontalHeader().setStretchLastSection(True)
        # 设置标题带排序
        self.tableWidget_show_all_datas.setSortingEnabled(True)
        # 隐藏默认行号
        self.tableWidget_show_all_datas.verticalHeader().setHidden(True)

    def ConnectDB(self):
        self.con = GetConn()
        self.cur = self.con.cursor()
        sql = "delete from videos"
        try:
            self.cur.execute(sql)
            self.con.commit()
            print('清空数据成功')
        except Exception as e:
            print('清空数据失败', e)


    def ShowSelWindow(self):
        selindex = self.tabWidget.currentIndex()
        self.tabWidget.setCurrentIndex(selindex)

    # 创建多线程
    def CreateThread(self):
        self.datathread = DataThread()
        self.datathread.data = 1
        self.datathread.signal.connect(self.DoWork)
        self.signal.connect(self.datathread.Stop)

    # 启动多线程
    def StartThread(self):  # 启动多线程
        text = self.pButton_data_collection.text()
        if text == '开始采集':
            self.pButton_data_collection.setText('停止采集')
            self.datathread.state = 1
            self.datathread.start()
        else:
            self.pButton_data_collection.setText('开始采集')
            self.datathread.Stop()


    def DoWork(self, VideoID, VideoName, VideoAuther, Category, VideoView, Comment, Duration):
        self.curind = self.datathread.data
        self.tableWidget_show_all_datas.insertRow(0)
        lst = [VideoID, VideoName, VideoAuther, Category, VideoView, Comment, Duration]
        if self.cur:
            sql = "insert into videos values ('{}','{}','{}','{}','{}','{}','{}')".format(VideoID, VideoName, VideoAuther, Category, VideoView, Comment, Duration)
            try:
                self.cur.execute(sql)
                self.con.commit()
            except Exception as e:
                print("插入失败！", e)

        for i in range(7):
            self.tableWidget_show_all_datas.setItem(0, i, QTableWidgetItem(str(lst[i])))
            self.tableWidget_show_all_datas.item(0, i).setTextAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

        self.dt[Category] = self.dt.get(Category, 0) + 1
        self.dt = dict(sorted(self.dt.items(), key=lambda x: x[0]))
        self.all_datas = list(self.dt.items())

        if self.showflag == 0:
            self.DrawPie()
            self.showflag = 1
        else:
            self.DrawFunnel()
            self.Draw_vv_Bar()
            self.Draw_cm_Bar()
            self.Draw_ca_Cloud()
            datas = list(self.dt.values())
            self.datathread.key = self.dt.keys()
            self.datathread.value = self.dt.values()
            js = "setValue({})".format(datas)
            self.WebEngineView_show_data_pie.page().runJavaScript(js)
            self.Label_current_collection_data.setText(
                '已采集:' + str(self.curind - 1) + '条    C#: ' + str(datas[0]) + '  C++: ' + str(
                    datas[1]) + '  C语言: ' + str(datas[2])
                + '  Java: ' + str(datas[3]) + '  Mysql: ' + str(datas[4]) + '  PHP: ' + str(
                    datas[5]) + '  Python: ' + str(datas[6])
                + '  Scratch: ' + str(datas[7]) + '  go语言: ' + str(datas[8])
                + '  web: ' + str(datas[9]) + '  算法: ' + str(datas[10]) + '  计算机: ' + str(datas[11])
            )
            self.label_pie.setText(self.get_fl_answer())



    def DrawFunnel(self):
        data = []
        for key,value in zip(self.datathread.key,self.datathread.value):
            data.append((key,value))
        # print(data)
        sort_data = sorted(data,key=lambda x:x[1],reverse=True)
        # print(sort_data)
        funnel = Funnel(init_opts=opts.InitOpts(theme=ThemeType.VINTAGE))
        funnel.add("",sort_data,
                   gap=0.9,
                   label_opts=opts.LabelOpts(formatter="{b} : {d}"),
                   )
        funnel.set_global_opts(
            title_opts=opts.TitleOpts(title="各编程课程分类统计漏斗图",pos_left="center"),
            legend_opts=opts.LegendOpts(pos_left='70%',pos_bottom='40%'),
        )
        funnel.render('各编程课程分类统计漏斗图.html')

    def Draw_vv_Bar(self):
        self.cur = self.con.cursor()
        sql_query = "SELECT Category, VideoView FROM videos ORDER BY VideoView DESC LIMIT 20"
        self.cur.execute(sql_query)
        result = self.cur.fetchall()
        # 提取结果中的数据
        video_category = [row[0] for row in result]
        vv_values = [row[1] for row in result]
        # 使用 Pyecharts 生成横向柱状图
        bar = (
            Bar()
            .add_xaxis(video_category)
            .add_yaxis("Views", vv_values)
            .set_global_opts(
                title_opts=opts.TitleOpts(title="播放量最高的前20条视频的类型"),
                xaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(
                        rotate=-45,
                        font_size=11,
                        interval=0,
                    )
                ),
            )
        )
        bar.render("videoview.html")

    def Draw_cm_Bar(self):
        self.cur = self.con.cursor()
        sql_query1 = "SELECT Category, Comment FROM videos ORDER BY Comment DESC LIMIT 20"
        self.cur.execute(sql_query1)
        result = self.cur.fetchall()
        # 提取结果中的数据
        video_category = [row[0] for row in result]
        vv_comment = [row[1] for row in result]
        # 使用 Pyecharts 生成横向柱状图
        bar = (
            Bar()
            .add_xaxis(video_category)  # 将视频名称作为 x 轴数据
            .add_yaxis("Comments", vv_comment)  # 将视频数据作为 y 轴数据
            .reversal_axis()  # 将 x 轴和 y 轴交换
            .set_global_opts(
                title_opts=opts.TitleOpts(title="评论量最高的前20条视频"),
                xaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(
                        font_size=11,  # 调整字体大小
                        interval=0,  # 设置标签显示的间隔
                    )
                ),
            )
        )
        bar.render("comment.html")

    def Draw_ca_Cloud(self):
        data = []
        for key, value in zip(self.datathread.key, self.datathread.value):
            data.append((key, value))
        # print(data)
        sort_data = sorted(data, key=lambda x: x[1], reverse=True)
        print(sort_data)
        cloud = WordCloud(init_opts=opts.InitOpts(theme=ThemeType.VINTAGE))
        cloud.add('',data,shape='circle')
        cloud.set_global_opts(
            title_opts=opts.TitleOpts(title="课程分类云图",pos_left="37%",pos_top="3%")
        )
        cloud.render("课程分类云图.html")



    def show_ca_Funnel(self):
        with open('各编程课程分类统计漏斗图.html', 'r') as file:
            html_content = file.read()
        self.WebEngineView_show_ca_Tunnel.setHtml(html_content)

    def show_vv_Bar(self):
        with open('videoview.html', 'r') as file:
            html_content = file.read()
        self.WebEngineView_show_vv_Bar.setHtml(html_content)

    def show_cm_Bar(self):
        with open('comment.html', 'r') as file:
            html_content = file.read()
        self.WebEngineView_show_cm_Bar.setHtml(html_content)

    def show_ca_Cloud(self):
        with open('课程分类云图.html', 'r') as file:
            html_content = file.read()
        self.WebEngineView_show_ca_Cloud.setHtml(html_content)

    def show_four_htmls(self):
        self.show_ca_Funnel()
        self.show_vv_Bar()
        self.show_cm_Bar()
        self.show_ca_Cloud()

    def show1(self):
        with open('videoview.html', 'r') as file:
            html_content = file.read()
        self.WebEngineView_show_vv_Bar2.setHtml(html_content)
        self.label_vv.setText(self.get_vv_answer())

    def show2(self):
        with open('comment.html', 'r') as file:
            html_content = file.read()
        self.WebEngineView_show_cm_Bar2.setHtml(html_content)
        self.label_cm.setText(self.get_cm_answer())

    def show3(self):
        with open('各编程课程分类统计漏斗图.html', 'r') as file:
            html_content1 = file.read()
        with open('课程分类云图.html', 'r') as file:
            html_content2 = file.read()
        self.WebEngineView_show_ca_Tunnel2.setHtml(html_content1)
        self.WebEngineView_show_ca_Cloud2.setHtml(html_content2)
        self.label_ca.setText(self.get_fl_answer())


    def get_fl_answer(self):
        data = []
        for key, value in zip(self.datathread.key, self.datathread.value):
            data.append((key, value))
        sort_data = sorted(data, key=lambda x: x[1])
        # print(sort_data)
        str = '从统计的结果来看，\n学习'+sort_data[0][0]+'、'+sort_data[1][0]+'、'+sort_data[2][0]+'的人相对较少，\n该些语言相对冷门\n'+'学习'+sort_data[-1][0]+'、'+sort_data[-2][0]+'、'+sort_data[-3][0]+'的人相对\n较多，\n该些语言相对热门\n'
        return str
        # self.label_pie.setText('从统计的结果来看，学习'+sort_data[0][0]+'的人最少，该语言相对冷门\n'+'学习'+sort_data[-1][0]+'的人最多，该语言相对热门\n')

    def get_vv_answer(self):
        data = []
        for key, value in zip(self.datathread.key, self.datathread.value):
            data.append((key, value))
        sort_data = sorted(data, key=lambda x: x[1])
        # print(sort_data)
        str = 'B站编程社区对'+sort_data[0][0]+'、'+sort_data[1][0]+'、'+sort_data[2][0]+'等内容表\n现出浓厚的兴趣，而每个主题的播放量和视\n频数量提供了关于观众偏好和学习方向的\n有益见解。'
        # print(str)
        return str

    def get_cm_answer(self):
        data = []
        for key, value in zip(self.datathread.key, self.datathread.value):
            data.append((key, value))
        sort_data = sorted(data, key=lambda x: x[1])
        # print(sort_data)
        str = sort_data[-1][0]+'是B站上最受欢迎的编程主题，\n其次是'+sort_data[-2][0]+'和'+sort_data[-3][0]+'科学基础知识。\n这些数据反映了不同编程主题在B站\n观众中的受欢迎程度和市场需求。\n高评论量表明了这些主题\n在编程学习社区中的重要性和吸引力。'
        # print(str)
        return str

    def DrawPie(self):
        self.creat_echarts_byhtml(self.WebEngineView_show_data_pie, 'pie', self.all_datas)


    def creat_echarts_byhtml(self, curwidget, drawtype, all_datas):
        # print(all_datas)
        the_html_content = '''
           <!DOCTYPE html>
           <html >
           <head>
               <meta charset="utf-8">
           </head>
           <body style="width:800px; height:300px;margin:auto;top:30px">
           <div id="container" style="width:800px; height:300px;margin:auto;top:30px"></div>
           <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
           <script type="text/javascript"> 
                   var dom = document.getElementById("container");
                   var myChart = echarts.init(dom);
                   var app = {};
                   var option;'''
        #######设置类型########
        if drawtype == 'pie':
            the_html_content = the_html_content + '''option = {
                       tooltip: {
                           trigger: 'item',
                       },
                       title: {
                           text: '类别分布饼状图',
                           left: 'left'
                       },
                       legend: {
                           orient: 'vertical',
                           left: 'right',
                       },series: ['''
            the_html_content = the_html_content + "{name: '数据',type: 'pie',radius:'70%',emphasis: {itemStyle: {shadowBlur: 10,shadowOffsetX: 0,shadowColor: 'rgba(0, 0, 0, 0.5)'}},data:["
            for i in range(len(all_datas)):
                the_html_content = the_html_content + "{value:" + str(all_datas[i][1]) + ", name: '" + str(
                    all_datas[i][0]) + "'},"
            the_html_content = the_html_content + "]},"

        the_html_content = the_html_content + ''']};
           if (option && typeof option === 'object') {myChart.setOption(option);}
           function setValue(vals) {
                   for (var i=0;i<vals.length;i++)
                   option.series[0].data[i].value = vals[i]
                   myChart.setOption(option)
               }
           </script>
           </body>
           </html>
           '''

        curwidget.setHtml(the_html_content)