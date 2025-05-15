import dash
from dash import dcc, html, dash_table, Input, Output, callback
import plotly.express as px
import pandas as pd
import numpy as np
from dash.dash_table.Format import Group
import dash_bootstrap_components as dbc

# Инициализация Dash-приложения
class dash_app():
    def __init__(self, df):
        categories = df['req'].unique().tolist()
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
        self.server = self.app.server

        # Навигационное меню
        navbar = dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Главная", href="/")),
                dbc.NavItem(dbc.NavLink("Данные", href="/data")),
                dbc.NavItem(dbc.NavLink("EDA", href="/eda")),
                dbc.NavItem(dbc.NavLink("Тренды", href="/trends")),
                dbc.NavItem(dbc.NavLink("Выводы", href="/conclusions")),
            ],
            brand="Яндекс Маркет: Анализ цен и рейтингов",
            brand_href="/",
            color="primary",
            dark=True,
        )

        # Стиль для контента страниц
        CONTENT_STYLE = {
            "margin": "2rem",
            "padding": "2rem",
            "maxWidth": "1200px",
            "marginLeft": "auto",
            "marginRight": "auto"
        }

        # Главная страница
        home_layout = html.Div([
            html.H2("Анализ зависимости ценовой категории и рейтинга цифровых устройств на Яндекс Маркете"),
            html.P("""
                Этот дэшборд позволяет исследовать взаимосвязь между ценовой категорией товаров и их рейтингом 
                на платформе Яндекс Маркет. Используйте навигационное меню для перехода между разделами анализа.
            """),
            html.Hr(),
            html.H4("Описание данных"),
            html.P("""
                Датасет содержит информацию о товарах из следующих категорий: Мышь, Клавиатура, Телевизор, 
                Монитор, Камера, Ноутбук, Смартфон, Микрофон, Наушники, Компьютер.
            """),
            html.P("""
                Для каждого товара доступны: название, цена, рейтинг, количество отзывов и ссылка на товар.
            """),
            html.P("""
                Ценовые категории разделены на 4 квартиля.
            """),
        ], style=CONTENT_STYLE)

        # Раздел с данными
        data_layout = html.Div([
            html.H2("Данные Яндекс Маркета", style=CONTENT_STYLE),
            html.Div([
                dbc.Row([
                    dbc.Col(dbc.Card([
                        dbc.CardHeader("Всего записей"),
                        dbc.CardBody([
                            html.H4(id='total-records', className="card-title")
                        ])
                    ]), md=3),
                    dbc.Col(dbc.Card([
                        dbc.CardHeader("Пропуски в данных"),
                        dbc.CardBody([
                            html.H4(id='missing-values', className="card-title")
                        ])
                    ]), md=3),
                    dbc.Col(dbc.Card([
                        dbc.CardHeader("Средний рейтинг"),
                        dbc.CardBody([
                            html.H4(id='avg-rating', className="card-title")
                        ])
                    ]), md=3),
                    dbc.Col(dbc.Card([
                        dbc.CardHeader("Средняя цена"),
                        dbc.CardBody([
                            html.H4(id='avg-price', className="card-title")
                        ])
                    ]), md=3),
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col(dcc.Graph(id='category-dist'), md=6),
                    dbc.Col(dcc.Graph(id='price-dist'), md=6),
                ]),
                html.Br(),
                html.H4("Интерактивная таблица данных"),
                dash_table.DataTable(
                    id='datatable',
                    columns=[
                        {"name": i, "id": i, "deletable": False, "selectable": True} 
                        for i in df.columns if i != 'link'
                    ],
                    data=df.to_dict('records'),
                    editable=False,
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    column_selectable=False,
                    row_selectable=False,
                    row_deletable=False,
                    selected_columns=[],
                    selected_rows=[],
                    page_action="native",
                    page_current=0,
                    page_size=10,
                    style_table={
                        'overflowX': 'auto',
                        'margin': '1rem 0'
                    },
                    style_cell={
                        'height': 'auto',
                        'minWidth': '100px', 
                        'width': '100px', 
                        'maxWidth': '180px',
                        'whiteSpace': 'normal',
                        'padding': '8px'
                    },
                    style_header={
                        'backgroundColor': 'rgb(230, 230, 230)',
                        'fontWeight': 'bold',
                        'padding': '8px'
                    },
                ),
            ], style=CONTENT_STYLE)
        ])

        # Раздел EDA
        eda_layout = html.Div([
            html.H2("Первичный анализ данных (EDA)"),
            dbc.Row([
                dbc.Col(dcc.Graph(
                    figure=px.box(df, x='req', y='price', color='req', 
                                 title='Распределение цен по категориям',
                                 labels={'req': 'Категория', 'price': 'Цена'})
                ), md=6),
                dbc.Col(dcc.Graph(
                    figure=px.box(df, x='req', y='rating', color='req', 
                                 title='Распределение рейтингов по категориям',
                                 labels={'req': 'Категория', 'rating': 'Рейтинг'})
                ), md=6),
            ], style={"margin": "1rem 0"}),
            html.Br(),
            dbc.Row([
                dbc.Col(dcc.Graph(
                    figure=px.histogram(df, x='rating', nbins=20, 
                                      title='Распределение рейтингов',
                                      labels={'rating': 'Рейтинг'}),
                ), md=6),
                dbc.Col(dcc.Graph(
                    figure=px.imshow(
                        df[['price', 'rating', 'reviews']].corr(),
                        title='Корреляция между числовыми переменными',
                        labels=dict(x="Переменная", y="Переменная", color="Корреляция"),
                        x=['Цена', 'Рейтинг', 'Отзывы'],
                        y=['Цена', 'Рейтинг', 'Отзывы'],
                        color_continuous_scale='RdBu',
                        zmin=-1,
                        zmax=1,
                        text_auto=True
                    ),
                ), md=6),
            ], style={"margin": "1rem 0"}),
            html.Br(),
            dbc.Row([
                dbc.Col(dcc.Graph(
                    figure=px.scatter(df, x='reviews', y='rating', color='req',
                                    title='Зависимость рейтинга от количества отзывов',
                                    labels={'reviews': 'Количество отзывов', 'rating': 'Рейтинг'}),
                ), md=12),
            ], style={"margin": "1rem 0"}),
        ], style=CONTENT_STYLE)

        # Раздел с трендами
        trends_layout = html.Div([
            html.H2("Тренды и закономерности"),
            dbc.Row([
                dbc.Col([
                    html.Label("Выберите категории:"),
                    dcc.Dropdown(
                        id='category-selector',
                        options=[{'label': cat, 'value': cat} for cat in categories],
                        value=categories,
                        multi=True,
                        style={"marginBottom": "1rem"}
                    ),
                ], md=6),
                dbc.Col([
                    html.Label("Выберите ценовые категории:"),
                    dcc.Dropdown(
                        id='price-category-selector',
                        options=[
                            {'label': 'Q1', 'value': 'Q1'},
                            {'label': 'Q2', 'value': 'Q2'},
                            {'label': 'Q3', 'value': 'Q3'},
                            {'label': 'Q4', 'value': 'Q4'}
                        ],
                        value=['Q1', 'Q2', 'Q3', 'Q4'],
                        multi=True,
                        style={"marginBottom": "1rem"}
                    ),
                ], md=6),
            ], style={"margin": "1rem 0"}),
            html.Br(),
            dbc.Row([
                dbc.Col(dcc.Graph(id='price-vs-rating'), md=6),
                dbc.Col(dcc.Graph(id='category-price-trend'), md=6),
            ], style={"margin": "1rem 0"}),
            html.Br(),
            dbc.Row([
                dbc.Col(dcc.Graph(id='price-category-rating'), md=6),
                dbc.Col(dcc.Graph(id='reviews-vs-rating'), md=6),
            ], style={"margin": "1rem 0"}),
        ], style=CONTENT_STYLE)

        # Раздел с выводами
        conclusions_layout = html.Div([
            html.H2("Выводы и рекомендации"),
            dbc.Card([
                dbc.CardHeader("Ключевые инсайты"),
                dbc.CardBody([
                    html.Ul([
                        html.Li("Существует слабая положительная корреляция(0.21) между ценой и рейтингом товаров"),
                        html.Li("Премиум сегмент показывает более стабильно высокие рейтинги по сравнению с бюджетным"),
                        html.Li("Количество отзывов не связано с рейтингом товара"),
                        html.Li("В бюджетном сегменте наблюдается больший разброс рейтингов, поэтому лучше покупать не самые дешёвые товары(меньше шанс, что товар окажется ненадлежащего качества)"),
                    ], style={"paddingLeft": "2rem"})
                ])
            ], style={"marginBottom": "2rem"}),
            dbc.Card([
                dbc.CardHeader("Дальнейшие шаги"),
                dbc.CardBody([
                    html.Ul([
                        html.Li("Сбор дополнительных данных: бренды, дата добавления товара, технические характеристики"),
                        html.Li("Анализ текстовых отзывов для выявления причин низких рейтингов"),
                        html.Li("Сравнение с конкурентами (Wildberries, Ozon, Ситилинк)"),
                        html.Li("Добавление временного анализа для выявления динамики изменения рейтингов"),
                    ], style={"paddingLeft": "2rem"})
                ])
            ]),
        ], style=CONTENT_STYLE)

        self.app.layout = html.Div([
            dcc.Location(id='url', refresh=False),
            navbar,
            html.Div(id='page-content')
        ])

        @callback(
            Output('page-content', 'children'),
            [Input('url', 'pathname')]
        )
        def display_page(pathname):
            if pathname == '/data':
                return data_layout
            elif pathname == '/eda':
                return eda_layout
            elif pathname == '/trends':
                return trends_layout
            elif pathname == '/conclusions':
                return conclusions_layout
            else:
                return home_layout

        @callback(
            [Output('total-records', 'children'),
             Output('missing-values', 'children'),
             Output('avg-rating', 'children'),
             Output('avg-price', 'children')],
            [Input('datatable', 'data')]
        )
        def update_summary(data):
            df_summary = pd.DataFrame(data)
            total = len(df_summary)
            missing = df_summary.isnull().sum().sum()
            avg_rating = round(df_summary['rating'].mean(), 2)
            avg_price = f"{int(df_summary['price'].mean()):,}".replace(",", " ")
            return total, missing, avg_rating, avg_price

        @callback(
            Output('category-dist', 'figure'),
            [Input('datatable', 'data')]
        )
        def update_category_dist(data):
            df_plot = pd.DataFrame(data)
            fig = px.pie(df_plot, names='req', title='Распределение по категориям')
            return fig

        @callback(
            Output('price-dist', 'figure'),
            [Input('datatable', 'data')]
        )
        def update_price_dist(data):
            df_plot = pd.DataFrame(data)
            fig = px.histogram(df_plot, x='price_category', title='Распределение по ценовым категориям')
            return fig

        @callback(
            [Output('price-vs-rating', 'figure'),
             Output('category-price-trend', 'figure'),
             Output('price-category-rating', 'figure'),
             Output('reviews-vs-rating', 'figure')],
            [Input('category-selector', 'value'),
             Input('price-category-selector', 'value')]
        )
        def update_trends(selected_categories, selected_price_cats):
            filtered_df = df[df['req'].isin(selected_categories) & df['price_category'].isin(selected_price_cats)]
            
            fig1 = px.scatter(
                filtered_df, x='price', y='rating', color='req',
                title='Зависимость рейтинга от цены',
                labels={'price': 'Цена', 'rating': 'Рейтинг'}
            )
            
            avg_prices = filtered_df.groupby('req')['price'].mean().reset_index()
            fig2 = px.bar(
                avg_prices, x='req', y='price',
                title='Средняя цена по категориям',
                labels={'req': 'Категория', 'price': 'Средняя цена'}
            )
            
            fig3 = px.box(
                filtered_df, x='price_category', y='rating', color='price_category',
                title='Распределение рейтингов по ценовым категориям',
                labels={'price_category': 'Ценовая категория', 'rating': 'Рейтинг'}
            )
            
            fig4 = px.scatter(
                filtered_df, x='reviews', y='rating', color='req',
                title='Зависимость рейтинга от количества отзывов',
                labels={'reviews': 'Количество отзывов', 'rating': 'Рейтинг'}
            )
            
            return fig1, fig2, fig3, fig4

