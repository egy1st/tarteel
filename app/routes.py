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
    
    pagez = ""
    for i in range(1,605):
        safah_i= db_helper.get_data_for_safah(i)
        safah_len = len(safah_i)
        ayah_start = safah_i[0]['ayah']
        surah_i = safah_i[safah_len -1]['sura']
        ayah_end = safah_i[safah_len -1]['ayah']
        pagez +=  str(i) + ": {'surah':" + str(surah_i) + ", 'from':" + str(ayah_start) + ", 'to':" + str(ayah_end) + "}," + "\n"
        
    #open text file
    text_file = open("C:\\Users\\moham\\Documents\\GitHub\\tarteel\\data.txt", "w")

    #write string to file
    n = text_file.write(pagez)

    #close file
    text_file.close()
    
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
    TO_SCROLL = 580
    ayah_pointer = 1
    
    surahNamesList = '' 
    for s in   range(len(surahNames)):
        surahNamesList +=   "<option value='" + str(s+1) + "'>" +  surahNames[s] + "</option>"
    
    
    if  request.method == 'POST':
        surah = request.form['surah']
        ayah = request.form['ayah']
        safah = request.form['safah']
        reciter_mode = request.form.getlist('reciters')[0].split("-")
        mode = reciter_mode[0]
        reciter = reciter_mode[1]
        radioReciters[mode + "-" + reciter] = 'checked=""'
        to_ayah = request.form['to_ayah']
        to_surah = request.form['to_surah']
        repeat = request.form['repeat']
        ayah_repeat = request.form['ayah_repeat']
        part = int(request.form.getlist('partlist')[0])
        hezb = int(request.form.getlist('hezblist')[0])
        quarter = int(request.form.getlist('quarterlist')[0])
         
        
    elif request.method == 'GET':
        surah = request.args.get('surah')
        safah = request.args.get('safah')
        to_ayah = request.args.get('to_ayah')
        to_surah = request.args.get('to_surah')
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
        toayah_id = to_surah + ":" + to_ayah
        
    safahSelection = []   
    safah_dic = {} 
    
   
    if  safah == "":
        safah_data = db_helper.get_safah_data_from_ayah_key(ayah_id, img_res)
        safah = int(safah_data[0]['page'])
        
        safah_data_end = db_helper.get_safah_data_from_ayah_key(toayah_id, img_res)
        safah_end = int(safah_data_end[0]['page'])
        n_pages = safah_end - safah + 1
        ayah_pointer = 1
        safah_len = len(safah_data)
        ayah_start = safah_data[0]['ayah']
        
        n_surah = (int(to_surah) - int(surah)) + 1
        
        ayah_end = to_ayah
        selection_count = 0
        if n_surah == 1 and n_pages == 1:
            ayah_end = to_ayah
            ayah_count = (int(ayah_end) - int(ayah)) + 1 
        elif n_surah == 1 and n_pages > 1:
            ayah_end = safah_data[safah_len -1]['ayah']
            ayah_count = (int(ayah_end) - int(ayah)) + 1 
        else: #  n_surah > 1 ansdn_pages == 1 or :  n_surah > 1 ansdn_pages > 1
            a_prev = '288'
            a_tot = 0
            for c_ in range(len(safah_data)):
                if int(safah_data[c_]['sura']) > int(surah) or (int(safah_data[c_]['sura']) == int(surah)  and  int(safah_data[c_]['ayah'] >= int(ayah) )):
                    a_ = safah_data[c_]['ayah']
                    if a_ != a_prev:
                        a_tot += 1
                        a_prev = a_
                 
            ayah_count =  a_tot 
       
       
        selection_count = ayah_count
        safah_dic[ayah_pointer] = {}
        safah_dic[ayah_pointer]['count'] = ayah_count
        safah_dic[ayah_pointer]['data'] = safah_data
        safah_dic[ayah_pointer]['page'] = safah
        #print(safah, ayah_end, ayah, ayah_count, 'only one')
        
        half_found = False
        n_ = 0
        a_prev = '288'
        for pos in safah_data: #522 583 643
          if half_found == True:
                break
          else:   
                if  int(pos['sura']) > int(surah) or (int(pos['sura']) == int(surah)  and  int(pos['ayah']) >= int(ayah)):
                    a_ = pos['ayah']
                    if a_ != a_prev:
                         n_ += 1
                         a_prev =  a_
              
                maxY_pos = pos['max_y']
                if maxY_pos >= TO_SCROLL:
                    half_found = True
                    
                    
        safah_dic[ayah_pointer]['scroll'] = n_ #int(halfY) - int(ayah)
        ayah_pointer += ayah_count
        #print(selection_count, 'selection_count')
        print('safah: ' , safah, safah_end)    
        for i in range(safah+1, safah_end+1):
            safah_next= db_helper.get_data_for_safah(i)
     
            safah_len = len(safah_next)
            ayah_start = safah_next[0]['ayah']
            ayah_end = safah_next[safah_len -1]['ayah']
                  
            safah_dic[ayah_pointer] = {}
            
            if n_surah == 1 and i == safah_end:
                ayah_end = to_ayah
                ayah_count = (int(ayah_end) - int(ayah_start)) + 1 
            elif n_surah == 1 and i < safah_end:
                ayah_end = safah_next[safah_len -1]['ayah']
                ayah_count = (int(ayah_end) - int(ayah_start)) + 1 
            else: #  n_surah > 1 
                a_prev = '288'
                a_tot = 0
                for c_ in range(len(safah_next)):
                    if int(safah_next[c_]['sura']) < int(to_surah) or (int(safah_next[c_]['sura']) == int(to_surah)  and  int(safah_next[c_]['ayah'] <= int(to_ayah) )):
                        a_ = safah_next[c_]['ayah']
                        if a_ != a_prev:
                            a_tot += 1
                            a_prev = a_
                ayah_count =  a_tot 
          
           
                
            safah_dic[ayah_pointer]['count'] = ayah_count
            safah_dic[ayah_pointer]['data'] = safah_next
            safah_dic[ayah_pointer]['page'] = i
                      
            n_ = 0
            half_found = False
            a_prev = '288'
            for pos in safah_next: #522 583 643
              if half_found == True:
                    break
              else:  
                     #print( int(pos['ayah'],  int(to_ayah) ) )              
                     if int(pos['sura']) < int(to_surah) or (int(pos['sura']) == int(to_surah)  and  int(pos['ayah'] <= int(to_ayah) )):
                         a_ = pos['ayah']
                         if a_ != a_prev:
                             n_ += 1
                             a_prev =  a_
                  
                     maxY_pos = pos['max_y']
                     if maxY_pos >= TO_SCROLL:
                        half_found = True
            
            safah_dic[ayah_pointer]['scroll'] = n_ #int(halfY) - int(ayah_start) 
            ayah_pointer += ayah_count
            selection_count += ayah_count
            #print('selection_count all loop', selection_count)

    else: # not None  
        #print('surah', surah, 'ayah', ayah, 'to_ayah', to_ayah)
        safah_data= db_helper.get_data_for_safah(safah)
        safah = int(safah)
        ayah = str(pages[safah]['from'])
        to_ayah = str(pages[safah]['to'])
        surah = str(pages[safah]['surah'])
        #print(safah, ayah, to_ayah)


    #selection_count = ayah_pointer-1 # it points now to the count 
       
    get_Device()
    TPL = get_Device()
    
    
    
    if to_surah is None:
        to_surah = surah   
        
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
    n_times = (int(to_surah) - int(surah)) + 1
    for r in range (int(repeat)):
        for s in range(int(surah), int(to_surah)+1):
            _surahfill = uniformNumber(str(s))
            if n_times == 1:
                _ayah= ayah
                _toayah =   to_ayah
            elif  n_times > 1 and s ==  int(surah) :
                _ayah = ayah
                _toayah =   str(ayahCount[int(s)-1])
            elif  n_times > 1 and s ==  int(to_surah) :
                _ayah = '1'
                _toayah =   to_ayah
            elif  n_times > 1 and s > int(surah) and s < int(to_surah) :
                _ayah = '1'
                _toayah =   str(ayahCount[int(s)-1])     
            
           
            for i in range (int(_ayah), int(_toayah)+1):
                ayah_fill = uniformNumber(str(i))
                for a in range(int(ayah_repeat)):
                    ayah_i =  "https://cdn.tarteel.net/ayat/N1/mp3/" + mode + "/" + reciter + "/" + _surahfill + ayah_fill + ".mp3"
                    to_repeat +=  "'" + ayah_i + "'" + ", "
         
    #print(to_repeat)
    #print(safah_dic.keys())
   
    return render_template(template, STATIC_URL=STATIC_URL, title=title, surah=surah, ayah=ayah, next_ayah=next_ayah, prev_ayah=prev_ayah, surah_fill=surah_fill, ayah_fill=ayah_fill, img=img, reciter=reciter, mode=mode, narration=narration, img_mode=img_mode, img_type=img_type, surah_list=surahNames,  values=[], pagePath=page_path, data=safah_data,  data_dic=safah_dic, highlight=ayah_id, resolution=resolution, to_repeat=to_repeat, safah=safah, repeat=repeat, stage_0=stage_0, to_ayah=to_ayah, selection_count=selection_count, ayah_repeat=ayah_repeat, radioReciters=radioReciters, reciter_names=reciter_names, mode_type=mode_type, surahNamesList=surahNamesList, ayahCount=ayahCount, parts_dic=parts_dic, to_surah=to_surah, QuranParts=QuranParts, part=part, hezb=hezb, quarter=quarter )
    
    
@app.route('/' )
@app.route('/<surah>/')
@app.route('/<surah>/<ayah>')
@app.route('/<surah>/<ayah>.html')
#@mobile_template('/{mobile/}' + USER_LANG + '_index.html')
def index(ayah='1', to_ayah='1', surah='1', to_surah= '1', reciter='06', mode='R1', narration='N1', img_mode='T1', img_type='01', ayah_id="1:1", img_res='1053', stage_0 = 0, safah='', repeat='1', selection_count = '1', ayah_repeat='1',  radioReciters = {}):
    
        
    surahNamesList = '' 
    for s in   range(len(surahNames)):
        surahNamesList +=   "<option value='" + str(s+1) + "'>" +  surahNames[s] + "</option>"
    partList = '' 
    for s in   range(len(QuranParts)):
        partList +=   "<option value='" + str(s+1) + "'>" +  QuranParts[s] + "</option>"         
        
    get_Device()
    TPL = get_Device()
    
    mode = request.args.get('mode')
    reciter = request.args.get('reciter')
    narration = request.args.get('narration')
    img_mode = request.args.get('img_mode')
    img_type = request.args.get('img_type')
    repeat = request.args.get('repeat')
    to_surah = request.args.get('to_surah')
    
    
    if to_surah is None:
        to_surah = surah   
        
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

    return render_template(template, STATIC_URL=STATIC_URL, title=title, surah=surah, ayah=ayah, to_ayah=to_ayah, next_ayah=next_ayah, prev_ayah=prev_ayah, surah_fill=surah_fill, ayah_fill=ayah_fill, img=img, reciter=reciter, mode=mode, narration=narration, img_mode=img_mode, img_type=img_type, surah_list=surahNames,  values=[], pagePath=page_path, data=safah_data, highlight=ayah_id, resolution=resolution, safah=safah, stage_0=stage_0, repeat=repeat, selection_count=selection_count, ayah_repeat=ayah_repeat, radioReciters=radioReciters, reciter_names=reciter_names, mode_type=mode_type, surahNamesList= surahNamesList, ayahCount=ayahCount, parts_dic=parts_dic, to_surah=to_surah, QuranParts=QuranParts)


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

reciter_names = {'01': 'محمود خليل الحصرى', '02': 'محمد صديق المنشاوى', '03': 'عبد الباسط عبد الصمد', '04': 'محمود على البنا' , '05': 'مصطفى اسماعيل', '06': 'أحمد نعينع', '07': 'على الحذيفى', '08': 'أيمن سويد'}
mode_type = {'R0': 'قراءة تعليمية للشيخ: ', 'R1': 'ترتيل للشيخ: ', 'R2': 'تجويد للشيخ: '}

QuranParts = ['', 'الأول', 'الثانى', 'الثالث', 'الرابع', 'الخامس', 'السادس', 'السابع', 'الثامن', 'التاسع', 'العاشر', 'الحادى عشر', 'الثانى عشر', 'الثالث عشر', 'الرابع عشر', 'الخامس عشر', 'السادس عشر', 'السابع عشر', 'الثامن عشر', 'التاسع عشر', 'العشرون', 'الواحد والعشرون', 'الثانى والعشرون', 'الثالث والعشرون', 'الرابع والعشرون', 'الخامس والعشرون', 'السادس والعشرون', 'السابع والعشرون', 'الثامن والعشرون', 'التاسع والعشرون', 'الثلاثون', 'الجزء كاملاً', 'الحزب كاملاً']
 

ayahCount = [7, 286, 200, 176, 120, 165, 206, 75, 129, 109, 123, 111, 43, 52, 99, 128, 111, 110, 98, 135, 112, 78, 118, 64, 77, 227, 93, 88, 69, 60, 34, 30, 73, 54, 45, 83, 182, 88, 75, 85, 54, 53, 89, 59, 37, 35, 38, 29, 18, 45, 60, 49, 62, 55, 78, 96, 29, 22, 24, 13, 14, 11, 11, 18, 12, 12, 30, 52, 52, 44, 28, 28, 20, 56, 40, 31, 50, 40, 46, 42, 29, 19, 36, 25, 22, 17, 19, 26, 30, 20, 15, 21, 11, 8, 8, 19, 5, 8, 8, 11, 11, 8, 3, 9, 5, 4, 7, 3, 6, 3, 5, 4, 5, 6]

surahNames = ["الفاتحة", "البقرة", "آل عمران", "النساء", "المائدة", "الأنعام", "الأعراف", "الأنفال", "التوبة", "يونس", "هود", "يوسف", "الرعد", "إبراهيم", "الحجر", "النحل", "الإسراء", "الكهف", "مريم", "طه", "الأنبياء", "الحج", "المؤمنون", "النور", "الفرقان", "الشعراء", "النمل", "القصص", "العنكبوت", "الروم", "لقمان", "السجدة", "سورة الأحزاب", "سبأ", "فاطر", "يس", "الصافات", "ص", "الزمر", "غافر", "فصلت", "الشورى", "الزخرف", "الدخان", "الجاثية", "الأحقاف", "محمد", "الفتح", "الحجرات", "ق", "الذاريات", "الطور", "النجم", "القمر", "الرحمن", "الواقعة", "الحديد", "المجادلة", "الحشر", "الممتحنة", "الصف", "الجمعة", "المنافقون", "التغابن", "الطلاق", "التحريم", "الملك", "القلم", "الحاقة", "المعارج", "نوح", "الجن", "المزمل", "المدثر", "القيامة", "الإنسان", "المرسلات", "النبأ", "النازعات", "عبس", "التكوير", "الانفطار", "المطففين", "الإنشقاق", "البروج", "الطارق", "الأعلى", "الغاشية", "الفجر", "البلد", "الشمس", "الليل", "الضحى", "الشرح", "التين", "العلق", "القدر", "البينة", "الزلزلة", "العاديات", "القارعة", "التكاثر", "العصر", "الهمزة", "الفيل", "قريش", "الماعون", "الكوثر", "الكافرون", "النصر", "المسد", "الإخلاص", "الفلق", "الناس"]

parts_dic = {
1: {'hezb1': {  'q1': {'from_ayah':1, 'from_surah':1, 'from_page':1, 'to_ayah':25, 'to_surah':2, 'to_page':5},
                'q2': {'from_ayah':26, 'from_surah':2, 'from_page':5, 'to_ayah':43, 'to_surah':2, 'to_page':7},
                'q3': {'from_ayah':44, 'from_surah':2, 'from_page':7, 'to_ayah':59, 'to_surah':2, 'to_page':9},
                'q4': {'from_ayah':60, 'from_surah':2, 'from_page':9, 'to_ayah':74, 'to_surah':2, 'to_page':11} },
                
    'hezb2': {  'q1': {'from_ayah':75, 'from_surah':2, 'from_page':11, 'to_ayah':91, 'to_surah':2, 'to_page':14},
                'q2': {'from_ayah':92, 'from_surah':2, 'from_page':14, 'to_ayah':105, 'to_surah':2, 'to_page':16},
                'q3': {'from_ayah':106, 'from_surah':2, 'from_page':17, 'to_ayah':123, 'to_surah':2, 'to_page':19},
                'q4': {'from_ayah':124, 'from_surah':2, 'from_page':19, 'to_ayah':141, 'to_surah':2, 'to_page':21} } },              
                
2: {'hezb1': { 'q1': {'from_ayah':142, 'from_surah':2, 'from_page':22, 'to_ayah':157, 'to_surah':2, 'to_page':24},
                'q2': {'from_ayah':158, 'from_surah':2, 'from_page':24, 'to_ayah':176, 'to_surah':2, 'to_page':26},
                'q3': {'from_ayah':177, 'from_surah':2, 'from_page':27, 'to_ayah':188, 'to_surah':2, 'to_page':29},
                'q4': {'from_ayah':189, 'from_surah':2, 'from_page':29, 'to_ayah':202, 'to_surah':2, 'to_page':31} },
                
    'hezb2': {  'q1': {'from_ayah':203, 'from_surah':2, 'from_page':32, 'to_ayah':218, 'to_surah':2, 'to_page':34},
                'q2': {'from_ayah':219, 'from_surah':2, 'from_page':34, 'to_ayah':232, 'to_surah':2, 'to_page':37},
                'q3': {'from_ayah':233, 'from_surah':2, 'from_page':37, 'to_ayah':242, 'to_surah':2, 'to_page':39},
                'q4': {'from_ayah':243, 'from_surah':2, 'from_page':39, 'to_ayah':252, 'to_surah':2, 'to_page':41} } },   

3: {'hezb1': {  'q1': {'from_ayah':253, 'from_surah':2, 'from_page':42, 'to_ayah':262, 'to_surah':2, 'to_page':44},
                'q2': {'from_ayah':263, 'from_surah':2, 'from_page':44, 'to_ayah':271, 'to_surah':2, 'to_page':46},
                'q3': {'from_ayah':272, 'from_surah':2, 'from_page':46, 'to_ayah':282, 'to_surah':2, 'to_page':48},
                'q4': {'from_ayah':283, 'from_surah':2, 'from_page':49, 'to_ayah':14, 'to_surah':3, 'to_page':51} },
                
    'hezb2': {  'q1': {'from_ayah':15, 'from_surah':3, 'from_page':51, 'to_ayah':32, 'to_surah':3, 'to_page':54},
                'q2': {'from_ayah':33, 'from_surah':3, 'from_page':54, 'to_ayah':51, 'to_surah':3, 'to_page':56},
                'q3': {'from_ayah':52, 'from_surah':3, 'from_page':56, 'to_ayah':74, 'to_surah':3, 'to_page':59},
                'q4': {'from_ayah':75, 'from_surah':3, 'from_page':59, 'to_ayah':91, 'to_surah':3, 'to_page':61} } }, 
 
4: {'hezb1': {  'q1': {'from_ayah':92, 'from_surah':3, 'from_page':62, 'to_ayah':112, 'to_surah':3, 'to_page':64},
                'q2': {'from_ayah':113, 'from_surah':3, 'from_page':64, 'to_ayah':132, 'to_surah':3, 'to_page':66},
                'q3': {'from_ayah':133, 'from_surah':3, 'from_page':67, 'to_ayah':152, 'to_surah':3, 'to_page':69},
                'q4': {'from_ayah':153, 'from_surah':3, 'from_page':69, 'to_ayah':170, 'to_surah':3, 'to_page':72} },
                
    'hezb2': {  'q1': {'from_ayah':171, 'from_surah':3, 'from_page':72, 'to_ayah':185, 'to_surah':3, 'to_page':74},
                'q2': {'from_ayah':186, 'from_surah':3, 'from_page':74, 'to_ayah':200, 'to_surah':3, 'to_page':76},
                'q3': {'from_ayah':1, 'from_surah':4, 'from_page':77, 'to_ayah':11, 'to_surah':4, 'to_page':78},
                'q4': {'from_ayah':12, 'from_surah':4, 'from_page':79, 'to_ayah':23, 'to_surah':4, 'to_page':81} } }, 
                
 
}

                



pages = {
1: {'surah':1, 'from':1, 'to':7},
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
81: {'surah':4, 'from':20, 'to':23},
82: {'surah':4, 'from':24, 'to':26},
83: {'surah':4, 'from':27, 'to':33},
84: {'surah':4, 'from':34, 'to':37},
85: {'surah':4, 'from':38, 'to':44},
86: {'surah':4, 'from':45, 'to':51},
87: {'surah':4, 'from':52, 'to':59},
88: {'surah':4, 'from':60, 'to':65},
89: {'surah':4, 'from':66, 'to':74},
90: {'surah':4, 'from':75, 'to':79},
91: {'surah':4, 'from':80, 'to':86},
92: {'surah':4, 'from':87, 'to':91},
93: {'surah':4, 'from':92, 'to':94},
94: {'surah':4, 'from':95, 'to':101},
95: {'surah':4, 'from':102, 'to':105},
96: {'surah':4, 'from':106, 'to':113},
97: {'surah':4, 'from':114, 'to':121},
98: {'surah':4, 'from':122, 'to':127},
99: {'surah':4, 'from':128, 'to':134},
100: {'surah':4, 'from':135, 'to':140},
101: {'surah':4, 'from':141, 'to':147},
102: {'surah':4, 'from':148, 'to':154},
103: {'surah':4, 'from':155, 'to':162},
104: {'surah':4, 'from':163, 'to':170},
105: {'surah':4, 'from':171, 'to':175},
106: {'surah':5, 'from':176, 'to':2},
107: {'surah':5, 'from':3, 'to':5},
108: {'surah':5, 'from':6, 'to':9},
109: {'surah':5, 'from':10, 'to':13},
110: {'surah':5, 'from':14, 'to':17},
111: {'surah':5, 'from':18, 'to':23},
112: {'surah':5, 'from':24, 'to':31},
113: {'surah':5, 'from':32, 'to':36},
114: {'surah':5, 'from':37, 'to':41},
115: {'surah':5, 'from':42, 'to':45},
116: {'surah':5, 'from':46, 'to':50},
117: {'surah':5, 'from':51, 'to':57},
118: {'surah':5, 'from':58, 'to':64},
119: {'surah':5, 'from':65, 'to':70},
120: {'surah':5, 'from':71, 'to':76},
121: {'surah':5, 'from':77, 'to':82},
122: {'surah':5, 'from':83, 'to':89},
123: {'surah':5, 'from':90, 'to':95},
124: {'surah':5, 'from':96, 'to':103},
125: {'surah':5, 'from':104, 'to':108},
126: {'surah':5, 'from':109, 'to':113},
127: {'surah':5, 'from':114, 'to':120},
128: {'surah':6, 'from':1, 'to':8},
129: {'surah':6, 'from':9, 'to':18},
130: {'surah':6, 'from':19, 'to':27},
131: {'surah':6, 'from':28, 'to':35},
132: {'surah':6, 'from':36, 'to':44},
133: {'surah':6, 'from':45, 'to':52},
134: {'surah':6, 'from':53, 'to':59},
135: {'surah':6, 'from':60, 'to':68},
136: {'surah':6, 'from':69, 'to':73},
137: {'surah':6, 'from':74, 'to':81},
138: {'surah':6, 'from':82, 'to':90},
139: {'surah':6, 'from':91, 'to':94},
140: {'surah':6, 'from':95, 'to':101},
141: {'surah':6, 'from':102, 'to':110},
142: {'surah':6, 'from':111, 'to':118},
143: {'surah':6, 'from':119, 'to':124},
144: {'surah':6, 'from':125, 'to':131},
145: {'surah':6, 'from':132, 'to':137},
146: {'surah':6, 'from':138, 'to':142},
147: {'surah':6, 'from':143, 'to':146},
148: {'surah':6, 'from':147, 'to':151},
149: {'surah':6, 'from':152, 'to':157},
150: {'surah':6, 'from':158, 'to':165},
151: {'surah':7, 'from':1, 'to':11},
152: {'surah':7, 'from':12, 'to':22},
153: {'surah':7, 'from':23, 'to':30},
154: {'surah':7, 'from':31, 'to':37},
155: {'surah':7, 'from':38, 'to':43},
156: {'surah':7, 'from':44, 'to':51},
157: {'surah':7, 'from':52, 'to':57},
158: {'surah':7, 'from':58, 'to':67},
159: {'surah':7, 'from':68, 'to':73},
160: {'surah':7, 'from':74, 'to':81},
161: {'surah':7, 'from':82, 'to':87},
162: {'surah':7, 'from':88, 'to':95},
163: {'surah':7, 'from':96, 'to':104},
164: {'surah':7, 'from':105, 'to':120},
165: {'surah':7, 'from':121, 'to':130},
166: {'surah':7, 'from':131, 'to':137},
167: {'surah':7, 'from':138, 'to':143},
168: {'surah':7, 'from':144, 'to':149},
169: {'surah':7, 'from':150, 'to':155},
170: {'surah':7, 'from':156, 'to':159},
171: {'surah':7, 'from':160, 'to':163},
172: {'surah':7, 'from':164, 'to':170},
173: {'surah':7, 'from':171, 'to':178},
174: {'surah':7, 'from':179, 'to':187},
175: {'surah':7, 'from':188, 'to':195},
176: {'surah':7, 'from':196, 'to':206},
177: {'surah':8, 'from':1, 'to':8},
178: {'surah':8, 'from':9, 'to':16},
179: {'surah':8, 'from':17, 'to':25},
180: {'surah':8, 'from':26, 'to':33},
181: {'surah':8, 'from':34, 'to':40},
182: {'surah':8, 'from':41, 'to':45},
183: {'surah':8, 'from':46, 'to':52},
184: {'surah':8, 'from':53, 'to':61},
185: {'surah':8, 'from':62, 'to':69},
186: {'surah':8, 'from':70, 'to':75},
187: {'surah':9, 'from':1, 'to':6},
188: {'surah':9, 'from':7, 'to':13},
189: {'surah':9, 'from':14, 'to':20},
190: {'surah':9, 'from':21, 'to':26},
191: {'surah':9, 'from':27, 'to':31},
192: {'surah':9, 'from':32, 'to':36},
193: {'surah':9, 'from':37, 'to':40},
194: {'surah':9, 'from':41, 'to':47},
195: {'surah':9, 'from':48, 'to':54},
196: {'surah':9, 'from':55, 'to':61},
197: {'surah':9, 'from':62, 'to':68},
198: {'surah':9, 'from':69, 'to':72},
199: {'surah':9, 'from':73, 'to':79},
200: {'surah':9, 'from':80, 'to':86},
201: {'surah':9, 'from':87, 'to':93},
202: {'surah':9, 'from':94, 'to':99},
203: {'surah':9, 'from':100, 'to':106},
204: {'surah':9, 'from':107, 'to':111},
205: {'surah':9, 'from':112, 'to':117},
206: {'surah':9, 'from':118, 'to':122},
207: {'surah':9, 'from':123, 'to':129},
208: {'surah':10, 'from':1, 'to':6},
209: {'surah':10, 'from':7, 'to':14},
210: {'surah':10, 'from':15, 'to':20},
211: {'surah':10, 'from':21, 'to':25},
212: {'surah':10, 'from':26, 'to':33},
213: {'surah':10, 'from':34, 'to':42},
214: {'surah':10, 'from':43, 'to':53},
215: {'surah':10, 'from':54, 'to':61},
216: {'surah':10, 'from':62, 'to':70},
217: {'surah':10, 'from':71, 'to':78},
218: {'surah':10, 'from':79, 'to':88},
219: {'surah':10, 'from':89, 'to':97},
220: {'surah':10, 'from':98, 'to':106},
221: {'surah':11, 'from':107, 'to':5},
222: {'surah':11, 'from':6, 'to':12},
223: {'surah':11, 'from':13, 'to':19},
224: {'surah':11, 'from':20, 'to':28},
225: {'surah':11, 'from':29, 'to':37},
226: {'surah':11, 'from':38, 'to':45},
227: {'surah':11, 'from':46, 'to':53},
228: {'surah':11, 'from':54, 'to':62},
229: {'surah':11, 'from':63, 'to':71},
230: {'surah':11, 'from':72, 'to':81},
231: {'surah':11, 'from':82, 'to':88},
232: {'surah':11, 'from':89, 'to':97},
233: {'surah':11, 'from':98, 'to':108},
234: {'surah':11, 'from':109, 'to':117},
235: {'surah':12, 'from':118, 'to':4},
236: {'surah':12, 'from':5, 'to':14},
237: {'surah':12, 'from':15, 'to':22},
238: {'surah':12, 'from':23, 'to':30},
239: {'surah':12, 'from':31, 'to':37},
240: {'surah':12, 'from':38, 'to':43},
241: {'surah':12, 'from':44, 'to':52},
242: {'surah':12, 'from':53, 'to':63},
243: {'surah':12, 'from':64, 'to':69},
244: {'surah':12, 'from':70, 'to':78},
245: {'surah':12, 'from':79, 'to':86},
246: {'surah':12, 'from':87, 'to':95},
247: {'surah':12, 'from':96, 'to':103},
248: {'surah':12, 'from':104, 'to':111},
249: {'surah':13, 'from':1, 'to':5},
250: {'surah':13, 'from':6, 'to':13},
251: {'surah':13, 'from':14, 'to':18},
252: {'surah':13, 'from':19, 'to':28},
253: {'surah':13, 'from':29, 'to':34},
254: {'surah':13, 'from':35, 'to':42},
255: {'surah':14, 'from':43, 'to':5},
256: {'surah':14, 'from':6, 'to':10},
257: {'surah':14, 'from':11, 'to':18},
258: {'surah':14, 'from':19, 'to':24},
259: {'surah':14, 'from':25, 'to':33},
260: {'surah':14, 'from':34, 'to':42},
261: {'surah':14, 'from':43, 'to':52},
262: {'surah':15, 'from':1, 'to':15},
263: {'surah':15, 'from':16, 'to':31},
264: {'surah':15, 'from':32, 'to':51},
265: {'surah':15, 'from':52, 'to':70},
266: {'surah':15, 'from':71, 'to':90},
267: {'surah':16, 'from':91, 'to':6},
268: {'surah':16, 'from':7, 'to':14},
269: {'surah':16, 'from':15, 'to':26},
270: {'surah':16, 'from':27, 'to':34},
271: {'surah':16, 'from':35, 'to':42},
272: {'surah':16, 'from':43, 'to':54},
273: {'surah':16, 'from':55, 'to':64},
274: {'surah':16, 'from':65, 'to':72},
275: {'surah':16, 'from':73, 'to':79},
276: {'surah':16, 'from':80, 'to':87},
277: {'surah':16, 'from':88, 'to':93},
278: {'surah':16, 'from':94, 'to':102},
279: {'surah':16, 'from':103, 'to':110},
280: {'surah':16, 'from':111, 'to':118},
281: {'surah':16, 'from':119, 'to':128},
282: {'surah':17, 'from':1, 'to':7},
283: {'surah':17, 'from':8, 'to':17},
284: {'surah':17, 'from':18, 'to':27},
285: {'surah':17, 'from':28, 'to':38},
286: {'surah':17, 'from':39, 'to':49},
287: {'surah':17, 'from':50, 'to':58},
288: {'surah':17, 'from':59, 'to':66},
289: {'surah':17, 'from':67, 'to':75},
290: {'surah':17, 'from':76, 'to':86},
291: {'surah':17, 'from':87, 'to':96},
292: {'surah':17, 'from':97, 'to':104},
293: {'surah':18, 'from':105, 'to':4},
294: {'surah':18, 'from':5, 'to':15},
295: {'surah':18, 'from':16, 'to':20},
296: {'surah':18, 'from':21, 'to':27},
297: {'surah':18, 'from':28, 'to':34},
298: {'surah':18, 'from':35, 'to':45},
299: {'surah':18, 'from':46, 'to':53},
300: {'surah':18, 'from':54, 'to':61},
301: {'surah':18, 'from':62, 'to':74},
302: {'surah':18, 'from':75, 'to':83},
303: {'surah':18, 'from':84, 'to':97},
304: {'surah':18, 'from':98, 'to':110},
305: {'surah':19, 'from':1, 'to':11},
306: {'surah':19, 'from':12, 'to':25},
307: {'surah':19, 'from':26, 'to':38},
308: {'surah':19, 'from':39, 'to':51},
309: {'surah':19, 'from':52, 'to':64},
310: {'surah':19, 'from':65, 'to':76},
311: {'surah':19, 'from':77, 'to':95},
312: {'surah':20, 'from':96, 'to':12},
313: {'surah':20, 'from':13, 'to':37},
314: {'surah':20, 'from':38, 'to':51},
315: {'surah':20, 'from':52, 'to':64},
316: {'surah':20, 'from':65, 'to':76},
317: {'surah':20, 'from':77, 'to':87},
318: {'surah':20, 'from':88, 'to':98},
319: {'surah':20, 'from':99, 'to':113},
320: {'surah':20, 'from':114, 'to':125},
321: {'surah':20, 'from':126, 'to':135},
322: {'surah':21, 'from':1, 'to':10},
323: {'surah':21, 'from':11, 'to':24},
324: {'surah':21, 'from':25, 'to':35},
325: {'surah':21, 'from':36, 'to':44},
326: {'surah':21, 'from':45, 'to':57},
327: {'surah':21, 'from':58, 'to':72},
328: {'surah':21, 'from':73, 'to':81},
329: {'surah':21, 'from':82, 'to':90},
330: {'surah':21, 'from':91, 'to':101},
331: {'surah':21, 'from':102, 'to':112},
332: {'surah':22, 'from':1, 'to':5},
333: {'surah':22, 'from':6, 'to':15},
334: {'surah':22, 'from':16, 'to':23},
335: {'surah':22, 'from':24, 'to':30},
336: {'surah':22, 'from':31, 'to':38},
337: {'surah':22, 'from':39, 'to':46},
338: {'surah':22, 'from':47, 'to':55},
339: {'surah':22, 'from':56, 'to':64},
340: {'surah':22, 'from':65, 'to':72},
341: {'surah':22, 'from':73, 'to':78},
342: {'surah':23, 'from':1, 'to':17},
343: {'surah':23, 'from':18, 'to':27},
344: {'surah':23, 'from':28, 'to':42},
345: {'surah':23, 'from':43, 'to':59},
346: {'surah':23, 'from':60, 'to':74},
347: {'surah':23, 'from':75, 'to':89},
348: {'surah':23, 'from':90, 'to':104},
349: {'surah':23, 'from':105, 'to':118},
350: {'surah':24, 'from':1, 'to':10},
351: {'surah':24, 'from':11, 'to':20},
352: {'surah':24, 'from':21, 'to':27},
353: {'surah':24, 'from':28, 'to':31},
354: {'surah':24, 'from':32, 'to':36},
355: {'surah':24, 'from':37, 'to':43},
356: {'surah':24, 'from':44, 'to':53},
357: {'surah':24, 'from':54, 'to':58},
358: {'surah':24, 'from':59, 'to':61},
359: {'surah':25, 'from':62, 'to':2},
360: {'surah':25, 'from':3, 'to':11},
361: {'surah':25, 'from':12, 'to':20},
362: {'surah':25, 'from':21, 'to':32},
363: {'surah':25, 'from':33, 'to':43},
364: {'surah':25, 'from':44, 'to':55},
365: {'surah':25, 'from':56, 'to':67},
366: {'surah':25, 'from':68, 'to':77},
367: {'surah':26, 'from':1, 'to':19},
368: {'surah':26, 'from':20, 'to':39},
369: {'surah':26, 'from':40, 'to':60},
370: {'surah':26, 'from':61, 'to':83},
371: {'surah':26, 'from':84, 'to':111},
372: {'surah':26, 'from':112, 'to':136},
373: {'surah':26, 'from':137, 'to':159},
374: {'surah':26, 'from':160, 'to':183},
375: {'surah':26, 'from':184, 'to':206},
376: {'surah':26, 'from':207, 'to':227},
377: {'surah':27, 'from':1, 'to':13},
378: {'surah':27, 'from':14, 'to':22},
379: {'surah':27, 'from':23, 'to':35},
380: {'surah':27, 'from':36, 'to':44},
381: {'surah':27, 'from':45, 'to':55},
382: {'surah':27, 'from':56, 'to':63},
383: {'surah':27, 'from':64, 'to':76},
384: {'surah':27, 'from':77, 'to':88},
385: {'surah':28, 'from':89, 'to':5},
386: {'surah':28, 'from':6, 'to':13},
387: {'surah':28, 'from':14, 'to':21},
388: {'surah':28, 'from':22, 'to':28},
389: {'surah':28, 'from':29, 'to':35},
390: {'surah':28, 'from':36, 'to':43},
391: {'surah':28, 'from':44, 'to':50},
392: {'surah':28, 'from':51, 'to':59},
393: {'surah':28, 'from':60, 'to':70},
394: {'surah':28, 'from':71, 'to':77},
395: {'surah':28, 'from':78, 'to':84},
396: {'surah':29, 'from':85, 'to':6},
397: {'surah':29, 'from':7, 'to':14},
398: {'surah':29, 'from':15, 'to':23},
399: {'surah':29, 'from':24, 'to':30},
400: {'surah':29, 'from':31, 'to':38},
401: {'surah':29, 'from':39, 'to':45},
402: {'surah':29, 'from':46, 'to':52},
403: {'surah':29, 'from':53, 'to':63},
404: {'surah':30, 'from':64, 'to':5},
405: {'surah':30, 'from':6, 'to':15},
406: {'surah':30, 'from':16, 'to':24},
407: {'surah':30, 'from':25, 'to':32},
408: {'surah':30, 'from':33, 'to':41},
409: {'surah':30, 'from':42, 'to':50},
410: {'surah':30, 'from':51, 'to':60},
411: {'surah':31, 'from':1, 'to':11},
412: {'surah':31, 'from':12, 'to':19},
413: {'surah':31, 'from':20, 'to':28},
414: {'surah':31, 'from':29, 'to':34},
415: {'surah':32, 'from':1, 'to':11},
416: {'surah':32, 'from':12, 'to':20},
417: {'surah':32, 'from':21, 'to':30},
418: {'surah':33, 'from':1, 'to':6},
419: {'surah':33, 'from':7, 'to':15},
420: {'surah':33, 'from':16, 'to':22},
421: {'surah':33, 'from':23, 'to':30},
422: {'surah':33, 'from':31, 'to':35},
423: {'surah':33, 'from':36, 'to':43},
424: {'surah':33, 'from':44, 'to':50},
425: {'surah':33, 'from':51, 'to':54},
426: {'surah':33, 'from':55, 'to':62},
427: {'surah':33, 'from':63, 'to':73},
428: {'surah':34, 'from':1, 'to':7},
429: {'surah':34, 'from':8, 'to':14},
430: {'surah':34, 'from':15, 'to':22},
431: {'surah':34, 'from':23, 'to':31},
432: {'surah':34, 'from':32, 'to':39},
433: {'surah':34, 'from':40, 'to':48},
434: {'surah':35, 'from':49, 'to':3},
435: {'surah':35, 'from':4, 'to':11},
436: {'surah':35, 'from':12, 'to':18},
437: {'surah':35, 'from':19, 'to':30},
438: {'surah':35, 'from':31, 'to':38},
439: {'surah':35, 'from':39, 'to':44},
440: {'surah':36, 'from':45, 'to':12},
441: {'surah':36, 'from':13, 'to':27},
442: {'surah':36, 'from':28, 'to':40},
443: {'surah':36, 'from':41, 'to':54},
444: {'surah':36, 'from':55, 'to':70},
445: {'surah':36, 'from':71, 'to':83},
446: {'surah':37, 'from':1, 'to':24},
447: {'surah':37, 'from':25, 'to':51},
448: {'surah':37, 'from':52, 'to':76},
449: {'surah':37, 'from':77, 'to':102},
450: {'surah':37, 'from':103, 'to':126},
451: {'surah':37, 'from':127, 'to':153},
452: {'surah':37, 'from':154, 'to':182},
453: {'surah':38, 'from':1, 'to':16},
454: {'surah':38, 'from':17, 'to':26},
455: {'surah':38, 'from':27, 'to':42},
456: {'surah':38, 'from':43, 'to':61},
457: {'surah':38, 'from':62, 'to':83},
458: {'surah':39, 'from':84, 'to':5},
459: {'surah':39, 'from':6, 'to':10},
460: {'surah':39, 'from':11, 'to':21},
461: {'surah':39, 'from':22, 'to':31},
462: {'surah':39, 'from':32, 'to':40},
463: {'surah':39, 'from':41, 'to':47},
464: {'surah':39, 'from':48, 'to':56},
465: {'surah':39, 'from':57, 'to':67},
466: {'surah':39, 'from':68, 'to':74},
467: {'surah':40, 'from':75, 'to':7},
468: {'surah':40, 'from':8, 'to':16},
469: {'surah':40, 'from':17, 'to':25},
470: {'surah':40, 'from':26, 'to':33},
471: {'surah':40, 'from':34, 'to':40},
472: {'surah':40, 'from':41, 'to':49},
473: {'surah':40, 'from':50, 'to':58},
474: {'surah':40, 'from':59, 'to':66},
475: {'surah':40, 'from':67, 'to':77},
476: {'surah':40, 'from':78, 'to':85},
477: {'surah':41, 'from':1, 'to':11},
478: {'surah':41, 'from':12, 'to':20},
479: {'surah':41, 'from':21, 'to':29},
480: {'surah':41, 'from':30, 'to':38},
481: {'surah':41, 'from':39, 'to':46},
482: {'surah':41, 'from':47, 'to':54},
483: {'surah':42, 'from':1, 'to':10},
484: {'surah':42, 'from':11, 'to':15},
485: {'surah':42, 'from':16, 'to':22},
486: {'surah':42, 'from':23, 'to':31},
487: {'surah':42, 'from':32, 'to':44},
488: {'surah':42, 'from':45, 'to':51},
489: {'surah':43, 'from':52, 'to':10},
490: {'surah':43, 'from':11, 'to':22},
491: {'surah':43, 'from':23, 'to':33},
492: {'surah':43, 'from':34, 'to':47},
493: {'surah':43, 'from':48, 'to':60},
494: {'surah':43, 'from':61, 'to':73},
495: {'surah':43, 'from':74, 'to':89},
496: {'surah':44, 'from':1, 'to':18},
497: {'surah':44, 'from':19, 'to':39},
498: {'surah':44, 'from':40, 'to':59},
499: {'surah':45, 'from':1, 'to':13},
500: {'surah':45, 'from':14, 'to':22},
501: {'surah':45, 'from':23, 'to':32},
502: {'surah':46, 'from':33, 'to':5},
503: {'surah':46, 'from':6, 'to':14},
504: {'surah':46, 'from':15, 'to':20},
505: {'surah':46, 'from':21, 'to':28},
506: {'surah':46, 'from':29, 'to':35},
507: {'surah':47, 'from':1, 'to':11},
508: {'surah':47, 'from':12, 'to':19},
509: {'surah':47, 'from':20, 'to':29},
510: {'surah':47, 'from':30, 'to':38},
511: {'surah':48, 'from':1, 'to':9},
512: {'surah':48, 'from':10, 'to':15},
513: {'surah':48, 'from':16, 'to':23},
514: {'surah':48, 'from':24, 'to':28},
515: {'surah':49, 'from':29, 'to':4},
516: {'surah':49, 'from':5, 'to':11},
517: {'surah':49, 'from':12, 'to':18},
518: {'surah':50, 'from':1, 'to':15},
519: {'surah':50, 'from':16, 'to':35},
520: {'surah':51, 'from':36, 'to':6},
521: {'surah':51, 'from':7, 'to':30},
522: {'surah':51, 'from':31, 'to':51},
523: {'surah':52, 'from':52, 'to':14},
524: {'surah':52, 'from':15, 'to':31},
525: {'surah':52, 'from':32, 'to':49},
526: {'surah':53, 'from':1, 'to':26},
527: {'surah':53, 'from':27, 'to':44},
528: {'surah':54, 'from':45, 'to':6},
529: {'surah':54, 'from':7, 'to':27},
530: {'surah':54, 'from':28, 'to':49},
531: {'surah':55, 'from':50, 'to':16},
532: {'surah':55, 'from':17, 'to':40},
533: {'surah':55, 'from':41, 'to':67},
534: {'surah':56, 'from':68, 'to':16},
535: {'surah':56, 'from':17, 'to':50},
536: {'surah':56, 'from':51, 'to':76},
537: {'surah':57, 'from':77, 'to':3},
538: {'surah':57, 'from':4, 'to':11},
539: {'surah':57, 'from':12, 'to':18},
540: {'surah':57, 'from':19, 'to':24},
541: {'surah':57, 'from':25, 'to':29},
542: {'surah':58, 'from':1, 'to':6},
543: {'surah':58, 'from':7, 'to':11},
544: {'surah':58, 'from':12, 'to':21},
545: {'surah':59, 'from':22, 'to':3},
546: {'surah':59, 'from':4, 'to':9},
547: {'surah':59, 'from':10, 'to':16},
548: {'surah':59, 'from':17, 'to':24},
549: {'surah':60, 'from':1, 'to':5},
550: {'surah':60, 'from':6, 'to':11},
551: {'surah':61, 'from':12, 'to':5},
552: {'surah':61, 'from':6, 'to':14},
553: {'surah':62, 'from':1, 'to':8},
554: {'surah':63, 'from':9, 'to':4},
555: {'surah':63, 'from':5, 'to':11},
556: {'surah':64, 'from':1, 'to':9},
557: {'surah':64, 'from':10, 'to':18},
558: {'surah':65, 'from':1, 'to':5},
559: {'surah':65, 'from':6, 'to':12},
560: {'surah':66, 'from':1, 'to':7},
561: {'surah':66, 'from':8, 'to':12},
562: {'surah':67, 'from':1, 'to':12},
563: {'surah':67, 'from':13, 'to':26},
564: {'surah':68, 'from':27, 'to':15},
565: {'surah':68, 'from':16, 'to':42},
566: {'surah':69, 'from':43, 'to':8},
567: {'surah':69, 'from':9, 'to':34},
568: {'surah':70, 'from':35, 'to':10},
569: {'surah':70, 'from':11, 'to':39},
570: {'surah':71, 'from':40, 'to':10},
571: {'surah':71, 'from':11, 'to':28},
572: {'surah':72, 'from':1, 'to':13},
573: {'surah':72, 'from':14, 'to':28},
574: {'surah':73, 'from':1, 'to':19},
575: {'surah':74, 'from':20, 'to':17},
576: {'surah':74, 'from':18, 'to':47},
577: {'surah':75, 'from':48, 'to':19},
578: {'surah':76, 'from':20, 'to':5},
579: {'surah':76, 'from':6, 'to':25},
580: {'surah':77, 'from':26, 'to':19},
581: {'surah':77, 'from':20, 'to':50},
582: {'surah':78, 'from':1, 'to':30},
583: {'surah':79, 'from':31, 'to':15},
584: {'surah':79, 'from':16, 'to':46},
585: {'surah':80, 'from':1, 'to':42},
586: {'surah':81, 'from':1, 'to':29},
587: {'surah':83, 'from':1, 'to':6},
588: {'surah':83, 'from':7, 'to':34},
589: {'surah':84, 'from':35, 'to':25},
590: {'surah':85, 'from':1, 'to':22},
591: {'surah':87, 'from':1, 'to':15},
592: {'surah':88, 'from':16, 'to':26},
593: {'surah':89, 'from':1, 'to':23},
594: {'surah':90, 'from':24, 'to':20},
595: {'surah':92, 'from':1, 'to':14},
596: {'surah':94, 'from':15, 'to':8},
597: {'surah':96, 'from':1, 'to':19},
598: {'surah':98, 'from':1, 'to':7},
599: {'surah':100, 'from':8, 'to':9},
600: {'surah':102, 'from':10, 'to':8},
601: {'surah':105, 'from':1, 'to':5},
602: {'surah':108, 'from':1, 'to':3},
603: {'surah':111, 'from':1, 'to':5},
604: {'surah':114, 'from':1, 'to':6}
}
    
    
