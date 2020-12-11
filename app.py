import dash
import dash_table
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.express as px
import dash_core_components as dcc
import dash_html_components as html
import dash_table.FormatTemplate as FormatTemplate
import datetime
import time
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
import urllib.parse
import pathlib
import math
from garenadata import hdfs
from garenadata.dt import DT

import base64
import io

import sys
sys.path.append(r"tools")
import GetFormat
import GetColorBar 

ENABLED = True
NAME = "Store Weekly Dashboard"
url_base_pathname = "/"
server = True
if not __name__ == "__main__":
    from constant import PREFIX
    from pathlib import Path
    from flask_app import flask_app
    server = flask_app
    url_base_pathname = Path(PREFIX, *__package__.split(".")[1:]).as_posix() + "/"

app = dash.Dash(__name__, server=server, url_base_pathname=url_base_pathname)


PATH = pathlib.Path("/workspace/reports/ff/store")
DATA_PATH = PATH.joinpath("data").resolve()
store_consume = hdfs.read_csv(DATA_PATH.joinpath("store_consume"))
store_consume.loc[store_consume.region.isna(),'region'] = 'NA'
gun_box_consume = hdfs.read_csv(DATA_PATH.joinpath("gun_box_consume"))
gun_box_consume.loc[gun_box_consume.region.isna(),'region'] = 'NA'
store_ratio = hdfs.read_csv(DATA_PATH.joinpath("store_ratio"))
store_ratio.loc[store_ratio.region.isna(),'region'] = 'NA'
gun_box_power = hdfs.read_csv(DATA_PATH.joinpath("gun_box_power"))
gun_box_power.loc[gun_box_power.region.isna(),'region'] = 'NA'
gem_consume_bychannel_all = hdfs.read_csv(DATA_PATH.joinpath("gem_consume_bychannel_all"))
gem_consume_bychannel_all.loc[gem_consume_bychannel_all.region.isna(),'region'] = 'NA'
type_conversion = hdfs.read_csv(DATA_PATH.joinpath("type_conversion"))
type_conversion.loc[type_conversion.region.isna(),'region'] = 'NA'
top10 = hdfs.read_csv(DATA_PATH.joinpath("top10"))
top10.loc[top10.region.isna(),'region'] = 'NA'
top10 = top10.sort_values(by=['region','rank'])
purchase_all = hdfs.read_csv(DATA_PATH.joinpath("purchase_all"))
purchase_all.loc[purchase_all.region.isna(),'region'] = 'NA'
top30 = hdfs.read_csv(DATA_PATH.joinpath("top30"))
top30 = top30.sort_values(by=['region','rank'])
purchase_regions = hdfs.read_csv(DATA_PATH.joinpath("purchase_regions"))
top30.loc[top30.region.isna(), 'region'] = 'NA'
purchase_regions.loc[purchase_regions.region.isna(),'region'] = 'NA'
null_item = hdfs.read_csv(DATA_PATH.joinpath("null_item"))
type_consume = hdfs.read_csv(DATA_PATH.joinpath("type_consume"))
type_consume.loc[type_consume.region.isna(), 'region'] = 'NA'

lst_day = datetime.datetime.strptime(str(max(type_conversion.local_dt)),'%Y%m%d') + datetime.timedelta(days=6)
new_time = datetime.datetime.strftime(lst_day-datetime.timedelta(days=6),'%Y/%m/%d') +' - ' + datetime.datetime.strftime(lst_day,'%Y/%m/%d')
old_time = datetime.datetime.strftime(lst_day-datetime.timedelta(days=13),'%Y/%m/%d') +' - ' + datetime.datetime.strftime(lst_day-datetime.timedelta(days=7),'%Y/%m/%d')

update_date = datetime.datetime.strftime(lst_day+datetime.timedelta(days=2),'%Y/%m/%d')

def give_num_format(num):
    return (f"{num:,}")

def get_per(num):
    return str(round(num*100,2))+'%'

def get_round_num(num):
    num = str(num)
    if len(num) <=6:
        new_num = num
    elif len(num)>=7 and len(num)<=9:
        new_num = int(round(int(num)/1000000,1)*1000000)
    else:
        new_num = int(round(int(num)/1000000000,1)*1000000000)
    return new_num

tabs_styles = {
    'height': '100px'
}
tab_style = {
    'borderBottom': '1px solid #FFFFFF',
    'borderTop': '1px solid #FFFFFF',
    'padding': '15px',
    'fontWeight': 'bold',
    'backgroundColor': '#FFFFFF'
}

tab_selected_style = {
    'borderTop': '1px solid #FFFFFF',
    'borderBottom': '1px solid #FFFFFF',
    'backgroundColor': '#F05A63',
    'color': 'white',
    'padding': '15px',
}

app.layout = html.Div([
    html.H1("Store Weekly Report"),
    html.H5('update_date: '+update_date),
    html.Div([
        html.H3("1. Overall Analysis"),
        html.Div([
            dcc.Dropdown(
                id='time_dropdown_1',
                options=[{'label': new_time,'value': 1},
                         {'label': old_time,'value':0}],
                value=1
            )
        ],style={'display':'inline-block','margin-left':'5%','width':'20%','height':'25px'}),
        html.Div([
            dcc.Dropdown(
                id='region_dropdown2',
                options=[{'label': i, 'value': i} for i in set(top30.region.to_list())],
                value='ALL'
            )
        ],style={'display': 'inline-block','margin-left':'3%','width':'10%','height':'25px'}),
        html.Div([
            html.H4("Store Gem Consumption Ratio:"),
            html.Div(id='store_ratio',style={'display': 'inline-block','margin-left':'2%','margin-right':'8%','color':'#c43c3c'}),
            html.H4("Gun Box Gem Consumption Ratio:"),
            html.Div(id='gun_box_ratio',style={'display': 'inline-block','margin-left':'2%','color':'#c43c3c'})
        ])
    ],style={'margin-bottom':'30px'}),

    html.Div([
        dcc.Graph(id='gem_consume_bar')
    ],style={'margin-top':'-40px','margin-bottom':'50px','margin-left':'-5%','width':'90%'}),

    html.Div([
        html.H3("2. Analysis by Item Type"),
        html.Div([
            dcc.Dropdown(
                id='time_dropdown_2',
                options=[{'label': new_time, 'value': 1},
                         {'label': old_time,'value':0}],
                value=1
            )
        ],style={'display': 'inline-block','margin-left':'5%','width':'20%','height':'25px'}),
        html.Div([
            dcc.Dropdown(
                id='region_dropdown3',
                options=[{'label': i, 'value': i} for i in set(top30.region.to_list())],
                value='ALL'
            )
        ],style={'display': 'inline-block','margin-left':'3%','width':'10%','height':'25px'}),
        html.Div([
            html.Div([
                dcc.Graph(id='pie_chart_1')
            ],style={'width':'45%','display': 'inline-block'}),
            html.Div([
                dcc.Graph(id='pie_chart_2')
            ],style={'width':'45%','display': 'inline-block'})
        ],style={'margin-top':'20px'})
    ],style={'margin-bottom':'50px'}),
    html.Div([
        dcc.Graph(id='consumption_line')
    ],style={'margin-top':'-30px','margin-bottom':'50px','margin-left':'-5%','width':'90%'}),
    html.Div([
        dcc.Graph(id='conversion_bar')
    ],style={'margin-top':'-30px','margin-bottom':'50px','margin-left':'-5%','width':'90%'}),

    html.Div([
        html.H3("3. Top10 Item Ranklist"),
        html.Div([
            dcc.Dropdown(
                id='time_dropdown_3',
                options=[{'label': new_time, 'value': 1},
                        {'label': old_time,'value':0}],
                value=1
            )  
        ],style={'display': 'inline-block','margin-left':'5%','width':'20%','height':'25px'}),
        html.Div([
            dcc.Dropdown(
                id='region_dropdown4',
                options=[{'label': i, 'value': i} for i in set(top30.region.to_list())],
                value='ALL'
            )
        ],style={'display': 'inline-block','margin-left':'3%','width':'10%','height':'25px'}),
        html.Div([
            dcc.Tabs(
                id="tabs",
                value='character',
                children=[
                dcc.Tab(label='Character', value='character',style=tab_style, selected_style=tab_selected_style),
                dcc.Tab(label='Emote', value='emote',style=tab_style, selected_style=tab_selected_style),
                dcc.Tab(label='Gun Box', value='gun_box',style=tab_style, selected_style=tab_selected_style),
                dcc.Tab(label='Pet', value='pet',style=tab_style, selected_style=tab_selected_style),
                dcc.Tab(label='Cloth', value='cloth',style=tab_style, selected_style=tab_selected_style),
                dcc.Tab(label='Token Box', value='token_box',style=tab_style, selected_style=tab_selected_style)
                ])
            ],style={'margin-top':'30px'}),
        dcc.Markdown('The filter item above the cumulative distribution curve on the right is used to remove Top N items. By default, gem consumption distribution of all items is displayed.'),

        html.Div([
            html.Div([
                html.Div([
                dash_table.DataTable(           
                            id='table'
                            ,style_cell={'minWidth':'20px','maxWidth':'50px','width':'50px'
                                        ,'whiteSpace': 'normal','height': 'auto'
                                        ,'textAlign': 'left','font-family':'Verdana','font-size':8
                                        ,'border': '1px solid black'
                                            } 
                            ,style_cell_conditional=[
                                                    {'if': {'column_id': 'name'},'width': '35%'},
                                                    {'if': {'column_id': 'rank'},'width': '6%'},
                                                    {'if': {'column_id': 'total_cost'},'width': '20%'}
                                                ]
                            ,style_header={
                                        'backgroundColor': '#F05A63'
                                        ,'border': '1px solid black'
                                        ,'textAlign': 'left'
                                        ,'font-family':'Verdana'
                                        ,'color':'white'
                                        }
                            ,style_as_list_view=True
                            )
                ],style={'width':'50%','float': 'left','margin-left':'5%'}),
                html.Div([
                    html.Div([
                        dcc.RadioItems(
                            id='rmv_dropdown_1',
                            options=[{'label': i, 'value': i} for i in range(4)],
                            value=0
                        )
                    ],style={'text-align':'center'}),
                    html.Div([
                        dcc.Graph(id='line')
                    ])   
                ],style={'width':'40%','display': 'inline-block','margin-left':'5%'})
            ],style={'margin-top':'30px'}),
        ],style={'margin-left':'-5%','margin-bottom':'20px','margin-top':'50px'}),
        html.A(html.Button('Download Data', id='download-button-1'), id='my-link-1')

    ],style={'margin-bottom':'50px'}),


    html.H3("4. Top30 Item Ranklist"),
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='time_dropdown_4',
                options=[{'label': new_time, 'value': 1},
                        {'label': old_time,'value':0}],
                value=1
            )
        ],style={'display': 'inline-block','width':'35%','height':'25px'}),
        html.Div([
            dcc.Dropdown(
                id='region_dropdown',
                options=[{'label': i, 'value': i} for i in set(top30.region.to_list())],
                value='ALL'
            )
        ],style={'display': 'inline-block','margin-left':'5%','width':'15%','height':'25px'})
    ],style={'display': 'inline-block','margin-left':'5%','width':'60%'}),

    html.Div([
        html.Div([
                html.Div([
                dash_table.DataTable(           
                            id='table_2'
                            ,style_cell={'minWidth':'20px','maxWidth':'50px','width':'50px'
                                        ,'whiteSpace': 'normal','height': 'auto'
                                        ,'textAlign': 'left','font-family':'Verdana','font-size':8
                                        ,'border': '1px solid black'
                                            } 
                            ,style_cell_conditional=[
                                                    {'if': {'column_id': 'name'},'width': '30%'},
                                                    {'if': {'column_id': 'rank'},'width': '8%'},
                                                    {'if': {'column_id': 'total_cost'},'width': '13%'},
                                                    {'if': {'column_id': 'total_sold'},'width': '13%'}
                                                ]
                            ,style_header={
                                        'backgroundColor': '#F05A63'
                                        ,'border': '1px solid black'
                                        ,'textAlign': 'left'
                                        ,'font-family':'Verdana'
                                        ,'color':'white'
                                        }
                            ,style_as_list_view=True
                            )
                ]),
        ],style={'width':'80%','margin-left':'5%','margin-top':'30px','margin-bottom':'20px'}),
        html.A(html.Button('Download Data', id='download-button-2'), id='my-link-2'),

        html.Div([
            html.Div([
                dcc.RadioItems(
                    id='rmv_dropdown_5',
                    options=[{'label': i, 'value': i} for i in range(4)],
                    value=0
                )
            ],style={'text-align':'center'}),
            html.Div([
                dcc.Graph(id='line_regions')
            ])   
        ],style={'width':'80%','display': 'inline-block','margin-top':'50px'})

    ],style={'margin-left':'10%'}),
        
    html.Div([
        html.H3("5. Item without Name"),
        html.Div([
            dcc.Graph(id='table_3')
        ],style={'width':'50%','margin-left':'5%'})
    ])

    
],style={'margin-left':'10%','margin-right':'10%','margin-bottom':'50px'})


@app.callback(
    Output('store_ratio', 'children'),
    [Input('time_dropdown_1','value'),
    Input('region_dropdown2','value')]
)
def update_figure(time,region):
    df = store_consume.loc[store_consume.if_latest==time,]
    if region == 'ALL':
        val = sum(df.total_amount)/sum(df.total_gem_consume)
    else:
        val = np.array(df.loc[df.region==region,'store_consume_ratio'])[0]
    val = str(round(val*100,2))+'%'
    return val

@app.callback(
    Output('gun_box_ratio', 'children'),
    [Input('time_dropdown_1','value'),
    Input('region_dropdown2','value')]
)
def update_figure(time,region):
    df = gun_box_consume.loc[gun_box_consume.if_latest==time,]
    if region == 'ALL':
        val = sum(df.total_gun_box_amount)/sum(df.total_amount)
    else:
        val = np.array(df.loc[df.region==region,'gun_box_ratio'])[0]
    val = str(round(val*100,1))+'%'
    return val

@app.callback(
    Output('gem_consume_bar', 'figure'),
    [Input('time_dropdown_1','value'),
    Input('region_dropdown2','value')]
)
def update_figure(time,region):
    if region == 'ALL':
        df = gem_consume_bychannel_all.groupby(['channel','local_dt']).agg({'total_amount':'sum'}).reset_index()
    else:
        df = gem_consume_bychannel_all.loc[gem_consume_bychannel_all.region==region,]
    color_dict = {'Web events':'#3768C3','Store':'#EE731F','Lottery':'#9F9E9E','EP':'#FEC601','Others':'#00CED1'}
    data = []
    for i in ('Web events','Store','Lottery','EP','Others'):
        trace = go.Bar(x=[datetime.datetime.strptime(str(i), '%Y%m%d') for i in list(df.loc[df.channel==i,'local_dt'].unique())],
                       y=[get_round_num(i) for i in df.loc[df.channel==i,'total_amount'].to_list()],
                       name=i,
                       marker=dict(color=color_dict[i]))
        data.append(trace)
    layout = dict(title = dict(text='<b>Gem Consumption Trend by Channel</b>',x=0.5,y=0.85,font_color="#444444",font_size=18,font_family='verdana'),
                plot_bgcolor='#FFFFFF',
                xaxis=dict(showline=True,showgrid=False,linecolor='#000000',linewidth=2,tickfont =dict(size = 11,family='verdana')),
                yaxis=dict(showline=True,showgrid=False,tickfont =dict(size = 11,family='verdana')),
                barmode='stack',
                legend=dict(orientation="h",x=0.33,font_family='verdana',font_size=11),
                height=400)
    fig = go.Figure(data,layout)
    return fig

@app.callback(
    Output('pie_chart_1', 'figure'),
    [Input('time_dropdown_2','value'),
    Input('region_dropdown3','value')]
)
def update_figure(time,region):
    df = store_ratio.loc[store_ratio.if_latest==time,]
    if region == 'ALL':
        df = df.groupby('type').agg({'total_price':'sum'}).reset_index()
    else:
        df = df.loc[df.region==region,]
    fig = px.pie(df, values='total_price', names='type',color='type',color_discrete_map={'gun_box':'#3768C3','character':'#EE731F','emote':'#9F9E9E','pet':'#FEC601','cloth':'#00CED1','token_box':'#DB7093','other':'#E6E6E6'})
    fig.update_traces(textposition='outside', textinfo='percent+label',marker=dict(line=dict(color='#FFFFFF', width=3)))
    fig.update_layout(
        title=dict(text="<b>Gem Consumption by Type</b>",font_family="Verdana",x=0.5,y=1),
        font = dict(color='#000000',size=11,family="Verdana"),
        legend=dict(font_size=11,font_family="Verdana",orientation="h",y=-0.2),
        height=450
    )
    return fig 

@app.callback(
    Output('pie_chart_2', 'figure'),
    [Input('time_dropdown_2','value'),
    Input('region_dropdown3','value')]
)
def update_figure(time,region):
    df = gun_box_power.loc[gun_box_power.if_latest==time,]
    if region == 'ALL':
        df = df.groupby('power').agg({'total_price':'sum'}).reset_index()
    else:
        df = df.loc[df.region==region,]    
    fig = px.pie(df, values='total_price', names='power',color='power',color_discrete_map={'strong power':'#3768C3','low power':'#EE731F','no power':'#9F9E9E'})
    fig.update_traces(textposition='outside', textinfo='percent+label',marker=dict(line=dict(color='#FFFFFF', width=3)))
    fig.update_layout(
        title= dict(text="<b>Gun Box Consumption by Power</b>",font_family="Verdana",x=0.5,y=1),
        font = dict(color='#000000',size=11,family='Verdana'),
        legend=dict(font_size=11,font_family="Verdana",orientation="h",x=0.1,y=-0.2),
        height=450
    )
    return fig 

@app.callback(
    Output('consumption_line', 'figure'),
    [Input('time_dropdown_2','value'),
    Input('region_dropdown3','value')]
)
def update_figure(time,region):
    if region == 'ALL':
        df = type_consume.groupby(['local_dt','type']).agg({'total_price':'sum'}).reset_index()
    else:
        df = type_consume.loc[type_consume.region==region,]
    df = df.sort_values(by='local_dt',ascending=True)
    color_dict={'gun_box':'#3768C3','character':'#EE731F','emote':'#9F9E9E','pet':'#FEC601','cloth':'#00CED1','token_box':'#DB7093'}
    data = []
    for i in ('gun_box','character','emote','pet','cloth','token_box'):
        trace = go.Scatter(x=[datetime.datetime.strptime(str(i), '%Y%m%d') for i in list(df.loc[df.type==i,'local_dt'].unique())],
                            y=[get_round_num(i) for i in df.loc[df.type==i,'total_price'].to_list()],
                            name=i,
                            mode = 'lines',
                            text = [get_round_num(i) for i in df.loc[df.type==i,'total_price'].to_list()],
                            line=dict(color=color_dict[i]))
        data.append(trace)
    layout = dict(title = dict(text='<b>Gem Consumption Trend by Item Type</b>',x=0.5,y=0.9,font_color="#444444",font_size=18,font_family='verdana'),
                plot_bgcolor='#FFFFFF',
                xaxis=dict(showline=True,showgrid=False,linecolor='#000000',linewidth=2,tickfont =dict(size = 11,family='verdana')),
                yaxis=dict(showgrid=False,tickfont =dict(size = 11,family='verdana')),
                legend=dict(orientation="h",x=0.28,font_family='verdana',font_size=11),
                height=400
                )
    fig = go.Figure(data,layout)     
    return fig

@app.callback(
    Output('conversion_bar', 'figure'),
    [Input('time_dropdown_2','value'),
    Input('region_dropdown3','value')]
)
def update_figure(time,region):
    if region == 'ALL':
        df = type_conversion.groupby(['local_dt','type']).agg({'click_num':'sum','purchase_num':'sum'}).reset_index()
        df['conversion_rate'] = df['purchase_num']/df['click_num']
    else:
        df = type_conversion.loc[type_conversion.region==region,]
    df = df.sort_values(by='local_dt',ascending=True)
    color_dict={'gun_box':'#3768C3','character':'#EE731F','emote':'#9F9E9E','pet':'#FEC601','cloth':'#00CED1','token_box':'#DB7093','other':'#E6E6E6'}
    data = []
    for i in ('gun_box','character','emote','pet','cloth','token_box','other'):
        trace = go.Scatter(x=[datetime.datetime.strptime(str(i), '%Y%m%d') for i in list(df.loc[df.type==i,'local_dt'].unique())],
                            y=df.loc[df.type==i,'conversion_rate'],
                            name=i,
                            mode = 'lines',
                            text = [str(round(i*100,2))+'%' for i in df.loc[df.type==i,'conversion_rate'].to_list()],
                            line=dict(color=color_dict[i]))
        data.append(trace)
    layout = dict(title = dict(text='<b>Conversion Rate by Item Type(Purchase times/Click times)</b>',x=0.5,y=0.9,font_color="#444444",font_size=18,font_family='verdana'),
                plot_bgcolor='#FFFFFF',
                xaxis=dict(showline=True,showgrid=False,linecolor='#000000',linewidth=2,tickfont =dict(size = 11,family='verdana')),
                yaxis=dict(tickformat="%",showgrid=False,tickfont =dict(size = 11,family='verdana')),
                legend=dict(orientation="h",x=0.28,font_family='verdana',font_size=11),
                height=400
                )
    fig = go.Figure(data,layout)     
    return fig


@app.callback(
    Output('table', 'columns'),
    [Input('time_dropdown_3','value'),
    Input('tabs','value'),
    Input('region_dropdown4','value')]
) 
def update_figure(time,tabs,region):
    df = top10.loc[(top10.if_latest==time)&(top10.type==tabs)&(top10.region==region),['rank','name','total_cost','conversion','price','item_id']]
    y_columns = df.columns.tolist()
    return ([{"name": 'Rank', "id": 'rank','type':'numeric'}] +
            [{"name": 'Name', "id": 'name','type':'text'}] +
            [{"name": 'Total Cost', "id": 'total_cost','type':'numeric','format':GetFormat.three_d_format(0)}] +
            [{"name": 'Conversion', "id": 'conversion','type':'numeric','format':GetFormat.percentage(2)}] +
            [{"name": 'Price', "id": 'price','type':'numeric','format':GetFormat.roundnum(0)}] +
            [{"name": 'ID', "id": 'item_id','type':'numeric'}])

@app.callback(
    Output('table', 'data'),
    [Input('time_dropdown_3','value'),
    Input('tabs','value'),
    Input('region_dropdown4','value')]
)
def update_figure(time,tabs,region):
    df = top10.loc[(top10.if_latest==time)&(top10.type==tabs)&(top10.region==region),['rank','name','total_cost','conversion','price','item_id']]
    return df.to_dict('records')

@app.callback(
    Output('table', 'style_data_conditional'),
    [Input('time_dropdown_3','value'),
    Input('tabs','value'),
    Input('region_dropdown4','value')]
)
def update_figure(time,tabs,region):
    df = top10.loc[(top10.if_latest==time)&(top10.type==tabs)&(top10.region==region),['total_cost']]
    return (GetColorBar.data_bars(df,'total_cost',no_color_cell=0,color = '#FFDEAD'))

tags = {
    'character':['Character','#EE731F'],
    'emote':['Emote','#9F9E9E'],
    'gun_box':['Gun Box','#3768C3'],
    'pet':['Pet','#FEC601'],
    'cloth':['Cloth','#00CED1'],
    'token_box':['Token Box','#DB7093']
}

@app.callback(
    Output('line', 'figure'),
    [Input('time_dropdown_3','value'),
    Input('rmv_dropdown_1','value'),
    Input('tabs','value'),
    Input('region_dropdown4','value')]
)
def update_figure(time,val,tabs,region):
    df = purchase_all.loc[(purchase_all.if_latest==time)&(purchase_all.type==tabs)&(purchase_all.region==region)&(purchase_all['rank']>val),['type','rank','total_cost']]
    df['rank'] = np.arange(1,len(df)+1)
    df['cost_cum'] = df.groupby('type')['total_cost'].cumsum()
    df['percent'] = df['cost_cum']/max(df['cost_cum'])
    x_val = [0] + df['rank'].to_list()
    y_val = [0] + df['percent'].to_list()
    trace = go.Scatter(
        x = x_val,
        y = y_val,
        mode='lines',
        line=dict(color=tags[tabs][1],width=2)
        )
    data = [trace]
    layout = dict(title_text=f"<b>Cumulative Distribution of {tags[tabs][0]}</b>",
                  title_x=0.5,
                  title_font_family="Verdana",
                  font = dict(color='#000000',size=11,family='verdana'),
                  plot_bgcolor='#FFFFFF',
                  xaxis=dict(showline=True,showgrid=False,linecolor='#000000',linewidth=1,tickfont =dict(size = 11,family='verdana')),
                  yaxis=dict(tickformat="%",showgrid=False,tickfont =dict(size = 11,family='verdana')),
                  height=350)
    fig = go.Figure(data,layout)
    return fig 

@app.callback(
    Output('table_2', 'columns'),
    [Input('time_dropdown_4','value'),
     Input('region_dropdown','value')]
)
def update_figure(time,region):
    df = top30.loc[(top30.if_latest==time)&(top30.region==region),['rank','name','type','total_cost','total_sold','conversion','price','item_id']]
    y_columns = df.columns.tolist()
    return ([{"name": 'Rank', "id": 'rank','type':'numeric'}] +
            [{"name": 'Name', "id": 'name','type':'text'}] +
            [{"name": 'Total Cost', "id": 'total_cost','type':'numeric','format':GetFormat.three_d_format(0)}] +
            [{"name": 'Total Sold', "id": 'total_sold','type':'numeric','format':GetFormat.three_d_format(0)}] +
            [{"name": 'Conversion', "id": 'conversion','type':'numeric','format':GetFormat.percentage(2)}] +
            [{"name": 'Price', "id": 'price','type':'numeric','format':GetFormat.roundnum(0)}] +
            [{"name": 'ID', "id": 'item_id','type':'numeric'}])

@app.callback(
    Output('table_2', 'data'),
    [Input('time_dropdown_4','value'),
     Input('region_dropdown','value')]
)
def update_figure(time,region):
    df = top30.loc[(top30.if_latest==time)&(top30.region==region),['rank','name','type','total_cost','total_sold','conversion','price','item_id']]
    return df.to_dict('records')

@app.callback(
    Output('table_2', 'style_data_conditional'),
    [Input('time_dropdown_4','value'),
     Input('region_dropdown','value')]
)
def update_figure(time,region):
    df1 = top30.loc[(top30.if_latest==time)&(top30.region==region),['total_cost']]
    df2 = top30.loc[(top30.if_latest==time)&(top30.region==region),['total_sold']]
    return (GetColorBar.data_bars(df1,'total_cost',no_color_cell=0,color = '#FFDEAD')+
            GetColorBar.data_bars(df2, 'total_sold',no_color_cell=0,color = '#FFDEAD')) 


@app.callback(
    Output('line_regions', 'figure'),
    [Input('time_dropdown_3','value'),
    Input('region_dropdown','value'),
    Input('rmv_dropdown_5','value')]
)
def update_figure(time,region,val):
    df = purchase_regions.loc[(purchase_regions.if_latest==time)&(purchase_regions.region==region)&(purchase_regions['rank']>val),['region','rank','total_cost']]
    df['rank'] = np.arange(1,len(df)+1)
    df['cost_cum'] = df.groupby('region')['total_cost'].cumsum()
    df['percent'] = df['cost_cum']/max(df['cost_cum'])
    x_val = [0] + df['rank'].to_list()
    y_val = [0] + df['percent'].to_list()
    trace = go.Scatter(
        x = x_val,
        y = y_val,
        mode='lines',
        line=dict(color='#c43c3c',width=2)
        )
    data = [trace]
    layout = dict(title_text="<b>Cumulative Distribution</b>"+'<b>('+region+')</b>',
                  title_x=0.5,
                  title_font_family="Verdana",
                  font = dict(color='#000000',size=11,family='verdana'),
                  plot_bgcolor='#FFFFFF',
                  xaxis=dict(showline=True,showgrid=False,linecolor='#000000',linewidth=1,tickfont =dict(size = 11,family='verdana')),
                  yaxis=dict(tickformat="%",showgrid=False,tickfont =dict(size = 11,family='verdana')),
                  height=300)
    fig = go.Figure(data,layout)
    return fig 


@app.callback(
    Output('table_3', 'figure'),
    [Input('time_dropdown_4','value'),
     Input('region_dropdown','value')]
)
def update_figure(time,region):
    df = null_item
    trace = go.Table(
        columnwidth = [10,10,20,20],
        header=dict(values=['Item id','Type','Total cost','Total sold'],line_color='#000000',fill_color='#F05A63',font=dict(color='#FFFFFF',size=11,family='Verdana')),
        cells=dict(values=[df['item_id'].to_list(),df['type'].to_list(),df['total_cost'].apply(give_num_format).to_list(),df['total_sold'].apply(give_num_format).to_list()],
                   line_color='#000000',fill_color='#FFFFFF',font=dict(color='#000000',size=11,family='Verdana'),align='left')
    )
    data = [trace]
    layout = dict(height=200,margin={'l':10, 'b': 10,'t': 10})
    fig = go.Figure(data,layout)
    return fig 


@app.callback(
    dash.dependencies.Output('my-link-1', 'href'),
    [dash.dependencies.Input('time_dropdown_3', 'value'),
    dash.dependencies.Input('region_dropdown4','value')])
def update_download_link(time,region):
    xlsx_io = io.BytesIO()
    writer = pd.ExcelWriter(xlsx_io, engine='xlsxwriter')
    df = top10.loc[(top10.if_latest==time)&(top10.region==region),['rank','name','total_cost','conversion','price','item_id']]
    df.to_excel(writer,index=False)
    writer.save()
    xlsx_io.seek(0)
    media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    data = base64.b64encode(xlsx_io.read()).decode("utf-8")
    href_data_downloadable = f'data:{media_type};base64,{data}'
    return href_data_downloadable 

@app.callback(
    dash.dependencies.Output('my-link-2', 'href'),
    [dash.dependencies.Input('time_dropdown_4', 'value'),
    dash.dependencies.Input('region_dropdown','value')])
def update_download_link(time,region):
    xlsx_io = io.BytesIO()
    writer = pd.ExcelWriter(xlsx_io, engine='xlsxwriter')
    df = top30.loc[top30.if_latest==time,['region','rank','name','total_cost','conversion','total_sold','price','item_id']]
    df.to_excel(writer,index=False)
    writer.save()
    xlsx_io.seek(0)
    media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    data = base64.b64encode(xlsx_io.read()).decode("utf-8")
    href_data_downloadable = f'data:{media_type};base64,{data}'
    return href_data_downloadable 

if __name__ == '__main__':
    app.run_server(debug=True)