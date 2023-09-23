// api_file.js

$(document).ready(function () {
    // Handle the Delete Folder button
    $(document).on('click', '.delete-folder-button', function () {
        const folderId = $(this).data('folder-id');

        // Send an AJAX request to delete the folder
        $.ajax({
            url: '/api/folders/' + folderId,
            method: 'DELETE',
            success: function (response) {
                // Remove the deleted folder from the UI
                $('#folder-card-' + folderId).remove();
            },
            error: function (error) {
                // Handle errors here, e.g., display an error message
            },
        });
    });

    // JavaScript code to set the folder_id when opening the modal
    $('#create-file').on('show.bs.modal', function (event) {
        var modal = $(this);
        var folderSelect = modal.find('#folder-select');

        // Fetch folder data via AJAX
        $.ajax({
            url: '/get_folders',
            type: 'GET',
            success: function (data) {
                // Clear existing options and add new options
                folderSelect.empty();
                data.forEach(function (folder) {
                    folderSelect.append($('<option>', {
                        value: folder.id,
                        text: folder.name
                    }));
                });
            },
            error: function () {
                alert('Failed to fetch folder data.');
            }
        });
    });

    // Handle folder deletion
    const deleteFolderButtons = document.querySelectorAll(".delete-folder");
    deleteFolderButtons.forEach((button) => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            const folderId = this.getAttribute("data-folder-id");
            Swal.fire({
                title: "Are you sure?",
                text: "You won't be able to revert this!",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#3085d6",
                cancelButtonColor: "#d33",
                confirmButtonText: "Yes, delete it!",
                focusConfirm: false,
                focusCancel: false,
                showClass: {
                    popup: "animate__animated animate__fadeInDown",
                },
                hideClass: {
                    popup: "animate__animated animate__fadeOutUp",
                },
            }).then((result) => {
                if (result.isConfirmed) {
                    // Send a DELETE request to the API to delete the folder
                    fetch(`/api/folders/${folderId}`, {
                        method: "DELETE",
                    })
                        .then((response) => response.json())
                        .then((data) => {
                            if (data.message === "Folder and associated files deleted") {
                                Swal.fire({
                                    title: "Deleted!",
                                    text: "Your folder has been deleted.",
                                    icon: "success",
                                }).then(() => location.reload());
                            } else {
                                Swal.fire({
                                    title: "Error!",
                                    text: "There was an error deleting your folder.",
                                    icon: "error",
                                });
                            }
                        })
                        .catch((error) => {
                            console.error(error);
                            Swal.fire({
                                title: "Error!",
                                text: "Failed to delete the folder",
                                icon: "error",
                            });
                        });
                }
            });
        });
    });

    // Function to populate the folder dropdown with API data
    function populateFolderDropdown() {
        const folderSelect = document.getElementById('folder-select');

        // Make an API request to get the list of user's folders
        fetch('/api/folders', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer {{ API_TOKEN }}', // Render the API_TOKEN here
            },
        })
        .then(response => response.json())
        .then(data => {
            // Populate the dropdown options with folder data
            data.forEach(folder => {
                const option = document.createElement('option');
                option.value = folder.id;
                option.textContent = folder.name;
                folderSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error fetching folders:', error);
        });
    }

    // Function to create a folder using the API
    function createFolder(event) {
        event.preventDefault();
        const folderName = document.getElementById('create-folder1').value;

        // Make an API request to create a new folder
        fetch('/api/folders', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer {{ API_TOKEN }}', // Render the API_TOKEN here
            },
            body: JSON.stringify({ name: folderName }),
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            // Reload the page to reflect the newly created folder
            location.reload();
        })
        .catch(error => {
            console.error('Error creating folder:', error);
        });
    }

    // Function to upload a file using the API
    function uploadFile() {
        const folderSelect = document.getElementById('folder-select');
        const formData = new FormData(document.getElementById('uploadFileForm'));

        // Set the folder_id field in the form data with the selected folder's value
        formData.set('folder_id', folderSelect.value);

        // Make an API request to upload a file
        fetch('/api/files', {
            method: 'POST',
            headers: {
                'Authorization': 'Bearer {{ API_TOKEN }}', // Render the API_TOKEN here
            },
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            // Reload the page to reflect the newly uploaded file
            location.reload();
        })
        .catch(error => {
            console.error('Error uploading file:', error);
        });
    }

    // Call the populateFolderDropdown function when the page loads
    window.addEventListener('load', () => {
        populateFolderDropdown();
    });

    // Handle edit folder form submission
    $(document).on('click', '.edit-folder-button', function () {
        const folderId = $(this).data('folder-id');
        const newName = $('#edit-folder-name-' + folderId).val();

        $.ajax({
            url: `/api/folders/${folderId}`,
            method: 'PUT',
            contentType: 'application/json',
            data: JSON.stringify({ 'name': newName, 'folder_id': folderId }), // Include folder_id
            success: function (data) {
                // Close the modal
                $('#editFolderModal-' + folderId).modal('hide');

                // Display a SweetAlert success message
                Swal.fire({
                    title: 'Success!',
                    text: 'Folder name updated successfully.',
                    icon: 'success',
                }).then((result) => {
                    // Update the folder name in the UI
                    $('#folder-name-' + folderId).text(newName);
                });
            },
            error: function () {
                Swal.fire({
                    title: 'Error!',
                    text: 'An error occurred while updating the folder name.',
                    icon: 'error',
                });
            }
        });
   
