function return_text (r, code, msg) {
  r.status = code
  r.headersOut['Content-Type'] = 'text/plain; charset=utf-8';
  r.headersOut['Content-Length'] = msg.length;
  r.sendHeader()
  r.send(msg)
  r.finish()
}

function flag_getinfo_403 (r) {
  return_text(r, 403, 'ERROR_ACCESS_DENIED')
}

function flag_getinfo_404 (r) {
  return_text(r, 404, 'ERROR_NOT_FOUND')
}

function flag_getinfo_429 (r) {
  return_text(r, 429, 'ERROR_RATELIMIT')
}

function flag_submit_403 (r) {
  return_text(r, 403, 'ERROR_ACCESS_DENIED')
}

function flag_submit_413 (r) {
  return_text(r, 413, 'ERROR_FLAG_INVALID')
}

function flag_submit_429 (r) {
  return_text(r, 429, 'ERROR_RATELIMIT')
}

function service_getstatus_403 (r) {
  return_text(r, 403, 'ERROR_ACCESS_DENIED')
}

function service_getstatus_404 (r) {
  return_text(r, 404, 'ERROR_NOT_FOUND')
}

function service_getstatus_429 (r) {
  return_text(r, 429, 'ERROR_RATELIMIT')
}

function team_logo_403 (r) {
  return_text(r, 403, 'ERROR_ACCESS_DENIED')
}

function team_logo_429 (r) {
  return_text(r, 429, 'ERROR_RATELIMIT')
}

function open_data_403 (r) {
  return_text(r, 403, 'ERROR_ACCESS_DENIED')
}

function open_data_429 (r) {
  return_text(r, 429, 'ERROR_RATELIMIT')
}

export default {
  flag_getinfo_403,
  flag_getinfo_404,
  flag_getinfo_429,
  flag_submit_403,
  flag_submit_413,
  flag_submit_429,
  service_getstatus_403,
  service_getstatus_404,
  service_getstatus_429,
  team_logo_403,
  team_logo_429,
  open_data_403,
  open_data_429
}
