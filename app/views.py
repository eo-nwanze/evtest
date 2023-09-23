from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file, abort
from flask_login import login_required, current_user
from .models import db, User, Folder, File
from werkzeug.utils import secure_filename
from .api import api  # Import the 'api' variable from the 'api' module
import os
import io
from sqlalchemy import desc
from sqlalchemy import func

views = Blueprint('views', __name__)

# Your existing code...


@views.route('/') 
@login_required 
def home(): 
    return render_template('index.html')

def get_file_type_info():
    file_type_info = (
        db.session.query(File.file_type, func.sum(File.size).label('total_size'))
        .filter(Folder.user_id == current_user.id, File.folder_id == Folder.id)
        .group_by(File.file_type)
        .all()
    )
    return file_type_info

@views.route('/file_manager/')
@login_required
def file_manager():
    folders = Folder.query.filter_by(user_id=current_user.id).order_by(Folder.created_at).all()
    success = request.args.get('success')

    # Query the 5 most recent files for the current user
    recent_files = (
        File.query
        .join(Folder)  # Join with the Folder model to filter files by user ID
        .filter(Folder.user_id == current_user.id)  # Filter files associated with the current user's folders
        .order_by(desc(File.created_at))  # Order by creation date in descending order
        .limit(5)  # Limit the result to the top 5 files
        .all()
    )

    # Get file type information and total sizes
    file_type_info = get_file_type_info()

    # Pass the 'folder' variable, 'success' message, and 'recent_files' to the template
    return render_template('files/index.html', success=success, folders=folders, folder=None, recent_files=recent_files, file_type_info=file_type_info)

@views.route('/file_manager/<file_type>')
@login_required
def file_type_manager(file_type):
    # Retrieve files of the specified file type for the current user
    files = (
        File.query
        .join(Folder)  # Join with the Folder model to filter files by user ID
        .filter(Folder.user_id == current_user.id, File.folder_id == Folder.id, File.file_type == file_type)
        .all()
    )

    return render_template('files/file_type_manager.html', files=files, file_type=file_type)


@views.route('/checker/') 
@login_required 
def checker(): 
    return render_template('checker/index.html')


# Folder Views

@views.route('/create_folder', methods=['POST']) 
@login_required 
def create_folder(): 
    data = request.get_json() 
    new_folder = Folder(name=data['name'], user_id=current_user.id) 
    db.session.add(new_folder) 
    db.session.commit() 
    return render_template('files/index.html')
    return jsonify({'message': 'Folder created'}), 200


@views.route('/get_folders', methods=['GET'])
@login_required
def get_folders():
    folders = Folder.query.filter_by(user_id=current_user.id).order_by(desc(Folder.created_at)).all()
    folder_data = [{'id': folder.id, 'name': folder.name} for folder in folders]
    return jsonify(folder_data)


@views.route('/my_folders', methods=['GET']) 
@login_required 
def my_folders(): 
    folders = Folder.query.filter_by(user_id=current_user.id).all() 
    return jsonify([folder.name for folder in folders]), 200

@views.route('/edit_folder/<int:id>', methods=['PUT'])
@login_required
def edit_folder(id):
    data = request.get_json()
    folder = Folder.query.get_or_404(id)
    if folder.user_id != current_user.id:
        return jsonify({'message': 'Permission denied'}), 403
    folder.name = data['name']
    db.session.commit()
    return jsonify({'message': 'Folder updated'}), 200




@views.route('/folders/<int:folder_id>/contents', methods=['GET'])
@login_required
def view_folder(folder_id):
    folder = Folder.query.get_or_404(folder_id)

    if folder.user_id != current_user.id:
        return "Permission denied", 403

    # Fetch all child folders
    child_folders = Folder.query.filter_by(parent_id=folder_id).all()
    child_folders_data = [{
        'id': child.id,
        'name': child.name,
        'created_at': child.created_at,
        'type': 'folder'
    } for child in child_folders]

    # Fetch all files within the folder
    files = File.query.filter_by(folder_id=folder_id).all()
    files_data = [{
        'id': file.id,
        'name': file.name,
        'created_at': file.created_at,
        'size': file.size,
        'type': 'file'
    } for file in files]

    # Pass the folder contents to the template for rendering
    return render_template('files/contents.html', folder=folder,
                           contents=child_folders_data + files_data)






@views.route('/delete_folder/<int:id>', methods=['DELETE'])
@login_required
def delete_folder(id):
    folder = Folder.query.get_or_404(id)
    if folder.user_id != current_user.id:
        return jsonify({'message': 'Permission denied'}), 403
    db.session.delete(folder)
    db.session.commit()
    return jsonify({'message': 'Folder deleted'}), 200



# Files Views

@views.route('/upload_file', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'message': 'No file part'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400

        # Get the folder ID from the form data or provide a default value (e.g., None)
        folder_id = request.form.get('folder_id')

        # Check if the folder_id is valid
        folder = Folder.query.get(folder_id)
        if folder is None:
            return jsonify({'message': 'Invalid folder ID'}), 400

        if file:
            filename = secure_filename(file.filename)
            file_content = file.read()
            file_size = len(file_content)  # get the size of the file
            new_file = File(name=filename, data=file_content, size=file_size, folder_id=folder_id)  # include size in your File object
            new_file.set_file_type()
            db.session.add(new_file)
            db.session.commit()
            return redirect(url_for('views.file_manager', success='File uploaded successfully'))

    else:
        folders = Folder.query.filter_by(user_id=current_user.id).all()
        print(folders)  # add this line to debug
        return render_template('files/index.html', folders=folders)

@views.route('/my_files', methods=['GET'])
@login_required
def my_files():
    files = File.query.join(Folder).filter(Folder.user_id == current_user.id).all()
    file_data = [{'id': file.id, 'name': file.name} for file in files]
    return jsonify(file_data), 200



@views.route('/download_file/<int:file_id>', methods=['GET'])
@login_required
def download_file(file_id):
    # Get the file based on the file_id and user permissions
    file = File.query.filter_by(id=file_id, folder_id=current_user.id).first()

    if not file:
        # File does not exist or does not belong to the current user
        abort(404)

    # Create a response to send the file to the client
    response = send_file(
        io.BytesIO(file.data),  # Provide the file content as bytes
        as_attachment=True,    # Treat it as an attachment to trigger download
        download_name=file.name  # Set the file name for download
    )

    return response


@views.route('/delete_file/<int:id>', methods=['DELETE'])
@login_required
def delete_file(id):
    file = File.query.get_or_404(id)
    if file.folder.user_id != current_user.id:
        return jsonify({'message': 'Permission denied'}), 403
    db.session.delete(file)
    db.session.commit()
    return jsonify({'message': 'File deleted'}), 200



@views.route('/edit_file/<int:id>', methods=['PUT'])
@login_required
def edit_file(id):
    data = request.get_json()
    file = File.query.get_or_404(id)
    if file.folder.user_id != current_user.id:
        return jsonify({'message': 'Permission denied'}), 403
    file.name = data['name']
    db.session.commit()
    return jsonify({'message': 'File updated'}), 200
