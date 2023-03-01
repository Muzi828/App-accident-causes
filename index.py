from dash import Dash,html,dcc,Output,Input,State,dash_table
import dash_bootstrap_components as dbc

import re

from fuzzywuzzy import process
import pandas as pd
import numpy as np 

#间接原因：管理上的问题
indirect_causes = [
    '3.2.2.1 技术和设计上有缺陷—工业构件、建筑物、机械设备、仪器仪表、工艺过程、操作方法、维修检验等的设计、施工和材料使用存在问题',
    '3.2.2.2 教育培训不够、未经培训、缺乏或不懂安全操作技术知识',
    '3.2.2.3 劳动组织不合理',
    '3.2.2.4 对现场工作缺乏检查或指导错误',
    '3.2.2.5 没有安全操作规程或不健全',
    '3.2.2.6 没有或不认真实施事故防范措施，对事故隐患整改不力',
    '3.2.2.7 其他'
]



#直接原因：不安全物态和不安全行为

##不安全物态：大类
unsafe_behavior_big = [
    '6.01 防护、保险、信号等装置缺乏或有缺陷',
    '6.02 设备、设施、工具、附件有缺陷',
    '6.03 个人防护用品用具——防护服、手套、护目镜及面罩、呼吸器官护具、听力护具、安全带、安全帽、安全鞋等缺少或有缺陷',
    '6.04 生产(施工)场地环境不良'
]
##不安全物态：小类
unsafe_behavior_small = [
    '6.01.1 无防护',
    '6.01.2 防护不当',
    '6.02.1 设计不当，结构不合安全要求',
    '6.02.2 强度不够',
    '6.02.3 设备在非正常状态下运行',
    '6.02.4 维修、调整不良',
    '6.03.1 无个人防护用品、用具',
    '6.03.2 所用防护用品、用具不符合安全要求',
    '6.04.1 照明光线不良',
    '6.04.2 通风不良',
    '6.04.3 作业场所狭窄',
    '6.04.4 作业场地杂乱',
    '6.04.5 交通线路的配置不安全',
    '6.04.6 操作工序设计或配置不安全',
    '6.04.7 地面滑',
    '6.04.8 贮存方法不安全',
    '6.04.9 环境温度、湿度不当'
] 

##不安全物态：细类
unsafe_behavior_detail = [
    '6.01.1.1 无防护罩',
    '6.01.1.2 无安全保险装置',
    '6.01.1.3 无报警装置',
    '6.01.1.4 无安全标志',
    '6.01.1.5 无护栏、或护栏损坏',
    '6.01.1.6 (电气)未接地',
    '6.01.1.7 绝缘不良',
    '6.01.1.8 局扇无消音系统、噪声大',
    '6.01.1.9 危房内作业',
    '6.01.1.10 未安装防止“跑车”的挡车器或挡车栏',
    '6.01.1.11 其他',
    '6.01.2.1 防护罩未在适应位置',
    '6.01.2.2 防护装置调整不当',
    '6.01.2.3 坑道掘进，隧道开凿支撑不当',
    '6.01.2.4 防爆装置不当',
    '6.01.2.5 采伐、集材作业安全距离不够',
    '6.01.2.6 放炮作业隐蔽所有缺陷',
    '6.01.2.7 电气装置带电部分裸露',
    '6.01.2.8 其他',
    '6.02.1.1 通道门遮挡视线',
    '6.02.1.2 制动装置有缺欠',
    '6.02.1.3 安全间距不够',
    '6.02.1.4 拦车网有缺欠',
    '6.02.1.5 工件有锋利毛刺、毛边',
    '6.02.1.6 设施上有锋利倒棱',
    '6.02.1.7 其他',
    '6.02.2.1 机械强度不够',
    '6.02.2.2 绝缘强度不够',
    '6.02.2.3 起吊重物的绳索不合安全要求',
    '6.02.2.4 其他',
    '6.02.3.1 设备带“病”运转',
    '6.02.3.2 超负荷运转',
    '6.02.3.3 其他',
    '6.02.4.1 设备失修',
    '6.02.4.2 地面不平',
    '6.02.4.3 保养不当、设备失灵',
    '6.02.4.4 其他',
    '6.04.1.1 照度不足',
    '6.04.1.2 作业场地烟雾尘弥漫视物不清',
    '6.04.1.3 光线过强',
    '6.04.2.1 无通风',
    '6.04.2.2 通风系统效率低',
    '6.04.2.3 风流短路',
    '6.04.2.4 停电停风时放炮作业',
    '6.04.2.5 瓦斯排放未达到安全浓度放炮作业',
    '6.04.2.6 瓦斯越限',
    '6.04.2.7 其他',
    '6.04.4.1 工具、制品、材料堆放不安全',
    '6.04.4.2 采伐时，未开“安全道”',
    '6.04.4.3 迎门树、坐殿树、搭挂树未作处理',
    '6.04.4.4 其他',
    '6.04.7.1 地面有油或其他液体',
    '6.04.7.2 冰雪覆盖',
    '6.04.7.3 地面有其他易滑物',
] 


#不安全行为:大类
unsafe_condition = [
    '7.01 操作错误，忽视安全，忽视警告',
    '7.02 造成安全装置失效',
    '7.03 使用不安全设备',
    '7.04 手代替工具操作',
    '7.05 物体(指成品半成品、材料、工具、切屑和生产用品等) 存放不当',
    '7.06 冒险进入危险场所',
    '7.07 攀坐不安全位置(如平台护栏、汽车挡板、吊车吊钩)',
    '7.08 在起吊物下作业、停留',
    '7.09 机器运转时加油、修理、检查、调整、焊接、清扫等工作',
    '7.10 有分散注意力行为',
    '7.11 在必须使用个人防护用品用具的作业或场合中,忽视其使用',
    '7.12 不安全装束',
    '7.13 对易燃、易爆等危险物品处理错误'
]


unsafe_condition_small = [
    '7.01.1 未经许可开动、关停、移动机器',
    '7.01.2 开动、关停机器时未给信号',
    '7.01.3 开关未锁紧、造成意外转动、通电、或泄漏等',
    '7.01.4 忘记关闭设备',
    '7.01.5 忽视警告标志、警告信号',
    '7.01.6 操作错误(指按钮、阀门、搬手、把柄等的操作)',
    '7.01.7 奔跑作业',
    '7.01.8 供料或送料速度过快',
    '7.01.9 机器超速运转',
    '7.01.10 违章驾驶机动车',
    '7.01.11 酒后作业',
    '7.01.12 客货混载',
    '7.01.13 冲压机作业时，手伸进冲压模',
    '7.01.14 工件紧尚不牢',
    '7.01.15 用压缩空气吹铁屑',
    '7.01.16 其他',
    '7.02.1 拆除了安全装置',
    '7.02.2 安全装置堵塞、失掉了作用',
    '7.02.3 调整的错误造成安全装置失效',
    '7.02.4 其他',
    '7.03.1 临时使用不牢固的设施',
    '7.03.2 使用无安全装置的设备',
    '7.03.3 其他',
    '7.04.1 用手代替手动工具',
    '7.04.2 用手清除切屑',
    '7.04.3 不用夹具固定、用手拿工件进行机加工',
    '7.06.1 冒险进入涵洞',
    '7.06.2 接近漏料处 (无安全设施)',
    '7.06.3 采伐、集材、运材、装车时，未离危险区',
    '7.06.4 未经安全监察人员允许进入油罐或井中',
    '7.06.5 未“敲帮向顶”开始作业',
    '7.06.6 冒进信号',
    '7.06.7 调车场超速上下车',
    '7.06.8 易燃易爆场合明火',
    '7.06.9 私自搭乘矿车',
    '7.06.10 在绞车道行走',
    '7.06.11 未及时瞭望',
    '7.11.1 未戴护目镜或面罩',
    '7.11.2 未戴防护手套',
    '7.11.3 未穿安全鞋',
    '7.11.4 未戴安全帽',
    '7.11.5 未佩戴呼吸护具',
    '7.11.6 未佩戴安全带',
    '7.11.7 未戴工作帽',
    '7.11.8 其他',
    '7.12.1 在有旋转零部件的设备旁作业穿过肥大服装',
    '7.12.2 操纵带有旋转零部件的设备时戴手套',
    '7.12.3 其他',
]




all_causes = np.concatenate([indirect_causes,
                            unsafe_behavior_big,
                            unsafe_behavior_detail,
                            unsafe_behavior_small,
                            unsafe_condition,
                            unsafe_condition_small]).tolist()

# 满足的功能:
## 1. 可以实现针对分类号的精确或者模糊查找
## 2. 可以实现针对输入内容的模糊匹配查找





app = Dash()
server = app.server


def f(s):
    ls_test = s.split('.')
    num = len(ls_test)
    return [".".join(ls_test[:i+1]) for i in range(1,num)]

app.layout = html.Div(
    [   dbc.Row(
            [
                dbc.Col(
                    [
                        
                        html.H4('事故直接原因'),
                        html.H6('不安全物态：',style={'paddingTop':'5px'}),
                        dcc.Dropdown(unsafe_behavior_big,
                                unsafe_behavior_big[0],
                                id='dpd-big',style={'paddingTop':'5px'}),
                        dcc.Dropdown(id='dpd-small',style={'paddingTop':'5px'}),
                        html.Div(id='content-1',style={'paddingTop':'5px'}),
                        html.H6('不安全行为：',style={'paddingTop':'5px'}),
                        dcc.Dropdown(unsafe_condition,
                                unsafe_condition[0],
                                id='dpd-big-act',style={'paddingTop':'5px'}),
                        html.Div(id='content-2',style={'paddingTop':'5px'}),
                        html.Div(
                            [
                                html.H4('事故间接原因'),
                                dcc.Dropdown(
                                    indirect_causes,
                                    indirect_causes[0],
                                    id='dpd-indirect')
                            ],style={'paddingTop':'5px'}
                        ),
                        html.H4('原因分类图',style={'paddingTop':'20px'}),
                        html.Img(src='assets/cause.png',width=600,height=380),
                    ],width=6,
                ),
                dbc.Col(
                        [
                            html.H4('类别查询：',style={'paddingBottom':'10px'}),
                            dcc.Input(id='my-input', value='请输入查询分类号或者文字信息', type='text',style={'width':'600px','height':'50px','color':'gray','marginTop':'25px'}),
                            html.Button('搜索', id='submit-val',n_clicks=0,style={'textAlign':'center','marginLeft':'60px'} ) ,
                            html.H6('精准匹配：',style={'paddingTop':'30px'}  ),
                            html.Div(id='content-rigour',style={'paddingTop':'20px','paddingBottom':'80px','paddingLeft':'30px','paddingRight':'30px'}),
                            html.H6('模糊匹配：'),
                            html.Div(id='content-fuzzy',style={'paddingTop':'20px'} )

                        ],width=6
                )
            ],style={'paddingTop':'20px','paddingLeft':'30px','paddingRight':'30px'}     
        )
    ]
)

@app.callback(
    Output('dpd-small','options'),
    Input('dpd-big','value')
)
def update(v):
    #更新小类
    return [i for i in unsafe_behavior_small if v.split()[0] in i]

@app.callback(
    Output('dpd-small','value'),
    Input('dpd-small','options')
)
def update(v):
    #更新小类数值
    return v[0]

@app.callback(
    Output('content-1','children'),
    Input('dpd-small','value')
)
def update(v):
    #更新细类
    test = [i for i in unsafe_behavior_detail if v.split()[0] in i]
    if test:
        return dcc.Dropdown(test,test[0])
    else:
        pass



@app.callback(
    Output('content-2','children'),
    Input('dpd-big-act','value')
)
def update(v):
    #更新小类-不安全行为
    test = [i for i in unsafe_condition_small if v.split()[0] in i]
    if test:
        return dcc.Dropdown(test,test[0])
    else:
        pass


@app.callback(
    [Output('content-rigour','children'),Output('content-fuzzy','children')],
    Input('submit-val', 'n_clicks'),
    State('my-input', 'value')
)
def update(n_clicks,v):
    v = v if not None else '请输入查询分类号或者文字信息'
    biaodian = '[\u4e00-\u9fa5=,?!@#$%^&*()_+:"<>/\[\]\\`~——，。、《》？；’：“【】、{}|·！￥…（）-]'
    if '.' in v:
        result = re.sub(biaodian,'',v)
        if result.count('.') == 1:
            return [i for i in all_causes if result == i.split()[0]],[i for i in all_causes if result == i.split()[0]]
        else:
            return [i+'\t' for i in all_causes if i.split()[0] in result],[i+'\t' for i in all_causes if i.split()[0] in result]
    elif v in all_causes:
        if v.count('.') == 1:
            return [i for i in all_causes if result == i.split()[0]],[i for i in all_causes if result == i.split()[0]]
        else:
            return [i+'\t' for i in all_causes if i.split()[0] in result],[i+'\t' for i in all_causes if i.split()[0] in result]
    else:
        # result = process.extractOne(v, all_causes)[0]
        # print(result)
        # if result.count('.') == 1:
        #     return '未匹配到数据',[i for i in all_causes if result == i]
        # else:
        #     return '未匹配到数据',[i+'\n' for i in all_causes if i.split()[0] in result]

        ls = []
        for i in range(5):
            dic = {}
            result = process.extract(v, all_causes)[i]
            similarity = result[1]
            print(result)
            if result[0].count('.') == 1:
                dic['大类'] = result[0]
                dic['相似度'] = similarity
            elif result[0].count('.') == 2:
                results = f(result[0].split()[0])
                ls_ = sorted([i for i in all_causes for j in results if i.split()[0] == j])

                # ls_ = sorted([i for i in all_causes if i.split()[0] in result[0]])#这种做法会忽略掉末尾为两位数的标号，比如6.02.1.11和6.02.1.1
                # print(ls_)
                dic['大类'] = ls_[0]
                dic['小类'] = ls_[1]
                dic['相似度'] = similarity
            else:
                results = f(result[0].split()[0])
                ls_ = sorted([i for i in all_causes for j in results if i.split()[0] == j])
                # ls_ = sorted([i for i in all_causes if i.split()[0] in result[0]])
                if len(ls_) == 1:
                    dic['间接原因'] = ls_[0]
                    dic['相似度'] = similarity
                else:
                    dic['大类'] = ls_[0]
                    dic['小类'] = ls_[1]
                    dic['细类'] = ls_[2]
                    dic['相似度'] = similarity
            ls.append(dic)
        df = pd.DataFrame(ls)
        # print(df)
        cols = df.columns.tolist()
        cols.insert(0, cols.pop(cols.index('相似度')))
        return '未匹配到数据',html.Div(
            [
                dash_table.DataTable(
                    data = df[cols].to_dict('records'),
                    fixed_rows={'headers': True},
                    sort_action='native',
                    virtualization=True,
                    style_cell={'textAlign': 'center',
                                     'min-width': '100px'}
                    # style_header={'backgroundColor': '#1f2c56',
                    #                    'fontWeight': 'bold',
                    #                    'font': 'Lato, sans-serif',
                    #                    'color': 'orange',
                    #                    'border': '#1f2c56'},

                )
            ]
        )



    


if __name__  == '__main__':
    app.run_server(debug=True)