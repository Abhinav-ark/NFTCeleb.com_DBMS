from flask import Flask, render_template, request, redirect, url_for, session,flash
from flask_mysqldb import MySQL
from werkzeug.utils import redirect
import MySQLdb.cursors
import re


app = Flask(__name__)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'sql003'
app.config['MYSQL_DB'] = 'mydb'


mysql = MySQL(app)
app.secret_key = 'seckey'

@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
	msg = ''
	if request.method == 'POST' and 'userid' in request.form and 'password' in request.form:
		userid = request.form['userid']
		password = request.form['password']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM accounts WHERE userid = % s AND password = % s', (userid, password, ))
		account = cursor.fetchone()
		if account:
			session['loggedin'] = True
			session['userid'] = account['userid']
			msg = 'Logged in successfully !'
			print(msg)
			# cur = mysql.connection.cursor()
			# cur.execute("SELECT collection_id, collection_name, cryptocurrency, description from collection;")
			# data = cur.fetchall()
			# cur.close()
			# return render_template('Manage_collections.html', msg = msg)
			cur=mysql.connection.cursor()
			cur.execute(f"SELECT * from collection where creator_id='{session['userid']}'")
			data=cur.fetchall()
			if data:
				global curr_user 
				curr_user = session['userid']
				return redirect(url_for('Index'))
			else:
				return redirect(url_for('nft'))
		else:
			msg = 'Incorrect user id or password !'
	return render_template('login.html', msg = msg)
@app.route('/nft')
def nft():
	return render_template('nft_h.html')

@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('userid', None)
	return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
	msg = ''
	if request.method == 'POST' and 'userid' in request.form and 'password' in request.form and 'email' in request.form :
		userid = request.form['userid']
		password = request.form['password']
		email = request.form['email']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM accounts WHERE userid = % s', (userid, ))
		account = cursor.fetchone()
		if account:
			msg = 'Account already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', userid):
			msg = 'user id must contain only characters and numbers !'
		elif not userid or not password or not email:
			msg = 'Please fill out the form !'
		else:
			cursor.execute('INSERT INTO accounts VALUES (% s, % s, % s)', (userid, password, email, ))
			mysql.connection.commit()
			msg = 'You have successfully registered !'
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('register.html', msg = msg)

@app.route('/mc')
def Index():
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT collection_id, collection_name, cryptocurrency, description from collection where creator_id='{curr_user}' ;")
    data = cur.fetchall()
    cur.close()
    return render_template('Manage_collections.html', data=data)
global scol
scol =0
@app.route('/sortcolid')
def sortcolid():
	cur = mysql.connection.cursor()
	global scol
	scol=(scol+1)%2
	if scol==1:
		cur.execute(f"SELECT collection_id, collection_name, cryptocurrency, description from collection where creator_id='{curr_user}' order by collection_id;")
	else:
		cur.execute(f"SELECT collection_id, collection_name, cryptocurrency, description from collection where creator_id='{curr_user}' order by collection_id DESC;")
	data = cur.fetchall()
	cur.close()
	return render_template('Manage_collections.html', data=data)

global scolname
scolname =0
@app.route('/sortcolname')
def sortcolname():
	cur = mysql.connection.cursor()
	global scolname
	scolname=(scolname+1)%2
	if scolname==1:
		cur.execute(f"SELECT collection_id, collection_name, cryptocurrency, description from collection where creator_id='{curr_user}' order by collection_name;")
	else:
		cur.execute(f"SELECT collection_id, collection_name, cryptocurrency, description from collection where creator_id='{curr_user}' order by collection_name DESC;")
	data = cur.fetchall()
	cur.close()
	return render_template('Manage_collections.html', data=data)

global scrypto
scrypto =0
@app.route('/sortcrypto')
def sortcrypto():
	cur = mysql.connection.cursor()
	global scrypto
	scrypto=(scrypto+1)%2
	if scrypto==1:
		cur.execute(f"SELECT collection_id, collection_name, cryptocurrency, description from collection where creator_id='{curr_user}' order by cryptocurrency;")
	else:
		cur.execute(f"SELECT collection_id, collection_name, cryptocurrency, description from collection where creator_id='{curr_user}' order by cryptocurrency DESC;")
	data = cur.fetchall()
	cur.close()
	return render_template('Manage_collections.html', data=data)

user_id='abhi'

@app.route('/mc/insert', methods = ['POST'])
def insert():
    if request.method == "POST":
        flash("Data Inserted Successfully")
        Collection_id = request.form['Collection_id']
        Collection_name = request.form['Collection_name']
        Cryptocurrency = request.form['Cryptocurrency']
        Description = request.form['Description']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO collection (Collection_id,Collection_name,Creator_id,Cryptocurrency,Description) VALUES (%s, %s, %s, %s, %s);", (Collection_id,Collection_name,curr_user,Cryptocurrency,Description))
        mysql.connection.commit()
        return redirect(url_for('Index'))

@app.route('/mc/searchcollection', methods = ['POST'])
def searchcollection():
	if request.method == "POST":
		searchfor = request.form['searchfor']
		cur = mysql.connection.cursor()
		cur.execute(f"SELECT collection_id, collection_name, cryptocurrency, description from collection where (creator_id='{curr_user}' and  collection_id='{searchfor}') or (creator_id='{curr_user}' and collection_name like '%{searchfor}%') or (creator_id='{curr_user}' and cryptocurrency='{searchfor}') ;")
		data = cur.fetchall()
		cur.close()
		return render_template('Manage_collections.html', data=data)

@app.route('/mc/searchnft', methods = ['POST'])
def searchnft():
	if request.method == "POST":
		searchfor = request.form['searchfor']
		cur = mysql.connection.cursor()
		cur.execute(f"SELECT NFT_id, NFT_name, image_url, NFT_type, price, token_standard, description from nft where (collection_id='{curr_collection}' and NFT_id='{searchfor}') or (collection_id='{curr_collection}' and NFT_name like '%{searchfor}%') or (collection_id='{curr_collection}' and NFT_type='{searchfor}') or (collection_id='{curr_collection}' and token_standard like '%{searchfor}%');")
		data = cur.fetchall()
		cur.close()
		return render_template('Manage_nfts.html', data=data)

@app.route('/delete/<string:id_data>', methods = ['GET'])
def delete(id_data):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute(f"DELETE FROM collection WHERE Collection_id={id_data};")
    mysql.connection.commit()
    return redirect(url_for('Index'))



@app.route('/mc/update', methods= ['POST', 'GET'])
def update():
    if request.method == 'POST':
        Collection_id = request.form['Collection_id']
        Collection_name = request.form['Collection_name']
        Cryptocurrency = request.form['Cryptocurrency']
        Description = request.form['Description']

        cur = mysql.connection.cursor()
        print(Collection_name, Cryptocurrency, Description, Collection_id )
        print(f"""UPDATE collection SET Collection_name='{Collection_name}', Cryptocurrency='{Cryptocurrency}', Description='{Description}' WHERE Collection_id={Collection_id};""")
        cur.execute(f"""UPDATE collection SET Collection_name='{Collection_name}', Cryptocurrency='{Cryptocurrency}', Description='{Description}' WHERE Collection_id={Collection_id};""")
        mysql.connection.commit()
        flash("Data Updated Successfully")
        return redirect(url_for('Index'))
global curr_collection
@app.route('/view/<string:id_data>',methods=['GET'])
def view(id_data):
	global curr_collection
	curr_collection=id_data
	cur = mysql.connection.cursor()
	cur.execute(f"SELECT NFT_id, NFT_name, image_url, NFT_type, price, token_standard, description from nft where collection_id='{id_data}' ;")
	data = cur.fetchall()
	cur.close()
	return render_template('Manage_nfts.html', data=data)

global snftid
snftid=0
@app.route('/sortnftid')
def sortnftid():
	cur = mysql.connection.cursor()
	global snftid
	snftid=(snftid+1)%2
	global curr_collection
	if snftid==1:
		cur.execute(f"SELECT NFT_id, NFT_name, image_url, NFT_type, price, token_standard, description from nft where collection_id='{curr_collection}' order by nft_id;")
	else:
		cur.execute(f"SELECT NFT_id, NFT_name, image_url, NFT_type, price, token_standard, description from nft where collection_id='{curr_collection}' order by nft_id desc;")
	data = cur.fetchall()
	cur.close()
	return render_template('Manage_nfts.html', data=data)

global snftname
snftname=0
@app.route('/sortnftname')
def sortnftname():
	cur = mysql.connection.cursor()
	global snftname
	global curr_collection
	snftname=(snftname+1)%2
	if snftname==1:
		cur.execute(f"SELECT NFT_id, NFT_name, image_url, NFT_type, price, token_standard, description from nft where collection_id='{curr_collection}' order by nft_name;")
	else:
		cur.execute(f"SELECT NFT_id, NFT_name, image_url, NFT_type, price, token_standard, description from nft where collection_id='{curr_collection}' order by nft_name desc;")
	data = cur.fetchall()
	cur.close()
	return render_template('Manage_nfts.html', data=data)

global snfttype
snfttype=0
@app.route('/sortnfttype')
def sortnfttype():
	cur = mysql.connection.cursor()
	global snfttype
	global curr_collection
	snfttype=(snfttype+1)%2
	if snfttype==1:
		cur.execute(f"SELECT NFT_id, NFT_name, image_url, NFT_type, price, token_standard, description from nft where collection_id='{curr_collection}' order by nft_type;")
	else:
		cur.execute(f"SELECT NFT_id, NFT_name, image_url, NFT_type, price, token_standard, description from nft where collection_id='{curr_collection}' order by nft_type desc;")
	data = cur.fetchall()
	cur.close()
	return render_template('Manage_nfts.html', data=data)

global sprice
sprice=0
@app.route('/sortprice')
def sortprice():
	cur = mysql.connection.cursor()
	global sprice
	global curr_collection
	sprice=(sprice+1)%2
	if sprice==1:
		cur.execute(f"SELECT NFT_id, NFT_name, image_url, NFT_type, price, token_standard, description from nft where collection_id='{curr_collection}' order by price;")
	else:
		cur.execute(f"SELECT NFT_id, NFT_name, image_url, NFT_type, price, token_standard, description from nft where collection_id='{curr_collection}' order by price desc;")
	data = cur.fetchall()
	cur.close()
	return render_template('Manage_nfts.html', data=data)

global stokenstandard
stokenstandard=0
@app.route('/sorttokenstandard')
def sorttokenstandard():
	cur = mysql.connection.cursor()
	global stokenstandard
	global curr_collection
	stokenstandard=(stokenstandard+1)%2
	if stokenstandard==1:
		cur.execute(f"SELECT NFT_id, NFT_name, image_url, NFT_type, price, token_standard, description from nft where collection_id='{curr_collection}' order by token_standard;")
	else:
		cur.execute(f"SELECT NFT_id, NFT_name, image_url, NFT_type, price, token_standard, description from nft where collection_id='{curr_collection}' order by token_standard desc;")
	data = cur.fetchall()
	cur.close()
	return render_template('Manage_nfts.html', data=data)

@app.route('/mc/insertnft', methods = ['POST'])
def insertnft():
	if request.method == "POST":
		flash("Data Inserted Successfully")
		nft_id = request.form['nft_id']
		nft_name = request.form['nft_name']
		image_url = request.form['image_url']
		nft_type = request.form['nft_type']
		price = request.form['price']
		token_standard = request.form['token_standard']
		description = request.form['description']
		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO NFT (nft_id,nft_name,Collection_id,image_url,nft_type,price,token_standard,description) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);", (nft_id,nft_name,curr_collection,image_url,nft_type,price,token_standard,description))
		mysql.connection.commit()
		return redirect(f'/view/{curr_collection}')

@app.route('/mc/editnft', methods = ['POST'])
def editnft():
	if request.method == "POST":
		flash("Data Updated Successfully")
		nft_id=request.form['nft_id']
		nft_name = request.form['nft_name']
		image_url = request.form['image_url']
		nft_type = request.form['nft_type']
		price = request.form['price']
		token_standard = request.form['token_standard']
		description = request.form['description']
		cur = mysql.connection.cursor()
		cur.execute("UPDATE NFT SET nft_name=%s,image_url=%s,nft_type=%s,price=%s,token_standard=%s,description=%s where nft_id=%s ;", (nft_name,image_url,nft_type,price,token_standard,description,nft_id))
		mysql.connection.commit()
		return redirect(f'/view/{curr_collection}')

@app.route('/deletenft/<string:id_data>', methods = ['GET'])
def deletenft(id_data):
	flash("Record Has Been Deleted Successfully")
	cur = mysql.connection.cursor()
	cur.execute(f"DELETE FROM NFT WHERE NFT_id={id_data};")
	mysql.connection.commit()
	return redirect(f'/view/{curr_collection}')

if __name__ == "__main__":
    app.run(debug=True,host="localhost")