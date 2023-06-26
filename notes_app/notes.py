from flask import Blueprint,request,jsonify
from flask_login import login_user,logout_user,login_required,current_user



# Importing the Database Models and Instance
from .models import Note
from . import db

# Creating the Blueprint Instance
notes = Blueprint("notes",__name__)

@notes.route('/')
@login_required
def get_user_notes():
    user_specific_notes = Note.query.filter_by(author=current_user.id).all()
    res = []

    if not len(user_specific_notes):
        return jsonify({"msg":"No Notes Found for Specific User!"})

    for note in user_specific_notes:
        res.append({"id":note.id,"title":note.title,"content":note.content,"is_public":note.is_public})
    
    return jsonify({"username":current_user.username,"notes" : res})


@notes.route('/<id>')
@login_required
def get_note_by_id(id):
    note_from_id = Note.query.filter_by(id=id).first()

    if not note_from_id:
        return jsonify({"status":"error","msg":f"No note with id = {id} exists!"})
    
    if note_from_id.is_public:
        return jsonify({"id":note_from_id.id,"author" : note_from_id.user.username, "title":note_from_id.title,"content":note_from_id.content,"is_public":note_from_id.is_public})
    else:
        if note_from_id.author != current_user.id:
            return jsonify({"status":"error","msg" : "You are not allowed to access this Private Note"})
        else:
            return jsonify({"id":note_from_id.id,"author" : note_from_id.user.username, "title":note_from_id.title,"content":note_from_id.content,"is_public":note_from_id.is_public})

@notes.route('/update/<id>',methods=['PUT'])
@login_required
def update_note(id):
    note_from_id = Note.query.filter_by(id=id).first()

    # Getting the Note Content
    jsonified_req = request.json
    title = jsonified_req["title"]
    content = jsonified_req["content"]
    is_public = jsonified_req["is_public"]

    if not note_from_id:
        return jsonify({"status":"error","msg":f"No note with id = {id} exists!"})
    
    if not title:
        return jsonify({"status": "error", "msg" : "Title Cannot be empty"})
    
    if not content:
        return jsonify({"status": "error", "msg" : "Notes cannot be empty"})
    
    if note_from_id.author != current_user.id:
        return jsonify({"status":"Unauthourized","msg":"You have don't have the access to Delete the Specific Note!"})
    else:
        note_from_id.title=title
        note_from_id.content=content
        note_from_id.is_public=is_public
        db.session.commit()
        return "Done!"
    




@notes.route('/get')
def get_notes():
    notes = Note.query.all()
    res = []
    for note in notes:
        res.append({"id":note.id,"author" : note.user.username,"title":note.title,"content":note.content,"is_public":note.is_public})
    return jsonify(res)



@notes.route('/create',methods = ['POST'])
@login_required
def create_note():
    # Getting the Note Content
    jsonified_req = request.json
    title = jsonified_req["title"]
    content = jsonified_req["content"]
    is_public = jsonified_req["is_public"]

    if not title:
        return jsonify({"status": "error", "msg" : "Title Cannot be empty"})

    elif not content:
        return jsonify({"status": "error", "msg" : "Notes cannot be empty"})
    
    else:
        try:
            new_note = Note(title=title,content=content,is_public=is_public,author=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            return jsonify({"status":"success","msg" : "Note Created", "note_id":new_note.id})
        except Exception as err:
            print(err)
            return jsonify({"status":"Failure","msg":"Internal Database error occured"})

@notes.route('/delete',methods=['DELETE'])
@login_required
def delete_note():
    # Getting the ID of Note to be Deleted
    jsonified_req = request.json
    note_id = jsonified_req["note_id"]

    note = Note.query.filter_by(id=note_id).first()

    if not note:
        return jsonify({"status":"Failure","msg":"Note does not exist"})
    
    elif note.author != current_user.id:
        return jsonify({"status":"Unauthourized","msg":"You have don't have the access to Delete the Specific Note!"})

    else:
        db.session.delete(note)
        db.session.commit()
        return jsonify({"status":"Success","msg" : "Note Deleted"})