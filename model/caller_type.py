#!/usr/bin/env python3


class CallerType:
    HARASSMENT = 0
    FRAUD = 1
    AD = 2
    EXPRESS = 3
    RESTAURANT = 4
    GENERAL = 64


def from_name(name):
    if '骚扰' in name:
        return CallerType.HARASSMENT
    if '诈骗' in name or '欺诈' in name:
        return CallerType.FRAUD
    if '广告' in name or '推销' in name:
        return CallerType.AD
    if '快递' in name or 'EMS' in name or '顺丰' in name:
        return CallerType.EXPRESS
    if '送餐' in name or '外卖' in name:
        return CallerType.RESTAURANT
    return CallerType.GENERAL
