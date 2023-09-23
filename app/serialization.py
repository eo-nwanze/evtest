def serialize_shared_file(shared_file):
    return {
        'id': shared_file.id,
        'file_id': shared_file.file_id,
        'user_id': shared_file.user_id,
        'shared_at': shared_file.shared_at.strftime('%Y-%m-%d %H:%M:%S'),
    }


def serialize_folder(folder):
    return {
        'id': folder.id,
        'name': folder.name,
        'created_at': folder.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'is_zipped': folder.is_zipped,
        'files': [serialize_file(file) for file in folder.files],
        'children': [serialize_folder(child_folder) for child_folder in folder.children],  # serialize child folders
    }


def serialize_file(file):
    return {
        'id': file.id,
        'name': file.name,
        'size': file.size,
        'file_type': file.file_type.value,
        'created_at': file.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'deleted': file.deleted,
        'folder_id': file.folder_id,  # Include folder_id
        'folder_name': file.folder.name if file.folder else None,  # Include folder name
        'shared_files': [serialize_shared_file(shared_file) for shared_file in file.shared_files],
    }
