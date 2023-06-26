from flask import Blueprint,request,jsonify
from flask_login import login_user,logout_user,login_required,current_user

# Importing the Database Models and Instance
from .models import Note
from . import db

# Creating the Blueprint Instance
notes = Blueprint("notes",__name__)


# Route for the User to see their own Notes
@notes.route('/')
@login_required
def get_user_notes():
    # Get the List of Notes for a Given User
    user_specific_notes = Note.query.filter_by(author=current_user.id).all()
    res = []

    # If there is no note for that user
    if not len(user_specific_notes):
        return jsonify({"msg":"No Notes Found for Specific User!"})

    # Constructing the Result and returning it
    for note in user_specific_notes:
        res.append({"id":note.id,"title":note.title,"content":note.content,"is_public":note.is_public})
    return jsonify({"username":current_user.username,"notes" : res})



# Route for Creating a Note
@notes.route('/create',methods = ['POST'])
@login_required
def create_note():
    # Getting the Note Content
    jsonified_req = request.json
    title = jsonified_req["title"]
    content = jsonified_req["content"]
    is_public = jsonified_req["is_public"]

    # Handling the "Title" or/and "content" being blank
    if not title:
        return jsonify({"status": "error", "msg" : "Title Cannot be empty"})

    elif not content:
        return jsonify({"status": "error", "msg" : "Notes cannot be empty"})
    
    # Saving the Note
    else:
        try:
            new_note = Note(title=title,content=content,is_public=is_public,author=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            return jsonify({"status":"success","msg" : "Note Created", "note_id":new_note.id})
        except Exception as err:
            print(err)
            return jsonify({"status":"Failure","msg":"Internal Database error occured"})


# Route for getting all the Notes
@notes.route('/get')
def get_notes():
    # Getting all the Notes and populating in a JSON Array to be returned
    notes = Note.query.all()
    res = []
    for note in notes:
        res.append({"id":note.id,"author" : note.user.username,"title":note.title,"content":note.content,"is_public":note.is_public})
    return jsonify(res)


# Route for Updating the note by its ID
@notes.route('/update/<id>',methods=['PUT'])
@login_required
def update_note(id):
    note_from_id = Note.query.filter_by(id=id).first()

    # Getting the Note Content
    jsonified_req = request.json
    title = jsonified_req["title"]
    content = jsonified_req["content"]
    is_public = jsonified_req["is_public"]

    # If there is no note with the specific ID
    if not note_from_id:
        return jsonify({"status":"error","msg":f"No note with id = {id} exists!"})
    
    # Handling the "Title" or/and "content" being blank
    if not title:
        return jsonify({"status": "error", "msg" : "Title Cannot be empty"})
    
    if not content:
        return jsonify({"status": "error", "msg" : "Notes cannot be empty"})

    # Checking whether the author is editing the Note or not
    if note_from_id.author != current_user.id:
        return jsonify({"status":"Unauthorized","msg":"You have don't have the access to Delete the Specific Note!"})
    else:
        note_from_id.title=title
        note_from_id.content=content
        note_from_id.is_public=is_public
        db.session.commit()
        return jsonify({"id":note_from_id.id,"title":note_from_id.title,"content":note_from_id.content,"is_public":note_from_id.is_public})
    

# Route for deleting a Note
@notes.route('/delete',methods=['DELETE'])
@login_required
def delete_note():
    # Getting the ID of Note to be Deleted
    jsonified_req = request.json
    note_id = jsonified_req["note_id"]

    note = Note.query.filter_by(id=note_id).first()

    # If the Note with the given ID doesn't exist
    if not note:
        return jsonify({"status":"Failure","msg":"Note does not exist"})
    
    # Checking whether the user is the author cz for deleting a Note, You must be its author!
    elif note.author != current_user.id:
        return jsonify({"status":"Unauthourized","msg":"You have don't have the access to Delete the Specific Note!"})

    else:
        db.session.delete(note)
        db.session.commit()
        return jsonify({"status":"Success","msg" : "Note Deleted"})
    

# Route for accessing a Note by its ID
@notes.route('/<id>')
@login_required
def get_note_by_id(id):
    note_from_id = Note.query.filter_by(id=id).first()

    # Checking whether the Note with the given ID exists or not!
    if not note_from_id:
        return jsonify({"status":"error","msg":f"No note with id = {id} exists!"})
    
    res = {"id":note_from_id.id,"author" : note_from_id.user.username, "title":note_from_id.title,"content":note_from_id.content,"is_public":note_from_id.is_public}

    # If the Note is Public, then show it!
    if note_from_id.is_public:
        return jsonify(res)
    else:

        # (Note is not public) and (current viewer is not the author)
        if note_from_id.author != current_user.id:
            return jsonify({"status":"error","msg" : "You are not allowed to access this Private Note"})
        else:
            return jsonify(res)
