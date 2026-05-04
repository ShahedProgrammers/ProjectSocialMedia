document.addEventListener('DOMContentLoaded', () => {
  const editModal = document.getElementById('editModal');
  const editProfileBtn = document.getElementById('editProfileBtn');
  const closeModalBtn = document.getElementById('closeModalBtn');
  const editBio = document.getElementById('editBio');
  const bioElement = document.getElementById('bio');
  const postsGrid = document.getElementById('postsGrid');

  function loadDummyData() {
    document.getElementById('postsCount').innerText = '۱۲';
    document.getElementById('followersCount').innerText = '۱٬۲۰۳';
    document.getElementById('followingCount').innerText = '۳۴۵';

    postsGrid.innerHTML = '';
    const colors = ['#f8f9fc', '#f3f4f6', '#e5e7eb', '#d1d5db', '#9ca3af', '#6b7280', '#4b5563', '#374151', '#1f2937'];
    for (let i = 1; i <= 9; i++) {
      const postItem = document.createElement('div');
      postItem.className = 'post-item';
      const color = colors[i % colors.length];
      const svg = `<svg width="300" height="300" viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg"><rect width="300" height="300" fill="${color}"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="#ffffff" font-size="24" font-family="sans-serif">پست ${i}</text></svg>`;
      postItem.innerHTML = `<img src="data:image/svg+xml;utf8,${encodeURIComponent(svg)}" alt="پست ${i}">`;
      postsGrid.appendChild(postItem);
    }
  }

  function openEditModal() {
    editModal.style.display = 'flex';
    editBio.value = bioElement.innerText;
  }

  function closeEditModal() {
    editModal.style.display = 'none';
  }

  editProfileBtn.addEventListener('click', openEditModal);
  closeModalBtn.addEventListener('click', closeEditModal);
  window.addEventListener('click', (event) => {
    if (event.target === editModal) closeEditModal();
  });

  loadDummyData();
});

console.log("parham");
