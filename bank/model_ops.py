import pytz
from django.utils import timezone
from bank.generator import regNumber
import datetime as dt
tdelta = dt.timedelta(days=31)

def cpy(srcObj, dstObj):
    srcList = []
    i = 0
    for src_field in srcObj._meta.fields:
        if not src_field.primary_key:
            srcList.append(src_field)

    for dst_field in dstObj._meta.fields:
        if not dst_field.primary_key:
            if dst_field.name == srcList[i].name:
                dst_field = srcList[i]
                setattr(dstObj, dst_field.name,
                        getattr(srcObj, srcList[i].name))
                i += 1
            else:
                print('Column Mismatch...')
                print(srcList[i].name + ' -:- ' + dst_field.name)
    dstObj.save()
    return dstObj


def mve(request, srcObj, dstObj):
    srcList = []
    i = 0
    for src_field in srcObj._meta.fields:
        if not src_field.primary_key:
            srcList.append(src_field)

    for dst_field in dstObj._meta.fields:
        if not dst_field.primary_key:
            if dst_field.name == 'claimer':
                setattr(dstObj, dst_field.name, request.user)
                i += 1
            elif dst_field.name == 'reference':
                setattr(dstObj, dst_field.name, regNumber())
                i += 1
            elif dst_field.name == 'claim_date':
                setattr(dstObj, dst_field.name, str(timezone.now()))
                i += 1
            elif dst_field.name == 'viewed':
                setattr(dstObj, dst_field.name, 0)
                i += 1
            elif dst_field.name == 'dealStatus':
                setattr(dstObj, dst_field.name, 'Pending')
                i += 1
            elif dst_field.name == 'dealComment':
                setattr(dstObj, dst_field.name, ' ')
                i += 1
            elif dst_field.name == 'claim_exp_date':
                setattr(dstObj, dst_field.name, str(timezone.now()+tdelta))
                i += 1
            elif dst_field.name == srcList[i].name:
                dst_field = srcList[i]
                setattr(dstObj, dst_field.name,
                        getattr(srcObj, srcList[i].name))
                i += 1
            else:
                print('Column Mismatch...')
                print(srcList[i].name + ' -:- ' + dst_field.name)
    dstObj.save()
    srcObj.delete()
    return dstObj
