from flask import Flask, make_response, jsonify, render_template, request
import pdfkit


import qrcode
from io import BytesIO
from datetime import datetime

import json
import base64

import sys

# run the script with the arguments
# python app.py <confirmed_seating_path> <Institute_Name>

def help_msg():
	print("""
Run The Script with the following Arguments
python app.py <confirmed_seating_path> <Institute_Name>
""")

try:
	confirmed_seating_data_path = sys.argv[1]
	institute_name = sys.argv[2]
	wkhtmltopdf_path = 'wkhtmltox\\bin\\wkhtmltopdf.exe'
except IndexError:
	help_msg()
	exit()




## Flask Configurations
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Hello_I_am_Arijit_Bhowmick_sys41x4'


@app.route('/',methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/generate_admitcard',methods= ['POST'])
def home():
	data = request.get_json()
	roll_num = data['roll']
	aadhar_num =  data['aadhar']

	return jsonify({"roll_num":roll_num})

@app.route("/<aadhar_num>")
def roll_not_provided(aadhar_num):

	std_seating_info={"std_name": "","branch_name": "","roll_num": "Enrollment Number Not Provided","aadhar_num": aadhar_num,"block_num": "","room_num": "","row": "","column": ""}
	std_seating_info.update({'base64_qr_str':gen_verifiable_qr_code(std_seating_info), 'institute_name':institute_name})
	return generate_pdf(std_seating_info)

def generate_pdf(std_seating_info):
	rendered = render_template("pdf_templete.html", std_name = std_seating_info['std_name'], branch_name = std_seating_info['branch_name'], roll_num = std_seating_info['roll_num'], aadhar_num = std_seating_info['aadhar_num'], block_num = std_seating_info['block_num'], room_num = std_seating_info['room_num'], row = std_seating_info['row'], column = std_seating_info['column'], base64_qr_str=std_seating_info['base64_qr_str'], institute_name=std_seating_info['institute_name'])

	pdf = pdfkit.from_string(rendered, False, configuration=pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path))

	response = make_response(pdf)

	response.headers['Content-Type'] = 'application/pdf'
	
	response.headers['Content-Disposition'] = "inline;filename="+std_seating_info['roll_num']+"_"+str(datetime.date(datetime.now()))+".pdf"

	return response

@app.route("/<aadhar_num>/<roll_num>")
def admitcard(aadhar_num, roll_num):
	global confirmed_seating_data_path

	std_seating_info = fetch_json_data(confirmed_seating_data_path, roll_num)

	std_seating_info.update({'base64_qr_str':gen_verifiable_qr_code(std_seating_info), 'institute_name':institute_name})

	

	return generate_pdf(std_seating_info)

def fetch_json_data(confirmed_seating_data_path, roll_num):

	json_data=json.load(open(confirmed_seating_data_path))

	try:
		std_seating_info = json_data[roll_num.upper()]
	except KeyError:
		return {"std_name": "","branch_name": "","roll_num": "Enrollment Number is Not Valid","aadhar_num": "","block_num": "","room_num": "","row": "","column": "" }

	return std_seating_info

def gen_verifiable_qr_code(student_seating_data):
	qr = qrcode.QRCode(
		version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=3,
        border=3,
    )

	student_seating_data = json.dumps(student_seating_data, indent = 1)

	qr.add_data(student_seating_data)

	qr.make(fit=True)

	qr_img = qr.make_image()

	buffered = BytesIO()
	qr_img.save(buffered, format="PNG")

	base64_qr_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

	return base64_qr_str 

if __name__ == "__main__":
	app.run(debug=True,port='8090')