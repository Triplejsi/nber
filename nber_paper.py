import json
import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
import requests
import seaborn as sns
import statistics
import warnings
from glob import glob

# set xkcd mode for plotting
font_manager._rebuild()
plt.xkcd()

# ignore warning
warnings.filterwarnings('ignore')

def bar_plot(df, label, title, column):
    fig, ax = plt.subplots(figsize=(15, 5))
    bar_width = 0.35
    opacity = 0.9
    ax.bar(
        df.index,
        height='count',
        width=0.5,
        data=df,
        alpha=opacity,
        color='black',
        label=label
    )
    plt.title(title)
    plt.ylabel('Jumlah paper')
    plt.xticks(df.index)
    plt.yticks()
    
    caption = lambda df, column: ' \n'.join([f'{df.index[x]}: {df[column][x]}' for x in range(len(df))])
    plt.xlabel(caption(df, column), loc='left')
    vals = ax.get_yticks()
    ax.legend()
    plt.show()
    
def citation(df):
    df = df[['cites', 'cited_by']]
    fig, ax = plt.subplots(figsize=(15, 5))
    plt.scatter(x='cites', y='cited_by', data=df, c='black')
    plt.title('Citations in NBER (no causality implied)')
    plt.xlabel('Total cites per paper')
    plt.ylabel('Total cited per paper')
    plt.show
    
def citation_density(df):
    # log scale
    df['log_total_cites'] = df.apply(lambda x: np.log(x['cites']), axis=1)
    df['log_cited_by'] = df.apply(lambda x: np.log(x['cited_by']), axis=1)

    # visualize
    fig, ax = plt.subplots(figsize=(15, 5))
    # must be > 0 otherwise error appears
    sns.kdeplot(df[df['log_total_cites'] > 0]['log_total_cites'], shade=True, color='red')
    sns.kdeplot(df[df['log_cited_by'] > 0]['log_cited_by'], shade=True, color='blue')

    # show median values
    log_total_cites_median = np.median(df['log_total_cites'][~np.isnan(df['log_total_cites'])])
    log_cited_by_median = np.median(df['log_cited_by'][~np.isnan(df['log_cited_by'])])
    
    ax.axvline(log_total_cites_median, color='red')
    ax.axvline(log_cited_by_median, color='blue')

    # exponentiate median values
    total_cites = int(np.exp(log_total_cites_median))
    cited_by = int(np.exp(log_cited_by_median))

    caption = f"Vertical lines show median citations: \n \tTotal cites: {total_cites} \n \tTotal cited by: {cited_by}"
    plt.title('Distributions of citations in NBER (log scale)')
    fig.text(0.1, -0.05, caption)
    
def collaboration(df):
    # transform data
    df = df[df['citation_publication_date'].isna() == False]
    df = df[['citation_publication_date', 'citation_author']]
    df['total_author'] = df.apply(lambda x: len(x['citation_author']), axis=1)
    df['year'] = df.apply(lambda x: x['citation_publication_date'][:4], axis=1)
    df = df[df['year'] != 'None']
    df['year'] = df['year'].astype(int)
    df = df.groupby('year')['total_author'].agg('median')
    df = df.to_frame().reset_index()
    df = df.rename(columns={'total_author': 'median_total_author'})
    
    # visualize data
    fig, ax = plt.subplots(figsize=(15, 5))
    plt.plot('year', 'median_total_author', data=df, color='black')
    plt.title(f'Median total authors per paper each year')
    plt.xlabel('Year')
    plt.ylabel('Median total author')
    plt.xticks(np.arange(df.year.min(), df.year.max()+1, 3))
    plt.yticks(np.arange(min(df['median_total_author']), max(df['median_total_author'])+1, 1))
    plt.show
    
def count_by_year(df):
    df = df[df['citation_publication_date'].isna() == False]
    count = df[['id', 'citation_publication_date']]
    count['citation_publication_date'] = count.apply(lambda x: x['citation_publication_date'][:4], axis=1)
    count = count.groupby('citation_publication_date').size().to_frame().reset_index()
    count = count.rename(columns={0: 'count', 'citation_publication_date': 'year'})
    
    return count
    
def get_data(file_name):
    df = glob(f'data/{file_name}/*')
    df = [json.load(open(x, 'r')) for x in df]
    df = pd.DataFrame(df)
    
    return df

def published_paper(df, title, x_interval=1, y_interval=1):
    df = df[df['year'] != 'None']
    df['year'] = df['year'].astype(int)
    fig, ax = plt.subplots(figsize=(15, 5))
    plt.plot('year', 'count', data=df, color='black')
    plt.title(title)
    plt.xlabel('Year')
    plt.ylabel('Total paper')
    plt.xticks(np.arange(df.year.min(), df.year.max()+1, x_interval))
    plt.yticks(np.arange(0, max(df['count']), y_interval))
    plt.show
    
def section_trends(df, column, title, keyword, x_interval, y_interval):
    # transform data
    df = df[['citation_publication_date', column]]
    df[column] = df[column].fillna('N/A')
    df.loc[:, 'year'] = df.apply(lambda x: x['citation_publication_date'][:4], axis=1)
    df = df[df['year'] != 'None']
    df['year'] = df['year'].astype(int)
    df.loc[:, column] = df.apply(lambda x: x[column].lower(), axis=1)
    df = df[df.apply(lambda x: keyword in x[column], axis=1) == True]
    df = df.groupby('year').size().to_frame().reset_index()
    df = df.rename(columns={0: 'count'})

    # visualize tiem series
    fig, ax = plt.subplots(figsize=(15, 5))
    plt.plot('year', 'count', data=df, color='black')
    plt.title(f'NBER trends: {title} in the {column} section in NBER')
    plt.xlabel('Year')
    plt.ylabel('Total paper')
    plt.xticks(np.arange(df.year.min(), df.year.max()+1, x_interval))
    plt.yticks(np.arange(0, max(df['count']), y_interval))
    plt.show
    
def top_five(df, column='topics'):
    df = df[df[column].isna() == False]
    df = df[[column]]
    df = df.explode(column)
    df = df.groupby(column).size().to_frame().reset_index()
    df = df.rename(columns={0: 'count'})
    df = df.sort_values(by='count', ascending=False)
    df = df[~df[column].isin(['', ', '])]
    df = df.reset_index(drop=True)
    df = df.iloc[:5, :]
    
    return df

def top_five_trends(df, column, title):
    # transform
    df = df[['citation_publication_date', column]]
    df = df.explode(column)
    df['year'] = df.apply(lambda x: x['citation_publication_date'][:4], axis=1)
    df = df[df['year'] != 'None']
    df['year'] = df['year'].astype(int)
    df = df[['year', column]]
    top_five = df.groupby(column).size().to_frame().reset_index().sort_values(by=0, ascending=False)
    top_five = top_five.reset_index(drop=True)[:5][column].to_list()
    df = df[df[column].isin(top_five)]
    dfs = [df[df[column] == x].groupby('year').size() for x in top_five]
    dfs = [x.to_frame().reset_index().rename(columns={0: 'count'}) for x in dfs]
    
    # visualize
    fig, ax = plt.subplots(figsize=(15, 5))
    plt.plot('year', 'count', data=dfs[0], color='black')
    plt.plot('year', 'count', '--', data=dfs[1], color='red')
    plt.plot('year', 'count', data=dfs[2], color='blue')
    plt.plot('year', 'count', '--', data=dfs[3], color='green')
    plt.plot('year', 'count', data=dfs[4], color='orange')
    plt.title(title)
    plt.xlabel('Year')
    plt.ylabel('Total paper')
    plt.xticks(np.arange(df.year.min(), df.year.max()+1, 3))
    ax.legend(labels=top_five)
    plt.show()
