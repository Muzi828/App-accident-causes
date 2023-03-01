from dash import Dash,html,dcc,Output,Input,State,dash_table
import dash_bootstrap_components as dbc
from accident_causes import *
import re

from fuzzywuzzy import process
import pandas as pd


app = Dash()



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
    app.run_server(debug=False)