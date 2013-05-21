#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on Mar 15, 2013

@author: rega
'''
        
def similar_list_calculating(l1, l2):
    """
    Tính similarity giữa 2 thành phần của 2 vector đặc trưng, công thức áp dụng 
    trong hàm này là tính hệ số Jaccard, nếu 2 thành phần càng giống nhau thì hệ số 
    Jaccard càng tiệm cận 1 và ngược lại nếu 2 thành phần càng khác nhau thì hệ số 
    Jaccard càng tiệm cận 0.
    
    @param l1: list 1st
    @param l2: list 2nd
    
    @return: float, hệ số Jaccard
    """
    if not isinstance(l1, list) and not isinstance(l1, tuple):
        l1 = l1.all()
    if not isinstance(l2, list) and not isinstance(l2, tuple):
        l2 = l2.all()
    shared_items = list(set(l1) & set(l2))
    if shared_items:
        n_shared_items = len(shared_items)
        global_max = len(l1) + len(l2) - n_shared_items
        return 1.0*n_shared_items/global_max
    else:
        return 0.0

def similar_number_calculating(n1, n2):
    """
    Tính similarity giữa 2 thành phần của 2 vector đặc trưng, công thức áp dụng 
    trong hàm này là tính hệ số Jaccard, nếu 2 thành phần càng giống nhau thì hệ số 
    Jaccard càng tiệm cận 1 và ngược lại nếu 2 thành phần càng khác nhau thì hệ số 
    Jaccard càng tiệm cận 0.
    
    @param n1: number 1st
    @param n2: number 2nd
    
    @return: float, hệ số Jaccard
    """
    # applied the formula:
    # score = (max(n1,n2) - diff(n1,n2))/max(n1,n2)
    min_value = min(n1, n2)
    max_value = max(n1, n2)
    return 1.0*min_value/max_value
    
