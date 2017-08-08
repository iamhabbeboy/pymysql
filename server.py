from __future__ import division
from flask import Flask ,url_for,render_template,request,abort, session, redirect
from  werkzeug.debug import get_current_traceback
from flask.ext import excel
import pymysql.cursors
import math, json, collections
import os
import itertools
app = Flask(__name__)
connection = pymysql.connect(host='localhost', user='root', password='', db='flask', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
app.secret_key = os.urandom(24)

def combine_list(list_value):
    combine = []
    for x in list_value:
        combine = combine + x
    return combine

def get_error(list_value):
    error = 0
    for x in list_value:
        if x == '0':
            error = error + 1
    return error

@app.route('/', methods=['POST', 'GET'])
def index():
  count = 0
  found = []
  new_doc = []
  student = []
  new_record = []
  old_me = []
  totalP = 0
  percentA = 0
  average = 0
  old_split = []
  ermsg = 5
  old_split = []
  older_split = []
  compute = []
  ermessage = []
  get_me = ''

  if request.method == 'POST':
    with connection.cursor() as cursor:
      # Read a single record
      doc_type = request.form['doc_type'].encode('ascii', 'ignore').lower()
      doc_ = request.form['document'].encode('ascii', 'ignore').lower()

      if doc_type != "0":
          new_doc = doc_.split('.')
          """ Query Table for Record """
          sql = "SELECT * FROM `documents` WHERE `doc_type` = %s"
          cursor.execute(sql, (doc_type))
          result = cursor.fetchall()
          prt = ""
          if int(len(result)) > 0:
            """ This is the Old Documents From DB """
            for old in xrange(len(result)):
              old_ones = result[old]['docs'].encode('ascii', 'ignore').lower()
              old_split = old_ones.split('.')
              student_level = result[old]['level'].encode('ascii', 'ignore')
              student_matric = result[old]['matric'].encode('ascii', 'ignore')
              supervisor = result[old]['supervisor'].encode('ascii', 'ignore')
              topic = result[old]['topic'].encode('ascii', 'ignore')

              for x in xrange(len(old_split)):
                old_var = old_split[x].strip()
                """ This is for the new Doc... """
                for doc in xrange(len(new_doc)):
                  new_ones = new_doc[doc].strip().lower()
                  if old_var == new_ones:
                    if new_ones != '':
                      old_me.append(old_var)
                      found.append({
                       'found' : new_ones,
                       'matric': student_matric,
                       'level': student_level,
                       'topic': topic,
                       'supervisor' : supervisor })
                      older_split.append(old_split)
                      count = count +1
                      ermsg = 0
                      compute = combine_list(older_split)
                      ermessage.append('0')
                  else:
                      ermessage.append('1')
              get_me = get_error(ermessage)
              #totalP = int(len(found)) / int(len(compute))
              #average = math.floor(totalP * 100)
          else:
              ermsg = 3
      else:
          ermsg = 2
  else:
      result = ""
  #combine = str(len(found)) + str(len(old_split))
  return render_template("home.html", data=found, exist= len(compute), counter=int(len(found)), avg = average, std=student, errmsg = ermsg, test = get_me )

@app.route('/ajax', methods=['GET', 'POST'])
def ajax():
    if request.method == 'POST':
      topic = request.form['topic'].encode('ascii', 'ignore')
      superv = request.form['supervisor'].encode('ascii', 'ignore')
      year = request.form['year'].encode('ascii', 'ignore')
      level = request.form['level'].encode('ascii', 'ignore')
      matric = request.form['matric'].encode('ascii', 'ignore')
      doc_type = request.form['doc_type'].encode('ascii', 'ignore')
      doc = request.form['doc'].encode('ascii', 'ignore')
      """
        Connection to DB
      """
      cursor = connection.cursor()
      sql = "SELECT * FROM `documents` WHERE `doc_type` = %s AND `level` = %s AND `matric`= %s"
      cursor.execute(sql, (doc_type, level, matric))
      result = cursor.fetchall()
      rowcount = str(len(result))

      if rowcount == '1':
        message = "exist"
      else:
        cur = connection.cursor()
        query = "INSERT INTO `documents`(`docs`, `doc_type`, `level`, `matric`, `topic`, `supervisor`) VALUES(%s, %s, %s, %s, %s, %s)"
        cur.execute(query, (doc, doc_type, level, matric, topic, superv))
        connection.commit()
        message = "ok"
    else:
      message = "guest"
    return message

@app.route('/add-new', methods=['GET', 'POST'])
def add_new():
  lpush = ''
  ssid = ""
  if request.method == 'POST':

    doc_type = request.form['doc_type'].encode('ascii', 'ignore')
    doc_main = request.form['document'].encode('ascii', 'ignore')
    #a = doc_type + "_" + doc_main
    #lpush.append(a)
    cursor = connection.cursor()
    sql = "INSERT INTO `documents`(`docs`, `doc_type`) VALUES(%s, %s)"
    cursor.execute(sql, (doc_main, doc_type))
    connection.commit()
    lpush = 'Record Added Successfully !'
  else:
    lpush = ''

  """
    Validate User Session
  """
  return render_template('add-new.html', data=lpush)

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ""
    if request.method == 'POST':
        email = request.form['email'].encode('ascii', 'ignore')
        pass1  = request.form['pass'].encode('ascii', 'ignore')
        cursor = connection.cursor()
        sql = "SELECT * FROM `users` WHERE `email` = %s AND `password` = %s"
        cursor.execute(sql, (email, pass1))
        result = cursor.fetchall()
        rowcount = int(len(result))
        if rowcount > 0:
            session['adminkey'] = email
            return redirect(url_for('dashboard'))
        else:
            #redirect(url_for('login'))
            msg = "Invalid Information supplied !"
    return render_template('login.html', error = msg )

@app.route('/dashboard')
def dashboard():
    cursor = connection.cursor()
    sql = "SELECT * FROM `documents`"
    cursor.execute(sql)
    rows = len(cursor.fetchall())
    """
      Topic Registered
    """
    query = "SELECT * FROM `topics`"
    cursor.execute(query)
    rows1 = len(cursor.fetchall())
    return render_template('dashboard.html', doc = rows, topic = rows1)

@app.route('/view')
def view():
  connect = connection.cursor()
  sql = "SELECT * FROM `documents` ORDER BY id DESC"
  connect.execute(sql)
  result = connect.fetchall()
  rows = len(result)
  _doc_ = []
  ssid = ""
  for x in xrange(len(result)):
    #_doc_type[x] = result[x]['doc_type'].encode('ascii', 'ignore')
    #_doc_[x] = result[x]['docs'].encode('ascii', 'ignore')
    _doc_.append({ 'id': str(result[x]['id']).encode('ascii', 'ignore'), 'topic': result[x]['topic'].encode('ascii', 'ignore'), 'doc_type': result[x]['doc_type'].encode('ascii', 'ignore'), 'doc' : result[x]['docs'].encode('ascii', 'ignore'), 'supervisor': result[x]['supervisor'].encode('ascii', 'ignore'), 'level': result[x]['level'].encode('ascii', 'ignore'), 'matric': result[x]['matric'].encode('ascii', 'ignore')})

  return render_template('view.html', rowcount = rows, doc=_doc_)

@app.route('/edit_url/<ID>', methods=['GET', 'POST'])
def edit_url(ID):
    cursor = connection.cursor()
    sql = "DELETE FROM `documents` WHERE id = %s"
    cursor.execute(sql, (ID))
    connection.commit()
    return "deleted"

@app.route('/add-topic', methods=['GET', 'POST'])
def add_topic():
    msg = ""
    if request.method == 'POST':
        topic = request.form['topic']
        supervisor = request.form['supervisor']
        platform = request.form['platform']
        session = request.form['session']
        level = request.form['level']
        matric = request.form['matric']
        phone = request.form['phone']

        cursor = connection.cursor()
        sql = "SELECT * FROM `topics` WHERE `topic` = %s"
        cursor.execute(sql, (topic))
        rowcount = int(len(cursor.fetchall()))
        if rowcount > 0:
            msg = "Record already exist"
        else:
            query = "INSERT INTO `topics`(`topic`, `student`, `supervisor`, `category`, `phone`, `session`, `level`) VALUES(%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (topic, matric, supervisor, platform, phone, session, level))
            connection.commit()
            msg = "Record Inserted Successfully"

    cursor = connection.cursor()
    query = "SELECT * FROM `topics` ORDER BY id DESC"
    cursor.execute(query)
    fetch = cursor.fetchall()
    data = []
    rows = len(fetch)
    for result in xrange(len(fetch)):
        data.append({ 'topic' : fetch[result]['topic'].encode('ascii', 'ignore'), 'matric' : fetch[result]['student'].encode('ascii', 'ignore'), 'supervisor' : fetch[result]['supervisor'].encode('ascii', 'ignore'), 'level': fetch[result]['level'], 'category' : fetch[result]['category'].encode('ascii', 'ignore'), 'phone': fetch[result]['phone'].encode('ascii','ignore'), 'session': fetch[result]['session'].encode('ascii', 'ignore'), 'id': str(fetch[result]['id']).encode('ascii', 'ignore')})
    #
    return render_template('add-topic.html', message = msg, record = data, rowcount = rows)

@app.route('/topic-search/<topic>', methods=['GET', 'POST'])
def search(topic):
    #dic = [{ 'topic': 'Hello', 'method': "POST"}, { 'topic': 'World', 'method': 'GET'}]
    q = topic.encode('ascii', 'ignore')
    cursor = connection.cursor()
    sql = "SELECT * FROM `topics` WHERE `topic` LIKE %s"
    cursor.execute(sql, ('%'+q+'%'))
    fetch = cursor.fetchall()
    rowcount = str(len(fetch))
    dic = []
    for x in xrange(len(fetch)):
         #dic.append({ 'topic': fetch[x]['topic'].encode('ascii', 'ignore')})
          d = collections.OrderedDict()
          d['id'] = int(fetch[x]['id'])
          d['topic'] = fetch[x]['topic']
          d['supervisor'] = fetch[x]['supervisor']
          d['category'] = fetch[x]['category']
          d['level'] = fetch[x]['level']
          d['phone'] = fetch[x]['phone']
          d['matric'] = fetch[x]['student']
          d['session'] = fetch[x]['session']
          dic.append(d)
    result = json.dumps(dic)
    return result

@app.route('/search-topic-id/<id>', methods=['GET', 'POST'])
def search_topic_id(id):

    q = id.encode('ascii', 'ignore')
    cursor = connection.cursor()
    sql = "SELECT * FROM `topics` WHERE `id` = %s"
    cursor.execute(sql, (q))
    fetch = cursor.fetchall()
    rowcount = str(len(fetch))
    dic = []
    for x in xrange(len(fetch)):
         #dic.append({ 'topic': fetch[x]['topic'].encode('ascii', 'ignore')})
          d = collections.OrderedDict()
          d['id'] = int(fetch[x]['id'])
          d['topic'] = fetch[x]['topic']
          d['supervisor'] = fetch[x]['supervisor']
          d['category'] = fetch[x]['category']
          d['level'] = fetch[x]['level']
          d['phone'] = fetch[x]['phone']
          d['matric'] = fetch[x]['student']
          d['session'] = fetch[x]['session']
          dic.append(d)
    result = json.dumps(dic)
    return result

@app.route('/remove-topic/<ID>', methods=['GET'])
def remove_topic(ID):

    if ID is not None:
        cursor = connection.cursor()
        sql = "DELETE FROM `topics` WHERE `id` = %s"
        cursor.execute(sql, (ID))
        connection.commit()
        msg = "deleted"
        return msg
    else:
        return "error"

@app.route('/view-data/<ID>', methods=['GET'])
def view_data(ID):
    fetchArray = []
    if ID is not None:
        cursor = connection.cursor()
        sql = "SELECT * FROM `documents` WHERE `id` = %s"
        cursor.execute(sql, (ID))
        fetch = cursor.fetchall()
        rowcount = len(fetch)
        msg = ""
        for x in xrange(len(fetch)):
            fetchArray.append({ 'docs' : fetch[x]['docs'].encode('ascii', 'ignore'), 'topic': fetch[x]['topic'].encode('ascii', 'ignore'), 'matric': fetch[x]['matric'].encode('ascii', 'ignore'), 'supervisor' : fetch[x]['supervisor'].encode('ascii', 'ignore'), 'level': fetch[x]['level'].encode('ascii', 'ignore'), 'type': fetch[x]['doc_type'].encode('ascii', 'ignore')})
    else:
        msg = "ID not found !"
    return render_template('view-data.html', data=fetchArray )

@app.route('/export', methods=['GET'])
def export():
    cursor = connection.cursor()
    sql = "SELECT * FROM `topics` GROUP BY session"
    cursor.execute(sql)
    fetch = cursor.fetchall()
    fetchArray = []
    for x in xrange(len(fetch)):
        fetchArray.append({'session': fetch[x]['session'].encode('ascii', 'ignore')})
    return render_template('export.html', data=fetchArray, length = str(len(fetch)) )

@app.route('/exporter/<ID>', methods=['GET'])
def exporter(ID):
    rowcount = 0
    dic = []
    split = ID.split('_')
    param = str(split[0])
    form2 = str(split[1])
    if request.method == 'GET':
        if param == 'session':
            cursor = connection.cursor()
            sql = "SELECT * FROM `topics` ORDER BY session DESC"
            cursor.execute(sql)
            fetch = cursor.fetchall()
            rowcount = len(fetch)
            if rowcount > 0:
                for x in xrange(len(fetch)):
                     d = collections.OrderedDict()
                     d['id'] = str(fetch[x]['id'])
                     d['topic'] = fetch[x]['topic'].lower().encode('ascii', 'ignore')
                     d['supervisor'] = fetch[x]['supervisor'].lower().encode('ascii', 'ignore')
                     d['category'] = fetch[x]['category'].lower().encode('ascii', 'ignore')
                     d['level'] = fetch[x]['level'].lower().encode('ascii', 'ignore')
                     d['phone'] = fetch[x]['phone'].lower().encode('ascii', 'ignore')
                     d['matric'] = fetch[x]['student'].lower().encode('ascii', 'ignore')
                     d['session'] = fetch[x]['session'].encode('ascii', 'ignore')
                     dic.append(d)
                result = json.dumps(dic)
        elif param == 'supervisor':
            cursor = connection.cursor()
            sql = "SELECT * FROM `topics` ORDER BY supervisor DESC"
            cursor.execute(sql)
            fetch = cursor.fetchall()
            rowcount = len(fetch)
            if rowcount > 0:
                for x in xrange(len(fetch)):
                     d = collections.OrderedDict()
                     d['id'] = str(fetch[x]['id'])
                     d['topic'] = fetch[x]['topic'].lower().encode('ascii', 'ignore')
                     d['supervisor'] = fetch[x]['supervisor'].lower().encode('ascii', 'ignore')
                     d['category'] = fetch[x]['category'].lower().encode('ascii', 'ignore')
                     d['level'] = fetch[x]['level'].lower().encode('ascii', 'ignore')
                     d['phone'] = fetch[x]['phone'].lower().encode('ascii', 'ignore')
                     d['matric'] = fetch[x]['student'].lower().encode('ascii', 'ignore')
                     d['session'] = fetch[x]['session'].encode('ascii', 'ignore')
                     dic.append(d)
                result = json.dumps(dic)
        elif param == 'platform':
            cursor = connection.cursor()
            sql = "SELECT * FROM `topics` ORDER BY category"
            cursor.execute(sql)
            fetch = cursor.fetchall()
            rowcount = len(fetch)
            if rowcount > 0:
                for x in xrange(len(fetch)):
                     d = collections.OrderedDict()
                     d['id'] = str(fetch[x]['id'])
                     d['topic'] = fetch[x]['topic'].lower().encode('ascii', 'ignore')
                     d['supervisor'] = fetch[x]['supervisor'].lower().encode('ascii', 'ignore')
                     d['category'] = fetch[x]['category'].lower().encode('ascii', 'ignore')
                     d['level'] = fetch[x]['level'].lower().encode('ascii', 'ignore')
                     d['phone'] = fetch[x]['phone'].lower().encode('ascii', 'ignore')
                     d['matric'] = fetch[x]['student'].lower().encode('ascii', 'ignore')
                     d['session'] = fetch[x]['session'].encode('ascii', 'ignore')
                     dic.append(d)
                result = json.dumps(dic)
        elif param == 'level':
            cursor = connection.cursor()
            sql = "SELECT * FROM `topics` ORDER BY level"
            cursor.execute(sql)
            fetch = cursor.fetchall()
            rowcount = len(fetch)
            if rowcount > 0:
                for x in xrange(len(fetch)):
                     d = collections.OrderedDict()
                     d['id'] = str(fetch[x]['id'])
                     d['topic'] = fetch[x]['topic'].lower().encode('ascii', 'ignore')
                     d['supervisor'] = fetch[x]['supervisor'].lower().encode('ascii', 'ignore')
                     d['category'] = fetch[x]['category'].lower().encode('ascii', 'ignore')
                     d['level'] = fetch[x]['level'].lower().encode('ascii', 'ignore')
                     d['phone'] = fetch[x]['phone'].lower().encode('ascii', 'ignore')
                     d['matric'] = fetch[x]['student'].lower().encode('ascii', 'ignore')
                     d['session'] = fetch[x]['session'].encode('ascii', 'ignore')
                     dic.append(d)
                result = json.dumps(dic)
            rowcount = 0
        return result

@app.route('/get-option/<opt>', methods=['GET'])
def get_option(opt):
    dic = []
    cursor = connection.cursor()
    sql = "SELECT * FROM `topics` GROUP BY " + opt
    cursor.execute(sql)
    fetch = cursor.fetchall()
    rowcount = len(fetch)
    if rowcount > 0:
        for x in xrange(len(fetch)):
             d = collections.OrderedDict()
             d['id'] = str(fetch[x]['id'])
             d['topic'] = fetch[x]['topic'].lower().encode('ascii', 'ignore')
             d['supervisor'] = fetch[x]['supervisor'].lower().encode('ascii', 'ignore')
             d['category'] = fetch[x]['category'].lower().encode('ascii', 'ignore')
             d['level'] = fetch[x]['level'].lower().encode('ascii', 'ignore')
             d['phone'] = fetch[x]['phone'].lower().encode('ascii', 'ignore')
             d['matric'] = fetch[x]['student'].lower().encode('ascii', 'ignore')
             d['session'] = fetch[x]['session'].encode('ascii', 'ignore')
             dic.append(d)
        result = json.dumps(dic)
    rowcount = 0
    return result

@app.route('/print', methods = ['GET','POST'])
def print_stuff():
    fetchArray = []
    lv = ''
    scss = ''
    cursor = connection.cursor()
    sql = ''
    if request.form['option'] != '0':
        if request.form['export'] != '0' and request.form['option'] != 'supervisor':
            select = request.form['selection'].encode('ascii', 'ignore')
            option = request.form['option'].encode('ascii', 'ignore')
            export = request.form['export'].encode('ascii', 'ignore')
            scss += select
            #lv += 'First Found'
            sql = 'SELECT * FROM `topics` WHERE session=%s AND ' + option + '=%s'
            cursor.execute(sql, (select, export))
        elif request.form['option'] == 'supervisor':
            select = request.form['selection'].encode('ascii', 'ignore')
            option = request.form['option'].encode('ascii', 'ignore')
            export = request.form['export'].encode('ascii', 'ignore')
            level  = request.form['level'].encode('ascii', 'ignore')
            scss += select
            #lv += 'Found Here'
            if level == 'ALL':
                sql = 'SELECT * FROM `topics` WHERE session=%s AND supervisor=%s ORDER BY level'
                cursor.execute(sql, (select, export))
            else:
                sql = 'SELECT * FROM `topics` WHERE session=%s AND supervisor=%s AND level=%s'
                cursor.execute(sql, (select, export, level))
        else:
            select = request.form['selection'].encode('ascii', 'ignore')
            option = request.form['option'].encode('ascii', 'ignore')
            scss += select
            sql = 'SELECT * FROM `topics` WHERE session=%s ORDER BY ' + option
            cursor.execute(sql, (select))
    elif request.form['option'] == '0':
        select = request.form['selection'].encode('ascii', 'ignore')
        scss += select
        sql = 'SELECT * FROM `topics` WHERE session=%s'
        cursor.execute(sql, (select))
    else:
        fetch = 0
    fetch = cursor.fetchall()
    rowcount = len(fetch)

    for x in xrange(len(fetch)):
        fetchArray.append({ 'topic': fetch[x]['topic'].encode('ascii', 'ignore'), 'student': fetch[x]['student'].encode('ascii', 'ignore'), 'supervisor' : fetch[x]['supervisor'].encode('ascii', 'ignore'), 'level': fetch[x]['level'].encode('ascii', 'ignore'), 'phone': fetch[x]['phone'].encode('ascii', 'ignore'),'category' : fetch[x]['category'].encode('ascii', 'ignore')})
    #return request.form['option'] +', ' + request.form['level']
    return render_template('print.html', row = rowcount, array=fetchArray, session= scss )


@app.route('/excel')
def excel_stuff():
    #format row-1 - [1,2], row-2 - [3, 4], ...
    fetchArray = []
    lv = ''
    scss = ''
    cursor = connection.cursor()
    sql = ''
    if request.form['option'] != '0':
        if request.form['export'] != '0' and request.form['option'] != 'supervisor':
            select = request.form['selection'].encode('ascii', 'ignore')
            option = request.form['option'].encode('ascii', 'ignore')
            export = request.form['export'].encode('ascii', 'ignore')
            scss += select
            #lv += 'First Found'
            sql = 'SELECT * FROM `topics` WHERE session=%s AND ' + option + '=%s'
            cursor.execute(sql, (select, export))
        elif request.form['option'] == 'supervisor':
            select = request.form['selection'].encode('ascii', 'ignore')
            option = request.form['option'].encode('ascii', 'ignore')
            export = request.form['export'].encode('ascii', 'ignore')
            level  = request.form['level'].encode('ascii', 'ignore')
            scss += select
            #lv += 'Found Here'
            if level == 'ALL':
                sql = 'SELECT * FROM `topics` WHERE session=%s AND supervisor=%s ORDER BY level'
                cursor.execute(sql, (select, export))
            else:
                sql = 'SELECT * FROM `topics` WHERE session=%s AND supervisor=%s AND level=%s'
                cursor.execute(sql, (select, export, level))
        else:
            select = request.form['selection'].encode('ascii', 'ignore')
            option = request.form['option'].encode('ascii', 'ignore')
            scss += select
            sql = 'SELECT * FROM `topics` WHERE session=%s ORDER BY ' + option
            cursor.execute(sql, (select))
    elif request.form['option'] == '0':
        select = request.form['selection'].encode('ascii', 'ignore')
        scss += select
        sql = 'SELECT * FROM `topics` WHERE session=%s'
        cursor.execute(sql, (select))
    else:
        fetch = 0
    fetch = cursor.fetchall()
    rowcount = len(fetch)
    for x in xrange(len(fetch)):
        fetchArray.append({ 'topic': fetch[x]['topic'].encode('ascii', 'ignore'), 'student': fetch[x]['student'].encode('ascii', 'ignore'), 'supervisor' : fetch[x]['supervisor'].encode('ascii', 'ignore'), 'level': fetch[x]['level'].encode('ascii', 'ignore'), 'phone': fetch[x]['phone'].encode('ascii', 'ignore'),'category' : fetch[x]['category'].encode('ascii', 'ignore')})
    #return excel.make_response_from_array([fetchArray], "csv", file_name="export_data")
    return fetchArray

@app.route('/sign-out')
def signout():
    session.pop('adminkey', None)
    return redirect(url_for('login'))

@app.errorhandler(500)
def internal_error(error):
  return "500 error"

@app.errorhandler(404)
def not_found(error):
  return "404 error",404

if __name__== "__main__":
    app.run(debug=True)
