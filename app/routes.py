from flask import Flask, render_template, flash, redirect, url_for, request, Response
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User
from flask_bootstrap import Bootstrap
from flask_moment import Moment
import json
from flask_paginate import Pagination, get_page_args
from airtable.airtable import Airtable
from pyairtable import Table
import os
import requests

import db_helper, static_helper
from constants import get_page_resolution

import re
import random
#from vimeo import VimeoClient, client

TPL = ''
STATIC_URL = '/static/' + TPL

CDN = True

if CDN:
    STATIC_URL = 'https://cdn.tarteel.net' + '/' + TPL
else:
    STATIC_URL = '/static/' + TPL

bootstrap = Bootstrap(app)
moment = Moment(app)


@app.errorhandler(404)
def page_not_found(e):
    template = TPL +  '/' + '404.html'
    return render_template(template,  STATIC_URL=STATIC_URL), 404

@app.errorhandler(500)
def internal_server_error(e):
    template = TPL + USER_LANG +  '/' + '500.html'
    return render_template(template, STATIC_URL=STATIC_URL), 500

#@app.route('/')
#def index_redirect():
#    return redirect(url_for('index'))

def get_Device():
    global TPL
    global CDN
    global STATIC_URL
    
    if TPL == '':
        #TPL = '/'

        
        if CDN:
            STATIC_URL = 'https://cdn.tarteel.net' + '/' + TPL
        else:
            STATIC_URL = '/static/' + TPL

    
    return  TPL   

def uniformNumber(num):
    if len(num) == 1:
        num = '00' + num
    elif len(num) == 2:
        num = '0' + num   
    return num


#@app.route('/')
@app.route('/loop')
def loop():
    
    
    
    return render_template('faq.html')



#@app.route('/')
@app.route('/safah/<safah>/')
def main(safah='3', images='1053'):
    #safah = request.GET.get('safah') or 3 #1
    images='1053'
    safah = request.args.get('safah')

    if safah is None:
        safah = '01'
    #images = request.GET.get('images') or '1053' #'1024'
    images = request.args.get('images') 
    if images is  None:
        images='1053'
  
    safah = int(safah)
    page_path = static_helper.get_image_path_from_safah(safah, images)
    values = db_helper.get_bounds_for_safah(safah, images)
    highlight_data =request.args.get('highlight') or ''
    resolution = get_page_resolution(images, safah)
    return render_template('index.html', STATIC_URL=STATIC_URL, values=values, pagePath=page_path, data=[], highlight=highlight_data, resolution=resolution, safah=safah)


@app.route('/highlight/')
def route_test(ayah="1:1", images='1053'):

    ayah_key = request.args.get('ayah')
    if ayah_key is None:
        ayah_key = ayah = "1:2"
    
    images = request.args.get('images')     
    if images is None:
        images='1053'

    safah_data = db_helper.get_safah_data_from_ayah_key(ayah_key, images)
    safah = int(safah_data[0]['page'])
    page_path = static_helper.get_image_path_from_safah(safah, images)
    resolution = get_page_resolution(images, safah)
    return render_template('main.html', STATIC_URL=STATIC_URL, values=[], pagePath=page_path, data=safah_data, highlight=ayah_key, resolution=resolution)

@app.route('/hefz', methods=['GET', 'POST'])
def hefz():
    stage_0 = 1
    img_res = None
    narration = None
    img_mode = None
    img_type = None
    ayah = "1"
    ayah_id = None
    toayah_id = None
    to_ayah = '1'
    halfY = '1'
    selection_count = 1
    radioReciters = {}
    
    
    if  request.method == 'POST':
        surah = request.form['surah']
        ayah = request.form['ayah']
        safah = request.form['safah']
        reciter_mode = request.form.getlist('reciters')[0].split("-")
        mode = reciter_mode[0]
        reciter = reciter_mode[1]
        radioReciters[mode + "-" + reciter] = 'checked=""'
        to_ayah = request.form['to_ayah']
        repeat = request.form['repeat']
        ayah_repeat = request.form['ayah_repeat']
        #print('mode', mode, 'reciter', reciter)
        
    elif request.method == 'GET':
        surah = request.args.get('surah')
        safah = request.args.get('safah')
        reciter = request.args.get('reciter')
        img_res = request.args.get('img_res')
        mode = request.args.get('mode')
        narration = request.args.get('narration')
        img_mode = request.args.get('img_mode')
        img_type = request.args.get('img_type')
        repeat = request.args.get('repeat')
        ayah_repeat = request.args.get('ayah_repeat')
     
        
    if img_res is None:
        img_res='1053'
        
    #print('safah', safah, 'surah', surah, 'img_res', img_res)  
    
    
    

    
    if ayah == '':
            ayah = "1"
        
    if to_ayah is None:
        to_ayah = str(ayahCount[int(surah)-1])
            
    ayah_id = request.args.get('ayah_id')
    if ayah_id is None:
        ayah_id = surah + ":" + ayah
        
    toayah_id = request.args.get('toayah_id')
    if toayah_id is None:
        toayah_id = surah + ":" + to_ayah
        
    safahSelection = []   
    safah_dic = {} 
    
    if safah == "":
        safah_data = db_helper.get_safah_data_from_ayah_key(ayah_id, img_res)
        safah = int(safah_data[0]['page'])
        
        safah_data_end = db_helper.get_safah_data_from_ayah_key(toayah_id, img_res)
        safah_end = int(safah_data_end[0]['page'])
       
        ayah_pointer = 1
        safah_len = len(safah_data)
        ayah_start = safah_data[0]['ayah']
        ayah_end = safah_data[safah_len -1]['ayah']
        ayah_count = (int(ayah_end) -  int(ayah)) + 1 
        safah_dic[ayah_pointer] = {}
        safah_dic[ayah_pointer]['count'] = ayah_count
        safah_dic[ayah_pointer]['data'] = safah_data
        safah_dic[ayah_pointer]['page'] = safah
        for pos in safah_data:
                minY_pos = pos['min_y']
                if minY_pos >= 550:
                    halfY =  pos['ayah']
                    break
        safah_dic[ayah_pointer]['scroll'] = int(halfY) - int(ayah)
        #print(halfY, ayah, int(halfY) - int(ayah))
        ayah_pointer += ayah_count
            
        for i in range(safah+1, safah_end+1):
            safah_next= db_helper.get_data_for_safah(i)
     
            safah_len = len(safah_next)
            ayah_start = safah_next[0]['ayah']
            ayah_end = safah_next[safah_len -1]['ayah']
            ayah_count = (int(ayah_end) -  int(ayah_start)) + 1
                  
            safah_dic[ayah_pointer] = {}
            safah_dic[ayah_pointer]['count'] = ayah_count
            safah_dic[ayah_pointer]['data'] = safah_next
            safah_dic[ayah_pointer]['page'] = i
            for pos in safah_next:
                minY_pos = pos['min_y']
                if minY_pos >= 550:
                    halfY =  pos['ayah']
                    break
            
            safah_dic[ayah_pointer]['scroll'] = int(halfY) - int(ayah_start) 
            ayah_pointer += ayah_count
            
       
    else: # not None  
        #print('surah', surah, 'ayah', ayah, 'to_ayah', to_ayah)
        safah_data= db_helper.get_data_for_safah(safah)
        safah = int(safah)
        ayah = str(pages[safah]['from'])
        to_ayah = str(pages[safah]['to'])
        surah = str(pages[safah]['surah'])
        #print(safah, ayah, to_ayah)


    selection_count = (int(to_ayah) - int(ayah)) + 1 
    
    get_Device()
    TPL = get_Device()
    
    
    
             
    if narration is None:
        narration='N1'
   
    if mode is None:
        mode='R1' 
        
    if reciter is None:
        reciter='01'
    if radioReciters == {}:
        radioReciters["R1-" + reciter]='checked=""'       
        
    if img_mode is None:
        img_mode='T1' 
        
    if img_type is None:
        img_type='02'         
    
      
    
    title ='إِنَّهُ لَقُرْآنٌ كَرِيمٌ'
    template = TPL +  'index.html' 
    img = surah + "_" + ayah
    surah_fill = uniformNumber(surah)
    ayah_fill = uniformNumber(ayah)
    #ayah_url = STATIC_URL + "ayat/mp3/" + surah_fill + "/" + surah_fill + ayah_fill + ".mp3"
    #request = requests.get(ayah_url)
    #if request.status_code >= 400:
    
 
    next_ayah = str(int(ayah)+1)
    if int(next_ayah) > ayahCount[int(surah)-1] :
        next_ayah = str(int(ayah))
    
    prev_ayah = str(int(ayah)-1)
    if int(ayah) == 1:
        prev_ayah = str(int(ayah))
        
        
    if CDN:
        page_path =  "https://cdn.tarteel.net/ayat/N1/img/T2/02/" + str(safah) + ".jpg" ;
    else:
        page_path = static_helper.get_image_path_from_safah(safah, img_res)  
    
    resolution = get_page_resolution(img_res, safah)
 
            
    to_repeat = ""
    for r in range (int(repeat)):
        for i in range (int(ayah), int(to_ayah)+1):
            for a in range(int(ayah_repeat)):
                ayah_fill = uniformNumber(str(i))
                ayah_i =  "https://cdn.tarteel.net/ayat/N1/mp3/" + mode + "/" + reciter + "/" + surah_fill + ayah_fill + ".mp3"
                to_repeat +=  "'" + ayah_i + "'" + ", "
         
    
    return render_template(template, STATIC_URL=STATIC_URL, title=title, surah=surah, ayah=ayah, next_ayah=next_ayah, prev_ayah=prev_ayah, surah_fill=surah_fill, ayah_fill=ayah_fill, img=img, reciter=reciter, mode=mode, narration=narration, img_mode=img_mode, img_type=img_type, surah_list=surahNames,  values=[], pagePath=page_path, data=safah_data,  data_dic=safah_dic, highlight=ayah_id, resolution=resolution, to_repeat=to_repeat, safah=safah, repeat=repeat, stage_0=stage_0, to_ayah=to_ayah, selection_count=selection_count, ayah_repeat=ayah_repeat, radioReciters=radioReciters )
    
    
@app.route('/' )
@app.route('/<surah>/')
@app.route('/<surah>/<ayah>')
@app.route('/<surah>/<ayah>.html')
#@mobile_template('/{mobile/}' + USER_LANG + '_index.html')
def index(ayah='1', to_ayah='1', surah='2', reciter='06', mode='R1', narration='N1', img_mode='T1', img_type='01', ayah_id="1:1", img_res='1053', stage_0 = 0, safah='', repeat='1', selection_count = '1', ayah_repeat='1',  radioReciters = {}):
    
        
       
    get_Device()
    TPL = get_Device()
    
    mode = request.args.get('mode')
    reciter = request.args.get('reciter')
    narration = request.args.get('narration')
    img_mode = request.args.get('img_mode')
    img_type = request.args.get('img_type')
    repeat = request.args.get('repeat')
    
             
    if narration is None:
        narration='N1'
    if mode is None:
        mode='R1' 
    if reciter is None:
        reciter='01'
    if radioReciters == {}:
        radioReciters["R1-" + reciter]='checked=""'    
    if img_mode is None:
        img_mode='T1' 
    if img_type is None:
        img_type='01' 
    if repeat is None:
        repeat='1' 
        
    
      
    
    title ='إِنَّهُ لَقُرْآنٌ كَرِيمٌ'
    template = TPL +  'index.html' 
    img = surah + "_" + ayah
    surah_fill = uniformNumber(surah)
    ayah_fill = uniformNumber(ayah)
    #ayah_url = STATIC_URL + "ayat/mp3/" + surah_fill + "/" + surah_fill + ayah_fill + ".mp3"
    #request = requests.get(ayah_url)
    #if request.status_code >= 400:
    
    next_ayah = str(int(ayah)+1)
    if int(next_ayah) > ayahCount[int(surah)-1] :
        next_ayah = str(int(ayah))
    
    prev_ayah = str(int(ayah)-1)
    if int(ayah) == 1:
        prev_ayah = str(int(ayah))
        
    ayah_id = request.args.get('ayah_id')
    if ayah_id is None:
        ayah_id = surah + ":" + ayah
    
    img_res = request.args.get('img_res')
  
    if img_res is None:
        img_res='1053'
    
  
    if safah == '':
        safah_data = db_helper.get_safah_data_from_ayah_key(ayah_id, img_res)
        safah = int(safah_data[0]['page'])
    else: # not None  
        safah_data= db_helper.get_data_for_safah(safah)
        safah = int(safah)
        ayah = str(pages[safah]['from'])
        ayah_to = str(pages[safah]['to'] + 1)
        #print(safah, ayah, ayah_to)

    if CDN:
        page_path =  "https://cdn.tarteel.net/ayat/N1/img/T2/02/" + str(safah) + ".jpg" ;
    else:
        page_path = static_helper.get_image_path_from_safah(safah, img_res)     
        
    resolution = get_page_resolution(img_res, safah)

    return render_template(template, STATIC_URL=STATIC_URL, title=title, surah=surah, ayah=ayah, to_ayah=to_ayah, next_ayah=next_ayah, prev_ayah=prev_ayah, surah_fill=surah_fill, ayah_fill=ayah_fill, img=img, reciter=reciter, mode=mode, narration=narration, img_mode=img_mode, img_type=img_type, surah_list=surahNames,  values=[], pagePath=page_path, data=safah_data, highlight=ayah_id, resolution=resolution, safah=safah, stage_0=stage_0, repeat=repeat, selection_count=selection_count, ayah_repeat=ayah_repeat, radioReciters=radioReciters)


@app.route('/login', methods=['GET', 'POST'])
@app.route('/' +  '/login', methods=['GET', 'POST'])
def login():
    TPL = get_Device()
    template = TPL +  '/' + 'login.html'
    TPL = get_Device()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template(template, title='Sign In', form=form, STATIC_URL=STATIC_URL)


@app.route('/logout')
@app.route('/'  + '/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
@app.route('/' +  '/register', methods=['GET', 'POST'])
def register():
    TPL = get_Device()
    template = TPL +  '/' + 'register.html'
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template(template, title='Register', form=form, STATIC_URL=STATIC_URL)


@app.route('/faq.html')
@app.route('/' + '/faq.html')
def faq():
    TPL = get_Device()
    template = TPL +  '/' + 'faq.html'
    title='FAQ'
    
    return render_template(template,  title=title, STATIC_URL=STATIC_URL)

@app.route('/profile.html')
@app.route('/' + '/profile.html')
@login_required
def profile():
    TPL = get_Device()
    template = TPL +  '/' + 'profile.html'
    title='My Profile'
    return render_template(template,  title=title, STATIC_URL=STATIC_URL)

@app.route('/aboutus.html')
@app.route('/' + '/aboutus.html')
def aboutus():
    TPL = get_Device()
    template = TPL +   '/' + 'aboutus.html'
    title='About Us'
    return render_template(template,  title=title, STATIC_URL=STATIC_URL)

@app.route('/contactus.html')
@app.route('/' +  '/contactus.html')
def contactus():
    TPL = get_Device()
    template = TPL +  '/' + 'contactus.html'
    title='Contact Us'
    return render_template(template,  title=title, STATIC_URL=STATIC_URL)


ayahCount = [7, 286, 200, 176, 120, 165, 206, 75, 129, 109, 123, 111, 43, 52, 99, 128, 111, 110, 98, 135, 112, 78, 118, 64, 77, 227, 93, 88, 69, 60, 34, 30, 73, 54, 45, 83, 182, 88, 75, 85, 54, 53, 89, 59, 37, 35, 38, 29, 18, 45, 60, 49, 62, 55, 78, 96, 29, 22, 24, 13, 14, 11, 11, 18, 12, 12, 30, 52, 52, 44, 28, 28, 20, 56, 40, 31, 50, 40, 46, 42, 29, 19, 36, 25, 22, 17, 19, 26, 30, 20, 15, 21, 11, 8, 8, 19, 5, 8, 8, 11, 11, 8, 3, 9, 5, 4, 7, 3, 6, 3, 5, 4, 5, 6]

surahNames = ["الفاتحة", "البقرة", "آل عمران", "النساء", "المائدة", "الأنعام", "الأعراف", "الأنفال", "التوبة", "يونس", "هود", "يوسف", "الرعد", "إبراهيم", "الحجر", "النحل", "الإسراء", "الكهف", "مريم", "طه", "الأنبياء", "الحج", "المؤمنون", "النور", "الفرقان", "الشعراء", "النمل", "القصص", "العنكبوت", "الروم", "لقمان", "السجدة", "سورة الأحزاب", "سبأ", "فاطر", "يس", "الصافات", "ص", "الزمر", "غافر", "فصلت", "الشورى", "الزخرف", "الدخان", "الجاثية", "الأحقاف", "محمد", "الفتح", "الحجرات", "ق", "الذاريات", "الطور", "النجم", "القمر", "الرحمن", "الواقعة", "الحديد", "المجادلة", "الحشر", "الممتحنة", "الصف", "الجمعة", "المنافقون", "التغابن", "الطلاق", "التحريم", "الملك", "القلم", "الحاقة", "المعارج", "نوح", "الجن", "المزمل", "المدثر", "القيامة", "الإنسان", "المرسلات", "النبأ", "النازعات", "عبس", "التكوير", "الانفطار", "المطففين", "الإنشقاق", "البروج", "الطارق", "الأعلى", "الغاشية", "الفجر", "البلد", "الشمس", "الليل", "الضحى", "الشرح", "التين", "العلق", "القدر", "البينة", "الزلزلة", "العاديات", "القارعة", "التكاثر", "العصر", "الهمزة", "الفيل", "قريش", "الماعون", "الكوثر", "الكافرون", "النصر", "المسد", "الإخلاص", "الفلق", "الناس"]

pages = {1: {'surah':1, 'from':1, 'to':7}, 

2: {'surah':2, 'from':1, 'to':5},
3: {'surah':2, 'from':6, 'to':16},
4: {'surah':2, 'from':17, 'to':24},
5: {'surah':2, 'from':25, 'to':29},
6: {'surah':2, 'from':30, 'to':37},
7: {'surah':2, 'from':38, 'to':48},
8: {'surah':2, 'from':49, 'to':57},
9: {'surah':2, 'from':58, 'to':61},
10: {'surah':2, 'from':62, 'to':69},
11: {'surah':2, 'from':70, 'to':76},
12: {'surah':2, 'from':77, 'to':83},
13: {'surah':2, 'from':84, 'to':88},
14: {'surah':2, 'from':89, 'to':93},
15: {'surah':2, 'from':94, 'to':101},
16: {'surah':2, 'from':102, 'to':105},
17: {'surah':2, 'from':106, 'to':112},
18: {'surah':2, 'from':113, 'to':119},
19: {'surah':2, 'from':120, 'to':126},
20: {'surah':2, 'from':127, 'to':134},
21: {'surah':2, 'from':135, 'to':141},
22: {'surah':2, 'from':142, 'to':145},
23: {'surah':2, 'from':146, 'to':153},
24: {'surah':2, 'from':154, 'to':163},
25: {'surah':2, 'from':164, 'to':169},
26: {'surah':2, 'from':170, 'to':176},
27: {'surah':2, 'from':177, 'to':181},
28: {'surah':2, 'from':182, 'to':186},
29: {'surah':2, 'from':187, 'to':190},
30: {'surah':2, 'from':191, 'to':196},
31: {'surah':2, 'from':197, 'to':202},
32: {'surah':2, 'from':203, 'to':210},
33: {'surah':2, 'from':211, 'to':215},
34: {'surah':2, 'from':216, 'to':219},
35: {'surah':2, 'from':220, 'to':224},
36: {'surah':2, 'from':225, 'to':230},
37: {'surah':2, 'from':231, 'to':233},
38: {'surah':2, 'from':234, 'to':237},
39: {'surah':2, 'from':238, 'to':245},
40: {'surah':2, 'from':246, 'to':248},
41: {'surah':2, 'from':249, 'to':252},
42: {'surah':2, 'from':253, 'to':256},
43: {'surah':2, 'from':257, 'to':259},
44: {'surah':2, 'from':260, 'to':264},
45: {'surah':2, 'from':265, 'to':269},
46: {'surah':2, 'from':270, 'to':274},
47: {'surah':2, 'from':275, 'to':281},
48: {'surah':2, 'from':282, 'to':282},
49: {'surah':2, 'from':283, 'to':286},

50: {'surah':3, 'from':1, 'to':9},
51: {'surah':3, 'from':10, 'to':15},
52: {'surah':3, 'from':16, 'to':22},
53: {'surah':3, 'from':23, 'to':29},
54: {'surah':3, 'from':30, 'to':37},
55: {'surah':3, 'from':38, 'to':45},
56: {'surah':3, 'from':46, 'to':52},
57: {'surah':3, 'from':53, 'to':61},
58: {'surah':3, 'from':62, 'to':70},
59: {'surah':3, 'from':71, 'to':77},
60: {'surah':3, 'from':78, 'to':83},
61: {'surah':3, 'from':84, 'to':91},
62: {'surah':3, 'from':92, 'to':100},
63: {'surah':3, 'from':101, 'to':108},
64: {'surah':3, 'from':109, 'to':115},
65: {'surah':3, 'from':116, 'to':121},
66: {'surah':3, 'from':122, 'to':132},
67: {'surah':3, 'from':133, 'to':140},
68: {'surah':3, 'from':141, 'to':148},
69: {'surah':3, 'from':149, 'to':153},
70: {'surah':3, 'from':154, 'to':157},
71: {'surah':3, 'from':158, 'to':165},
72: {'surah':3, 'from':166, 'to':173},
73: {'surah':3, 'from':174, 'to':180},
74: {'surah':3, 'from':181, 'to':186},
75: {'surah':3, 'from':187, 'to':194},
76: {'surah':3, 'from':195, 'to':200},

77: {'surah':4, 'from':1, 'to':6},
78: {'surah':4, 'from':7, 'to':11},
79: {'surah':4, 'from':12, 'to':14},
80: {'surah':4, 'from':15, 'to':19},

}
    
    
