document.addEventListener('DOMContentLoaded', () => {
  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function buildCommentItem(comment) {
    const item = document.createElement('div');
    item.className = 'comment-item';
    item.innerHTML = `
      <div class="comment-header">
        <strong>${escapeHtml(comment.username)}</strong>
        <small>${escapeHtml(comment.created_at)}</small>
      </div>
      <p class="comment-content">${escapeHtml(comment.content)}</p>
    `;
    return item;
  }

  function renderComments(panel, comments) {
    const list = panel.querySelector('.comments-list');
    const empty = panel.querySelector('.comments-empty');
    list.innerHTML = '';

    if (!comments.length) {
      empty.hidden = false;
      return;
    }

    empty.hidden = true;
    comments.forEach((comment) => {
      list.appendChild(buildCommentItem(comment));
    });
  }

  function prependComment(panel, comment) {
    const list = panel.querySelector('.comments-list');
    const empty = panel.querySelector('.comments-empty');
    empty.hidden = true;
    list.prepend(buildCommentItem(comment));
  }

  async function loadComments(postId, panel) {
    const loading = panel.querySelector('.comments-loading');
    const errorBox = panel.querySelector('.comments-error');
    const url = window.EXPLORE_COMMENTS_URL.replace('/0/', `/${postId}/`);

    loading.hidden = false;
    errorBox.hidden = true;

    try {
      const response = await fetch(url);
      const data = await response.json();
      loading.hidden = true;

      if (!response.ok) {
        errorBox.textContent = data.error || 'خطا در بارگذاری کامنت‌ها';
        errorBox.hidden = false;
        return;
      }

      renderComments(panel, data.comments || []);
      panel.dataset.loaded = 'true';
    } catch (error) {
      loading.hidden = true;
      errorBox.textContent = 'خطا در ارتباط با سرور';
      errorBox.hidden = false;
    }
  }

  document.querySelectorAll('.like-btn').forEach((button) => {
    button.addEventListener('click', async () => {
      const postId = button.dataset.postId;
      const isLiked = button.dataset.isLiked === 'true';
      const like = !isLiked;
      const url = window.EXPLORE_LIKE_URL.replace('/0/', `/${postId}/`);

      button.disabled = true;

      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': window.CSRF_TOKEN,
          },
          body: JSON.stringify({ like }),
        });

        const data = await response.json();
        if (!response.ok) {
          return;
        }

        button.dataset.isLiked = data.is_liked ? 'true' : 'false';
        button.classList.toggle('liked', data.is_liked);

        const icon = button.querySelector('i');
        icon.classList.toggle('fa-regular', !data.is_liked);
        icon.classList.toggle('fa-solid', data.is_liked);

        const feed = button.closest('.feed');
        const countElement = feed.querySelector('.like-count');
        if (countElement) {
          countElement.textContent = data.like_count;
        }
      } catch (error) {
        console.error(error);
      } finally {
        button.disabled = false;
      }
    });
  });

  document.querySelectorAll('.comment-toggle-btn').forEach((button) => {
    button.addEventListener('click', async () => {
      const postId = button.dataset.postId;
      const panel = document.getElementById(`comments-panel-${postId}`);
      const commentsEnabled = button.dataset.commentsEnabled === 'true';
      const isOpen = !panel.hidden;

      if (isOpen) {
        panel.hidden = true;
        return;
      }

      panel.hidden = false;

      if (!commentsEnabled) {
        panel.querySelector('.comments-disabled').hidden = false;
        panel.querySelector('.comments-loading').hidden = true;
        return;
      }

      if (panel.dataset.loaded !== 'true') {
        await loadComments(postId, panel);
      }
    });
  });

  document.querySelectorAll('.comment-form').forEach((form) => {
    form.addEventListener('submit', async (event) => {
      event.preventDefault();

      const feed = form.closest('.feed');
      const postId = feed.dataset.postId;
      const panel = form.closest('.comments-panel');
      const input = form.querySelector('.comment-input');
      const submitBtn = form.querySelector('.comment-submit-btn');
      const errorBox = panel.querySelector('.comments-error');
      const content = input.value.trim();

      if (!content) {
        return;
      }

      submitBtn.disabled = true;
      errorBox.hidden = true;

      try {
        const url = window.EXPLORE_COMMENTS_URL.replace('/0/', `/${postId}/`);
        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': window.CSRF_TOKEN,
          },
          body: JSON.stringify({ content }),
        });

        const data = await response.json();

        if (!response.ok) {
          errorBox.textContent = data.error || 'خطا در ثبت کامنت';
          errorBox.hidden = false;
          return;
        }

        prependComment(panel, data.comment);
        input.value = '';
        panel.dataset.loaded = 'true';
      } catch (error) {
        errorBox.textContent = 'خطا در ارتباط با سرور';
        errorBox.hidden = false;
      } finally {
        submitBtn.disabled = false;
      }
    });
  });

  function buildFollowUrl(userId) {
    return window.EXPLORE_FOLLOW_URL.replace('/0/', `/${userId}/`);
  }

  async function parseJsonResponse(response) {
    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      throw new Error('پاسخ نامعتبر از سرور');
    }
    return response.json();
  }

  function updateFollowButtons(userId, isFollowing) {
    document.querySelectorAll(`.follow-btn[data-user-id="${userId}"]`).forEach((button) => {
      button.dataset.isFollowing = isFollowing ? 'true' : 'false';
      button.classList.toggle('following', isFollowing);
      button.textContent = isFollowing ? 'دنبال می‌کنید' : 'دنبال کردن';
    });
  }

  document.querySelectorAll('.follow-btn').forEach((button) => {
    button.addEventListener('click', async (event) => {
      event.preventDefault();
      event.stopPropagation();

      const userId = button.dataset.userId;
      const isFollowing = button.dataset.isFollowing === 'true';
      const follow = !isFollowing;

      document.querySelectorAll(`.follow-btn[data-user-id="${userId}"]`).forEach((btn) => {
        btn.disabled = true;
      });

      try {
        const response = await fetch(buildFollowUrl(userId), {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': window.CSRF_TOKEN,
          },
          body: JSON.stringify({ follow }),
        });

        const data = await parseJsonResponse(response);
        if (!response.ok) {
          alert(data.error || 'خطا در انجام عملیات');
          return;
        }

        updateFollowButtons(userId, data.is_following);
      } catch (error) {
        console.error(error);
        alert(error.message || 'خطا در ارتباط با سرور');
      } finally {
        document.querySelectorAll(`.follow-btn[data-user-id="${userId}"]`).forEach((btn) => {
          btn.disabled = false;
        });
      }
    });
  });
});
