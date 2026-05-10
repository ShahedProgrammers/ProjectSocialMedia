let hashtags = [];
let selectedMedia = null;

const postForm = document.getElementById("postForm");
const postContent = document.getElementById("postContent");
const contentLabel = document.getElementById("contentLabel");

const hashtagInput = document.getElementById("hashtagInput");
const hashtagList = document.getElementById("hashtagList");
const previewHashtags = document.getElementById("previewHashtags");
const tagsInput = document.getElementById("tagsInput");

const mediaInput = document.getElementById("mediaInput");
const mediaPreview = document.getElementById("mediaPreview");
const mediaHolder = document.getElementById("mediaHolder");
const uploadPlaceholder = document.getElementById("uploadPlaceholder");
const previewMedia = document.getElementById("previewMedia");
const removeMediaBtn = document.getElementById("removeMediaBtn");

const scheduleToggle = document.getElementById("scheduleToggle");
const scheduleSection = document.getElementById("scheduleSection");
const scheduleTime = document.getElementById("scheduleTime");

const commentsEnabled = document.getElementById("commentsEnabled");
const postMessage = document.getElementById("postMessage");

/* ---------- Hashtag ---------- */
hashtagInput?.addEventListener("keypress", (e) => {
    if (e.key === " " || e.key === "Enter") {
        e.preventDefault();
        const value = hashtagInput.value.trim();
        if (value) {
            addHashtag(value);
            hashtagInput.value = "";
        }
    }
});

function addHashtag(tag){
    tag = normalizeTag(tag);
    if (!tag) return;
    if (!tag.startsWith("#")) tag = "#" + tag;
    if (hashtags.includes(tag)) return;

    hashtags.push(tag);

    const span = document.createElement("span");
    span.innerText = tag;
    hashtagList.appendChild(span);

    updatePreviewHashtags();
}

function normalizeTag(tag){
    return tag.replace(/,/g, "").replace(/^#/, "").trim();
}

function addPendingHashtag(){
    if (!hashtagInput) return;

    const value = normalizeTag(hashtagInput.value);
    if (value) {
        addHashtag(value);
        hashtagInput.value = "";
    }
}

function updatePreviewHashtags(){
    previewHashtags.innerHTML = "";
    hashtags.forEach(tag => {
        const s = document.createElement("span");
        s.innerText = tag;
        previewHashtags.appendChild(s);
    });
    if (tagsInput) {
        tagsInput.value = hashtags.map(tag => tag.replace(/^#/, "")).join(",");
    }
}

/* ---------- Media ---------- */
mediaInput?.addEventListener("change", previewMediaFile);

function previewMediaFile(e){
    const file = e.target.files[0];
    if (!file) return;

    selectedMedia = file;

    mediaHolder.innerHTML = "";
    previewMedia.innerHTML = "";
    mediaPreview.style.display = "block";
    uploadPlaceholder.style.display = "none";

    // تبدیل محتوا به کپشن
    contentLabel.innerText = "کپشن پست";
    postContent.placeholder = "برای پست خود کپشن بنویسید (اختیاری)";
    postContent.required = false;

    const reader = new FileReader();
    reader.onload = function(){
        if (file.type.startsWith("image")) {
            mediaHolder.innerHTML = `<img src="${reader.result}">`;
            previewMedia.innerHTML = `<img src="${reader.result}">`;
        } else if (file.type.startsWith("video")) {
            mediaHolder.innerHTML = `<video src="${reader.result}" controls></video>`;
            previewMedia.innerHTML = `<video src="${reader.result}" controls></video>`;
        }
    };
    reader.readAsDataURL(file);
}

removeMediaBtn?.addEventListener("click", () => {
    mediaInput.value = "";
    selectedMedia = null;

    mediaHolder.innerHTML = "";
    previewMedia.innerHTML = "";
    mediaPreview.style.display = "none";
    uploadPlaceholder.style.display = "block";

    resetContentToPost();
});

/* ---------- Reset Content ---------- */
function resetContentToPost(){
    contentLabel.innerText = "محتوای پست";
    postContent.placeholder = "چه چیزی در ذهن دارید؟";
    postContent.required = true;
}

/* ---------- Preview Text ---------- */
postContent.addEventListener("input", () => {
    document.getElementById("previewText").innerText = postContent.value || "...";
});

/* ---------- Schedule ---------- */
scheduleToggle?.addEventListener("change", () => {
    scheduleSection.style.display = scheduleToggle.checked ? "block" : "none";
});

/* ---------- Submit ---------- */
postForm.addEventListener("submit", (e) => {
    addPendingHashtag();

    const content = postContent.value.trim();

    if (mediaInput && !selectedMedia && content === "") {
        e.preventDefault();
        showMessage("پست متنی نمی‌تواند خالی باشد");
        return;
    }

    if (tagsInput) {
        tagsInput.value = hashtags.map(tag => tag.replace(/^#/, "")).join(",");
    }
});

function showMessage(text, success=false){
    postMessage.innerText = text;
    postMessage.style.color = success ? "green" : "red";
}

