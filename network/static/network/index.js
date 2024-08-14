function edit(id) {
  const content = document.getElementById(`content${id}`);
  const editarea = document.getElementById(`editarea${id}`);
  const editBtn = document.getElementById(`edit-btn${id}`);

  // Hide content show textarea
  content.classList.toggle('hidden');
  editarea.classList.toggle('hidden');

  // Toggle the edit button
  if (editBtn.textContent === 'edit') {
    editBtn.textContent = 'cancel'; 
  }
  else {
    editBtn.textContent = 'edit';
  }
}

function save(id) {
  const newContent = document.getElementById(`textarea${id}`).value;
  const content = document.getElementById(`content${id}`);
  const editarea = document.getElementById(`editarea${id}`);
  const editBtn = document.getElementById(`edit-btn${id}`);

  // Send edited content to backend
  fetch(`/edit/${id}`, {
    method: 'POST',
    body: JSON.stringify({
      newContent: newContent
    })
  })
  .then(response => response.json())
  .then(result => {
    console.log(result)
  })

  // Replace old content with new content
  content.textContent = newContent

  // Hide textarea and show new content
  content.classList.toggle('hidden');
  editarea.classList.toggle('hidden');

  // Toggle the edit button
  editBtn.textContent = 'edit';
}

function like(id) {
  const likeBtn = document.getElementById(`like${id}`);
  var likeCount = document.getElementById(`like-count${id}`);

  // Toggle the like button properties
  likeBtn.classList.toggle('clicked');

  setTimeout(() => {
    likeBtn.classList.toggle('red-like-btn');
  }, 100);

  setTimeout(() => {
    likeBtn.classList.toggle('clicked');
  }, 100);

  // Add or remove like
  fetch(`/like/${id}`)
  .then(response => response.json())
  .then(result => {
    console.log(result);
    
    // Change like count on page temporarily without reload
    if (result.message === 'Liked') {

      // Remove one like
      likeCount.innerHTML = parseInt(likeCount.innerHTML) + 1;
    }
    else {

      // Add one like
      likeCount.innerHTML = parseInt(likeCount.innerHTML) - 1;
    }
  })
}