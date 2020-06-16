from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, request, jsonify, redirect, Response
import json

# Connect to our local MongoDB
client = MongoClient('mongodb://192.168.99.100:27017/')

# Choose InfoSys database
db = client['InfoSys']
students = db['Students']

# Initiate Flask App
app = Flask(__name__)

# Insert Student
# Create Operation
@app.route('/insertstudent', methods=['POST'])
def insert_student():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
        print(data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "name" in data or not "yearOfBirth" in data or not "email" in data or not "address" in data or not "street" in data['address'] or not "city" in data['address'] or not "postcode" in data['address']:
        return Response("Information incompleted",status=500,mimetype="application/json")
    
    if students.count_documents({"email":data["email"]}) == 0 :
        student = {"email": data['email'], "name": data['name'],  "yearOfBirth":data['yearOfBirth'], "address":data['address']}
        # Add student to the 'students' collection
        students.insert_one(student)
        return Response("was added to the MongoDB",status=200,mimetype='application/json') 
    else:
        return Response("A user with the given email already exists",status=200,mimetype='application/json')

# Read Operations

@app.route('/getAllStudentsAddress', methods=['GET'])
def get_all_students_address():
    iterable = students.find({"address": {"$exists" : "true"}})
    output = []
    for student in iterable:
        student['_id'] = None 
        output.append(student)
    return jsonify(output)

@app.route('/getStudentAddress/<string:email>', methods=['GET'])
def get_student_address_by_email(email):
    if email == None:
        return Response("Bad request", status=500, mimetype='application/json')
    iterable = students.find({"email":email})
    if iterable !=None:
        output = []
        for student in iterable:
            if "name" in student and "yearOfBirth" in student and "email" in student and "address" in student:
                student = {'_id':str(student["_id"]),'name':student["name"],'email':student["email"], 'yearOfBirth':student["yearOfBirth"], 'address':student["address"]} 
                output.append(student)
        if output == []:
            return Response('no address found',status=500,mimetype='application/json')
        else:
            return jsonify(output)    
    return Response('no student found',status=500,mimetype='application/json')

@app.route('/getEightiesAddress', methods=['GET'])
def get_eighties_address():
    iterable = students.find({"address": {"$exists" : "true"}, "yearOfBirth": {"$gt" : 1979, "$lt" : 1990}})
    output = []
    for student in iterable:
        student['_id'] = None 
        output.append(student)
    return jsonify(output) 

@app.route('/countAddress', methods=['GET'])
def count_address():
    number_of_students = students.count_documents({"address": {"$exists" : "true"}})
    return jsonify({"Number of students with address": number_of_students})

@app.route('/countYearOfBirth/<int:yearOfBirth>', methods=['GET'])
def count_year_of_birth(yearOfBirth):
    number_of_students = students.count_documents({"yearOfBirth":yearOfBirth})
    return jsonify({"Number of students": number_of_students})

# Run Flask App
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)