import pickle
import glob
import os
import matplotlib.pyplot as plt
import matplotlib.text as text
import numpy as np

curr_dir = os.path.dirname(__file__)
data_path = os.path.join(curr_dir, 'Receipt data/data')
aldelo_path = os.path.join(data_path, 'Aldelo')
pkl_path = os.path.join(aldelo_path, 'line_item_pkls')

pkl_files = glob.glob(pkl_path + '/*.pkl')

for pkl in pkl_files:
    plt.clf()
    store_name = pkl.split("/")[-1].split("_")[0]
    line_items = pickle.load(open(pkl))
    list_of_costs = [float(receipt.get('cost')) for receipt in line_items if receipt.get('cost')]
    mean = np.mean(list_of_costs)
    std = np.std(list_of_costs)
    plt.hist(list_of_costs, 25, facecolor='green', alpha=0.75)

    plt.ylabel('price frequency')
    plt.xlabel('cost')
    title = r'{} \mu = {} \sigma = {}'.format(store_name, mean, std)
    plt.title(title)
    plt.savefig(store_name + '.png')
    plt.show()

    # plot pie chart
    # list_of_items = [receipt.get('main item') for receipt in line_items if receipt.get('main item')]
    # item_counts = {}
    # for item in list_of_items:
    #     if item_counts.get(item):
    #         item_counts[item] += 1
    #     else:
    #         item_counts[item] = 1
    # list_of_item_counts = [(item, count) for item, count in item_counts.iteritems()]
    # list_of_item_counts = sorted(list_of_item_counts, key=lambda x: x[1], reverse=True)
    # list_of_item_counts = list_of_item_counts[0:10]
    # list_of_item_counts = map(list, zip(*list_of_item_counts))
    # labels = list_of_item_counts[0]
    # sizes = list_of_item_counts[1]
    # colors = ['#a897c3', '#e7c980', '#b0adb2', '#cdb79e', '#faebd7']
    # plt.pie(sizes, autopct='%1.1f%%', labels=labels, colors=colors, startangle=90)
    # title = 'Distribution of Top 10 Line Items at ' + store_name
    # plt.title(title)
    # plt.savefig(store_name + 'pie' + '.png', bbox_inches='tight')

