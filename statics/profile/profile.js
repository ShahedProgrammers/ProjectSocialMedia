document.addEventListener('DOMContentLoaded', () => {
  const editModal = document.getElementById('editModal');
  const commentsModal = document.getElementById('commentsModal');
  const usersModal = document.getElementById('usersModal');
  const editProfileBtn = document.getElementById('editProfileBtn');
  const closeModalBtn = document.getElementById('closeModalBtn');
  const closeCommentsModalBtn = document.getElementById('closeCommentsModalBtn');
  const closeUsersModalBtn = document.getElementById('closeUsersModalBtn');
  const editBio = document.getElementById('editBio');
  const bioElement = document.getElementById('bio');
  const commentsList = document.getElementById('commentsList');
  const commentsLoading = document.getElementById('commentsLoading');
  const commentsEmpty = document.getElementById('commentsEmpty');
  const usersList = document.getElementById('usersList');
  const usersLoading = document.getElementById('usersLoading');
  const usersEmpty = document.getElementById('usersEmpty');
  const usersModalTitle = document.getElementById('usersModalTitle');
  const followBtn = document.getElementById('followBtn');
  const followersStat = document.getElementById('followersStat');
  const followingStat = document.getElementById('followingStat');
  const followersCountEl = document.getElementById('followersCount');
  const followingCountEl = document.getElementById('followingCount');

  const defaultAvatar = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='40' viewBox='0 0 40 40'%3E%3Crect width='40' height='40' fill='%23e5e7eb'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' fill='%239ca3af' font-size='18' dy='.3em'%3E%F0%9F%91%A4%3C/text%3E%3C/svg%3E";

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

  function buildUserUrl(baseUrl, userId) {
    return baseUrl.replace('/0/', `/${userId}/`);
  }

  function buildFollowUrl(userId) {
    return buildUserUrl(window.PROFILE_FOLLOW_URL, userId);
  }

  function buildProfileUrl(userId) {
    return buildUserUrl(window.PROFILE_USER_URL, userId);
  }

  function updateFollowButton(button, isFollowing) {
    button.dataset.isFollowing = isFollowing ? 'true' : 'false';
    button.classList.toggle('following', isFollowing);
    button.textContent = isFollowing ? 'دنبال می‌کنید' : 'دنبال کردن';
  }

  async function parseJsonResponse(response) {
    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      throw new Error('پاسخ نامعتبر از سرور');
    }
    return response.json();
  }

  async function toggleFollow(userId, follow, button) {
    const csrfToken = getCsrfToken();
    if (!csrfToken) {
      alert('خطا در احراز هویت. صفحه را رفرش کنید.');
      return null;
    }

    if (button) {
      button.disabled = true;
    }

    try {
      const response = await fetch(buildFollowUrl(userId), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({ follow }),
      });

      const data = await parseJsonResponse(response);
      if (!response.ok) {
        alert(data.error || 'خطا در انجام عملیات');
        return null;
      }

      if (button) {
        updateFollowButton(button, data.is_following);
      }

      if (followersCountEl && button && button.id === 'followBtn') {
        followersCountEl.textContent = data.followers_count;
      }

      return data;
    } catch (error) {
      alert('خطا در ارتباط با سرور');
      return null;
    } finally {
      if (button) {
        button.disabled = false;
      }
    }
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

  function openUsersModal() {
    usersModal.style.display = 'flex';
  }

  function closeUsersModal() {
    usersModal.style.display = 'none';
    usersList.innerHTML = '';
    usersEmpty.style.display = 'none';
    usersLoading.style.display = 'none';
  }

  function renderUserRow(user) {
    const row = document.createElement('div');
    row.className = 'user-row';

    const avatarSrc = user.profile_pic
      ? `data:image/jpeg;base64,${user.profile_pic}`
      : defaultAvatar;

    const canToggle = window.CURRENT_USER_ID && user.user_id !== window.CURRENT_USER_ID;
    const actionHtml = canToggle
      ? `<button type="button" class="follow-btn list-follow-btn${user.is_following ? ' following' : ''}" data-user-id="${user.user_id}" data-is-following="${user.is_following ? 'true' : 'false'}">${user.is_following ? 'دنبال می‌کنید' : 'دنبال کردن'}</button>`
      : '';

    row.innerHTML = `
      <a href="${buildProfileUrl(user.user_id)}" class="user-info-link">
        <img src="${avatarSrc}" alt="${escapeHtml(user.username)}" class="user-avatar">
        <strong>${escapeHtml(user.username)}</strong>
      </a>
      ${actionHtml}
    `;

    const listBtn = row.querySelector('.list-follow-btn');
    if (listBtn) {
      listBtn.addEventListener('click', async (event) => {
        event.preventDefault();
        event.stopPropagation();
        const isFollowing = listBtn.dataset.isFollowing === 'true';
        const data = await toggleFollow(user.user_id, !isFollowing, listBtn);
        if (!data) {
          return;
        }

        if (followBtn && String(followBtn.dataset.userId) === String(user.user_id)) {
          updateFollowButton(followBtn, data.is_following);
          if (followersCountEl) {
            followersCountEl.textContent = data.followers_count;
          }
        }

        if (!data.is_following && usersModalTitle.textContent === 'دنبال‌شوندگان' && window.IS_OWN_PROFILE) {
          row.remove();
          if (followingCountEl) {
            const current = parseInt(followingCountEl.textContent, 10) || 0;
            followingCountEl.textContent = Math.max(0, current - 1);
          }
          if (!usersList.children.length) {
            usersEmpty.textContent = 'کاربری یافت نشد.';
            usersEmpty.style.display = 'block';
          }
        }
      });
    }

    return row;
  }

  async function loadUsers(url, title) {
    usersList.innerHTML = '';
    usersEmpty.style.display = 'none';
    usersLoading.style.display = 'block';
    usersModalTitle.textContent = title;
    openUsersModal();

    try {
      const response = await fetch(url);
      const data = await response.json();
      usersLoading.style.display = 'none';

      if (!response.ok) {
        usersEmpty.textContent = data.error || 'خطا در بارگذاری';
        usersEmpty.style.display = 'block';
        return;
      }

      if (!data.users || data.users.length === 0) {
        usersEmpty.textContent = 'کاربری یافت نشد.';
        usersEmpty.style.display = 'block';
        return;
      }

      data.users.forEach((user) => {
        usersList.appendChild(renderUserRow(user));
      });
    } catch (error) {
      usersLoading.style.display = 'none';
      usersEmpty.textContent = 'خطا در ارتباط با سرور';
      usersEmpty.style.display = 'block';
    }
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

  if (closeUsersModalBtn && usersModal) {
    closeUsersModalBtn.addEventListener('click', closeUsersModal);

    window.addEventListener('click', (event) => {
      if (event.target === usersModal) closeUsersModal();
    });
  }

  if (followersStat) {
    followersStat.addEventListener('click', () => {
      loadUsers(window.PROFILE_FOLLOWERS_URL, 'دنبال‌کنندگان');
    });
  }

  if (followingStat) {
    followingStat.addEventListener('click', () => {
      loadUsers(window.PROFILE_FOLLOWINGS_URL, 'دنبال‌شوندگان');
    });
  }

  if (followBtn) {
    followBtn.addEventListener('click', async () => {
      const userId = followBtn.dataset.userId;
      const isFollowing = followBtn.dataset.isFollowing === 'true';
      await toggleFollow(userId, !isFollowing, followBtn);
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
