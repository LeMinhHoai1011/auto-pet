'use strict';

const start = document.querySelector('#start');
const stop = document.querySelector('#stop');
const file = document.querySelector('#file');
const camera = document.querySelector('#camera');
const preview = document.querySelector('#preview');
const placeholder = document.querySelector('#placeholder');
const status = document.querySelector('#status');
const result = document.querySelector('#result');
const overlay = preview.getContext('2d');
const frame = document.createElement('canvas');
const pixels = frame.getContext('2d');
const labels = { cat: 'Mèo', dog: 'Chó' };
let modelPromise;
let session = 0;
let busy = false;
let stream;

function loadModel() {
  modelPromise ??= Promise.resolve().then(() => {
    if (!window.cocoSsd || !window.tf) throw new Error('Missing dependencies');
    return window.cocoSsd.load();
  }).catch(() => {
    modelPromise = undefined;
    throw new Error('Không tải được mô hình. Hãy kiểm tra kết nối Internet và thử lại.');
  });
  return modelPromise;
}

function setBusy(value) {
  busy = value;
  start.disabled = value;
  file.disabled = value;
}

function releaseCamera() {
  session++;
  stream?.getTracks().forEach(track => track.stop());
  stream = undefined;
  camera.srcObject = null;
  stop.disabled = true;
}

function resetPreview() {
  preview.hidden = true;
  placeholder.hidden = false;
  result.textContent = '';
}

async function detect(model, source, width, height, current) {
  const scale = Math.min(1, 800 / Math.max(width, height));
  frame.width = Math.max(1, Math.round(width * scale));
  frame.height = Math.max(1, Math.round(height * scale));
  pixels.drawImage(source, 0, 0, frame.width, frame.height);
  const predictions = await model.detect(frame, 40, 0.5);
  if (session !== current) return;

  const pets = predictions.filter(item => Object.hasOwn(labels, item.class));
  preview.width = frame.width;
  preview.height = frame.height;
  overlay.drawImage(frame, 0, 0);
  overlay.font = 'bold 18px system-ui';
  overlay.lineWidth = 3;
  const descriptions = pets.map(pet => {
    const [x, y, width, height] = pet.bbox;
    const caption = `${labels[pet.class]} ${Math.round(pet.score * 100)}%`;
    const color = pet.class === 'cat' ? '#a3ffbf' : '#ffd280';
    const textWidth = overlay.measureText(caption).width + 12;
    const left = Math.max(0, Math.min(x, preview.width - textWidth));
    const top = Math.max(0, Math.min(y - 25, preview.height - 25));
    overlay.strokeStyle = color;
    overlay.strokeRect(x, y, width, height);
    overlay.fillStyle = color;
    overlay.fillRect(left, top, textWidth, 25);
    overlay.fillStyle = '#10251a';
    overlay.fillText(caption, left + 6, top + 19);
    return caption;
  });
  preview.hidden = false;
  placeholder.hidden = true;
  result.textContent = descriptions.join(' · ') || 'Chưa phát hiện chó hoặc mèo.';
}

start.addEventListener('click', async () => {
  if (busy) return;
  if (!navigator.mediaDevices?.getUserMedia) {
    status.textContent = 'Webcam cần HTTPS hoặc localhost. Bạn vẫn có thể chọn ảnh.';
    return;
  }
  const current = ++session;
  setBusy(true);
  resetPreview();
  status.textContent = 'Đang tải mô hình…';
  try {
    const model = await loadModel();
    if (session !== current) return;
    status.textContent = 'Đang chờ quyền truy cập webcam…';
    const input = await navigator.mediaDevices.getUserMedia({
      video: { width: { ideal: 640 }, height: { ideal: 480 } },
      audio: false,
    });
    if (session !== current) {
      input.getTracks().forEach(track => track.stop());
      return;
    }
    stream = input;
    camera.srcObject = stream;
    stop.disabled = false;
    await camera.play();
    if (session !== current) return;
    status.textContent = 'Đang nhận dạng từ webcam.';
    while (session === current && stream.active) {
      if (camera.readyState >= 2) {
        await detect(model, camera, camera.videoWidth, camera.videoHeight, current);
      }
      await new Promise(resolve => setTimeout(resolve, 80));
    }
    if (session === current) status.textContent = 'Webcam đã ngừng cung cấp hình ảnh.';
  } catch (error) {
    if (session === current) {
      status.textContent = error.name === 'NotAllowedError'
        ? 'Webcam chưa được cấp quyền. Bạn có thể thử lại hoặc chọn ảnh.'
        : error.name === 'NotFoundError' || error.name === 'NotReadableError'
          ? 'Không mở được webcam. Bạn có thể chọn ảnh.'
          : error.message;
    }
  } finally {
    if (session === current) releaseCamera();
    setBusy(false);
  }
});

stop.addEventListener('click', () => {
  releaseCamera();
  resetPreview();
  status.textContent = 'Đã dừng webcam.';
});

file.addEventListener('change', async () => {
  const selected = file.files[0];
  file.value = '';
  if (!selected || busy) return;
  const current = ++session;
  setBusy(true);
  resetPreview();
  status.textContent = 'Đang tải mô hình và phân tích ảnh…';
  const url = URL.createObjectURL(selected);
  try {
    const image = new Image();
    image.src = url;
    await image.decode().catch(() => { throw new Error('Không đọc được ảnh đã chọn.'); });
    const model = await loadModel();
    if (session !== current) return;
    await detect(model, image, image.naturalWidth, image.naturalHeight, current);
    if (session === current) status.textContent = 'Đã phân tích ảnh.';
  } catch (error) {
    if (session === current) status.textContent = error.message;
  } finally {
    URL.revokeObjectURL(url);
    setBusy(false);
  }
});

window.addEventListener('pagehide', () => {
  releaseCamera();
  resetPreview();
  status.textContent = 'Chọn nguồn hình để bắt đầu.';
});
