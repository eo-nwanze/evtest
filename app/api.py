from flask import Blueprint, request, jsonify
from sqlalchemy import desc
from .models import db, Folder, File, SharedFile, FileType  # Import FileType here
from .serialization import serialize_folder, serialize_file
from flask_login import login_required, current_user
from datetime import datetime
from .token import read_api_token_from_file
from werkzeug.utils import secure_filename
import os.path  # Add this import

# Update the file_extension_map with correct enum values
file_extension_map = {
    'pdf': FileType.PDF,
    'docx': FileType.DOCX,
    'csv': FileType.CSV,
    'xlsx': FileType.XLSX,
    'xlsx': 'XLSX File (.xlsx)',  # Updated entry for XLSX files
    'jpg': FileType.IMAGE,  # Use the correct enum value for images
    'jpeg': FileType.IMAGE,  # Use the correct enum value for images
    'png': FileType.IMAGE,  # Use the correct enum value for images
    'gif': FileType.IMAGE,  # Use the correct enum value for images
    'mp4': FileType.VIDEO,
    'other': FileType.OTHER,
}




# Read the API token from the file
API_TOKEN = read_api_token_from_file()
# Create a Blueprint for your API views
api = Blueprint('api', __name__)

# Define the filename for the API token file
API_TOKEN_FILENAME = 'api_token.txt'

# Read the API token from the file
with open(API_TOKEN_FILENAME, 'r') as token_file:
    API_TOKEN = token_file.read().strip()


# ... (rest of your code)

# Create Folder API
@api.route('/api/folders', methods=['POST'])
@login_required
def create_folder_api():
    data = request.get_json()
    new_folder = Folder(name=data['name'], user_id=current_user.id, parent_id=data.get('parent_id', None))
    db.session.add(new_folder)
    db.session.commit()
    return jsonify({'message': 'Folder created'}), 201


@api.route('/api/folders/<int:parent_id>/children', methods=['POST'])
@login_required
def create_child_folder_api(parent_id):
    data = request.get_json()
    parent_folder = Folder.query.get_or_404(parent_id)
    if parent_folder.user_id != current_user.id:
        return jsonify({'message': 'Permission denied'}), 403
    new_folder = Folder(name=data['name'], user_id=current_user.id, parent_id=parent_id)
    db.session.add(new_folder)
    db.session.commit()
    return jsonify({'message': 'Child folder created'}), 201

@api.route('/api/folders/<int:folder_id>/contents', methods=['GET'])
@login_required
def get_folder_contents(folder_id):
    folder = Folder.query.get_or_404(folder_id)

    if folder.user_id != current_user.id:
        return jsonify({'message': 'Permission denied'}), 403

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

    return jsonify({
        'folder_name': folder.name,
        'contents': child_folders_data + files_data
    }), 200


# List Folders API
@api.route('/api/folders', methods=['GET'])
@login_required
def list_folders_api():
    folders = Folder.query.filter_by(user_id=current_user.id).order_by(desc(Folder.created_at)).all()
    folder_data = [serialize_folder(folder) for folder in folders]
    return jsonify(folder_data), 200

# List Files in Folder API
@api.route('/api/folders/<int:id>/files', methods=['GET'])
@login_required
def list_files_in_folder_api(id):
    folder = Folder.query.get_or_404(id)
    if folder.user_id != current_user.id:
        return jsonify({'message': 'Permission denied'}), 403
    files = File.query.filter_by(folder_id=id).all()
    file_data = [serialize_file(file) for file in files]
    return jsonify(file_data), 200

# Retrieve Folder API
@api.route('/api/folders/<int:id>', methods=['GET'])
@login_required
def get_folder_api(id):
    folder = Folder.query.get_or_404(id)
    if folder.user_id != current_user.id:
        return jsonify({'message': 'Permission denied'}), 403
    folder_data = serialize_folder(folder)
    return jsonify(folder_data), 200

# Update Folder API
@api.route('/api/folders/<int:id>', methods=['PUT'])
@login_required
def update_folder_api(id):
    data = request.get_json()
    folder = Folder.query.get_or_404(id)
    if folder.user_id != current_user.id:
        return jsonify({'message': 'Permission denied'}), 403
    folder.name = data['name']
    db.session.commit()
    return jsonify({'message': 'Folder updated'}), 200

@api.route('/api/folders/<int:id>', methods=['DELETE'])
@login_required
def delete_folder_api(id):
    folder = Folder.query.get_or_404(id)
    if folder.user_id != current_user.id:
        return jsonify({'message': 'Permission denied'}), 403
    
    # Delete associated files within the folder
    files_to_delete = File.query.filter_by(folder_id=id).all()
    for file in files_to_delete:
        db.session.delete(file)
    
    db.session.delete(folder)
    db.session.commit()
    return jsonify({'message': 'Folder and associated files deleted'}), 200




@api.route('/api/files', methods=['POST'])
@login_required
def upload_file_api():
    print('API route hit')  # Add this line for debugging
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    folder_id = request.form.get('folder_id')
    folder = Folder.query.get(folder_id)

    if folder is None or folder.user_id != current_user.id:
        return jsonify({'message': 'Invalid folder ID'}), 400

    filename = secure_filename(file.filename)

    # Extract the file extension
    file_extension = os.path.splitext(filename)[1][1:].lower()

    file_content = file.read()
    file_size_kb = len(file_content) / 1024.0  # Calculate file size in KB

    # Create the File object using the correct attribute name 'size'
    new_file = File(name=filename, data=file_content, size=file_size_kb, folder_id=folder_id)

    # Use the file_extension_map to set the file_type attribute
    if file_extension == 'xlsx':
        new_file.file_type = FileType.XLSX
    else:
        new_file.file_type = file_extension_map.get(file_extension, FileType.OTHER)

    db.session.add(new_file)
    db.session.commit()
    return jsonify({'message': 'File uploaded successfully'}), 201




# List Files API
@api.route('/api/files', methods=['GET'])
@login_required
def list_files_api():
    files = File.query.join(Folder).filter(Folder.user_id == current_user.id).all()
    file_data = [serialize_file(file) for file in files]
    return jsonify(file_data), 200

# Retrieve File API
@api.route('/api/files/<int:id>', methods=['GET'])
@login_required
def get_file_api(id):
    file = File.query.get_or_404(id)
    if file.folder.user_id != current_user.id:
        return jsonify({'message': 'Permission denied'}), 403
    file_data = serialize_file(file)
    return jsonify(file_data), 200

# Update File API
@api.route('/api/files/<int:id>', methods=['PUT'])
@login_required
def update_file_api(id):
    data = request.get_json()
    file = File.query.get_or_404(id)
    if file.folder.user_id != current_user.id:
        return jsonify({'message': 'Permission denied'}), 403
    file.name = data['name']
    db.session.commit()
    return jsonify({'message': 'File updated'}), 200

# Delete File API
@api.route('/api/files/<int:id>', methods=['DELETE'])
@login_required
def delete_file_api(id):
    file = File.query.get_or_404(id)
    if file.folder.user_id != current_user.id:
        return jsonify({'message': 'Permission denied'}), 403
    db.session.delete(file)
    db.session.commit()
    return jsonify({'message': 'File deleted'}), 200


@api.route('/api/secure-endpoint', methods=['POST'])
def secure_endpoint():
    # Check if the provided token matches the expected token
    provided_token = request.headers.get('Authorization')

    if provided_token != f'Bearer {API_TOKEN}':
        return jsonify({'message': 'Authentication failed'}), 401

    # Your API logic here

    return jsonify({'message': 'Success'}), 200


# calculated querries api
@api.route('/api/files/recent', methods=['GET'])
@login_required
def list_recent_files_api():
    # Query the top 5 most recently uploaded files by the user
    files = File.query.filter_by(folder_id=None, deleted=False).filter_by(folder.user_id == current_user.id).order_by(desc(File.created_at)).limit(5).all()
    file_data = [serialize_file(file) for file in files]
    return jsonify(file_data), 200


@api.route('/api/folders/<int:id>/file_count', methods=['GET'])
@login_required
def count_files_in_folder_api(id):
    folder = Folder.query.get_or_404(id)
    if folder.user_id != current_user.id:
        return jsonify({'message': 'Permission denied'}), 403
    file_count = File.query.filter_by(folder_id=id).count()
    return jsonify({'file_count': file_count}), 200


@api.route('/api/folders/<int:id>/total_size', methods=['GET'])
@login_required
def calculate_total_size_in_folder_api(id):
    folder = Folder.query.get_or_404(id)
    if folder.user_id != current_user.id:
        return jsonify({'message': 'Permission denied'}), 403
    files = File.query.filter_by(folder_id=id).all()
    total_size_bytes = sum(file.size * 1024 for file in files)  # Convert KB to bytes
    total_size_MB = total_size_bytes / (1024 * 1024)  # Convert bytes to MB
    total_size_GB = total_size_MB / 1024  # Convert MB to GB
    return jsonify({'total_size_MB': total_size_MB, 'total_size_GB': total_size_GB}), 200


