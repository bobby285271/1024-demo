from django.shortcuts import render, reverse, redirect
from django.http import HttpResponse
import re
from django.contrib import messages
from .models import STUDB
import django.utils.timezone as timezone


def index(request):
    return HttpResponse("<h1>Hello World</h1>")


def login(request):
    code = request.GET.get('code', None)
    if code == '-3':
        messages.error(request, "请 先 登 录")
    if code == '-2':
        messages.error(request, "不要没填完就登录啊喂！")
    if code == '-1':
        messages.error(request, "啊哦~登录失败了←_←")
    if code == '1':
        messages.success(request, "注 册 成 功")
    return render(request, 'login.html')


def register(request):
    code = request.GET.get('code', None)
    if code == '-5':
        messages.error(request, "不要没填完就注册啊喂！")
    elif code == '-4':
        messages.error(request, "学 号 格 式 有 误")
    elif code == '-3':
        messages.error(request, "密码需要 6-18 位且必须是英文字母或数字")
    elif code == '-2':
        messages.error(request, "两次密码输入不一致的说")
    elif code == '-1':
        messages.error(request, "这个学号已被注册！请不要试图顶替别人(｡•ˇ‸ˇ•｡)")
    return render(request, 'register.html')


def register_to_db(request):
    userid = request.POST.get('userid', None)
    username = request.POST.get('username', None)
    passwd = request.POST.get('passwd', None)
    repasswd = request.POST.get('repasswd', None)
    if not userid or not passwd or not username or not repasswd:
        return redirect(reverse('register')+"?code=-5")
    if not re.match(r'^(201).*\d{8}$', userid):
        return redirect(reverse('register')+"?code=-4")
    if not re.match(r'^[A-Za-z0-9]{6,18}$', passwd):
        return redirect(reverse('register')+"?code=-3")
    if passwd != repasswd:
        return redirect(reverse('register')+"?code=-2")
    users = STUDB.objects.filter(userid=userid)
    if len(users) == 1:
        return redirect(reverse('register')+"?code=-1")
    STUDBdent = STUDB.objects.create(
        userid=userid, username=username, passwd=passwd)
    STUDBdent.save()
    return redirect(reverse('login')+"?code=1")


def check_user(request):
    id = request.POST.get('id', None)
    passwd = request.POST.get('passwd', None)
    if not id or not passwd:
        return redirect(reverse('login')+"?code=-2")
    users = STUDB.objects.filter(userid=id, passwd=passwd)
    if len(users) == 1:
        request.session['userid'] = id
        request.session['is_login'] = '1'
        return redirect(reverse('play')+"?code=1")
    else:
        return redirect(reverse('login')+"?code=-1")


def play(request):
    if request.session.get('is_login') == '1':
        code = request.GET.get('code', None)
        userid = request.session['userid']
        user = STUDB.objects.filter(userid=userid).last()
        if user.rank < 3 and code == '-1':
            messages.error(request, "哎呀，错了orz")
        if user.rank > 2 and code == '-1':
            messages.error(request, "终局之战总是很坎坷的，请再找找flag是什么吧_(:з」∠)_")
        if code == '1':
            messages.success(request, '登录成功(｡･ω･｡)ﾉ♡')
        if user.rank > 2 and code == '2':
            messages.success(request, '哦吼！恭喜你发现了不得了的β时间线，这一切都是命运石之门的选择~！')
        if user.rank > 3:
            url = 'level3.html'
        else:
            url = 'level' + str(user.rank) + '.html'
        return render(request, url)
    else:
        return redirect(reverse('login')+"?code=-3")


def compare_flag(request):
    correct_flag = [
        '',
        '2018',
    ]
    flag = request.POST.get('flag', None)
    userid = request.session['userid']
    user = STUDB.objects.filter(userid=userid).last()
    if user.rank < 2:
        if correct_flag[user.rank] == flag:
            user.rank += 1
            user.save()
            return redirect(reverse('play'))
        else:
            return redirect(reverse('play')+"?code=-1")
    elif user.rank == 2:
        if flag == 'sdltql':
            user.lastflag = timezone.now()
            user.timesubtract = (
                user.lastflag - user.firstflag).total_seconds()
            user.rank += 1
            user.save()
            return redirect(reverse('play'))
        else:
            return redirect(reverse('play')+"?code=-1")
    elif user.rank > 2:
        if flag == 'happy':
            user.superflag = timezone.now()
            user.timesubtract_last = (
                user.superflag-user.firstflag).total_seconds()
            user.rank = 4
            user.save()
            return redirect(reverse('win'))
        elif flag == '666':
            user.specialflag = timezone.now()
            user.timesubtract_suprise = (
                user.firstflag - user.specialflag).total_seconds()
            user.save()
            return redirect(reverse('play')+"?code=2")
        else:
            return redirect(reverse('play')+"?code=-1")
    return redirect(reverse('play'))


def win(request):
    if request.session.get('is_login') == '1':
        userid = request.session['userid']
        user = STUDB.objects.filter(userid=userid).last()
        if user.rank == 4:
            return render(request, 'win.html')
        else:
            return redirect(reverse('play'))
    else:
        return redirect(reverse('login')+"?code=-3")
