# -*- coding: utf-8 -*-
__author__ = 'jsz'
__version__ = 0.1

import csv
import random

def create_fake_dataset(size, num_of_attri, fill_ratio, name=None):
    if not name:
        name = 'fake_%d_%d_%.2f.csv' % (size, num_of_attri, fill_ratio)

    dataset_file = file(name, 'w')
    writer = csv.writer(dataset_file)
    dataset = []
    for i in xrange(size):
        dataset.append(create_fake_obj(num_of_attri, fill_ratio))
    writer.writerows(dataset)
    dataset_file.close()


def create_fake_obj(num_of_attri, fill_ratio):
    res = set()
    temp = int(num_of_attri * fill_ratio)
    while len(res) < temp:
        res.add(random.randint(1, num_of_attri))
    return list(res)


def get_dataset(name):
    dataset_file = file(name, 'r')
    reader = csv.reader(dataset_file)
    dataset = []
    for line in reader:
        dataset.append(trans_to_set(line))
    dataset_file.close()
    return dataset

def trans_to_set(line):
    res = set()
    for n in line:
        res.add(int(n))
    return res


if __name__ == '__main__':
    for size in range(1000, 11000, 1000):
        create_fake_dataset(size, 50, 0.4)
