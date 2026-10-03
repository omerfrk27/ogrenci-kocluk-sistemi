import sqlite3, os, json
from flask import Flask, request, redirect, session, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, timedelta

app=Flask(__name__); app.secret_key=os.environ.get('SECRET_KEY','degistir-beni')
DB=os.path.join(os.path.dirname(__file__),'kocluk.db')
LEVELS=['5. Sınıf','6. Sınıf','7. Sınıf','8. Sınıf / LGS','9. Sınıf','10. Sınıf','11. Sınıf','12. Sınıf / YKS','Mezun / YKS']
COURSES={
'5. Sınıf':['Türkçe','Matematik','Fen Bilimleri','Sosyal Bilgiler','İngilizce','Din Kültürü'],
'6. Sınıf':['Türkçe','Matematik','Fen Bilimleri','Sosyal Bilgiler','İngilizce','Din Kültürü'],
'7. Sınıf':['Türkçe','Matematik','Fen Bilimleri','Sosyal Bilgiler','İngilizce','Din Kültürü'],
'8. Sınıf / LGS':['Türkçe','Matematik','Fen Bilimleri','T.C. İnkılap Tarihi','İngilizce','Din Kültürü'],
'9. Sınıf':['Türk Dili ve Edebiyatı','Matematik','Fizik','Kimya','Biyoloji','Tarih','Coğrafya','İngilizce'],
'10. Sınıf':['Türk Dili ve Edebiyatı','Matematik','Fizik','Kimya','Biyoloji','Tarih','Coğrafya','İngilizce'],
'11. Sınıf':['Türk Dili ve Edebiyatı','Matematik','Fizik','Kimya','Biyoloji','Tarih','Coğrafya','İngilizce'],
'12. Sınıf / YKS':['TYT Türkçe','TYT Matematik','TYT Sosyal','TYT Fen','AYT Matematik','AYT Fizik','AYT Kimya','AYT Biyoloji','AYT Edebiyat','AYT Tarih','AYT Coğrafya'],
'Mezun / YKS':['TYT Türkçe','TYT Matematik','TYT Sosyal','TYT Fen','AYT Matematik','AYT Fizik','AYT Kimya','AYT Biyoloji','AYT Edebiyat','AYT Tarih','AYT Coğrafya']}
TOPICS={
'Matematik':['Doğal Sayılar','Kesirler','Ondalık Gösterim','Oran-Orantı','Cebirsel İfadeler','Denklemler','Geometri','Veri ve Olasılık'],
'Türkçe':['Sözcükte Anlam','Cümlede Anlam','Paragraf','Dil Bilgisi','Yazım Kuralları','Noktalama'],
'Fen Bilimleri':['Dünya ve Evren','Canlılar ve Yaşam','Fiziksel Olaylar','Madde ve Doğası','Enerji'],
'TYT Matematik':['Temel Kavramlar','Sayı Basamakları','Bölme-Bölünebilme','Rasyonel Sayılar','Üslü Sayılar','Köklü Sayılar','Denklemler','Problemler','Kümeler','Fonksiyonlar','Geometri'],
'AYT Matematik':['Fonksiyonlar','Polinomlar','2. Dereceden Denklemler','Trigonometri','Logaritma','Diziler','Limit','Türev','İntegral','Analitik Geometri'],
'TYT Türkçe':['Sözcükte Anlam','Cümlede Anlam','Paragraf','Dil Bilgisi','Yazım-Noktalama'],
'AYT Fizik':['Vektörler','Kuvvet-Hareket','Enerji','Elektrik-Manyetizma','Dalgalar','Modern Fizik'],
'AYT Kimya':['Modern Atom','Gazlar','Çözeltiler','Tepkimelerde Enerji','Denge','Organik Kimya'],
'AYT Biyoloji':['Sinir Sistemi','Endokrin Sistem','Duyu Organları','Destek-Hareket','Sindirim','Dolaşım','Solunum','Üreme','Genetik','Ekoloji']}
EXAMS={
'5. Sınıf':['Genel Deneme','Branş Denemesi','Okul Sınavı'],'6. Sınıf':['Genel Deneme','Branş Denemesi','Okul Sınavı'],'7. Sınıf':['Genel Deneme','Branş Denemesi','Okul Sınavı'],
'8. Sınıf / LGS':['LGS','LGS Branş'],'9. Sınıf':['Genel Deneme','Branş Denemesi','Okul Sınavı'],'10. Sınıf':['Genel Deneme','Branş Denemesi','Okul Sınavı'],'11. Sınıf':['Genel Deneme','Branş Denemesi','TYT Denemesi','Okul Sınavı'],
'12. Sınıf / YKS':['TYT','AYT','Branş Denemesi'],'Mezun / YKS':['TYT','AYT','Branş Denemesi']}
EXAM_LESSONS={'TYT':['Türkçe','Matematik','Sosyal','Fen'],'TYT Denemesi':['Türkçe','Matematik','Sosyal','Fen'],'AYT':['Matematik','Fizik','Kimya','Biyoloji'],'LGS':['Türkçe','Matematik','Fen','İnkılap','Din Kültürü','İngilizce']}

def db():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c

def init():
 c=db(); q=c.cursor(); q.executescript('''
 CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,name TEXT,username TEXT UNIQUE,password TEXT,role TEXT,level TEXT);
 CREATE TABLE IF NOT EXISTS study(id INTEGER PRIMARY KEY,user_id INTEGER,d TEXT,exam_type TEXT,lesson TEXT,topic TEXT,correct_n INTEGER,wrong_n INTEGER,blank_n INTEGER,minutes INTEGER DEFAULT 0,note TEXT);
 CREATE TABLE IF NOT EXISTS goals(id INTEGER PRIMARY KEY,user_id INTEGER,week_start TEXT,question_goal INTEGER DEFAULT 0,minute_goal INTEGER DEFAULT 0);
 CREATE TABLE IF NOT EXISTS exam_sessions(id INTEGER PRIMARY KEY,user_id INTEGER,d TEXT,exam_type TEXT,title TEXT);
 CREATE TABLE IF NOT EXISTS exam_results(id INTEGER PRIMARY KEY,session_id INTEGER,lesson TEXT,correct_n INTEGER,wrong_n INTEGER,blank_n INTEGER);
 ''')
 if not q.execute("SELECT 1 FROM users WHERE username='koc'").fetchone(): q.execute('INSERT INTO users(name,username,password,role,level) VALUES(?,?,?,?,?)',('Koç','koc',generate_password_hash('123456'),'coach',''))
 if not q.execute("SELECT 1 FROM users WHERE username='ogrenci'").fetchone(): q.execute('INSERT INTO users(name,username,password,role,level) VALUES(?,?,?,?,?)',('Demo Öğrenci','ogrenci',generate_password_hash('123456'),'student','7. Sınıf'))
 c.commit(); c.close()
init()

def net(d,y): return round((d or 0)-(y or 0)/4,2)
def ws():
 t=date.today(); return (t-timedelta(days=t.weekday())).isoformat()
def pct(a,b): return round(a/b*100,1) if b else 0
CSS='''<style>*{box-sizing:border-box}body{margin:0;font-family:Arial,sans-serif;background:#f4f7fb;color:#172033}.nav{background:#172033;color:#fff;padding:15px 4%;display:flex;justify-content:space-between}.nav a{color:#fff;text-decoration:none;margin-left:14px}.wrap{max-width:1200px;margin:24px auto;padding:0 16px}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:14px}.card{background:#fff;border-radius:14px;padding:18px;box-shadow:0 2px 12px #0001;margin-bottom:14px}.big{font-size:28px;font-weight:700;margin:8px 0}.green{color:#13875b}.red{color:#c43c3c}.amber{color:#a66a00}.btn,button{background:#172033;color:#fff;border:0;padding:10px 15px;border-radius:8px;text-decoration:none;display:inline-block;margin:2px}input,select,textarea{width:100%;padding:10px;border:1px solid #ccd3df;border-radius:8px;margin:5px 0 12px}.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}table{width:100%;border-collapse:collapse;background:#fff}th,td{padding:10px;border-bottom:1px solid #eee;text-align:left}th{background:#eef2f8}.alert{padding:12px;background:#fff3cd;border-radius:9px;margin:8px 0}.bar{height:10px;background:#e9edf4;border-radius:9px;overflow:hidden}.bar span{display:block;height:100%;background:#172033}@media(max-width:700px){.grid{grid-template-columns:1fr}table{font-size:12px}}</style>'''
def shell(t,b):
 nav='' if not session.get('uid') else '<div class="nav"><b>Öğrenci Koçluk Sistemi</b><div><a href="/">Panel</a><a href="/logout">Çıkış</a></div></div>'
 return render_template_string(f'<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{t}</title>{CSS}</head><body>{nav}<div class="wrap">{b}</div></body></html>')

def user(uid):
 c=db(); u=c.execute('SELECT * FROM users WHERE id=?',(uid,)).fetchone(); c.close(); return u

@app.route('/login',methods=['GET','POST'])
def login():
 err=''
 if request.method=='POST':
  c=db(); u=c.execute('SELECT * FROM users WHERE username=?',(request.form['username'],)).fetchone(); c.close()
  if u and check_password_hash(u['password'],request.form['password']): session.update(uid=u['id'],role=u['role'],name=u['name']); return redirect('/')
  err='<p class="red">Kullanıcı adı veya şifre hatalı.</p>'
 return shell('Giriş',f'<div class="card" style="max-width:420px;margin:70px auto"><h2>Giriş</h2>{err}<form method="post"><input name="username" placeholder="Kullanıcı adı" required><input type="password" name="password" placeholder="Şifre" required><button>Giriş Yap</button></form><small>Koç: koc / 123456 &nbsp; Demo: ogrenci / 123456</small></div>')
@app.route('/logout')
def logout(): session.clear(); return redirect('/login')
@app.route('/')
def home():
 if not session.get('uid'): return redirect('/login')
 return coach_home() if session['role']=='coach' else student_home()

def student_home():
 u=user(session['uid']); c=db(); rows=c.execute('SELECT * FROM study WHERE user_id=? AND d>=? ORDER BY d DESC,id DESC',(u['id'],ws())).fetchall(); g=c.execute('SELECT * FROM goals WHERE user_id=? AND week_start=?',(u['id'],ws())).fetchone(); es=c.execute('SELECT * FROM exam_sessions WHERE user_id=? ORDER BY d DESC,id DESC LIMIT 5',(u['id'],)).fetchall(); c.close()
 q=sum(r['correct_n']+r['wrong_n']+r['blank_n'] for r in rows); co=sum(r['correct_n'] for r in rows); mins=sum(r['minutes'] for r in rows); qp=pct(q,g['question_goal']) if g else 0; mp=pct(mins,g['minute_goal']) if g else 0
 body=f'<h1>{u["name"]}</h1><p><b>{u["level"]}</b></p><div class="cards"><div class="card">Bu hafta soru<div class="big">{q}</div></div><div class="card">Başarı<div class="big green">%{pct(co,q)}</div></div><div class="card">Çalışma<div class="big">{mins} dk</div></div><div class="card">Deneme<div class="big">{len(es)}</div></div></div>'
 if g: body+=f'<div class="card"><b>Haftalık soru hedefi: %{min(qp,999)}</b><div class="bar"><span style="width:{min(qp,100)}%"></span></div><br><b>Çalışma süresi hedefi: %{min(mp,999)}</b><div class="bar"><span style="width:{min(mp,100)}%"></span></div></div>'
 body+='<p><a class="btn" href="/study/add">+ Çalışma Gir</a><a class="btn" href="/exam/add">+ Deneme Gir</a><a class="btn" href="/goals">🎯 Hedefler</a><a class="btn" href="/reviews">🔁 48 Saat</a><a class="btn" href="/analysis/'+str(u['id'])+'">📈 Analiz</a></p><h2>Bu Haftaki Çalışmalar</h2><table><tr><th>Tarih</th><th>Ders</th><th>Konu</th><th>D</th><th>Y</th><th>B</th><th>%</th></tr>'
 for r in rows:
  total=r['correct_n']+r['wrong_n']+r['blank_n']; body+=f'<tr><td>{r["d"]}</td><td>{r["lesson"]}</td><td>{r["topic"]}</td><td>{r["correct_n"]}</td><td>{r["wrong_n"]}</td><td>{r["blank_n"]}</td><td>%{pct(r["correct_n"],total)}</td></tr>'
 return shell('Öğrenci Paneli',body+'</table>')

def coach_home():
 c=db(); ss=c.execute("SELECT * FROM users WHERE role='student' ORDER BY name").fetchall(); cards=''; alerts=''
 for s in ss:
  rows=c.execute('SELECT * FROM study WHERE user_id=? AND d>=?',(s['id'],ws())).fetchall(); q=sum(r['correct_n']+r['wrong_n']+r['blank_n'] for r in rows); co=sum(r['correct_n'] for r in rows); ac=pct(co,q); last=max([r['d'] for r in rows],default='-'); status='🟢 İyi' if q>=300 and ac>=70 else ('🟡 Takip' if q else '🔴 Giriş yok')
  if not q: alerts+=f'<div class="alert"><b>{s["name"]}</b> ({s["level"]}): Bu hafta veri girişi yok.</div>'
  cards+=f'<div class="card"><h3>{s["name"]}</h3><p>{s["level"]}</p><p>{status}</p><div class="big">{q} soru</div><p>Başarı %{ac} · Son giriş {last}</p><a class="btn" href="/student/{s["id"]}">İncele</a></div>'
 c.close(); return shell('Koç Paneli',f'<h1>Koç Kontrol Merkezi</h1><p><a class="btn" href="/student/add">+ Öğrenci Ekle</a></p><h2>Bugün Bakılması Gerekenler</h2>{alerts or "<div class=\"alert\">Kritik uyarı yok.</div>"}<h2>Tüm Öğrenciler</h2><div class="cards">{cards}</div>')

@app.route('/student/add',methods=['GET','POST'])
def student_add():
 if session.get('role')!='coach': return redirect('/')
 err=''
 if request.method=='POST':
  try:
   c=db(); c.execute('INSERT INTO users(name,username,password,role,level) VALUES(?,?,?,?,?)',(request.form['name'],request.form['username'],generate_password_hash(request.form['password']),'student',request.form['level'])); c.commit(); c.close(); return redirect('/')
  except sqlite3.IntegrityError: err='<p class="red">Bu kullanıcı adı kullanılıyor.</p>'
 opts=''.join(f'<option>{x}</option>' for x in LEVELS)
 return shell('Öğrenci Ekle',f'<h1>Yeni Öğrenci</h1>{err}<div class="card"><form method="post"><label>Ad Soyad</label><input name="name" required><label>Kullanıcı adı</label><input name="username" required><label>Şifre</label><input name="password" required><label>Sınıf / Sınav Grubu</label><select name="level">{opts}</select><button>Öğrenci Oluştur</button></form></div>')

@app.route('/api/topics')
def api_topics():
 lesson=request.args.get('lesson',''); return json.dumps(TOPICS.get(lesson,['1. Ünite / Konu','2. Ünite / Konu','3. Ünite / Konu']),ensure_ascii=False)

@app.route('/study/add',methods=['GET','POST'])
def study_add():
 if session.get('role') not in ['student','coach']: return redirect('/')
 u=user(session['uid']); lessons=COURSES.get(u['level'],[])
 if request.method=='POST':
  c=db(); c.execute('INSERT INTO study(user_id,d,exam_type,lesson,topic,correct_n,wrong_n,blank_n,minutes,note) VALUES(?,?,?,?,?,?,?,?,?,?)',(u['id'],request.form['d'],u['level'],request.form['lesson'],request.form['topic'],int(request.form['correct_n']),int(request.form['wrong_n']),int(request.form['blank_n']),int(request.form.get('minutes') or 0),request.form.get('note',''))); c.commit(); c.close(); return redirect('/')
 lesson_opts=''.join(f'<option>{x}</option>' for x in lessons); initial=TOPICS.get(lessons[0] if lessons else '',['1. Ünite / Konu']); topic_opts=''.join(f'<option>{x}</option>' for x in initial)
 js='''<script>async function topics(){let l=document.getElementById('lesson').value;let a=await fetch('/api/topics?lesson='+encodeURIComponent(l)).then(r=>r.json());document.getElementById('topic').innerHTML=a.map(x=>`<option>${x}</option>`).join('')}</script>'''
 return shell('Çalışma Girişi',f'<h1>Günlük Çalışma — {u["level"]}</h1><div class="card"><form method="post"><div class="grid"><div><label>Tarih</label><input type="date" name="d" value="{date.today()}" required></div><div><label>Ders</label><select id="lesson" name="lesson" onchange="topics()">{lesson_opts}</select></div><div><label>Konu</label><select id="topic" name="topic">{topic_opts}</select></div><div><label>Süre (dk)</label><input type="number" min="0" name="minutes" value="0"></div><div><label>Doğru</label><input type="number" min="0" name="correct_n" value="0" required></div><div><label>Yanlış</label><input type="number" min="0" name="wrong_n" value="0" required></div><div><label>Boş</label><input type="number" min="0" name="blank_n" value="0" required></div></div><label>Not</label><textarea name="note"></textarea><button>Kaydet</button></form></div>{js}')

def exam_lessons(level,et):
 if et in EXAM_LESSONS:return EXAM_LESSONS[et]
 if et=='LGS Branş' or et=='Branş Denemesi': return COURSES.get(level,[])
 return COURSES.get(level,[])
@app.route('/exam/add',methods=['GET','POST'])
def exam_add():
 if session.get('role')!='student': return redirect('/')
 u=user(session['uid']); types=EXAMS.get(u['level'],['Genel Deneme']); et=request.args.get('type') or request.form.get('exam_type') or types[0]; lessons=exam_lessons(u['level'],et)
 if request.method=='POST':
  c=db(); cur=c.execute('INSERT INTO exam_sessions(user_id,d,exam_type,title) VALUES(?,?,?,?)',(u['id'],request.form['d'],et,request.form['title'])); sid=cur.lastrowid
  for i,l in enumerate(lessons): c.execute('INSERT INTO exam_results(session_id,lesson,correct_n,wrong_n,blank_n) VALUES(?,?,?,?,?)',(sid,l,int(request.form.get(f'd{i}') or 0),int(request.form.get(f'y{i}') or 0),int(request.form.get(f'b{i}') or 0)))
  c.commit(); c.close(); return redirect('/')
 links=' '.join(f'<a class="btn" href="/exam/add?type={x}">{x}</a>' for x in types); fields=''
 for i,l in enumerate(lessons): fields+=f'<div class="card"><h3>{l}</h3><div class="grid"><div><label>D</label><input type="number" min="0" name="d{i}" value="0"></div><div><label>Y</label><input type="number" min="0" name="y{i}" value="0"></div><div><label>B</label><input type="number" min="0" name="b{i}" value="0"></div></div></div>'
 return shell('Deneme Girişi',f'<h1>{u["level"]} — {et}</h1><p>{links}</p><form method="post"><input type="hidden" name="exam_type" value="{et}"><div class="card"><label>Tarih</label><input type="date" name="d" value="{date.today()}" required><label>Deneme adı</label><input name="title" required></div>{fields}<button>Denemeyi Kaydet</button></form>')

@app.route('/goals',methods=['GET','POST'])
def goals():
 if session.get('role')!='student': return redirect('/')
 c=db(); old=c.execute('SELECT * FROM goals WHERE user_id=? AND week_start=?',(session['uid'],ws())).fetchone()
 if request.method=='POST':
  vals=(int(request.form.get('question_goal') or 0),int(request.form.get('minute_goal') or 0))
  if old:c.execute('UPDATE goals SET question_goal=?,minute_goal=? WHERE id=?',(*vals,old['id']))
  else:c.execute('INSERT INTO goals(user_id,week_start,question_goal,minute_goal) VALUES(?,?,?,?)',(session['uid'],ws(),*vals))
  c.commit(); c.close(); return redirect('/')
 c.close(); return shell('Hedefler',f'<h1>Haftalık Hedef</h1><div class="card"><form method="post"><label>Soru hedefi</label><input type="number" name="question_goal" value="{old["question_goal"] if old else 0}"><label>Çalışma süresi hedefi (dk)</label><input type="number" name="minute_goal" value="{old["minute_goal"] if old else 0}"><button>Kaydet</button></form></div>')
@app.route('/reviews')
def reviews():
 if session.get('role')!='student':return redirect('/')
 c=db(); rows=c.execute('SELECT * FROM study WHERE user_id=? AND wrong_n>0 ORDER BY d DESC',(session['uid'],)).fetchall(); c.close(); tr=''
 for r in rows:
  due=(date.fromisoformat(r['d'])+timedelta(days=2)).isoformat(); tr+=f'<tr><td>{due}</td><td>{r["lesson"]}</td><td>{r["topic"]}</td><td>{r["wrong_n"]}</td><td>{"🔴 Tekrar zamanı" if due<=date.today().isoformat() else "Bekliyor"}</td></tr>'
 return shell('48 Saat',f'<h1>48 Saat Yanlış Tekrarı</h1><table><tr><th>Tarih</th><th>Ders</th><th>Konu</th><th>Yanlış</th><th>Durum</th></tr>{tr}</table>')

@app.route('/student/<int:uid>')
def detail(uid):
 if session.get('role') not in ('coach','student'): return redirect('/')
 s=user(uid); c=db(); rows=c.execute('SELECT * FROM study WHERE user_id=? ORDER BY d DESC,id DESC LIMIT 200',(uid,)).fetchall(); c.close(); agg={}
 for r in rows:
  k=(r['lesson'],r['topic']); v=agg.setdefault(k,[0,0,0]); v[0]+=r['correct_n'];v[1]+=r['wrong_n'];v[2]+=r['blank_n']
 tr=''.join(f'<tr><td>{k[0]}</td><td>{k[1]}</td><td>{v[0]}</td><td>{v[1]}</td><td>{v[2]}</td><td>%{pct(v[0],sum(v))}</td></tr>' for k,v in agg.items())
 return shell(s['name'],f'<h1>{s["name"]} — {s["level"]}</h1><p><a class="btn" href="/analysis/{uid}">📈 Deneme Analizi</a><a class="btn" href="/report/{uid}">📄 Veli Raporu</a></p><h2>Konu Performansı</h2><table><tr><th>Ders</th><th>Konu</th><th>D</th><th>Y</th><th>B</th><th>Başarı</th></tr>{tr}</table>')
@app.route('/analysis/<int:uid>')
def analysis(uid):
 if session.get('role')!='coach' and session.get('uid')!=uid:return redirect('/')
 s=user(uid); c=db(); sessions=c.execute('SELECT * FROM exam_sessions WHERE user_id=? ORDER BY d,id',(uid,)).fetchall(); data=[]
 for x in sessions:
  rs=c.execute('SELECT * FROM exam_results WHERE session_id=?',(x['id'],)).fetchall(); data.append((x,round(sum(net(r['correct_n'],r['wrong_n']) for r in rs),2),rs))
 c.close(); vals=[x[1] for x in data]; mx=max(vals,default=1) or 1; bars=''.join(f'<div title="{v} net" style="width:34px;height:{max(5,int(v/mx*160))}px;background:#172033;border-radius:6px 6px 0 0"></div>' for v in vals[-12:]); tr=''.join(f'<tr><td>{x[0]["d"]}</td><td>{x[0]["exam_type"]}</td><td>{x[0]["title"]}</td><td><b>{x[1]}</b></td></tr>' for x in reversed(data))
 return shell('Analiz',f'<h1>{s["name"]} — Deneme Analizi</h1><div class="cards"><div class="card">Son Net<div class="big">{vals[-1] if vals else "-"}</div></div><div class="card">Değişim<div class="big">{round(vals[-1]-vals[-2],2) if len(vals)>1 else 0:+}</div></div><div class="card">Deneme<div class="big">{len(vals)}</div></div></div><div class="card"><div style="height:190px;display:flex;align-items:end;gap:10px">{bars or "Henüz deneme yok."}</div></div><table><tr><th>Tarih</th><th>Tür</th><th>Ad</th><th>Net</th></tr>{tr}</table>')
@app.route('/report/<int:uid>')
def report(uid):
 if session.get('role')!='coach':return redirect('/')
 s=user(uid); c=db(); rows=c.execute('SELECT * FROM study WHERE user_id=? AND d>=?',(uid,ws())).fetchall(); es=c.execute('SELECT * FROM exam_sessions WHERE user_id=? AND d>=? ORDER BY d DESC',(uid,ws())).fetchall(); c.close(); q=sum(r['correct_n']+r['wrong_n']+r['blank_n'] for r in rows); co=sum(r['correct_n'] for r in rows); wr=sum(r['wrong_n'] for r in rows); bl=sum(r['blank_n'] for r in rows); mins=sum(r['minutes'] for r in rows)
 return shell('Veli Raporu',f'<h1>Haftalık Öğrenci Gelişim Raporu</h1><div class="card"><h2>{s["name"]}</h2><p>{s["level"]} · Hafta: {ws()}</p><div class="cards"><div>Toplam Soru<div class="big">{q}</div></div><div>Doğru<div class="big green">{co}</div></div><div>Yanlış<div class="big red">{wr}</div></div><div>Boş<div class="big">{bl}</div></div><div>Başarı<div class="big">%{pct(co,q)}</div></div><div>Çalışma<div class="big">{mins} dk</div></div></div><h3>Koç Değerlendirmesi</h3><p>{"Düzenli çalışma verisi mevcut. Haftalık başarı oranı %"+str(pct(co,q))+"." if q else "Bu hafta yeterli çalışma verisi girilmemiştir."}</p><p>Bu hafta girilen deneme sayısı: <b>{len(es)}</b></p></div>')

if __name__=='__main__': app.run(host='0.0.0.0',port=5000,debug=True)
