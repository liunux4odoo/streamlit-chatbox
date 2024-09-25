import streamlit as st
from streamlit_raw_echarts import st_echarts,JsCode,CustomMap
import random


with st.echo('below'):
    option={
        'backgroundColor':'#fff',
        'title':{
            'text':'example chart',
            'subtext':'using pyecharts-assets',
        },
        'tooltip':{
            'trigger':'item',
        },
        'visualMap':{
            'seriesIndex':1,
        },
        'grid':{'bottom':'55%'},
        'xAxis':{
            'data':[1,2,3,4,5],
        },
        'yAxis':{},
        'series':[
            {
                'type':'bar',
                'name':'KPI',
                'data':[1,2,3,4,5],
                'label':{
                    'show':True,
                    'position':'top',
                },
                'visualMap':False,
                'color':JsCode('new echarts.graphic.LinearGradient(0,0,0,1,[{"offset":0,"color":"red"},{"offset":1,"color":"yellow"}])')             
            },
            {
                'name':'users',
                'type':'map',
                'mapType':'world',
                'top':'55%',
                'label':{'show':False},
                'roam':True,
                'data':[
                    {'name':'China','value':150,'label':{'show':True,'formatter':JsCode('function(p){return p.data.name+":"+p.value;}')}},
                    {'name':'United States','value':200,'label':{'show':True,'formatter':JsCode('function(p){return p.data.name+":"+p.value;}')}},
                    {'name':'Brazil','value':100},
                ]
            }
        ]
    }

    st.title('example:')

    for i in range(3):
        option['series'][1]['data'][i]['value']=random.randint(1,200)
    for i in range(5):
        option['series'][0]['data'][i]=random.randint(1,10)

    chart=st_echarts(option=option,
                    theme='shine',
                    height=600,
                    events={
                        'click':'function(param){alert("your click:"+param.data.name);}'
                        },
                    returnData={},
                    key='echarts1',
                    )
    st.button('refresh',help='update chart dynamiclly')
    if chart:
        st.write('the component returns as :')
        st.write(chart[:25]+' ... '+chart[-25:])
        st.markdown('<a href="{}" download="{}">download chart as picture</a>'.format(chart,'echarts1.png'),unsafe_allow_html=True)

from pathlib import Path
st.markdown(Path(__file__).parent.parent.absolute().joinpath(
    'README.md').read_text())