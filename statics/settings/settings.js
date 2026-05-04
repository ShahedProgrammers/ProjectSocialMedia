let video = document.getElementById("video");
let canvas = document.getElementById("canvas");
let capturedImages = [];
let stream;

// CHANGE PASSWORD
function changePassword(e){
    e.preventDefault();

    let newPass = document.getElementById("newPassword").value;
    let confirm = document.getElementById("confirmPassword").value;

    if(newPass !== confirm){
        document.getElementById("passwordMessage").innerText="رمزها یکسان نیست";
        return;
    }

    document.getElementById("passwordMessage").innerText="رمز با موفقیت تغییر کرد";
}

// TOGGLE FACE LOGIN
function toggleFaceLogin(){
    let toggle = document.getElementById("faceLoginToggle");

    if(toggle.checked){
        document.getElementById("faceSetupSection").style.display="block";
    }else{
        document.getElementById("faceSetupSection").style.display="none";
    }
}

// START CAMERA
function startCamera(){
    navigator.mediaDevices.getUserMedia({video:true})
        .then(s=>{
            stream=s;
            video.srcObject=s;
            document.getElementById("captureBtn").disabled=false;
        });
}

// CAPTURE IMAGE
function captureImage(){

    if(capturedImages.length>=5) return;

    let ctx = canvas.getContext("2d");

    canvas.width=video.videoWidth;
    canvas.height=video.videoHeight;

    ctx.drawImage(video,0,0);

    let data = canvas.toDataURL("image/png");

    capturedImages.push(data);

    let img=document.createElement("img");
    img.src=data;

    document.getElementById("capturedImages").appendChild(img);

    document.getElementById("imageCount").innerText=capturedImages.length+"/5 تصویر ثبت شده";

    if(capturedImages.length>=5){
        document.getElementById("submitBtn").disabled=false;
    }
}

// SEND FACE DATA TO SERVER
function submitFaceData(){

    fetch("/api/face-register/",{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body:JSON.stringify({
            images:capturedImages
        })
    })
        .then(r=>r.json())
        .then(data=>{
            document.getElementById("faceMessage").innerText="چهره ذخیره شد";
        });
}

// PROFILE IMAGE PREVIEW
function previewProfileImage(event){

    let reader=new FileReader();

    reader.onload=function(){
        document.getElementById("previewImage").src=reader.result;
    }

    reader.readAsDataURL(event.target.files[0]);
}

// UPLOAD PROFILE IMAGE
function uploadProfileImage(){

    let file=document.getElementById("profileImageInput").files[0];

    let formData=new FormData();
    formData.append("image",file);

    fetch("/api/upload-profile-image/",{
        method:"POST",
        body:formData
    })
        .then(r=>r.json())
        .then(data=>{
            document.getElementById("profileMessage").innerText="تصویر ذخیره شد";
        });
}

function removeProfileImage(){
    document.getElementById("previewImage").src="https://via.placeholder.com/150";
}
