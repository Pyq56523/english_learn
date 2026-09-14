import request from './request'

export function getCaptcha() {
  return request.get('/captcha')
}