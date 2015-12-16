# -*- coding:utf-8 -*-
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from models import *
import urllib.parse
import json
import time


# view 分为网页版和移动版，移动版以mobile_开头


# 安卓post解码用
def m_decode(message):  # json字符串解码
    decodestr = urllib.parse.unquote(message.decode())
    decodestr = decodestr[11:]
    decode = json.loads(decodestr)
    return decode


# Create your views here.
@csrf_exempt
def register(request):
    name = request.POST['name']
    idcard = request.POST['idcard']
    realname = request.POST['realname']
    password = request.POST['password']
    try:
        context = {}
        context['key'] = "value"
        User.objects.get(name=name)
        return render(request, 'show/hello.html', context)
        # 判断用户名是否被注册
    except ObjectDoesNotExist:
        User.objects.create(name=name, passwd=password, idcard=idcard, realname=realname)
        try:
            context['name'] = request.session['username']
        finally:
            return render(request, 'show/index.html', context)


@csrf_exempt
def login(request):
    name = request.POST['name']
    password = request.POST['password']
    # 判断用户名是否被注册
    try:
        context = {}
        user = User.objects.get(name=name)
        if (user.passwd != password or user.verify == False):
            try:
                context['name'] = request.session['username']
            finally:
                return render(request, 'show/login.html', context)
        request.session['username'] = name
        try:
            context['name'] = request.session['username']
        finally:
            return render(request, 'show/index.html', context)
            # 判断用户名是否被注册
    except ObjectDoesNotExist:
        try:
            context['name'] = request.session['username']
        finally:
            return render(request, 'show/register.html', context)


@csrf_exempt
def logout(request):
    del request.session['username']
    context = []
    try:
        context['name'] = request.session['username']
    finally:
        return render(request, 'show/index.html', context)


@csrf_exempt
def searchhospname(request):
    hospname = request.GET["hospname"]
    hosplist = Hospital.objects.filter(name__contains=hospname)
    if hosplist.__len__() > 0:
        context = {}
        try:
            context['name'] = request.session['username']
        finally:
            context['hospitalList'] = []
            for hosp in hosplist:
                hosp1 = {}
                hosp1['id'] = hosp.id
                hosp1['name'] = hosp.name
                hosp1['loc'] = hosp.address
                hosp1['intro'] = hosp.contact
                context['hospitalList'].append(hosp1)
            try:
                context['name'] = request.session['username']
            finally:
                return render(request, 'show/hospitals.html', context)
                # 判断用户名是否被注册
    else:
        context = {}
        return render(request, 'show/hello.html', context)


@csrf_exempt
def searchdepartment(request, hospitalid):
    deplist = Department.objects.filter(hospital=hospitalid)
    context = {}
    context['hospitalid'] = hospitalid
    context['departments'] = []
    i = 0
    for dep in deplist:
        dep1 = {}
        dep1['id'] = dep.id
        dep1['name'] = dep.name
        dep1['doctors'] = []
        doclist = Doctor.objects.filter(department=dep.id)
        for doc in doclist:
            doc1 = {}
            doc1['id'] = doc.id
            doc1['tag'] = i
            i = i + 1
            doc1['name'] = doc.name
            doc1['rank'] = doc.rank
            doc1['price'] = doc.fee
            doc1['limit'] = doc.limit
            dep1['doctors'].append(doc1)
        context['departments'].append(dep1)
    try:
        context['name'] = request.session['username']
    finally:
        return render(request, 'show/select.html', context)


@csrf_exempt
def showlist(request):
    username = request.session.get('username')
    user = User.objects.get(name=username)
    appointlist = Appointment.objects.filter(user=user)
    context = {}
    context['unpayedOrders'] = []
    for appoint in appointlist:
        appoint1 = {}
        appoint1['appointid'] = appoint.id
        appoint1['hospital'] = appoint.hospital.name
        #   appoint1['hospitalid'] = appoint.hospital.id
        #   appoint1['doctorid'] = appoint.doctor.id
        #   appoint1['deptid'] = appoint.department.id
        appoint1['dept'] = appoint.department.name
        appoint1['price'] = appoint.fare
        appoint1['date'] = appoint.appointment_date.strftime('%Y-%m-%d') + appoint.date2
        appoint1['doctor'] = appoint.doctor.name
        appoint1['rank'] = appoint.doctor.rank
        context['unpayedOrders'].append(appoint1)
    context['payedOrders'] = []
    paylist = Order.objects.filter(user=user)
    # paylist = Appointment.objects.filter(user=user, status=1)
    for pay in paylist:
        pay1 = {}
        pay1['appointid'] = pay.id
        pay1['hospital'] = pay.hospital.name
        #   pay1['hospitalid'] = appoint.hospital.id
        #   pay1['doctorid'] = appoint.doctor.id
        #   pay1['deptid'] = appoint.department.id
        pay1['dept'] = pay.department.name
        pay1['price'] = pay.fare
        pay1['date'] = pay.appointment_date.strftime('%Y-%m-%d') + pay.date2
        pay1['doctor'] = pay.doctor.name
        pay1['rank'] = pay.doctor.rank
        context['payedOrders'].append(pay1)
    try:
        context['name'] = username
    finally:
        return context


@csrf_exempt
def list(request):
    context = showlist(request)
    return render(request, 'show/list.html', context)


@csrf_exempt
def cancelappoint(request, appointid):
    appoint = Appointment.objects.get(id=appointid)
    context = {}
    Appointment.delete(appoint)
    context = showlist(request)
    return render(request, 'show/list.html', context)


@csrf_exempt
def payappoint(request, appointid):
    appoint = Appointment.objects.get(id=appointid)
    context = {}
    order = Order()
    order.hospital = appoint.hospital
    order.doctor = appoint.doctor
    order.department = appoint.department
    order.user = appoint.user
    order.appointment_date = appoint.appointment_date
    order.date2 = appoint.date2
    order.create_date = appoint.create_date
    order.fare = appoint.fare
    order.save()
    Appointment.delete(appoint)
    context = showlist(request)
    return render(request, 'show/list.html', context)


@csrf_exempt
def appoint(request):
    context = {}
    hospital = request.POST['hospital']
    department = request.POST['department']
    doctorid = request.POST['doctor']
    username = request.session.get('username')
    price = request.POST['price']
    user = User.objects.get(name=username)
    date2 = request.POST['date2']
    # user=User.objects.get(id=1)
    appointment_date = request.POST['appointment_date']
    doctor = Doctor.objects.get(id=doctorid)
    appointlist = Appointment.objects.filter(user=user)
    if appointlist.__len__() <= 3:
        appointlist = Appointment.objects.filter(user=user, department=department)
        if appointlist.__len__() == 0:
            context = {}
            appoint = Appointment()
            appoint.user = user
            appoint.fare = price
            appoint.doctor = doctor
            appoint.date2 = date2
            appoint.hospital = Hospital.objects.get(id=hospital)
            appoint.department = Department.objects.get(id=department)
            appoint.appointment_date = appointment_date
            appoint.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'fail': True})
    else:
        return JsonResponse({'fail': True})


@csrf_exempt
def adminlist(context):
    userlist = User.objects.filter(verify=False)
    context['userlist'] = []
    i = 0
    for user in userlist:
        user1 = dict()
        user1['id'] = user.id
        user1['tag'] = i
        i = i + 1
        user1['name'] = user.name
        user1['realname'] = user.realname
        user1['idcard'] = user.idcard
        context['userlist'].append(user1)
    return context


def adminprelogin(request):
    context = {}
    try:
        context['name'] = request.session['username']
        user = User.objects.get(name=request.session['username'])
        if user.admin:
            adminlist(context)
            return render(request, 'show/backstage.html', context)
    except:
        return render(request, 'show/bkstg_login.html', context)


@csrf_exempt
def adminlogin(request):
    name = request.POST['name']
    password = request.POST['password']
    # 判断用户名是否被注册
    try:
        context = {}
        user = User.objects.get(name=name)
        if user.passwd != password:
            try:
                context['name'] = request.session['username']
            finally:
                return render(request, 'show/bkstg_login.html', context)
        if user.admin != True:
            try:
                context['name'] = request.session['username']
            finally:
                return render(request, 'show/bkstg_login.html', context)
        request.session['username'] = name
        try:
            context['name'] = request.session['username']
        finally:
            context = adminlist(context)
            return render(request, 'show/backstage.html', context)
            # 判断用户名是否被注册
    except ObjectDoesNotExist:
        try:
            context['name'] = request.session['username']
        finally:
            return render(request, 'show/bkstg_login.html', context)


@csrf_exempt
def rejectuser(request, userid):
    user = User.objects.get(id=userid)
    context = {}
    User.delete(user)
    context = adminlist(context)
    return render(request, 'show/backstage.html', context)


@csrf_exempt
def admituser(request):
    userid = request.POST['userid']
    credit = request.POST['credit']
    user = User.objects.get(id=userid)
    context = {}
    user.verify = True
    user.credit = credit
    user.save()
    return JsonResponse({'success': True})


@csrf_exempt
def info(request):
    context = {}
    hospitallist = Hospital.objects.all()
    context['hospitalList'] = []
    for hosp in hospitallist:
        hosp1 = dict()
        hosp1['id'] = hosp.id
        hosp1['name'] = hosp.name
        context['hospitalList'].append(hosp1)
    return render(request, 'show/info.html', context)


@csrf_exempt
def getdept(request):
    context = {}
    hospital = request.POST['hospital']
    deptlist = Department.objects.filter(hospital=hospital)
    context['deptlist'] = []
    for dept in deptlist:
        dept1 = dict()
        dept1['id'] = dept.id
        dept1['name'] = dept.name
        context['deptlist'].append(dept1)
    return JsonResponse({'success': True, 'context': context})


@csrf_exempt
def getdoc(request):
    context = {}
    dept = request.POST['dept']
    doclist = Doctor.objects.filter(department=dept)
    context['doclist'] = []
    for doc in doclist:
        doc1 = dict()
        doc1['id'] = doc.id
        doc1['name'] = doc.name
        context['doclist'].append(doc1)
    return JsonResponse({'success': True, 'context': context})

@csrf_exempt
def setmax(request):
    # context = {}
    doctor = request.POST['doctor']
    date = request.POST['date']
    num = request.POST['num']
    maxlist = Maxium_Appointment.objects.filter(doctor=doctor,date=date)
    if maxlist.__len__() == 0:
        # context = {}
        maxapp = Maxium_Appointment()
        maxapp.doctor = Doctor.objects.get(id=doctor)
        maxapp.date = date
        maxapp.number = num
        maxapp.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'fail': True})

# Android
# 安卓端只有普通用户界面，无管理员权限





@csrf_exempt
def mobile_login(request):
    """
    返回信息结构为{status:状态参数 username:用户名}
    :param request: Http request
    :return:    Http return
    """
    if request.method == 'POST':
        try:
            decode = m_decode(request.body)
        except:
            rresponse = dict()
            rresponse['status'] = 'decode_error'
            jresponse = json.dumps(rresponse)
            return HttpResponse(jresponse)
        try:
            user_tempt = User.objects.get(name=decode['username'])
        except:
            rresponse = dict()
            rresponse['status'] = 'user_not_exist'
            jresponse = json.dumps(rresponse)
            return HttpResponse(jresponse)
        if user_tempt.passwd == decode['password']:  # 密码吻合
            rresponse = dict()
            rresponse['status'] = 'normal'
            rresponse['username'] = decode['username']
            jresponse = json.dumps(rresponse)
            return HttpResponse(jresponse)

        else:
            rresponse = dict()
            rresponse['status'] = 'password_error'
            jresponse = json.dumps(rresponse)
            return HttpResponse(jresponse)
    else:
        rresponse = dict()
        rresponse['status'] = 'unkown_error'
        jresponse = json.dumps(rresponse)
        return HttpResponse(jresponse)


@csrf_exempt
def mobile_register(request):
    """
    返回信息结构为{status:状态参数}
    :param request: Http request
    :return:    Http return
    """
    if request.method == 'POST':
        try:
            decode = m_decode(request.body)
        except:
            rresponse = dict()
            rresponse['status'] = 'decode_error'
            jresponse = json.dumps(rresponse)
            return HttpResponse(jresponse)
    try:
        User.objects.get(name=decode['username'])
        rresponse = dict()
        rresponse['status'] = 'register_fail'
        jresponse = json.dumps(rresponse)
        return HttpResponse(jresponse)
    except ObjectDoesNotExist:
        m_user = User()
        m_user.name = decode['username']
        m_user.passwd = decode['password']
        m_user.contact = decode['email']
        m_user.save()
        rresponse = dict()
        rresponse['status'] = 'normal'
        jresponse = json.dumps(rresponse)
        return HttpResponse(jresponse)


@csrf_exempt
def mobile_searchhospname(request):
    """
    返回信息结构为{status:状态参数, hospitalList:医院列表信息}
                医院列表信息{id:医院ID, name:医院名, loc:医院地址, intro:介绍}
    :param request: Http request
    :return:    Http return
    """
    if request.method == 'POST':
        try:
            decode = m_decode(request.body)
        except:
            rresponse = dict()
            rresponse['status'] = 'decode_error'
            jresponse = json.dumps(rresponse)
            return HttpResponse(jresponse)
        hosplist = Hospital.objects.filter(name__contains=decode['hospital'])
        if hosplist.__len__() > 0:
            rresponse = dict()
            rresponse['hospitalList'] = []
            for hosp in hosplist:
                hosp1 = {}
                hosp1['id'] = hosp.id
                hosp1['name'] = hosp.name
                hosp1['loc'] = hosp.address
                hosp1['intro'] = hosp.contact
                rresponse['hospitalList'].append(hosp1)
            rresponse['status'] = 'normal'
            jresponse = json.dumps(rresponse)
            return HttpResponse(jresponse)
        else:
            rresponse = dict()
            rresponse['status'] = 'failed'
            jresponse = json.dumps(rresponse)
            return HttpResponse(jresponse)


@csrf_exempt
def mobile_searchdepartment(request):
    """
    返回信息结构为{status:状态参数, hospitalid:医院id, departments:部门列表信息}
                部门列表信息{id:部门id, name:部门名, doctors:医生列表信息}
                医生列表信息{id:医生ID, name:医生名, rank:医生职称, price:医生价格}
    :param request: Http request
    :return:    Http return
    """
    if request.method == 'POST':
        try:
            decode = m_decode(request.body)
        except:
            rresponse = dict()
            rresponse['status'] = 'decode_error'
            jresponse = json.dumps(rresponse)
            return HttpResponse(jresponse)
        deplist = Department.objects.filter(hospital=decode['hospital'])
        if deplist.__len__() > 0:
            rresponse = dict()
            rresponse['hospitalid'] = decode['hospital']
            rresponse['departments'] = []
            for dep in deplist:
                dep1 = {}
                dep1['id'] = dep.id
                dep1['name'] = dep.name
                dep1['doctors'] = []
                doclist = Doctor.objects.filter(department=dep.id)
                for doc in doclist:
                    doc1 = {}
                    doc1['id'] = doc.id
                    doc1['name'] = doc.name
                    doc1['rank'] = doc.rank
                    doc1['price'] = doc.fee
                    dep1['doctors'].append(doc1)
                    rresponse['departments'].append(dep1)
            rresponse['status'] = 'normal'
            jresponse = json.dumps(rresponse)
            return HttpResponse(jresponse)
        else:
            rresponse = dict()
            rresponse['status'] = 'failed'
            jresponse = json.dumps(rresponse)
            return HttpResponse(jresponse)


@csrf_exempt
def mobile_showlist(user):
    """
    返回信息结构为{status:状态参数, UnpayedOrders:未付费订单列表, payedOrders:已付费订单列表}
                未付费订单列表{appointid:订单id hospital:医院名 date2:预约日期 dept:部门名
                                price:订单费用 date:下订单日期 doctor:医生名 rank:医生职称}
                已付费订单列表{appointid:订单id hospital:医院名 date2:预约日期 dept:部门名
                                price:订单费用 date:下订单日期 doctor:医生名 rank:医生职称}
    :param request: user
    :return:    Http return
    """
    user = User.objects.get(name=user)
    appointlist = Appointment.objects.filter(user=user)
    if appointlist.__len__() > 0:
        rresponse = dict()
        rresponse['unpayedOrders'] = []
        for appoint in appointlist:
            appoint1 = {}
            appoint1['appointid'] = appoint.id
            appoint1['hospital'] = appoint.hospital.name
            #   appoint1['hospitalid'] = appoint.hospital.id
            #   appoint1['doctorid'] = appoint.doctor.id
            #   appoint1['deptid'] = appoint.department.id
            appoint['date2'] = appoint.date2
            appoint1['dept'] = appoint.department.name
            appoint1['price'] = appoint.fare
            appoint1['date'] = appoint.appointment_date
            appoint1['doctor'] = appoint.doctor.name
            appoint1['rank'] = appoint.doctor.rank
            rresponse['unpayedOrders'].append(appoint1)
        rresponse['payedOrders'] = []
        paylist = Order.objects.filter(user=user)
        for pay in paylist:
            pay1 = {}
            pay1['appointid'] = pay.id
            pay1['hospital'] = pay.hospital.name
            #   pay1['hospitalid'] = appoint.hospital.id
            #   pay1['doctorid'] = appoint.doctor.id
            #   pay1['deptid'] = appoint.department.id
            pay1['dept'] = pay.department.name
            pay1['price'] = pay.fare
            pay1['date2'] = pay.date2
            pay1['date'] = pay.appointment_date
            pay1['doctor'] = pay.doctor.name
            pay1['rank'] = pay.doctor.rank
            rresponse['payedOrders'].append(pay1)
        rresponse['status'] = 'normal'
        jresponse = json.dumps(rresponse)
        return jresponse
    else:
        rresponse = dict()
        rresponse['status'] = 'failed'
        jresponse = json.dumps(rresponse)
        return HttpResponse(jresponse)


@csrf_exempt
def mobile_list(request):
    """
    返回信息结构为{status:状态参数}
    :param request: Http request
    :return:    Http return
    """
    if request.method == 'POST':
        try:
            decode = m_decode(request.body)
        except:
            rresponse = dict()
            rresponse['status'] = 'decode_error'
            jresponse = json.dumps(rresponse)
            return HttpResponse(jresponse)
        user = User.objects.get(name=decode['user'])
        jresponse = showlist(user)
        return HttpResponse(jresponse)


@csrf_exempt
def mobile_cancelappoint(request):
    """
    返回信息结构为{status:状态参数}
    :param request: Http request
    :return:    Http return
    """
    if request.method == 'POST':
        try:
            decode = m_decode(request.body)
        except:
            rresponse = dict()
            rresponse['status'] = 'decode_error'
            jresponse = json.dumps(rresponse)
            return HttpResponse(jresponse)
        try:
            appoint = Appointment.objects.get(id=decode['appoint'])
            Appointment.delete(appoint)
            username = decode['username']
            jresponse = showlist(username)
            return HttpResponse(jresponse)
        except ObjectDoesNotExist:
            rresponse = dict()
            rresponse['status'] = 'failed'
            jresponse = json.dumps(rresponse)
            return HttpResponse(jresponse)


@csrf_exempt
def mobile_payappoint(request):
    """
    返回信息结构为{status:状态参数}
    :param request: Http request
    :return:    Http return
    """
    if request.method == 'POST':
        try:
            decode = m_decode(request.body)
        except:
            rresponse = dict()
            rresponse['status'] = 'decode_error'
            jresponse = json.dumps(rresponse)
            return HttpResponse(jresponse)
        try:
            appoint = Appointment.objects.get(id=decode['appoint'])
            appoint.status = 1
            appoint.save()
            username = decode['username']
            jresponse = showlist(username)
            return HttpResponse(jresponse)
        except ObjectDoesNotExist:
            rresponse = dict()
            rresponse['status'] = 'failed'
            jresponse = json.dumps(rresponse)
            return HttpResponse(jresponse)


@csrf_exempt
def mobile_appoint(request):
    """
    返回信息结构为{status:状态参数}
    :param request: Http request
    :return:    Http return
    """
    if request.method == 'POST':
        try:
            decode = m_decode(request.body)
        except:
            rresponse = dict()
            rresponse['status'] = 'decode_error'
            jresponse = json.dumps(rresponse)
            return HttpResponse(jresponse)
        hospital = decode['hospital']
        department = decode['department']
        doctorid = decode['doctorid']
        username = decode['username']
        price = decode['price']
        date2 = decode['date2']
        user = User.objects.get(name=username)
        appointment_date = decode['date']
        doctor = Doctor.objects.get(id=doctorid)
        appointlist = Appointment.objects.filter(user=user, doctor=doctor)
        if appointlist.__len__() == 0:
            appoint = Appointment()
            appoint.user = user
            appoint.fare = price
            appoint.doctor = doctor
            appoint.date2 = date2
            appoint.hospital = Hospital.objects.get(id=hospital)
            appoint.department = Department.objects.get(id=department)
            appoint.appointment_date = appointment_date
            appoint.save()
            rresponse = dict()
            rresponse['status'] = 'normal'
            jresponse = json.dumps(rresponse)
            return HttpResponse(jresponse)
        else:
            rresponse = dict()
            rresponse['status'] = 'failed'
            jresponse = json.dumps(rresponse)
            return HttpResponse(jresponse)


@csrf_exempt
def mobile_info(request):
    """
    返回信息结构为{status:状态参数, info:医院列表信息, count:医院总数}
                医院列表信息{id:医院ID， name:医院名}
    :param request: Http request
    :return:    Http return
    """
    rresponse = dict()
    try:
        hospitallist = Hospital.objects.all()
        rresponse['status'] = 'normal'      # 状态信息加入返回信息
    except ObjectDoesNotExist:             # 数据库中无医院数据
        rresponse['status'] = 'failed'
        rresponse['info'] = 'No hospital'
        jresponse = json.dumps(rresponse)
        return HttpResponse(jresponse)
    info = dict()                           # 医院列表
    count = 0                               # 医院条目计数
    for hosp in hospitallist:              # 遍历所有医院条目
        count += 1
        hosp1 = dict()
        hosp1['id'] = hosp.id
        hosp1['name'] = hosp.name
        hosp1['city'] = hosp.city
        hos_single_info = json.dumps(hosp1)     # 将单个医院的属性转为json
        info[str(count)] = hos_single_info      # 将单个医院实体加入医院列表信息字典
    j_info = json.dumps(info)                   # 将医院列表转为json
    rresponse['info'] = j_info                  # 医院列表实体加入返回信息
    rresponse['count'] = count                  # 计数加入返回信息
    jresponse = json.dumps(rresponse)
    return HttpResponse(jresponse)


@csrf_exempt
def mobile_getdept(request):
    """
    返回信息结构为{status:状态参数, info:部门列表信息, count:部门总数}
                部门列表信息{id:部门ID， name:部门名}
    :param request:
    :return:
    """
    decode = m_decode(request.body)     # request内容由json解码为dict
    rresponse = dict()
    hospital = decode['hospital']
    deptlist = Department.objects.filter(hospital=hospital)
    info = dict()                           # 部门列表
    count = 0
    rresponse['status'] = 'normal'
    for dept in deptlist:
        count += 1
        dept1 = dict()
        dept1['id'] = dept.id
        dept1['name'] = dept.name
        j_dept1 = json.dumps(dept1)       # 将单个部门的属性转为json
        info[str(count)] = j_dept1          # 将单个部门加入部门列表字典
    j_info = json.dumps(info)               # 将部门列表转为json
    rresponse['info'] = j_info              # 部门列表加入返回信息
    rresponse['count'] = count              # 计数加入返回信息
    jresponse = json.dumps(rresponse)
    return HttpResponse(jresponse)


@csrf_exempt
def mobile_getdoc(request):
    """
    返回信息结构为{status:状态参数, info:医生列表信息, count:医生总数}
                医生列表信息{id:医生ID， name:医生名}
    :param request:
    :return:
    """
    decode = m_decode(request.body)     # request内容由json解码为dict
    rresponse = dict()
    dept = decode['dept']
    doclist = Doctor.objects.filter(department=dept)
    info = dict()                           # 医生列表
    count = 0
    rresponse['status'] = 'normal'
    for doc in doclist:
        doc1 = dict()
        doc1['id'] = doc.id
        doc1['name'] = doc.name
        j_doc1 = json.dumps(doc1)           # 将单个医生的属性转为json
        info[str(count)] = j_doc1           # 将单个医生加入部门列表字典
    j_info = json.dumps(info)               # 将医生列表转为json
    rresponse['info'] = j_info              # 医生列表加入返回信息
    rresponse['count'] = count              # 计数加入返回信息
    jresponse = json.dumps(rresponse)
    return HttpResponse(jresponse)
