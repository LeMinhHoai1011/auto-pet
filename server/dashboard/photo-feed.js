function configurePhotoFeed(button, file, result, showMessage) {
  const pet = result?.can_request_feed ? result.results[0] : null;
  button.hidden = !pet;
  button.style.display = pet ? '' : 'none';
  button.disabled = false;
  button.onclick = null;
  if (!pet) return;

  button.textContent = 'Xác nhận nhả thật cho ' + pet.pet_name;
  button.onclick = async () => {
    button.disabled = true;
    button.hidden = true;
    button.style.display = 'none';
    const form = new FormData();
    form.append('file', file);
    try {
      const params = new URLSearchParams({ feed_pet_id: pet.pet_id });
      const response = await fetch('/api/recognition/identify?' + params, {
        method: 'POST',
        body: form
      });
      const data = await response.json();
      const sent = response.ok && Boolean(data.feed_request_id);
      const message = sent
        ? 'Đã gửi lệnh nhả cho ' + pet.pet_name + '. Đang chờ ESP32 phản hồi.'
        : typeof data.detail === 'string' ? data.detail : 'Không gửi được lệnh nhả.';
      showMessage(message, sent);
    } catch {
      showMessage('Mất kết nối khi gửi yêu cầu. Kiểm tra máy trước khi thử lại.', false);
    }
  };
}
