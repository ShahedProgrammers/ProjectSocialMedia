document.addEventListener('DOMContentLoaded', () => {
  const editModal = document.getElementById('editModal');
  const commentsModal = document.getElementById('commentsModal');
  const editProfileBtn = document.getElementById('editProfileBtn');
  const closeModalBtn = document.getElementById('closeModalBtn');
  const closeCommentsModalBtn = document.getElementById('closeCommentsModalBtn');
  const editBio = document.getElementById('editBio');
  const bioElement = document.getElementById('bio');
  const commentsList = document.getElementById('commentsList');
  const commentsLoading = document.getElementById('commentsLoading');
  const commentsEmpty = document.getElementById('commentsEmpty');

  function getCsrfToken() {
    const tokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
    if (tokenInput) {
      return tokenInput.value;
    }

    const cookies = document.cookie ? document.cookie.split(';') : [];
    for (const cookie of cookies) {
      const trimmed = cookie.trim();
      if (trimmed.startsWith('csrftoken=')) {
        return decodeURIComponent(trimmed.slice('csrftoken='.length));
      }
    }

    return '';
  }

  function buildPostUrl(baseUrl, postId) {
    return baseUrl.replace('/0/', `/${postId}/`);
  }

  function openEditModal() {
    editModal.style.display = 'flex';
    editBio.value = bioElement.innerText.trim();
  }

  function closeEditModal() {
    editModal.style.display = 'none';
  }

  function openCommentsModal() {
    commentsModal.style.display = 'flex';
  }

  function closeCommentsModal() {
    commentsModal.style.display = 'none';
    commentsList.innerHTML = '';
    commentsEmpty.style.display = 'none';
    commentsLoading.style.display = 'none';
  }

  async function loadComments(postId) {
    commentsList.innerHTML = '';
    commentsEmpty.style.display = 'none';
    commentsLoading.style.display = 'block';
    openCommentsModal();

    try {
      const url = buildPostUrl(window.PROFILE_COMMENTS_BASE, postId);
      const response = await fetch(url);
      const data = await response.json();

      commentsLoading.style.display = 'none';

      if (!response.ok) {
        commentsEmpty.textContent = data.error || 'خطا در بارگذاری کامنت‌ها';
        commentsEmpty.style.display = 'block';
        return;
      }

      if (!data.comments || data.comments.length === 0) {
        commentsEmpty.textContent = 'هنوز کامنتی ثبت نشده.';
        commentsEmpty.style.display = 'block';
        return;
      }

      data.comments.forEach((comment) => {
        const item = document.createElement('div');
        item.className = 'comment-item';
        item.innerHTML = `
          <div class="comment-header">
            <strong>${escapeHtml(comment.username)}</strong>
            <small>${escapeHtml(comment.created_at)}</small>
          </div>
          <p class="comment-content">${escapeHtml(comment.content)}</p>
        `;
        commentsList.appendChild(item);
      });
    } catch (error) {
      commentsLoading.style.display = 'none';
      commentsEmpty.textContent = 'خطا در ارتباط با سرور';
      commentsEmpty.style.display = 'block';
    }
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  if (editProfileBtn && editModal && closeModalBtn && editBio && bioElement) {
    editProfileBtn.addEventListener('click', openEditModal);
    closeModalBtn.addEventListener('click', closeEditModal);

    window.addEventListener('click', (event) => {
      if (event.target === editModal) closeEditModal();
    });
  }

  if (closeCommentsModalBtn && commentsModal) {
    closeCommentsModalBtn.addEventListener('click', closeCommentsModal);

    window.addEventListener('click', (event) => {
      if (event.target === commentsModal) closeCommentsModal();
    });
  }

  document.querySelectorAll('.comments-btn').forEach((button) => {
    button.addEventListener('click', () => {
      loadComments(button.dataset.postId);
    });
  });

  document.querySelectorAll('.like-btn').forEach((button) => {
    button.addEventListener('click', async (event) => {
      event.preventDefault();
      event.stopPropagation();

      const postId = button.dataset.postId;
      const isLiked = button.dataset.isLiked === 'true';
      const like = !isLiked;
      const url = buildPostUrl(window.PROFILE_LIKE_URL, postId);
      const csrfToken = getCsrfToken();

      if (!csrfToken) {
        alert('خطا در احراز هویت. صفحه را رفرش کنید.');
        return;
      }

      button.disabled = true;

      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
          },
          body: JSON.stringify({ like }),
        });

        let data = {};
        try {
          data = await response.json();
        } catch (parseError) {
          throw new Error('پاسخ نامعتبر از سرور');
        }

        if (!response.ok) {
          alert(data.error || 'خطا در ثبت لایک');
          return;
        }

        button.dataset.isLiked = data.is_liked ? 'true' : 'false';
        button.classList.toggle('liked', data.is_liked);

        const countElement = button.querySelector('.like-count');
        if (countElement) {
          countElement.textContent = data.like_count;
        }
      } catch (error) {
        console.error(error);
        alert('خطا در ارتباط با سرور');
      } finally {
        button.disabled = false;
      }
    });
  });
});
